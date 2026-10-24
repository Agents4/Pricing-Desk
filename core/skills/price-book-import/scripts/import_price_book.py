#!/usr/bin/env python3
"""Import an existing price book into the standard price book format.

For a price book that already exists (a spreadsheet, a CSV export, a quote tool dump). It does not need
the rights register or Legal: the pricing desk assumes we hold the rights, and the product manager
assesses that separately with the rights pack.

Usage:
  python import_price_book.py --in FILE.(csv|xlsx) --out-dir OUT_DIR
        [--sheet NAME] [--map map.json] [--default-currency USD] [--version legacy-2026-10]
        [--tier-model all_units|graduated]

Writes to OUT_DIR:
  price_book.csv              standard columns, one row per tier, status "Existing"
  import_report.md            mapping used, product types, issues, assumptions, what needs a human decision
  product_rights_handoff.csv  the data and API products and the right each one grants the customer, with
                              revenue and customers. Give it to the product manager for the rights check.

Rules it follows
  - It never invents a number. A missing floor price stays blank and is reported.
  - It infers product_type from the words in the product, category, description and unit. Every
    inference is listed with its reason so a person can correct it. Correct with --map or by editing.
  - The price book records what we GRANT the customer (conferred_right): what the customer may do with
    the data or the API responses. Legacy price books rarely say. A right is inferred only from words in
    the product name (resale, derivative, AI training...) and is marked as an inference.
  - It does not check whether we hold the rights, and does not set status Approved.

--map JSON: {"list_price": "Source header", "product_id": "SKU", ...,
             "types": {"Product name": "service"}, "rights": {"Product name": "internal_use"}}
"""
import argparse
import csv
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

STANDARD = ["line_id", "product_id", "product_type", "product_name", "product_family", "conferred_right", "right_basis",
            "delivery", "unit", "tier_min", "tier_max", "list_price", "floor_price", "currency", "term_months",
            "tier_model", "status", "version", "annual_revenue", "customers", "price_period",
            "source_row", "notes"]
SCOPE_TYPES = ("data_license", "api_access")

