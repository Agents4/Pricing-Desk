#!/usr/bin/env python3
"""Rank open deal desk requests and name the skill that handles each.

Usage:
  python triage_rank.py --in requests.csv --today YYYY-MM-DD [--band-pct N] [--md out.md] [--csv out.csv]

requests.csv columns (header row required):
  request_id, account, product, request_type, tcv, requested_discount_pct, received, due   required
  anchor_deal                                                                                optional: yes if the account has an anchor deal
  request_type: non_standard_quote, api_data_request, data_licence, renewal, standard
  received and due are YYYY-MM-DD. tcv is total contract value in one currency. due may be blank.
  requested_discount_pct may be written 15 or 15%. Write 0 for no discount: a blank is Unknown, not zero.

--band-pct is the discount band the deal desk may approve alone, from pricing-governance.md. Leave it out when the
band is Unknown: then EVERY request that asks for a discount goes to review (fail closed). No default is assumed.

Routing rules (these override the request_type the requester typed, so a label cannot skip review):
  - a request asking for a discount that exceeds the band, or any discount when the band is Unknown, goes to deal-desk-review,
    whatever its request_type says (api_data_request keeps its own route and is also marked for review);
  - an account with an anchor deal goes to account-price-fit first (any type but standard with no discount).

Order: overdue first (most overdue first), then due soonest, then larger tcv. Blank due dates sort after dated ones.
Rows that cannot be read are listed at the top, not dropped. Accounts with more than one open request are grouped.
Exit codes: 0 = ranked, 2 = unusable input (missing columns, bad --today).
"""
import argparse
import csv
import datetime as dt
import re
import sys

ROUTE = {
    "non_standard_quote": "deal-desk-review",
    "api_data_request": "api-access-request",
    "data_licence": "data-license-pricing",
    "renewal": "deal-desk-review",
    "standard": "quote from the price book; no review needed",
}
REQUIRED = ["request_id", "account", "product", "request_type", "tcv", "requested_discount_pct", "received", "due"]


def d(s):
    s = (s or "").strip()
    return dt.date.fromisoformat(s) if s else None


def num(s):
    s = (s or "").replace("$", "").replace("%", "").strip()
    if re.search(r",\d{1,2}$", s):
        raise ValueError("a comma before one or two digits looks like a decimal comma; write it with a point")
    s = s.replace(",", "")
    if not s:
        return None
    v = float(s)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError("not a finite number")
    return v


