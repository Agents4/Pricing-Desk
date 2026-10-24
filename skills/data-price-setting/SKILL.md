---
name: data-price-setting
description: Work out what to charge for a product, data licence or API access before building a price book. Defines the value metric, builds a cost floor, a customer-value ceiling, market comparables and willingness-to-pay evidence into a price corridor, prices the extra rights a customer can be granted from the value they add, and tests the result. Use when launching a product, pricing a new customer right or API use, or when list prices lack a defensible basis.
---

# Data Price Setting

Answer one question: **what should we charge, and how sure are we?** The `price-book-builder` skill turns prices into a controlled price book; this skill finds the prices. Do this first.

This skill prices what we **grant** the customer: for a data product or API access, the rights they get (internal use, display, redistribution, retention, AI uses). The price assumes we may grant them. The product manager assesses that separately with the rights pack, so do not look for it here. The corridor method works for any product (API access, software, services, data); the right-by-right ladder applies to data and API products.

## Inputs to collect first

1. **Product**: what a buyer receives, delivery, refresh, history. For a data or API product, the right the customer is granted (`base_right`): what they may do with the data or responses, and for how long they may keep them.
2. **Rights to price as options** (data and API products): the broader rights customers ask for, such as display to third parties, redistribution, keeping and building on responses, and each AI use. Each is its own line with its own value case.
3. **Coverage**: the share of the market, volume or parties the product includes, the coverage the value estimates assume, and the coverage if it widens.
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
5. Does it line up with our costs, and with what the customer is allowed to do with it?

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

It returns the floor, the value-based price and cap, the market and willingness-to-pay anchors, a blended recommendation clamped between floor and cap, a list price that allows for the expected discount, prices for extra rights granted, sensitivities, a confidence rating, and flags. Report its numbers; do not recompute them by hand.

### 6. Read the result like a pricer

- **Not viable** (floor above value cap): no price works. Offer options: cut cost or scope, aim at a higher-value segment or right, spread cost across products, or re-check the value estimate.
- **Anchors differ by more than 1.5x**: find out why. Usually a wrong unit, a weak comp, or a value estimate that is too low or too high. Do not average away a disagreement.
- **Segment value-based prices differ by more than 1.5x**: consider fenced segment prices, with fences customers accept (use case, customer type, rights) and that cannot be arbitraged.
- **Priced at the floor or at the cap**: the evidence does not support the target. Say so.
- **Low confidence**: present as provisional, a range to test, with the next evidence to collect.

### 7. Price the granted-right ladder from value

Price each additional right the customer is granted as base price + capture share × the extra value per unit that right creates + its extra risk and supplier cost. Do not use standard multipliers. Treat each AI use as its own right, with its own value case. For API access, the base right is serving the customer's own live transactions; keeping responses, bulk extraction, rebuilding or reselling the data, and feeding AI are broader rights priced from their value, not at the per-call rate (see `price-book-builder/references/api-access-scope.md`). A customer who asks for API access only to collect data is asking for a data right.

### 8. Design the test

Set a pilot plan: three to five design partners across segments, the recommended price, and the outcome of each conversation (accept, counter, decline) with the reason. Define the decision rule up front: for example, "if fewer than half accept at list within the discount band, revisit the value metric before cutting the price." Feed the results back as willingness-to-pay points and rerun.

### 9. Hand off

Give the Pricing Council the memo, the CSV lines (Draft, single tier), and the open evidence list. Then use `price-book-builder` to add volume tiers, discount bands, terms, and the validation check. Reopen this skill when coverage changes, costs move more than 20 percent, or a pilot result disagrees with the corridor.

## Output format

1. **Headline**: the recommended realized price and list price per unit, the confidence, and the one thing that would change the answer.
2. **Corridor table** and **segments**.
3. **Granted-right ladder** with the reasoning for each step.
4. **Sensitivity table**, including the value of wider coverage.
5. **Flags and next evidence**.
6. **Pilot plan and decision rule.**
7. **Inputs and assumptions**, with each source.

## Rules

- Compute with `scripts/price_corridor.py`. Show the inputs next to the result.
- Say which right every price covers. A price without a stated right is not a price.
- Whether we may grant a right is the product manager's check in the rights pack. If the product manager tells you a right cannot be granted, drop that line; do not price around it.
- Label invented, illustrative, or assumed inputs. A worked example is not a quote.
- Do not present a price as certain when confidence is Low.
- Prices are proposals. The Pricing Council approves them and Finance confirms margin floors.
- Keep customer-specific data (individual willingness to pay, contract prices) out of general outputs.
