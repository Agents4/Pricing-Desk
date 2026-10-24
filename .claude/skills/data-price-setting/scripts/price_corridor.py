#!/usr/bin/env python3
"""Price corridor calculator for a product or data licence.

Works for any product the pricing desk prices (API access, software, services, data).

The prices are for the rights we GRANT the customer: what the customer may do with a data product or
API responses (base_right and rights[]). The pricing desk assumes we hold the rights to grant them;
the product manager checks that separately with the rights pack. Set product_type to data_license or
api_access for a product that grants a scope; leave rights out for software and services.

Triangulates three anchors into a price corridor and a recommended price:
  - cost floor         (what the price must cover, including supplier royalties and target margin)
  - value-based price  (customer value x share captured), with a hard cap
  - market reference   (comparable products, weighted by comparability)
  - WTP evidence       (stated maximum prices, when there are enough points)

It also prices extra rights granted to the customer from the incremental value they create (not from
fixed multipliers), tests sensitivities, and values wider coverage
through the share of customers or volume the product could reach.

Company values are never defaulted here. The expected discount, the value cap (max_capture_share),
each right's capture share, the coverage cap, the flag cutoffs and the minimum number of willingness-to-pay
points come from the input (which gets them from pricing-governance.md, the Council or the study design).
A missing required value stops the run (exit 2). A missing optional value switches that check off and
says so in the report. The margin floor is a share of PRICE: floor = unit cost / (1 - royalty - margin).

Usage:
    python price_corridor.py --in input.json [--md report.md] [--json result.json] [--csv lines.csv]

Exit codes: 0 = result produced, 2 = invalid input. A NOT_VIABLE result still exits 0;
read the status line.
"""
import argparse
import copy
import csv
import json
import math
import re
import statistics
import sys

SOURCES = ("estimate", "interview", "pilot", "contract data", "contract_data")
ANCHORS = ("value", "market", "wtp")
REVIEW_KEYS = ("divergence_flag", "divergence_stop", "segment_spread_flag", "weak_comparability")
SCOPE_TYPES = ("data_license", "api_access")
LINE_COLUMNS = ["line_id", "product_id", "product_family", "product_type", "conferred_right", "right_basis", "delivery",
                "unit", "tier_min", "tier_max", "list_price", "floor_price", "currency", "term_months", "tier_model",
                "minimum_commitment", "retention_term", "audit_right", "status", "version", "notes"]


def scoped(inp):
    """True when the product grants a data or API scope (a conferred right)."""
    return inp.get("product_type") in SCOPE_TYPES or "base_right" in inp or bool(inp.get("rights"))


def base_right_of(inp):
    return inp.get("base_right", "internal_use" if scoped(inp) else "")


