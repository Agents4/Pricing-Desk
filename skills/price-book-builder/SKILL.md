---
name: price-book-builder
description: Build and maintain the price book for any product the pricing desk prices (API access, software, services, data licences). Sets list prices, floors, tiers and terms from cost, past deals, willingness-to-pay evidence and benchmarks, states on each data and API line what the customer may do with it, and checks consistency. Use when creating or revising a price book, or after importing an existing one.
---

# Price Book Builder

Create list prices that the desk can quote without a custom study each time. Prices come from evidence. Every data and API line says what the customer may do with what they buy (the **granted right**). That scope is part of the product: the same volume sells at a different price for internal use, for keeping the data, or for reselling it. Read `references/granted-scope.md`, and for API lines `references/api-access-scope.md`.

The desk assumes we hold the rights to grant what it prices. The product manager checks that separately with the rights pack. If an existing price book needs to be brought in first, use the `price-book-import` skill.

## What this skill needs

1. **Products and scope**: for each data or API product, what the customer receives and what they may do with it. If the scope is not known, price `internal_use` only and say so.
2. **Product attributes**: coverage, refresh frequency, history depth, delivery methods, volume, and number of current customers.
3. **Cost data** if available: cost to produce, source fees owed to suppliers, cost to serve (delivery and support). Ask Finance for the margin floor per family.
4. **Existing prices**: past data deals, quotes, and renewals, with realized price, volume, term, and use.
5. **Value evidence**: willingness-to-pay research, win and loss reasons, and customer value drivers (revenue enabled, cost avoided, time saved).
6. **Benchmarks**: public price lists and published information only, with sources. Never use competitor information obtained directly from a competitor.
7. **Goals and constraints**: penetration targets, strategic accounts, existing contract price protections.

If an input is missing, say what you cannot do without it and what you can do with assumptions that you label clearly.

## Process

### 1. Scope the price book

List products and the right each line grants. For API products, decide which of the five uses the line sells (own live transactions, short retention, bulk analysis, rebuilding or reselling, AI) and whether any customer is already using the API for a broader purpose than the price covers.

### 2. Choose the licensing units and structure

Decide, with the evidence, the unit that best tracks value and is easy to meter and audit: calls and bookings for API access, coverage (markets, carriers, properties), records or rows, queries, entities refreshed, or users. Prefer a simple structure: **base annual fee by dataset and coverage** plus a **volume component** where usage varies widely. Choose a delivery dimension (file, API, feed, dashboard) only when delivery cost or value differs. Note the metering source for each unit.

### 3. Build three price anchors per dataset family

For a new product or a new granted right, run the `data-price-setting` skill first and use its corridor, ladder, and confidence as the starting point for each line. Keep this step for refreshing anchors from realized deals.

Compute with code and show the inputs.

- **Floor**: cost to produce and serve, plus any supplier fee, plus the margin floor.
- **Reference**: realized prices from comparable past deals (median and range, by size band), and public benchmarks with sources.
- **Value ceiling**: customer value drivers or willingness-to-pay results, expressed as a share of the value created.

Set the list price inside the range between floor and ceiling, near the reference, and state the reasoning. Where evidence is thin, give a range and mark the line **hypothesis, to test**.

### 4. Set the granted-right ladder

The rights we grant the customer are priced as a ladder relative to `internal_use`. Broader rights (display to third parties, redistribution or resale, derivative products, keeping and reusing responses, AI training, fine-tuning, retrieval or grounding, evaluation) carry higher prices because they create more value and more risk. Derive each uplift from the evidence (value created, reduced exclusivity, supplier fees, risk) and show the logic. Do not apply standard multipliers without evidence. Treat each AI use as its own right. For API access, price collecting or keeping data at the data-licence rate for that right, not at the per-call rate.

### 5. Add tiers, fences, and terms

- Volume tiers with a stated tier model: `all_units` (the tier price applies to all units) or `graduated`
- Floor price per line, discount bands, and the approval tier each discount depth triggers (align with the approval matrix)
- Term discounts and renewal uplift caps
- Minimum commitments, overage rate, true-up, audit rights, and what happens when the licence ends
- Conditions that travel with the right: retention limit, attribution, audit, look-to-book or distinct-query fences, no resale to named competitors

### 6. Write the price book file

Create a CSV with these columns, one row per priced line: `line_id, product_id, product_type, conferred_right, delivery, unit, tier_min, tier_max, list_price, floor_price, currency, term_months, tier_model, status, version` (plus optional `product_name, product_family, annual_revenue, customers, notes`; see `price-book-import/references/standard-price-book.md`). `conferred_right` is for data and API lines: what the customer may do. Leave `tier_max` blank for the last tier. `status` is Existing, Draft or Proposed; only the Pricing Council sets Approved. Keep a second sheet or file for rationale: one row per product and right with the anchors, reasoning, evidence sources, and confidence.

### 7. Validate

Run `scripts/check_price_book.py --pricebook <price-book.csv> [--mode release]` from this skill's folder.

- **Strategy mode (default).** A missing floor, or a data or API line with no stated right, is a warning. Use this while building.
- **Release mode (`--mode release`).** Those two are errors. Run it before a price book goes out for quoting.

The script also checks tier overlaps and gaps, unit price versus volume, volume cliffs, floor above list, duplicates, and that broader rights are not priced below internal use. Fix every error before presenting. Then backtest: re-quote the last 12 months of deals at the new list prices and show the difference against realized prices, by customer size.

### 8. Prepare the decision

Summarize what the Pricing Council must decide: list prices, tiers, floors, approval triggers, fences, and the data and API products the product manager needs to clear (`product_rights_handoff.csv` from the importer, or the list of data and API lines). Note the next review date and what reopens pricing: a new product, a new right requested, or a change in how customers use an API.

### Worked example

`examples/price-book-example.csv` has data, API and software lines. L005 prices the Shopping API for live booking use only. L006 prices bulk retention of the same responses at a much higher rate, with a minimum commitment. Run it in release mode: no issues.

## Output format

1. **Headline**: lines priced by type, data and API lines by granted right, and the main uncertainty.
2. **Price book table** (summary) and the CSV file.
3. **Rationale table**: anchors, chosen price, reasoning, evidence, confidence.
4. **Granted-right ladder** with the reasoning for each uplift.
5. **Validation results** and **backtest**.
6. **Council decision list**, including data and API products for the product manager to clear.
7. **Inputs and assumptions used.**

## Rules

- Compute figures with code. Show inputs next to every result.
- Say which right every data and API line grants. A line without it is not a priced product.
- An API price covers the use it states. Collecting, keeping or reusing responses is a separate, higher-priced right.
- Never invent costs, benchmarks, or past prices. Mark assumptions and hypotheses.
- Benchmarks come from public or customer-supplied sources with citations; do not infer competitor prices from private conversations.
- Prices are proposals. The Pricing Council approves the price book, and Finance confirms the margin floors.
- Whether we may grant a right is the product manager's check in the rights pack. If it says a right cannot be granted, remove the line.
- Customer-specific past prices are used only to set the reference range; do not reproduce them in general outputs.
