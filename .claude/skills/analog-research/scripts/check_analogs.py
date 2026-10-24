#!/usr/bin/env python3
"""Check analog library entries for the fields rule 11 requires.

Usage:
  python check_analogs.py --dir workspace/context-library/analogs [--today YYYY-MM-DD] [--max-age-days N]

Each analog file (not README.md) needs frontmatter with: source_url (http or https), access_date (YYYY-MM-DD),
unit, metric, right_or_use, comparability. With --max-age-days it also lists entries whose access_date is older
than N days from --today. N is a company or user value; no default is assumed.
Exit code 1 when any entry is incomplete.
"""
import argparse
import datetime as dt
import os
import re
import sys

REQ = ["source_url", "access_date", "unit", "metric", "right_or_use", "comparability"]


def front(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip().strip('"')
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--today")
    ap.add_argument("--max-age-days", type=int)
    a = ap.parse_args()
    bad, stale, n = 0, [], 0
    for f in sorted(os.listdir(a.dir)):
        if not f.endswith(".md") or f.lower() == "readme.md":
            continue
        n += 1
        fm = front(os.path.join(a.dir, f))
        miss = [k for k in REQ if not fm.get(k)]
        if fm.get("source_url") and not re.match(r"^https?://", fm["source_url"]):
            miss.append("source_url is not a web address")
        if fm.get("access_date") and not re.match(r"^\d{4}-\d{2}-\d{2}$", fm["access_date"]):
            miss.append("access_date is not YYYY-MM-DD")
        if miss:
            bad += 1
            print("INCOMPLETE %s: %s" % (f, "; ".join(miss)))
        elif a.max_age_days is not None and a.today:
            age = (dt.date.fromisoformat(a.today) - dt.date.fromisoformat(fm["access_date"])).days
            if age > a.max_age_days:
                stale.append("%s (%d days)" % (f, age))
    for s in stale:
        print("STALE %s" % s)
    print("%d analog(s) checked, %d incomplete, %d stale." % (n, bad, len(stale)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