# ----------------------------------------------------------------------------- validation
def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate(inp):
    errs = []
    if not isinstance(inp, dict):
        return ["the input must be a JSON object"]

    def need(path, obj, key, kind=(int, float)):
        if not isinstance(obj, dict) or key not in obj:
            errs.append(f"missing {path}.{key}")
            return None
        v = obj[key]
        if kind == (int, float):
            if not finite(v):
                errs.append(f"{path}.{key} must be a finite number")
                return None
        elif kind and (not isinstance(v, kind) or isinstance(v, bool)):
            errs.append(f"{path}.{key} has the wrong type")
            return None
        return v

    for k in ("product", "currency", "unit"):
        need("input", inp, k, str)
    cost = inp.get("cost")
    if not isinstance(cost, dict):
        errs.append("missing cost")
    else:
        f = need("cost", cost, "annual_fixed")
        v = need("cost", cost, "variable_per_unit")
        r = need("cost", cost, "royalty_pct")
        m = need("cost", cost, "min_margin_pct")
        c = need("cost", cost, "cannibalization_per_unit")
        for name, val in (("annual_fixed", f), ("variable_per_unit", v), ("royalty_pct", r), ("min_margin_pct", m),
                          ("cannibalization_per_unit", c)):
            if val is not None and not finite(val):
                errs.append(f"cost.{name} must be a finite number")
            elif isinstance(val, (int, float)) and val < 0:
                errs.append(f"cost.{name} cannot be negative")
        if finite(r) and finite(m) and r + m >= 1:
            errs.append("cost.royalty_pct + cost.min_margin_pct must be below 1 (the margin floor is a share of price)")
    # ---- company values: required, never defaulted
    disc = (inp.get("discount") or {})
    if "expected_list_to_realized" in disc:
        d = disc["expected_list_to_realized"]
        if not finite(d) or not 0 <= d < 1:
            errs.append("discount.expected_list_to_realized must be a number from 0 up to (not including) 1")
    value = inp.get("value")
    if not isinstance(value, dict):
        errs.append("missing value")
        value = {}
    mc = value.get("max_capture_share")
    if mc is None:
        errs.append("missing value.max_capture_share (the most of customer value the company will charge for; "
                    "from pricing-governance.md or the Council. Unknown if blank: stop and ask)")
    elif not finite(mc) or not 0 < mc <= 1:
        errs.append("value.max_capture_share must be above 0 and at most 1")
    segs = value.get("segments")
    if not segs or not isinstance(segs, list):
        errs.append("value.segments needs at least one segment")
    else:
        for i, s in enumerate(segs):
            p = f"value.segments[{i}]"
            if not isinstance(s, dict):
                errs.append(f"{p} must be an object")
                continue
            for k in ("customers", "penetration", "units_per_customer", "value_per_customer_per_year", "capture_share"):
                need(p, s, k)
            if s.get("source", "estimate") not in SOURCES:
                errs.append(f"{p}.source must be one of {sorted(set(SOURCES))}")
            for k in ("customers", "value_per_customer_per_year"):
                if finite(s.get(k)) and s[k] < 0:
                    errs.append(f"{p}.{k} cannot be negative")
            if finite(s.get("penetration")) and not 0 < s["penetration"] <= 1:
                errs.append(f"{p}.penetration must be above 0 and at most 1")
            if finite(s.get("capture_share")) and not 0 < s["capture_share"] < 1:
                errs.append(f"{p}.capture_share must be between 0 and 1")
            if finite(s.get("units_per_customer")) and s["units_per_customer"] <= 0:
                errs.append(f"{p}.units_per_customer must be above 0")
            if finite(s.get("capture_share")) and finite(mc) and s["capture_share"] > mc:
                errs.append(f"{p}.capture_share exceeds value.max_capture_share")
    cov = inp.get("coverage")
    if cov:
        if not isinstance(cov, dict):
            errs.append("coverage must be an object")
        else:
            for k in ("current", "reference", "resolved"):
                if k in cov and (not finite(cov[k]) or cov[k] <= 0):
                    errs.append(f"coverage.{k} must be above 0")
            if bool(cov.get("current")) != bool(cov.get("reference")):
                errs.append("coverage needs both current and reference, or neither")
            if cov.get("current") and cov.get("reference"):
                if not finite(cov.get("elasticity")) or cov["elasticity"] <= 0:
                    errs.append("coverage.elasticity is required (above 0) when coverage is used; 1 means value is proportional to coverage")
            if "max_factor" in cov and (not finite(cov["max_factor"]) or cov["max_factor"] < 1):
                errs.append("coverage.max_factor must be 1 or more")
    comps = (inp.get("market") or {}).get("comps", [])
    for i, c in enumerate(comps):
        if not isinstance(c, dict):
            errs.append(f"market.comps[{i}] must be an object")
            continue
        for k in ("unit_price", "comparability"):
            need(f"market.comps[{i}]", c, k)
        if finite(c.get("unit_price")) and c["unit_price"] <= 0:
            errs.append(f"market.comps[{i}].unit_price must be above 0")
        if finite(c.get("comparability")) and not 0 < c["comparability"] <= 1:
            errs.append(f"market.comps[{i}].comparability must be above 0 and at most 1")
    wtp = inp.get("wtp") or {}
    for i, w in enumerate(wtp.get("points", [])):
        v = need(f"wtp.points[{i}]", w, "max_price_per_unit")
        if finite(v) and v <= 0:
            errs.append(f"wtp.points[{i}].max_price_per_unit must be above 0")
    if "min_points" in wtp and (not isinstance(wtp["min_points"], int) or isinstance(wtp["min_points"], bool) or wtp["min_points"] < 1):
        errs.append("wtp.min_points must be a whole number of 1 or more")
    for i, r in enumerate(inp.get("rights", [])):
        if not isinstance(r, dict):
            errs.append(f"rights[{i}] must be an object")
            continue
        for k in ("right", "incremental_value_per_unit"):
            if k not in r:
                errs.append(f"rights[{i}] missing {k}")
        if "capture_share" not in r:
            errs.append(f"rights[{i}] missing capture_share (the share of the added value we charge for; the Council's or "
                        "requester's call, no default)")
        elif not finite(r["capture_share"]) or not 0 < r["capture_share"] < 1:
            errs.append(f"rights[{i}].capture_share must be between 0 and 1")
        for k in ("incremental_value_per_unit", "incremental_cost_per_unit"):
            if k in r and (not finite(r[k]) or r[k] < 0):
                errs.append(f"rights[{i}].{k} must be a number of 0 or more")
    wts = inp.get("weights")
    if wts is not None:
        if not isinstance(wts, dict):
            errs.append("weights must be an object")
        else:
            for k, v in wts.items():
                if k not in ANCHORS:
                    errs.append(f"weights.{k} is not an anchor (use {', '.join(ANCHORS)})")
                elif not finite(v) or v < 0:
                    errs.append(f"weights.{k} must be a number of 0 or more")
    rv = inp.get("review") or {}
    for k, v in rv.items():
        if k not in REVIEW_KEYS:
            errs.append(f"review.{k} is not a known setting (use {', '.join(REVIEW_KEYS)})")
        elif not finite(v) or v <= 0:
            errs.append(f"review.{k} must be a number above 0")
    return errs


