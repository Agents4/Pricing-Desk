---
name: quarterly-price-review
description: Run the quarterly review of every product line against value, market and realization, compare earlier price changes with their forecast, refresh the analog library, and propose changes, holds and retirements for the Council. Use when the quarter closes, before the Council meeting that follows it, or when asked which lines to change next quarter.
compatibility: "Any Agent Skills client. Runs the sub-skills' scripts where a shell exists; otherwise says which checks were not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, templates/quarterly-review.md"
---

# Quarterly price review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Once a quarter, every line gets the same questions: is it priced to value, to the market, and does it realize? The review ends in proposals for the Council, each with evidence and a test that would prove it wrong.

## When to use

- The quarter has closed.
- Before the Council meeting that follows it.
- Someone asks which lines to change, hold or retire.

Not for: the weekly view (`weekly-pricing-review`), one change in depth (`price-change-proposal`), the annual release (`price-book-release`).

## Inputs

The price book; three months of weekly reviews and realization (`price-realization-analysis`); win-loss for the quarter (`pricing-win-loss`); the latest competitor scan (`competitive-price-scan`); willingness-to-pay evidence (`wtp-study-design`); the decision log with earlier changes and their forecasts; the exception log. Ask one question at a time for what is missing and list gaps in the review.

## Procedure

1. **List the lines** from the price book, with the granted right for each data and API line. A line with no stated right is a finding.
2. **Gather the three readings per line:** value (WTP, `data-product-valuation`), market (scan, analogs), realization (weekly roll-ups, `price-realization-analysis`). Run the scripts; do not estimate.
3. **Add win-loss and usage fit** (`pricing-win-loss`, `api-usage-tier-fit`).
4. **Close the loop:** for each change approved in the last four quarters, compare forecast with realized effect and name the gap and likely cause. Send repeated misses to `pd-ratchet`.
5. **Refresh analogs.** Re-check entries and add new ones (`analog-research`).
6. **Recommend** change, hold or retire for each line, with the evidence and a disproof test. Changes go to `price-change-proposal` and `council-decision-pack`.
7. **Review the exceptions.** Concessions still open without a get; accounts whose anchor deal is up for renewal.

## Output

Fill `assets/quarterly-review.md`: the line table, proposed changes, forecast against realized, analog library changes, Missing, four-part handoff. Status Draft.

## Quality gate

- Every line appears, even if only to say hold and why.
- All figures come from scripts or sources named in the review.
- Every change proposal carries evidence and a disproof test.
- Forecast against realized is shown for earlier changes, or the output says no forecast was recorded.
- No threshold or target appears that the context library or the user did not supply.
- Nothing is marked Approved.
