#!/usr/bin/env python3
"""Check a price book for consistency, and (where rights matter) against the data rights register.

Works for any product the pricing desk prices: data licences, API access, software, services.
The rights register only applies to lines that carry data or third-party content.

Usage:
  python check_price_book.py --pricebook PRICEBOOK.csv [--register REGISTER.xlsx]
         [--mode strategy|release] [--exposure-csv OUT.csv] [--lines-csv OUT.csv]

Modes:
  strategy (default)  Provisional pricing is allowed. A line whose rights are not confirmed by
                      Legal is labelled rights_basis=Provisional and reported as a warning, never an
                      error, so the desk can run a pricing strategy before Legal responds. A missing
                      register is allowed. The exposure report ranks the rights questions by what
                      they put at risk, to focus intake and Legal time.
  release             Use before a price book is released for quoting. Any line whose rights are not
                      confirmed, or whose floor price is missing, is an error.
  Prohibited is an error in both modes only when Legal has confirmed it. If the register shows
  Prohibited but Legal has not confirmed, the line is Contradicted: priced against the evidence, a
  warning in strategy mode, an error in release mode, and the top of the intake priority list.

Price book CSV columns (header row required)
  Required: line_id, unit, tier_min, tier_max, list_price, currency, term_months, and one of
            product_id or dataset_id
  Optional: product_type (data_license, api_access, software, service, other), product_name,
            product_family, dataset_id, use_right, delivery, floor_price, tier_model (all_units or
            graduated), status, version, base_fee, annual_revenue, customers,
            rights_relevance (Required, Possible, None)
  Older price books with dataset_id and no product_id or product_type still work (treated as data_license).
  tier_max may be blank for the last tier.

Rights relevance (when not given): data_license = Required, api_access = Possible, others = None.
A line with a dataset_id is Required. Possible lines with no dataset_id get a warning to decide.

Rights basis per line
  N/A          rights do not apply to this product line
  Confirmed    register row is Granted or Conditional and legal_confirmed = Yes
  Provisional  anything else: no register, dataset or use right not in the register, Unknown,
               or Granted/Conditional but not yet confirmed by Legal
  Contradicted register row is Prohibited but Legal has not confirmed it (intake evidence says no)
  Blocked      register row is Prohibited and confirmed by Legal

Checks (E = error, W = warning)
  E  missing columns, unparsable numbers, duplicate lines
  E  list price missing or not positive; floor above list
  W  floor price missing (E in release mode)
  E  Prohibited rights confirmed by Legal; W Contradicted rights (E in release mode)
  W  Provisional rights (E in release mode); W Conditional rights (conditions must travel with price)
  E  tier overlap; W tier gap
  E  unit price rises with volume
  E  volume cliff in all_units tiers (more volume costs less in total)
  E  a broader use right priced below internal_use for the same product, dataset, delivery, unit, tier
  W  multiple currencies; W mixed product types sharing one product_id
Exit code 1 if any error.
"""
import argparse
import csv
import math
import sys
from collections import defaultdict