# ----------------------------------------------------------------------------- core
def quantiles(vals):
    vals = sorted(vals)
    if len(vals) < 4:
        return None, statistics.median(vals), None
    q = statistics.quantiles(vals, n=4, method="inclusive")
    return q[0], q[1], q[2]


def compute(inp):
    cost = inp["cost"]
    cov = inp.get("coverage") or {}
    segs_in = inp["value"]["segments"]
    max_capture = inp["value"]["max_capture_share"]
    disc = (inp.get("discount") or {}).get("expected_list_to_realized")  # None = Unknown
    rv = inp.get("review") or {}
    r = cost.get("royalty_pct", 0.0)
    m = cost["min_margin_pct"]
    cannib = cost.get("cannibalization_per_unit", 0.0)

    cf = 1.0
    cf_flag = None
    if cov.get("current") and cov.get("reference"):
        cf = (cov["current"] / cov["reference"]) ** cov["elasticity"]
        if cov.get("max_factor") and cf > cov["max_factor"]:
            cf = cov["max_factor"]
        elif cf > 1 and not cov.get("max_factor"):
            cf_flag = (f"Current coverage is above the coverage the value estimates assume, so value is scaled up by {cf:.2f}x "
                       "with no cap set (coverage.max_factor). Confirm that is intended.")
    segs = []
    for s in segs_in:
        buyers = s["customers"] * s["penetration"]
        units = buyers * s["units_per_customer"]
        vpu = s["value_per_customer_per_year"] * cf / s["units_per_customer"]
        segs.append(dict(
            name=s.get("name", "segment"), buyers=buyers, units=units, source=s.get("source", "estimate"),
            value_per_unit=vpu, vbp=vpu * s["capture_share"], vmax=vpu * max_capture,
            capture=s["capture_share"],
        ))
    units = sum(s["units"] for s in segs)
    if units <= 0:
        raise ValueError("expected units come to zero (check customers, penetration and units_per_customer)")
    unit_cost = cost["annual_fixed"] / units + cost["variable_per_unit"] + cannib
    floor = unit_cost / (1 - r - m)

    v_target = sum(s["vbp"] * s["units"] for s in segs) / units
    v_cap = sum(s["vmax"] * s["units"] for s in segs) / units
    est_share = sum(s["units"] for s in segs if s["source"] == "estimate") / units

    comps = [c for c in (inp.get("market") or {}).get("comps", [])]
    market = None
    if comps:
        w = sum(c["comparability"] for c in comps)
        market = dict(
            ref=sum(c["unit_price"] * c["comparability"] for c in comps) / w,
            low=min(c["unit_price"] for c in comps), high=max(c["unit_price"] for c in comps),
            n=len(comps), avg_comp=w / len(comps),
        )

    wt = inp.get("wtp") or {}
    pts = [p["max_price_per_unit"] for p in wt.get("points", [])]
    wtp = None
    if pts:
        p25, med, p75 = quantiles(pts)
        minp = wt.get("min_points")
        wtp = dict(n=len(pts), p25=p25, median=med, p75=p75, min_points=minp, usable=bool(minp) and len(pts) >= minp)

    anchors = {"value": v_target}
    if market:
        anchors["market"] = market["ref"]
    if wtp and wtp["usable"]:
        anchors["wtp"] = wtp["median"]
    supplied = inp.get("weights")
    if supplied:
        weights = {k: supplied.get(k, 0.0) for k in anchors}
        weights_basis = "weights supplied in the input"
    else:
        weights = {k: 1.0 for k in anchors}
        weights_basis = "equal weights: no company weighting was supplied"
    wsum = sum(weights.values())
    if wsum <= 0:
        raise ValueError("the weights for the available anchors add to zero")
    blended = sum(weights[k] * anchors[k] for k in anchors) / wsum

    out = dict(units=units, coverage_factor=cf, unit_cost=unit_cost, floor=floor, value_target=v_target,
               value_cap=v_cap, anchors=anchors, blended=blended, market=market, wtp=wtp, segments=segs,
               weights_used={k: weights[k] / wsum for k in anchors}, weights_basis=weights_basis, disc=disc,
               estimate_share=est_share)

    flags = []
    if cf_flag:
        flags.append(cf_flag)
    if floor > v_cap:
        out["status"] = "NOT_VIABLE"
        out["target"] = out["list"] = None
        flags.append("The cost floor is above the value cap. No price works at this cost, scope, and value. Options: cut cost or "
                     "scope, find a higher-value segment or right to grant, share cost with another product, or re-check the value estimate.")
    else:
        t = blended
        if t < floor:
            t = floor
            flags.append("Blended anchors are below the cost floor, so the price sits at the floor with no margin of safety.")
        if t > v_cap:
            t = v_cap
            flags.append("Blended anchors are above the value cap, so the price is capped at the cap.")
        out["target"] = t
        if disc is None:
            out["list"] = None
            flags.append("List price NOT computed: discount.expected_list_to_realized is Unknown (not supplied). "
                         "Take the expected discount from pricing-governance.md or the Council and rerun. The realized price is shown.")
        else:
            out["list"] = t / (1 - disc)
        out["status"] = "VIABLE"
        out["revenue"] = units * t
        out["contribution"] = units * t * (1 - r) - units * (cost["variable_per_unit"] + cannib) - cost["annual_fixed"]

    if len(anchors) > 1:
        ratio = max(anchors.values()) / min(anchors.values())
        out["divergence"] = ratio
        if rv.get("divergence_stop") and ratio > rv["divergence_stop"]:
            flags.append(f"The anchors differ by {ratio:.1f}x (above the stop cutoff of {rv['divergence_stop']}x). Find out why before trusting a number (wrong segment, wrong unit, or a weak comp).")
        elif rv.get("divergence_flag") and ratio > rv["divergence_flag"]:
            flags.append(f"The anchors differ by {ratio:.1f}x (above the flag cutoff of {rv['divergence_flag']}x). Check which one is weakest.")
        elif not rv.get("divergence_flag") and not rv.get("divergence_stop"):
            flags.append(f"The anchors differ by {ratio:.1f}x. No divergence cutoff is set (review.divergence_flag), so this is shown, not judged.")
    if len(segs) > 1:
        lo = min(s["vbp"] for s in segs)
        spread = (max(s["vbp"] for s in segs) / lo) if lo > 0 else None
        out["segment_spread"] = spread
        if spread is None:
            flags.append("A segment has zero value-based price, so the spread across segments cannot be computed.")
        elif rv.get("segment_spread_flag") and spread > rv["segment_spread_flag"]:
            flags.append(f"Value-based prices differ {spread:.1f}x across segments (above the cutoff of {rv['segment_spread_flag']}x). Consider fenced segment prices (by use case or customer type) instead of one list price.")
    if market and rv.get("weak_comparability") and market["avg_comp"] < rv["weak_comparability"]:
        flags.append(f"Comparables are weak (average comparability {market['avg_comp']:.2f}, below the cutoff of {rv['weak_comparability']}). Treat the market anchor as context, not a price.")
    if not market:
        flags.append("No market comparables. Add comparables with sources, or state that none exist.")
    if not wtp:
        flags.append("No willingness-to-pay evidence.")
    elif not wtp["usable"]:
        if not wtp["min_points"]:
            flags.append(f"{wtp['n']} willingness-to-pay points are shown but NOT blended: no minimum number of points is set "
                         "(wtp.min_points, from the study design or the Council).")
        else:
            flags.append(f"Only {wtp['n']} willingness-to-pay points; the minimum set is {wtp['min_points']}, so they are shown, not blended.")
    if est_share > 0:
        flags.append(f"{est_share:.0%} of expected units rest on internal estimates of customer value. Quantify with customers or a pilot.")

    reasons = [f"{len(anchors)} of 3 anchors in the blend ({', '.join(anchors)})",
               f"{est_share:.0%} of units rest on estimate-only value evidence",
               f"{wtp['n'] if wtp else 0} willingness-to-pay points" + ("" if not wtp or wtp["usable"] else " (not blended)"),
               f"{market['n'] if market else 0} comparables" + (f" at {market['avg_comp']:.2f} average comparability" if market else "")]
    # The tool states the evidence; it does not invent a High/Medium scale. Low is the only rating it will give.
    low = len(anchors) == 1 or est_share >= 1
    out["confidence"] = "Low" if low else "Not rated (the company has set no confidence criteria)"
    out["confidence_reasons"] = reasons
    out["flags"] = flags
    return out


