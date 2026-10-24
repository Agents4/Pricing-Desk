#!/usr/bin/env python3
"""Price corridor calculator for a product or data licence.

Works for any product the pricing desk prices (API access, software, services, data). Data rights
only matter when the product carries data: give a dataset_id and the rights lists. Rights are a
basis for the price, not a gate on running it:
  eligible_rights     use rights confirmed by Legal (Granted or Conditional): priced as Confirmed
  prohibited_rights   use rights Legal has confirmed as Prohibited: not priced (Blocked)
  anything else       priced as Provisional: the price is a strategy, not yet cleared to quote

Triangulates three anchors into a price corridor and a recommended price:
  - cost floor         (what the price must cover, including supplier royalties and target margin)
  - value-based price  (customer value x share captured), with a hard cap
  - market reference   (comparable products, weighted by comparability)
  - WTP evidence       (stated maximum prices, when there are enough points)

It also prices extra use rights from the incremental value they create (not from
fixed multipliers), tests sensitivities, and values resolving open rights items
through the coverage the product could reach.

Usage:
    python price_corridor.py --in input.json [--md report.md] [--json result.json] [--csv lines.csv]

Exit codes: 0 = result produced, 2 = invalid input. A NOT_VIABLE result still exits 0;
read the status line.
"""
import argparse
import copy
import csv
import json
import re
import statistics
import sys

SOURCE_QUALITY = {"estimate": 0.5, "interview": 0.75, "pilot": 1.0, "contract data": 1.0, "contract_data": 1.0}
DEFAULT_WEIGHTS = {"value": 0.4, "market": 0.3, "wtp": 0.3}
LINE_COLUMNS = ["line_id", "product_id", "product_type", "dataset_id", "use_right", "delivery", "unit", "tier_min",
                "tier_max", "list_price", "floor_price", "currency", "term_months", "tier_model", "status", "version",
                "rights_relevance", "notes"]


def rights_bound(inp):
    return bool(inp.get("dataset_id")) or any(k in inp for k in ("eligible_rights", "provisional_rights", "prohibited_rights"))


def base_right_of(inp):
    return inp.get("base_right", "internal_use" if rights_bound(inp) else "")


def right_basis(inp, right):
    """Confirmed, Provisional, Blocked, or N/A (the product carries no data rights)."""
    if not rights_bound(inp) or not right:
        return "N/A"
    if right in (inp.get("prohibited_rights") or []):
        return "Blocked"
    if right in (inp.get("eligible_rights") or []):
        return "Confirmed"
    return "Provisional"


