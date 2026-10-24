---
name: pd-start
description: Entry point for the Pricing Desk OS. Checks the state of the context library, price book and tools, asks what the user needs, and routes to the right skill or rhythm. Use when the user is unsure where to begin, says "pricing desk", or asks what is due today, this week, this month or this quarter.
compatibility: "Any Agent Skills client. File access recommended to inspect the workspace; otherwise it asks the user what exists."
metadata:
  version: "1.0.0"
  layer: system
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, shared/interview-protocol.md"
---

# Pricing Desk start

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Find out where the user is, then send them to the one skill that moves the work.

## When to use

- The user is new, unsure, or says "help me with pricing".
- The user asks what is due: deals today, the weekly review, the Council pack, the quarter review, the annual release.
- A request fits no skill: answer from the rules and say which skill would come closest.

Not for: doing the work itself. Route and stop.

## Inputs

Read if present: `workspace/context-library/pricing-governance.md`, `product-catalog.md`, `systems-and-data.md`, `lessons.md`; `workspace/price-book/`; the newest files in `workspace/outputs/`. If a library file says `status: template`, it counts as empty.

## Procedure

1. **Check state.** Report in three lines: context library (filled, partly, template), price book (present, version, last checker run), tools (files, shell, web). If you cannot look, ask one question: what exists?
2. **Ask one question** (see `references/interview-protocol.md`): what do you need to decide or produce? Offer the common answers from the table below.
3. **Route.** Name the skill and what it needs from the user. If the context library is a template and the work needs thresholds or the Council, route to `pd-setup` first and say why in one line.
4. **Rhythm check.** Given today's date, say which rhythms are due: daily deal desk, weekly review (same weekday each week), monthly Council pack, quarter-end review, annual release. Use dates in `workspace/outputs/`; if none exist, say "no history yet".

| The user wants to | Skill |
|---|---|
| Set up the context library for a company | `pd-setup` |
| Decide what to charge for a new product, right or API use | `data-price-setting` (after `analog-research` if there is no price history) |
| Handle today's quote requests | `deal-desk-triage` |
| Review one deal | `deal-desk-review`, with `account-price-fit` when there is an anchor deal |
| Handle new or expanded API access, including access that may collect data | `api-access-request` |
| Price a data licence, or the right once the purpose is decided | `data-license-pricing` |
| Run the weekly realization and API usage review | `weekly-pricing-review` |
| Prepare the Council | `council-decision-pack` |
| Release the price book | `price-book-release` |
| Turn a miss into an improvement | `pd-ratchet` |

The full routing table is in `AGENTS.md`.

## Output

The header, then: state (three lines), the one skill to run next with what it needs, rhythms due, and the single question you still have. Do not file anything.

## Quality gate

- One next step only, not a menu of five.
- Nothing about thresholds, the Council or floors stated from memory; Unknown if the library is a template.
- No work done that belongs to the routed skill.
