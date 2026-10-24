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
import datetime as dt
import math
import re
import sys
from collections import defaultdict


def money(s):
    """Parse an amount. Blank is NOT zero: it returns None so the caller can stop."""
    s = (s or "").strip()
    if not s:
        return None
    s = s.replace("$", "").replace(",", "").replace(" ", "")
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        raise ValueError("not a plain number: %r" % s)
    v = float(s)
    if not math.isfinite(v):
        raise ValueError("not finite")
    return -v if neg else v


def iso_week(s):
    s = (s or "").strip()
    s = s.split(" ")[0].split("T")[0]
    return dt.date.fromisoformat(s)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--week")
    ap.add_argument("--md")
    a = ap.parse_args()
    by_week = defaultdict(lambda: [0.0, 0.0])
    fam = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    cause = defaultdict(lambda: defaultdict(float))
    errors, notes = [], []
    n_rows = 0
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        cols = [(c or "").strip() for c in (rd.fieldnames or [])]
        miss = [c for c in ("week", "list_value", "realized_value") if c not in cols]
        if miss:
            print("The CSV is missing columns: " + ", ".join(miss), file=sys.stderr)
            return 2
        for i, r in enumerate(rd, 2):
            r = {(k or "").strip(): v for k, v in r.items()}
            try:
                wd = iso_week(r.get("week"))
            except ValueError:
                errors.append("line %d: week %r is not a date (use YYYY-MM-DD)" % (i, r.get("week")))
                continue
            try:
                lv, rv = money(r.get("list_value")), money(r.get("realized_value"))
            except ValueError as e:
                errors.append("line %d: %s" % (i, e))
                continue
            if lv is None or rv is None:
                errors.append("line %d: list_value and realized_value are both required (a blank is not zero)" % i)
                continue
            if lv < 0 or rv < 0:
                errors.append("line %d: negative value; credits belong in realized_value as a lower number, not a negative line" % i)
                continue
            w = wd.isoformat()
            if wd.weekday() != 0:
                notes.append("line %d: week %s is not a Monday; it is kept as its own week" % (i, w))
            k = ((r.get("family") or "").strip()) or "Unlabeled"
            c = ((r.get("cause") or "").strip()) or "Unlabeled"
            if rv > lv:
                notes.append("line %d (%s, %s): realized is above list by %s; it nets against the gap, check it is not a data error" % (i, w, k, "{:,.0f}".format(rv - lv)))
            n_rows += 1
            by_week[w][0] += lv
            by_week[w][1] += rv
            fam[w][k][0] += lv
            fam[w][k][1] += rv
            cause[w][c] += lv - rv
    if errors:
        print("Input errors (nothing was rolled up):", file=sys.stderr)
        for e in errors[:50]:
            print(" -", e, file=sys.stderr)
        if len(errors) > 50:
            print(" - and %d more" % (len(errors) - 50), file=sys.stderr)
        return 2
    weeks = sorted(by_week)
    if not weeks:
        print("no rows", file=sys.stderr)
        return 2
    cur = a.week or weeks[-1]
    if cur not in by_week:
        print("week %s not in file; weeks present: %s" % (cur, ", ".join(weeks)), file=sys.stderr)
        return 2
    i = weeks.index(cur)
    prev = None
    prev_note = " (no prior week in the file)"
    if i > 0:
        gap = (dt.date.fromisoformat(cur) - dt.date.fromisoformat(weeks[i - 1])).days
        if gap == 7:
            prev, prev_note = weeks[i - 1], " against %s" % weeks[i - 1]
        else:
            prev_note = " (no comparison: the last earlier week in the file is %s, %d days before; a week is missing)" % (weeks[i - 1], gap)

    def rate(w):
        l, r = by_week[w]
        return (r / l) if l else None

    out = ["Week %s%s" % (cur, prev_note), ""]
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
    out += ["", "Computed from the input lines (F). Rows with no cause are shown as Unlabeled, not guessed. One currency is assumed; the file has no currency column."]
    cur_notes = [n for n in notes]
    if cur_notes:
        out += ["", "Notes on the input:"] + ["- " + n for n in cur_notes[:20]]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
