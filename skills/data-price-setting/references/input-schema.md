# Calculator input schema

All money fields use one currency. Unit means the value metric chosen in step 1.

| Field | Meaning |
|---|---|
| `product`, `currency`, `unit` | Labels. `unit` is the value metric, e.g. "market-year". |
| `product_id`, `product_type` | Optional. `product_type` is data_license, api_access, software, service or other. Data and API products grant a scope to the customer (`base_right`, `rights[]`). Leave the rights out for software and services. |
| `illustrative` | `true` adds a warning banner to the report. Use for invented examples. |
| `base_right` | The right **granted to the customer** that the corridor prices: what the customer may do with the data or API responses. Default `internal_use` for data and API products. |
| `coverage.current` | Share of the market, volume or parties the product can include today. |
| `coverage.reference` | The coverage the value estimates assume. |
| `coverage.resolved` | Coverage if it widens (new sources, new markets). Used for the sensitivity. |
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
| `rights[]` | Extra rights to grant, each priced from the value it adds: `right`, `incremental_value_per_unit`, `capture_share` (default 0.3), `incremental_cost_per_unit`, `basis`. |

Outputs: a Markdown report (also printed), optional JSON (`--json`), and optional price book lines (`--csv`) in the `price-book-builder` format, all Draft, single tier. Each line carries the right it grants (`conferred_right`).

Confidence score: anchors available (3 = 2 points, 2 = 1), value evidence quality (0.9 or more = 2, 0.6 or more = 1), willingness-to-pay points (15 or more = 2, 5 or more = 1), comparables (two or more at 0.6 average comparability = 1), minus 1 if anchors differ by more than 2x. High needs 6, Medium 3 to 5, Low below 3.
