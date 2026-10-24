#!/usr/bin/env python3
"""Screen API keys for usage patterns worth a question to the account owner.

The screen looks at three signals, not one: look-to-book against the segment median, the share of
searches that are distinct (a sweep rarely repeats a query), and how long responses are kept. A heavy
user in a high-look-to-book segment is not by that fact collecting data, so the output is a list of
signals and a question, never a finding.

Usage:
  python harvest_screen.py --in keys.csv --segment-median NAME=N [--segment-median NAME=N ...]
         [--default-median N] [--multiple X] [--distinct-ratio X] [--retention-days N] [--min-volume N]
         [--md out.md]

keys.csv columns (header row required):
  key_id, customer, searches, bookings        required on every row
  segment                                     the segment name used in --segment-median (needed when you give more than one median)
  distinct_queries                            optional: distinct origin, destination and date combinations among the searches
  retention_days                              optional: how long responses are kept, if known
  kept_share                                  optional: share of responses stored, 0 to 1

Company values (none has a default; each comes from pricing-governance.md review parameters or the API policy):
  --segment-median NAME=N   median look-to-book (searches per booking) for that segment. Required for every segment present.
  --default-median N        used for rows with no segment column. Same source.
  --multiple X              flag a key whose look-to-book is at least X times its segment median.
  --distinct-ratio X        flag a key whose distinct-query share is at least X (0 to 1).
  --retention-days N        flag a key whose responses are kept at least N days.
  --min-volume N            keys and customers with fewer searches than N are listed and not judged.
A signal whose value is not given is not run, and the report says "Unknown".

Rows with blank, negative or impossible counts stop the run (exit 2); they are never skipped quietly.
Keys are rolled up by customer, because splitting traffic across keys hides a pattern.
Exit codes: 0 = screen produced, 2 = invalid input.
"""
import argparse
import csv
import math
import sys


def num(s):
    s = (s or "").replace(",", "").strip()
    if s == "":
        return None
    v = float(s)
    if not math.isfinite(v):
        raise ValueError("not a finite number")
    return v


def read_rows(path, errors):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        need = {"key_id", "customer", "searches", "bookings"}
        if not rd.fieldnames or not need <= {(c or "").strip() for c in rd.fieldnames}:
            errors.append("the CSV needs the columns key_id, customer, searches, bookings")
            return rows
        for i, r in enumerate(rd, 2):
            r = {(k or "").strip(): v for k, v in r.items()}
            where = f"line {i} ({(r.get('key_id') or '').strip() or 'no key_id'})"
            try:
                s, b = num(r.get("searches")), num(r.get("bookings"))
                dq, ks = num(r.get("distinct_queries")), num(r.get("kept_share"))
                rd_days = num(r.get("retention_days"))
            except ValueError as e:
                errors.append(f"{where}: a count is not a number ({e})")
                continue
            if s is None or b is None:
                errors.append(f"{where}: searches and bookings are both required (a blank is not zero)")
                continue
            if s < 0 or b < 0 or (dq is not None and dq < 0):
                errors.append(f"{where}: counts cannot be negative")
                continue
            if b > s:
                errors.append(f"{where}: bookings ({b:g}) exceed searches ({s:g}); check the counts")
                continue
            if dq is not None and dq > s:
                errors.append(f"{where}: distinct_queries ({dq:g}) exceed searches ({s:g})")
                continue
            if ks is not None and not 0 <= ks <= 1:
                errors.append(f"{where}: kept_share must be from 0 to 1")
                continue
            if not (r.get("key_id") or "").strip() or not (r.get("customer") or "").strip():
                errors.append(f"{where}: key_id and customer are required")
                continue
            rows.append({"key": r["key_id"].strip(), "customer": r["customer"].strip(), "segment": (r.get("segment") or "").strip(),
                         "searches": s, "bookings": b, "distinct": dq, "retention_days": rd_days, "kept_share": ks})
    return rows


