# Phase 1b: Rhythms

Status: draft for confirmation.

Every rhythm has an owner role, a trigger, inputs, the skills that run it, an output, the decision it supports, and a measure. Time targets are proposed defaults to agree with Finance and Sales; they are not benchmarks.

## Daily: deal desk triage
- **Owner:** deal desk analyst.
- **Trigger:** each working day, and each new quote request.
- **Inputs:** open quote requests, price book, approval matrix, usage for the account if it is an API deal.
- **Skills:** deal-desk-triage (new), deal-desk-review, data-license-pricing, api-usage-tier-fit.
- **Output:** a triage list ranked by value and age, a deal package per request (price, granted right, approval route, counteroffer), and the exception log.
- **Account context:** when the account has an anchor deal, deal-desk-triage runs account-price-fit before the deal package is written. List price is not touched; only the deal price moves, inside the discount band.
- **Decision:** approve within authority, counter, or escalate.
- **Measure:** turnaround time against the agreed target, share of requests with a stated granted right, exception rate, discount against floor.

## Weekly: realization and API usage review
- **Owner:** pricing analyst.
- **Trigger:** same day each week.
- **Inputs:** invoices against list, discount and credit data, API usage by key and plan, deals closed.
- **Skills:** weekly-pricing-review (new), price-realization-analysis, api-usage-tier-fit.
- **Output:** one-page review: realized price against list and against last week, top leakage by cause, plans where usage and plan do not fit, harvest flags ("possible data collection, to confirm") with evidence, exceptions summary, three actions with owners.
- **Decision:** which leaks to chase, which accounts need a conversation, which flags go to the product manager.
- **Measure:** realization rate, leakage by cause, flags opened and closed, actions closed on time.

## Monthly: Pricing Council
- **Owner:** pricing lead (chair role; membership set by the company: Finance, Sales, Product, Legal as needed).
- **Trigger:** monthly, with a pack issued ahead of the meeting.
- **Inputs:** weekly reviews, exceptions, proposed price changes, new product proposals, rights hand-off status from the product manager, decision log.
- **Skills:** council-decision-pack (new), price-change-proposal, deal-desk-review (for large exceptions).
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
- **Skills:** price-book-release (new), price-book-import, approval-matrix-design (wave 3), pd-ratchet.
- **Output:** the released price book (checker clean in release mode), change log, notice calendar, updated approval matrix, annual review of the OS itself (rules, skills, evals).
- **Decision:** the price book for the year and the governance for it.
- **Measure:** release checks passed first time, post-release corrections, lines without a stated granted right (target zero).

## Event-driven
| Event | Skills | Output |
|---|---|---|
| New product or construct with no price history | analog-research, data-price-setting, packaging-design, council-decision-pack | Corridor memo and Council pack. A pre-release review window of several weeks is a practitioner suggestion (see 04-frameworks.md); the company sets its own. |
| API access request for data collection | api-access-request, data-license-pricing | Priced at the data-licence rate with minimum commitment, retention term and audit, and a hand-off to the product manager |
| Harvest flag from the weekly review | api-usage-tier-fit | Evidence file; conversation plan; hand-off |
| Supplier cost or contract change | price-change-proposal, cost-to-serve-model (wave 3) | Impact on floors; change proposal |
| Competitor move | competitive-price-scan, analog-research | Brief with sources and dates; recommendation only |
| Renewal with a price change | renewal-price-play (wave 3), price-change-proposal | Notice-aware renewal plan |

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