# ----------------------------------------------------------------------------- validation
def validate(inp):
    errs = []

    def need(path, obj, key, kind=(int, float)):
        if not isinstance(obj, dict) or key not in obj:
            errs.append(f"missing {path}.{key}")
            return None
        v = obj[key]
        if kind and (not isinstance(v, kind) or isinstance(v, bool)):
            errs.append(f"{path}.{key} has the wrong type")
            return None
        return v

    for k in ("product", "currency", "unit"):
        need("input", inp, k, str)
    for k in ("eligible_rights", "provisional_rights", "prohibited_rights"):
        if k in inp and not isinstance(inp[k], list):
            errs.append(f"{k} must be a list of use rights")
    cost = inp.get("cost")
    if not isinstance(cost, dict):
        errs.append("missing cost")
    else:
        f = need("cost", cost, "annual_fixed")
        v = need("cost", cost, "variable_per_unit")
        r = cost.get("royalty_pct", 0)
        m = need("cost", cost, "min_margin_pct")
        for name, val in (("annual_fixed", f), ("variable_per_unit", v), ("royalty_pct", r), ("min_margin_pct", m)):
            if isinstance(val, (int, float)) and val < 0:
                errs.append(f"cost.{name} cannot be negative")
        if isinstance(r, (int, float)) and isinstance(m, (int, float)) and r + m >= 1:
            errs.append("cost.royalty_pct + cost.min_margin_pct must be below 1")
    value = inp.get("value")
    segs = value.get("segments") if isinstance(value, dict) else None
    if not segs or not isinstance(segs, list):
        errs.append("value.segments needs at least one segment")
    else:
        for i, s in enumerate(segs):
            p = f"value.segments[{i}]"
            for k in ("customers", "penetration", "units_per_customer", "value_per_customer_per_year", "capture_share"):
                need(p, s, k)
            if s.get("source", "estimate") not in SOURCE_QUALITY:
                errs.append(f"{p}.source must be one of {sorted(set(SOURCE_QUALITY))}")
            if isinstance(s.get("penetration"), (int, float)) and not 0 < s["penetration"] <= 1:
                errs.append(f"{p}.penetration must be above 0 and at most 1")
            if isinstance(s.get("capture_share"), (int, float)) and not 0 < s["capture_share"] < 1:
                errs.append(f"{p}.capture_share must be between 0 and 1")
            if isinstance(s.get("units_per_customer"), (int, float)) and s["units_per_customer"] <= 0:
                errs.append(f"{p}.units_per_customer must be above 0")
            if isinstance(s.get("capture_share"), (int, float)) and s["capture_share"] > value.get("max_capture_share", 0.5):
                errs.append(f"{p}.capture_share exceeds value.max_capture_share")
    for i, c in enumerate((inp.get("market") or {}).get("comps", [])):
        for k in ("unit_price", "comparability"):
            need(f"market.comps[{i}]", c, k)
        if isinstance(c.get("comparability"), (int, float)) and not 0 < c["comparability"] <= 1:
            errs.append(f"market.comps[{i}].comparability must be above 0 and at most 1")
    for i, w in enumerate((inp.get("wtp") or {}).get("points", [])):
        need(f"wtp.points[{i}]", w, "max_price_per_unit")
    if rights_bound(inp) and base_right_of(inp) in (inp.get("prohibited_rights") or []):
        errs.append("base_right is in prohibited_rights (Legal confirmed Prohibited): the product cannot be priced for that right")
    for i, r in enumerate(inp.get("rights", [])):
        for k in ("right", "incremental_value_per_unit"):
            if k not in r:
                errs.append(f"rights[{i}] missing {k}")
        if isinstance(r.get("incremental_value_per_unit"), (int, float)) and r["incremental_value_per_unit"] < 0:
            errs.append(f"rights[{i}].incremental_value_per_unit cannot be negative")
    d = (inp.get("discount") or {}).get("expected_list_to_realized", 0.15)
    if not isinstance(d, (int, float)) or not 0 <= d < 0.6:
        errs.append("discount.expected_list_to_realized must be between 0 and 0.6")
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
    max_capture = inp["value"].get("max_capture_share", 0.5)
    disc = (inp.get("discount") or {}).get("expected_list_to_realized", 0.15)
    r = cost.get("royalty_pct", 0.0)
    m = cost["min_margin_pct"]
    cannib = cost.get("cannibalization_per_unit", 0.0)

    cf = 1.0
    if cov.get("current") and cov.get("reference"):
        cf = min(1.5, (cov["current"] / cov["reference"]) ** cov.get("elasticity", 1.0))

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
        raise ValueError("expected units come to zero")
    unit_cost = cost["annual_fixed"] / units + cost["variable_per_unit"] + cannib
    floor = unit_cost / (1 - r - m)

    v_target = sum(s["vbp"] * s["units"] for s in segs) / units
    v_cap = sum(s["vmax"] * s["units"] for s in segs) / units
    quality = sum(SOURCE_QUALITY[s["source"]] * s["units"] for s in segs) / units

    comps = [c for c in (inp.get("market") or {}).get("comps", [])]
    market = None
    if comps:
        w = sum(c["comparability"] for c in comps)
        market = dict(
            ref=sum(c["unit_price"] * c["comparability"] for c in comps) / w,
            low=min(c["unit_price"] for c in comps), high=max(c["unit_price"] for c in comps),
            n=len(comps), avg_comp=w / len(comps),
        )

    pts = [p["max_price_per_unit"] for p in (inp.get("wtp") or {}).get("points", [])]
    wtp = None
    if pts:
        p25, med, p75 = quantiles(pts)
        wtp = dict(n=len(pts), p25=p25, median=med, p75=p75, usable=len(pts) >= 5)

    anchors = {"value": v_target}
    if market:
        anchors["market"] = market["ref"]
    if wtp and wtp["usable"]:
        anchors["wtp"] = wtp["median"]
    weights = dict(DEFAULT_WEIGHTS)
    weights.update(inp.get("weights") or {})
    wsum = sum(weights[k] for k in anchors)
    blended = sum(weights[k] * anchors[k] for k in anchors) / wsum

    out = dict(units=units, coverage_factor=cf, unit_cost=unit_cost, floor=floor, value_target=v_target,
               value_cap=v_cap, anchors=anchors, blended=blended, market=market, wtp=wtp, segments=segs,
               weights_used={k: weights[k] / wsum for k in anchors}, disc=disc)

    flags = []
    if floor > v_cap:
        out["status"] = "NOT_VIABLE"
        out["target"] = out["list"] = None
        flags.append("The cost floor is above the value cap. No price works at this cost, scope, and value. Options: cut cost or "
                     "scope, find a higher-value segment or use right, share cost with another product, or re-check the value estimate.")
    else:
        t = blended
        if t < floor:
            t = floor
            flags.append("Blended anchors are below the cost floor, so the price sits at the floor with no margin of safety.")
        if t > v_cap:
            t = v_cap
            flags.append("Blended anchors are above the value cap, so the price is capped at the cap.")
        out["target"] = t
        out["list"] = t / (1 - disc)
        out["status"] = "VIABLE"
        out["revenue"] = units * t
        out["contribution"] = units * t * (1 - r) - units * (cost["variable_per_unit"] + cannib) - cost["annual_fixed"]

    if len(anchors) > 1:
        ratio = max(anchors.values()) / min(anchors.values())
        out["divergence"] = ratio
        if ratio > 2:
            flags.append(f"The anchors differ by {ratio:.1f}x. Find out why before trusting a number (wrong segment, wrong unit, or a weak comp).")
        elif ratio > 1.5:
            flags.append(f"The anchors differ by {ratio:.1f}x. Check which one is weakest.")
    if len(segs) > 1:
        spread = max(s["vbp"] for s in segs) / min(s["vbp"] for s in segs)
        out["segment_spread"] = spread
        if spread > 1.5:
            flags.append(f"Value-based prices differ {spread:.1f}x across segments. Consider fenced segment prices (by use case or customer type) instead of one list price.")
    if market and market["avg_comp"] < 0.5:
        flags.append("Comparables are weak (average comparability below 0.5). Treat the market anchor as context, not a price.")
    if not market:
        flags.append("No market comparables. Add at least two, or state that none exist.")
    if not wtp:
        flags.append("No willingness-to-pay evidence.")
    elif not wtp["usable"]:
        flags.append(f"Only {wtp['n']} willingness-to-pay points (needs 5 to be used, 15 to be strong).")
    if quality < 0.6:
        flags.append("Customer value rests mainly on internal estimates. Quantify it with customers or a pilot.")

    score = 0
    reasons = []
    n_anch = len(anchors)
    score += {3: 2, 2: 1}.get(n_anch, 0)
    reasons.append(f"{n_anch} of 3 anchors available")
    if quality >= 0.9:
        score += 2
    elif quality >= 0.6:
        score += 1
    reasons.append(f"value evidence quality {quality:.2f} (estimate 0.5, interview 0.75, pilot or contract data 1.0)")
    if wtp and wtp["n"] >= 15:
        score += 2
    elif wtp and wtp["usable"]:
        score += 1
    reasons.append(f"{wtp['n'] if wtp else 0} willingness-to-pay points")
    if market and market["avg_comp"] >= 0.6 and market["n"] >= 2:
        score += 1
    reasons.append(f"{market['n'] if market else 0} comparables" + (f" at {market['avg_comp']:.2f} average comparability" if market else ""))
    if out.get("divergence", 1) > 2:
        score -= 1
    out["confidence"] = "High" if score >= 6 else "Medium" if score >= 3 else "Low"
    out["confidence_reasons"] = reasons
    out["flags"] = flags
    return out