TEST_SIZES = {"capture": 0.2, "cost": 0.2, "demand": 0.3, "market": 0.2}


def run_scenarios(inp):
    """Sensitivity tests. The test sizes are this tool's own (shown in each label), not company thresholds;
    override them with a `sensitivity` block: {capture, cost, demand, market} as shares."""
    base = compute(inp)
    scen = []
    sz = dict(TEST_SIZES)
    sz.update(inp.get("sensitivity") or {})

    def add(label, fn):
        x = copy.deepcopy(inp)
        fn(x)
        try:
            res = compute(x)
        except ValueError as e:
            scen.append((label, dict(status="NOT_COMPUTED: " + str(e), floor=None, target=None, contribution=None)))
            return
        scen.append((label, res))

    def capture(f):
        def go(x):
            for s in x["value"]["segments"]:
                s["capture_share"] = min(s["capture_share"] * f, x["value"]["max_capture_share"])
        return go

    def costs(f):
        def go(x):
            x["cost"]["annual_fixed"] *= f
            x["cost"]["variable_per_unit"] *= f
        return go

    def demand(f):
        def go(x):
            for s in x["value"]["segments"]:
                s["penetration"] = min(1, s["penetration"] * f)
        return go

    def market(f):
        def go(x):
            for c in (x.get("market") or {}).get("comps", []):
                c["unit_price"] *= f
        return go

    add(f"Value share captured -{sz['capture']:.0%}", capture(1 - sz["capture"]))
    add(f"Value share captured +{sz['capture']:.0%}", capture(1 + sz["capture"]))
    add(f"Costs +{sz['cost']:.0%}", costs(1 + sz["cost"]))
    add(f"Demand -{sz['demand']:.0%}", demand(1 - sz["demand"]))
    if (inp.get("market") or {}).get("comps"):
        add(f"Market reference -{sz['market']:.0%}", market(1 - sz["market"]))
    cov = inp.get("coverage") or {}
    if cov.get("resolved") and cov.get("current"):
        def resolved(x):
            x["coverage"]["current"] = x["coverage"]["resolved"]
        add(f"Wider coverage ({cov['current']:.0%} to {cov['resolved']:.0%})", resolved)
    return base, scen


