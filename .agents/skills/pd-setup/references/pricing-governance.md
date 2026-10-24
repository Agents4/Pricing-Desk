---
type: context
name: pricing-governance
client: "{{client}}"
status: template
last_reviewed: "{{date}}"
---

# Pricing governance: {{client}}

> The source for every approval route, threshold and floor. Skills read this file and never use a default. Blank means Unknown. Run `pd-setup`.

## Pricing Council
**Chair:** Unknown
**Members and roles:** Unknown
**Cadence and quorum:** Unknown
**Pack lead time:** Unknown

## Decision rights
| Decision | Proposes | Approves | Consulted |
|---|---|---|---|
| New product or construct price | Unknown | Unknown | Unknown |
| List price change | Unknown | Unknown | Unknown |
| Floor price change | Unknown | Unknown | Unknown |
| Deal below list within band | Unknown | Unknown | Unknown |
| Deal below floor (exception) | Unknown | Unknown | Unknown |
| Approval-matrix change | Unknown | Unknown | Unknown |

## Discount bands and margin floors
> The margin floor is a share of **price** (floor price = unit cost ÷ (1 − royalty − margin floor)), not a markup on cost. State it that way.

| Product family | Discount band the deal desk may approve alone | Margin floor | Who approves above |
|---|---|---|---|
| Unknown | Unknown | Unknown | Unknown |

## Deal desk
**Authority:** Unknown
**Target response times (proposals until agreed):** Unknown
**Escalation path:** Unknown
**Override authority:** Unknown

## Account-level limits
**Largest total discount an account may reach across all its products:** Unknown
**Missing band means:** every discount escalates to the escalation path above (fail closed).

## Review parameters
> Every number a skill or script uses to flag, rank or window data. Skills read these and never use a default. Blank means Unknown: the skill states the figure it found and does not judge it. Set by the Council or the chair.

| Parameter | Used by | Value |
|---|---|---|
| Trend windows (months) | `api-usage-tier-fit`, `weekly-pricing-review` | Unknown |
| Realization window for the quarterly review (months) | `quarterly-price-review` | Unknown |
| Backtest window for a new price book (months) | `price-book-builder` | Unknown |
| Price-change scenario horizon (months) | `price-change-proposal` | Unknown |
| Minimum comparable deals to cite | `deal-desk-review` | Unknown |
| Minimum deals for a win-loss pattern | `pricing-win-loss` | Unknown |
| Customer and action list length | `price-change-proposal`, `price-realization-analysis`, `weekly-pricing-review`, `api-usage-tier-fit` | Unknown |
| Renewal review window (days) | `api-usage-tier-fit`, `deal-desk-triage` | Unknown |
| Cost-change threshold that reopens a price | `data-price-setting` | Unknown |
| Reconciliation tolerance between billing and price book | `price-realization-analysis`, `weekly-pricing-review` | Unknown |
| Freshness limit for analogs and competitor scans (days) | `analog-research`, `competitive-price-scan` | Unknown |
| Pilot design partners | `data-price-setting` | Unknown |
| Expected average discount from list, by family | `data-price-setting` (`discount.expected_list_to_realized`) | Unknown |
| Most of customer value we would charge for (`max_capture_share`) | `data-price-setting` | Unknown |
| Blend weights for value, market and willingness to pay | `data-price-setting` | Unknown |
| Anchor divergence: flag and stop (ratios) | `data-price-setting` | Unknown |
| Segment spread that suggests fenced prices (ratio) | `data-price-setting` | Unknown |
| Comparability below which a market anchor is context only | `data-price-setting` | Unknown |
| Minimum willingness-to-pay points to blend | `data-price-setting`, `wtp-study-design` | Unknown |
| Cap on the coverage uplift | `data-price-setting` | Unknown |
| Look-to-book per segment (median) | `api-access-request`, `api-usage-tier-fit` | Unknown |
| Harvest screen: multiple of the segment median that flags | `api-access-request`, `api-usage-tier-fit` | Unknown |
| Harvest screen: distinct-query ratio that flags | `api-access-request`, `api-usage-tier-fit` | Unknown |
| Harvest screen: share of responses kept (retention) that flags | `api-access-request`, `api-usage-tier-fit` | Unknown |
| Harvest screen: minimum monthly volume before a ratio is judged | `api-access-request`, `api-usage-tier-fit` | Unknown |
