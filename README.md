# Pricing desk package

Everything built for the travel-technology pricing desk, in one place. Prices, customers and agreements in the examples are invented.

This package prices products and services: API access, premium software, services and data products. It assumes we hold the rights to sell what it prices. The rights we hold on data are assessed by the product manager in a separate package, the **Rights Desk** (Agents4/Rights-Desk). The two meet at one hand-off file, `product_rights_handoff.csv`.

## 1. Blueprint (online document)
Pricing desk blueprint: mandate, tasks, responsibilities, operating model, roles, skills, KPIs, 90-day plan.
https://claude.ai/code/artifact/8dc08cc2-0cf5-41ac-8250-eded39f28038 (private to the author; it is not stored in this repo)

## 2. AI skills (22 skills in skills/, ready-to-upload zips in dist/gemini-app/zips/)
| Skill | Use it to |
|---|---|
| deal-desk-review | Review a non-standard deal, route approvals; asks the purpose of new API access |
| price-realization-analysis | Find where list price leaks before it is realized |
| api-usage-tier-fit | Check customers sit in the right API tier; flag possible data collection through the API |
| price-change-proposal | Build and justify a price change |
| wtp-study-design | Design and analyze willingness-to-pay research |
| data-price-setting | Work out what to charge: corridor, granted-right ladder, sensitivities (any product) |
| price-book-import | Bring an existing price book into the standard format, check it, and write the hand-off list for the product manager |
| price-book-builder | Build and check the price book for any product, with strategy and release checks |
| data-license-pricing | Price a customer's data request, or an API request that would collect data |

Suggested order, starting from an existing price book: price-book-import, then price-book-builder (strategy check). Give product_rights_handoff.csv to the product manager.
Suggested order for a new product: data-price-setting, then price-book-builder, then data-license-pricing for each deal.

### Pricing the scope the customer gets
For data and API products, every price covers a stated right: what the customer may do with the data or the API responses. The price book records it in the `conferred_right` column, using nine rights: internal_use, internal_analytics_shared_outputs, display_to_third_parties, redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding and ai_evaluation. `internal_use` is the base and the narrowest. Each broader right is a separate line priced above it.

API access needs the most care. Serving the customer's own live transactions is the standard use. Keeping responses beyond the session, bulk extraction, rebuilding or reselling data, and feeding AI are data rights, and some customers ask for API access only to collect data. The price book prices them at the data-licence rate with a minimum commitment, a retention term and audit. `api-usage-tier-fit` looks for the usage pattern (distinct-query ratio, look-to-book, volume per key) and flags it as a question to confirm, not a finding. See `skills/price-book-builder/references/granted-scope.md` and `api-access-scope.md`.

### Checks
- check_price_book.py, strategy mode (default): a missing floor price, or a data or API line with no stated right, is a warning.
- check_price_book.py --mode release: those two are errors. Run it before a price book goes out for quoting.
- Always errors: overlapping tiers, unit price rising with volume, volume cliffs, floor above list, duplicates, a broader right priced below internal use.

Scripts inside skills (run with python3):
- price-book-import/scripts/import_price_book.py --in LEGACY.xlsx --out-dir OUT imports an existing price book and writes product_rights_handoff.csv (example: price-book-import/examples/legacy-price-book.csv).
- data-price-setting/scripts/price_corridor.py --in examples/air-shopping-insights.json
- price-book-builder/scripts/check_price_book.py --pricebook PRICEBOOK.csv [--mode strategy|release] [--lines-csv OUT.csv]

## 3. Microsoft Copilot guide (copilot-guide/)
For use without creating agents.
- Copilot-Guide.docx: setup in about 20 minutes, the routine for each task, number checks, data handling, troubleshooting.
- Copilot-Playbooks.docx: playbooks with a copy-and-paste prompt for each. Add it to a Copilot Notebook as a reference.
- custom-instructions.txt: paste into Copilot custom instructions.
- notebook-instructions.txt: paste into the Notebook's instructions.
- Copilot-Guide.md and Copilot-Playbooks.md: the same text as the .docx files, readable on GitHub.
- source/: the Node scripts that build the two .docx files (npm install docx, then node guide.js OUT.docx and node playbooks.js OUT.docx from inside source/). content.js holds the paste-in instructions and the playbook prompts.
Copilot cannot load the Claude skills or run the scripts. Use it to draft and extract, and use the scripts or Excel formulas for numbers that matter.

## 4. Gemini CLI extension (repo root)
This repo is also a Gemini CLI extension. Install it with:
- gemini extensions install https://github.com/Agents4/Pricing-Desk
- or, from a clone for development: gemini extensions link .
Restart the CLI after installing. The extension carries:
- GEMINI.md: standing desk rules (price the scope, API price buys the use it states, compute don't estimate, recommend only).
- skills/: the nine skills, loaded on demand.
- commands/pricing/: /pricing:deal-review, :realization, :tier-fit, :price-change, :wtp-study, :import-price-book, :price-setting, :price-book, :licence-request.
- agents/: price-book-checker (runs the checker script only). Gemini CLI marks subagents as a preview feature and may need them enabled in settings.
- hooks/: a BeforeTool guard that blocks write_file and replace edits that set a price book line to Approved. It is a guardrail against model mistakes, not a security control: it does not see shell commands. The Pricing Council can set PRICING_DESK_COUNCIL=1 to override.

### Upgrading from 0.2.0
Version 0.3.0 moved the rights work out. These are no longer in this extension: the `dataset-intake-register` skill, the `/pricing:register-intake` and `/pricing:rights-lookup` commands, the `rights-reviewer` subagent, the data rights register example, the SharePoint kit, and the `legal_confirmed` hook. Install the Rights Desk for them. If Gemini CLI warns about a skill conflict, an older copy of a skill is in `~/.gemini/skills`; move it out. After upgrading, run `gemini extensions update pricing-desk`.

## Notes
- Only the Pricing Council sets a line to Approved.
- Rights held on the data (what we may do with it, given suppliers and contributing customers) are the Rights Desk's job. This package names the right each price grants and hands that list over.
