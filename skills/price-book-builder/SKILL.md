---
name: price-book-builder
description: Build and maintain the price book for any product the pricing desk prices (API access, software, services, data licences). Sets list prices, floors, tiers and terms from cost, past deals, willingness-to-pay evidence and benchmarks, links data lines to the rights register, and checks consistency. Provisional pricing is allowed before Legal confirms rights; a release check gates quoting. Use when creating or revising a price book, or after importing an existing one.
---

# Price Book Builder

Create list prices that the desk can quote without a custom study each time. Prices come from evidence. Lines that carry data are tied to the data rights register. Pricing can run before Legal responds: such lines are labelled Provisional, and a separate release check keeps unconfirmed lines from being quoted.

This skill covers every product type: `data_license`, `api_access`, `software`, `service`, `other`. The rights register applies only to lines that carry data or third-party content. If an existing price book needs to be brought in first, use the `price-book-import` skill.

## What this skill needs

1. **Data rights register** (workbook with `Datasets` and `Use_Rights` sheets), for lines that carry data. Optional. If it is missing or incomplete, price the lines as **Provisional** and use the `dataset-intake-register` skill to start filling it, in the order the exposure report suggests. Only use rights with `legal_confirmed = Yes` and status Granted or Conditional are Confirmed. Legal has confirmed Prohibited rights are Blocked and are not priced.
2. **Dataset attributes**: coverage, refresh frequency, history depth, delivery methods, volume, and number of current customers.
3. **Cost data** if available: cost to produce, source fees owed to suppliers, cost to serve (delivery and support). Ask Finance for the margin floor per family.
4. **Existing prices**: past data deals, quotes, and renewals, with realized price, volume, term, and use.
5. **Value evidence**: willingness-to-pay research, win and loss reasons, and customer value drivers (revenue enabled, cost avoided, time saved).
6. **Benchmarks**: public price lists and published information only, with sources. Never use competitor information obtained directly from a competitor.
7. **Goals and constraints**: penetration targets, strategic accounts, existing contract price protections.

If an input is missing, say what you cannot do without it and what you can do with assumptions that you label clearly.

## Process

### 1. Scope the price book

List products, datasets and use rights in scope. For data lines, cross-check each with the register (if there is one) and sort into: **Confirmed** (Granted or Conditional, Legal confirmed), **Provisional** (Unknown, not in the register, or not yet confirmed), **Contradicted** (evidence says Prohibited, Legal has not confirmed) and **Blocked** (Legal confirmed Prohibited). Price Confirmed and Provisional lines. Price Contradicted lines only as a labelled scenario. Do not price Blocked lines. Give the open question behind each Provisional and Contradicted line, so intake and Legal time go where the revenue is.

### 2. Choose the licensing units and structure

Decide, with the evidence, the unit that best tracks value and is easy to meter and audit: coverage (markets, carriers, properties), records or rows, queries, entities refreshed, or users. Prefer a simple structure: **base annual fee by dataset and coverage** plus a **volume component** where usage varies widely. Choose a delivery dimension (file, API, feed, dashboard) only when delivery cost or value differs. Note the metering source for each unit.

### 3. Build three price anchors per dataset family

For a new product or a new use right, run the `data-price-setting` skill first and use its corridor, ladder, and confidence as the starting point for each line. Keep this step for refreshing anchors from realized deals.

Compute with code and show the inputs.

- **Floor**: cost to produce and serve, plus any supplier fee, plus the margin floor.
- **Reference**: realized prices from comparable past deals (median and range, by size band), and public benchmarks with sources.
- **Value ceiling**: customer value drivers or willingness-to-pay results, expressed as a share of the value created.

Set the list price inside the range between floor and ceiling, near the reference, and state the reasoning. Where evidence is thin, give a range and mark the line **hypothesis, to test**.

### 4. Set the use-right ladder

Use rights are priced as a ladder relative to `internal_use`. Broader rights (display to third parties, redistribution or resale, derivative products, AI training, fine-tuning, retrieval or grounding, evaluation) carry higher prices because they create more value and more risk. Derive each uplift from the evidence (value created, reduced exclusivity, supplier fees, risk) and show the logic. Do not apply standard multipliers without evidence. Treat each AI use as its own right.

### 5. Add tiers, fences, and terms

- Volume tiers with a stated tier model: `all_units` (the tier price applies to all units) or `graduated`
- Floor price per line, discount bands, and the approval tier each discount depth triggers (align with the approval matrix)
- Term discounts and renewal uplift caps
- Minimum commitments, overage rate, true-up, audit rights, and what happens when the licence ends
- Conditions that travel with Conditional rights

### 6. Write the price book file

Create a CSV with these columns, one row per priced line: `line_id, product_id, product_type, dataset_id, use_right, delivery, unit, tier_min, tier_max, list_price, floor_price, currency, term_months, tier_model, status, version` (plus optional `annual_revenue, customers, rights_relevance, notes`; see `price-book-import/references/standard-price-book.md`). `dataset_id` and `use_right` are for data lines only. Leave `tier_max` blank for the last tier. `status` is Existing, Draft or Proposed; only the Pricing Council sets Approved. Keep a second sheet or file for rationale: one row per dataset and use right with the anchors, reasoning, evidence sources, and confidence.

### 7. Validate

Run `scripts/check_price_book.py --pricebook <price-book.csv> [--register <register.xlsx>] [--exposure-csv exposure.csv]` from this skill's folder.

- **Strategy mode (default).** Provisional and Contradicted rights are warnings, a missing register is allowed, and the exposure report ranks the rights questions by what they put at risk. Use this for pricing strategy and planning intake.
- **Release mode (`--mode release`).** Provisional, Contradicted and missing-floor lines are errors. Run it before a price book goes out for quoting. A line that fails is not cleared to quote.
- Blocked (Legal confirmed Prohibited) is an error in both modes.

Fix every error before presenting. The script also checks floors, tier overlaps and gaps, unit price versus volume, volume cliffs, and that broader use rights are not priced below internal use. Then backtest: re-quote the last 12 months of data deals at the new list prices and show the difference against realized prices, by customer size.

### 8. Prepare the decision

Summarize what the Pricing Council must decide: list prices, tiers, floors, approval triggers, and any blocked items. Note the next review date, and which register events (new dataset, contract change, new use right) reopen pricing.

## Output format

1. **Headline**: lines priced by rights basis (Confirmed, Provisional, Contradicted, Blocked, N/A), revenue in Provisional lines, and the main uncertainty.
2. **Price book table** (summary) and the CSV file.
3. **Rationale table**: anchors, chosen price, reasoning, evidence, confidence.
4. **Use-right ladder** with the reasoning for each uplift.
5. **Rights exposure and intake priority** (from the exposure report), with the open questions and owners.
6. **Validation results** and **backtest**.
7. **Council decision list.**
8. **Inputs and assumptions used.**

## Rules

- Compute figures with code. Show inputs next to every result.
- Rights are a basis, not a gate on analysis. Price Provisional lines, label them, and report what is provisional. Never present a Provisional line as cleared to quote; the release check decides that.
- Never price a right Legal has confirmed as Prohibited.
- Never invent costs, benchmarks, or past prices. Mark assumptions and hypotheses.
- Benchmarks come from public or customer-supplied sources with citations; do not infer competitor prices from private conversations.
- Prices are proposals. The Pricing Council approves the price book, and Finance confirms the margin floors.
- Every data line links to a `dataset_id` and use right. Re-run the check after any register or price change.
- Customer-specific past prices are used only to set the reference range; do not reproduce them in general outputs.
