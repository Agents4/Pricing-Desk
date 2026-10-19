#!/usr/bin/env python3
"""Check a data-licensing price book against the data rights register.

Usage:
  python check_price_book.py --register REGISTER.xlsx --pricebook PRICEBOOK.csv

Price book CSV columns (header row required):
  line_id, dataset_id, use_right, delivery, unit, tier_min, tier_max,
  list_price, floor_price, currency, term_months, tier_model, status, version
Optional: base_fee. tier_max may be blank for the last tier. tier_model is
all_units (default) or graduated.

Checks (E = error, W = warning):
  E  missing columns, unparsable numbers, duplicate lines
  E  dataset not in register, or use right not confirmed by Legal and Granted/Conditional
  W  use right is Conditional (conditions must travel with the price)
  E  floor above list, or non-positive prices
  E  tier overlap; W tier gap
  E  unit price rises with volume
  E  volume cliff in all_units tiers (more volume costs less in total)
  E  a broader use right priced below internal_use for the same dataset, delivery, unit, tier
Exit code 1 if any error.
"""
import argparse
import csv
import math
import sys
from collections import defaultdict

from openpyxl import load_workbook

REQUIRED = [
    "line_id", "dataset_id", "use_right", "delivery", "unit", "tier_min", "tier_max",
    "list_price", "floor_price", "currency", "term_months",
]
BROADER_THAN_INTERNAL = {
    "internal_analytics_shared_outputs", "display_to_third_parties", "redistribution_resale",
    "derivative_data_product", "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
}


def read_sheet(wb, name):
    if name not in wb.sheetnames:
        sys.exit(f"Register is missing sheet: {name}")
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--register", required=True)
    ap.add_argument("--pricebook", required=True)
    args = ap.parse_args()

    wb = load_workbook(args.register, read_only=True, data_only=True)
    datasets = {r["dataset_id"]: r for r in read_sheet(wb, "Datasets") if r.get("dataset_id")}
    rights = {}
    for r in read_sheet(wb, "Use_Rights"):
        rights[(r.get("dataset_id"), r.get("use_right"))] = r

    with open(args.pricebook, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"Price book is missing columns: {', '.join(missing)}")
        lines = list(reader)

    issues = []
    seen = set()
    parsed = []
    for row in lines:
        lid = row["line_id"] or "(no line_id)"
        ds, ur = row["dataset_id"], row["use_right"]
        tmin = num(row["tier_min"], lid, "tier_min", issues)
        tmax = num(row["tier_max"], lid, "tier_max", issues)
        lp = num(row["list_price"], lid, "list_price", issues)
        fp = num(row["floor_price"], lid, "floor_price", issues)
        key = (ds, ur, row["delivery"], row["unit"], row["currency"], row["term_months"], tmin)
        if key in seen:
            issues.append(("E", lid, "duplicate line for the same dataset, use right, delivery, unit, tier, currency, and term"))
        seen.add(key)

        if ds not in datasets:
            issues.append(("E", lid, f"dataset {ds} is not in the register"))
        else:
            r = rights.get((ds, ur))
            if r is None:
                issues.append(("E", lid, f"no register row for {ds} / {ur}: rights unknown, do not price"))
            else:
                confirmed = r.get("legal_confirmed", "") == "Yes"
                status = r.get("status", "")
                if not confirmed:
                    issues.append(("E", lid, f"{ds} / {ur} is not confirmed by Legal: treat as unknown, do not price"))
                elif status == "Prohibited" or status == "Unknown":
                    issues.append(("E", lid, f"{ds} / {ur} has status {status}: cannot be priced"))
                elif status == "Conditional":
                    issues.append(("W", lid, f"{ds} / {ur} is Conditional: conditions must be stated with the price"))

        if lp is not None and fp is not None:
            if lp <= 0 or fp <= 0:
                issues.append(("E", lid, "prices must be positive"))
            if fp > lp:
                issues.append(("E", lid, f"floor price {fp} is above list price {lp}"))
        elif lp is None or fp is None:
            issues.append(("E", lid, "list_price and floor_price are required"))

        parsed.append({"row": row, "lid": lid, "tmin": tmin, "tmax": tmax, "lp": lp, "fp": fp})

    # Tier checks by group
    groups = defaultdict(list)
    for p in parsed:
        r = p["row"]
        groups[(r["dataset_id"], r["use_right"], r["delivery"], r["unit"], r["currency"], r["term_months"])].append(p)

    for g, items in groups.items():
        items = [i for i in items if i["tmin"] is not None]
        items.sort(key=lambda i: i["tmin"])
        for a, b in zip(items, items[1:]):
            a_max = a["tmax"] if a["tmax"] is not None else math.inf
            if b["tmin"] <= a_max:
                issues.append(("E", f"{a['lid']} / {b['lid']}", f"tiers overlap ({a['tmin']}-{a_max} and from {b['tmin']})"))
            elif b["tmin"] - a_max > 1:
                issues.append(("W", f"{a['lid']} / {b['lid']}", f"gap between tiers ({a_max} to {b['tmin']})"))
            if a["lp"] is not None and b["lp"] is not None:
                if b["lp"] > a["lp"]:
                    issues.append(("E", f"{a['lid']} / {b['lid']}", f"unit price rises with volume ({a['lp']} to {b['lp']})"))
                model = (b["row"].get("tier_model") or "all_units").strip() or "all_units"
                if model == "all_units" and a["tmax"] is not None:
                    total_a = a["tmax"] * a["lp"]
                    total_b = b["tmin"] * b["lp"]
                    if total_b < total_a:
                        issues.append(("E", f"{a['lid']} / {b['lid']}", f"volume cliff: {b['tmin']:g} units costs {total_b:,.2f} but {a['tmax']:g} units costs {total_a:,.2f}"))

    # Use-right ladder against internal_use
    base = {}
    for p in parsed:
        r = p["row"]
        if r["use_right"] == "internal_use" and p["lp"] is not None:
            base[(r["dataset_id"], r["delivery"], r["unit"], r["currency"], r["term_months"], p["tmin"])] = p["lp"]
    for p in parsed:
        r = p["row"]
        if r["use_right"] in BROADER_THAN_INTERNAL and p["lp"] is not None:
            k = (r["dataset_id"], r["delivery"], r["unit"], r["currency"], r["term_months"], p["tmin"])
            if k in base and p["lp"] < base[k]:
                issues.append(("E", p["lid"], f"{r['use_right']} list price {p['lp']} is below internal_use {base[k]} for the same tier"))

    currencies = {p["row"]["currency"] for p in parsed}
    if len(currencies) > 1:
        issues.append(("W", "price book", f"multiple currencies: {', '.join(sorted(currencies))}"))

    errors = [i for i in issues if i[0] == "E"]
    warns = [i for i in issues if i[0] == "W"]
    print(f"Lines checked: {len(parsed)} | datasets in register: {len(datasets)} | errors: {len(errors)} | warnings: {len(warns)}")
    for sev, where, msg in issues:
        print(f"[{sev}] {where}: {msg}")
    if not issues:
        print("No issues found.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
