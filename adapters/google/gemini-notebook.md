# Gemini Notebook

Gemini Notebook (formerly NotebookLM) answers only from the sources you load, with citations. It cannot run skills or scripts, so it is for lookup, onboarding and briefings, not for computing.

## Packs

| Pack | Built by | Use |
|---|---|---|
| Pricing coach | `python3 tools/pdos.py build` (output in `dist/notebook-packs/pricing-coach/`) | Method questions, quizzes, onboarding. No company data. |
| Company playbook | `python3 tools/pdos.py notebook-pack --company` | Governance, catalog, deal structures, price book tables, analogs, decision log |
| Account room | `python3 tools/pdos.py notebook-pack --account <slug>` | One account: price sheet, deal packages, notes |

Each pack folder has `sources/`, `chat-instructions.txt`, `studio-prompts.md` and a `README.md` with the upload steps.

## Confidential

Company and account packs can hold floors, discount bands, incentives and customer prices. Everyone with access to a notebook can read its sources. Share them only with the deal desk and the Pricing Council. Never add what the company has not approved for this tool. Files still marked `status: template` hold no company facts.

## Freshness

A notebook is a snapshot unless its sources are synced Google Docs. Regenerate after meaningful changes, replace only the changed sources, and put the build date in the notebook title.

## Limits

Source counts, per-source size and chat-instruction length are Google's and change. See `platform-facts.md` fact 16 and verify. The builder splits long sources and warns when chat instructions pass 3,000 characters.
