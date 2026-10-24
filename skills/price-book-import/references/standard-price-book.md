# Standard price book columns

One row per price line (one tier of one product, unit and term). CSV with a header row.

| Column | Required | Meaning |
|---|---|---|
| line_id | yes | Unique ID |
| product_id | yes (or dataset_id) | Stable product or SKU id |
| product_type | recommended | data_license, api_access, software, service, other |
| product_name | no | Business name |
| product_family | no | Family or category |
| dataset_id | data lines | Link to the data rights register. Candidates use DS-CAND-... until intake gives a real id |
| use_right | data lines | One of the nine use rights, or blank when not stated |
| delivery | no | API, file, feed, dashboard, or blank |
| unit | yes | What the price is per (per 1,000 calls, per seat per year, per day) |
| tier_min, tier_max | yes | First and last unit of the tier. tier_max blank on the last tier. Tiers must not overlap |
| list_price | yes | Price per unit in this tier |
| floor_price | release | Lowest price the desk may accept. Blank is a warning in strategy mode and an error in release mode |
| currency, term_months | yes | |
| tier_model | no | all_units (the tier price applies to all units) or graduated. Default all_units |
| status | no | Existing, Draft, Proposed. Only the Pricing Council sets Approved |
| version | no | Price book version label |
| annual_revenue, customers | no | Used to rank rights questions by what they put at risk. Keep on the first tier of a product to avoid double counting |
| rights_relevance | no | Required (data), Possible (API that may carry third-party content), None. Default by product_type |
| notes | no | Inferences and flags |

## Rights basis (computed by the checker, not stored)

| Basis | Meaning |
|---|---|
| N/A | The line carries no data or third-party content |
| Confirmed | Register says Granted or Conditional and Legal has confirmed |
| Provisional | Anything else: no register, not in register, Unknown, or not yet confirmed |
| Contradicted | Register evidence says Prohibited but Legal has not confirmed |
| Blocked | Legal has confirmed Prohibited |

## Modes

- strategy (default): Provisional and Contradicted lines are warnings. Use for pricing strategy, import review and intake planning.
- release: Provisional, Contradicted or missing-floor lines are errors. Use before a price book goes out for quoting.
- Blocked is an error in both modes.
