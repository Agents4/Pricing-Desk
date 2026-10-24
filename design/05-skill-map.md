# Phase 1c: Skill map

Status: draft for confirmation.

Existing skill names stay (installs keep working). New system skills use the `pd-` prefix. Commands stay under `/pricing:`.

## Existing nine (kept; each gets a stage, a rhythm and an eval case)
| Skill | Stage | Rhythm | Change in the OS build |
|---|---|---|---|
| data-price-setting | 5 | event: new product; quarterly | Add framework citations; link to analog-research |
| price-book-builder | 5 | annual; event | Gate to price-book-release |
| price-book-import | 8 | annual; first setup | Unchanged |
| data-license-pricing | 9 | daily; event | Unchanged |
| deal-desk-review | 9 | daily | Becomes the engine under deal-desk-triage |
| price-realization-analysis | 10 | weekly | Becomes an input to weekly-pricing-review |
| api-usage-tier-fit | 10 | weekly | Same; flags feed the weekly review |
| price-change-proposal | 6, 7 | monthly; event | Output feeds council-decision-pack |
| wtp-study-design | 4, 6 | quarterly; event | Add VW and GG guidance with sources |

## Wave 1: everything except specialist skills (19 new skills)
Decision by the owner: the former wave 2 is part of wave 1. Built in five internal batches, each batch usable on its own and each skill with an eval.

| Batch | Skill | Stage | What it does |
|---|---|---|---|
| 1 Foundation | pd-start | all | Entry point: reads context, asks what the user needs, routes to a skill or rhythm |
| 1 | pd-setup | 1, 2 | Interviews one question at a time and writes the context library (09-context-library.md): governance, approval matrix, floors, product catalog, deal structures, systems, hand-off route, guardrails, writing style. Writes only what the user says; Unknown otherwise |
| 1 | pd-ratchet | 11 | Learning loop: turn a miss into a rule, skill change or eval case |
| 1 | pd-skill-author | maintenance | Adds or changes a skill under the OS conventions |
| 2 Deal desk | deal-desk-triage | 9 | Daily: ranks open requests, runs the right skill per request, produces the exception log |
| 2 | account-price-fit | 9 | Account context for a deal: anchor economics, incentives paid, cost to serve, give-get plan, precedent check (08-account-price-fit.md) |
| 2 | api-access-request | 9 | API access requests, including data collection: use, harvest test, data-licence pricing with minimum, retention and audit |
| 3 Monitor | weekly-pricing-review | 10 | Weekly: one-page review from realization and API usage outputs |
| 3 | pricing-win-loss | 10 | Win and loss review for pricing causes |
| 4 Govern and release | council-decision-pack | 7 | Monthly: decisions first, options, numbers, risks, rights hand-off status |
| 4 | pricing-stakeholder-review | 7 | Review of a proposal through lenses: Finance, Sales, customer procurement, product manager and Legal, competitor, engineering and metering |
| 4 | price-book-release | 8 | Release checklist: checker in release mode, change log, notice calendar, hand-offs |
| 4 | rights-handoff | 8, 9 | Builds the hand-off list for the product manager; reads back the answer |
| 5 Research and design | analog-research | 4 | Research for new constructs from public sources, with URL and access date |
| 5 | competitive-price-scan | 4 | Dated, sourced competitor price checks; public information only |
| 5 | value-metric-design | 3 | Choose what to charge on (for example look-to-book and value adds): visible to the customer, meterable by us |
| 5 | packaging-design | 5 | Tiers, good-better-best, fences, API and data packages |
| 5 | data-product-valuation | 3, 5 | Cost, market and income approaches to valuing a data product |
| 5 | quarterly-price-review | rhythm | Quarterly review of every line against value, market and realization |

## Wave 3: specialist
renewal-price-play, cost-to-serve-model, elasticity-estimate, pricing-health-check (our extension, not a published framework), price-change-postmortem, approval-matrix-design.

## Sizing
Wave 1: 19 new skills plus tooling and evals. Existing nine: light edits. Total after wave 1: 28 skills. Wave 3 adds six later: 34. Each skill 60 to 150 lines, detail in `references/`.