def rights_ladder(inp, base):
    out = []
    if base["status"] != "VIABLE":
        return out
    r = inp["cost"].get("royalty_pct", 0.0)
    m = inp["cost"]["min_margin_pct"]
    disc = base["disc"]
    base_right = base_right_of(inp)
    out.append(dict(right=base_right or "(no granted scope)", status="Base", price=base["target"],
                    list=base["list"], floor=base["floor"], multiple=1.0,
                    note="Base right priced from the corridor." + ("" if "base_right" in inp else " The base right was NOT stated; internal_use is an assumption (A).")))
    for x in inp.get("rights", []):
        right = x["right"]
        if right == base_right:
            continue
        cap = x["capture_share"]
        add_cost = x.get("incremental_cost_per_unit", 0.0) / (1 - r - m)
        price = base["target"] + x["incremental_value_per_unit"] * cap + add_cost
        out.append(dict(right=right, status="Priced", price=price, list=(price / (1 - disc)) if disc is not None else None,
                        floor=base["floor"] + add_cost,
                        multiple=price / base["target"],
                        note=f"Base + {cap:.0%} of {x['incremental_value_per_unit']:,.2f} added value per unit + risk and supplier cost. Basis: {x.get('basis', 'not stated, treat as a hypothesis')}"))
    return out


