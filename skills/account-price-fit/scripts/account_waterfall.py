#!/usr/bin/env python3
"""Account-level economics for pricing one product inside a whole account.

Compares options for an add-on product against the anchor deal (for example the GDS economic deal
with incentives paid to the agency). List price is not changed here: options move only the deal price,
the included allowance, credits, the price ramp and the unit ramp.

Usage:
  python account_waterfall.py --in input.json [--md report.md] [--json result.json]

Input JSON (see ../examples/atlas-example.json):
  account, currency, term_months (required, above 0; a part year is prorated)
  inputs_basis: optional {"anchor": "F: billing export 2026-09", "addon": "...", "options": "A: typed by the rep"}
                Anything not given is reported as "A (source not stated)". Figures typed by a rep are A.
  anchor:  annual_revenue, annual_incentives_paid, annual_cost_to_serve,
           annual_list_value (optional; needed for the account discount cap)
  decline: optional {annual_anchor_net, note}  the anchor's net per year if the customer declines the add-on.
           Missing: the baseline is the anchor net unchanged, labelled A.
  addon:   name, unit, list_price, floor_price, annual_units, unit_cost, granted_right (required for data or API)
           product_type (data_license, api_access, software, service, other)
           unit_cost missing: contribution and account net are Unknown, not zero.
  discount_band_pct: from the company's approval matrix, or null when Unknown (then every discount escalates)
  account_discount_cap_pct: the company's cap on total discount across the account, or null when Unknown
  escalation_path: text from pricing-governance.md, or null when Unknown
  options: [{name, price or price_by_year[], annual_units, included_units (free allowance per year),
             credits_annual, ramp (unit multipliers by year), incentive_change_annual,
             anchor_revenue_change_annual,
             gets: [text or {name, annual_value, basis}]  annual_value comes from the gets catalog in
                   deal-structures.md; a get with no value counts as zero}]

Every figure printed comes from the input. Nothing is estimated. Exit codes: 0 = result, 2 = invalid input.
"""
import argparse
import json
import math
import sys

RIGHTS = ["internal_use", "internal_analytics_shared_outputs", "display_to_third_parties", "redistribution_resale",
          "derivative_data_product", "ai_training", "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation"]
SCOPE_TYPES = {"data_license", "api_access"}
EPS = 1e-9


