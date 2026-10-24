# Standard price book columns

One row per price line (one tier of one product, unit and term). CSV with a header row.

| Column | Required | Meaning |
|---|---|---|
| line_id | yes | Unique ID |
| product_id | yes (or dataset_id) | Stable product or SKU id |
| product_type | recommended | data_license, api_access, software, service, other |
| product_name | no | Business name |
| product_family | no | Family or category |
| dataset_id | data lines | The register dataset the product is built from or delivers (several separated by `;`). For a derivative product this is usually the Derived register entry. Candidates use DS-CAND-... until intake gives a real id |
| conferred_right | data lines | The right **granted to the customer** on this product: one of the nine rights, or blank when not stated. Not the right we hold; that is in the register. An older column named use_right is read as this one |
| data_form | no | `derived` (an aggregate, benchmark or insight built from the dataset; default) or `passthrough` (the customer receives the underlying data itself) |
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

For each data line the checker asks: do we hold what we need to confer this? It maps the line's `conferred_right` and `data_form` to the held rights the dataset must carry (`price-book-builder/references/rights-coverage.csv`) and reads those from the register. The basis is the worst result across the needed held rights.

| Basis | Meaning |
|---|---|
| N/A | The line carries no data or third-party content |
| Confirmed | Every needed held right is Granted or Conditional and Legal has confirmed it |
| Provisional | Anything else: no register, dataset or held right not in the register, Unknown, not yet confirmed, or no dataset or conferred right on the line |
| Contradicted | A needed held right is Prohibited in the register but Legal has not confirmed it |
| Blocked | Legal has confirmed a needed held right as Prohibited: we cannot confer this right |

## Modes

- strategy (default): Provisional and Contradicted lines are warnings. Use for pricing strategy, import review and intake planning.
- release: Provisional, Contradicted or missing-floor lines are errors. Use before a price book goes out for quoting.
- Blocked is an error in both modes.
