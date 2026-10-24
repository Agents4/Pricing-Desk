#!/usr/bin/env python3
"""Check a price book for consistency and, where data is involved, against the data rights register.

Works for any product the pricing desk prices: data licences, API access, software, services.

Two kinds of right are kept apart:
  held rights      what WE may do with a dataset. They live in the register (Use_Rights sheet).
  conferred rights what we grant the CUSTOMER on the product. They live in the price book
                   (conferred_right column).
We can only confer what we hold. The checker takes each line's conferred right, looks up in the
coverage table (references/rights-coverage.csv) which held rights the dataset must carry, and reads
those from the register.

Usage:
  python check_price_book.py --pricebook PRICEBOOK.csv [--register REGISTER.xlsx]
         [--mode strategy|release] [--coverage rights-coverage.csv]
         [--exposure-csv OUT.csv] [--lines-csv OUT.csv] [--backfill-csv OUT.csv]

Modes:
  strategy (default)  Provisional pricing is allowed. A line whose held rights are not confirmed by
                      Legal is labelled rights_basis=Provisional and reported as a warning, never an
                      error, so the desk can run a pricing strategy before Legal responds. A missing
                      register is allowed. The exposure report ranks the register questions by what
                      they put at risk, to focus intake and Legal time.
  release             Use before a price book is released for quoting. Any line whose held rights are
                      not confirmed, or whose floor price is missing, is an error.
  Blocked is an error in both modes. It needs Legal's confirmation. If the register shows Prohibited
  but Legal has not confirmed, the line is Contradicted: priced against the evidence, a warning in
  strategy mode, an error in release mode, and the top of the intake priority list.

Price book CSV columns (header row required)
  Required: line_id, unit, tier_min, tier_max, list_price, currency, term_months, and one of
            product_id or dataset_id
  Optional: product_type (data_license, api_access, software, service, other), product_name,
            product_family, dataset_id (one or several register datasets, separated by ;),
            conferred_right (the right granted to the customer), data_form (derived or passthrough,
            default derived), delivery, floor_price, tier_model (all_units or graduated), status,
            version, annual_revenue, customers, rights_relevance (Required, Possible, None)
  An older column named use_right is read as conferred_right, with a warning.
  Older price books with dataset_id and no product_id or product_type still work (treated as data_license).
  tier_max may be blank for the last tier.

Rights relevance (when not given): data_license = Required, api_access = Possible, others = None.
A line with a dataset_id is Required. Possible lines with no dataset_id get a warning to decide.

Rights basis per line (worst of its needed (dataset, held right) pairs)
  N/A          rights do not apply to this product line
  Confirmed    every needed held right is Granted or Conditional and legal_confirmed = Yes
  Provisional  anything else: no register, dataset or held right not in the register, Unknown,
               Granted/Conditional but not yet confirmed by Legal, no dataset or no conferred right on the line
  Contradicted a needed held right is Prohibited but Legal has not confirmed it (intake evidence says no)
  Blocked      a needed held right is Prohibited and confirmed by Legal

Checks (E = error, W = warning)
  E  missing columns, unparsable numbers, duplicate lines
  E  list price missing or not positive; floor above list
  W  floor price missing (E in release mode)
  E  held rights Prohibited and confirmed by Legal; W Contradicted (E in release mode)
  W  Provisional (E in release mode); W Conditional held rights (conditions must travel with price)
  E  tier overlap; W tier gap
  E  unit price rises with volume
  E  volume cliff in all_units tiers (more volume costs less in total)
  E  a broader conferred right priced below internal_use for the same product, dataset, delivery, unit, tier
  W  multiple currencies; W mixed product types sharing one product_id
Exit code 1 if any error.
"""
import argparse
import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

HELD_RIGHTS = [
    "internal_use", "internal_analytics_shared_outputs", "display_to_third_parties", "redistribution_resale",
    "derivative_data_product", "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
]
BROADER_THAN_INTERNAL = set(HELD_RIGHTS) - {"internal_use"}
HIGH_RISK_UNDER_CONFERRED = {
    "redistribution_resale", "derivative_data_product", "display_to_third_parties",
    "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
}
PRODUCT_TYPES = {"data_license", "api_access", "software", "service", "other"}
DATA_FORMS = {"derived", "passthrough"}
REQUIRED = ["line_id", "unit", "tier_min", "tier_max", "list_price", "currency", "term_months"]
BASIS_RANK = {"Confirmed": 0, "Provisional": 1, "Contradicted": 2, "Blocked": 3}
DEFAULT_COVERAGE = Path(__file__).resolve().parent.parent / "references" / "rights-coverage.csv"


