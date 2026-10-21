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
| dataset-intake-register | Intake a dataset into the data rights register |
| data-price-setting | Work out what to charge: corridor, use-right ladder, sensitivities |
| data-price-book-builder | Turn prices into a controlled, checked price book |
| data-license-pricing | Price a customer's data licensing request against the register |

Suggested order for data products: dataset-intake-register, then data-price-setting, then data-price-book-builder, then data-license-pricing for each deal.

Scripts inside skills (run with python3):
- dataset-intake-register/scripts/create_register.py builds an empty register workbook.
- data-price-setting/scripts/price_corridor.py --in examples/air-shopping-insights.json
- data-price-book-builder/scripts/check_price_book.py --register REGISTER.xlsx --pricebook PRICEBOOK.csv

## 3. Data rights register example (data-rights-register/)
air-shopping-register-example.xlsx: agency requests and supplier fare responses, with use rights, evidence, and open questions. Legal confirmation is blank on purpose. build_example.py regenerates it (python3 data-rights-register/build_example.py).

## 4. SharePoint kit (sharepoint-kit/)
Party-aware rights model for rights that vary by agency and supplier: list schema (xlsx and JSON), a resolver that computes effective rights and coverage, and sample data. See sharepoint-kit/README.md.

## 5. Microsoft Copilot guide (copilot-guide/)
For use without creating agents.
- Copilot-Guide.docx: setup in about 20 minutes, the routine for each task, number checks, data handling, troubleshooting.
- Copilot-Playbooks.docx: the nine skills plus a rights lookup, rewritten as playbooks with a copy-and-paste prompt for each. Add it to a Copilot Notebook as a reference.
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
- skills/: the nine skills, loaded on demand.
- commands/pricing/: /pricing:deal-review, :realization, :tier-fit, :price-change, :wtp-study, :register-intake, :price-setting, :price-book, :licence-request, :rights-lookup.
- agents/: @rights-reviewer (read-only) and @price-book-checker (runs the checker script only). Gemini CLI marks subagents as a preview feature and may need them enabled in settings.
- hooks/: a BeforeTool guard that blocks write_file and replace edits that set legal_confirmed to Yes or a price book line to Approved. It is a guardrail against model mistakes, not a security control: it does not see shell commands. Legal can set PRICING_DESK_LEGAL=1 and the Pricing Council PRICING_DESK_COUNCIL=1 to override. Note the sample CSVs in sharepoint-kit/ contain Yes values, so editing them needs the override.
Checked with Gemini CLI 0.65.0: extensions validate passes, link succeeds, the context file and all nine skills load. The commands, subagents and hook were checked for format only (TOML and JSON parse, hook tested with sample inputs); they have not been run against a live model session.

## Notes
- Only Legal sets legal_confirmed. Anything other than Yes counts as not confirmed.
- The sample CSVs in the SharePoint kit mark rows confirmed only so the tests run.
- Secondary processing (aggregated and derived products) is handled by Transform and Inherit modes; splitting processing into separate rights is a possible next step.
