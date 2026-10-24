---
name: deal-desk-review
description: Review a non-standard quote or deal for API access, premium software, or data products. Builds the price waterfall, checks guardrails, assigns an approval tier, flags risks, and drafts an approval memo with counteroffers. Use when a sales rep or deal desk analyst submits a deal for pricing review.
---

# Deal Desk Review

Turn a deal request into a decision-ready package for the approver. You recommend; a named person approves. Never send anything to a customer.

## Inputs to collect first

Ask for anything missing before analyzing. Do not guess.

1. **Deal request**: customer, segment, products and families (API, software, data), volumes or seats, term, requested price or discount, requested non-standard terms, deadline, competing alternative if known.
2. **Price book**: current list prices, tiers, units, and fences (file or pasted table).
3. **Approval matrix**: tier triggers, approvers, margin floors per product family.
4. **Comparable deals**: recent deals from the deal log with similar product, size, and segment (at least 5 if available).
5. **Customer context**: current spend, usage history, renewal date, open disputes, strategic notes.

If the price book or approval matrix is not provided, say so at the top of your answer and use the placeholder tiers from the desk blueprint (Tier 0 up to 10 percent discount; Tier 1 beyond band; Tier 2 above 250,000 USD total contract value, multi-year, or cross-family bundle; Tier 3 above 1 million USD, below floor, MFN, exclusivity, or data redistribution rights). Label them as placeholders.

## Process

1. **Normalize the request.** Restate the deal in a table: product, unit, quantity, list price, requested price, term, ramp, commit, overage.
2. **Compute the waterfall with code.** Use a script on the provided data; do not do arithmetic in prose. Show list value, each discount layer (volume, term, bundle, special), net price, total contract value, and annualized value. For usage-based pricing, model commit, expected usage, and overage at low, base, and high usage.
3. **Check guardrails.** For each line: discount versus band, price versus floor, margin versus family floor (if cost data is supplied), term and payment terms versus standard, and non-standard clauses (MFN, exclusivity, price protection, redistribution or AI-use rights for data). For data lines, state the rights basis (Confirmed, Provisional, Contradicted, Blocked) from the register; a Provisional line can be priced and reviewed but is flagged as not cleared to quote.
4. **Compare with similar deals.** Show where this deal sits against comparables on net price per unit and discount depth. Flag if it would become the new low.
5. **Assign the approval tier** by the first rule tripped, and name the rule.
6. **Flag risks.** Precedent risk, cross-family cannibalization, metering or unit ambiguity, supplier-data rights, revenue recognition questions for Finance, legal terms for Legal.
7. **Draft two or three counteroffers** that trade value for concessions: for example a larger commit for a deeper tier, a longer term for a lower rate, a smaller starting scope with a ramp, or removal of a clause. Show the waterfall for each.

## Output format

Deliver in this order, kept short enough to read in two minutes:

1. **Recommendation** (one line): approve as requested, approve with changes, counter, or decline; plus the tier.
2. **Deal summary table** and **waterfall table**.
3. **Guardrail results**: pass or fail per check, with the numbers.
4. **Comparables**: small table.
5. **Risks and open questions** for Finance, Legal, Product.
6. **Counteroffers** with their waterfalls.
7. **Approval memo** (under 150 words) the analyst can paste into the approval request: ask, rationale, tier, risks, recommendation.
8. **Inputs and assumptions used**: files, date ranges, assumptions, and anything missing.

## Rules

- Compute figures with code and show their source; never estimate in prose.
- Do not invent list prices, floors, or approval rules. If missing, say so.
- Do not approve exceptions or tell the customer anything. Output is for the approver.
- Use customer-specific prices only for this request; do not copy them into general summaries.
- Treat competitor pricing as valid only if the rep supplied it with a source; mark it unverified otherwise.
- If a clause or data right looks like a legal question, escalate it as an open question rather than interpreting it.
