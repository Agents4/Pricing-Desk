#!/usr/bin/env python3
"""Notice calendar for a price change: who must be told by when.

Usage:
  python notice_calendar.py --in contracts.csv --effective YYYY-MM-DD --today YYYY-MM-DD [--md out.md]

contracts.csv columns (header row required):
  contract_id, account, notice_days, price_protected_until
  notice_days: days of written notice the contract requires before a price change takes effect. Blank = Unknown.
  price_protected_until: YYYY-MM-DD, blank if none. A change cannot apply before this date.

send_by = effective date minus notice_days. The notice days are contract values; none is assumed.
Contract terms are read as supplied; Legal confirms them.
"""
import argparse
import csv
import datetime as dt
import sys


def d(s):
    s = (s or "").strip()
    return dt.date.fromisoformat(s) if s else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--effective", required=True)
    ap.add_argument("--today", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    eff, today = dt.date.fromisoformat(a.effective), dt.date.fromisoformat(a.today)
    rows = []
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            nd = (r.get("notice_days") or "").strip()
            prot = d(r.get("price_protected_until"))
            send_by = (eff - dt.timedelta(days=int(float(nd)))) if nd else None
            if prot and prot > eff:
                st = "protected until %s: change cannot apply on the effective date" % prot
            elif send_by is None:
                st = "notice period Unknown: ask Legal"
            elif send_by < today:
                st = "send-by date passed %d day(s) ago: effective date cannot be met" % (today - send_by).days
            else:
                st = "send by %s (%d day(s) from today)" % (send_by, (send_by - today).days)
            rows.append(((send_by or dt.date.max), r.get("contract_id", ""), r.get("account", ""), nd or "Unknown", st))
    rows.sort()
    out = ["Notice calendar for effective date %s, as of %s." % (eff, today), "",
           "| Contract | Account | Notice days | Status |", "|---|---|---|---|"]
    out += ["| %s | %s | %s | %s |" % (c, ac, nd, st) for _, c, ac, nd, st in rows]
    out += ["", "Dates are computed from the supplied contract terms (F if the terms were read from the contract, A if relayed). Legal confirms."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
