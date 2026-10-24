"""Notice calendar for a price change: who must be told by when.

Usage:
  python notice_calendar.py --in contracts.csv --effective YYYY-MM-DD --today YYYY-MM-DD [--md out.md]

contracts.csv columns (header row required):
  contract_id, account, notice_days, price_protected_until
  notice_days: days of written notice the contract requires before a price change takes effect. Write 30 or "30 days".
               Blank, a range or other text = Unknown (listed, not guessed). Negative is an error.
  price_protected_until: YYYY-MM-DD, the LAST day of price protection (inclusive); blank if none. A change cannot apply
               on or before this date.

send_by = effective date minus notice_days. The notice days are contract values; none is assumed.
Contract terms are read as supplied; the approver for contract questions in pricing-governance.md confirms them (Unknown if blank).
Rows that cannot be read are listed at the top and the exit code is 1; nothing is dropped quietly.
Exit codes: 0 = calendar, 1 = calendar with unreadable rows, 2 = unusable input.
"""
import argparse
import csv
import datetime as dt
import re
import sys


def cell(r, k):
    v = r.get(k)
    return v.strip() if isinstance(v, str) else ""


def parse_days(s):
    """Return (days, note). days is None when Unknown. Raises ValueError for a negative value."""
    s = s.strip()
    if not s:
        return None, "blank"
    m = re.fullmatch(r"(\d+)(?:\s*-?\s*(?:calendar\s+)?days?)?", s, re.I)
    if m:
        return int(m.group(1)), ""
    if re.fullmatch(r"-\d+.*", s):
        raise ValueError("notice_days %r is negative" % s)
    return None, "could not read %r as a number of days" % s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--effective", required=True)
    ap.add_argument("--today", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    try:
        eff, today = dt.date.fromisoformat(a.effective), dt.date.fromisoformat(a.today)
    except ValueError:
        print("--effective and --today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    rows, problems, seen = [], [], set()
    with open(a.inp, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        cols = [(c or "").strip() for c in (rd.fieldnames or [])]
        miss = [c for c in ("contract_id", "notice_days", "price_protected_until") if c not in cols]
        if miss:
            print("The CSV is missing columns: " + ", ".join(miss), file=sys.stderr)
            return 2
        for i, r in enumerate(rd, 2):
            r = {(k or "").strip(): v for k, v in r.items()}
            cid = cell(r, "contract_id") or "line%d" % i
            if cid in seen:
                problems.append("line %d: contract_id %s repeats; not listed twice" % (i, cid))
                continue
            seen.add(cid)
            try:
                days, why = parse_days(cell(r, "notice_days"))
            except ValueError as e:
                problems.append("line %d (%s): %s" % (i, cid, e))
                continue
            try:
                p = cell(r, "price_protected_until")
                prot = dt.date.fromisoformat(p) if p else None
            except ValueError:
                problems.append("line %d (%s): price_protected_until %r is not YYYY-MM-DD" % (i, cid, cell(r, "price_protected_until")))
                continue
            send_by = (eff - dt.timedelta(days=days)) if days is not None else None
            if prot and prot >= eff:
                st = "protected through %s (inclusive): the change cannot apply on the effective date; earliest %s" % (prot, prot + dt.timedelta(days=1))
            elif send_by is None:
                st = "notice period Unknown (%s): take it to the contract-questions approver in pricing-governance.md" % why
            elif send_by < today:
                st = "send-by date %s passed %d day(s) ago: effective date cannot be met" % (send_by, (today - send_by).days)
            else:
                st = "send by %s (%d day(s) from today)" % (send_by, (send_by - today).days)
            rows.append(((send_by or dt.date.max), cid, cell(r, "account"), str(days) if days is not None else "Unknown", st))
    rows.sort()
    out = ["Notice calendar for effective date %s, as of %s." % (eff, today), ""]
    if eff < today:
        out += ["**The effective date is in the past.**", ""]
    if problems:
        out += ["**Rows not listed (fix and rerun):**"] + ["- " + p for p in problems] + [""]
    out += ["| Contract | Account | Notice days | Status |", "|---|---|---|---|"]
    out += ["| %s | %s | %s | %s |" % (c, ac, nd, st) for _, c, ac, nd, st in rows]
    out += ["", "Dates are computed from the supplied contract terms (F if the terms were read from the contract, A if relayed). The contract-questions approver in pricing-governance.md confirms (Unknown if blank)."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