SYNONYMS = {
    "product_id": ["sku", "product code", "product id", "item", "item code", "product", "offering", "plan"],
    "product_name": ["product name", "name", "product", "offering", "plan"],
    "description": ["description", "desc", "details"],
    "product_family": ["family", "category", "product family", "group", "line", "portfolio"],
    "product_type": ["type", "product type"],
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
    s = s.replace("$", "").replace("€", "").replace("£", "").strip()
    if re.search(r"\d,\d{1,2}$", s):
        return None  # "0,05" is a decimal comma in some locales and a thousands error in others: do not guess
    s = s.replace(",", "")
    m = re.match(r"^(-?\d+(?:\.\d+)?)\s*([kmb])?$", s, re.IGNORECASE)
    if not m:
        return None  # trailing words or unknown suffixes are not read as a number
    return float(m.group(1)) * {"": 1, "k": 1e3, "m": 1e6, "b": 1e9}[(m.group(2) or "").lower()]


CCY_WORDS = {"usd": "USD", "us$": "USD", "eur": "EUR", "gbp": "GBP", "cad": "CAD", "aud": "AUD", "chf": "CHF", "jpy": "JPY",
             "inr": "INR", "cny": "CNY", "sgd": "SGD", "aed": "AED", "€": "EUR", "£": "GBP", "¥": "JPY"}
RIGHTS = ["internal_use", "internal_analytics_shared_outputs", "display_to_third_parties", "redistribution_resale",
          "derivative_data_product", "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation"]
PRODUCT_TYPES = ("data_license", "api_access", "software", "service", "other")
TYPE_WORDS = {"data license": "data_license", "data licence": "data_license", "data_licence": "data_license", "datalicense": "data_license",
              "api": "api_access", "api access": "api_access", "software": "software", "service": "service", "services": "service",
              "other": "other"}
RIGHT_WORDS = {"internal use only": "internal_use", "internal use": "internal_use", "internal": "internal_use",
               "resale": "redistribution_resale", "redistribution": "redistribution_resale", "display": "display_to_third_parties"}


def cell_currency(v):
    """The currency a price cell names ('EUR 5.00', '€4.00'), or None. A bare $ names no currency."""
    s = "" if v is None else str(v).lower()
    for w, code in CCY_WORDS.items():
        if (w.isalpha() and re.search(r"\b%s\b" % w, s)) or (not w.isalpha() and w in s):
            return code
    return None


def canon_type(v):
    s = " ".join(str(v or "").replace("_", " ").lower().split())
    if s.replace(" ", "_") in PRODUCT_TYPES:
        return s.replace(" ", "_")
    return TYPE_WORDS.get(s)


def canon_right(v):
    s = " ".join(str(v or "").replace("_", " ").lower().split())
    if s.replace(" ", "_") in RIGHTS:
        return s.replace(" ", "_")
    return RIGHT_WORDS.get(s)


def bad_money(v):
    """True when a non-blank cell could not be read as a number (so the caller can report it)."""
    s = "" if v is None else str(v).strip()
    return s != "" and s.lower() not in ("n/a", "na", "-", "tbd", "none", "null") and money(v) is None


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
        try:
            f = open(p, newline="", encoding="utf-8-sig")
        except OSError as e:
            sys.exit("cannot read %s: %s" % (p, e.strerror or e))
        with f:
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
             "customers", "currency", "description", "product_family", "product_type", "conferred_right",
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
    ap.add_argument("--default-currency", help="Currency to use where the file names none. No default: without it the currency stays blank and the checker stops on it.")
    ap.add_argument("--version", default="legacy")
    ap.add_argument("--tier-model", choices=["all_units", "graduated"],
                    help="How the tiers bill. all_units: the tier price applies to every unit. graduated: each tier prices only its own units. No default: without it tier_model stays blank and the checker warns on multi-tier products.")
    args = ap.parse_args()

    user_map = json.load(open(args.map)) if args.map else {}
    forced_types = user_map.get("types", {})
    forced_rights = user_map.get("rights", {})
    for label, forced, canon in (("types", forced_types, canon_type), ("rights", forced_rights, canon_right)):
        for k, v in forced.items():
            if canon(v) is None:
                sys.exit(f"--map {label}[{k!r}] = {v!r} is not one of the allowed values")
            forced[k] = canon(v)
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
        # fill down blanks for product-level columns when a tier row leaves them empty, but only within the
        # same product: a new product id resets what was carried
        if rec.get("product_id") and rec["product_id"] != last_product.get("product_id"):
            last_product = {}
        for k in fill_down:
            if k in mapping:
                if rec.get(k, "") == "" and last_product.get(k):
                    rec[k] = last_product[k]
                elif rec.get(k):
                    last_product[k] = rec[k]
        if not rec.get("product_id") and not money(rec.get("list_price")):
            continue  # section or blank line
        n_data_rows += 1
        for fld in ("floor_price", "annual_revenue", "customers", "tier_min", "tier_max"):
            if fld in mapping and bad_money(rec.get(fld)):
                issues.append(f"Row {ri} ({rec.get('product_id','?')}): {fld} {rec.get(fld)!r} could not be read as a number (decimal commas and trailing text are not guessed); left blank")
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
            if rec.get("term_months"):
                issues.append(f"Row {ri} ({rec['product_id']}): term {rec['term_months']!r} not understood; term_months left blank")
            else:
                issues.append(f"Row {ri} ({rec['product_id']}): term not stated; term_months left blank (Unknown, not assumed)")
            tm = ""
        ccy_col = (rec.get("currency") or "").strip().upper()
        ccy_cells = {c for c in (cell_currency(rec.get("list_price")), cell_currency(rec.get("floor_price"))) if c}
        if len(ccy_cells) > 1:
            issues.append(f"Row {ri} ({rec['product_id']}): list and floor price name different currencies {sorted(ccy_cells)}; currency left blank")
            ccy = ""
        elif ccy_cells:
            ccy = next(iter(ccy_cells))
            if ccy_col and ccy_col != ccy:
                issues.append(f"Row {ri} ({rec['product_id']}): the price cell says {ccy} but the currency column says {ccy_col}; used {ccy}")
        else:
            ccy = ccy_col or (args.default_currency or "").upper()
            if not ccy:
                issues.append(f"Row {ri} ({rec['product_id']}): no currency in the file and no --default-currency; currency left blank")
        rev = money(rec.get("annual_revenue"))
        cust = money(rec.get("customers"))
        name = rec.get("product_name") or rec.get("product_id")
        given_type = canon_type(rec.get("product_type"))
        if rec.get("product_type") and given_type is None:
            issues.append(f"Row {ri} ({rec['product_id']}): type {rec['product_type']!r} is not data_license, api_access, software, service or other; worked out from the product words instead")
        ptype, conf, why = classify(name, rec.get("product_family"), rec.get("description"), rec.get("unit"),
                                    forced_types.get(name) or forced_types.get(rec.get("product_id")) or given_type or None)
        if given_type and not (forced_types.get(name) or forced_types.get(rec.get("product_id"))):
            ptype, conf, why = given_type, "high", "given in the file"
        scoped = ptype in SCOPE_TYPES
        use_right = forced_rights.get(name) or forced_rights.get(rec.get("product_id")) or ""
        if not use_right and rec.get("conferred_right"):
            use_right = canon_right(rec["conferred_right"]) or ""
            if not use_right:
                issues.append(f"Row {ri} ({rec['product_id']}): {rec['conferred_right']!r} is not one of the nine rights; granted right left blank (not stated)")
        ur_inferred = False
        right_basis = "stated" if use_right else ""
        if not use_right and scoped:
            use_right = infer_conferred_right(f"{name} {rec.get('description','')}")
            ur_inferred = bool(use_right)
            right_basis = "inferred" if use_right else ""
        if not scoped:
            use_right = ""
        out.append(OrderedDict(
            line_id="", product_id=rec.get("product_id") or slug(name), product_type=ptype, product_name=name,
            product_family=rec.get("product_family", ""), conferred_right=use_right, right_basis=right_basis,
            delivery=rec.get("delivery", ""), unit=rec.get("unit", ""),
            tier_min=int(tmin) if tmin is not None else "", tier_max=int(tmax) if tmax is not None else "",
            list_price=lp, floor_price="" if fp is None else fp, currency=ccy,
            term_months=tm, tier_model=args.tier_model or "", status="Existing", version=args.version,
            annual_revenue="" if rev is None else rev, customers="" if cust is None else int(cust),
            price_period="", source_row=ri,
            notes="; ".join(x for x in [f"type {ptype} ({conf}: {why})" if conf != "high" else "",
                                        "granted right inferred from the product words, confirm in contracts" if ur_inferred else "",
                                        "granted right not stated: say what the customer may do with it" if scoped and not use_right else ""] if x)))
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
    first_rev = {}
    for o in out:
        k = (o["product_id"], o["unit"], o["term_months"])
        if o["annual_revenue"] == "":
            continue
        if k not in first_rev:
            first_rev[k] = (o["annual_revenue"], o["customers"])
        elif (o["annual_revenue"], o["customers"]) == first_rev[k]:
            o["annual_revenue"] = ""
            o["customers"] = ""
        else:
            issues.append(f"{o['product_name']} ({o['unit']}): revenue differs between tier rows; kept on each row as per-tier revenue. If it is really a product total, the rights hand-off overstates it")
    if first_rev:
        assumptions.append("Where annual revenue and customer counts are identical on every tier row of a product they are taken as a product total and kept on the first tier only (so they are not double counted). If the source meant them per tier, the hand-off ranking understates them.")

    od = Path(args.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    with open(od / "price_book.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=STANDARD, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    # hand-off list for the product manager (rights pack)
    hand = OrderedDict()
    for o in out:
        if o["product_type"] not in SCOPE_TYPES:
            continue
        k = (o["product_id"], o["conferred_right"])
        h = hand.setdefault(k, {"name": o["product_name"], "type": o["product_type"], "rev": 0.0, "cust": 0, "lines": 0})
        h["lines"] += 1
        h["rev"] += float(o["annual_revenue"] or 0)
        h["cust"] += int(o["customers"] or 0)
    has_rev = any(h["rev"] for h in hand.values())
    ranked = sorted(hand.items(), key=lambda kv: (-(kv[1]["rev"] if has_rev else kv[1]["lines"]), kv[0]))
    with open(od / "product_rights_handoff.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["priority_rank", "product_id", "product_name", "product_type", "conferred_right", "price_lines",
                    "annual_revenue", "customers", "dataset_id", "data_form"])
        for i, ((pid, cr), h) in enumerate(ranked, 1):
            w.writerow([i, pid, h["name"], h["type"], cr, h["lines"], round(h["rev"], 2) if has_rev else "", h["cust"] or "", "", ""])

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
    L.append("| Type | Products | Lines |\n|---|---|---|")
    for t, items in sorted(by_type.items()):
        L.append(f"| {t} | {len({x['product_name'] for x in items})} | {len(items)} |")
    if low:
        L.append("\nProduct types inferred with less than high confidence (check these):\n")
        for n, (t, c, why) in low.items():
            L.append(f"- {n}: {t} ({c}; {why})")
    L.append("\n## What needs a human decision\n")
    nsc = sum(1 for o in out if o["product_type"] in SCOPE_TYPES and not o["conferred_right"])
    L.append(f"- Granted scope: {nsc} of {sum(1 for o in out if o['product_type'] in SCOPE_TYPES)} data and API lines do not say what the customer may do with the data or responses. Legacy price books rarely say. Find it in the customer contracts or API terms; until then treat the line as internal_use only and do not offer it for retention, resale or AI use.")
    L.append(f"- Floor price is missing on {len(missing_floor)} of {len(out)} lines. Floors are not invented. Set them with the data-price-setting skill (cost floor) or from Finance.")
    L.append("\n## Issues\n")
    L.extend([f"- {i}" for i in issues] or ["- None"])
    L.append("\n## Assumptions\n")
    for a in assumptions + [
        "All imported lines have status Existing (current prices in force). Nothing is Approved or Proposed.",
        (f"tier_model is set to {args.tier_model} for every line; confirm how the tiers actually bill." if args.tier_model
         else "tier_model is blank: how the tiers bill (every unit at the tier price, or each tier its own units) is Unknown. Re-run with --tier-model once known."),
        (f"Currency {args.default_currency.upper()} was used only where the source named none." if args.default_currency
         else "No --default-currency was given: lines whose file names no currency have a blank currency."),
        "Price period (monthly or annual) is not detected: check the unit text.",
        "The price book records the rights we grant the customer. Whether we hold the rights to grant them is assessed by the product manager with the rights pack; the pricing desk assumes we do. Give product_rights_handoff.csv to the product manager."]:
        L.append(f"- {a}")
    L.append("\n## Next steps\n")
    L.append("1. Run check_price_book.py on price_book.csv (strategy mode). Fix errors; floors and granted scope show as warnings.")
    L.append("2. Check the product types and the granted right on each data and API line. Correct them with --map or by editing price_book.csv.")
    L.append("3. Give product_rights_handoff.csv to the product manager for the rights check. It does not block pricing work.")
    (od / "import_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"Read {n_data_rows} rows, wrote {len(out)} price lines, {len(hand)} data or API products for the rights hand-off to {od}")
    print(f"Product types: " + ", ".join(f"{t} {len(v)}" for t, v in sorted(by_type.items())))
    print(f"Floor price missing on {len(missing_floor)} lines; {len(issues)} import issues")


if __name__ == "__main__":
    main()