def judge(searches, bookings, distinct, retention_days, median, a):
    """Return (l2b, vs_median, distinct_ratio, signals, status)."""
    l2b = (searches / bookings) if bookings > 0 else None
    vs = (l2b / median) if (l2b is not None and median) else None
    dr = (distinct / searches) if (distinct is not None and searches) else None
    if a.min_volume is not None and searches < a.min_volume:
        return l2b, vs, dr, [], "below minimum volume: not judged"
    sig = []
    if a.multiple is not None:
        if l2b is None and searches > 0:
            sig.append("searches with no bookings")
        elif vs is not None and vs >= a.multiple:
            sig.append(f"look-to-book {vs:.1f}x the segment median")
    if a.distinct_ratio is not None and dr is not None and dr >= a.distinct_ratio:
        sig.append(f"distinct-query share {dr:.2f}")
    if a.retention_days is not None and retention_days is not None and retention_days >= a.retention_days:
        sig.append(f"responses kept {retention_days:g} days")
    if sig:
        return l2b, vs, dr, sig, "pattern to confirm with the account owner (" + "; ".join(sig) + ")"
    if a.multiple is None and a.distinct_ratio is None and a.retention_days is None:
        return l2b, vs, dr, [], "no threshold given: ratios shown, nothing judged"
    return l2b, vs, dr, [], "no signal tripped"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--segment-median", action="append", default=[], metavar="NAME=N")
    ap.add_argument("--default-median", type=float)
    ap.add_argument("--multiple", type=float)
    ap.add_argument("--distinct-ratio", type=float)
    ap.add_argument("--retention-days", type=float)
    ap.add_argument("--min-volume", type=float)
    ap.add_argument("--md")
    a = ap.parse_args()

    errors = []
    medians = {}
    for item in a.segment_median:
        name, _, val = item.partition("=")
        try:
            v = float(val)
        except ValueError:
            errors.append(f"--segment-median {item!r}: use NAME=number")
            continue
        if not math.isfinite(v) or v <= 0:
            errors.append(f"--segment-median {item!r}: the median must be above zero")
            continue
        medians[name.strip()] = v
    if a.default_median is not None and (not math.isfinite(a.default_median) or a.default_median <= 0):
        errors.append("--default-median must be above zero")
    for flag, v in (("--multiple", a.multiple), ("--distinct-ratio", a.distinct_ratio), ("--retention-days", a.retention_days), ("--min-volume", a.min_volume)):
        if v is not None and (not math.isfinite(v) or v <= 0):
            errors.append(f"{flag} must be above zero")
    if a.distinct_ratio is not None and a.distinct_ratio > 1:
        errors.append("--distinct-ratio is a share from 0 to 1")
    if not medians and a.default_median is None:
        errors.append("give the segment median look-to-book: --segment-median NAME=N or --default-median N (a company value; no default)")
    try:
        rows = read_rows(a.inp, errors)
    except OSError as e:
        errors.append(f"cannot read {a.inp}: {e}")
        rows = []
    for r in rows:
        r["median"] = medians.get(r["segment"]) if r["segment"] else a.default_median
        if r["median"] is None:
            errors.append(f"key {r['key']}: no median for segment {r['segment'] or '(none)'}; give --segment-median or --default-median")
    if not rows and not errors:
        errors.append("the CSV has no data rows")
    if errors:
        print("Input errors:", file=sys.stderr)
        for e in errors:
            print(" -", e, file=sys.stderr)
        return 2

    def show(v, fmt):
        return "n/a" if v is None else format(v, fmt)

    out = ["Company values used (none has a default):",
           "- segment medians: " + (", ".join(f"{k} {v:g}" for k, v in sorted(medians.items())) or "-")
           + (f"; default {a.default_median:g}" if a.default_median is not None else ""),
           f"- look-to-book multiple: {'%gx' % a.multiple if a.multiple is not None else 'Unknown (not run)'}",
           f"- distinct-query share: {'%g' % a.distinct_ratio if a.distinct_ratio is not None else 'Unknown (not run)'}",
           f"- retention days: {'%g' % a.retention_days if a.retention_days is not None else 'Unknown (not run)'}",
           f"- minimum volume: {'%g searches' % a.min_volume if a.min_volume is not None else 'Unknown (every key judged)'}",
           "", "## By customer (all keys rolled up)",
           "| Customer | Keys | Searches | Bookings | Look-to-book | x median | Distinct-query share | Screen |", "|---|---|---|---|---|---|---|---|"]
    by_cust = {}
    for r in rows:
        by_cust.setdefault(r["customer"], []).append(r)
    cust_rows = []
    for cust, rs in by_cust.items():
        s, b = sum(x["searches"] for x in rs), sum(x["bookings"] for x in rs)
        all_d = all(x["distinct"] is not None for x in rs)
        d = sum(x["distinct"] for x in rs) if all_d else None
        rets = [x["retention_days"] for x in rs if x["retention_days"] is not None]
        med = max(x["median"] for x in rs)  # the most generous median when a customer spans segments
        l2b, vs, dr, sig, status = judge(s, b, d, max(rets) if rets else None, med, a)
        cust_rows.append((vs if vs is not None else float("inf"), cust, len(rs), s, b, l2b, vs, dr, status))
    for _, cust, n, s, b, l2b, vs, dr, status in sorted(cust_rows, key=lambda x: -x[0]):
        out.append(f"| {cust} | {n} | {s:,.0f} | {b:,.0f} | {show(l2b, ',.1f')} | {show(vs, ',.1f')} | {show(dr, '.2f')} | {status} |")
    out += ["", "## By key",
            "| Key | Customer | Segment | Searches | Bookings | Look-to-book | x median | Distinct-query share | Retention days | Screen |", "|---|---|---|---|---|---|---|---|---|---|"]
    key_rows = []
    for r in rows:
        l2b, vs, dr, sig, status = judge(r["searches"], r["bookings"], r["distinct"], r["retention_days"], r["median"], a)
        key_rows.append((vs if vs is not None else float("inf"), r, l2b, vs, dr, status))
    for _, r, l2b, vs, dr, status in sorted(key_rows, key=lambda x: -x[0]):
        out.append("| {k} | {c} | {sg} | {s:,.0f} | {b:,.0f} | {l} | {m} | {d} | {rt} | {sc} |".format(
            k=r["key"], c=r["customer"], sg=r["segment"] or "-", s=r["searches"], b=r["bookings"], l=show(l2b, ",.1f"), m=show(vs, ",.1f"),
            d=show(dr, ".2f"), rt="" if r["retention_days"] is None else f"{r['retention_days']:g}", sc=status))
    out += ["", "Ratios come from the input counts (F). A customer's distinct-query share adds distinct counts across its keys, so it can overstate when keys repeat the same queries.",
            "A flag is a question for the account owner, not a finding against the customer. Next: `references/harvest-handling.md`."]
    text = "\n".join(out) + "\n"
    sys.stdout.write(text)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
