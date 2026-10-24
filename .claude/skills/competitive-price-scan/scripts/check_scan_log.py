#!/usr/bin/env python3
"""Check a competitor price scan log before it is used.

Usage:
  python check_scan_log.py --in scan.csv --today YYYY-MM-DD [--max-age-days N]

scan.csv columns (header row required):
  competitor, product, unit, price, currency, right_or_scope, source_url, access_date, notes
A row is accepted only with: a price above zero, a unit, a currency, the right or scope it covers, a real web address
in source_url (http or https, a host with a dot, not a placeholder such as example.com) and a real YYYY-MM-DD
access_date that is not in the future. Any other row is marked unverified, with the reasons, and must not be quoted.
With --max-age-days, older rows are marked stale. N is a company or user value (the freshness limit in
pricing-governance.md); no default is assumed.
Exit codes: 1 if any row is unverified, 2 for unusable input, 0 otherwise.
"""
import argparse
import csv
import datetime as dt
import math
import re
import sys
from urllib.parse import urlparse

REQUIRED = ["competitor", "product", "unit", "price", "currency", "right_or_scope", "source_url", "access_date"]
PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "localhost", "test.com", "domain.com", "yoursite.com"}
PLACEHOLDER_TLDS = {"invalid", "test", "example", "localhost"}


def url_problem(u):
    p = urlparse(u)
    if p.scheme not in ("http", "https") or not p.hostname:
        return "source_url is not a web address"
    h = p.hostname.lower()
    if "." not in h:
        return "source_url host %r is not a public site" % h
    if h in PLACEHOLDER_HOSTS or h.rsplit(".", 1)[-1] in PLACEHOLDER_TLDS or h.endswith(".example.com"):
        return "source_url host %r is a placeholder, not a source" % h
    return None


def cell(r, k):
    v = r.get(k)
    return v.strip() if isinstance(v, str) else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--today", required=True)
    ap.add_argument("--max-age-days", type=int)
    a = ap.parse_args()
    try:
        today = dt.date.fromisoformat(a.today)
    except ValueError:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if a.max_age_days is not None and a.max_age_days < 0:
        print("--max-age-days must be 0 or more", file=sys.stderr)
        return 2
    unver = stale = ok = 0
    lines = ["| Competitor | Product | Price | Unit | Scope | Status |", "|---|---|---|---|---|---|"]
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        cols = [(c or "").strip() for c in (rd.fieldnames or [])]
        miss = [c for c in REQUIRED if c not in cols]
        if miss:
            print("The CSV is missing columns: " + ", ".join(miss), file=sys.stderr)
            return 2
        for r in rd:
            r = {(k or "").strip(): v for k, v in r.items()}
            why = []
            price = cell(r, "price").replace(",", "")
            try:
                pv = float(price)
                if not math.isfinite(pv) or pv <= 0:
                    why.append("price must be above zero")
            except ValueError:
                why.append("price is blank or not a number")
            for k in ("unit", "currency", "competitor", "product"):
                if not cell(r, k):
                    why.append("%s is blank" % k)
            scope = cell(r, "right_or_scope")
            if not scope:
                why.append("right_or_scope is blank: not comparable until known (rule 8)")
            url, ad = cell(r, "source_url"), cell(r, "access_date")
            if not url:
                why.append("no source_url")
            elif url_problem(url):
                why.append(url_problem(url))
            adate = None
            if not ad:
                why.append("no access_date")
            elif not re.match(r"^\d{4}-\d{2}-\d{2}$", ad):
                why.append("access_date is not YYYY-MM-DD")
            else:
                try:
                    adate = dt.date.fromisoformat(ad)
                except ValueError:
                    why.append("access_date %s is not a real date" % ad)
                if adate and adate > today:
                    why.append("access_date %s is in the future" % ad)
            if why:
                st = "UNVERIFIED (" + "; ".join(why) + "): do not quote"
                unver += 1
            elif a.max_age_days is not None and (today - adate).days > a.max_age_days:
                st = "STALE: accessed %s" % ad
                stale += 1
            else:
                st = "ok, accessed %s" % ad
                ok += 1
            lines.append("| %s | %s | %s %s | %s | %s | %s |" % (cell(r, "competitor"), cell(r, "product"), cell(r, "price"), cell(r, "currency"),
                         cell(r, "unit"), scope or "Unknown", st))
    print("\n".join(lines))
    print("\n%d ok, %d stale, %d unverified." % (ok, stale, unver))
    return 1 if unver else 0


if __name__ == "__main__":
    sys.exit(main())
