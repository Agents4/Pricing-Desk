# Standard price book columns

One row per price line (one tier of one product, unit and term). CSV with a header row.

| Column | Required | Meaning |
|---|---|---|
| line_id | yes | Unique ID |
| product_id | yes | Stable product or SKU id |
| product_type | recommended | data_license, api_access, software, service, other |
| product_name | no | Business name |
| product_family | no | Family or category |
| conferred_right | data and API lines | The right **granted to the customer** on this product: what they may do with the data or API responses. One of the nine rights (internal_use, internal_analytics_shared_outputs, display_to_third_parties, redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding, ai_evaluation). Blank means not stated; treat it as internal_use only. An older column named use_right is read as this one |
| delivery | no | API, file, feed, dashboard, or blank |
| unit | yes | What the price is per (per 1,000 calls, per seat per year, per day) |
| tier_min, tier_max | yes | First and last unit of the tier. tier_max blank on the last tier. Tiers must not overlap |
| list_price | yes | Price per unit in this tier |
| floor_price | release | Lowest price the desk may accept. Blank is a warning in strategy mode and an error in release mode |
| currency, term_months | yes | |
| tier_model | no | all_units (the tier price applies to all units) or graduated. Default all_units |
| status | no | Existing, Draft, Proposed. Only the Pricing Council sets Approved |
| version | no | Price book version label |
| annual_revenue, customers | no | Used to rank the hand-off list. Keep on the first tier of a product to avoid double counting |
| notes | no | Inferences, flags, conditions that travel with the right (retention limit, attribution, audit) |

## Scope on data and API lines

The price is for a stated scope. `internal_use` is the narrowest and the base. Every broader right is a separate line priced above it. For API lines, keeping, collecting or reusing responses is a broader right than serving the customer's own transactions. See `price-book-builder/references/granted-scope.md` and `api-access-scope.md`.

## Modes

- strategy (default): a missing floor, or a data or API line with no stated right, is a warning. Use for pricing strategy and import review.
- release: those two are errors. Use before a price book goes out for quoting.