def cell(r, k):
    v = r.get(k)
    return v.strip() if isinstance(v, str) else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--today", required=True)
    ap.add_argument("--band-pct", type=float)
    ap.add_argument("--md")
    ap.add_argument("--csv")
    a = ap.parse_args()
    try:
        today = dt.date.fromisoformat(a.today)
    except ValueError:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if a.band_pct is not None and not 0 <= a.band_pct <= 100:
        print("--band-pct must be from 0 to 100", file=sys.stderr)
        return 2
    rows, problems = [], []
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        cols = [(c or "").strip() for c in (rd.fieldnames or [])]
        missing = [c for c in REQUIRED if c not in cols]
        if missing:
            print("The CSV is missing columns: " + ", ".join(missing), file=sys.stderr)
            return 2
        for i, r in enumerate(rd, start=2):
            r = {(k or "").strip(): v for k, v in r.items()}
            rid = cell(r, "request_id") or f"row{i}"
            if any(v is None for k, v in r.items() if k in REQUIRED):
                problems.append(f"line {i} ({rid}): the row is short (a field is missing); not ranked")
                continue
            try:
                rec, due = d(r.get("received")), d(r.get("due"))
                tcv, disc = num(r.get("tcv")), num(r.get("requested_discount_pct"))
            except ValueError as e:
                problems.append(f"line {i} ({rid}): {e}; not ranked")
                continue
            if disc is not None and 0 < disc < 1 and "%" not in (r.get("requested_discount_pct") or ""):
                problems.append(f"line {i} ({rid}): requested_discount_pct {disc:g} looks like a fraction; write 25 or 25% for twenty-five percent; not ranked")
                continue
            if disc is not None and (disc < 0 or disc > 100):
                problems.append(f"line {i} ({rid}): requested_discount_pct {disc:g} is outside 0 to 100; not ranked")
                continue
            if tcv is not None and tcv < 0:
                problems.append(f"line {i} ({rid}): tcv is negative; not ranked")
                continue
            if rec and due and due < rec:
                problems.append(f"line {i} ({rid}): due is before received; ranked on the due date as written")
            if rec and rec > today:
                problems.append(f"line {i} ({rid}): received is after --today; ranked as written")
            rtype = cell(r, "request_type").lower().replace(" ", "_").replace("-", "_")
            rtype = {"data_license": "data_licence"}.get(rtype, rtype)
            if rtype not in ROUTE:
                problems.append(f"line {i} ({rid}): request_type {rtype!r} is not one of {', '.join(ROUTE)}; routed to deal-desk-review")
                rtype = "non_standard_quote"
            araw = cell(r, "anchor_deal").lower()
            if araw not in ("", "yes", "y", "true", "1", "no", "n", "false", "0"):
                problems.append(f"line {i} ({rid}): anchor_deal {cell(r, 'anchor_deal')!r} is not yes or no; treated as yes so account-price-fit looks at it")
                araw = "yes"
            anchor = araw in ("yes", "y", "true", "1")
            asks = disc is not None and disc > 0
            if disc is None:
                band = "Unknown: discount not stated"
            elif a.band_pct is None:
                band = "Unknown: escalate" if asks else "n/a (no discount asked)"
            elif not asks:
                band = "n/a (no discount asked)"
            else:
                band = "within band" if disc <= a.band_pct else "exceeds band"
            skill = ROUTE[rtype]
            note = ""
            if disc is None:
                note = "discount not stated: ask the requester (0 if none) before this is quoted or approved"
                if rtype == "standard":
                    skill = "ask the requester to state the discount (0 if none); not quoted"
                problems.append(f"line {i} ({rid}): requested_discount_pct is blank; treated as Unknown, not zero")
            elif asks and band != "within band" and rtype == "data_licence":
                skill = "data-license-pricing (price the right), then deal-desk-review for the discount"
                note = f"data licence with a discount {'over the band' if a.band_pct is not None else 'and no band on file'}"
            elif asks and band != "within band" and rtype in ("standard", "data_licence", "renewal"):
                skill = "deal-desk-review"
                note = f"{rtype} with a discount {'over the band' if a.band_pct is not None else 'and no band on file'}: reviewed, not quoted"
            elif asks and band == "within band" and rtype == "standard":
                skill = "deal desk within band: a give tied to a get, logged"
            elif asks and band != "within band" and rtype == "api_data_request":
                note = "also needs deal-desk-review for the discount"
            if anchor and not (rtype == "standard" and not asks):
                skill = "account-price-fit, then " + skill
            rows.append({"request_id": rid, "account": cell(r, "account"), "product": cell(r, "product"),
                         "type": rtype, "tcv": tcv, "disc": disc, "days_open": (today - rec).days if rec else None,
                         "days_to_due": (due - today).days if due else None, "band": band, "skill": skill, "note": note,
                         "anchor": anchor})
    rows.sort(key=lambda x: (x["days_to_due"] is None, x["days_to_due"] if x["days_to_due"] is not None else 0, -(x["tcv"] or 0)))
    out = [f"Triage as of {today}: {len(rows)} request(s) ranked, {sum(1 for p in problems if 'not ranked' in p)} not ranked."
           + (f" Band: {a.band_pct:g}% (from the approval matrix)." if a.band_pct is not None else " **NO BAND ON FILE: every request that asks for a discount goes to review.**"), ""]
    if any("not ranked" in p for p in problems):
        out += ["**Rows not ranked (fix and rerun):**"] + [f"- {p}" for p in problems if "not ranked" in p] + [""]
    out += ["| # | Request | Account | Product | Type | TCV | Discount asked | Days open | Days to due | Band | Skill |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in enumerate(rows, 1):
        dd = r["days_to_due"]
        due = "no due date" if dd is None else (f"OVERDUE {-dd}" if dd < 0 else str(dd))
        skill = r["skill"] + (f" ({r['note']})" if r["note"] else "")
        out.append(f"| {n} | {r['request_id']} | {r['account']} | {r['product']} | {r['type']} | {'' if r['tcv'] is None else format(r['tcv'], ',.0f')} | "
                   f"{'' if r['disc'] is None else format(r['disc'], 'g') + '%'} | {'' if r['days_open'] is None else r['days_open']} | {due} | {r['band']} | {skill} |")
    groups = {}
    for r in rows:
        groups.setdefault(r["account"].lower(), []).append(r)
    multi = {k: v for k, v in groups.items() if k and len(v) > 1}
    if multi:
        out += ["", "**Same account, more than one open request (review together; concessions on one are precedent for the others):**"]
        for v in multi.values():
            out.append(f"- {v[0]['account']}: " + ", ".join(f"{x['request_id']} ({x['product']}, due {'none' if x['days_to_due'] is None else x['days_to_due']})" for x in v))
    other = [p for p in problems if "not ranked" not in p]
    if other:
        out += ["", "Notes on input:"] + [f"- {p}" for p in other]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["request_id"])
            w.writeheader()
            w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
