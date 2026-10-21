#!/usr/bin/env python3
"""Pricing desk guard (Gemini CLI BeforeTool hook for write_file and replace).

Blocks a file edit when the new text would:
  1. set legal_confirmed to Yes in a register export (only Legal does that), or
  2. set a price book line status to Approved (only the Pricing Council does that).

It is a guardrail against mistakes by the model, not a security control: it only sees
write_file and replace calls, not edits made through shell commands or in other tools.

Override for the people who hold the authority: set PRICING_DESK_LEGAL=1 (Legal) or
PRICING_DESK_COUNCIL=1 (Pricing Council) in the environment before starting the CLI.

Reads the hook JSON on stdin. Writes only JSON on stdout.
Exit 0 always (decision is in the JSON); on unexpected input it allows the call.
"""
import csv
import io
import json
import os
import re
import sys

CONFIRMED_COLS = ("legal_confirmed", "confirmed")


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


def sets_legal_confirmed(path, text):
    if os.environ.get("PRICING_DESK_LEGAL") == "1":
        return False
    low = path.lower()
    # CSV or table style: a legal_confirmed column with value Yes
    if low.endswith((".csv", ".tsv")):
        for row in csv_rows(text):
            for col in CONFIRMED_COLS:
                if str(row.get(col, "")).strip().lower() == "yes":
                    return True
    # JSON / YAML / markdown style: legal_confirmed: Yes  or  "legal_confirmed": "Yes"
    if re.search(r"legal_confirmed[\"']?\s*[:=]\s*[\"']?yes\b", text, re.I):
        return True
    return False


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
    if sets_legal_confirmed(path, text):
        print(json.dumps({
            "decision": "deny",
            "reason": "Blocked: only Legal sets legal_confirmed to Yes. Leave it blank and add the question for Legal instead.",
        }))
        return
    if sets_approved(path, text):
        print(json.dumps({
            "decision": "deny",
            "reason": "Blocked: only the Pricing Council sets a price book line to Approved. Use Draft or Proposed.",
        }))
        return
    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
