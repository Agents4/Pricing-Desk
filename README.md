# Pricing desk package

Everything built for the travel-technology pricing desk, in one place. Prices, customers, agreements, and rights in the examples are invented.

## 1. Blueprint (online document)
Pricing desk blueprint: mandate, tasks, responsibilities, operating model, roles, skills, KPIs, 90-day plan.
https://claude.ai/code/artifact/8dc08cc2-0cf5-41ac-8250-eded39f28038 (private to the author; it is not stored in this repo)

## 2. AI skills (skills/, with ready-to-upload zips in skills-upload/)
| Skill | Use it to |
|---|---|
| deal-desk-review | Review a non-standard deal, route approvals |
| price-realization-analysis | Find where list price leaks before it is realized |
| api-usage-tier-fit | Check customers sit in the right API tier |
| price-change-proposal | Build and justify a price change |
| wtp-study-design | Design and analyze willingness-to-pay research |
| dataset-intake-register | Intake a dataset into the data rights register (the rights we hold on the data) |
| data-price-setting | Work out what to charge: corridor, conferred-right ladder, sensitivities (any product; rights only for data) |
| price-book-import | Bring an existing price book into the standard format, check it, and rank the register questions |
| price-book-builder | Build and check the price book for any product, with strategy and release checks |
| data-license-pricing | Price a customer's data licensing request, checking we hold the rights to grant it |

Suggested order, starting from an existing price book: price-book-import, then price-book-builder (strategy check), then dataset-intake-register on the ranked list, in parallel with pricing work.
Suggested order for a new data product: dataset-intake-register, then data-price-setting, then price-book-builder, then data-license-pricing for each deal.

### Held rights and conferred rights
The same nine rights appear in two places and mean two different things.

| | Register (Use_Rights sheet) | Price book (conferred_right column) |
|---|---|---|
| Records | The rights **we hold** on a dataset: what we may do with it, given our suppliers, contributing customers and the derivative products we may create | The rights **we grant the customer** on a product: what they may do with it |
| Set by | Evidence; Legal confirms | Pricing proposes; the Pricing Council approves |

We can only confer what we hold. Each data line names its `dataset_id`, its `conferred_right` and its `data_form` (derived, the default, or passthrough). The checker looks up in `skills/price-book-builder/references/rights-coverage.csv` which held rights the dataset must carry for that conferred right, reads them from the register, and takes the worst result. Example: conferring `display_to_third_parties` on a derived product needs `internal_analytics_shared_outputs` (we may supply the outputs) and `display_to_third_parties` (we may let them be shown) held on that dataset. The coverage table is a default for Legal and the Pricing Council to confirm; edit the CSV and the checker follows. Full explanation: `skills/price-book-builder/references/rights-model.md`.

### Provisional pricing and the release check
Pricing does not wait for Legal. Data lines whose rights are not confirmed are priced as Provisional, and the checker reports them as warnings (strategy mode, the default). Provisional means usable for strategy and for deciding where rights intake starts; it does not mean cleared to quote. Before a price book goes out for quoting, run the checker with --mode release, which fails any line whose rights are not confirmed or whose floor is missing.

| Rights basis | Meaning | Strategy mode | Release mode |
|---|---|---|---|
| N/A | Not a data line (software, services, plain API access) | pass | pass |
| Confirmed | Every held right needed is Granted or Conditional, Legal confirmed | pass | pass |
| Provisional | A needed held right is Unknown, missing from the register, or not yet confirmed | warning | error |
| Contradicted | A needed held right looks Prohibited, Legal has not confirmed | warning, top of intake list | error |
| Blocked | Legal confirmed a needed held right Prohibited | error | error |

Only the products that carry data or third-party content need the register. The checker takes an optional register and writes an exposure report that ranks the register questions (a held right we need on a dataset) by the annual revenue that depends on them, weighted when the customer right is broad (redistribution, derivative, display, AI uses), and a backfill file of the held rights the register is missing.

