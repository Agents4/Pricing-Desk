---
name: data-license-pricing
description: Classify a data licensing request by the rights the customer wants (internal use, display, redistribution, keeping responses, derivative products, AI use), price each right from the price book, and route the deal. Use when a customer asks to license a travel data product, when pricing a custom data deal, or when `api-access-request` has decided the purpose and the right needs a price.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted data and says the check was not run."
metadata:
  version: "1.1.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Data License Pricing

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Decide what the customer wants to do with the data, and what to charge for that. Price the right they are asking for, not just the volume. Pricing proposes; the Pricing Council approves. Whether we may grant a right is the product manager's call, using the rights pack.

## When to use

- A customer asks to license a travel data product.
- A custom data deal needs pricing by the right granted.
- `api-access-request` has found that an API request needs a wider right (keeping, analysing, reselling or AI use of responses) and the right needs a price.

Not for: a new or expanded API access request (`api-access-request` owns it, and calls this skill to price the right), a standard quote inside the price book (`deal-desk-review`), or whether we hold a right (`rights-handoff`; the product manager answers that).

## Inputs

Context library files read: `pricing-governance.md`, `product-catalog.md`, `rights-handoff.md`. If a file still says `status: template`, treat its values as Unknown.

1. **The request**: customer, dataset, feed or API, fields and coverage (markets, carriers, properties, time range), refresh frequency, delivery method, term.
2. **What the customer will do with it**, in their words: use it in their own business, show it to their own customers, resell it, combine it with other data, keep it, or use it for model training, retrieval, or agent grounding. For API requests, how long they will keep responses and how many calls they expect against how many bookings.
3. **Price book** (built with the `price-book-builder` skill): subscription prices, volume tiers, uplifts by right granted. If a product or right is not there, use the `data-price-setting` skill.
4. **Customer context**: current spend and products held. Strategic importance, if raised, moves a deal price only through `account-price-fit` and the deal desk, never the list or the corridor (rule 13).

If the customer will not say what they will do with the data, do not price it as internal use. Price the broadest plausible use, or decline.

## Procedure

1. **Restate the request** in a table: dataset or API, fields, coverage, frequency, term, delivery, intended use.
2. **Classify the right to grant** for each dataset: internal use only, internal analytics with outputs shared, display to third parties, redistribution, derivative data product, AI or model use (training, fine-tuning, retrieval, agent grounding). Quote the customer's own words that led to each classification and mark ambiguous cases.
3. **For an API request that reached this skill, check the purpose first.** Read `../price-book-builder/references/api-access-scope.md`. If the purpose is to collect, keep, analyse in bulk, rebuild or feed AI, it is a data right: price at the data-licence rate for that right, with a minimum commitment, a retention term and audit rights, not at the per-call booking rate.
4. **Check sensitivity.** Flag personal data, customer-contributed data, or supplier-confidential fields that need removal, aggregation or consent. These are questions for the product manager and Legal.
5. **Price with code, from the price book or the `data-price-setting` skill.** Base subscription by coverage and frequency, volume tier, uplift for each right granted, term discount, and any approved exception band. Show the waterfall. Where no price book rule fits, say so and give a range with the reasoning, labeled as a proposal for the council.
6. **Route** by the approval matrix in `pricing-governance.md`: standard (inside the price book) or non-standard. Redistribution, AI use, keeping or rebuilding data and exclusivity are the broad-right cases. If the matrix is not filled, the route is Unknown.
7. **Hand off to the product manager.** Add the product and the right to the hand-off list (see `rights-handoff` when available, otherwise `rights-handoff.md` in the context library). Never say whether we hold the right. Draft the price meanwhile; label it pending the rights answer. The Council note says whether the right has been cleared.

## Output

1. **Recommendation** (one line): standard quote, quote with conditions, or decline, the approval route, and whether the product manager has cleared the right to grant (Unknown until they answer).
2. **Request table** and **classification of the rights to grant** with quotes.
3. **Price proposal and waterfall**, line by line, with the right each line covers.
4. **Conditions to request**: retention limit, attribution, audit, volume fences, no resale to named competitors (a list for Legal, not contract language).
5. **Question for the product manager.**
6. **Inputs and assumptions used.**

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Price by the right granted, not by volume alone.
- Treat AI and model use as its own right; never assume it is covered by internal use.
- API access priced at the booking rate buys the booking use only. Collecting data is a data right.
- Do not draft contract clauses or interpret contracts; list questions for Legal.
- Do not copy customer-specific terms or supplier-confidential details into general summaries.
- Pricing recommends. The Pricing Council approves the price; the product manager and Legal decide whether we may grant the right.
