#!/usr/bin/env python3
"""Score candidate value metrics against criteria.

Usage:
  python metric_scorecard.py --in metrics.json [--md out.md]

metrics.json:
  {"criteria": [{"name": "visible to the customer", "weight": 1}, ...],   weight optional; equal weights if all omitted (stated in output)
   "candidates": [{"name": "per booking", "scores": {"visible to the customer": 4, ...}, "evidence": {"visible to the customer": "text"}}]}
Scores are whole numbers 1 to 5 supplied by the user or taken from evidence. A missing score is Unknown and the
candidate is shown as incomplete; it is not scored as zero. Totals are weighted sums over the scored criteria and
the maximum possible for those criteria is shown beside them.
"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    d = json.load(open(a.inp, encoding="utf-8"))
    crit = d["criteria"]
    equal = all("weight" not in c for c in crit)
    w = {c["name"]: (1.0 if equal else float(c.get("weight", 0))) for c in crit}
    rows = []
    for c in d["candidates"]:
        sc = c.get("scores", {})
        tot = mx = 0.0
        miss = []
        for k in w:
            v = sc.get(k)
            if v is None:
                miss.append(k)
                continue
            if not (isinstance(v, int) and 1 <= v <= 5):
                sys.exit("score for %s / %s must be a whole number 1 to 5" % (c["name"], k))
            tot += w[k] * v
            mx += w[k] * 5
        rows.append((c["name"], tot, mx, miss))
    rows.sort(key=lambda r: (len(r[3]) > 0, -(r[1] / r[2] if r[2] else 0)))
    out = ["Weights: " + ("equal (assumption A, no weights supplied)." if equal else ", ".join("%s %g" % (k, v) for k, v in w.items()) + " (supplied)."), "",
           "| Candidate | Score | Out of | Share | Unknown criteria |", "|---|---|---|---|---|"]
    for n, t, m, miss in rows:
        out.append("| %s | %g | %g | %s | %s |" % (n, t, m, "n/a" if not m else "%.0f%%" % (t / m * 100), ", ".join(miss) or "none"))
    out += ["", "Scores come from the input (F if evidenced, I if judged). Incomplete candidates are not ranked above complete ones."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