def run_scenarios(inp):
    base = compute(inp)
    scen = []

    def add(label, fn):
        x = copy.deepcopy(inp)
        fn(x)
        try:
            res = compute(x)
        except ValueError:
            return
        scen.append((label, res))

    def capture(f):
        def go(x):
            for s in x["value"]["segments"]:
                s["capture_share"] *= f
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

    add("Value share captured -20%", capture(0.8))
    add("Value share captured +20%", capture(1.2))
    add("Costs +20%", costs(1.2))
    add("Demand -30%", demand(0.7))
    if (inp.get("market") or {}).get("comps"):
        add("Market reference -20%", market(0.8))
    cov = inp.get("coverage") or {}
    if cov.get("resolved") and cov.get("current"):
        def resolved(x):
            x["coverage"]["current"] = x["coverage"]["resolved"]
        add(f"Open rights items resolved (coverage {cov['current']:.0%} to {cov['resolved']:.0%})", resolved)
    return base, scen


def rights_ladder(inp, base):
    out = []
    if base["status"] != "VIABLE":
        return out
    r = inp["cost"].get("royalty_pct", 0.0)
    m = inp["cost"]["min_margin_pct"]
    disc = base["disc"]
    base_right = base_right_of(inp)
    out.append(dict(right=base_right or "(no data rights)", status="Base", basis=right_basis(inp, base_right), price=base["target"],
                    list=base["list"], floor=base["floor"], multiple=1.0, note="Base right priced from the corridor."))
    for x in inp.get("rights", []):
        right = x["right"]
        if right == base_right:
            continue
        basis = right_basis(inp, right)
        if basis == "Blocked":
            out.append(dict(right=right, status="Blocked", basis=basis, note="Legal confirmed this right as Prohibited. Not priced."))
            continue
        cap = x.get("capture_share", 0.3)
        add_cost = x.get("incremental_cost_per_unit", 0.0) / (1 - r - m)
        price = base["target"] + x["incremental_value_per_unit"] * cap + add_cost
        out.append(dict(right=right, status="Priced", basis=basis, price=price, list=price / (1 - disc), floor=base["floor"] + add_cost,
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
    L.append(f"# Price corridor: {inp['product']}" + (f" ({inp['dataset_id']})" if inp.get("dataset_id") else ""))
    bb = right_basis(inp, base_right_of(inp))
    if bb == "Provisional":
        L.append("> RIGHTS PROVISIONAL: Legal has not confirmed the rights this price depends on. Use it for strategy and to focus rights intake. "
                 "Do not quote it until the rights are confirmed.\n")
    L.append(f"Unit: {inp['unit']}. Status: **{base['status']}**. Confidence: **{base['confidence']}**.\n")
    if base["status"] == "VIABLE":
        prov = "Provisional (low confidence): " if base["confidence"] == "Low" else ""
        L.append(f"**{prov}Recommended realized price {money(base['target'], cur)}; list price {money(base['list'], cur)}** "
                 f"(list assumes {base['disc']:.0%} average discount). Deal desk walk-away floor {money(base['floor'], cur)}.\n")
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
        note = f"n={w['n']}" + ("" if w["usable"] else ", too few to use")
        L.append(f"| WTP median | {money(w['median'], cur)} | {note} |")
    L.append(f"| Blended | {money(base['blended'], cur)} | weights " + ", ".join(f"{k} {v:.0%}" for k, v in base["weights_used"].items()) + " |")
    L.append("\n## Segments")
    L.append("| Segment | Units/yr | Value per unit | Value-based price | Cap | Evidence |\n|---|---|---|---|---|---|")
    for s in base["segments"]:
        L.append(f"| {s['name']} | {s['units']:,.0f} | {money(s['value_per_unit'], cur)} | {money(s['vbp'], cur)} | {money(s['vmax'], cur)} | {s['source']} |")
    if ladder:
        L.append("\n## Use-right ladder")
        L.append("| Right | Rights basis | Status | Realized | List | Multiple | Basis |\n|---|---|---|---|---|---|---|")
        for x in ladder:
            if x["status"] == "Blocked":
                L.append(f"| {x['right']} | Blocked | Blocked | - | - | - | {x['note']} |")
            else:
                L.append(f"| {x['right']} | {x.get('basis', 'N/A')} | {x['status']} | {money(x['price'], cur)} | {money(x['list'], cur)} | {x['multiple']:.2f}x | {x['note']} |")
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
            L.append(f"| {label} | {res['status']} | - | | {money(res['floor'], cur)} | - | - |")
    cov = inp.get("coverage") or {}
    if cov.get("resolved") and base["status"] == "VIABLE":
        for label, res in scen:
            if label.startswith("Open rights"):
                if res["status"] == "VIABLE":
                    gain = (res["target"] - base["target"]) * base["units"]
                    L.append(f"\nResolving the open rights items lifts annual revenue by about {money(gain, cur)} through price alone, before any extra volume from wider coverage.")
    L.append("\n## Confidence")
    L.append(", ".join(base["confidence_reasons"]) + ".")
    if base["flags"]:
        L.append("\n## Flags")
        L += [f"- {f}" for f in base["flags"]]
    L.append("\n## Next evidence to collect")
    nxt = []
    if base["market"] is None or base["market"]["n"] < 2:
        nxt.append("Two or more comparable products with source links.")
    if not base["wtp"] or not base["wtp"]["usable"]:
        nxt.append("Willingness-to-pay data: run the `wtp-study-design` skill, or interview five or more buyers.")
    if any(s["source"] == "estimate" for s in base["segments"]):
        nxt.append("Customer-validated value for estimated segments: interviews or a priced pilot.")
    nxt.append("Pilot with three to five design partners at the recommended price, and record accept, counter, and decline.")
    L += [f"- {n}" for n in nxt]
    return "\n".join(L) + "\n"


def lines_csv(inp, base, ladder, path):
    if base["status"] != "VIABLE":
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LINE_COLUMNS)
        w.writeheader()
        for x in ladder:
            if x["status"] == "Blocked":
                continue
            ds = inp.get("dataset_id", "")
            ur = x["right"] if ds else ""
            pid = inp.get("product_id") or ds or re.sub(r"[^A-Z0-9]+", "-", inp["product"].upper()).strip("-")
            basis = x.get("basis", "N/A")
            w.writerow(dict(
                line_id=f"PL-{pid}-{ur or 'base'}", product_id=pid, product_type=inp.get("product_type") or ("data_license" if ds else "other"),
                dataset_id=ds, use_right=ur, delivery="", unit=inp["unit"], tier_min=1, tier_max="",
                list_price=round(x["list"], 2), floor_price=round(x["floor"], 2), currency=inp["currency"], term_months=12,
                tier_model="all_units", status="Draft", version="0.1",
                rights_relevance="Required" if ds else "None",
                notes="rights provisional: not cleared to quote" if basis == "Provisional" else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--md")
    ap.add_argument("--json")
    ap.add_argument("--csv")
    a = ap.parse_args()
    with open(a.inp, encoding="utf-8") as fh:
        inp = json.load(fh)
    errs = validate(inp)
    if errs:
        print("Input errors:", file=sys.stderr)
        for e in errs:
            print(" -", e, file=sys.stderr)
        return 2
    base, scen = run_scenarios(inp)
    ladder = rights_ladder(inp, base)
    md = render(inp, base, scen, ladder)
    print(md)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(md)
    if a.json:
        slim = {k: v for k, v in base.items()}
        json.dump(dict(result=slim, ladder=ladder, scenarios=[dict(label=l, status=r["status"], target=r["target"]) for l, r in scen]),
                  open(a.json, "w", encoding="utf-8"), indent=2, default=float)
    if a.csv:
        lines_csv(inp, base, ladder, a.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
