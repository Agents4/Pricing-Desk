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

FIELDS = ["product_id", "product_type", "product_name", "product_family", "conferred_right", "right_basis", "delivery", "unit",
          "tier_min", "tier_max", "tier_model", "list_price", "floor_price", "currency", "term_months", "status",
          "minimum_commitment", "retention_term", "audit_right"]
NUMERIC = {"list_price", "floor_price", "tier_min", "tier_max", "term_months"}


def load(p):
    try:
        fh = open(p, newline="", encoding="utf-8-sig")
    except OSError as e:
        sys.exit("cannot read %s: %s" % (p, e.strerror or e))
    with fh:
        rows = list(csv.DictReader(fh))
    if rows and "line_id" not in rows[0]:
        sys.exit("%s has no line_id column" % p)
    out = {}
    blank = []
    for n, r in enumerate(rows, 2):
        if "use_right" in r and "conferred_right" not in r:
            r["conferred_right"] = r["use_right"]   # legacy column name, same meaning
        k = (r.get("line_id") or "").strip().lower()
        if not k:
            blank.append(n)
            continue
        if k in out:
            sys.exit("%s has a duplicated line_id %r; fix it before comparing" % (p, k))
        out[k] = r
    if blank:
        sys.exit("%s has blank line_id on file line(s) %s; a line without an id cannot be compared. Fix it first" % (p, ", ".join(map(str, blank[:10]))))
    return out


def num(s):
    try:
        x = float((s or "").replace(",", "").strip())
    except ValueError:
        return None
    return x if x == x and abs(x) != float("inf") else None


def same(fld, o, n):
    """Spelling is not a change: Existing and existing, usd and USD."""
    if fld in NUMERIC and num(o) is not None and num(n) is not None:
        return num(o) == num(n)
    return " ".join(o.split()).lower() == " ".join(n.split()).lower()


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
            if same(fld, o, n):
                continue
            pct = ""
            if fld in ("list_price", "floor_price") and num(o) and num(n) is not None:
                pct = "%+.1f%%" % ((num(n) - num(o)) / num(o) * 100)
            changes.append((new[k].get("line_id", k).strip(), new[k].get("product_id", ""), fld, o or "(blank)", n or "(blank)", pct))
    out = ["Price book change log: %d line(s) added, %d removed, %d field change(s) on %d line(s)." % (
        len(added), len(removed), len(changes), len({c[0] for c in changes})), ""]
    if changes:
        out += ["| Line | Product | Field | Old | New | Change |", "|---|---|---|---|---|---|"]
        out += ["| %s | %s | %s | %s | %s | %s |" % c for c in changes]
        out.append("")
    if added:
        out += ["Added: " + ", ".join("%s (%s)" % (new[k].get("line_id", k).strip(), new[k].get("product_id", "")) for k in added), ""]
    if removed:
        out += ["Removed: " + ", ".join("%s (%s)" % (old[k].get("line_id", k).strip(), old[k].get("product_id", "")) for k in removed), ""]
    out.append("Computed from the two files (F).")
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
