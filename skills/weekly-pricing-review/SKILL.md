---
name: weekly-pricing-review
description: Produce the one-page weekly pricing review from billing lines, API usage and the exception log. Shows realization against list and last week, leakage by cause, plans where usage does not fit, usage patterns to confirm, and three actions with owners. Use when it is review day, when someone asks how pricing performed this week, or when realized price drops.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted figures and says the roll-up was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Weekly pricing review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

One page, same day each week. It tells the desk where money leaked, which accounts need a conversation, and what to do before next week.

## When to use

- The weekly review day.
- Realized price fell and someone asks why.
- Input to the monthly Council pack (`council-decision-pack`).

Not for: a deep leakage study by customer and segment (`price-realization-analysis`), a single deal (`deal-desk-review`), tier design (`api-usage-tier-fit`).

## Inputs

1. Billing lines for the week and at least the prior week: week, family, list value, realized value, cause (CSV, see `examples/lines.csv`).
2. API usage by key, if available (searches, bookings, distinct queries). The screen and its threshold come from `api-access-request`; the threshold is a company value and may be Unknown.
3. The exception log from `workspace/`.
4. A plan or target for realization, only if the user supplies it. None is assumed.

Ask one question at a time for what is missing. Say which sections are skipped for lack of data.

## Procedure

1. **Roll up with the script.** `scripts/weekly_roll.py --in <file> [--week YYYY-MM-DD]` gives the realization rate against the prior week, by family and by cause.
2. **Read the gap.** Name the largest cause and the family with the largest change. Treat Unlabeled causes as a finding: someone must label them.
3. **Usage fit.** For API keys, apply `api-usage-tier-fit` and, for a flagged pattern, the screen in `api-access-request`. Word every flag as "usage pattern to confirm with the account owner".
4. **Exceptions.** Count new, expiring and unrequited concessions from the exception log.
5. **Choose three actions**, each with an owner and a date. If an owner is not known, write Unknown and ask.
6. **Route.** Rights questions to `rights-handoff`. Price changes to `price-change-proposal`. Large exceptions to `deal-desk-review`.

## Output

Header; one line on the week; realization table; leakage by cause; usage fit and flags; exceptions; three actions with owners and dates; Missing list; four-part handoff. Status Draft. Keep to one page.

## Quality gate

- Every number came from the script or the input and says so.
- No target or threshold is shown that the user or the context library did not supply.
- Flags are questions to confirm, never findings against a customer.
- Exactly three actions, each with an owner and date, or a stated reason there are fewer.
- Customer names stay in this internal review and are not copied into broader summaries.
