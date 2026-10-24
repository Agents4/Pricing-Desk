---
name: pricing-stakeholder-review
description: Read a pricing proposal through the lenses of Finance, Sales, customer procurement, the product manager and Legal, a competitor, and engineering and metering, and return each lens's top question, objection and what would change the proposal. Use when a proposal is going to the Council, before a price book release, or when you want an independent read before anything leaves the desk.
compatibility: "Any Agent Skills client. Runs lenses in parallel when subagents are available; otherwise runs them one after another and says so."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, methodology/stakeholder-lenses.md"
---

# Pricing stakeholder review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

The proposer cannot see their own blind spots. Each lens reads the proposal as someone who was not in the room, and says what they would ask, object to and need. The lenses are in `references/stakeholder-lenses.md`.

## When to use

- A proposal is heading to the Council (`council-decision-pack`).
- Before a price book release (`price-book-release`).
- Any time rule 7 applies: independent review before anything leaves the desk.

Not for: sales-side stakeholder maps of a customer's buying group (use Sales-OS), or a replacement for a real person's sign-off.

## Inputs

The proposal (price change, new construct, deal package, price book diff) and its computed numbers. Roles and names for each lens come from the context library; if absent, use role names only. Ask one question at a time for what is missing.

## Procedure

1. **Pick the lenses** the proposal touches and say which are skipped and why. A data or API line always includes product manager and Legal.
2. **Run each lens fresh.** With subagents, run each lens on its own with only the proposal and the lens definition, so one reading does not colour another. Without subagents, run them in turn and say the review was not independent.
3. **Each lens returns** three lines: top question, top objection, what would change the proposal. Tag every statement I (inference) unless a real person has given a view; then quote it with date and source and tag F.
4. **Show conflicts** between lenses side by side. Do not resolve them.
5. **Sort the findings**: must fix before the Council; should answer in the pack; note only.
6. **Rights questions** go to `rights-handoff`. Clause questions go to Legal as questions, not interpretations.

## Output

Header; the finding in one line (the number of must-fix items); a table with one row per lens; conflicts; findings sorted by must fix, should answer, note; four-part handoff. Status Draft.

## Quality gate

- Every lens statement is tagged I, or F with a dated source.
- No lens invents a named person's opinion.
- Skipped lenses are listed with the reason.
- The review says whether it was independent (separate runs) or sequential.
- Findings are not softened to match the recommendation.
- Nothing in the review approves or rejects the proposal.
