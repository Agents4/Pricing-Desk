---
name: deal-desk-review
description: Review a non-standard quote or deal for API access, premium software, or data products. Builds the price waterfall, checks guardrails, assigns an approval tier, flags risks, and drafts an approval memo with counteroffers. Use when a sales rep or deal desk analyst submits a deal for pricing review.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted data and says the check was not run."
metadata:
  version: "1.1.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Deal Desk Review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Turn a deal request into a decision-ready package for the approver. You recommend; a named person approves. Never send anything to a customer.

## When to use

- A rep or deal desk analyst submits a non-standard quote for API access, premium software or data products.
- A requested discount is outside the band, or a non-standard term is asked for.
- New or expanded API access is requested (the purpose question applies).

Not for: a new list price (`data-price-setting`), a price change for the Council (`price-change-proposal`), a data licence request (`data-license-pricing`), or new or expanded API access (`api-access-request`). For an account with an anchor deal, run `account-price-fit` first and record any concession in the exception log.

## Inputs

Context library files read: `pricing-governance.md` (approval matrix, bands, floors), `product-catalog.md`, `deal-structures.md`. If a file still says `status: template`, treat its values as Unknown.

Ask for anything missing before analyzing. Do not guess.

1. **Deal request**: customer, segment, products and families (API, software, data), volumes or seats, term, requested price or discount, requested non-standard terms, deadline, competing alternative if known.
2. **Price book**: current list prices, tiers, units, and fences (file or pasted table).
3. **Approval matrix**: tier triggers, approvers, margin floors per product family.
4. **Comparable deals**: recent deals from the deal log with similar product, size, and segment (the minimum number is in the review parameters in `pricing-governance.md`; Unknown if blank, so say how many you found).
5. **Customer context**: current spend, usage history, renewal date, open disputes, strategic notes.
6. **For new or expanded API access: the purpose.** What will the customer do with the responses, and for how long will they keep them? Ask when the request does not say. Booking and serving their own traffic is the standard API use. Collecting, storing or analysing data in bulk, rebuilding it, reselling it or feeding AI is a data right and is priced as one (see `price-book-builder/references/api-access-scope.md`).

If the price book or approval matrix is missing or still a template, say so at the top of the answer. Mark the approval route Unknown, name `pricing-governance.md` as the file to fill, and offer `pd-setup`. Do not use remembered or example tiers or thresholds. Still compute the waterfall and the guardrails that need only the price book.

## Procedure

1. **Normalize the request.** Restate the deal in a table: product, unit, quantity, list price, requested price, term, ramp, commit, overage.
2. **Compute the waterfall with code.** Use a script on the provided data; do not do arithmetic in prose. Show list value, each discount layer (volume, term, bundle, special), net price, total contract value, and annualized value. For usage-based pricing, model commit, expected usage, and overage at low, base, and high usage.
3. **Check guardrails.** For each line: discount versus band, price versus floor, margin versus family floor (if cost data is supplied), term and payment terms versus standard, and non-standard clauses (MFN, exclusivity, price protection, redistribution or AI-use rights for data). For data and API lines, state the right the quote grants the customer (`conferred_right`) and check it matches the price: a data right sold at an API booking rate, or a retention or bulk-use request on a per-call price, is a fail. Whether we may grant the right is the product manager's question; list it as an open question.
4. **Compare with similar deals.** Show where this deal sits against comparables on net price per unit and discount depth. Flag if it would become the new low.
5. **Assign the approval route** from the approval matrix in `pricing-governance.md` by the first rule tripped, and name the rule. If the matrix is not filled, write Unknown.
6. **Flag risks.** Precedent risk, cross-family cannibalization, metering or unit ambiguity, supplier-data questions for the product manager, revenue recognition questions for Finance, legal terms for Legal.
7. **Draft two or three counteroffers** that trade value for concessions: for example a larger commit for a deeper tier, a longer term for a lower rate, a smaller starting scope with a ramp, or removal of a clause. Show the waterfall for each.

## Output

Deliver in this order, kept short enough to read in two minutes:

1. **Recommendation** (one line): approve as requested, approve with changes, counter, or decline; plus the approval route.
2. **Deal summary table** and **waterfall table**.
3. **Guardrail results**: pass or fail per check, with the numbers.
4. **Comparables**: small table.
5. **Risks and open questions** for Finance, Legal, Product.
6. **Counteroffers** with their waterfalls.
7. **Approval memo** (one short paragraph) the analyst can paste into the approval request: ask, rationale, tier, risks, recommendation.
8. **Inputs and assumptions used**: files, date ranges, assumptions, and anything missing.

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute figures with code and show their source; never estimate in prose.
- Do not invent list prices, floors, or approval rules. If missing, say so.
- Do not approve exceptions or tell the customer anything. Output is for the approver.
- Use customer-specific prices only for this request; do not copy them into general summaries.
- Treat competitor pricing as valid only if the rep supplied it with a source; mark it unverified otherwise.
- If a clause or data right looks like a legal question, escalate it as an open question rather than interpreting it.
