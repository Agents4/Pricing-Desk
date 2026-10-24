---
name: packaging-design
description: Design tiers and packages for API access, software, services and data products. Sets tier structure on the chosen value metric, adds fences between tiers, writes good-better-best options with the granted right for each, and checks the result with the price book checker. Use when a new product needs packages, when tiers overlap or invite gaming, or when a price book is rebuilt.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill checks tiers by hand and says the checker was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, methodology/frameworks.md"
---

# Packaging design

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A package is a price, a unit, an allowance, a right and the fences that stop customers using a cheaper tier for a dearer use. See `references/frameworks.md` for named methods and their status.

## When to use

- A product needs tiers or packages after the metric is chosen (`value-metric-design`).
- Tiers overlap, have gaps, or let a heavy user sit in a light tier.
- A price book is being rebuilt or released.

Not for: the price level in each tier (`data-price-setting`), checking live customers against tiers (`api-usage-tier-fit`).

## Inputs

The value metric, the corridor or price points from `data-price-setting`, segments and what each does with the product, the rights to offer, usage distribution if known. Ask one question at a time.

## Procedure

1. **Segments to tiers.** Name the segments and what each needs. Give each tier a plain purpose.
2. **Allowances.** Set included amounts on the metric from usage data. If distribution is unknown, mark the boundaries A and name the data that would settle them.
3. **Fences.** What stops a heavy or different use from sitting in a light tier: usage caps, look-to-book bands, retention terms, rights granted, term, audit. Fences sit on the right and the metric, not on the account.
4. **Good, better, best.** Each option states the right it grants. A tier that allows retention, display, resale or AI use is a different right and a different price, never a larger allowance of the same one.
5. **Write the price book lines** in the standard columns with `conferred_right` on every data and API line.
6. **Check**: run `price-book-builder/scripts/check_price_book.py --pricebook <file>` and fix overlaps, gaps and prices that rise with volume.
7. **Test the fences** by asking what a customer wanting the best tier's use at the cheapest tier's price would do.

## Output

Header; the recommendation; a table of packages with unit, allowance, right, fences and price points; checker result; fence test; open questions; four-part handoff. Status Draft.

## Quality gate

- Every data and API package states its granted right.
- The checker ran without errors, or the output says it did not run.
- Boundaries based on assumed usage are tagged A with the data needed.
- Fences are on the metric or the right, not on a named account.
- No list price depends on an account (rule 13).
