# Calculator input schema

All money fields use one currency. Unit means the value metric chosen in step 1.

**The tool has no company defaults.** A value marked *required* stops the run (exit 2) when it is missing. A value marked *optional* switches its check off and the report says so. Where the value comes from is in the last column. If the source is blank, the value is Unknown: ask, do not fill it in.

| Field | Meaning | Required? / source |
|---|---|---|
| `product`, `currency`, `unit` | Labels. `unit` is the value metric, e.g. "market-year". | Required |
| `product_id`, `product_family`, `product_type` | `product_type` is data_license, api_access, software, service or other. Data and API products grant a scope to the customer (`base_right`, `rights[]`). Leave the rights out for software and services. | Optional |
| `illustrative` | `true` adds a warning banner. Use for invented examples. | Optional |
| `base_right` | The right **granted to the customer** that the corridor prices. If it is missing for a data or API product, the report says `internal_use` was assumed (A). | Optional, but state it |
| `term_months` | Term the lines are priced for. Missing: the CSV leaves it blank. | Optional |
| `coverage.current`, `coverage.reference` | Share of the market the product covers today, and the share the value estimates assume. Give both or neither. | Optional |
| `coverage.elasticity` | How strongly value follows coverage. 1 means proportional. | Required when coverage is used |
| `coverage.resolved` | Coverage if it widens. Used for the sensitivity. | Optional |
| `coverage.max_factor` | Cap on the coverage uplift. Missing: no cap, and the report flags an uplift above 1. | Optional; company value |
| `cost.annual_fixed`, `cost.variable_per_unit` | Yearly fixed cost and cost to serve one unit. | Required; Finance figures |
| `cost.royalty_pct` | Share of price owed to suppliers or agencies. | Required. Enter 0 only if there is no supplier or agency share; blank is Unknown and the script stops |
| `cost.min_margin_pct` | The margin floor **as a share of price** (not of cost): floor = unit cost ÷ (1 − royalty − margin). | Required; `pricing-governance.md`, Unknown if blank |
| `cost.cannibalization_per_unit` | Revenue lost on existing products per unit sold. | Required. Enter 0 only if you know there is none |
| `discount.expected_list_to_realized` | Average discount from list. List = realized ÷ (1 − discount). Missing: the list price is **not computed** and the report says Unknown. | Optional; `pricing-governance.md` |
| `value.max_capture_share` | The most of the customer's value the company would ever charge for. Sets the value cap. | **Required**; `pricing-governance.md` or the Council |
| `value.segments[]` | `name`, `customers`, `penetration` (0 to 1), `units_per_customer`, `value_per_customer_per_year` (at reference coverage), `capture_share`, `source` (estimate, interview, pilot, contract data). | Required |
| `market.comps[]` | `name`, `unit_price` (above 0), `comparability` (0 to 1; an analog scored 1 to 5 in the library is entered as score ÷ 5), `source`. | Optional |
| `wtp.points[]` | `max_price_per_unit` (above 0), optionally `segment`. | Optional |
| `wtp.min_points` | The fewest points the study design says it needs before they are blended. Missing: points are shown, not blended. | Optional; study design or Council |
| `weights` | Blend weights for `value`, `market`, `wtp`. Missing: equal weights across the anchors available, and the report says so. | Optional; company value |
| `review.divergence_flag`, `review.divergence_stop` | Cutoffs (as ratios) for flagging anchors that disagree. Missing: the ratio is shown, not judged. | Optional; company values |
| `review.segment_spread_flag` | Ratio of the highest to the lowest segment value-based price that suggests fenced prices. | Optional; company value |
| `review.weak_comparability` | Average comparability below which the market anchor is context, not a price. | Optional; company value |
| `rights[]` | Extra rights to grant: `right`, `incremental_value_per_unit`, `capture_share`, `incremental_cost_per_unit`, `basis`. | `capture_share` **required** for each right; the Council's or requester's call |
| `sensitivity` | Sizes of the sensitivity tests: `capture`, `cost`, `demand`, `market` as shares. Missing: the tool's own test sizes, shown in each scenario label. These are test sizes, not company thresholds. | Optional |

Outputs: a Markdown report (also printed), optional JSON (`--json`), and optional price book lines (`--csv`) in the `price-book-builder` format, all Draft, single tier. Each line carries the right it grants (`conferred_right`) with `right_basis=assumed` unless the input says otherwise, and notes what is still missing (term, keeping terms, Unknown list price).

**Confidence.** The tool lists the evidence (anchors in the blend, share of units on estimate-only value, willingness-to-pay points, comparables and their comparability). It rates a result **Low** when only the value anchor is available or all value evidence is estimates, and otherwise says *Not rated*, because the company has set no confidence criteria. If the Council sets criteria, add them here and in `pricing-governance.md`.
