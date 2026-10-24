#!/usr/bin/env python3
"""Import an existing price book into the standard price book format.

For a price book that already exists (a spreadsheet, a CSV export, a quote tool dump) and whose
products are not yet in the data rights register. It does not need the register or Legal.

Usage:
  python import_price_book.py --in FILE.(csv|xlsx) --out-dir OUT_DIR
        [--sheet NAME] [--map map.json] [--default-currency USD] [--version legacy-2026-10]
        [--tier-model all_units|graduated]

Writes to OUT_DIR:
  price_book.csv          standard columns, one row per tier, status "Existing"
  import_report.md        mapping used, product types, issues, assumptions, what needs a human decision
  dataset_candidates.csv  products that carry data or third-party content, as candidate source datasets for
                          the register, ranked by annual revenue (the intake priority list)
  The held rights the register needs (register_backfill.csv) come from the next step: run
  check_price_book.py with --exposure-csv and --backfill-csv. It maps each conferred right to the held
  rights it needs.

Rules it follows
  - It never invents a number. A missing floor price stays blank and is reported.
  - It infers product_type from the words in the product, category, description and unit. Every
    inference is listed with its reason so a person can correct it. Correct with --map or by editing.
  - The price book records what we CONFER to the customer (conferred_right), not what we hold. The
    register holds the rights we have on the source data. They are linked by dataset_id.
  - Data products get a candidate dataset_id (DS-CAND-...): the source dataset the product is built from,
    inferred from the product name. Candidate ids are placeholders for intake and lineage checks.
  - API products are marked rights_relevance=Possible: responses may carry supplier or third-party content.
  - It does not set legal_confirmed, any register status, or status Approved.

--map JSON: {"list_price": "Source header", "product_id": "SKU", ...,
             "types": {"Product name": "service"}, "datasets": {"Product name": "DS-SUP-001"},
             "forms": {"Product name": "passthrough"}}
  forms: data_form per product, derived (default: an aggregate or insight built from the dataset) or
  passthrough (the customer receives the underlying data itself).
"""
import argparse
import csv
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

STANDARD = ["line_id", "product_id", "product_type", "product_name", "product_family", "dataset_id", "conferred_right",
            "data_form", "delivery", "unit", "tier_min", "tier_max", "list_price", "floor_price", "currency", "term_months",
            "tier_model", "status", "version", "annual_revenue", "customers", "rights_relevance", "price_period",
            "source_row", "notes"]

SYNONYMS = {
    "product_id": ["sku", "product code", "product id", "item", "item code", "product", "offering", "plan"],
    "product_name": ["product name", "name", "product", "offering", "plan"],
    "description": ["description", "desc", "details"],
    "product_family": ["family", "category", "product family", "group", "line", "portfolio"],
    "product_type": ["type", "product type"],
    "dataset_id": ["dataset", "dataset id", "dataset_id"],
    "conferred_right": ["conferred right", "conferred_right", "use right", "use_right", "rights", "license type",
                        "licence type", "usage right", "rights granted"],
    "delivery": ["delivery", "delivery method", "channel", "format"],
    "unit": ["pricing unit", "unit", "uom", "unit of measure", "metric", "charge unit", "billing unit", "per"],
    "tier_range": ["volume band", "band", "tier", "tiers", "volume", "range", "quantity band", "volume tier"],
    "tier_min": ["tier min", "min qty", "from", "lower", "min volume", "start"],
    "tier_max": ["tier max", "max qty", "to", "upper", "max volume", "end"],
    "list_price": ["list price", "price", "list", "rate", "unit price", "annual price", "amount", "fee", "msrp"],
    "floor_price": ["min price", "floor", "floor price", "minimum price", "lowest price", "walk-away"],
    "currency": ["currency", "ccy"],
    "term_months": ["term", "term months", "contract term", "term (months)"],
    "annual_revenue": ["fy revenue", "annual revenue", "revenue", "arr", "annual recurring revenue", "booked revenue"],
    "customers": ["accounts", "customers", "customer count", "# customers", "clients"],
}

