#!/usr/bin/env python3
"""Tally won and lost deals by pricing cause.

Usage:
  python winloss_tally.py --in deals.csv [--md out.md]

deals.csv columns (header row required):
  deal_id, account, product, outcome, price_cause, discount_pct, competitor
  outcome: won, lost, no_decision
  price_cause: price_too_high, value_gap, terms, packaging, competitor_price, no_price_reason, unknown
  discount_pct and competitor are optional.

Shows counts and the share in each cell, always with n. Averages of discount are shown for each outcome only
when at least one value exists. No significance claim is made and no minimum sample is assumed: the reader decides
how much weight a count of a few deals deserves. Causes come from the input; blank is Unknown.
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    cnt = defaultdict(Counter)
    disc = defaultdict(list)
    comp = defaultdict(Counter)
    n = Counter()
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            o = (r.get("outcome") or "").strip().lower() or "unknown"
            c = (r.get("price_cause") or "").strip().lower() or "unknown"
            cnt[o][c] += 1
            n[o] += 1
            d = (r.get("discount_pct") or "").replace("%", "").strip()
            if d:
                try:
                    disc[o].append(float(d))
                except ValueError:
                    pass
            k = (r.get("competitor") or "").strip()
            if k:
                comp[o][k] += 1
    outcomes = [o for o in ("won", "lost", "no_decision") if n[o]] + [o for o in n if o not in ("won", "lost", "no_decision")]
    causes = sorted({c for o in cnt for c in cnt[o]})
    out = ["Deals: " + ", ".join("%s n=%d" % (o, n[o]) for o in outcomes), "",
           "| Price cause | " + " | ".join("%s (n=%d)" % (o, n[o]) for o in outcomes) + " |",
           "|---|" + "---|" * len(outcomes)]
    for c in causes:
        out.append("| %s | " % c + " | ".join("%d (%.0f%%)" % (cnt[o][c], cnt[o][c] / n[o] * 100) for o in outcomes) + " |")
    out += ["", "| Outcome | Deals with a discount recorded | Average discount |", "|---|---|---|"]
    for o in outcomes:
        out.append("| %s | %d | %s |" % (o, len(disc[o]), "n/a" if not disc[o] else "%.1f%%" % (sum(disc[o]) / len(disc[o]))))
    if any(comp[o] for o in outcomes):
        out += ["", "| Competitor named | " + " | ".join(outcomes) + " |", "|---|" + "---|" * len(outcomes)]
        for k in sorted({k for o in comp for k in comp[o]}):
            out.append("| %s | " % k + " | ".join(str(comp[o][k]) for o in outcomes) + " |")
    out += ["", "Counts and averages are computed from the input (F). Causes were entered by the deal team, so they are the team's reading (I), not proof."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
