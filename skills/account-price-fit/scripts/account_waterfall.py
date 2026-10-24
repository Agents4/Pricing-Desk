#!/usr/bin/env python3
"""Account-level economics for pricing one product inside a whole account.

Compares options for an add-on product against the anchor deal (for example the GDS economic deal
with incentives paid to the agency). List price is not changed here: options move only the deal price,
the included allowance, credits and ramp.

Usage:
  python account_waterfall.py --in input.json [--md report.md] [--json result.json]

Input JSON (see ../examples/atlas-example.json):
  account, currency, term_months
  anchor:  annual_revenue, annual_incentives_paid, annual_cost_to_serve
  addon:   name, unit, list_price, floor_price, annual_units, unit_cost, granted_right (required for data or API)
           product_type (data_license, api_access, software, service, other)
  discount_band_pct: number from the company's approval matrix, or null when Unknown
  options: [{name, price, annual_units (optional), included_units (optional free allowance per year),
             credits_annual (optional), ramp (optional list of unit multipliers by year), gets (list of text)}]

Every figure printed comes from the input. Nothing is estimated.
"""
import argparse
import json
import math
import sys

RIGHTS = ["internal_use", "internal_analytics_shared_outputs", "display_to_third_parties", "redistribution_resale",
          "derivative_data_product", "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation"]
SCOPE_TYPES = {"data_license", "api_access"}


def money(x, cur):
    return f"{cur} {x:,.0f}"


def evaluate(inp):
    cur = inp.get("currency", "USD")
    years = max(1, math.ceil(float(inp.get("term_months", 12)) / 12.0))
    a, p = inp["anchor"], inp["addon"]
    anchor_net = float(a["annual_revenue"]) - float(a["annual_incentives_paid"]) - float(a["annual_cost_to_serve"])
    band = inp.get("discount_band_pct")
    list_price, floor = float(p["list_price"]), p.get("floor_price")
    floor = None if floor in (None, "") else float(floor)
    unit_cost = float(p.get("unit_cost", 0.0))
    issues = []
    ptype = p.get("product_type", "other")
    right = p.get("granted_right", "")
    if ptype in SCOPE_TYPES and not right:
        issues.append("add-on is a data or API product with no granted_right: say what the customer may do (rule 8)")
    if right and right not in RIGHTS:
        issues.append(f"granted_right {right!r} is not one of the nine rights")
    if floor is None:
        issues.append("floor_price is Unknown: no walk-away check is possible")
    if band is None:
        issues.append("discount_band_pct is Unknown: set it in pricing-governance.md; the band check is not run")
    results = []
    for o in inp["options"]:
        units = float(o.get("annual_units", p["annual_units"]))
        incl = float(o.get("included_units", 0.0))
        credits = float(o.get("credits_annual", 0.0))
        price = float(o["price"])
        ramp = o.get("ramp") or [1.0] * years
        ramp = (list(ramp) + [ramp[-1]] * years)[:years]
        yearly = []
        for y in range(years):
            u = units * float(ramp[y])
            billable = max(0.0, u - incl)
            rev = price * billable - credits
            contrib = rev - unit_cost * u
            yearly.append({"year": y + 1, "units": u, "billable_units": billable, "addon_revenue": rev,
                           "addon_contribution": contrib, "account_net": anchor_net + contrib})
        steady = yearly[-1]
        eff = steady["addon_revenue"] / steady["units"] if steady["units"] else 0.0
        disc = 1.0 - eff / list_price if list_price else 0.0
        flags = []
        if floor is not None and eff < floor - 1e-9:
            flags.append(f"effective price {eff:.2f} is below floor {floor:.2f}: needs an exception, not a deal-desk approval")
        if band is not None and disc * 100.0 > float(band) + 1e-9:
            flags.append(f"effective discount {disc*100:.1f}% exceeds the approved band {float(band):g}%: escalate")
        if price > list_price + 1e-9:
            flags.append("option price is above list")
        if (incl > 0 or credits > 0) and not o.get("gets"):
            flags.append("a give (allowance or credit) with no get: log it as an unrequited concession")
        if not o.get("gets") and price < list_price - 1e-9:
            flags.append("a discount with no get: trade it for term, commitment, minimum or audit terms")
        results.append({
            "name": o["name"], "price": price, "included_units": incl, "credits_annual": credits, "ramp": ramp,
            "effective_price_steady": eff, "discount_vs_list_pct": disc * 100.0, "gets": o.get("gets", []),
            "years": yearly, "term_account_net": sum(y["account_net"] for y in yearly),
            "term_addon_revenue": sum(y["addon_revenue"] for y in yearly), "flags": flags})
    return {"account": inp.get("account", ""), "currency": cur, "years": years, "anchor_net_annual": anchor_net,
            "incentive_share_of_anchor_revenue_pct": (100.0 * float(a["annual_incentives_paid"]) / float(a["annual_revenue"])) if float(a["annual_revenue"]) else None,
            "addon": {"name": p.get("name", ""), "list_price": list_price, "floor_price": floor, "granted_right": right,
                      "product_type": ptype, "unit": p.get("unit", "unit")},
            "discount_band_pct": band, "issues": issues, "options": results}


def to_md(r):
    c = r["currency"]
    L = [f"# Account economics: {r['account']}", "",
         f"Add-on: {r['addon']['name']} at list {r['addon']['list_price']:.2f} per {r['addon']['unit']}"
         + (f", floor {r['addon']['floor_price']:.2f}" if r['addon']['floor_price'] is not None else ", floor Unknown")
         + (f", granted right {r['addon']['granted_right']}" if r['addon']['granted_right'] else ", granted right NOT STATED") + ".",
         f"Anchor net per year (revenue less incentives paid less cost to serve): {money(r['anchor_net_annual'], c)} (F, from input). "
         + (f"Incentives are {r['incentive_share_of_anchor_revenue_pct']:.1f}% of anchor revenue." if r['incentive_share_of_anchor_revenue_pct'] is not None else ""),
         "Discount band: " + (f"{r['discount_band_pct']:g}%" if r['discount_band_pct'] is not None else "Unknown") + ".", ""]
    L += ["| Option | Price | Effective price (steady) | Discount vs list | Add-on revenue over term | Account net over term |", "|---|---|---|---|---|---|"]
    for o in r["options"]:
        L.append(f"| {o['name']} | {o['price']:.2f} | {o['effective_price_steady']:.2f} | {o['discount_vs_list_pct']:.1f}% | {money(o['term_addon_revenue'], c)} | {money(o['term_account_net'], c)} |")
    L.append("")
    for o in r["options"]:
        L.append(f"## {o['name']}")
        if o["gets"]:
            L.append("Gets: " + "; ".join(o["gets"]))
        for f in o["flags"]:
            L.append(f"- FLAG: {f}")
        L.append("")
    if r["issues"]:
        L.append("## Missing or unknown")
        L += [f"- {i}" for i in r["issues"]]
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--md")
    ap.add_argument("--json")
    args = ap.parse_args()
    with open(args.inp, encoding="utf-8") as fh:
        data = json.load(fh)
    res = evaluate(data)
    md = to_md(res)
    if args.md:
        open(args.md, "w", encoding="utf-8").write(md)
    if args.json:
        json.dump(res, open(args.json, "w", encoding="utf-8"), indent=2)
    sys.stdout.write(md)


if __name__ == "__main__":
    main()
