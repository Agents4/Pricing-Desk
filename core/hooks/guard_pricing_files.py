#!/usr/bin/env python3
"""Pricing desk guard (PreToolUse / BeforeTool hook for file writes and edits).

Blocks a file write or edit that would ADD a record or document whose status is Approved. Only the
Pricing Council approves, and the model recommends (operating rule 10). It works on:
  - Gemini CLI: write_file and replace          (hook JSON: {"tool_name": ..., "tool_input": {"file_path", "content" | "old_string", "new_string"}})
  - Claude Code: Write, Edit, MultiEdit         (hook JSON: {"hook_event_name": "PreToolUse", "tool_name": ..., "tool_input": {"file_path", "content" | "old_string", "new_string" | "edits": [...]}})

What it looks at: files under workspace/ or outputs/, and any file whose name looks like a price book, council pack,
decision log, exception log, approval or account price (a symlink is judged by where it points as well as its name). It does
not look at the product source (core/, docs/, tests/, tools/, evals/), so ordinary maintenance edits are not blocked.
A change is blocked when the edit ADDS a record whose status is Approved or Decided (Decided is the Council's log entry;
skills draft and recommend, so they write Draft or For decision). Records are compared one by one, so approving one row
while un-approving another is still blocked, and editing other text of an already-approved record is allowed.
Markers: a CSV, TSV or other delimited column whose name contains status or approval, with a value that starts with
Approved or Decided ("Approved by Council" counts); a line "Status: Approved" (any case, bold, dash, equals or Markdown table);
a JSON or YAML status or approval key set to approved or decided (JSON is parsed, so escapes do not hide it).

It is a guardrail against mistakes by the model, not a security control. It cannot see edits made through shell commands,
notebooks, other tools, or a person editing a file. It does not make anything true: a document is Approved only when the
Council has approved it and a person records that.

Override for the Pricing Council: set PRICING_DESK_COUNCIL=1 in the environment before starting the CLI.

Reads the hook JSON on stdin and writes only JSON on stdout. Exit 0 always (the decision is in the JSON); on unexpected
input it allows the call, so a broken payload never blocks work.
"""
import csv
import io
import json
import os
import re
import sys
from collections import Counter

GUARDED_DIRS = ("workspace", "outputs")
SOURCE_DIRS = ("core", "docs", "tests", "tools", "evals", "design", "adapters", "skills", "commands", "agents", "hooks",
               "dist", ".claude", ".agents", "copilot-guide")
NAME_RE = re.compile(r"price[-_ ]?book|pricebook|council|decision[-_ ]?log|exception[-_ ]?log|approval|account[-_ ]?price", re.I)
EXTS = (".csv", ".tsv", ".json", ".md", ".markdown", ".txt", ".yaml", ".yml")
# Statuses only the Council may record. "Decided" is the Council's log entry; the model drafts and recommends.
WORD = r"(?:council[\s-]+)?(?:approved|decided)\b"
MD_RE = re.compile(r"^[ \t]*[*_#>|\-\s]*(?:approval[ \t]+)?status[ \t]*\**[ \t]*[:=|\-\u2013\u2014]+[ \t|]*\**[ \t]*" + WORD, re.I | re.M)
KEY_RE = re.compile(r"[\"']?(?:approval[_ ]?)?status[\"']?\s*[:=]\s*[\"']?" + WORD, re.I)
VALUE_RE = re.compile(r"^\W*" + WORD, re.I)   # a status cell that starts with Approved or Decided ("Approved by Council", "Approved.")
STATUS_COL_RE = re.compile(r"status|approval", re.I)


def _candidates(path):
    """The path as given and where it really points, so a symlink with an innocent name cannot hide a pricing file."""
    out = [path]
    try:
        real = os.path.realpath(path)
        if real != os.path.abspath(path):
            out.append(real)
    except OSError:
        pass
    return out


def _is_guarded_one(path):
    p = path.replace("\\", "/").lower()
    parts = [x for x in p.split("/") if x]
    if not parts:
        return False
    ext = os.path.splitext(parts[-1])[1]
    if ext and not p.endswith(EXTS):
        return False
    if any(d in parts[:-1] for d in GUARDED_DIRS):
        return True
    # The repo's own source and generated folders are not artifacts (works for absolute paths too).
    if any(d in parts[:-1] for d in SOURCE_DIRS):
        return False
    return bool(NAME_RE.search(parts[-1]))


