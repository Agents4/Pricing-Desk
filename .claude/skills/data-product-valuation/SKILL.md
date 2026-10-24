---
name: data-product-valuation
description: Value a data product three ways, by cost to recreate, by market comparables and by income to the buyer, and show the range with the inputs behind each. Use when a data product has no price history, when the corridor needs a value anchor, when a licence is large enough to justify a valuation, or when a buyer disputes value.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill computes by hand and says the script was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, methodology/frameworks.md"
---

# Data product valuation

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Three approaches give three readings. A wide gap is a finding about what we know, not a failure. The result is a value anchor for the corridor in `data-price-setting`, not a price. See `references/frameworks.md` for the named methods and their status.

## When to use

- A data product has no price history.
- The corridor needs a value anchor.
- A large licence or a buyer's dispute justifies a valuation.

Not for: setting the price (`data-price-setting`), pricing a right (`data-license-pricing`).

## Inputs

1. **Cost:** build cost, annual run cost, the horizon in years. From Finance or the product owner; label F with source, or A.
2. **Market:** comparable products with prices, unit, scope and source (`analog-research`, `competitive-price-scan`). Only verified rows.
3. **Income:** the buyer's annual net benefit and how it was estimated, the horizon, and the discount rate. The rate and horizon are the user's or Finance's; none is assumed.
4. The right the product grants (the value changes with the right).

Ask one question at a time. A missing input skips that approach and the output says so.

## Procedure

1. **Gather the inputs** and tag each F, I, A or U with a source.
2. **Run** `scripts/valuation.py --in <file>` (see `examples/input.json`).
3. **Read the range.** Which approach is lowest and highest, and why. The cost approach is what recreation costs; the market approach depends on comparability; the income approach depends on the benefit estimate, usually the weakest input.
4. **State the right** each value assumes, and how the value would change with a narrower or wider right.
5. **Pass the anchor on** to `data-price-setting`. State that the price must sit between the cost floor and the customer value, and who decides.

## Output

Header; the range in one line; table of approaches with basis; what is weak; the right assumed; handoff for the corridor; four-part handoff. Status Draft.

## Quality gate

- Every value comes from the script with its inputs shown.
- Discount rate and horizon are the user's, or the approach is skipped.
- Comparables carry a source and date or are excluded.
- The output states the right the value assumes.
- The range is not turned into a price.
