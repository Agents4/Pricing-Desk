---
name: council-decision-pack
description: Assemble the monthly Pricing Council pack with decisions first, each with recommendation, options, computed numbers, risks, stakeholder review and rights hand-off status, then a decision log entry template. Use when the Council meeting is coming up, when a price change, new construct, matrix change or large exception needs a decision, or when a pack lead time is near.
compatibility: "Any Agent Skills client. File access recommended; otherwise returns the pack as one block to save."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, templates/council-pack.md"
---

# Council decision pack

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

The Council reads decisions, not history. The pack puts the decisions first and lets a member decide each in a few minutes. Only the Council approves; the pack recommends.

## When to use

- A Council meeting is scheduled and a pack is due (lead time is in `pricing-governance.md`; Unknown if blank).
- A price change, new product or construct price, approval-matrix change or exception above delegated authority needs a decision.

Not for: writing the change itself (`price-change-proposal`), reviewing one deal (`deal-desk-review`), the weekly review (`weekly-pricing-review`).

## Inputs

Read `pricing-governance.md` for the Council, decision rights and pack lead time. Gather: proposals ready for decision (from `price-change-proposal`, `data-price-setting`, `deal-desk-review`), the latest weekly reviews, the exception log, the rights hand-off status (`rights-handoff`), and the decision log. Ask one question at a time for what is missing. A proposal with no named proposer or no computed numbers is not ready: list it under Missing, not under Decisions.

## Procedure

1. **List the decisions.** One row per decision with its recommendation, proposer and the approver the decision-rights table names. If the table is a template, write Unknown and name the file.
2. **Check readiness of each.** Numbers computed by script with inputs named; granted right stated for every data and API line; rights hand-off status shown (open, answer on file, not needed); stakeholder review run for changes with customer effect (`pricing-stakeholder-review`).
3. **Write each decision** in the template: ask, options with numbers, recommendation, risks and what would change our mind.
4. **Add information items**: weekly headlines, exceptions, flags.
5. **Order by consequence**, not by date received.
6. **Leave the decision log entry blank** for a person to fill after the meeting. Never write Approved.

## Output

Fill `assets/council-pack.md`. Decisions table first, then one section per decision, information items, Missing, four-part handoff. Status For decision, never Decided.

## Quality gate

- The first screen shows every decision and what is asked.
- No number is uncomputed or untagged; each option names its script and inputs.
- Every data and API line states the granted right and the hand-off status.
- No approver, threshold or membership appears that did not come from the context library.
- The pack never says a decision is made; the log entry is for a person.
- Customer names appear only where the decision needs them, and the pack is marked Internal.