def is_guarded(path):
    if not path:
        return False
    return any(_is_guarded_one(c) for c in _candidates(path))


def _csv_markers(text):
    """One marker per row whose status-like cell is Approved or Decided: (first cell, column). Any delimiter."""
    try:
        sample = text[:4096]
        delim = max(",;\t|", key=sample.count) if any(d in sample for d in ",;\t|") else ","
        found = []
        for r in csv.DictReader(io.StringIO(text), delimiter=delim):
            cells = list(r.items())
            ident = (cells[0][1] or "").strip().lower() if cells else ""
            for k, v in cells:
                if k and STATUS_COL_RE.search(k) and isinstance(v, str) and VALUE_RE.match(v.strip()):
                    found.append("row:%s:%s" % (ident, k.strip().lower()))
        return found
    except Exception:
        return []


def _json_markers(text):
    found = []

    def walk(o, trail):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and STATUS_COL_RE.search(str(k)) and VALUE_RE.match(v.strip()):
                    found.append("key:%s/%s" % ("/".join(trail), k))
                walk(v, trail + [str(k)])
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, trail + [str(i)])
    try:
        walk(json.loads(text), [])
    except Exception:
        return None
    return found


def markers(path, text):
    """The Approved/Decided records in a file, as comparable strings."""
    if not text:
        return []
    low = path.lower()
    if low.endswith((".csv", ".tsv")):
        return _csv_markers(text)
    out = ["line:" + m.group(0).strip().lower() for m in MD_RE.finditer(text)]
    if low.endswith((".json", ".yaml", ".yml")):
        js = _json_markers(text) if low.endswith(".json") else None
        out += js if js is not None else ["key:" + m.group(0).lower() for m in KEY_RE.finditer(text)]
    return out


def added_markers(path, before, after):
    b = Counter(markers(path, before))
    a = Counter(markers(path, after))
    return list((a - b).elements())


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def apply_edit(before, old, new, replace_all=False):
    if old and old in before:
        return before.replace(old, new) if replace_all else before.replace(old, new, 1)
    if not old:
        return new
    return before + "\n" + new   # cannot place the edit: judge the added text on top of the file


def proposed(tool_name, tool_input, path):
    """Return (before, after) text for the call, or (None, None) when the shape is not understood."""
    before = read(path)
    t = (tool_name or "").lower()
    if isinstance(tool_input.get("content"), str):
        return before, tool_input["content"]
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        after = before
        for e in edits:
            if isinstance(e, dict):
                after = apply_edit(after, e.get("old_string") or e.get("old_str") or "", e.get("new_string") or e.get("new_str") or "",
                                   bool(e.get("replace_all")))
        return before, after
    new = tool_input.get("new_string")
    if new is None:
        new = tool_input.get("new_str")
    if isinstance(new, str):
        return before, apply_edit(before, tool_input.get("old_string") or tool_input.get("old_str") or "", new,
                                  bool(tool_input.get("replace_all")))
    return None, None


def path_of(tool_input):
    for key in ("file_path", "path", "absolute_path", "notebook_path"):
        v = tool_input.get(key)
        if isinstance(v, str):
            return v
    return ""


def decide(data):
    """Return a reason string to deny, or None to allow."""
    if os.environ.get("PRICING_DESK_COUNCIL") == "1":
        return None
    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return None
    path = path_of(tool_input)
    if not is_guarded(path):
        return None
    before, after = proposed(data.get("tool_name"), tool_input, path)
    if after is None:
        return None
    if any(added_markers(c, before, after) for c in _candidates(path)):
        return "Blocked: only the Pricing Council sets a status to Approved or Decided. Use Draft, Proposed or For decision."
    return None


def respond(data, reason):
    # Claude Code names its event PreToolUse; Gemini CLI sends BeforeTool (and has its own deny shape).
    claude = data.get("hook_event_name") == "PreToolUse" or (
        "hook_event_name" not in data and str(data.get("tool_name", "")) in ("Write", "Edit", "MultiEdit", "NotebookEdit"))
    if reason is None:
        out = {"decision": "allow"}
        if claude:
            out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
    elif claude:
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}
    else:
        out = {"decision": "deny", "reason": reason}
    print(json.dumps(out))


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return
    try:
        reason = decide(data)
    except Exception:
        reason = None
    respond(data, reason)


if __name__ == "__main__":
    main()
