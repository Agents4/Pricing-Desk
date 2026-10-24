#!/usr/bin/env python3
"""Roll weekly billing lines into realization rate by week and leakage by cause.

Usage:
  python weekly_roll.py --in lines.csv [--week YYYY-MM-DD] [--md out.md]

lines.csv columns (header row required):
  week            Monday date of the billing week, YYYY-MM-DD
  family          product family
  list_value      value at list price, one currency
  realized_value  value actually invoiced net of discounts and credits
  cause           optional: why the gap exists (discount, credit, ramp, rounding, error, other). Blank is shown as Unlabeled.

Realization rate = realized_value / list_value. Everything printed comes from the lines. No target is assumed:
compare to a plan only if the user supplies it.
--week picks the week to review (default: the latest week in the file). The prior week is the previous week present.
"""
import argparse
import csv
import sys
from collections import defaultdict


def f(s):
    s = (s or "").replace(",", "").strip()
    return float(s) if s else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--week")
    ap.add_argument("--md")
    a = ap.parse_args()
    by_week = defaultdict(lambda: [0.0, 0.0])
    fam = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    cause = defaultdict(lambda: defaultdict(float))
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            w = (r.get("week") or "").strip()
            if not w:
                continue
            lv, rv = f(r.get("list_value")), f(r.get("realized_value"))
            by_week[w][0] += lv
            by_week[w][1] += rv
            k = (r.get("family") or "Unlabeled").strip() or "Unlabeled"
            fam[w][k][0] += lv
            fam[w][k][1] += rv
            c = (r.get("cause") or "Unlabeled").strip() or "Unlabeled"
            cause[w][c] += lv - rv
    weeks = sorted(by_week)
    if not weeks:
        sys.exit("no rows")
    cur = a.week or weeks[-1]
    if cur not in by_week:
        sys.exit("week %s not in file; weeks present: %s" % (cur, ", ".join(weeks)))
    i = weeks.index(cur)
    prev = weeks[i - 1] if i > 0 else None

    def rate(w):
        l, r = by_week[w]
        return (r / l) if l else None

    out = ["Week %s%s" % (cur, (" against %s" % prev) if prev else " (no prior week in the file)"), ""]
    rc, rp = rate(cur), rate(prev) if prev else None
    out.append("Realization rate: %s%s" % ("n/a" if rc is None else "%.1f%%" % (rc * 100),
               "" if (rc is None or rp is None) else " (prior %.1f%%, change %+.1f points)" % (rp * 100, (rc - rp) * 100)))
    out.append("Gap to list: %s of %s at list." % ("{:,.0f}".format(by_week[cur][0] - by_week[cur][1]), "{:,.0f}".format(by_week[cur][0])))
    out += ["", "| Family | List value | Realized | Rate | Gap | Prior rate | Change (points) |", "|---|---|---|---|---|---|---|"]
    for k, (l, r) in sorted(fam[cur].items(), key=lambda kv: -(kv[1][0] - kv[1][1])):
        pr = None
        if prev and k in fam[prev] and fam[prev][k][0]:
            pr = fam[prev][k][1] / fam[prev][k][0]
        cr = (r / l) if l else None
        out.append("| %s | %s | %s | %s | %s | %s | %s |" % (k, "{:,.0f}".format(l), "{:,.0f}".format(r),
                   "n/a" if cr is None else "%.1f%%" % (cr * 100), "{:,.0f}".format(l - r),
                   "n/a" if pr is None else "%.1f%%" % (pr * 100),
                   "n/a" if (cr is None or pr is None) else "%+.1f" % ((cr - pr) * 100)))
    out += ["", "| Cause of gap | Gap | Share of gap | Prior week gap |", "|---|---|---|---|"]
    tot = sum(cause[cur].values())
    for c, v in sorted(cause[cur].items(), key=lambda kv: -kv[1]):
        out.append("| %s | %s | %s | %s |" % (c, "{:,.0f}".format(v), "n/a" if not tot else "%.0f%%" % (v / tot * 100),
                   "n/a" if not prev else "{:,.0f}".format(cause[prev].get(c, 0.0))))
    out += ["", "Computed from the input lines (F). Rows with no cause are shown as Unlabeled, not guessed."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
