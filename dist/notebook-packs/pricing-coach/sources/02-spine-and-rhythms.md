# The pricing spine and rhythms

---

## Document: methodology/spine.md

# The pricing spine

Status: adopted. Company values (names, thresholds, targets) come from the context library, never from this file.

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
Stage 1 and 2: pd-start, pd-setup. Stage 3: value-metric-design. Stage 4: analog-research. Stage 5: data-price-setting, price-book-builder, packaging-design, api-access-request. Stage 6: wtp-study-design, price-change-proposal. Stage 7: council-decision-pack. Stage 8: price-book-release, price-book-import. Stage 9: deal-desk-triage, account-price-fit, deal-desk-review, data-license-pricing. Stage 10: weekly-pricing-review, price-realization-analysis, api-usage-tier-fit. Stage 11: pd-ratchet, quarterly-price-review.

---

## Document: methodology/rhythms.md

# Pricing rhythms

Status: adopted. Time targets and thresholds are set by the company in the context library.

Every rhythm has an owner role, a trigger, inputs, the skills that run it, an output, the decision it supports, and a measure. Time targets are set by the company with Finance and Sales; this file names none.

## Daily: deal desk triage
- **Owner:** deal desk analyst.
- **Trigger:** each working day, and each new quote request.
- **Inputs:** open quote requests, price book, approval matrix, usage for the account if it is an API deal.
- **Skills:** deal-desk-triage, deal-desk-review, data-license-pricing, api-usage-tier-fit.
- **Output:** a triage list ranked by value and age, a deal package per request (price, granted right, approval route, counteroffer), and the exception log.
- **Account context:** when the account has an anchor deal, deal-desk-triage runs account-price-fit before the deal package is written. List price is not touched; only the deal price moves, inside the discount band.
- **Decision:** approve within authority, counter, or escalate.
- **Measure:** turnaround time against the agreed target, share of requests with a stated granted right, exception rate, discount against floor.

## Weekly: realization and API usage review
- **Owner:** pricing analyst.
- **Trigger:** same day each week.
- **Inputs:** invoices against list, discount and credit data, API usage by key and plan, deals closed.
- **Skills:** weekly-pricing-review, price-realization-analysis, api-usage-tier-fit.
- **Output:** one-page review: realized price against list and against last week, top leakage by cause, plans where usage and plan do not fit, harvest flags ("possible data collection, to confirm") with evidence, exceptions summary, three actions with owners.
- **Decision:** which leaks to chase, which accounts need a conversation, which flags go to the product manager.
- **Measure:** realization rate, leakage by cause, flags opened and closed, actions closed on time.

## Monthly: Pricing Council
- **Owner:** pricing lead (chair role; membership set by the company: Finance, Sales, Product, Legal as needed).
- **Trigger:** monthly, with a pack issued ahead of the meeting.
- **Inputs:** weekly reviews, exceptions, proposed price changes, new product proposals, rights hand-off status from the product manager, decision log.
- **Skills:** council-decision-pack, price-change-proposal, deal-desk-review (for large exceptions).
- **Output:** decision pack (decisions needed first, each with recommendation, options, numbers, risk, owner), then a decision log entry per decision.
- **Decision:** approve, reject or defer price changes, new constructs, approval-matrix changes and policy exceptions.
- **Measure:** decisions made in the meeting, decisions reopened, time from proposal to decision.

## Quarterly: price review
- **Owner:** pricing lead.
- **Trigger:** quarter end.
- **Inputs:** four monthly packs, competitive scan, WTP evidence, win and loss, realization trend.
- **Skills:** quarterly-price-review, competitive-price-scan, pricing-win-loss, analog-research.
- **Output:** review of every product line against value, market and realization; proposed changes for the Council; refreshed analog library.
- **Decision:** which lines to change, hold or retire next quarter.
- **Measure:** lines reviewed, changes proposed against changes approved, forecast against realized effect of changes made earlier.

## Annual: price book release and governance review
- **Owner:** pricing lead with Finance.
- **Trigger:** annual planning cycle.
- **Inputs:** quarterly reviews, cost changes, contract notice calendar, approval matrix and decision rights.
- **Skills:** price-book-release, price-book-import, approval-matrix-design (planned, not yet built), pd-ratchet.
- **Output:** the released price book (checker clean in release mode), change log, notice calendar, updated approval matrix, annual review of the OS itself (rules, skills, evals).
- **Decision:** the price book for the year and the governance for it.
- **Measure:** release checks passed first time, post-release corrections, lines without a stated granted right (target zero).

## Event-driven
| Event | Skills | Output |
|---|---|---|
| New product or construct with no price history | analog-research, data-price-setting, packaging-design, council-decision-pack | Corridor memo and Council pack. A pre-release review window of several weeks is a practitioner suggestion (see 04-frameworks.md); the company sets its own. |
| API access request for data collection | api-access-request, data-license-pricing | Priced at the data-licence rate with minimum commitment, retention term and audit, and a hand-off to the product manager |
| Harvest flag from the weekly review | api-usage-tier-fit | Evidence file; conversation plan; hand-off |
| Supplier cost or contract change | price-change-proposal, cost-to-serve-model (planned, not yet built) | Impact on floors; change proposal |
| Competitor move | competitive-price-scan, analog-research | Brief with sources and dates; recommendation only |
| Renewal with a price change | renewal-price-play (planned, not yet built), price-change-proposal | Notice-aware renewal plan |

## Research for new constructs
This is the rhythm the user asked for by name. Method (skill `analog-research`):
1. State the construct in one sentence: what is sold, to whom, metered how, granting what right.
2. Build an analog set in three rings: same industry (travel distribution, airline and hotel content and APIs), adjacent (other data and API businesses), outside (any business that charges for access, crawling, data or machine traffic).
3. For each analog collect public price points with URL and access date. Public information only.
4. Normalize: unit, metric, granted right, term, volume level.
5. Score comparability (high, medium, low) with the reason.
6. State what the analogs imply for the corridor, with confidence, and what they cannot tell us.
7. Add to the analog library with the access date; re-check on the quarterly review.
Vendor pricing pages are dated snapshots. The skill never presents an analog price as a recommendation.
