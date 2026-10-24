#!/usr/bin/env python3
"""Check a price book for consistency.

Works for any product the pricing desk prices: data licences, API access, software, services.

The price book prices what we GRANT the customer. For data products and API access, each line says
which right it grants (conferred_right): what the customer may do with the data or the API responses.
Whether we hold the rights needed to grant it is assessed separately by the product manager (the
rights pack). The checker assumes we do.

Usage:
  python check_price_book.py --pricebook PRICEBOOK.csv [--mode strategy|release] [--lines-csv OUT.csv]

Modes:
  strategy (default)  For pricing strategy and review. A missing floor price, or a data or API line that does
                      not say which right it grants, is a warning.
  release             Use before a price book goes out for quoting. Those two are errors.

Price book CSV columns (header row required)
  Required: line_id, unit, tier_min, tier_max, list_price, currency, term_months, product_id
  Optional: product_type (data_license, api_access, software, service, other), product_name,
            product_family, conferred_right (the right granted to the customer: one of the nine),
            right_basis (stated, inferred or assumed: how the right was decided),
            minimum_commitment, retention_term, audit_right (terms that must travel with any right that keeps
            or reuses data),
            delivery, floor_price, tier_model (all_units or graduated), status, version,
            annual_revenue, customers
  An older column named use_right is read as conferred_right. A dataset_id column, if present, is
  ignored by the checker (it is for the rights pack).
  tier_max may be blank for the last tier.

The nine rights: internal_use, internal_analytics_shared_outputs, display_to_third_parties,
redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding,
ai_evaluation. internal_use is the narrowest: the customer uses the data or API responses only in its own
business. Anything broader is a separate, higher-priced right. See references/granted-scope.md.

Checks (E = error, W = warning)
  E  missing columns, unparsable numbers, duplicate lines
  E  list price missing or not positive; floor above list
  W  floor price missing (E in release mode)
  E  line_id blank or duplicated; currency, term_months or tier_min blank; non-finite or non-positive numbers
  E  no lines at all (release mode)
  W  product_type blank or unknown (E in release mode: the granted-right gate cannot be applied)
  W  right_basis inferred or assumed (E in release mode: a right must be stated, not guessed)
  W  a right that keeps or reuses data (everything broader than internal_use except display_to_third_parties)
     without minimum_commitment, retention_term and audit_right (E in release mode)
  W  data or API line with no conferred_right (E in release mode); W conferred_right not one of the nine
  E  tier overlap; W tier gap
  E  unit price rises with volume
  E  volume cliff in all_units tiers (more volume costs less in total)
  E  a broader conferred right priced below internal_use for the same product, delivery, unit, tier
  W  multiple currencies; W mixed product types sharing one product_id
Exit code 1 if any error.
"""
import argparse
import csv
import math
import sys
from collections import defaultdict

RIGHTS = [
    "internal_use", "internal_analytics_shared_outputs", "display_to_third_parties", "redistribution_resale",
    "derivative_data_product", "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
]
BROADER_THAN_INTERNAL = set(RIGHTS) - {"internal_use"}
PRODUCT_TYPES = {"data_license", "api_access", "software", "service", "other"}
SCOPE_TYPES = {"data_license", "api_access"}
REQUIRED = ["line_id", "unit", "tier_min", "tier_max", "list_price", "currency", "term_months"]
# Rights that keep, reuse or pass on data. They carry a minimum commitment, a retention term and audit (operating rule 3).
KEEPING_RIGHTS = set(RIGHTS) - {"internal_use", "display_to_third_parties"}
TERM_FIELDS = ["minimum_commitment", "retention_term", "audit_right"]


def blank(v):
    return v is None or str(v).strip() == "" or str(v).strip().lower() in ("unknown", "tbd", "n/a")


def num(value, line, field, issues):
    if value is None or str(value).strip() == "":
        return None
    try:
        x = float(str(value).replace(",", ""))
    except ValueError:
        issues.append(("E", line, f"{field} is not a number: {value!r}"))
        return None
    if not math.isfinite(x):
        issues.append(("E", line, f"{field} is not a finite number: {value!r}"))
        return None
    return x


def fmt(x):
    return "no limit" if x == math.inf else f"{x:,.0f}"


