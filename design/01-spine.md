# Phase 1: Spine

Status: draft for confirmation.

The spine is the life of a price, from the first question to the lessons after release. Eleven stages. Each has inputs, outputs and a gate: the check that must pass before the next stage starts. Stages marked (R) are rhythm stages: they repeat on a calendar, not once per product.

| # | Stage | Inputs | Outputs | Gate |
|---|---|---|---|---|
| 1 | Intake and scope | Request, product brief, requester, deadline | Scoped pricing question: product, unit, customer type, decision wanted, owner | Question is one decision, an owner and a date are named |
| 2 | Fact base | Cost to serve, volumes, current price book, past deals, usage data | Fact sheet with every number tagged F (fact), I (inference), A (assumption), U (unknown) | Every number used later has a tag and a source; unknowns listed |
| 3 | Value and segments | Customer use cases, value drivers, segment definitions | Value metric choice, customer value cap per segment | Value metric is something the customer can see and we can meter |
| 4 | Research | Analogs (same industry, adjacent, outside), public price points, WTP data | Analog table with URL and access date, comparability score, WTP evidence | Every price point has a source and a date; confidence stated |
| 5 | Price architecture | Stages 2 to 4 | Corridor (floor, cap, market reference, WTP), tiers, packaging, granted-right ladder for data and API lines, fences | Corridor computed by script; every data or API line states the right it grants; floor not above list |
| 6 | Test | Draft architecture, past deals | Backtest on past deals or WTP study design; expected revenue and margin effect | Test result or an explicit "untested" tag; downside case shown |
| 7 | Govern | Architecture, test, exceptions list, rights hand-off status | Decision pack for the Pricing Council; decision log entry | Decision recorded with owner, date and conditions; nothing customer-facing before approval |
| 8 | Release | Approved architecture | Price book that passes the checker in release mode; change log; notice calendar; hand-offs to billing, quote tool, product manager | Checker clean in release mode; rights hand-off sent; effective dates and notice terms checked |
| 9 (R) | Deal desk | Quote request, price book, approval matrix | Deal package: price, scope, approval route, counteroffer if needed | Floor respected or exception approved; granted right stated; harvest test run on API requests |
| 10 (R) | Monitor | Invoices, usage, deals closed, win and loss | Realization report, API usage review, leakage and harvest flags | Flags carry evidence and a to-confirm tag; each flag has an owner |
| 11 (R) | Learn | Decisions, outcomes, misses | Learning log entries, updated rules and analog library, annual review | Every miss is traced to a stage and a rule or skill is changed or the reason for not changing is written |

## Notes on the flow
- The loop is 9 to 10 to 11 and back to 2 and 3. A product enters at stage 1 once; after release it lives in the rhythms.
- Stage 4 (research) can be entered from any stage. A new construct (a product with no internal price history) starts there.
- Stage 7 is the only place a price becomes official. Stages 9 and 10 can recommend an exception or a change but cannot approve one.
- Rights are not a stage. The pricing OS prices the scope it grants and produces a hand-off list (stage 8 and 9). The product manager answers whether we hold the rights, in the Rights Desk. The Council pack reports the hand-off status.

## First skills by stage (see 05-skill-map.md for the full map)
Stage 1 and 2: pd-start, pd-setup. Stage 3: value-metric-design (wave 2). Stage 4: analog-research. Stage 5: data-price-setting, price-book-builder, packaging-design (wave 2), api-access-request (wave 2). Stage 6: wtp-study-design, price-change-proposal. Stage 7: council-decision-pack. Stage 8: price-book-release, price-book-import. Stage 9: deal-desk-triage, deal-desk-review, data-license-pricing. Stage 10: weekly-pricing-review, price-realization-analysis, api-usage-tier-fit. Stage 11: pd-ratchet, quarterly-price-review (wave 2).
