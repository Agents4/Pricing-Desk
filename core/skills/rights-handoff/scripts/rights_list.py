#!/usr/bin/env python3
"""Build the rights hand-off list for the product manager, and read the answers back.

Usage:
  python rights_list.py --pricebook price_book.csv [--answers rights_answers.csv] [--out handoff.csv] [--md out.md]

For every data and API product it lists each right the price book grants (product_id x conferred_right), with the
price lines, annual revenue and customers if the price book has them. If --answers is given, the answer on file is
shown beside each row, unchanged. A row with no answer is Open.

rights_answers.csv columns: product_id, conferred_right, answer, date, who
(the answer wording is the product manager's; this script reads it and does not interpret it).

The pricing desk does not assess whether we hold a right. This list is a question, not a finding.
"""
import argparse
import csv
import sys
from collections import OrderedDict

SCOPE = {"data_license", "api_access"}
OTHER_TYPES = {"software", "service", "other"}
ALIASES = {"data": "data_license", "datalicense": "data_license", "data_licence": "data_license", "datalicence": "data_license",
           "api": "api_access", "apiaccess": "api_access"}


def norm_type(s):
    k = (s or "").strip().lower().replace("-", "_").replace(" ", "_")
    return ALIASES.get(k, ALIASES.get(k.replace("_", ""), k))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pricebook", required=True)
    ap.add_argument("--answers")
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args()
    items = OrderedDict()
    missing_right, unknown_type, n_lines, n_other = [], [], 0, 0
    with open(a.pricebook, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            n_lines += 1
            ptype = norm_type(r.get("product_type"))
            if ptype in OTHER_TYPES:
                n_other += 1
                continue
            if ptype not in SCOPE:
                unknown_type.append(r.get("line_id", "") or r.get("product_id", ""))
                continue
            pid = (r.get("product_id") or "").strip()
            cr = (r.get("conferred_right") or r.get("use_right") or "").strip()
            if not cr:
                missing_right.append(r.get("line_id", pid))
                continue
            it = items.setdefault((pid, cr), {"name": r.get("product_name", ""), "lines": 0, "rev": 0.0, "cust": 0})
            it["lines"] += 1
            for k, f in (("rev", "annual_revenue"), ("cust", "customers")):
                try:
                    it[k] += float((r.get(f) or "").replace(",", "") or 0)
                except ValueError:
                    pass
    answers = {}
    if a.answers:
        with open(a.answers, newline="", encoding="utf-8-sig") as fh:
            for r in csv.DictReader(fh):
                answers[((r.get("product_id") or "").strip(), (r.get("conferred_right") or "").strip())] = r
    ranked = sorted(items.items(), key=lambda kv: (-kv[1]["rev"], kv[0]))
    rows = []
    for i, ((pid, cr), it) in enumerate(ranked, 1):
        an = answers.get((pid, cr))
        rows.append([i, pid, it["name"], cr, it["lines"], round(it["rev"], 2) if it["rev"] else "", int(it["cust"]) if it["cust"] else "",
                     (an.get("answer", "") if an else "") or "Open", (an.get("date", "") if an else ""), (an.get("who", "") if an else "")])
    head = ["priority_rank", "product_id", "product_name", "conferred_right", "price_lines", "annual_revenue", "customers", "answer", "answer_date", "answered_by"]
    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(head)
            w.writerows(rows)
    open_n = sum(1 for r in rows if r[7] == "Open")
    out = ["Rights hand-off: %d product and right pair(s); %d open, %d with an answer on file." % (len(rows), open_n, len(rows) - open_n), "",
           "| # | Product | Name | Right granted | Lines | Annual revenue | Customers | Answer | Date | By |", "|---|---|---|---|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    out += ["", "Lines read: %d. Data or API: %d. Software, service or other (not listed): %d. Product type missing or not recognised: %d." % (
        n_lines, n_lines - n_other - len(unknown_type), n_other, len(unknown_type))]
    if unknown_type:
        out += ["", "Lines whose product_type is blank or not recognised cannot be classed as data, API or other, so they are NOT in the list above. Fix the type and rerun: " + ", ".join(str(x) for x in unknown_type)]
    if missing_right:
        out += ["", "Data or API lines with no conferred_right (cannot be listed until the granted right is stated): " + ", ".join(missing_right)]
    out += ["", "Answers are shown as the product manager wrote them. The pricing desk does not assess rights held."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    main()