def get(row, key):
    return (row.get(key) or "").strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pricebook", required=True)
    ap.add_argument("--mode", choices=["strategy", "release"], default="strategy")
    ap.add_argument("--lines-csv", help="Write the price book lines with product_type and conferred_right filled in")
    args = ap.parse_args()
    release = args.mode == "release"

    try:
        f = open(args.pricebook, newline="", encoding="utf-8-sig")
    except OSError as e:
        sys.exit(f"Cannot read the price book {args.pricebook}: {e.strerror or e}")
    with f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        missing = [c for c in REQUIRED if c not in fields]
        if "product_id" not in fields:
            missing.append("product_id")
        if missing:
            sys.exit(f"Price book is missing columns: {', '.join(missing)}")
        lines = list(reader)
    legacy = "use_right" in fields and "conferred_right" not in fields

    issues = []
    if legacy:
        issues.append(("W", "price book", "column use_right is read as conferred_right (the right granted to the customer). Rename it"))
    seen, parsed, no_scope, seen_ids = set(), [], [], set()
    if not lines:
        issues.append(("E" if release else "W", "price book", "the price book has no lines"))
    for row in lines:
        lid = get(row, "line_id") or "(no line_id)"
        pid = get(row, "product_id")
        cr = get(row, "conferred_right") or get(row, "use_right")
        ptype_raw = get(row, "product_type")
        ptype = ptype_raw or ("data_license" if get(row, "dataset_id") else "other")
        if ptype_raw and ptype_raw not in PRODUCT_TYPES:
            issues.append(("E" if release else "W", lid, f"product_type {ptype_raw!r} is not one of {', '.join(sorted(PRODUCT_TYPES))}; the granted-right gate cannot be applied"))
        elif not ptype_raw:
            issues.append(("E" if release else "W", lid, "product_type is blank; the granted-right gate cannot be applied. Set it (data_license, api_access, software, service, other)"))
        if get(row, "line_id") == "":
            issues.append(("E", lid, "line_id is blank"))
        elif get(row, "line_id") in seen_ids:
            issues.append(("E", lid, "line_id is duplicated"))
        seen_ids.add(get(row, "line_id"))
        if get(row, "currency") == "":
            issues.append(("E", lid, "currency is blank"))
        if get(row, "term_months") == "":
            issues.append(("E", lid, "term_months is blank (use 0 or 1 for one-time prices and say so in notes)"))
        else:
            tm = num(row.get("term_months"), lid, "term_months", issues)
            if tm is not None and tm < 0:
                issues.append(("E", lid, "term_months is negative"))
        if get(row, "tier_min") == "":
            issues.append(("E", lid, "tier_min is blank (use 0 or 1 for the first tier); the line cannot be tier-checked"))
        tmin = num(row.get("tier_min"), lid, "tier_min", issues)
        tmax = num(row.get("tier_max"), lid, "tier_max", issues)
        lp = num(row.get("list_price"), lid, "list_price", issues)
        fp = num(row.get("floor_price"), lid, "floor_price", issues)
        key = (pid, cr, get(row, "delivery"), get(row, "unit"), get(row, "currency"), get(row, "term_months"), tmin)
        if key in seen:
            issues.append(("E", lid, "duplicate line for the same product, conferred right, delivery, unit, tier, currency, and term"))
        seen.add(key)

        if ptype in SCOPE_TYPES and not cr:
            no_scope.append(lid)
        if cr and cr not in RIGHTS:
            issues.append(("W", lid, f"conferred_right {cr!r} is not one of the nine rights: {', '.join(RIGHTS)}"))
        basis = get(row, "right_basis").lower()
        if cr and basis in ("inferred", "assumed"):
            issues.append(("E" if release else "W", lid, f"conferred_right {cr} is {basis}, not stated. Confirm it from the contract or product definition and set right_basis to stated"))
        if cr in KEEPING_RIGHTS and ptype in SCOPE_TYPES:
            miss_terms = [f for f in TERM_FIELDS if blank(row.get(f))]
            if miss_terms:
                issues.append(("E" if release else "W", lid, f"{cr} keeps or reuses data, so it needs {', '.join(miss_terms)} (operating rule 3)"))
        if tmin is not None and tmin < 0:
            issues.append(("E", lid, "tier_min is negative"))
        if tmin is not None and tmax is not None and tmax < tmin:
            issues.append(("E", lid, f"tier_max {tmax:g} is below tier_min {tmin:g}"))
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
        parsed.append({"row": row, "lid": lid, "pid": pid, "ptype": ptype, "cr": cr, "tmin": tmin, "tmax": tmax, "lp": lp, "fp": fp})

    if no_scope:
        shown = ", ".join(no_scope[:8]) + (f" and {len(no_scope) - 8} more" if len(no_scope) > 8 else "")
        issues.append(("E" if release else "W", f"{len(no_scope)} data or API lines",
                       f"no conferred_right ({shown}). Say what the customer may do with the data or API responses; "
                       "internal_use means only their own use, and keeping, reselling or AI use are separate, higher-priced rights"))
    groups = defaultdict(list)
    for p in parsed:
        r = p["row"]
        groups[(p["pid"], p["cr"], get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"))].append(p)
    for items in groups.values():
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
                    total_a, total_b = a["tmax"] * a["lp"], b["tmin"] * b["lp"]
                    if total_b < total_a:
                        issues.append(("E", f"{a['lid']} / {b['lid']}", f"volume cliff: {fmt(b['tmin'])} units costs {total_b:,.2f} but {fmt(a['tmax'])} units costs {total_a:,.2f}"))

    base = {}
    for p in parsed:
        r = p["row"]
        fam = get(r, "product_family") or p["pid"]
        if p["cr"] == "internal_use" and p["lp"] is not None:
            base[(fam, get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"), p["tmin"])] = p["lp"]
    for p in parsed:
        r = p["row"]
        fam = get(r, "product_family") or p["pid"]
        if p["cr"] in BROADER_THAN_INTERNAL and p["lp"] is not None:
            k = (fam, get(r, "delivery"), get(r, "unit"), get(r, "currency"), get(r, "term_months"), p["tmin"])
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

    if args.lines_csv:
        cols = list(lines[0].keys()) if lines else []
        extra = [c for c in ("product_type", "conferred_right") if c not in cols]
        with open(args.lines_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols + extra)
            w.writeheader()
            for p in parsed:
                out = dict(p["row"])
                out["product_type"], out["conferred_right"] = p["ptype"], p["cr"]
                w.writerow(out)

    scoped = [p for p in parsed if p["ptype"] in SCOPE_TYPES]
    by_right = defaultdict(int)
    for p in scoped:
        by_right[p["cr"] or "(not stated)"] += 1
    errors = [i for i in issues if i[0] == "E"]
    warns = [i for i in issues if i[0] == "W"]
    print(f"Mode: {args.mode} | lines checked: {len(parsed)} | errors: {len(errors)} | warnings: {len(warns)}")
    if scoped:
        print("Granted scope on data and API lines: " + ", ".join(f"{k} {v}" for k, v in sorted(by_right.items())))
    for sev, where, msg in issues:
        print(f"[{sev}] {where}: {msg}")
    if not issues:
        print("No issues found.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
