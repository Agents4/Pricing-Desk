"""Check analog library entries for the fields rule 11 requires.

Usage:
  python check_analogs.py --dir workspace/context-library/analogs [--today YYYY-MM-DD] [--max-age-days N]

Each analog file (not README.md) needs frontmatter with: source_url (a real web address: http or https, a host with a dot,
not a placeholder such as example.com), access_date (a real date, YYYY-MM-DD, not in the future), unit, metric,
right_or_use, comparability (written 'N of 5', N from 1 to 5). With --max-age-days it also lists entries whose access_date is older than N days from
--today (--today is then required). N is a company or user value (the freshness limit in pricing-governance.md);
no default is assumed.
Exit codes: 1 when any entry is incomplete, 2 for unusable input, 0 otherwise.
"""
import argparse
import datetime as dt
import os
import re
import sys
from urllib.parse import urlparse

REQ = ["source_url", "access_date", "unit", "metric", "right_or_use", "comparability"]
PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "localhost", "test.com", "domain.com", "yoursite.com"}
PLACEHOLDER_TLDS = {"invalid", "test", "example", "localhost"}


def front(path):
    with open(path, encoding="utf-8") as fh:
        t = fh.read()
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip().strip('"')
    return out


def url_problem(u):
    p = urlparse(u)
    if p.scheme not in ("http", "https") or not p.hostname:
        return "source_url is not a web address"
    h = p.hostname.lower()
    if "." not in h:
        return "source_url host %r is not a public site" % h
    if h in PLACEHOLDER_HOSTS or h.rsplit(".", 1)[-1] in PLACEHOLDER_TLDS or h.endswith(".example.com"):
        return "source_url host %r is a placeholder, not a source" % h
    return None


def date_problem(s, today):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return "access_date is not YYYY-MM-DD"
    try:
        d = dt.date.fromisoformat(s)
    except ValueError:
        return "access_date %s is not a real date" % s
    if d > today:
        return "access_date %s is in the future" % s
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--today")
    ap.add_argument("--max-age-days", type=int)
    a = ap.parse_args()
    try:
        today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    except ValueError:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    if a.max_age_days is not None and (not a.today or a.max_age_days < 0):
        print("--max-age-days needs --today and a value of 0 or more", file=sys.stderr)
        return 2
    if not os.path.isdir(a.dir):
        print("%s is not a folder" % a.dir, file=sys.stderr)
        return 2
    bad, stale, n = 0, [], 0
    for f in sorted(os.listdir(a.dir)):
        if not f.endswith(".md") or f.lower() == "readme.md":
            continue
        n += 1
        fm = front(os.path.join(a.dir, f))
        miss = [k for k in REQ if not fm.get(k)]
        if fm.get("source_url") and url_problem(fm["source_url"]):
            miss.append(url_problem(fm["source_url"]))
        if fm.get("comparability") and not re.match(r"^[1-5] of 5\b", fm["comparability"]):
            miss.append("comparability must start with the score as 'N of 5' (1 to 5)")
        if fm.get("access_date") and date_problem(fm["access_date"], today):
            miss.append(date_problem(fm["access_date"], today))
        if miss:
            bad += 1
            print("INCOMPLETE %s: %s" % (f, "; ".join(miss)))
        elif a.max_age_days is not None:
            age = (today - dt.date.fromisoformat(fm["access_date"])).days
            if age > a.max_age_days:
                stale.append("%s (%d days)" % (f, age))
    for s in stale:
        print("STALE %s" % s)
    if n == 0:
        print("No analog files found in %s." % a.dir, file=sys.stderr)
        return 2
    print("%d analog(s) checked, %d incomplete, %d stale." % (n, bad, len(stale)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
