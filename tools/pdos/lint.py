"""Lint a pricing output (Markdown) against the operating rules that can be checked mechanically."""
from __future__ import annotations

import re
from typing import List, Tuple

from .skills import Issue

STATUSES = {"draft", "for decision", "decided"}
NUMERIC = re.compile(r"(\$\s?\d|\d\s?%|\b\d{1,3}(,\d{3})+\b|\b\d+\.\d+\b)")
TAG = re.compile(r"(\((F|I|A|U)\)|\[(F|I|A|U)\]|\b(F|I|A|U):\s|\|\s*(F|I|A|U)\s*\|)")
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")


def _tables(lines: List[str]) -> List[Tuple[int, List[str], List[List[str]]]]:
    out = []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            out.append((i + 1, header, rows))
            i = j
        else:
            i += 1
    return out


def lint_text(text: str, where: str) -> List[Issue]:
    issues: List[Issue] = []
    lines = text.splitlines()
    body = [l for l in lines if l.strip()]

    def add(level, code, msg):
        issues.append(Issue(level, code, where, msg))

    if len(body) < 2:
        add("error", "OL001", "output is empty")
        return issues
    head = "\n".join(body[:8])
    if not re.search(r"^\*\*Answer:\*\*\s*\S", head, re.MULTILINE):
        add("error", "OL001", "line one under the title must be `**Answer:** ...` (rule 1)")
    if not re.search(r"^\*\*Decision and owner:\*\*\s*\S", head, re.MULTILINE):
        add("error", "OL002", "missing `**Decision and owner:**` near the top (rule 2)")
    m = re.search(r"^Status:\s*([A-Za-z ]+?)(\s{2,}|\s*$)", head, re.MULTILINE)
    if not m:
        add("error", "OL003", "missing `Status:` line (rule 6)")
    else:
        s = m.group(1).strip().lower()
        if s == "approved":
            add("error", "OL004", "Status is Approved; only the Council logs a decision (rule 10)")
        elif s not in STATUSES:
            add("error", "OL003", "Status %r is not Draft, For decision or Decided" % m.group(1).strip())
    if not re.search(r"Handling:\s*(Internal|Shareable)", head):
        add("error", "OL005", "missing `Handling: Internal` or `Handling: Shareable` (rule 4)")
    if NUMERIC.search(text) and not TAG.search(text):
        add("warn", "OL006", "numbers appear but no evidence tag (F, I, A or U) is used (rule 3)")
    if re.search(r"^##\s+Handoff", text, re.MULTILINE | re.IGNORECASE):
        for label in ("Done:", "Not done:", "You decide:", "Watch:"):
            if not re.search(r"^\s*" + re.escape(label), text, re.MULTILINE):
                add("error", "OL007", "Handoff section is missing %r (rule 5)" % label)
    for line_no, header, rows in _tables(lines):
        h = [c.lower() for c in header]
        if any("source url" in c for c in h):
            idx = [i for i, c in enumerate(h) if "source url" in c][0]
            didx = [i for i, c in enumerate(h) if "access" in c]
            for r in rows:
                if idx >= len(r) or not r[idx].startswith("http"):
                    add("error", "OL008", "analog table line %d: row without a source URL (rule 11)" % line_no)
                    break
                if not didx or didx[0] >= len(r) or not DATE.search(r[didx[0]]):
                    add("error", "OL008", "analog table line %d: row without an access date (rule 11)" % line_no)
                    break
    unknown = len(re.findall(r"\bUnknown\b", text))
    if unknown:
        add("warn", "OL009", "%d Unknown placeholder(s) left; list them under Missing" % unknown)
    return issues


def lint_file(path: str) -> List[Issue]:
    with open(path, "r", encoding="utf-8") as fh:
        return lint_text(fh.read(), path)
