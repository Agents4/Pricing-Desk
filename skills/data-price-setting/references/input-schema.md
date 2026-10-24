# Calculator input schema

All money fields use one currency. Unit means the value metric chosen in step 1.

| Field | Meaning |
|---|---|
| `product`, `currency`, `unit` | Labels. `unit` is the value metric, e.g. "market-year". |
| `dataset_id`, `product_id`, `product_type` | Optional. `dataset_id` marks a product that carries data, so rights apply. Leave it out for API access, software or services. |
| `illustrative` | `true` adds a warning banner to the report. Use for invented examples. |
| `base_right` | The right the corridor prices. Default `internal_use` for data products. |
| `eligible_rights` | Rights confirmed by Legal (Granted or Conditional). Priced as Confirmed. Optional. |
| `prohibited_rights` | Rights Legal has confirmed as Prohibited. Shown as Blocked, not priced. Optional. The base right cannot be in it. |
| (any other right) | For a data product, any right in `rights[]` that is in neither list is priced as Provisional. The report carries a "RIGHTS PROVISIONAL" banner when the base right is not confirmed. |
| `coverage.current` | Share of volume (or parties) the product can include today, from the register. |
| `coverage.reference` | The coverage the value estimates assume. |
| `coverage.resolved` | Coverage if open rights items are resolved. Used for the sensitivity. |
| `coverage.elasticity` | How strongly value follows coverage. 1 means proportional. |
| `cost.annual_fixed` | Yearly fixed cost to produce and run. |
| `cost.variable_per_unit` | Cost to serve one unit. |
| `cost.royalty_pct` | Share of price owed to suppliers or agencies. |
| `cost.min_margin_pct` | Finance's margin floor as a share of price. Royalty plus margin must be below 1. |
| `cost.cannibalization_per_unit` | Revenue lost on existing products per unit sold. |
| `discount.expected_list_to_realized` | Average discount from list. List = realized ÷ (1 − discount). |
| `value.max_capture_share` | The most of the customer's value you could ever charge for. Default 0.5. Sets the value cap. |
| `value.segments[]` | `name`, `customers` (addressable), `penetration` (share who buy, 0 to 1), `units_per_customer`, `value_per_customer_per_year` (at reference coverage), `capture_share`, `source` (estimate, interview, pilot, contract data). |
| `market.comps[]` | `name`, `unit_price`, `comparability` (0 to 1), `source`. |
| `wtp.points[]` | `max_price_per_unit`, optionally `segment`. |
| `weights` | Blend weights for `value`, `market`, `wtp`. Default 0.4, 0.3, 0.3, renormalized over available anchors. |
| `rights[]` | Extra rights to price: `right`, `incremental_value_per_unit`, `capture_share` (default 0.3), `incremental_cost_per_unit`, `basis`. |

Outputs: a Markdown report (also printed), optional JSON (`--json`), and optional price book lines (`--csv`) in the `price-book-builder` format, all Draft, single tier, with a note on lines whose rights are provisional.

Confidence score: anchors available (3 = 2 points, 2 = 1), value evidence quality (0.9 or more = 2, 0.6 or more = 1), willingness-to-pay points (15 or more = 2, 5 or more = 1), comparables (two or more at 0.6 average comparability = 1), minus 1 if anchors differ by more than 2x. High needs 6, Medium 3 to 5, Low below 3.
