#!/usr/bin/env python3
"""Screen API keys for patterns that look like collecting data rather than serving bookings.

Usage:
  python harvest_screen.py --in keys.csv --segment-median-l2b N [--multiple X] [--md out.md]

keys.csv columns (header row required):
  key_id, customer, searches, bookings            required
  distinct_queries                                 optional: distinct origin, destination and date combinations among the searches
  retention_days                                   optional: how long responses are kept, if known

--segment-median-l2b  the median look-to-book ratio (searches per booking) for the customer's segment.
--multiple            the company's threshold: flag keys whose ratio is at least this multiple of the median. It is a
                      company value (pricing-governance.md or api policy). When it is not given, nothing is flagged;
                      ratios are shown with the label 'threshold Unknown'.

A flag is a question for the account owner: "possible data collection, to confirm". It is never a finding against the customer.
Keys with searches and no bookings are always listed: the ratio is undefined.
"""
import argparse
import csv
import sys


def num(s):
    s = (s or "").replace(",", "").strip()
    return float(s) if s else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--segment-median-l2b", type=float, required=True)
    ap.add_argument("--multiple", type=float)
    ap.add_argument("--md")
    a = ap.parse_args()
    rows = []
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            s, b = num(r.get("searches")), num(r.get("bookings"))
            if s is None or b is None:
                continue
            dq = num(r.get("distinct_queries"))
            l2b = (s / b) if b > 0 else None
            rows.append({"key": (r.get("key_id") or "").strip(), "customer": (r.get("customer") or "").strip(), "searches": s, "bookings": b,
                         "l2b": l2b, "vs_median": (l2b / a.segment_median_l2b) if l2b is not None else None,
                         "distinct_ratio": (dq / s) if (dq is not None and s) else None,
                         "retention": (r.get("retention_days") or "").strip()})
    rows.sort(key=lambda x: (x["l2b"] is not None, -(x["vs_median"] or 0)))
    out = [f"Segment median look-to-book: {a.segment_median_l2b:g} (input). Threshold multiple: " + (f"{a.multiple:g}x (input)." if a.multiple else "Unknown (nothing flagged)."), "",
           "| Key | Customer | Searches | Bookings | Look-to-book | x median | Distinct-query ratio | Retention days | Screen |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["l2b"] is None:
            screen = "searches with no bookings: ratio undefined, ask the account owner"
        elif a.multiple and r["vs_median"] >= a.multiple:
            screen = "possible data collection, to confirm"
        elif a.multiple:
            screen = "below threshold"
        else:
            screen = "threshold Unknown"
        out.append("| {k} | {c} | {s:,.0f} | {b:,.0f} | {l} | {m} | {d} | {rt} | {sc} |".format(
            k=r["key"], c=r["customer"], s=r["searches"], b=r["bookings"],
            l="n/a" if r["l2b"] is None else f"{r['l2b']:,.1f}", m="n/a" if r["vs_median"] is None else f"{r['vs_median']:,.1f}",
            d="" if r["distinct_ratio"] is None else f"{r['distinct_ratio']:.2f}", rt=r["retention"], sc=screen))
    out += ["", "Ratios are computed from the input counts (F). Flags are questions for the account owner, not findings against the customer."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