TYPE_RULES = [  # (type, regex on lowercase text, reason)
    ("data_license", r"\b(data\s?set|dataset|benchmark|insights?|data feed|data file|feed|fare data|data)\b", "data words"),
    ("service", r"\b(service|services|support|consulting|implementation|onboarding|training|professional|integration|managed)\b", "service words"),
    ("api_access", r"\b(api|calls?|transactions?|requests?|endpoint|queries)\b", "API or usage-metered words"),
    ("software", r"\b(seat|seats|user|users|desktop|subscription|platform|module|tool|licen[sc]e|app)\b", "software words"),
]


def norm(s):
    return re.sub(r"[^a-z0-9#() ]+", " ", str(s).lower()).strip()


def money(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s.lower() in ("n/a", "na", "-", "tbd", "none", "null"):
        return None
    s = re.sub(r"(?i)\b(usd|eur|gbp|us\$)\b", "", s)
    s = s.replace("$", "").replace("€", "").replace("£", "").replace(",", "").strip()
    m = re.match(r"^-?\d+(\.\d+)?", s)
    return float(m.group(0)) if m else None


def qty(tok):
    t = tok.strip().lower().replace(",", "")
    m = re.match(r"^(\d+(\.\d+)?)\s*([kmb]?)$", t)
    if not m:
        return None
    mult = {"": 1, "k": 1e3, "m": 1e6, "b": 1e9}[m.group(3)]
    return float(m.group(1)) * mult


def parse_band(text):
    """Return (tier_min, tier_max, ok). 'all' or blank means one tier."""
    t = str(text or "").strip().lower()
    if t in ("", "all", "any", "flat", "n/a", "-"):
        return 1.0, None, True
    t = t.replace("–", "-").replace("—", "-")
    m = re.match(r"^(.+?)\s*(\+|and above|and up|or more)$", t)
    if m and qty(m.group(1)) is not None:
        return qty(m.group(1)) if qty(m.group(1)) > 0 else 1.0, None, True
    m = re.match(r"^(>=|>)\s*(.+)$", t)
    if m and qty(m.group(2)) is not None:
        return qty(m.group(2)), None, True
    m = re.match(r"^(.+?)\s*(-|to)\s*(.+)$", t)
    if m and qty(m.group(1)) is not None and qty(m.group(3)) is not None:
        lo = qty(m.group(1))
        return (lo if lo > 0 else 1.0), qty(m.group(3)), True
    return 1.0, None, False


def term_months(v):
    s = str(v or "").strip().lower()
    if not s:
        return None, False
    if "one-time" in s or "one time" in s or "once" in s:
        return 1, True
    m = re.match(r"^(\d+(\.\d+)?)\s*(mo|mos|month|months|m)?$", s)
    if m:
        return int(float(m.group(1))), True
    m = re.match(r"^(\d+(\.\d+)?)\s*(y|yr|yrs|year|years)$", s)
    if m:
        return int(float(m.group(1)) * 12), True
    return None, False


def read_rows(path, sheet):
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xlsm"):
        from openpyxl import load_workbook
        wb = load_workbook(p, read_only=True, data_only=True)
        ws = wb[sheet] if sheet else wb[wb.sheetnames[0]]
        raw = [list(r) for r in ws.iter_rows(values_only=True)]
    else:
        with open(p, newline="", encoding="utf-8-sig") as f:
            raw = [r for r in csv.reader(f)]
    return raw


def find_header(raw, extra_syn):
    best, best_i = -1, 0
    allsyn = {norm(x) for v in SYNONYMS.values() for x in v}
    for i, r in enumerate(raw[:20]):
        score = sum(1 for c in r if c is not None and norm(c) in allsyn)
        if score > best:
            best, best_i = score, i
    return best_i


def build_mapping(headers, user_map):
    """canonical -> source header index"""
    mapping, used = {}, set()
    nh = [norm(h) for h in headers]
    for canon, src in user_map.items():
        canon = {"use_right": "conferred_right"}.get(canon, canon)
        if canon in SYNONYMS or canon in STANDARD:
            if src in headers:
                mapping[canon] = headers.index(src)
                used.add(mapping[canon])
    order = ["list_price", "floor_price", "tier_range", "tier_min", "tier_max", "unit", "term_months", "annual_revenue",
             "customers", "currency", "description", "product_family", "product_type", "dataset_id", "conferred_right",
             "delivery", "product_name", "product_id"]
    for canon in order:
        if canon in mapping:
            continue
        for syn in SYNONYMS[canon]:
            s = norm(syn)
            for i, h in enumerate(nh):
                if i in used:
                    continue
                # exact, or header starts with the synonym followed by a space or parenthesis
                if h == s or h.startswith(s + " ") or h.startswith(s + "("):
                    mapping[canon] = i
                    used.add(i)
                    break
            if canon in mapping:
                break
    # a product column serves as both id and name
    if "product_id" not in mapping and "product_name" in mapping:
        mapping["product_id"] = mapping["product_name"]
    if "product_name" not in mapping and "product_id" in mapping:
        mapping["product_name"] = mapping["product_id"]
    return mapping


def slug(s):
    return re.sub(r"[^A-Z0-9]+", "-", str(s).upper()).strip("-")[:40].strip("-")


CONFERRED_RIGHT_WORDS = [  # (conferred_right, regex on lowercase product text)
    ("redistribution_resale", r"\b(resale|resell|redistribut\w*|white[- ]?label)\b"),
    ("derivative_data_product", r"\b(derivative|derived product)\b"),
    ("ai_training", r"\b(ai training|model training|train(ing)? rights)\b"),
    ("ai_retrieval_grounding", r"\b(grounding|rag|agent access)\b"),
    ("display_to_third_parties", r"\b(display rights|third[- ]party display)\b"),
]


def infer_conferred_right(text):
    t = norm(text)
    for ur, rx in CONFERRED_RIGHT_WORDS:
        if re.search(rx, t):
            return ur
    return ""


def base_name(name):
    """'Fare Data - Resale' -> 'Fare Data' when the suffix names a conferred right."""
    m = re.match(r"^(.*?)\s+[-–—]\s+(.+)$", name)
    if m and infer_conferred_right(m.group(2)):
        return m.group(1).strip()
    return name


def classify(name, family, desc, unit, forced):
    if forced:
        return forced, "high", "set in --map"
    text = " ".join(norm(x) for x in (name, family, desc, unit))
    hits = [(t, why) for t, rx, why in TYPE_RULES if re.search(rx, text)]
    # plain 'data' in a family like "Air API" should not beat 'api' ; prefer specific data words
    fam = norm(family)
    if hits:
        types = [h[0] for h in hits]
        if fam in ("data",) and "data_license" in types:
            return "data_license", "high", f"category is Data"
        if fam in ("services", "service") and "service" in types:
            return "service", "high", "category is Services"
        if fam in ("software",) and "software" in types:
            return "software", "high", "category is Software"
        if fam.endswith("api") and "api_access" in types:
            return "api_access", "high", "category ends in API"
        if len(set(types)) == 1:
            return types[0], "medium", hits[0][1]
        return types[0], "low", "several signals: " + ", ".join(sorted(set(types)))
    return "other", "low", "no type words found"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--sheet")
    ap.add_argument("--map")
    ap.add_argument("--default-currency", default="USD")
    ap.add_argument("--version", default="legacy")
    ap.add_argument("--tier-model", choices=["all_units", "graduated"], default="all_units",
                    help="How the tiers bill. all_units: the tier price applies to every unit. graduated: each tier prices only its own units.")
    args = ap.parse_args()

    user_map = json.load(open(args.map)) if args.map else {}
    forced_types = user_map.get("types", {})
    forced_ds = user_map.get("datasets", {})
    forced_forms = user_map.get("forms", {})
    raw = read_rows(args.inp, args.sheet)
    if not raw:
        sys.exit("The input file is empty.")
    hi = find_header(raw, user_map)
    headers = [("" if h is None else str(h).strip()) for h in raw[hi]]
    mapping = build_mapping(headers, user_map)
    if "list_price" not in mapping:
        sys.exit(f"Could not find a list price column. Headers seen: {headers}. Use --map to name it.")
    if "product_id" not in mapping:
        sys.exit(f"Could not find a product column. Headers seen: {headers}. Use --map to name it.")

    issues, assumptions = [], []
    out, last_product = [], {}
    fill_down = ["product_id", "product_name", "product_family", "description", "unit", "term_months",
                 "annual_revenue", "customers", "currency"]
    n_data_rows = 0
    for ri, r in enumerate(raw[hi + 1:], start=hi + 2):
        cells = [("" if c is None else str(c).strip()) for c in r]
        if not any(cells):
            continue
        g = lambda k: cells[mapping[k]] if k in mapping and mapping[k] < len(cells) else ""
        rec = {k: g(k) for k in mapping}
        # fill down blanks for product-level columns when a tier row leaves them empty
        for k in fill_down:
            if k in mapping:
                if rec.get(k, "") == "" and last_product.get(k):
                    rec[k] = last_product[k]
                elif rec.get(k):
                    last_product[k] = rec[k]
        if not rec.get("product_id") and not money(rec.get("list_price")):
            continue  # section or blank line
        n_data_rows += 1
        lp = money(rec.get("list_price"))
        if lp is None:
            issues.append(f"Row {ri} ({rec.get('product_id','?')}): no usable list price {rec.get('list_price')!r}; row skipped")
            continue
        fp = money(rec.get("floor_price")) if "floor_price" in mapping else None
        if "tier_range" in mapping:
            tmin, tmax, ok = parse_band(rec.get("tier_range"))
            if not ok:
                issues.append(f"Row {ri} ({rec['product_id']}): band {rec.get('tier_range')!r} not understood; treated as one tier")
        else:
            tmin = money(rec.get("tier_min")) if "tier_min" in mapping else 1.0
            tmax = money(rec.get("tier_max")) if "tier_max" in mapping else None
            tmin = 1.0 if not tmin else tmin
        tm, ok = term_months(rec.get("term_months"))
        if tm is None:
            tm = 12
            if rec.get("term_months"):
                issues.append(f"Row {ri} ({rec['product_id']}): term {rec['term_months']!r} not understood; used 12")
            else:
                issues.append(f"Row {ri} ({rec['product_id']}): term not stated; used 12 months (assumption)")
        rev = money(rec.get("annual_revenue"))
        cust = money(rec.get("customers"))
        name = rec.get("product_name") or rec.get("product_id")
        ptype, conf, why = classify(name, rec.get("product_family"), rec.get("description"), rec.get("unit"),
                                    forced_types.get(name) or forced_types.get(rec.get("product_id")) or rec.get("product_type") or None)
        if rec.get("product_type") and rec["product_type"] in ("data_license", "api_access", "software", "service", "other"):
            ptype, conf, why = rec["product_type"], "high", "given in the file"
        rel = {"data_license": "Required", "api_access": "Possible"}.get(ptype, "None")
        ds = rec.get("dataset_id") or forced_ds.get(name) or forced_ds.get(rec.get("product_id")) or ""
        ds_inferred = False
        use_right = rec.get("conferred_right", "")
        ur_inferred = False
        if not use_right and rel != "None":
            use_right = infer_conferred_right(f"{name} {rec.get('description','')}")
            ur_inferred = bool(use_right)
        form = forced_forms.get(name) or forced_forms.get(rec.get("product_id")) or ""
        if not ds and rel == "Required":
            ds, ds_inferred = f"DS-CAND-{slug(base_name(name))}", True
        out.append(OrderedDict(
            line_id="", product_id=rec.get("product_id") or slug(name), product_type=ptype, product_name=name,
            product_family=rec.get("product_family", ""), dataset_id=ds, conferred_right=use_right,
            data_form=form if rel != "None" else "", delivery=rec.get("delivery", ""), unit=rec.get("unit", ""),
            tier_min=int(tmin) if tmin is not None else "", tier_max=int(tmax) if tmax is not None else "",
            list_price=lp, floor_price="" if fp is None else fp, currency=rec.get("currency") or args.default_currency,
            term_months=tm, tier_model=args.tier_model, status="Existing", version=args.version,
            annual_revenue="" if rev is None else rev, customers="" if cust is None else int(cust),
            rights_relevance=rel, price_period="", source_row=ri,
            notes="; ".join(x for x in [f"type {ptype} ({conf}: {why})" if conf != "high" else "",
                                        "dataset_id is a candidate: source dataset inferred from the product name" if ds_inferred else "",
                                        "conferred right inferred from the product words, confirm in contracts" if ur_inferred else "",
                                        "conferred right not stated" if rel != "None" and not use_right else ""] if x)))
        out[-1]["_conf"], out[-1]["_why"] = conf, why

    # Bands such as "0 - 1M" and "1M - 10M" share a boundary: the next tier starts one unit above it
    grp = defaultdict(list)
    for o in out:
        grp[(o["product_id"], o["unit"], o["term_months"], o["conferred_right"])].append(o)
    for items in grp.values():
        items.sort(key=lambda o: o["tier_min"] if o["tier_min"] != "" else 0)
        for a, b in zip(items, items[1:]):
            if a["tier_max"] != "" and b["tier_min"] != "" and b["tier_min"] == a["tier_max"]:
                b["tier_min"] = a["tier_max"] + 1
                b["notes"] = "; ".join(x for x in [b["notes"], "tier start moved up by 1 so tiers do not overlap"] if x)
                assumptions.append(f"{b['product_name']}: bands share a boundary at {a['tier_max']:,}; the higher tier starts at {b['tier_min']:,}.") if f"{b['product_name']}: bands share" not in " ".join(assumptions) else None

    # line ids and per-product revenue (revenue repeats on each tier row: count once per product, term)
    for i, o in enumerate(out, 1):
        o["line_id"] = f"L{i:03d}"
    if not out:
        sys.exit("No price lines were read.")

    # revenue is a product total repeated on tier rows: keep it on the first tier only to avoid double counting
    seen_rev = set()
    for o in out:
        k = (o["product_id"], o["unit"], o["term_months"])
        if o["annual_revenue"] != "" and k in seen_rev:
            o["annual_revenue"] = ""
            o["customers"] = ""
        elif o["annual_revenue"] != "":
            seen_rev.add(k)
    if any(o["annual_revenue"] != "" for o in out):
        assumptions.append("Annual revenue and customer counts repeat on every tier row in the source; they are kept on the first tier of each product and unit so they are not double counted.")

    od = Path(args.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    with open(od / "price_book.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=STANDARD, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    # dataset candidates and backfill
    cands = OrderedDict()
    for o in out:
        if o["rights_relevance"] == "None" or not o["dataset_id"]:
            continue
        c = cands.setdefault(o["dataset_id"], {"name": o["product_name"], "types": set(), "products": set(), "lines": 0,
                                               "rev": 0.0, "cust": 0, "rights": set(), "rel": o["rights_relevance"]})
        c["types"].add(o["product_type"])
        c["products"].add(o["product_name"])
        c["lines"] += 1
        c["rev"] += float(o["annual_revenue"] or 0)
        c["cust"] += int(o["customers"] or 0)
        c["rights"].add(o["conferred_right"] or "")
        if o["rights_relevance"] == "Required":
            c["rel"] = "Required"
    has_rev = any(c["rev"] for c in cands.values())
    ranked = sorted(cands.items(), key=lambda kv: (-(kv[1]["rev"] if has_rev else kv[1]["lines"]), kv[0]))
    with open(od / "dataset_candidates.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["priority_rank", "dataset_id", "name", "rights_relevance", "product_types", "price_lines",
                    "annual_revenue", "customers", "conferred_rights_stated", "next_step"])
        for i, (k, c) in enumerate(ranked, 1):
            nxt = ("Confirm the source dataset (lineage), then run dataset-intake-register: find the supplier and customer agreements and propose the held rights"
                   if c["rel"] == "Required" else
                   "Decide first: do responses carry supplier or third-party content? If yes, add a dataset_id and run intake")
            w.writerow([i, k, c["name"], c["rel"], ";".join(sorted(c["types"])), c["lines"],
                        round(c["rev"], 2) if has_rev else "", c["cust"] or "", ";".join(sorted(x for x in c["rights"] if x)) + (" + (not stated on some lines)" if "" in c["rights"] and len(c["rights"]) > 1 else ("(not stated)" if c["rights"] == {""} else "")), nxt])

    # report
    by_type = defaultdict(list)
    for o in out:
        by_type[o["product_type"]].append(o)
    missing_floor = [o for o in out if o["floor_price"] == ""]
    low = {}
    for o in out:
        if o["_conf"] != "high":
            low.setdefault(o["product_name"], (o["product_type"], o["_conf"], o["_why"]))
    L = []
    L.append("# Price book import report\n")
    L.append(f"Source: {args.inp} | header row {hi + 1} | rows read {n_data_rows} | price lines written {len(out)} | version label {args.version}\n")
    L.append("## Column mapping\n")
    L.append("| Standard column | Source column |\n|---|---|")
    for k, i in mapping.items():
        L.append(f"| {k} | {headers[i]} |")
    L.append("\n## Product types\n")
    L.append("| Type | Products | Lines | Rights relevance |\n|---|---|---|---|")
    for t, items in sorted(by_type.items()):
        L.append(f"| {t} | {len({x['product_name'] for x in items})} | {len(items)} | {items[0]['rights_relevance']} |")
    if low:
        L.append("\nProduct types inferred with less than high confidence (check these):\n")
        for n, (t, c, why) in low.items():
            L.append(f"- {n}: {t} ({c}; {why})")
    L.append("\n## What needs a human decision\n")
    nd = [(k, c) for k, c in ranked]
    L.append(f"- Register candidates: {len(nd)} (see dataset_candidates.csv). Data products need a rights check. API products are marked Possible: decide whether responses carry supplier or third-party content.")
    L.append(f"- The conferred right (what the customer may do with the product) is not stated for {sum(1 for o in out if o['rights_relevance'] != 'None' and not o['conferred_right'])} lines that carry data. Legacy price books rarely say which right a price covers; find it in the customer contracts.")
    dl = sorted({o['product_name'] for o in out if o['rights_relevance'] == 'Required' and not o['data_form']})
    if dl:
        L.append(f"- Data form is not set for {len(dl)} data products ({', '.join(dl[:6])}{'...' if len(dl) > 6 else ''}). The checker treats them as derived (an aggregate or insight built from the dataset). Tell it which deliver the underlying data itself (passthrough) with --map \"forms\", because that needs different held rights.")
    L.append(f"- Floor price is missing on {len(missing_floor)} of {len(out)} lines. Floors are not invented. Set them with the data-price-setting skill (cost floor) or from Finance.")
    L.append("\n## Issues\n")
    L.extend([f"- {i}" for i in issues] or ["- None"])
    L.append("\n## Assumptions\n")
    for a in assumptions + [
        "All imported lines have status Existing (current prices in force). Nothing is Approved or Proposed.",
        f"tier_model is set to {args.tier_model} for every line; confirm how the tiers actually bill (re-run with --tier-model graduated if each tier prices only its own units).",
        f"Currency defaults to {args.default_currency} where the source has no currency column. Price period (monthly or annual) is not detected: check the unit text.",
        "Candidate dataset ids (DS-CAND-...) are placeholders for the source dataset each product is built from. Confirm the lineage with data engineering and replace them with real register ids during intake.",
        "The price book records the rights we confer to the customer. The register records the rights we hold on the source data. Nothing here says whether we hold what we confer; the checker works that out from the register."]:
        L.append(f"- {a}")
    L.append("\n## Next steps\n")
    L.append("1. Run check_price_book.py on price_book.csv with no register (strategy mode) and --exposure-csv exposure.csv --backfill-csv register_backfill.csv. You get a consistency check, the held rights the register needs (register_backfill.csv) and a ranked list of the register questions.")
    L.append("2. Work the list top down with the dataset-intake-register skill, starting from register_backfill.csv. Candidate datasets are in dataset_candidates.csv.")
    L.append("3. Re-run the checker against the register as rows are confirmed. Use release mode only when a price book is going out for quoting.")
    (od / "import_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"Read {n_data_rows} rows, wrote {len(out)} price lines, {len(cands)} candidate source datasets to {od}")
    print(f"Product types: " + ", ".join(f"{t} {len(v)}" for t, v in sorted(by_type.items())))
    print(f"Floor price missing on {len(missing_floor)} lines; {len(issues)} import issues")


if __name__ == "__main__":
    main()
