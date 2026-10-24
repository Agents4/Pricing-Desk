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
import math
import re
import sys
from collections import Counter, defaultdict

OUTCOMES = {"won": "won", "win": "won", "closed won": "won", "closed_won": "won", "lost": "lost", "loss": "lost",
            "closed lost": "lost", "closed_lost": "lost", "no_decision": "no_decision", "no decision": "no_decision",
            "nodecision": "no_decision", "stalled": "no_decision"}
CAUSES = {"price_too_high", "value_gap", "terms", "packaging", "competitor_price", "no_price_reason", "unknown"}


def norm(s):
    return re.sub(r"[\s\-]+", "_", (s or "").strip().lower())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    cnt = defaultdict(Counter)
    disc = defaultdict(list)
    comp = defaultdict(Counter)
    n = Counter()
    errors, notes, seen = [], [], {}
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        cols = [(c or "").strip() for c in (rd.fieldnames or [])]
        miss = [c for c in ("deal_id", "outcome", "price_cause") if c not in cols]
        if miss:
            print("The CSV is missing columns: " + ", ".join(miss), file=sys.stderr)
            return 2
        for i, r in enumerate(rd, 2):
            r = {(k or "").strip(): v for k, v in r.items()}
            did = (r.get("deal_id") or "").strip()
            if not did:
                errors.append("line %d: deal_id is blank" % i)
                continue
            if did in seen:
                errors.append("line %d: deal_id %s repeats line %d (a deal would be counted twice)" % (i, did, seen[did]))
                continue
            seen[did] = i
            raw_o = (r.get("outcome") or "").strip()
            o = OUTCOMES.get(raw_o.lower().replace("-", " ")) or OUTCOMES.get(norm(raw_o))
            if o is None:
                notes.append("line %d (%s): outcome %r is not won, lost or no_decision; counted as unrecognised" % (i, did, raw_o))
                o = "unrecognised"
            c = norm(r.get("price_cause")) or "unknown"
            if c not in CAUSES:
                notes.append("line %d (%s): price_cause %r is not a listed cause; shown as entered" % (i, did, c))
            cnt[o][c] += 1
            n[o] += 1
            d = (r.get("discount_pct") or "").replace("%", "").strip()
            if d:
                try:
                    dv = float(d)
                    if not math.isfinite(dv) or dv < 0 or dv > 100:
                        raise ValueError
                    disc[o].append(dv)
                except ValueError:
                    notes.append("line %d (%s): discount_pct %r could not be read; left out of the average" % (i, did, (r.get("discount_pct") or "").strip()))
            k = (r.get("competitor") or "").strip()
            if k:
                comp[o][k] += 1
    if errors:
        print("Input errors (nothing was tallied):", file=sys.stderr)
        for e in errors:
            print(" -", e, file=sys.stderr)
        return 2
    if not n:
        print("The CSV has a header and no deals.", file=sys.stderr)
        return 2
    order = ("won", "lost", "no_decision", "unrecognised")
    outcomes = [o for o in order if n[o]]
    causes = sorted({c for o in cnt for c in cnt[o]})
    out = ["Deals: " + ", ".join("%s n=%d" % (o, n[o]) for o in outcomes), "",
           "| Price cause | " + " | ".join("%s (n=%d)" % (o, n[o]) for o in outcomes) + " |",
           "|---|" + "---|" * len(outcomes)]
    for c in causes:
        out.append("| %s | " % c + " | ".join("%d (%.0f%%)" % (cnt[o][c], cnt[o][c] / n[o] * 100) for o in outcomes) + " |")
    out += ["", "| Outcome | Deals with a discount recorded | Average discount |", "|---|---|---|"]
    for o in outcomes:
        out.append("| %s | %d of %d | %s |" % (o, len(disc[o]), n[o], "n/a" if not disc[o] else "%.1f%%" % (sum(disc[o]) / len(disc[o]))))
    if any(comp[o] for o in outcomes):
        out += ["", "| Competitor named | " + " | ".join(outcomes) + " |", "|---|" + "---|" * len(outcomes)]
        for k in sorted({k for o in comp for k in comp[o]}):
            out.append("| %s | " % k + " | ".join(str(comp[o][k]) for o in outcomes) + " |")
    out += ["", "Counts and averages are computed from the input (F). Causes were entered by the deal team, so they are the team's reading (I), not proof."]
    if notes:
        out += ["", "Notes on the input:"] + ["- " + x for x in notes[:30]]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
