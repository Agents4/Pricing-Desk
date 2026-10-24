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

## Wave 1: foundation and rhythms (first build)
| Skill | Stage | What it does |
|---|---|---|
| pd-start | all | Entry point: reads context, asks what the user needs, routes to a skill or rhythm |
| pd-setup | 1, 2 | Builds the context library: business info, approval matrix, margin floors, product catalog, price book location, rights hand-off location |
| deal-desk-triage | 9 | Daily: ranks open requests, runs the right skill per request, produces the exception log |
| weekly-pricing-review | 10 | Weekly: one-page review from realization and API usage outputs |
| council-decision-pack | 7 | Monthly: decisions first, options, numbers, risks, rights hand-off status |
| price-book-release | 8 | Release checklist: checker in release mode, change log, notice calendar, hand-offs |
| analog-research | 4 | Research for new constructs from public sources, with URL and access date |
| rights-handoff | 8, 9 | Builds the hand-off list for the product manager; reads back the answer |
| pd-ratchet | 11 | Learning loop: turn a miss into a rule, skill change or eval case |

## Wave 2: depth
value-metric-design (3), packaging-design (5), api-access-request (9), data-product-valuation (5), competitive-price-scan (4), quarterly-price-review (monthly to quarterly), pricing-win-loss (10), pricing-stakeholder-review (7, with lenses: Finance, Sales, customer procurement, product manager and Legal, competitor, engineering and metering), pd-skill-author (OS maintenance).

## Wave 3: specialist
renewal-price-play, cost-to-serve-model, elasticity-estimate, pricing-health-check (our extension, not a published framework), price-change-postmortem, approval-matrix-design.

## Sizing
Wave 1: 9 new skills plus tooling and evals. Existing nine: light edits. Total after wave 1: 18 skills. After wave 3: about 33. Each skill 60 to 150 lines, detail in `references/`.