Scripts inside skills (run with python3):
- price-book-import/scripts/import_price_book.py --in LEGACY.xlsx --out-dir OUT imports an existing price book (example: price-book-import/examples/legacy-price-book.csv).
- dataset-intake-register/scripts/create_register.py builds an empty register workbook.
- data-price-setting/scripts/price_corridor.py --in examples/air-shopping-insights.json
- price-book-builder/scripts/check_price_book.py --pricebook PRICEBOOK.csv [--register REGISTER.xlsx] [--mode strategy|release] [--exposure-csv OUT.csv] [--backfill-csv OUT.csv]

## 3. Data rights register example (data-rights-register/)
air-shopping-register-example.xlsx: agency requests and supplier fare responses, with the rights we hold on each dataset, evidence, and open questions. Legal confirmation is blank on purpose. build_example.py regenerates it (python3 data-rights-register/build_example.py).

## 4. SharePoint kit (sharepoint-kit/)
Party-aware rights model for rights that vary by agency and supplier: list schema (xlsx and JSON), a resolver that computes effective rights and coverage, and sample data. See sharepoint-kit/README.md.

## 5. Microsoft Copilot guide (copilot-guide/)
For use without creating agents.
- Copilot-Guide.docx: setup in about 20 minutes, the routine for each task, number checks, data handling, troubleshooting.
- Copilot-Playbooks.docx: eleven playbooks (the skills, a rights lookup and an existing-price-book import) with a copy-and-paste prompt for each. Add it to a Copilot Notebook as a reference.
- custom-instructions.txt: paste into Copilot custom instructions.
- notebook-instructions.txt: paste into the Notebook's instructions.
- Copilot-Guide.md and Copilot-Playbooks.md: the same text as the .docx files, readable on GitHub.
- source/: the Node scripts that build the two .docx files (npm install docx, then node guide.js OUT.docx and node playbooks.js OUT.docx from inside source/). content.js holds the paste-in instructions and the playbook prompts.
Copilot cannot load the Claude skills or run the scripts. Use it to draft and extract, and use the scripts or Excel formulas for numbers that matter.

## 6. Gemini CLI extension (repo root)
This repo is also a Gemini CLI extension. Install it with:
- gemini extensions install https://github.com/Agents4/Pricing-Desk
- or, from a clone for development: gemini extensions link .
Restart the CLI after installing. The extension carries:
- GEMINI.md: standing desk rules (unknown is the default, only Legal confirms rights, compute don't estimate, recommend only).
- skills/: the ten skills, loaded on demand.
- commands/pricing/: /pricing:deal-review, :realization, :tier-fit, :price-change, :wtp-study, :import-price-book, :register-intake, :price-setting, :price-book, :licence-request, :rights-lookup.
- agents/: @rights-reviewer (read-only) and @price-book-checker (runs the checker script only). Gemini CLI marks subagents as a preview feature and may need them enabled in settings.
- hooks/: a BeforeTool guard that blocks write_file and replace edits that set legal_confirmed to Yes or a price book line to Approved. Provisional pricing is not blocked. It is a guardrail against model mistakes, not a security control: it does not see shell commands. Legal can set PRICING_DESK_LEGAL=1 and the Pricing Council PRICING_DESK_COUNCIL=1 to override. Note the sample CSVs in sharepoint-kit/ contain Yes values, so editing them needs the override.
Checked with Gemini CLI 0.65.0: extensions validate passes, link succeeds, the context file and all ten skills load. The 11 commands, subagents and hook were checked for format only (TOML and JSON parse, hook tested with sample inputs); they have not been run against a live model session.

## Notes
- Only Legal sets legal_confirmed. Anything other than Yes counts as not confirmed (Provisional). Provisional prices are allowed for strategy; they are not cleared to quote.
- The sample CSVs in the SharePoint kit mark rows confirmed only so the tests run.
- Secondary processing (aggregated and derived products) is handled by Transform and Inherit modes; splitting processing into separate rights is a possible next step.