# ----------------------------------------------------------------------------- output
def money(v, cur):
    return "-" if v is None else f"{cur} {v:,.2f}"


def render(inp, base, scen, ladder):
    cur = inp["currency"]
    L = []
    if inp.get("illustrative"):
        L.append("> ILLUSTRATIVE: the inputs are invented to show the method. Do not quote these prices.\n")
    L.append(f"# Price corridor: {inp['product']}")
    if scoped(inp):
        L.append(f"Priced for the right granted to the customer: **{base_right_of(inp)}**. This price assumes we may grant it; the product manager checks that with the rights pack.\n")
    L.append(f"Unit: {inp['unit']}. Status: **{base['status']}**. Confidence: **{base['confidence']}**.\n")
    if base["status"] == "VIABLE":
        prov = "Provisional (low confidence): " if base["confidence"] == "Low" else ""
        if base["list"] is None:
            lp = "list price Unknown (the expected discount was not supplied)"
        else:
            lp = f"list price {money(base['list'], cur)} (list assumes {base['disc']:.0%} average discount, as supplied)"
        L.append(f"**{prov}Recommended realized price {money(base['target'], cur)}; {lp}.** "
                 f"Cost floor {money(base['floor'], cur)} (margin floor taken on price). The deal desk walk-away floor is the one in pricing-governance.md, not this number.\n")
        L.append(f"At {base['units']:,.0f} units a year: revenue {money(base['revenue'], cur)}, contribution {money(base['contribution'], cur)}.\n")
    else:
        L.append(f"**No viable price.** Cost floor {money(base['floor'], cur)} is above the value cap {money(base['value_cap'], cur)}.\n")
    L.append("## Corridor")
    L.append("| Anchor | Per unit | Notes |\n|---|---|---|")
    L.append(f"| Cost floor | {money(base['floor'], cur)} | unit cost {money(base['unit_cost'], cur)} incl. fixed cost spread over {base['units']:,.0f} units |")
    L.append(f"| Value-based price | {money(base['value_target'], cur)} | coverage factor {base['coverage_factor']:.2f} |")
    L.append(f"| Value cap | {money(base['value_cap'], cur)} | the most a customer could justify |")
    if base["market"]:
        mk = base["market"]
        L.append(f"| Market reference | {money(mk['ref'], cur)} | range {money(mk['low'], cur)} to {money(mk['high'], cur)}, {mk['n']} comps |")
    if base["wtp"]:
        w = base["wtp"]
        note = f"n={w['n']}" + ("" if w["usable"] else ", shown, not blended")
        L.append(f"| WTP median | {money(w['median'], cur)} | {note} |")
    L.append(f"| Blended | {money(base['blended'], cur)} | " + ", ".join(f"{k} {v:.0%}" for k, v in base["weights_used"].items()) + f" ({base['weights_basis']}) |")
    L.append("\n## Segments")
    L.append("| Segment | Units/yr | Value per unit | Value-based price | Cap | Evidence |\n|---|---|---|---|---|---|")
    for s in base["segments"]:
        L.append(f"| {s['name']} | {s['units']:,.0f} | {money(s['value_per_unit'], cur)} | {money(s['vbp'], cur)} | {money(s['vmax'], cur)} | {s['source']} |")
    if ladder:
        L.append("\n## Granted-right ladder (what the customer may do)")
        L.append("| Right | Status | Realized | List | Multiple | Basis |\n|---|---|---|---|---|---|")
        for x in ladder:
            L.append(f"| {x['right']} | {x['status']} | {money(x['price'], cur)} | {money(x['list'], cur)} | {x['multiple']:.2f}x | {x['note']} |")
    L.append("\n## Sensitivity")
    L.append("Price comes from value, market, and willingness to pay, so cost and demand changes show up in the floor and contribution, not the price.\n")
    L.append("| Scenario | Status | Realized | Change | Floor | Headroom over floor | Contribution |\n|---|---|---|---|---|---|---|")
    if base["status"] == "VIABLE":
        L.append(f"| Base case | VIABLE | {money(base['target'], cur)} | | {money(base['floor'], cur)} | {base['target'] / base['floor'] - 1:.0%} | {money(base['contribution'], cur)} |")
    for label, res in scen:
        if res["status"] == "VIABLE":
            chg = f"{res['target'] / base['target'] - 1:+.0%}" if base["status"] == "VIABLE" else ""
            L.append(f"| {label} | VIABLE | {money(res['target'], cur)} | {chg} | {money(res['floor'], cur)} | "
                     f"{res['target'] / res['floor'] - 1:.0%} | {money(res['contribution'], cur)} |")
        else:
            L.append(f"| {label} | {res['status']} | - | | {money(res.get('floor'), cur)} | - | - |")
    cov = inp.get("coverage") or {}
    if cov.get("resolved") and base["status"] == "VIABLE":
        for label, res in scen:
            if label.startswith("Wider coverage"):
                if res["status"] == "VIABLE":
                    gain = (res["target"] - base["target"]) * base["units"]
                    L.append(f"\nWider coverage lifts annual revenue by about {money(gain, cur)} through price alone, before any extra volume from wider coverage.")
    L.append("\n## Confidence")
    L.append(", ".join(base["confidence_reasons"]) + ".")
    if base["flags"]:
        L.append("\n## Flags")
        L += [f"- {f}" for f in base["flags"]]
    L.append("\n## Next evidence to collect")
    nxt = []
    if base["market"] is None:
        nxt.append("Comparable products with source links (run `analog-research` or `competitive-price-scan`).")
    if not base["wtp"] or not base["wtp"]["usable"]:
        nxt.append("Willingness-to-pay data: run the `wtp-study-design` skill, and set the minimum number of points it must reach.")
    if any(s["source"] == "estimate" for s in base["segments"]):
        nxt.append("Customer-validated value for estimated segments: interviews or a priced pilot.")
    nxt.append("Pilot with design partners at the recommended price (the number comes from the pilot plan or `pricing-governance.md`; Unknown if blank), and record accept, counter, and decline.")
    L += [f"- {n}" for n in nxt]
    return "\n".join(L) + "\n"


