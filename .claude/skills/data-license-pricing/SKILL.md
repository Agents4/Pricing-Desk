---
name: data-license-pricing
description: Classify a data licensing request, or a request for API access that would collect data, by the rights the customer wants (internal use, display, redistribution, keeping responses, derivative products, AI use), price each right from the price book, and route the deal. Use when a customer asks to license a travel data product, asks for API access to pull data in bulk, or when pricing a custom data deal.
---

# Data License Pricing

Decide what the customer wants to do with the data, and what to charge for that. Price the right they are asking for, not just the volume. Pricing proposes; the Pricing Council approves. Whether we may grant a right is the product manager's call, using the rights pack.

## Inputs to collect first

1. **The request**: customer, dataset, feed or API, fields and coverage (markets, carriers, properties, time range), refresh frequency, delivery method, term.
2. **What the customer will do with it**, in their words: use it in their own business, show it to their own customers, resell it, combine it with other data, keep it, or use it for model training, retrieval, or agent grounding. For API requests, how long they will keep responses and how many calls they expect against how many bookings.
3. **Price book** (built with the `price-book-builder` skill): subscription prices, volume tiers, uplifts by right granted. If a product or right is not there, use the `data-price-setting` skill.
4. **Customer context**: current spend, products held, strategic importance.

If the customer will not say what they will do with the data, do not price it as internal use. Price the broadest plausible use, or decline.

## Process

1. **Restate the request** in a table: dataset or API, fields, coverage, frequency, term, delivery, intended use.
2. **Classify the right to grant** for each dataset: internal use only, internal analytics with outputs shared, display to third parties, redistribution, derivative data product, AI or model use (training, fine-tuning, retrieval, agent grounding). Quote the customer's own words that led to each classification and mark ambiguous cases.
3. **For API requests, apply the harvest test.** Read `../price-book-builder/references/api-access-scope.md`. If the purpose is to collect, keep, analyse in bulk, rebuild or feed AI, it is a data right: price at the data-licence rate for that right, with a minimum commitment, a retention term and audit rights, not at the per-call booking rate.
4. **Check sensitivity.** Flag personal data, customer-contributed data, or supplier-confidential fields that need removal, aggregation or consent. These are questions for the product manager and Legal.
5. **Price with code, from the price book or the `data-price-setting` skill.** Base subscription by coverage and frequency, volume tier, uplift for each right granted, term discount, and any approved exception band. Show the waterfall. Where no price book rule fits, say so and give a range with the reasoning, labeled as a proposal for the council.
6. **Route**: standard (inside the price book), Tier 1 or 2 (non-standard terms), Tier 3 (redistribution, AI use, keeping or rebuilding data, exclusivity).
7. **Ask the product manager** whether we may grant each right asked for. Send the dataset, the right and the deal. Do not wait on the answer to draft the price; do wait on it before quoting data products. The Pricing Council's note should say whether the rights pack has cleared the right.

## Output format

1. **Recommendation** (one line): standard quote, quote with conditions, or decline, the tier, and whether the product manager has cleared the right to grant.
2. **Request table** and **classification of the rights to grant** with quotes.
3. **Price proposal and waterfall**, line by line, with the right each line covers.
4. **Conditions to request**: retention limit, attribution, audit, volume fences, no resale to named competitors (a list for Legal, not contract language).
5. **Question for the product manager.**
6. **Inputs and assumptions used.**

## Rules

- Price by the right granted, not by volume alone.
- Treat AI and model use as its own right; never assume it is covered by internal use.
- API access priced at the booking rate buys the booking use only. Collecting data is a data right.
- Do not draft contract clauses or interpret contracts; list questions for Legal.
- Do not copy customer-specific terms or supplier-confidential details into general summaries.
- Pricing recommends. The Pricing Council approves the price; the product manager and Legal decide whether we may grant the right.
