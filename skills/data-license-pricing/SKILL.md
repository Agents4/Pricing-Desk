---
name: data-license-pricing
description: Classify a data licensing request by the rights the customer wants (internal use, redistribution, derivative products, AI use), check that we hold what we need to grant them in the data rights register, flag conflicts, and recommend a price from the price book. Prices provisionally when rights are not yet confirmed, and says clearly what is cleared to quote. Use when a customer asks to license a travel data product or when pricing a custom data deal.
---

# Data License Pricing

Decide what is being licensed, whether we hold the rights to grant it, and what to charge. Pricing proposes; Legal confirms rights. A provisional price is always available so the deal and the rights work can move together; it is not cleared to quote until Legal confirms.

## Inputs to collect first

1. **The request**: customer, dataset or feed, fields and coverage (markets, carriers, properties, time range), refresh frequency, delivery method, term.
2. **Rights the customer wants** (what we would confer), in their words, including whether they will show the data to their own customers, resell it, combine it with other data, or use it for model training, retrieval, or agent grounding.
3. **Data rights register** (built with the `dataset-intake-register` skill): for each dataset, the source and the rights **we hold**, with evidence references and restrictions. A held right counts as confirmed only when `legal_confirmed = Yes` and status is Granted or Conditional. Treat every other row, and every missing row, as unknown (provisional). The register says what we may do; it does not say what the customer may do.
4. **Price book** (built with the `price-book-builder` skill): dataset subscription prices, volume tiers, uplifts by conferred right. If the dataset has no register entry, price provisionally from the price book or the `data-price-setting` skill and start an intake.
5. **Customer context**: current spend, products held, strategic importance.

If the rights register is missing or silent on a dataset, price it provisionally and report "rights unknown, provisional price, escalate to Legal". List what Legal needs to confirm. If Legal has confirmed that we do not hold a right we would need to grant what the customer asks for, do not price it.

## Process

1. **Restate the request** in a table: dataset, fields, coverage, frequency, term, delivery, intended use.
2. **Classify the right to confer** for each dataset: internal use only, internal analytics with derived outputs shared, redistribution or display to third parties, derivative data product, AI or model use (training, fine-tuning, retrieval, agent grounding). Quote the customer's own words that led to each classification and mark ambiguous cases.
3. **Check that we hold what we need.** For each dataset and right to confer, look up the held rights it needs in `price-book-builder/references/rights-coverage.csv` (for example, letting the customer show the product to its own customers needs us to hold both shared outputs and display on the dataset). Read each needed held right from the register: Confirmed (we hold it, or hold it with conditions), Provisional (unknown or unconfirmed), Contradicted (evidence says we do not hold it, Legal has not confirmed) or Blocked (Legal confirmed we do not hold it). The basis of the request is the worst of them. Include the register entry references. Conditions on a held right travel into the customer terms.
4. **Check privacy and sensitivity.** Flag personal data, customer-contributed data, or supplier-confidential fields that require removal, aggregation, or consent.
5. **Price with code, from the price book or the `data-price-setting` skill**. Label each line's rights basis: base subscription by coverage and frequency, volume tier, uplift for each conferred right, term discount, and any approved exception band. Show the waterfall. Where no price book rule fits, say so and give a range with the reasoning, labeled as a proposal for the council. Mark the whole proposal **Provisional** when any held right it relies on is not Confirmed.
6. **Route**: standard (inside price book and rights), Tier 1 or 2 (non-standard terms), Tier 3 (redistribution, AI use, exclusivity, or a rights conflict).
7. **Draft the Legal escalation note**: the dataset, the proposed use, the register entry, the question, and the deadline.

## Output format

1. **Recommendation** (one line): standard quote, quote with conditions, provisional price while Legal confirms, or decline, and the tier. State whether it is cleared to quote.
2. **Request table** and **classification of the rights to confer** with quotes.
3. **Rights check table** (right to confer, held rights needed, register status, basis).
4. **Price proposal and waterfall** with the rights basis of each line.
5. **Conditions and licensing terms to request from Legal** (not contract language).
6. **Legal escalation note.**
7. **Inputs and assumptions used.**

## Rules

- Never state that we may grant a right unless the register says we hold what it needs; if unsure, say "unknown", price it as Provisional, and escalate.
- Price by the right conferred, not by volume alone.
- Do not draft contract clauses or interpret contracts; list questions for Legal.
- Treat AI and model use as its own right, both held and conferred; never assume it is covered by internal use.
- Do not copy customer-specific terms or supplier-confidential details into general summaries.
- Pricing approves the price; Legal confirms the rights before any quote is sent to a customer. A provisional price may be used inside the desk, for strategy and for deciding where Legal time goes.
