# Pricing Desk OS

An operating system for the pricing desk of a travel-technology (GDS) company. It prices API access, premium software, services and data products, with proven frameworks, a calendar of rhythms and 28 skills. Prices, customers and agreements in the examples are invented.

The desk prices what the customer is **granted**. For data and API lines each price states the right it covers. Whether we hold that right is the product manager's call, assessed in the separate **Rights Desk** package (Agents4/Rights-Desk). The two meet at one hand-off list (`product_rights_handoff.csv`).

Company-specific values (Council, approval thresholds, discount bands, margin floors, notice terms, systems, the hand-off route) live only in the company's context library, filled by `pd-setup`. The product ships no company threshold, band, floor, margin, window, currency or term: scripts stop and say what is missing rather than fill one in. Blank means Unknown. Two analysis conveniences remain and are labelled in the output: equal weights when no weighting is supplied, and the sizes of the sensitivity tests in the price corridor (overridable with a `sensitivity` block).

## Start

Install the Gemini CLI extension, or use the skills where your company runs them (`adapters/google/README.md`):

```
gemini extensions install https://github.com/Agents4/Pricing-Desk
```

Then ask for `pd-start` (`/pricing:start`): it shows what is due today, this week and this month. First time: `pd-setup` (`/pricing:setup`) interviews you one question at a time and fills the context library.

## The rhythms

| Rhythm | Skills that run it |
|---|---|
| Daily deal desk | `deal-desk-triage`, `account-price-fit`, `deal-desk-review`, `api-access-request`, `data-license-pricing` |
| Weekly review | `weekly-pricing-review`, `api-usage-tier-fit` (`price-realization-analysis` for a deeper drill) |
| Monthly Pricing Council | `council-decision-pack`, `price-change-proposal`, `pricing-stakeholder-review` |
| Quarterly review | `quarterly-price-review`, `competitive-price-scan`, `pricing-win-loss`, `analog-research` |
| Annual release | `price-book-release`, `price-book-import`, `price-book-builder`, `rights-handoff` |
| New product or construct | `analog-research`, `value-metric-design`, `data-price-setting`, `data-product-valuation`, `packaging-design`, `wtp-study-design` |
| Running the OS | `pd-start`, `pd-setup`, `pd-ratchet`, `pd-skill-author` |

The full method is in `core/methodology/`: the eleven-stage spine, the rhythms, and the frameworks table with the verification status of every source. Design history is in `design/`.

## The rules that never change

1. Answer first; name the decision and who decides.
2. Tag every number F, I, A or U. Computed numbers come from scripts.
3. Price the scope: a data or API price states the right it grants. An API price buys the use it names; collecting or keeping data is a data licence with a minimum commitment, a retention term and audit.
4. Recommend only. The Pricing Council approves.
5. List price is independent of the account. The account enters only at the deal desk, as a give tied to a get, inside the approved band.
6. Rights questions go to the product manager.
7. Public sources only for outside research, with URL and access date.

Full text: `core/shared/operating-rules.md`.

## The nine rights

internal_use, internal_analytics_shared_outputs, display_to_third_parties, redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding, ai_evaluation. `internal_use` is the narrowest; each broader right is a separate line priced above it. See `skills/price-book-builder/references/granted-scope.md` and `api-access-scope.md`.

## Scripts

Run with python3 from the skill folder. Examples sit in each skill's `examples/`.

| Script | Does |
|---|---|
| `data-price-setting/scripts/price_corridor.py` | Corridor from cost floor to customer value |
| `price-book-builder/scripts/check_price_book.py` | Price book checks; `--mode release` makes a missing floor or granted right an error |
| `price-book-import/scripts/import_price_book.py` | Import an existing price book; writes the hand-off list |
| `account-price-fit/scripts/account_waterfall.py` | Account-level economics of options for an add-on |
| `deal-desk-triage/scripts/triage_rank.py` | Rank open requests and route them |
| `api-access-request/scripts/harvest_screen.py` | Look-to-book and distinct-query screen; flags are questions to confirm |
| `weekly-pricing-review/scripts/weekly_roll.py` | Realization rate by week, family and cause |
| `pricing-win-loss/scripts/winloss_tally.py` | Won and lost deals by pricing cause |
| `price-book-release/scripts/price_book_diff.py` | Change log between two price book versions |
| `price-book-release/scripts/notice_calendar.py` | Who must be told by when, from contract terms |
| `rights-handoff/scripts/rights_list.py` | Hand-off list and answers read back |
| `value-metric-design/scripts/metric_scorecard.py` | Score candidate value metrics |
| `data-product-valuation/scripts/valuation.py` | Cost, market and income approaches |
| `competitive-price-scan/scripts/check_scan_log.py`, `analog-research/scripts/check_analogs.py` | Source and date checks for research |

## Tools and checks

`python3 tools/pdos.py` has: `validate`, `build` (`--check` for drift), `doctor`, `lint <file>`, `evals --coverage`, `notebook-pack`, `new-instance`, `upgrade-instance`, `release`, `list`. `release` writes a source-only tarball: after extracting it run `python3 tools/pdos.py build` to produce the generated folders. Tests: `python3 -m unittest discover -s tests`. Edit `core/`, then build; never edit generated folders.

## Platforms

Gemini CLI extension (this repo root), Antigravity CLI (`.agents/skills/`), Gemini app skills (zips in `dist/gemini-app/zips/`), Gemini Notebook packs (the coach pack in `dist/notebook-packs/`; company and account packs from `notebook-pack` go to `workspace/outputs/notebook-packs/`). Details and the verify list: `adapters/google/`. The Microsoft Copilot guide in `copilot-guide/` is legacy (`copilot-guide/LEGACY.md`).

The extension also carries a guard hook that blocks writes that add an Approved or Decided status to pricing artifacts (price book, Council, decision log, exception log, anything under `workspace/` or `outputs/`); the Council overrides with `PRICING_DESK_COUNCIL=1`. It guards against model mistakes, not against a person.

## Upgrading

From 0.2.0: the rights work moved to the Rights Desk (`dataset-intake-register`, `/pricing:register-intake`, `/pricing:rights-lookup`, the `rights-reviewer` subagent and the `legal_confirmed` hook are gone). If Gemini CLI warns about a skill conflict, move the older copy out of `~/.gemini/skills`. Then run `gemini extensions update pricing-desk`. From 0.4.0: run `upgrade-instance`; `workspace/` and `local/` are untouched.

More: `docs/architecture.md`, `docs/rollout-playbook.md`, `docs/security-and-governance.md`.
