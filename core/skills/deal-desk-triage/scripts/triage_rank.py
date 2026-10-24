#!/usr/bin/env python3
"""Rank open deal desk requests and name the skill that handles each.

Usage:
  python triage_rank.py --in requests.csv --today YYYY-MM-DD [--band-pct N] [--md out.md] [--csv out.csv]

requests.csv columns (header row required):
  request_id, account, product, request_type, tcv, requested_discount_pct, received, due
  request_type: non_standard_quote, api_data_request, data_licence, renewal, standard
  received and due are YYYY-MM-DD. tcv is total contract value in one currency. due may be blank.

--band-pct is the discount band the deal desk may approve alone, from pricing-governance.md. Leave it out when the
band is Unknown: the band column then says Unknown. No default is assumed.

Order: overdue first (most overdue first), then due soonest, then larger tcv. Blank due dates sort after dated ones.
"""
import argparse
import csv
import datetime as dt
import sys

ROUTE = {
    "non_standard_quote": "deal-desk-review",
    "api_data_request": "api-access-request",
    "data_licence": "data-license-pricing",
    "renewal": "deal-desk-review with account-price-fit",
    "standard": "quote from the price book; no review needed",
}


def d(s):
    s = (s or "").strip()
    return dt.date.fromisoformat(s) if s else None


def num(s):
    s = (s or "").replace(",", "").replace("$", "").strip()
    return float(s) if s else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--today", required=True)
    ap.add_argument("--band-pct", type=float)
    ap.add_argument("--md")
    ap.add_argument("--csv")
    a = ap.parse_args()
    today = d(a.today)
    rows, problems = [], []
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        for i, r in enumerate(csv.DictReader(fh), start=2):
            rid = (r.get("request_id") or "").strip() or f"row{i}"
            try:
                rec, due = d(r.get("received")), d(r.get("due"))
                tcv, disc = num(r.get("tcv")), num(r.get("requested_discount_pct"))
            except ValueError as e:
                problems.append(f"{rid}: {e}")
                continue
            rtype = (r.get("request_type") or "").strip()
            if rtype not in ROUTE:
                problems.append(f"{rid}: request_type {rtype!r} is not one of {', '.join(ROUTE)}")
                rtype = "non_standard_quote"
            band = "Unknown" if a.band_pct is None or disc is None else ("within band" if disc <= a.band_pct else "exceeds band")
            rows.append({"request_id": rid, "account": r.get("account", "").strip(), "product": r.get("product", "").strip(),
                         "type": rtype, "tcv": tcv, "disc": disc, "days_open": (today - rec).days if rec else None,
                         "days_to_due": (due - today).days if due else None, "band": band, "skill": ROUTE[rtype]})
    rows.sort(key=lambda x: (x["days_to_due"] is None, x["days_to_due"] if x["days_to_due"] is not None else 0, -(x["tcv"] or 0)))
    out = [f"Triage as of {today}: {len(rows)} open request(s)." + (f" Band: {a.band_pct:g}% (from the approval matrix)." if a.band_pct is not None else " Band: Unknown."), "",
           "| # | Request | Account | Product | Type | TCV | Discount asked | Days open | Days to due | Band | Skill |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in enumerate(rows, 1):
        dd = r["days_to_due"]
        due = "no due date" if dd is None else (f"OVERDUE {-dd}" if dd < 0 else str(dd))
        out.append(f"| {n} | {r['request_id']} | {r['account']} | {r['product']} | {r['type']} | {'' if r['tcv'] is None else format(r['tcv'], ',.0f')} | "
                   f"{'' if r['disc'] is None else format(r['disc'], 'g') + '%'} | {'' if r['days_open'] is None else r['days_open']} | {due} | {r['band']} | {r['skill']} |")
    if problems:
        out += ["", "Input problems:"] + [f"- {p}" for p in problems]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["request_id"])
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