BROADER_THAN_INTERNAL = {
    "internal_analytics_shared_outputs", "display_to_third_parties", "redistribution_resale",
    "derivative_data_product", "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
}
HIGH_RISK_USES = {
    "redistribution_resale", "derivative_data_product", "display_to_third_parties",
    "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
}
PRODUCT_TYPES = {"data_license", "api_access", "software", "service", "other"}
REQUIRED = ["line_id", "unit", "tier_min", "tier_max", "list_price", "currency", "term_months"]


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pricebook", required=True)
    ap.add_argument("--register", help="Register workbook (.xlsx). Optional in strategy mode.")
    ap.add_argument("--mode", choices=["strategy", "release"], default="strategy")
    ap.add_argument("--exposure-csv", help="Write the rights exposure and intake priority report here")
    ap.add_argument("--lines-csv", help="Write the price book lines with rights_basis and notes here")
    args = ap.parse_args()
    release = args.mode == "release"

    datasets, rights = {}, {}
    if args.register:
        from openpyxl import load_workbook
        wb = load_workbook(args.register, read_only=True, data_only=True)
        datasets = {r["dataset_id"]: r for r in read_sheet(wb, "Datasets") if r.get("dataset_id")}
        for r in read_sheet(wb, "Use_Rights"):
            rights[(r.get("dataset_id"), r.get("use_right"))] = r

    with open(args.pricebook, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        missing = [c for c in REQUIRED if c not in fields]
        if "product_id" not in fields and "dataset_id" not in fields:
            missing.append("product_id (or dataset_id)")
        if missing:
            sys.exit(f"Price book is missing columns: {', '.join(missing)}")
        lines = list(reader)

    issues = []
    seen = set()
    parsed = []
    for row in lines:
        lid = get(row, "line_id") or "(no line_id)"
        ds, ur = get(row, "dataset_id"), get(row, "use_right")
        pid = get(row, "product_id") or ds
        ptype = get(row, "product_type") or ("data_license" if ds else "other")
        if ptype not in PRODUCT_TYPES:
            issues.append(("W", lid, f"product_type {ptype!r} is not one of {', '.join(sorted(PRODUCT_TYPES))}"))
        tmin = num(row.get("tier_min"), lid, "tier_min", issues)
        tmax = num(row.get("tier_max"), lid, "tier_max", issues)
        lp = num(row.get("list_price"), lid, "list_price", issues)
        fp = num(row.get("floor_price"), lid, "floor_price", issues)
        rev = num(row.get("annual_revenue"), lid, "annual_revenue", issues)
        cust = num(row.get("customers"), lid, "customers", issues)
        key = (pid, ds, ur, get(row, "delivery"), get(row, "unit"), get(row, "currency"), get(row, "term_months"), tmin)
        if key in seen:
            issues.append(("E", lid, "duplicate line for the same product, dataset, use right, delivery, unit, tier, currency, and term"))
        seen.add(key)

        # Rights relevance
        rel = get(row, "rights_relevance")
        if rel not in ("Required", "Possible", "None"):
            rel = "Required" if (ptype == "data_license" or ds) else ("Possible" if ptype == "api_access" else "None")
        basis, note, reg_status, confirmed = "N/A", "", "", ""
        if rel == "Possible" and not ds:
            issues.append(("W", lid, "rights relevance is Possible (API responses may carry supplier or third-party content): decide, and add a dataset_id if so"))
        if rel in ("Required",) or (rel == "Possible" and ds):
            if not args.register:
                basis, note = "Provisional", "no register supplied"
            elif not ds:
                basis, note = "Provisional", "no dataset_id on the line"
            elif ds not in datasets:
                basis, note = "Provisional", "dataset not in the register"
            elif not ur:
                basis, note = "Provisional", "use right not stated on the line"
            else:
                r = rights.get((ds, ur))
                if r is None:
                    basis, note = "Provisional", "no register row for this use right"
                else:
                    reg_status = r.get("status", "")
                    confirmed = r.get("legal_confirmed", "")
                    if reg_status == "Prohibited" and confirmed == "Yes":
                        basis, note = "Blocked", "Legal confirmed Prohibited"
                    elif reg_status == "Prohibited":
                        basis, note = "Contradicted", "register evidence says Prohibited, not yet confirmed by Legal"
                    elif confirmed == "Yes" and reg_status in ("Granted", "Conditional"):
                        basis = "Confirmed"
                        if reg_status == "Conditional":
                            issues.append(("W", lid, f"{ds} / {ur} is Conditional: conditions must be stated with the price"))
                    elif confirmed == "Yes":
                        basis, note = "Provisional", f"Legal confirmed status {reg_status or 'blank'}"
                    else:
                        basis, note = "Provisional", f"register status {reg_status or 'blank'}, not confirmed by Legal"
            if basis == "Blocked":
                issues.append(("E", lid, f"{ds} / {ur}: {note}; cannot be priced"))
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

        parsed.append({"row": row, "lid": lid, "pid": pid, "ptype": ptype, "ds": ds, "ur": ur, "tmin": tmin, "tmax": tmax,
                       "lp": lp, "fp": fp, "rev": rev, "cust": cust, "rel": rel, "basis": basis, "note": note,
                       "reg_status": reg_status, "confirmed": confirmed})

    # Tier checks by group
    groups = defaultdict(list)
    for p in parsed:
        r = p["row"]
        groups[(p["pid"], p["ds"], p["ur"], get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"))].append(p)

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

    # Use-right ladder against internal_use
    base = {}
    for p in parsed:
        r = p["row"]
        if p["ur"] == "internal_use" and p["lp"] is not None:
            base[(p["pid"], p["ds"], get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"), p["tmin"])] = p["lp"]
    for p in parsed:
        r = p["row"]
        if p["ur"] in BROADER_THAN_INTERNAL and p["lp"] is not None:
            k = (p["pid"], p["ds"], get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"), p["tmin"])
            if k in base and p["lp"] < base[k]:
                issues.append(("E", p["lid"], f"{p['ur']} list price {p['lp']} is below internal_use {base[k]} for the same tier"))

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
        extra = [c for c in ("product_type", "rights_relevance", "rights_basis", "rights_note") if c not in cols]
        with open(args.lines_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols + extra)
            w.writeheader()
            for p in parsed:
                out = dict(p["row"])
                out["product_type"] = p["ptype"]
                out["rights_relevance"] = p["rel"]
                out["rights_basis"] = p["basis"]
                out["rights_note"] = p["note"]
                w.writerow(out)

    exposure = []
    if args.exposure_csv:
        agg = {}
        for p in parsed:
            if p["basis"] in ("N/A", "Confirmed"):
                continue
            k = (p["ds"] or "(no dataset_id)", p["ur"] or "(not stated)")
            a = agg.setdefault(k, {"basis": p["basis"], "note": p["note"], "reg_status": p["reg_status"], "lines": 0,
                                   "rev": 0.0, "cust": 0.0, "products": set(), "types": set()})
            a["lines"] += 1
            a["rev"] += p["rev"] or 0.0
            a["cust"] += p["cust"] or 0.0
            a["products"].add(p["pid"])
            a["types"].add(p["ptype"])
            for worse in ("Blocked", "Contradicted"):
                if p["basis"] == worse and a["basis"] not in ("Blocked",):
                    a["basis"] = worse
        for (ds, ur), a in agg.items():
            weight = 3 if ur in HIGH_RISK_USES else 1
            size = a["rev"] if has_rev else float(a["lines"])
            exposure.append({
                "dataset_id": ds, "use_right": ur, "rights_basis": a["basis"], "register_status": a["reg_status"],
                "reason": a["note"], "lines": a["lines"], "products": ";".join(sorted(a["products"])),
                "product_types": ";".join(sorted(a["types"])), "annual_revenue": round(a["rev"], 2) if has_rev else "",
                "customers": round(a["cust"]) if a["cust"] else "", "risk_weight": weight,
                "priority_score": round(size * weight * (2 if a["basis"] in ("Blocked", "Contradicted") else 1), 2),
            })
        exposure.sort(key=lambda e: (-e["priority_score"], e["dataset_id"], e["use_right"]))
        for i, e in enumerate(exposure, 1):
            e["priority_rank"] = i
        cols = ["priority_rank", "dataset_id", "use_right", "rights_basis", "register_status", "reason", "lines", "products",
                "product_types", "annual_revenue", "customers", "risk_weight", "priority_score"]
        with open(args.exposure_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(exposure)

    errors = [i for i in issues if i[0] == "E"]
    warns = [i for i in issues if i[0] == "W"]
    print(f"Mode: {args.mode} | lines checked: {len(parsed)} | register datasets: {len(datasets)} | errors: {len(errors)} | warnings: {len(warns)}")
    bits = []
    for b in ("Confirmed", "Provisional", "Contradicted", "Blocked", "N/A"):
        if basis_counts.get(b):
            bits.append(f"{b} {basis_counts[b]}" + (f" ({basis_rev[b]:,.0f} annual revenue)" if has_rev else ""))
    print("Rights basis: " + (", ".join(bits) if bits else "none"))
    if exposure:
        print("Top intake priorities (score = revenue or line count x risk weight; Blocked and Contradicted doubled):")
        for e in exposure[:5]:
            print(f"  {e['priority_rank']}. {e['dataset_id']} / {e['use_right']} [{e['rights_basis']}] score {e['priority_score']}")
    for sev, where, msg in issues:
        print(f"[{sev}] {where}: {msg}")
    if not issues:
        print("No issues found.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
