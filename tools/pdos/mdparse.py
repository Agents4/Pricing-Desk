"""Frontmatter and Markdown helpers with no third-party dependencies.

Frontmatter is a YAML subset: top-level `key: value`, one level of nesting
(`key:` followed by indented `sub: value`), inline lists `[a, b]`, and folded
blocks (`key: >` followed by indented text).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        inner = v[1:-1]
        if v[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    return v


def _split_csv(s: str) -> List[str]:
    out, cur, q = [], [], None
    for ch in s:
        if q:
            cur.append(ch)
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
            cur.append(ch)
        elif ch == ",":
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur).strip())
    return out


def _scalar(v: str) -> Any:
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [] if not inner else [_unquote(x) for x in _split_csv(inner)]
    return _unquote(v)


def split_frontmatter(text: str) -> Tuple[Dict[str, Any], str, Optional[str]]:
    """Return (frontmatter dict, body, error)."""
    m = FM_RE.match(text)
    if not m:
        return {}, text, None
    raw = m.group(1)
    body = text[m.end():]
    fm: Dict[str, Any] = {}
    current: Optional[str] = None
    folded: Optional[str] = None
    for i, line in enumerate(raw.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line[:1] in (" ", "\t")
        if folded is not None and indented:
            fm[folded] = (fm[folded] + " " + line.strip()).strip()
            continue
        folded = None
        if indented:
            if current is None or not isinstance(fm.get(current), dict):
                return fm, body, "line %d: unexpected indentation" % i
            if ":" not in line:
                return fm, body, "line %d: expected `key: value`" % i
            k, _, v = line.strip().partition(":")
            fm[current][k.strip()] = _scalar(v)
            continue
        if ":" not in line:
            return fm, body, "line %d: expected `key: value`" % i
        k, _, v = line.partition(":")
        k = k.strip()
        if v.strip() in (">", "|", ">-", "|-"):
            fm[k] = ""
            folded = k
            current = None
        elif v.strip() == "":
            fm[k] = {}
            current = k
        else:
            fm[k] = _scalar(v)
            current = None
    for k, v in list(fm.items()):
        if v == {}:
            fm[k] = ""
    return fm, body, None
