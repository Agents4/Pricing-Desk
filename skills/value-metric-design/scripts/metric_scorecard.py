"""Score candidate value metrics against criteria.

Usage:
  python metric_scorecard.py --in metrics.json [--md out.md]

metrics.json:
  {"criteria": [{"name": "visible to the customer", "weight": 1, "knockout_min": 3}, ...],
   "candidates": [{"name": "per booking", "scores": {"visible to the customer": 4, ...}, "evidence": {"visible to the customer": "text"}}]}
Weights: give a weight (0 or more) on EVERY criterion or on none. All omitted = equal weights, stated as an assumption (A).
         Weights on some criteria and not others is an error.
knockout_min: optional, per criterion, a minimum score the user or the Council sets. A candidate below it is shown as
         "fails <criterion>" and ranks last whatever its total. The tool never invents a minimum.
Scores are whole numbers 1 to 5 supplied by the user or taken from evidence. A missing score is Unknown and the
candidate is shown as incomplete; it is not scored as zero. Totals are weighted sums over the scored criteria and
the maximum possible for those criteria is shown beside them.
Exit codes: 0 = scorecard, 2 = invalid input.
"""
import argparse
import json
import math
import sys


def isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def check(d):
    errs = []
    if not isinstance(d, dict) or not isinstance(d.get("criteria"), list) or not d["criteria"]:
        return ["criteria needs at least one criterion"]
    if not isinstance(d.get("candidates"), list) or not d["candidates"]:
        errs.append("candidates needs at least one candidate")
    names = []
    for i, c in enumerate(d["criteria"]):
        if not isinstance(c, dict) or not c.get("name"):
            errs.append("criteria[%d] needs a name" % i)
            continue
        if c["name"] in names:
            errs.append("criterion %r appears twice" % c["name"])
        names.append(c["name"])
        if "weight" in c and (not isnum(c["weight"]) or c["weight"] < 0):
            errs.append("criterion %r: weight must be a number of 0 or more" % c["name"])
        if "knockout_min" in c and (isinstance(c["knockout_min"], bool) or not isinstance(c["knockout_min"], int) or not 1 <= c["knockout_min"] <= 5):
            errs.append("criterion %r: knockout_min must be a whole number 1 to 5" % c["name"])
    have = [("weight" in c) for c in d["criteria"] if isinstance(c, dict)]
    if any(have) and not all(have):
        errs.append("weights are given on some criteria and not others; give all or none")
    if all(have) and have and sum(c["weight"] for c in d["criteria"] if isnum(c.get("weight"))) <= 0:
        errs.append("the weights add to zero")
    seen = set()
    for j, c in enumerate(d.get("candidates") or []):
        if not isinstance(c, dict) or not c.get("name"):
            errs.append("candidates[%d] needs a name" % j)
            continue
        if c["name"] in seen:
            errs.append("candidate %r appears twice" % c["name"])
        seen.add(c["name"])
        sc = c.get("scores", {})
        if not isinstance(sc, dict):
            errs.append("candidate %r: scores must be an object" % c["name"])
            continue
        for k, v in sc.items():
            if k not in names:
                errs.append("candidate %r scores %r, which is not a criterion (typo?)" % (c["name"], k))
            elif v is not None and (isinstance(v, bool) or not isinstance(v, int) or not 1 <= v <= 5):
                errs.append("candidate %r: score for %r must be a whole number 1 to 5, not %r" % (c["name"], k, v))
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    try:
        with open(a.inp, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError) as e:
        print("Cannot read the input: %s" % e, file=sys.stderr)
        return 2
    errs = check(d)
    if errs:
        print("Input errors:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        return 2
    crit = d["criteria"]
    equal = all("weight" not in c for c in crit)
    w = {c["name"]: (1.0 if equal else float(c["weight"])) for c in crit}
    ko = {c["name"]: c["knockout_min"] for c in crit if "knockout_min" in c}
    rows = []
    for c in d["candidates"]:
        sc = c.get("scores", {})
        tot = mx = 0.0
        miss, fails, ko_unknown = [], [], []
        for k in w:
            v = sc.get(k)
            if v is None:
                miss.append(k)
                if k in ko:
                    ko_unknown.append(k)
                continue
            tot += w[k] * v
            mx += w[k] * 5
            if k in ko and v < ko[k]:
                fails.append("%s (%d, minimum %d)" % (k, v, ko[k]))
        rows.append((c["name"], tot, mx, miss, fails, ko_unknown))
    rows.sort(key=lambda r: (len(r[4]) > 0, len(r[3]) > 0, -(r[1] / r[2] if r[2] else 0)))
    out = ["Weights: " + ("equal (assumption A, no weights supplied)." if equal else ", ".join("%s %g" % (k, v) for k, v in w.items()) + " (supplied)."),
           ("Knockout minimums (supplied): " + ", ".join("%s %d" % (k, v) for k, v in ko.items()) + ".") if ko else "Knockout minimums: none set.", "",
           "| Candidate | Score | Out of | Share | Unknown criteria | Knockout |", "|---|---|---|---|---|---|"]
    for n, t, m, miss, fails, ku in rows:
        k = ("fails " + "; ".join(fails)) if fails else ("Unknown on " + ", ".join(ku)) if ku else ("passes" if ko else "none set")
        out.append("| %s | %g | %g | %s | %s | %s |" % (n, t, m, "n/a" if not m else "%.0f%%" % (t / m * 100), ", ".join(miss) or "none", k))
    out += ["", "Scores come from the input (F if evidenced, I if judged). Candidates that fail a knockout, then incomplete ones, rank below complete ones."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
