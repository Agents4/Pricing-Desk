#!/usr/bin/env python3
"""Pricing desk guard (Gemini CLI BeforeTool hook for write_file and replace).

Blocks a file edit when the new text would set a price book line status to Approved (only the
Pricing Council does that).

It is a guardrail against mistakes by the model, not a security control: it only sees
write_file and replace calls, not edits made through shell commands or in other tools.

Override for the Pricing Council: set PRICING_DESK_COUNCIL=1 in the environment before starting the CLI.

Reads the hook JSON on stdin. Writes only JSON on stdout.
Exit 0 always (decision is in the JSON); on unexpected input it allows the call.
"""
import csv
import io
import json
import os
import re
import sys

def text_of(tool_input):
    # write_file sends "content"; replace sends "new_string"
    for key in ("content", "new_string"):
        v = tool_input.get(key)
        if isinstance(v, str):
            return v
    return ""


def path_of(tool_input):
    for key in ("file_path", "path", "absolute_path"):
        v = tool_input.get(key)
        if isinstance(v, str):
            return v
    return ""


def csv_rows(text):
    try:
        return list(csv.DictReader(io.StringIO(text)))
    except Exception:
        return []


def sets_approved(path, text):
    if os.environ.get("PRICING_DESK_COUNCIL") == "1":
        return False
    low = os.path.basename(path.lower())
    if not (low.endswith((".csv", ".tsv", ".json", ".md")) and re.search(r"price[-_ ]?book|pricebook", low)):
        return False
    if low.endswith((".csv", ".tsv")):
        return any(str(r.get("status", "")).strip().lower() == "approved" for r in csv_rows(text))
    return bool(re.search(r"status[\"']?\s*[:=]\s*[\"']?approved\b", text, re.I))


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input") or {}
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return
    path, text = path_of(tool_input), text_of(tool_input)
    if sets_approved(path, text):
        print(json.dumps({
            "decision": "deny",
            "reason": "Blocked: only the Pricing Council sets a price book line to Approved. Use Draft or Proposed.",
        }))
        return
    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