def fin(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def money(x, cur):
    return "Unknown" if x is None else f"{cur} {x:,.0f}"


def validate(inp):
    errs = []
    if not isinstance(inp, dict):
        return ["the input must be a JSON object"]

    def num(path, obj, key, lo=None, required=True, above=None):
        if not isinstance(obj, dict) or key not in obj or obj[key] in (None, ""):
            if required:
                errs.append(f"missing {path}.{key}")
            return
        v = obj[key]
        if not fin(v):
            errs.append(f"{path}.{key} must be a finite number")
        elif lo is not None and v < lo:
            errs.append(f"{path}.{key} cannot be below {lo}")
        elif above is not None and v <= above:
            errs.append(f"{path}.{key} must be above {above}")

    num("input", inp, "term_months", above=0)
    if not isinstance(inp.get("currency"), str) or not inp["currency"].strip():
        errs.append("missing currency (no default is assumed)")
    for k in ("annual_revenue", "annual_incentives_paid", "annual_cost_to_serve"):
        num("anchor", inp.get("anchor"), k, lo=0)
    num("anchor", inp.get("anchor"), "annual_list_value", lo=0, required=False)
    p = inp.get("addon")
    if not isinstance(p, dict):
        errs.append("missing addon")
        p = {}
    if p.get("product_type") not in ("data_license", "api_access", "software", "service", "other"):
        errs.append("addon.product_type is required: data_license, api_access, software, service or other (it decides whether a granted right must be stated)")
    num("addon", p, "list_price", above=0)
    num("addon", p, "annual_units", lo=0)
    num("addon", p, "floor_price", lo=0, required=False)
    num("addon", p, "unit_cost", lo=0, required=False)
    for k in ("discount_band_pct", "account_discount_cap_pct"):
        if inp.get(k) is not None and (not fin(inp[k]) or not 0 <= inp[k] <= 100):
            errs.append(f"{k} must be a number from 0 to 100, or null when Unknown")
    opts = inp.get("options")
    if not isinstance(opts, list) or not opts:
        errs.append("options needs at least one option")
        opts = []
    for i, o in enumerate(opts):
        path = f"options[{i}]"
        if not isinstance(o, dict):
            errs.append(f"{path} must be an object")
            continue
        if not o.get("name"):
            errs.append(f"{path} needs a name")
        if "price_by_year" in o:
            pb = o["price_by_year"]
            if not isinstance(pb, list) or not pb or not all(fin(x) and x >= 0 for x in pb):
                errs.append(f"{path}.price_by_year must be a list of prices of 0 or more")
        else:
            num(path, o, "price", lo=0)
        for k in ("annual_units", "included_units", "credits_annual"):
            num(path, o, k, lo=0, required=False)
        for k in ("incentive_change_annual", "anchor_revenue_change_annual"):
            num(path, o, k, required=False)
        r = o.get("ramp")
        if r is not None and (not isinstance(r, list) or not r or not all(fin(x) and x >= 0 for x in r)):
            errs.append(f"{path}.ramp must be a list of multipliers of 0 or more")
        for g in o.get("gets", []) or []:
            if isinstance(g, dict):
                if not g.get("name"):
                    errs.append(f"{path}.gets: each get needs a name")
                if g.get("annual_value") is not None and (not fin(g["annual_value"]) or g["annual_value"] < 0):
                    errs.append(f"{path}.gets: annual_value must be 0 or more")
            elif not isinstance(g, str):
                errs.append(f"{path}.gets must be text or objects with a name")
    d = inp.get("decline")
    if d is not None:
        if not isinstance(d, dict):
            errs.append("decline must be an object")
        else:
            num("decline", d, "annual_anchor_net", required=False)
    return errs


def norm_gets(raw):
    out = []
    for g in raw or []:
        if isinstance(g, str):
            out.append({"name": g, "annual_value": None, "basis": ""})
        else:
            out.append({"name": g["name"], "annual_value": g.get("annual_value"), "basis": g.get("basis", "")})
    return out


def evaluate(inp):
    cur = inp["currency"]
    term = float(inp["term_months"])
    n_years = int(math.ceil(term / 12.0 - EPS))
    fracs = [min(12.0, term - 12.0 * y) / 12.0 for y in range(n_years)]
    term_years = term / 12.0
    a, p = inp["anchor"], inp["addon"]
    anchor_net = float(a["annual_revenue"]) - float(a["annual_incentives_paid"]) - float(a["annual_cost_to_serve"])
    dec = inp.get("decline") or {}
    decline_given = dec.get("annual_anchor_net") is not None
    decline_net = float(dec["annual_anchor_net"]) if decline_given else anchor_net
    band = inp.get("discount_band_pct")
    cap = inp.get("account_discount_cap_pct")
    path = inp.get("escalation_path")
    list_price = float(p["list_price"])
    floor = None if p.get("floor_price") in (None, "") else float(p["floor_price"])
    unit_cost = None if p.get("unit_cost") in (None, "") else float(p["unit_cost"])
    basis = dict(anchor="A (source not stated)", addon="A (source not stated)", options="A (source not stated)")
    basis.update(inp.get("inputs_basis") or {})
    issues = []
    ptype = p["product_type"]
    right = p.get("granted_right", "")
    if ptype in SCOPE_TYPES and not right:
        issues.append("add-on is a data or API product with no granted_right: say what the customer may do (rule 8)")
    if right and right not in RIGHTS:
        issues.append(f"granted_right {right!r} is not one of the nine rights")
    if floor is None:
        issues.append("floor_price is Unknown: no walk-away check is possible")
    if band is None:
        issues.append("discount_band_pct is Unknown: set it in pricing-governance.md. NO BAND ON FILE: every discount escalates to "
                      + (path if path else "the escalation path (Unknown: set it in pricing-governance.md)"))
    if cap is None:
        issues.append("account_discount_cap_pct is Unknown: the account-level discount cap is not checked")
    if unit_cost is None:
        issues.append("unit_cost is Unknown: add-on contribution and account net are Unknown, not zero")
    if not decline_given:
        issues.append("decline baseline not supplied: it is the anchor net unchanged (A). If declining the add-on puts the anchor at risk, give decline.annual_anchor_net")
    if basis["options"].startswith("A"):
        issues.append("option figures are typed inputs (A), not read from a contract or the price book")

    results = []
    for o in inp["options"]:
        base_units = float(o.get("annual_units", p["annual_units"]))
        incl = float(o.get("included_units", 0.0))
        credits = float(o.get("credits_annual", 0.0))
        inc_chg = float(o.get("incentive_change_annual", 0.0))
        rev_chg = float(o.get("anchor_revenue_change_annual", 0.0))
        ramp = o.get("ramp") or [1.0]
        extra_flags = []
        if len(ramp) > n_years:
            extra_flags.append(f"ramp has {len(ramp)} entries but the term has {n_years} year(s): the extra entries are ignored")
        ramp = (list(ramp) + [ramp[-1]] * n_years)[:n_years]
        pb = o.get("price_by_year")
        if pb and len(pb) > n_years:
            extra_flags.append(f"price_by_year has {len(pb)} entries but the term has {n_years} year(s): the extra entries are ignored")
        prices = (list(pb) + [pb[-1]] * n_years)[:n_years] if pb else [float(o["price"])] * n_years
        gets = norm_gets(o.get("gets"))
        yearly = []
        flags = list(extra_flags)
        route_parts = []
        for y in range(n_years):
            f = fracs[y]
            u = base_units * float(ramp[y]) * f
            inc_y = incl * f
            billable = max(0.0, u - inc_y)
            rev = prices[y] * billable - credits * f
            eff = rev / u if u else None
            disc = (1.0 - eff / list_price) if eff is not None else None
            cost = unit_cost * u if unit_cost is not None else None
            contrib = rev - cost if cost is not None else None
            net_y = (anchor_net * f + rev_chg * f - inc_chg * f + contrib) if contrib is not None else None
            base_y = decline_net * f
            yearly.append({"year": y + 1, "share_of_year": f, "units": u, "billable_units": billable,
                           "price": prices[y], "effective_price": eff, "discount_vs_list_pct": None if disc is None else disc * 100.0,
                           "addon_revenue": rev, "addon_cost": cost, "addon_contribution": contrib,
                           "list_value": list_price * u, "account_net": net_y, "decline_net": base_y,
                           "incremental_vs_decline": None if net_y is None else net_y - base_y})
            if eff is None:
                continue
            if floor is not None and eff < floor - EPS:
                flags.append(f"year {y+1}: effective price {eff:.2f} is below floor {floor:.2f}: needs an exception, not a deal-desk approval")
                route_parts.append("exception")
            if disc is not None and disc > EPS:
                if band is None:
                    route_parts.append("no_band")
                elif disc * 100.0 > float(band) + EPS:
                    flags.append(f"year {y+1}: effective discount {disc*100:.1f}% exceeds the approved band {float(band):g}%: escalate")
                    route_parts.append("over_band")
        tot_u = sum(y["units"] for y in yearly)
        tot_rev = sum(y["addon_revenue"] for y in yearly)
        tot_list = sum(y["list_value"] for y in yearly)
        term_eff = tot_rev / tot_u if tot_u else None
        term_disc = (1.0 - tot_rev / tot_list) * 100.0 if tot_list else None
        if "no_band" in route_parts:
            flags.append("NO BAND ON FILE: this discount escalates to " + (path if path else "the escalation path (Unknown)"))
        if max(prices) > list_price + EPS:
            flags.append("option price is above list")
        if (incl > 0 or credits > 0) and not gets:
            flags.append("a give (allowance or credit) with no get: log it as an unrequited concession")
        if not gets and term_disc is not None and term_disc > EPS:
            flags.append("a discount with no get: trade it for term, commitment, minimum or audit terms")
        given = tot_list - tot_rev
        unvalued = [g["name"] for g in gets if g["annual_value"] is None]
        valued = sum(float(g["annual_value"]) for g in gets if g["annual_value"] is not None) * term_years
        if gets and unvalued:
            flags.append(f"{len(unvalued)} get(s) have no value on file and count as zero: " + "; ".join(unvalued))
        if given > EPS and valued + EPS < given and gets:
            flags.append(f"valued gets over the term ({money(valued, cur)}) are below the revenue given up against list ({money(given, cur)})")
        if inc_chg == 0.0 and "incentive_change_annual" not in o:
            flags.append("incentive change not stated: the account net assumes the add-on does not change incentives paid (A)")
        # a concession can also travel through the anchor: more incentive paid, or less anchor revenue
        anchor_give = (inc_chg - rev_chg) * term_years
        if anchor_give > EPS:
            flags.append(f"concession through the anchor deal: {money(anchor_give, cur)} over the term (more incentive paid or less anchor revenue). The add-on discount band does not cover it")
            route_parts.append("anchor_concession")
            if not gets:
                flags.append("an anchor concession with no get: log it as an unrequited concession")
        # account-level discount cap. Existing incentives are the baseline; only a CHANGE in incentives or anchor revenue counts here.
        acct_disc = None
        if cap is not None:
            if a.get("annual_list_value") in (None, ""):
                if (term_disc is not None and term_disc > EPS) or anchor_give > EPS:
                    flags.append("the account discount cap is set but anchor.annual_list_value is missing, so the cap cannot be checked: escalate")
                    route_parts.append("cap_unchecked")
            else:
                acct_list = float(a["annual_list_value"]) * term_years + tot_list
                acct_real = (float(a["annual_revenue"]) + rev_chg - inc_chg) * term_years + tot_rev
                acct_disc = (1.0 - acct_real / acct_list) * 100.0 if acct_list else None
                if acct_disc is not None and acct_disc > float(cap) + EPS:
                    flags.append(f"total account discount {acct_disc:.1f}% (counting any change in incentives) exceeds the account cap {float(cap):g}%: escalate")
                    route_parts.append("over_cap")
        nets = [y["account_net"] for y in yearly]
        incs = [y["incremental_vs_decline"] for y in yearly]
        if "exception" in route_parts:
            route = "EXCEPTION: below floor (exception request and log)"
        elif "no_band" in route_parts:
            route = "ESCALATE: no band on file -> " + (path if path else "escalation path Unknown")
        elif "over_band" in route_parts or "over_cap" in route_parts:
            route = "ESCALATE: outside the band or account cap"
        elif "cap_unchecked" in route_parts:
            route = "ESCALATE: the account cap cannot be checked (anchor.annual_list_value missing) -> " + (path if path else "escalation path Unknown")
        elif "anchor_concession" in route_parts:
            route = "ESCALATE: concession through the anchor deal (outside the add-on band) -> " + (path if path else "escalation path Unknown")
        elif term_disc is not None and term_disc > EPS:
            if valued <= EPS:
                route = "INSIDE BAND, NO VALUED GET: put a value on a get before this is approved as a trade; approver per pricing-governance.md"
            elif valued + EPS < given:
                route = "INSIDE BAND, GETS BELOW THE GIVE: strengthen the get or escalate; approver per pricing-governance.md"
            else:
                route = "INSIDE BAND: a give tied to a get; approver per pricing-governance.md"
        else:
            route = "AT OR ABOVE LIST"
        if cap is None and route.startswith("INSIDE BAND"):
            route += " (account cap Unknown: not checked)"
        results.append({
            "name": o["name"], "included_units": incl, "credits_annual": credits, "ramp": ramp, "prices": prices,
            "gets": gets, "years": yearly, "route": route,
            "term_effective_price": term_eff, "term_discount_vs_list_pct": term_disc,
            "revenue_given_up_vs_list": given, "valued_gets_over_term": valued,
            "term_addon_revenue": tot_rev,
            "term_account_net": None if any(n is None for n in nets) else sum(nets),
            "term_incremental_vs_decline": None if any(n is None for n in incs) else sum(incs),
            "account_discount_pct": acct_disc, "flags": flags})
    inc_share = (100.0 * float(a["annual_incentives_paid"]) / float(a["annual_revenue"])) if float(a["annual_revenue"]) else None
    return {"account": inp.get("account", ""), "currency": cur, "term_months": term, "years": n_years,
            "anchor_net_annual": anchor_net, "decline_net_annual": decline_net, "decline_given": decline_given,
            "incentive_share_of_anchor_revenue_pct": inc_share,
            "addon": {"name": p.get("name", ""), "list_price": list_price, "floor_price": floor, "granted_right": right,
                      "product_type": ptype, "unit": p.get("unit", "unit"), "unit_cost": unit_cost},
            "discount_band_pct": band, "account_discount_cap_pct": cap, "escalation_path": path,
            "inputs_basis": basis, "issues": issues, "options": results}


def to_md(r):
    c = r["currency"]
    L = [f"# Account economics: {r['account']}", ""]
    if r["discount_band_pct"] is None:
        L += ["> **NO BAND ON FILE: every discount escalates to " + (r["escalation_path"] or "the escalation path (Unknown)") + ".**", ""]
    ad = r["addon"]
    L += [f"Add-on: {ad['name']} at list {ad['list_price']:.2f} per {ad['unit']}"
          + (f", floor {ad['floor_price']:.2f}" if ad['floor_price'] is not None else ", floor Unknown")
          + (f", granted right {ad['granted_right']}" if ad['granted_right'] else ", granted right NOT STATED") + ".",
          f"Term: {r['term_months']:g} months ({r['years']} contract year(s); a part year is prorated).",
          f"Anchor net per year (revenue less incentives paid less cost to serve): {money(r['anchor_net_annual'], c)}. Basis: {r['inputs_basis']['anchor']}. "
          + (f"Incentives are {r['incentive_share_of_anchor_revenue_pct']:.1f}% of anchor revenue." if r['incentive_share_of_anchor_revenue_pct'] is not None else ""),
          f"If the customer declines the add-on, the anchor net per year is {money(r['decline_net_annual'], c)} "
          + ("(supplied)." if r["decline_given"] else "(A: assumed unchanged)."),
          "Discount band: " + (f"{r['discount_band_pct']:g}%" if r['discount_band_pct'] is not None else "Unknown")
          + ". Account discount cap: " + (f"{r['account_discount_cap_pct']:g}%" if r['account_discount_cap_pct'] is not None else "Unknown") + ".", ""]
    L += ["| Option | Route | Term effective price | Term discount vs list | Add-on revenue over term | Account net over term | Gain over declining |",
          "|---|---|---|---|---|---|---|"]
    for o in r["options"]:
        te = "-" if o["term_effective_price"] is None else f"{o['term_effective_price']:.2f}"
        td = "-" if o["term_discount_vs_list_pct"] is None else f"{o['term_discount_vs_list_pct']:.1f}%"
        L.append(f"| {o['name']} | {o['route']} | {te} | {td} | {money(o['term_addon_revenue'], c)} | {money(o['term_account_net'], c)} | {money(o['term_incremental_vs_decline'], c)} |")
    L.append("")
    for o in r["options"]:
        L.append(f"## {o['name']}")
        L.append("| Year | Share of year | Units | Price | Effective price | Discount vs list | Add-on contribution | Account net |")
        L.append("|---|---|---|---|---|---|---|---|")
        for y in o["years"]:
            ep = "-" if y["effective_price"] is None else f"{y['effective_price']:.2f}"
            dp = "-" if y["discount_vs_list_pct"] is None else f"{y['discount_vs_list_pct']:.1f}%"
            L.append(f"| {y['year']} | {y['share_of_year']:.2f} | {y['units']:,.0f} | {y['price']:.2f} | {ep} | {dp} | {money(y['addon_contribution'], c)} | {money(y['account_net'], c)} |")
        if o["gets"]:
            L.append("Gets: " + "; ".join(g["name"] + (f" ({c} {g['annual_value']:,.0f} a year, {g['basis'] or 'basis not stated'})" if g["annual_value"] is not None else " (no value on file)") for g in o["gets"]))
        L.append(f"Revenue given up against list over the term: {money(o['revenue_given_up_vs_list'], c)}; valued gets over the term: {money(o['valued_gets_over_term'], c)}.")
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
    try:
        with open(args.inp, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"Cannot read the input: {e}", file=sys.stderr)
        return 2
    errs = validate(data)
    if errs:
        print("Input errors:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        return 2
    res = evaluate(data)
    md = to_md(res)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(md)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2)
    sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
