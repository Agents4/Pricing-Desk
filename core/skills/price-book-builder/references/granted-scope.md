# What we grant the customer: the conferred right

Every data and API line in the price book says what the customer may do with what they buy. This is the **conferred right**. It is part of the product and part of the price. Two customers who pay for the same volume but may do different things with the data are not buying the same product.

The pricing desk assumes we hold the rights to grant what we price. The product manager checks that separately with the rights pack (see `product_rights_handoff.csv` from the importer). Do not look for the register here.

## The nine rights

| conferred_right | What the customer may do |
|---|---|
| internal_use | Use the data or API responses in their own business, for their own transactions and decisions. Nothing leaves the company. This is the base. |
| internal_analytics_shared_outputs | Analyse it internally and share the results (charts, reports, aggregates) outside the company, without the underlying data. |
| display_to_third_parties | Show the data to their own customers or partners, for example in a booking screen or a dashboard. No extraction. |
| redistribution_resale | Pass the data on, or sell it, to others. |
| derivative_data_product | Build their own data product, index or benchmark from it. |
| ai_training | Train a model on it. |
| ai_fine_tuning | Fine-tune a model on it. |
| ai_retrieval_grounding | Feed it to an AI system at answer time (retrieval, grounding, agents). |
| ai_evaluation | Use it to test or benchmark a model. |

Each AI use is its own right. Do not bundle them.

## Pricing rules

- Price `internal_use` first. Every broader right is a separate line priced above it for the same product, delivery, unit and tier. The checker fails a broader right priced below internal use.
- A broader right is worth more because it creates more value for the customer (a new revenue line), costs us exclusivity and market position, and carries more risk. Derive each uplift from evidence. Do not apply a standard multiplier.
- A line without a stated right is not a priced product yet. In strategy mode the checker warns; in release mode it fails.
- A right that keeps or collects data carries `minimum_commitment`, `retention_term` and `audit_right` as price book columns (the checker warns, and errors in release mode, when they are missing).
- Conditions travel with the right: attribution, no re-sale to named competitors, retention period, audit. Put them in `notes` and in the contract, and price the audit and enforcement cost.
- A customer asking for a right the price book does not list is a new line: use `data-price-setting`, do not improvise a discount.

See `api-access-scope.md` for API lines.
