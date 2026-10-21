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

## Notes
- Only Legal sets legal_confirmed. Anything other than Yes counts as not confirmed.
- The sample CSVs in the SharePoint kit mark rows confirmed only so the tests run.
- Secondary processing (aggregated and derived products) is handled by Transform and Inherit modes; splitting processing into separate rights is a possible next step.
