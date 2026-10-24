---
name: price-change-proposal
description: Build a price change proposal for API access, premium software, or data products. Models base, low, and high scenarios, lists impacted customers, checks contract price-protection and notice terms, and drafts a one-page council memo with a risk register and communication outline. Use when proposing a list price, tier, or packaging change.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted data and says the check was not run."
metadata:
  version: "1.1.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Price Change Proposal

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Turn a proposed price or packaging change into a decision package for the Pricing Council. The council decides; Legal confirms notice terms.

## When to use

- Proposing a change to list price, tiers, units, a fee, or packaging.
- A cost or supplier change forces a price move.
- A renewal needs a price increase and the notice terms matter.

Not for: setting a price for a new product (`data-price-setting`) or one account's concession (`deal-desk-review`).

## Inputs

Context library files read: `pricing-governance.md`, `deal-structures.md` (notice and price protection terms), `systems-and-data.md`. If a file still says `status: template`, treat its values as Unknown.

1. **The change**: product family, what changes (list price, tier boundaries, unit definition, new fee, discontinued plan), proposed effective date, rationale.
2. **Customer base**: customer, plan, current price, volume, contract end date, segment.
3. **Contract terms**: price-protection periods, notice periods, MFN clauses, renewal terms (a summary table is fine).
4. **Price book** (current version).
5. **Elasticity or churn assumptions**: from past price changes, research, or the desk's estimates. If none exist, say so and use stated ranges, clearly labeled as assumptions.
6. **Competitive context**, if available, with sources.

## Procedure

1. **Restate the change** in one table: before and after, by plan and unit.
2. **Segment customers** by how the change affects them: unaffected, increase, decrease, and by size of change. Compute with code.
3. **Check contracts.** Mark each customer: change can take effect at the proposed date, only at renewal, or only after notice. Show the earliest effective date per group and the share of revenue in each. Flag MFN or price-protection conflicts for Legal. Do not interpret contract language; quote the clause reference and escalate.
4. **Model scenarios with code**: base, low, and high, varying volume response and churn by segment. Show revenue, margin if cost is supplied, and customers lost or downgraded, month by month for 12 months, with the assumptions in a table.
5. **Compute sensitivities**: which assumption moves the result most.
6. **Build the notice calendar**: contract notice deadlines, internal approval dates, communication dates, effective dates.
7. **Draft a risk register**: churn in key accounts, win-rate effect, partner or channel reaction, billing and system readiness, legal exposure, and perception risk. Give each a mitigation and owner role.
8. **Outline communications** (not final copy): audiences, key message, what changes, what does not, timing, and who speaks to strategic accounts.

## Output

1. **One-page council memo**: decision requested, change, rationale, scenario results in a small table, top three risks, recommendation, and the conditions for approval.
2. **Scenario model summary** and **assumptions table**.
3. **Impacted customer list** (top 25 by revenue plus counts by group).
4. **Contract and notice summary** with items escalated to Legal.
5. **Notice calendar**.
6. **Risk register.**
7. **Communication outline.**
8. **Post-change monitoring plan**: metrics and thresholds at 30, 60, and 90 days.
9. **Inputs and assumptions used.**

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute all figures with code; show the assumptions behind every scenario.
- Never present a point estimate without the range.
- Do not state that a change is allowed under a contract; list what Legal must confirm.
- Do not contact customers or draft customer-facing final copy from this skill.
- Keep customer-specific figures inside the proposal; do not copy them into general summaries.
