---
name: price-realization-analysis
description: Analyze price realization and revenue leakage from billing lines, the price book, and the deal log. Builds a list-to-realized waterfall by product family, segment, and customer, ranks leakage drivers, and proposes recovery actions. Use when the monthly pricing review or when realized price is below plan.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted data and says the check was not run."
metadata:
  version: "1.1.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Price Realization Analysis

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Explain the gap between what the price book says and what customers actually pay, find where it leaks, and say what to do about it.

## When to use

- The weekly or monthly pricing review.
- Realized price is below plan or a customer's invoice is far below list.
- Revenue leakage needs sizing and an owner.

Not for: judging a single deal (`deal-desk-review`) or API tier fit (`api-usage-tier-fit`).

## Inputs

Context library files read: `systems-and-data.md`, `pricing-governance.md`. If a file still says `status: template`, treat its values as Unknown.

1. **Billing lines** for the period: customer, product, unit, quantity, billed amount, invoice date, credits and adjustments.
2. **Price book** (versioned, with effective dates) so list value can be rebuilt for each line.
3. **Deal log or contract terms**: approved discounts, commits, ramps, tier, approver.
4. **Optional**: metered usage for the same period, to test billing against usage.

If the price book version or deal log is missing, state which analyses you can and cannot run.

## Procedure

1. **Reconcile first.** Check totals against finance revenue if provided. Report row counts, nulls, duplicates, and unmatched products. Stop and report if the reconciliation gap exceeds the tolerance set in `pricing-governance.md` or by the user (ask if Unknown), since every later figure inherits it.
2. **Rebuild list value** for each line from the price book version in force on the invoice date.
3. **Build the waterfall with code**: list value, then approved discounts, then unapproved or unexplained discount, then credits and adjustments, then billing and metering gaps, to realized revenue. Report in USD and as a percent of list.
4. **Cut it** by product family, segment, discount tier, customer (top 20), contract vintage, and sales owner if provided.
5. **Classify leakage drivers**: approved discount beyond guardrail, discount with no recorded approval, expired promotions still applied, unbilled overage or usage, tier mismatch, credits and write-offs, price book errors, unit definition problems.
6. **Size and rank** each driver by monthly and annualized value, and by recoverability (easy fix, needs customer conversation, needs contract change).
7. **Recommend actions** per top driver: owner role, step, expected recovery range, and how it would be verified.

## Output

1. **Headline**: realization rate for the period, change versus prior period if data allows, and the largest driver in one sentence.
2. **Waterfall** (chart or table) with list, each step, and realized.
3. **Top five leakage drivers** table: driver, value, share, recoverability, owner.
4. **Customers and segments to review** (top 10), each with the reason.
5. **Recovery plan**: actions in priority order.
6. **Data quality notes**: reconciliation result, rows excluded and why.
7. **Inputs and assumptions used.**

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute everything with code. Show the script's key figures and where they come from.
- Never present unreconciled data as final; label it provisional.
- Separate approved discount (policy working as designed) from unexplained discount (a control gap). Do not treat all discount as leakage.
- Do not name individual sales reps in broad summaries; give owners at role or team level unless the Analytics Lead asks for detail.
- Hand the Analytics Lead the data checks to sign off before the results go beyond the desk.