def lines_csv(inp, base, ladder, path):
    if base["status"] != "VIABLE":
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LINE_COLUMNS)
        w.writeheader()
        for x in ladder:
            ur = x["right"] if scoped(inp) else ""
            if x.get("right", "").startswith("("):
                ur = ""
            pid = inp.get("product_id") or re.sub(r"[^A-Z0-9]+", "-", inp["product"].upper()).strip("-")
            # This tool cannot know where the right comes from; the analyst or the product manager sets it.
            basis = inp.get("right_basis", "assumed") if ur else ""
            notes = []
            if x["list"] is None:
                notes.append("list price Unknown: discount not supplied")
            if "term_months" not in inp:
                notes.append("term_months not supplied: set before release")
            if ur and x.get("status") != "Base":
                notes.append("keeping or wider right: add minimum_commitment, retention_term, audit_right")
            w.writerow(dict(
                line_id=f"PL-{pid}-{ur or 'base'}", product_id=pid, product_family=inp.get("product_family", pid),
                product_type=inp.get("product_type") or "other",
                conferred_right=ur, right_basis=basis, delivery="", unit=inp["unit"], tier_min=1, tier_max="",
                list_price="" if x["list"] is None else round(x["list"], 2), floor_price=round(x["floor"], 2),
                currency=inp["currency"], term_months=inp.get("term_months", ""),
                tier_model="all_units", minimum_commitment="", retention_term="", audit_right="",
                status="Draft", version="0.1", notes="; ".join(notes)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--csv")
    a = ap.parse_args()
    try:
        with open(a.inp, encoding="utf-8") as fh:
            inp = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"Cannot read the input: {e}", file=sys.stderr)
        return 2
    errs = validate(inp)
    if errs:
        print("Input errors:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        return 2
    try:
        base, scen = run_scenarios(inp)
    except ValueError as e:
        print(f"Input errors:\n - {e}", file=sys.stderr)
        return 2
    ladder = rights_ladder(inp, base)
    md = render(inp, base, scen, ladder)
    print(md)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(md)
    if a.json:
        slim = {k: v for k, v in base.items()}
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(dict(result=slim, ladder=ladder, scenarios=[dict(label=l, status=r["status"], target=r.get("target")) for l, r in scen]),
                      fh, indent=2, default=float)
    if a.csv:
        lines_csv(inp, base, ladder, a.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