def read_sheet(wb, name):
    if name not in wb.sheetnames:
        sys.exit(f"Register is missing sheet: {name}")
    rows = list(wb[name].iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    out = []
    for r in rows[1:]:
        if all(v is None or str(v).strip() == "" for v in r):
            continue
        out.append({headers[i]: ("" if v is None else str(v).strip()) for i, v in enumerate(r) if i < len(headers)})
    return out


def load_coverage(path):
    p = Path(path)
    if not p.exists():
        sys.exit(f"Coverage table not found: {p}. It maps each conferred right to the held rights it needs (rights-coverage.csv).")
    cov = {}
    with open(p, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            form, cr = (r.get("data_form") or "").strip(), (r.get("conferred_right") or "").strip()
            req = [x.strip() for x in (r.get("requires_held_rights") or "").split(";") if x.strip()]
            bad = [x for x in req + [cr] if x not in HELD_RIGHTS]
            if form not in DATA_FORMS or bad:
                sys.exit(f"Coverage table {p}: bad row {form!r}/{cr!r} ({', '.join(bad) or 'unknown data_form'})")
            cov[(form, cr)] = req
    return cov


def num(value, line, field, issues):
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        issues.append(("E", line, f"{field} is not a number: {value!r}"))
        return None


def fmt(x):
    return "no limit" if x == math.inf else f"{x:,.0f}"


def get(row, key):
    return (row.get(key) or "").strip()


def split_ids(text):
    return [x.strip() for x in re.split(r"[;|]", text or "") if x.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pricebook", required=True)
    ap.add_argument("--register", help="Register workbook (.xlsx). Optional in strategy mode.")
    ap.add_argument("--mode", choices=["strategy", "release"], default="strategy")
    ap.add_argument("--coverage", default=str(DEFAULT_COVERAGE),
                    help="Table mapping each conferred right to the held rights it needs (default: references/rights-coverage.csv)")
    ap.add_argument("--exposure-csv", help="Write the register questions ranked by what they put at risk (intake priority)")
    ap.add_argument("--lines-csv", help="Write the price book lines with rights_basis, held_rights_needed and notes here")
    ap.add_argument("--backfill-csv", help="Write Use_Rights rows to create for held rights the register does not have yet (status Unknown)")
    args = ap.parse_args()
    release = args.mode == "release"
    coverage = load_coverage(args.coverage)

    datasets, held = {}, {}
    if args.register:
        from openpyxl import load_workbook
        wb = load_workbook(args.register, read_only=True, data_only=True)
        datasets = {r["dataset_id"]: r for r in read_sheet(wb, "Datasets") if r.get("dataset_id")}
        for r in read_sheet(wb, "Use_Rights"):
            held[(r.get("dataset_id"), r.get("use_right"))] = r

    with open(args.pricebook, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        missing = [c for c in REQUIRED if c not in fields]
        if "product_id" not in fields and "dataset_id" not in fields:
            missing.append("product_id (or dataset_id)")
        if missing:
            sys.exit(f"Price book is missing columns: {', '.join(missing)}")
        lines = list(reader)
    legacy_col = "use_right" in fields and "conferred_right" not in fields

    issues = []
    if legacy_col:
        issues.append(("W", "price book", "column use_right is read as conferred_right (the right granted to the customer). Rename it; "
                       "the register's use_right column is a different thing: the right we hold"))

    def assess(ds, right):
        """One needed (dataset, held right) pair -> (basis, note, register status, legal_confirmed)."""
        if not args.register:
            return "Provisional", "no register supplied", "", ""
        if ds not in datasets:
            return "Provisional", "dataset not in the register", "", ""
        r = held.get((ds, right))
        if r is None:
            return "Provisional", "no register row for this held right", "", ""
        st, ok = r.get("status", ""), r.get("legal_confirmed", "")
        if st == "Prohibited" and ok == "Yes":
            return "Blocked", "Legal confirmed Prohibited", st, ok
        if st == "Prohibited":
            return "Contradicted", "register evidence says Prohibited, not yet confirmed by Legal", st, ok
        if ok == "Yes" and st in ("Granted", "Conditional"):
            return "Confirmed", "", st, ok
        if ok == "Yes":
            return "Provisional", f"Legal confirmed status {st or 'blank'}", st, ok
        return "Provisional", f"register status {st or 'blank'}, not confirmed by Legal", st, ok

    seen = set()
    parsed = []
    for row in lines:
        lid = get(row, "line_id") or "(no line_id)"
        ds_list = split_ids(get(row, "dataset_id"))
        ds = ";".join(ds_list)
        cr = get(row, "conferred_right") or get(row, "use_right")
        pid = get(row, "product_id") or (ds_list[0] if ds_list else "")
        ptype = get(row, "product_type") or ("data_license" if ds else "other")
        if ptype not in PRODUCT_TYPES:
            issues.append(("W", lid, f"product_type {ptype!r} is not one of {', '.join(sorted(PRODUCT_TYPES))}"))
        form = get(row, "data_form").lower() or "derived"
        if form not in DATA_FORMS:
            issues.append(("W", lid, f"data_form {form!r} is not derived or passthrough; treated as derived"))
            form = "derived"
        tmin = num(row.get("tier_min"), lid, "tier_min", issues)
        tmax = num(row.get("tier_max"), lid, "tier_max", issues)
        lp = num(row.get("list_price"), lid, "list_price", issues)
        fp = num(row.get("floor_price"), lid, "floor_price", issues)
        rev = num(row.get("annual_revenue"), lid, "annual_revenue", issues)
        cust = num(row.get("customers"), lid, "customers", issues)
        key = (pid, ds, cr, get(row, "delivery"), get(row, "unit"), get(row, "currency"), get(row, "term_months"), tmin)
        if key in seen:
            issues.append(("E", lid, "duplicate line for the same product, dataset, conferred right, delivery, unit, tier, currency, and term"))
        seen.add(key)

        rel = get(row, "rights_relevance")
        if rel not in ("Required", "Possible", "None"):
            rel = "Required" if (ptype == "data_license" or ds) else ("Possible" if ptype == "api_access" else "None")
        basis, note, pairs = "N/A", "", []   # pairs: (dataset, held right, basis, note, status, confirmed)
        if rel == "Possible" and not ds:
            issues.append(("W", lid, "rights relevance is Possible (API responses may carry supplier or third-party content): decide, and add a dataset_id if so"))
        if rel == "Required" or (rel == "Possible" and ds):
            if cr and cr not in HELD_RIGHTS:
                issues.append(("W", lid, f"conferred_right {cr!r} is not one of the nine rights: {', '.join(HELD_RIGHTS)}"))
            if not ds_list:
                basis, note = "Provisional", "no dataset_id on the line (what is the product built from?)"
            elif not cr:
                basis, note = "Provisional", "conferred right not stated on the line (what does the customer get?)"
                pairs = [(d, "(conferred right not stated)", "Provisional", note, "", "") for d in ds_list]
            elif (form, cr) not in coverage:
                basis, note = "Provisional", f"no coverage rule for {form} / {cr}"
                pairs = [(d, "(no coverage rule)", "Provisional", note, "", "") for d in ds_list]
            else:
                for d in ds_list:
                    need = list(coverage[(form, cr)])
                    src_type = (datasets.get(d) or {}).get("source_type", "")
                    if form == "derived" and src_type and src_type != "Derived" and "derivative_data_product" not in need:
                        need.insert(0, "derivative_data_product")   # built directly on a source dataset
                    for right in need:
                        b, n, st, ok = assess(d, right)
                        pairs.append((d, right, b, n, st, ok))
                worst = max(pairs, key=lambda x: BASIS_RANK[x[2]])
                basis = worst[2]
                bad = [p for p in pairs if p[2] == worst[2]]
                if basis != "Confirmed":
                    note = "; ".join(f"{p[0]} needs {p[1]}: {p[3]}" for p in bad[:3]) + (f" (+{len(bad) - 3} more)" if len(bad) > 3 else "")
                for p in pairs:
                    if p[2] == "Confirmed" and p[4] == "Conditional":
                        issues.append(("W", lid, f"{p[0]} / {p[1]} is Conditional: the conditions must be met by the product and stated with the price"))
            if basis == "Blocked":
                for p in pairs:
                    if p[2] == "Blocked":
                        issues.append(("E", lid, f"{p[0]} / {p[1]}: {p[3]}; the line confers {cr} and cannot be priced"))
            elif basis in ("Provisional", "Contradicted"):
                issues.append(("E" if release else "W", lid, f"rights are {basis.lower()} ({note}){': not for release until confirmed' if release else ''}"))

        if lp is None:
            issues.append(("E", lid, "list_price is required"))
        elif lp <= 0:
            issues.append(("E", lid, "list price must be positive"))
        if fp is None:
            issues.append(("E" if release else "W", lid, "floor_price is missing"))
        else:
            if fp <= 0:
                issues.append(("E", lid, "floor price must be positive"))
            if lp is not None and fp > lp:
                issues.append(("E", lid, f"floor price {fp} is above list price {lp}"))

        parsed.append({"row": row, "lid": lid, "pid": pid, "ptype": ptype, "ds": ds, "cr": cr, "form": form, "tmin": tmin, "tmax": tmax,
                       "lp": lp, "fp": fp, "rev": rev, "cust": cust, "rel": rel, "basis": basis, "note": note, "pairs": pairs})

    # Tier checks by group
    groups = defaultdict(list)
    for p in parsed:
        r = p["row"]
        groups[(p["pid"], p["ds"], p["cr"], get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"))].append(p)

    for g, items in groups.items():
        items = [i for i in items if i["tmin"] is not None]
        items.sort(key=lambda i: i["tmin"])
        for a, b in zip(items, items[1:]):
            a_max = a["tmax"] if a["tmax"] is not None else math.inf
            if b["tmin"] <= a_max:
                issues.append(("E", f"{a['lid']} / {b['lid']}", f"tiers overlap ({fmt(a['tmin'])}-{fmt(a_max)} and from {fmt(b['tmin'])})"))
            elif b["tmin"] - a_max > 1:
                issues.append(("W", f"{a['lid']} / {b['lid']}", f"gap between tiers ({fmt(a_max)} to {fmt(b['tmin'])})"))
            if a["lp"] is not None and b["lp"] is not None:
                if b["lp"] > a["lp"]:
                    issues.append(("E", f"{a['lid']} / {b['lid']}", f"unit price rises with volume ({a['lp']} to {b['lp']})"))
                model = get(b["row"], "tier_model") or "all_units"
                if model == "all_units" and a["tmax"] is not None:
                    total_a = a["tmax"] * a["lp"]
                    total_b = b["tmin"] * b["lp"]
                    if total_b < total_a:
                        issues.append(("E", f"{a['lid']} / {b['lid']}", f"volume cliff: {fmt(b['tmin'])} units costs {total_b:,.2f} but {fmt(a['tmax'])} units costs {total_a:,.2f}"))

    # Conferred-right ladder against internal_use
    base = {}
    for p in parsed:
        r = p["row"]
        if p["cr"] == "internal_use" and p["lp"] is not None:
            base[(p["pid"], p["ds"], get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"), p["tmin"])] = p["lp"]
    for p in parsed:
        r = p["row"]
        if p["cr"] in BROADER_THAN_INTERNAL and p["lp"] is not None:
            k = (p["pid"], p["ds"], get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"), p["tmin"])
            if k in base and p["lp"] < base[k]:
                issues.append(("E", p["lid"], f"{p['cr']} list price {p['lp']} is below internal_use {base[k]} for the same tier"))

    currencies = {get(p["row"], "currency") for p in parsed}
    if len(currencies) > 1:
        issues.append(("W", "price book", f"multiple currencies: {', '.join(sorted(c for c in currencies if c))}"))
    types_by_pid = defaultdict(set)
    for p in parsed:
        types_by_pid[p["pid"]].add(p["ptype"])
    for pid, t in types_by_pid.items():
        if len(t) > 1:
            issues.append(("W", pid, f"product_id used with several product types: {', '.join(sorted(t))}"))

    # Reports
    basis_counts = defaultdict(int)
    basis_rev = defaultdict(float)
    for p in parsed:
        basis_counts[p["basis"]] += 1
        basis_rev[p["basis"]] += p["rev"] or 0.0
    has_rev = any(p["rev"] for p in parsed)

    if args.lines_csv:
        cols = list(lines[0].keys()) if lines else []
        extra = [c for c in ("product_type", "conferred_right", "data_form", "rights_relevance", "held_rights_needed", "rights_basis", "rights_note")
                 if c not in cols]
        with open(args.lines_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols + extra)
            w.writeheader()
            for p in parsed:
                out = dict(p["row"])
                out["product_type"] = p["ptype"]
                out["conferred_right"] = p["cr"]
                out["data_form"] = p["form"] if p["basis"] != "N/A" else ""
                out["rights_relevance"] = p["rel"]
                out["held_rights_needed"] = ";".join(sorted({f"{d}:{r}" for d, r, *_ in p["pairs"]}))
                out["rights_basis"] = p["basis"]
                out["rights_note"] = p["note"]
                w.writerow(out)

    # Exposure: the register questions behind the unconfirmed lines, ranked by what they put at risk
    agg = {}
    for p in parsed:
        if p["basis"] in ("N/A", "Confirmed"):
            continue
        pairs = [x for x in p["pairs"] if x[2] != "Confirmed"] or [("(no dataset_id)", "(conferred right not stated)", p["basis"], p["note"], "", "")]
        for d, right, b, n, st, ok in pairs:
            a = agg.setdefault((d, right), {"basis": b, "note": n, "status": st, "lines": set(), "rev": 0.0, "cust": 0.0,
                                            "products": set(), "types": set(), "conferred": set(), "risk": 1})
            if p["lid"] not in a["lines"]:
                a["rev"] += p["rev"] or 0.0
                a["cust"] += p["cust"] or 0.0
            a["lines"].add(p["lid"])
            a["products"].add(p["pid"])
            a["types"].add(p["ptype"])
            if p["cr"]:
                a["conferred"].add(p["cr"])
            if p["cr"] in HIGH_RISK_UNDER_CONFERRED:
                a["risk"] = 3
    exposure = []
    for (d, right), a in agg.items():
        size = a["rev"] if has_rev else float(len(a["lines"]))
        exposure.append({
            "dataset_id": d, "held_right_needed": right, "rights_basis": a["basis"], "register_status": a["status"],
            "reason": a["note"], "lines": len(a["lines"]), "products": ";".join(sorted(a["products"])),
            "product_types": ";".join(sorted(a["types"])), "conferred_rights_depending": ";".join(sorted(a["conferred"])),
            "annual_revenue": round(a["rev"], 2) if has_rev else "", "customers": round(a["cust"]) if a["cust"] else "",
            "risk_weight": a["risk"],
            "priority_score": round(size * a["risk"] * (2 if a["basis"] in ("Blocked", "Contradicted") else 1), 2),
        })
    exposure.sort(key=lambda e: (-e["priority_score"], e["dataset_id"], e["held_right_needed"]))
    for i, e in enumerate(exposure, 1):
        e["priority_rank"] = i
    if args.exposure_csv:
        cols = ["priority_rank", "dataset_id", "held_right_needed", "rights_basis", "register_status", "reason", "lines", "products",
                "product_types", "conferred_rights_depending", "annual_revenue", "customers", "risk_weight", "priority_score"]
        with open(args.exposure_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(exposure)

    if args.backfill_csv:
        with open(args.backfill_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["dataset_id", "use_right", "status", "conditions", "evidence_ref", "legal_confirmed", "notes"])
            for e in exposure:
                if e["dataset_id"].startswith("(") or e["held_right_needed"].startswith("("):
                    continue
                if args.register and (e["dataset_id"], e["held_right_needed"]) in held:
                    continue   # the row exists; it is an open question, not a missing row
                w.writerow([e["dataset_id"], e["held_right_needed"], "Unknown", "", "", "",
                            f"Held right we need so we can confer: {e['conferred_rights_depending'] or 'not stated'}. Find the evidence in the source agreements; leave legal_confirmed to Legal"])

    errors = [i for i in issues if i[0] == "E"]
    warns = [i for i in issues if i[0] == "W"]
    print(f"Mode: {args.mode} | lines checked: {len(parsed)} | register datasets: {len(datasets)} | errors: {len(errors)} | warnings: {len(warns)}")
    bits = []
    for b in ("Confirmed", "Provisional", "Contradicted", "Blocked", "N/A"):
        if basis_counts.get(b):
            bits.append(f"{b} {basis_counts[b]}" + (f" ({basis_rev[b]:,.0f} annual revenue)" if has_rev else ""))
    print("Rights basis: " + (", ".join(bits) if bits else "none"))
    if exposure:
        print("Top register questions (held right we need; score = revenue or line count x risk weight; Blocked and Contradicted doubled):")
        for e in exposure[:5]:
            print(f"  {e['priority_rank']}. {e['dataset_id']} / {e['held_right_needed']} [{e['rights_basis']}] score {e['priority_score']}")
    for sev, where, msg in issues:
        print(f"[{sev}] {where}: {msg}")
    if not issues:
        print("No issues found.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
