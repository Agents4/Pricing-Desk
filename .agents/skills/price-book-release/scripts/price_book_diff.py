#!/usr/bin/env python3
"""Change log between two price book versions.

Usage:
  python price_book_diff.py --old old.csv --new new.csv [--md out.md]

Both files use the standard price book columns (line_id required). Lines are matched by line_id.
Reports added lines, removed lines, and changed fields (list_price, floor_price, conferred_right, unit, tier_min,
tier_max, term_months, currency, status). Percent change is shown for list and floor prices.
Every figure comes from the two files.
"""
import argparse
import csv
import sys

FIELDS = ["list_price", "floor_price", "conferred_right", "unit", "tier_min", "tier_max", "term_months", "currency", "status"]


def load(p):
    with open(p, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if rows and "line_id" not in rows[0]:
        sys.exit("%s has no line_id column" % p)
    return {r["line_id"].strip(): r for r in rows if (r.get("line_id") or "").strip()}


def num(s):
    try:
        return float((s or "").replace(",", "").strip())
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    old, new = load(a.old), load(a.new)
    added = [k for k in new if k not in old]
    removed = [k for k in old if k not in new]
    changes = []
    for k in new:
        if k not in old:
            continue
        for fld in FIELDS:
            o, n = (old[k].get(fld) or "").strip(), (new[k].get(fld) or "").strip()
            if o != n:
                pct = ""
                if fld in ("list_price", "floor_price") and num(o) and num(n) is not None:
                    pct = "%+.1f%%" % ((num(n) - num(o)) / num(o) * 100)
                changes.append((k, new[k].get("product_id", ""), fld, o or "(blank)", n or "(blank)", pct))
    out = ["Price book change log: %d line(s) added, %d removed, %d field change(s) on %d line(s)." % (
        len(added), len(removed), len(changes), len({c[0] for c in changes})), ""]
    if changes:
        out += ["| Line | Product | Field | Old | New | Change |", "|---|---|---|---|---|---|"]
        out += ["| %s | %s | %s | %s | %s | %s |" % c for c in changes]
        out.append("")
    if added:
        out += ["Added: " + ", ".join("%s (%s)" % (k, new[k].get("product_id", "")) for k in added), ""]
    if removed:
        out += ["Removed: " + ", ".join("%s (%s)" % (k, old[k].get("product_id", "")) for k in removed), ""]
    out.append("Computed from the two files (F).")
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
