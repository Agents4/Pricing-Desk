# Changelog

## Unreleased

## 0.5.0
- Full operating system: eleven-stage spine, five rhythms, frameworks table with verification status (`core/methodology/`).
- 19 new skills (28 in all): `pd-start`, `pd-setup` (one question at a time), `pd-ratchet`, `pd-skill-author`, `account-price-fit`, `deal-desk-triage`, `api-access-request`, `weekly-pricing-review`, `pricing-win-loss`, `council-decision-pack`, `pricing-stakeholder-review`, `price-book-release`, `rights-handoff`, `analog-research`, `competitive-price-scan`, `value-metric-design`, `packaging-design`, `data-product-valuation`, `quarterly-price-review`.
- Existing nine skills conformed to the OS standard. `deal-desk-review` and `data-license-pricing` no longer contain hardcoded approval tiers; approval routes come from the company context library, and are Unknown until filled.
- Company context library (`workspace/context-library/`) filled by `pd-setup`; product contains no default thresholds.
- 14 operating rules, shared references, instance commands (`new-instance`, `upgrade-instance`, `release`), `lint`, `evals` (30 cases), 35+ tests.
- Calculation scripts for account economics, triage, API harvest screen, weekly roll-up, win-loss, price book diff, notice calendar, rights list, metric scorecard, valuation, scan and analog checkers.
- Gemini Notebook packs (`dist/notebook-packs/`, `notebook-pack --company|--account`), Google adapters and platform facts (carried from Sales-OS, not re-verified), docs (architecture, rollout, security). Microsoft Copilot guide marked legacy.
- Seed analog library: Reddit API pricing 2023, Cloudflare pay per crawl 2025, look-to-book economics (sources fetched 2026-10-24).


## 0.4.0
- Restructured to the Sales-OS layout: one source under `core/`, generated extension files at the repo root, `tools/pdos.py` (validate, build, doctor, list).
- Existing nine skills unchanged in behavior.
