#!/usr/bin/env python3
"""Three approaches to the value of a data product: cost, market and income.

Usage:
  python valuation.py --in input.json [--md out.md]

input.json:
  currency
  cost:   {"build_cost": N, "annual_run_cost": N, "years": N}                 cost to recreate, over a stated horizon
  market: {"comparables": [{"name": "...", "price": N, "source": "url or note"}]}   prices of comparable products, same unit
  income: {"annual_net_benefit": N, "years": N, "discount_rate": 0.xx}          net benefit to the buyer, discounted
All inputs are supplied. The discount rate and horizon are the user's; none is assumed and a missing one skips that approach.
Output shows each value, the range across approaches, and which approach is lowest and highest. The corridor
calculator in data-price-setting turns a value into a price corridor; this script does not set a price.
"""
import argparse
import json
import statistics
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    d = json.load(open(a.inp, encoding="utf-8"))
    cur = d.get("currency", "USD")
    res, skipped = {}, []
    c = d.get("cost") or {}
    if all(k in c for k in ("build_cost", "annual_run_cost", "years")):
        res["Cost approach"] = (float(c["build_cost"]) + float(c["annual_run_cost"]) * float(c["years"]),
                                "build %s + run %s x %s years" % ("{:,.0f}".format(c["build_cost"]), "{:,.0f}".format(c["annual_run_cost"]), c["years"]))
    else:
        skipped.append("Cost approach: needs build_cost, annual_run_cost, years")
    m = (d.get("market") or {}).get("comparables") or []
    if m:
        p = [float(x["price"]) for x in m]
        res["Market approach"] = (statistics.median(p), "median of %d comparable(s): %s" % (len(p), ", ".join(x["name"] for x in m)))
    else:
        skipped.append("Market approach: needs comparables with prices and sources")
    i = d.get("income") or {}
    if all(k in i for k in ("annual_net_benefit", "years", "discount_rate")):
        r, n, b = float(i["discount_rate"]), int(i["years"]), float(i["annual_net_benefit"])
        pv = sum(b / (1 + r) ** t for t in range(1, n + 1))
        res["Income approach"] = (pv, "%s a year for %d years at %.1f%% (user's rate)" % ("{:,.0f}".format(b), n, r * 100))
    else:
        skipped.append("Income approach: needs annual_net_benefit, years, discount_rate")
    out = ["| Approach | Value (%s) | Basis |" % cur, "|---|---|---|"]
    for k, (v, basis) in res.items():
        out.append("| %s | %s | %s |" % (k, "{:,.0f}".format(v), basis))
    if res:
        vals = sorted(res.items(), key=lambda kv: kv[1][0])
        out += ["", "Range: %s (%s) to %s (%s)." % ("{:,.0f}".format(vals[0][1][0]), vals[0][0], "{:,.0f}".format(vals[-1][1][0]), vals[-1][0])]
    for s in skipped:
        out.append("Skipped: " + s)
    out += ["", "Computed from the supplied inputs. The cost approach sets a floor on what recreation costs, not a price; the income approach is only as good as the benefit estimate (A unless evidenced)."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
