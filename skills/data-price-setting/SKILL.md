---
name: data-price-setting
description: Work out what to charge for a data product or data licence before building a price book. Defines the value metric, builds a cost floor, a customer-value ceiling, market comparables and willingness-to-pay evidence into a price corridor, prices extra use rights from the value they add, and tests the result. Use when launching a data product, pricing a new use right, or when list prices lack a defensible basis.
---

# Data Price Setting

Answer one question: **what should we charge, and how sure are we?** The `price-book-builder` skill turns prices into a controlled price book; this skill finds the prices. Do this first.

The register decides what can be quoted. This skill decides what a product is worth. You can run it before Legal responds: rights not yet confirmed are priced as **Provisional**, and the result says so. A right Legal has confirmed as Prohibited is shown as Blocked and not priced. The corridor method works for any product (API access, software, services, data); the use-right ladder applies only to data.

## Inputs to collect first

1. **Product and dataset**: the `dataset_id`, what a buyer receives, delivery, refresh, history.
2. **Rights basis** for data products, from the register (`Effective_Rights` or the Use_Rights sheet): `eligible_rights` are Granted or Conditional with `legal_confirmed = Yes`; `prohibited_rights` are confirmed Prohibited; every other right is Provisional. If there is no register yet, everything is Provisional; start `dataset-intake-register` in parallel. If the product depends on secondary processing that is still open, treat the affected parties as excluded from the confirmed coverage and show the provisional coverage separately. Skip this input for products that carry no data.
3. **Coverage** from the register's `Coverage_Summary` (share of parties and volume that can be included), the coverage the value estimates assume, and the coverage if open items are resolved.
4. **Cost**: fixed annual cost to produce and run, variable cost per unit, supplier royalties or revenue share (as a percent of price), cannibalization of existing products, and Finance's margin floor.
5. **Customers and value**: segments, how many, how much each would use, and what the product is worth to each per year. Record the source of each estimate: estimate, interview, pilot, or contract data.
6. **Market**: comparable products with a public or customer-supplied price and a comparability score from 0 to 1.
7. **Willingness-to-pay points**: the highest price each interviewed buyer would pay, from a study or interviews.

If an input is missing, say what you cannot do without it. Run the calculator with what exists and let it report low confidence. Do not invent values.

## Process

### 1. Choose the value metric (what the price scales with)

Test each candidate unit against five questions. Choose the one that passes the most, and say which it fails.

1. Does it rise with the value the customer gets?
2. Can we meter it reliably and let the customer verify it?
3. Can the customer predict their bill?
4. Is it hard to game or split to avoid paying?
5. Does it line up with our costs and with the register's use rights?

Typical candidates for travel data: markets or routes covered, queries or records, entities tracked (properties, carriers, agencies), users, or a share of the revenue the data enables. Keep one metric per product; add a second only when value and cost split clearly.

### 2. Build the cost floor

Floor per unit = (fixed cost spread over expected units + variable cost + cannibalization) ÷ (1 − royalty percent − margin floor). It is the deal-desk walk-away price, not a target. If expected units are uncertain, run the demand sensitivity.

### 3. Quantify customer value

For each segment, estimate the yearly value one buyer gets at the usage you expect. Follow `references/value-quantification.md`. Start from a measurable outcome (cost avoided, revenue enabled, time saved), not from the data's features. State the capture share (the part of the value you charge for). Typical starting points are 10 to 30 percent; customers need a clear return to buy. Mark the source of each figure, and push estimates toward interviews and pilots.

Value depends on coverage. Express value at a reference coverage and let the calculator scale it to the coverage you can actually deliver.

### 4. Gather market and willingness-to-pay evidence

- Comparables: public price lists, published rate cards, customer-supplied quotes. Score comparability honestly: same buyer, same unit, same coverage, same rights. Weak comps are context.
- Never use competitor pricing obtained from a competitor, and never share your pricing with a competitor.
- Willingness to pay: five points are the minimum to use, fifteen to rely on. For a proper study, use `wtp-study-design`.

### 5. Run the corridor calculator

Write the inputs as JSON (see `references/input-schema.md` and `examples/air-shopping-insights.json`) and run:

`python scripts/price_corridor.py --in input.json --md report.md --csv lines.csv`

It returns the floor, the value-based price and cap, the market and willingness-to-pay anchors, a blended recommendation clamped between floor and cap, a list price that allows for the expected discount, prices for extra use rights, sensitivities, a confidence rating, and flags. Report its numbers; do not recompute them by hand.

### 6. Read the result like a pricer

- **Not viable** (floor above value cap): no price works. Offer options: cut cost or scope, aim at a higher-value segment or right, spread cost across products, or re-check the value estimate.
- **Anchors differ by more than 1.5x**: find out why. Usually a wrong unit, a weak comp, or a value estimate that is too low or too high. Do not average away a disagreement.
- **Segment value-based prices differ by more than 1.5x**: consider fenced segment prices, with fences customers accept (use case, customer type, rights) and that cannot be arbitraged.
- **Priced at the floor or at the cap**: the evidence does not support the target. Say so.
- **Low confidence**: present as provisional, a range to test, with the next evidence to collect.

### 7. Price the use-right ladder from value

Price each additional right as base price + capture share × the extra value per unit that right creates + its extra risk and supplier cost. Do not use standard multipliers. A right Legal has confirmed as Prohibited is shown as blocked, with no price. A right that is not yet confirmed is priced and labelled Provisional. Treat each AI use as its own right, with its own value case.

### 8. Design the test

Set a pilot plan: three to five design partners across segments, the recommended price, and the outcome of each conversation (accept, counter, decline) with the reason. Define the decision rule up front: for example, "if fewer than half accept at list within the discount band, revisit the value metric before cutting the price." Feed the results back as willingness-to-pay points and rerun.

### 9. Hand off

Give the Pricing Council the memo, the CSV lines (Draft, single tier), and the open evidence list. Then use `price-book-builder` to add volume tiers, discount bands, terms, and the validation check. Reopen this skill when the register changes coverage or rights, costs move more than 20 percent, or a pilot result disagrees with the corridor.

## Output format

1. **Headline**: the recommended realized price and list price per unit, the confidence, and the one thing that would change the answer.
2. **Corridor table** and **segments**.
3. **Use-right ladder** with the rights basis (Confirmed or Provisional) and the reasoning for each step, and the blocked rights.
4. **Sensitivity table** and the value of resolving open rights items.
5. **Flags and next evidence**.
6. **Pilot plan and decision rule.**
7. **Inputs and assumptions**, with each source.

## Rules

- Compute with `scripts/price_corridor.py`. Show the inputs next to the result.
- Price unconfirmed rights as Provisional and say so in the headline. Never price a right Legal has confirmed as Prohibited. Never present a Provisional price as cleared to quote.
- Label invented, illustrative, or assumed inputs. A worked example is not a quote.
- Do not present a price as certain when confidence is Low.
- Prices are proposals. The Pricing Council approves them and Finance confirms margin floors.
- Keep customer-specific data (individual willingness to pay, contract prices) out of general outputs.
