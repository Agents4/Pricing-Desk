#!/usr/bin/env python3
"""Check a competitor price scan log before it is used.

Usage:
  python check_scan_log.py --in scan.csv --today YYYY-MM-DD [--max-age-days N]

scan.csv columns (header row required):
  competitor, product, unit, price, currency, right_or_scope, source_url, access_date, notes
Rows are accepted only with a web address in source_url and a YYYY-MM-DD access_date. Rows without are marked
unverified and must not be quoted. With --max-age-days, older rows are marked stale. N is a company or user
value; no default is assumed. Exit code 1 if any row is unverified.
"""
import argparse
import csv
import datetime as dt
import re
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--today", required=True)
    ap.add_argument("--max-age-days", type=int)
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.today)
    unver = stale = ok = 0
    print("| Competitor | Product | Price | Unit | Scope | Status |")
    print("|---|---|---|---|---|---|")
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            url, ad = (r.get("source_url") or "").strip(), (r.get("access_date") or "").strip()
            if not re.match(r"^https?://", url) or not re.match(r"^\d{4}-\d{2}-\d{2}$", ad):
                st = "UNVERIFIED: needs a source URL and an access date; do not quote"
                unver += 1
            elif a.max_age_days is not None and (today - dt.date.fromisoformat(ad)).days > a.max_age_days:
                st = "STALE: accessed %s" % ad
                stale += 1
            else:
                st = "ok, accessed %s" % ad
                ok += 1
            sc = (r.get("right_or_scope") or "").strip() or "Unknown (not comparable until known)"
            print("| %s | %s | %s %s | %s | %s | %s |" % (r.get("competitor", ""), r.get("product", ""), r.get("price", ""), r.get("currency", ""),
                  r.get("unit", ""), sc, st))
    print("\n%d ok, %d stale, %d unverified." % (ok, stale, unver))
    sys.exit(1 if unver else 0)


if __name__ == "__main__":
    main()
