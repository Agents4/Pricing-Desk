---
name: pricing-win-loss
description: Review won and lost deals for pricing causes. Tallies outcomes by price cause, discount and competitor, separates what the deal team believes from what is evidenced, and turns patterns into proposed changes to list, packaging, bands or terms. Use when a quarter closes, after a notable loss, or when sales says price is the reason deals are lost.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill tallies the pasted list and says the script was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Pricing win and loss review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

"We lost on price" is a hypothesis. This skill tests it against the deal record and separates price from value, packaging, terms and a competitor.

## When to use

- Quarter end, as an input to `quarterly-price-review`.
- After a notable loss or a run of wins at deep discount.
- When sales says price is why deals are lost.

Not for: a sales-side win-loss on selling behavior (use Sales-OS), or reviewing a live deal (`deal-desk-review`).

## Inputs

A deal list with outcome, price cause, discount and competitor (CSV, see `examples/deals.csv`). Where available: the final quote, the deal desk package, and the buyer's stated reason. Causes entered by sellers are their reading; ask for the buyer's words when they exist.

Read `pricing-governance.md` for the band. Unknown is a valid answer. Ask one question at a time for what is missing.

## Procedure

1. **Tally with the script.** `scripts/winloss_tally.py --in <file>` counts causes by outcome and gives average discounts. Always report n. Make no significance claim.
2. **Separate the causes.** Price level, value gap, packaging or metric, terms, competitor price, no price reason. A loss with a deep discount offered is not a price-level loss.
3. **Check discount against outcome.** Did deeper discount buy wins, or did the same deals win anyway? Show the evidence, tagged F, I, A or U.
4. **Competitor claims.** Competitor prices are valid only with a source and date (see `competitive-price-scan`); otherwise mark them unverified.
5. **Propose changes** by lever: list, packaging, value metric, band, terms, fences. Each names the evidence and what would disprove it. Send accepted ideas to `price-change-proposal`.
6. **Say what the record cannot show.** Missing causes, thin counts, sellers' reading only.

## Output

Header; the finding in one line; tally table with n; discount against outcome; competitor table with sources; proposed changes with evidence and disproof; limits of the data; four-part handoff. Status Draft.

## Quality gate

- Counts and averages came from the script or the input; n is shown everywhere.
- Seller opinion is tagged I, not F.
- No conclusion that price caused a loss when the record shows a discount was offered and refused for another reason.
- Competitor prices carry a source and date, or are marked unverified.
- No change is recommended from fewer deals than the user would trust; say the count and let the user decide.
