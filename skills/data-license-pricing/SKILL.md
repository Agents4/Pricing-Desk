---
name: data-license-pricing
description: Classify a data licensing request by use right (internal use, redistribution, derivative products, AI use), check it against the data rights register, flag conflicts, and recommend a price from the price book. Use when a customer asks to license a travel data product or when pricing a custom data deal.
---

# Data License Pricing

Decide what is being licensed, whether the desk is allowed to license it, and what to charge. Pricing proposes; Legal confirms rights.

## Inputs to collect first

1. **The request**: customer, dataset or feed, fields and coverage (markets, carriers, properties, time range), refresh frequency, delivery method, term.
2. **Intended use** in the customer's words, including whether they will show the data to their own customers, resell it, combine it with other data, or use it for model training, retrieval, or agent grounding.
3. **Data rights register** (built with the `dataset-intake-register` skill): for each dataset, the source, the use-right matrix, evidence references, and restrictions. Only use rights with `legal_confirmed = Yes` and status Granted or Conditional count as allowed. Treat every other row, and every missing row, as unknown.
4. **Price book** (built with the `data-price-book-builder` skill): dataset subscription prices, volume tiers, use-right uplifts. If the dataset has no register entry, start an intake instead of quoting.
5. **Customer context**: current spend, products held, strategic importance.

If the rights register is missing or silent on a dataset, do not price it. Report "rights unknown, escalate to Legal" and list what is needed.

## Process

1. **Restate the request** in a table: dataset, fields, coverage, frequency, term, delivery, intended use.
2. **Classify the use right** for each dataset: internal use only, internal analytics with derived outputs shared, redistribution or display to third parties, derivative data product, AI or model use (training, fine-tuning, retrieval, agent grounding). Quote the customer's own words that led to each classification and mark ambiguous cases.
3. **Check rights against the register.** For each dataset and use right: allowed, allowed with conditions, not allowed, or unknown. Include the register entry reference.
4. **Check privacy and sensitivity.** Flag personal data, customer-contributed data, or supplier-confidential fields that require removal, aggregation, or consent.
5. **Price from the price book with code**: base subscription by coverage and frequency, volume tier, use-right uplift, term discount, and any approved exception band. Show the waterfall. Where no price book rule fits, say so and give a range with the reasoning, labeled as a proposal for the council.
6. **Route**: standard (inside price book and rights), Tier 1 or 2 (non-standard terms), Tier 3 (redistribution, AI use, exclusivity, or a rights conflict).
7. **Draft the Legal escalation note**: the dataset, the proposed use, the register entry, the question, and the deadline.

## Output format

1. **Recommendation** (one line): standard quote, quote with conditions, escalate to Legal, or decline, and the tier.
2. **Request table** and **use-right classification** with quotes.
3. **Rights check table.**
4. **Price proposal and waterfall**, or the reason none can be given.
5. **Conditions and licensing terms to request from Legal** (not contract language).
6. **Legal escalation note.**
7. **Inputs and assumptions used.**

## Rules

- Never state that a use is permitted unless the register says so; if unsure, say "unknown" and escalate.
- Price by use right, not by volume alone.
- Do not draft contract clauses or interpret contracts; list questions for Legal.
- Treat AI and model use as its own use right; never assume it is covered by internal use.
- Do not copy customer-specific terms or supplier-confidential details into general summaries.
- Pricing approves the price; Legal confirms the rights before any quote is sent.
