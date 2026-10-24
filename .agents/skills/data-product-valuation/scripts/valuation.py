"""Three approaches to the value of a data product: cost, market and income.

Usage:
  python valuation.py --in input.json [--md out.md]

input.json:
  currency
  cost:   {"build_cost": N, "annual_run_cost": N, "years": N}                 cost to recreate, over a stated horizon
  market: {"comparables": [{"name": "...", "price": N, "unit": "per market-year", "source": "url or note"}]}
          Every comparable must be in the SAME unit (the unit field is required when there is more than one).
  income: {"annual_net_benefit": N, "years": N, "discount_rate": 0.xx}          net benefit to the buyer, discounted
All inputs are supplied. The discount rate (a share from 0 up to, not including, 1: write 10% as 0.10) and the horizon
(a whole number of years) are the user's; none is assumed. An approach with no inputs at all is skipped and listed. An approach
with some of its inputs and not others is an error, not a quiet skip. Numbers must be numbers (not text) and not negative.
Output shows each value, the range across approaches, and which approach is lowest and highest. The corridor
calculator in data-price-setting turns a value into a price corridor; this script does not set a price.
Exit codes: 0 = result, 2 = invalid input.
"""
import argparse
import json
import math
import statistics
import sys


def isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def isyears(v):
    return isnum(v) and v >= 1 and float(v) == int(v)


def validate(d):
    errs = []
    if not isinstance(d, dict):
        return ["the input must be a JSON object"]
    c, m, i = d.get("cost") or {}, (d.get("market") or {}), d.get("income") or {}
    ck = ("build_cost", "annual_run_cost", "years")
    if any(k in c for k in ck):
        for k in ck:
            if k not in c:
                errs.append("cost.%s is missing (give all three or none)" % k)
            elif k == "years":
                if not isyears(c[k]):
                    errs.append("cost.years must be a whole number of 1 or more")
            elif not isnum(c[k]) or c[k] < 0:
                errs.append("cost.%s must be a number of 0 or more (numbers, not text)" % k)
    comps = m.get("comparables") or []
    units = set()
    for j, x in enumerate(comps):
        if not isinstance(x, dict) or not x.get("name"):
            errs.append("market.comparables[%d] needs a name" % j)
            continue
        if not isnum(x.get("price")) or x["price"] <= 0:
            errs.append("market.comparables[%d].price must be a number above 0" % j)
        if not x.get("source"):
            errs.append("market.comparables[%d] (%s) needs a source" % (j, x["name"]))
        if len(comps) > 1 and not x.get("unit"):
            errs.append("market.comparables[%d] (%s) needs a unit, so that prices can be compared" % (j, x["name"]))
        units.add((x.get("unit") or "").strip().lower())
    if len(units - {""}) > 1:
        errs.append("the comparables are in different units (%s); convert them to one unit first" % ", ".join(sorted(units - {""})))
    ik = ("annual_net_benefit", "years", "discount_rate")
    if any(k in i for k in ik):
        for k in ik:
            if k not in i:
                errs.append("income.%s is missing (give all three or none)" % k)
        if "years" in i and not isyears(i["years"]):
            errs.append("income.years must be a whole number of 1 or more")
        if "annual_net_benefit" in i and (not isnum(i["annual_net_benefit"]) or i["annual_net_benefit"] < 0):
            errs.append("income.annual_net_benefit must be a number of 0 or more")
        if "discount_rate" in i:
            r = i["discount_rate"]
            if not isnum(r) or r < 0:
                errs.append("income.discount_rate must be a number of 0 or more")
            elif r >= 1:
                errs.append("income.discount_rate %g looks like a percent; write 10%% as 0.10" % r)
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
    errs = validate(d)
    if errs:
        print("Input errors:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        return 2
    cur = d.get("currency", "USD")
    res, skipped = {}, []
    c = d.get("cost") or {}
    if "build_cost" in c:
        res["Cost approach"] = (float(c["build_cost"]) + float(c["annual_run_cost"]) * int(c["years"]),
                                "build %s + run %s x %d years" % ("{:,.0f}".format(c["build_cost"]), "{:,.0f}".format(c["annual_run_cost"]), int(c["years"])))
    else:
        skipped.append("Cost approach: no inputs (needs build_cost, annual_run_cost, years)")
    m = (d.get("market") or {}).get("comparables") or []
    if m:
        p = [float(x["price"]) for x in m]
        unit = next((x.get("unit") for x in m if x.get("unit")), "unit not stated")
        res["Market approach"] = (statistics.median(p), "median of %d comparable(s) (%s; range %s to %s; %s): %s" % (
            len(p), unit, "{:,.0f}".format(min(p)), "{:,.0f}".format(max(p)), "one comparable is not a market" if len(p) == 1 else "n=%d" % len(p), ", ".join(x["name"] for x in m)))
    else:
        skipped.append("Market approach: no comparables (needs prices, one unit, and sources)")
    i = d.get("income") or {}
    if "discount_rate" in i:
        r, n, b = float(i["discount_rate"]), int(i["years"]), float(i["annual_net_benefit"])
        pv = sum(b / (1 + r) ** t for t in range(1, n + 1))
        res["Income approach"] = (pv, "%s a year for %d years at %.1f%% (user's rate)" % ("{:,.0f}".format(b), n, r * 100))
    else:
        skipped.append("Income approach: no inputs (needs annual_net_benefit, years, discount_rate)")
    if not res:
        print("Nothing to value: give at least one approach its inputs.", file=sys.stderr)
        return 2
    out = ["| Approach | Value (%s) | Basis |" % cur, "|---|---|---|"]
    for k, (v, basis) in res.items():
        out.append("| %s | %s | %s |" % (k, "{:,.0f}".format(v), basis))
    vals = sorted(res.items(), key=lambda kv: kv[1][0])
    out += ["", "Range: %s (%s) to %s (%s)." % ("{:,.0f}".format(vals[0][1][0]), vals[0][0], "{:,.0f}".format(vals[-1][1][0]), vals[-1][0])]
    for s in skipped:
        out.append("Skipped: " + s)
    out += ["", "Computed from the supplied inputs. The cost approach sets a floor on what recreation costs, not a price; the income approach is only as good as the benefit estimate (A unless evidenced)."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
