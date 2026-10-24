#!/usr/bin/env python3
"""Pricing desk guard (PreToolUse / BeforeTool hook for file writes and edits).

Blocks a file write or edit that would ADD a record or document whose status is Approved. Only the
Pricing Council approves, and the model recommends (operating rule 10). It works on:
  - Gemini CLI: write_file and replace          (hook JSON: {"tool_name": ..., "tool_input": {"file_path", "content" | "old_string", "new_string"}})
  - Claude Code: Write, Edit, MultiEdit         (hook JSON: {"hook_event_name": "PreToolUse", "tool_name": ..., "tool_input": {"file_path", "content" | "old_string", "new_string" | "edits": [...]}})

What it looks at: files under workspace/ or outputs/, and any file whose name looks like a price book, council pack,
decision log, exception log or approval. It does not look at the product source (core/, docs/, tests/, tools/, evals/),
so ordinary maintenance edits are not blocked. A change is blocked only when the file AFTER the edit holds more
"status: Approved" markers than the file BEFORE it, so editing other lines of an already-approved record is allowed.
Markers: a CSV or TSV column named status (any case) with the value Approved; a line "Status: Approved" (any case, bold or
not); a JSON or YAML key status set to approved.

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

GUARDED_DIRS = ("workspace", "outputs")
SOURCE_DIRS = ("core", "docs", "tests", "tools", "evals", "design", "adapters", "skills", "commands", "agents", "hooks",
               "dist", ".claude", ".agents", "copilot-guide")
NAME_RE = re.compile(r"price[-_ ]?book|pricebook|council|decision[-_ ]?log|exception[-_ ]?log|approval|account[-_ ]?price", re.I)
EXTS = (".csv", ".tsv", ".json", ".md", ".txt", ".yaml", ".yml")
MD_RE = re.compile(r"^\s*[*_#>\-\s]*status\s*\**\s*[:=]\s*\**\s*approved\b", re.I | re.M)
KEY_RE = re.compile(r"[\"']?status[\"']?\s*[:=]\s*[\"']?approved\b", re.I)


def is_guarded(path):
    if not path:
        return False
    p = path.replace("\\", "/").lower()
    if not p.endswith(EXTS):
        return False
    parts = [x for x in p.split("/") if x]
    if any(d in parts[:-1] for d in GUARDED_DIRS):
        return True
    # The repo's own source and generated folders are not artifacts (works for absolute paths too).
    if any(d in parts[:-1] for d in SOURCE_DIRS):
        return False
    return bool(NAME_RE.search(parts[-1]))


def count_approved(path, text):
    if not text:
        return 0
    low = path.lower()
    n = 0
    if low.endswith((".csv", ".tsv")):
        try:
            delim = "\t" if low.endswith(".tsv") else ","
            for r in csv.DictReader(io.StringIO(text), delimiter=delim):
                for k, v in r.items():
                    if k and k.strip().lower() == "status" and isinstance(v, str) and v.strip().lower() == "approved":
                        n += 1
        except Exception:
            pass
        return n
    n += len(MD_RE.findall(text))
    if low.endswith((".json", ".yaml", ".yml")):
        n += len(KEY_RE.findall(text))
    return n


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
    if count_approved(path, after) > count_approved(path, before):
        return "Blocked: only the Pricing Council sets a status to Approved. Use Draft, Proposed or For decision."
    return None


def respond(data, reason):
    claude = "hook_event_name" in data or str(data.get("tool_name", "")) in ("Write", "Edit", "MultiEdit", "NotebookEdit")
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
