# Architecture

Pricing Desk follows the OS standard used by Sales-OS and Consulting-OS: one source, generated targets, lean skills, a company context library, and checks.

## Layers

| Layer | Where | Rule |
|---|---|---|
| Product | `core/` | The only place the product is edited: skills, commands, agents, hooks, shared rules, methodology, templates, scaffold, notebook packs |
| Generated | `skills/ commands/ agents/ hooks/ GEMINI.md gemini-extension.json .claude/skills .agents/skills dist/` | Written by `python3 tools/pdos.py build`. Never edited by hand. `build --check` fails on drift |
| Company | `workspace/` | Context library, price book, accounts, outputs. Filled by `pd-setup`. Never overwritten by an upgrade |
| Company skills | `local/skills/` | Company-only skills. Survive upgrades |
| Checks | `evals/ tests/` and the doctor | Eval cases name a skill and the behaviors expected; tests cover the scripts and the tool |

## Where company values live

The product contains no Council member, threshold, discount band, margin floor, notice term, system name or default target. Skills read them from `workspace/context-library/`. A file marked `status: template` means every value in it is Unknown, and the skill says Unknown and names the file to fill. This is rule 14 and design rule D7.

## Skills

Each skill is a folder with `SKILL.md` (purpose, when to use with Not-for, inputs, procedure, output, quality gate), optional `scripts/`, `examples/`, `references/`. Shared files are listed in `metadata.includes` and copied into each skill at build, so a zip is self-contained. Calculations are scripts: corridor, price book checker, account waterfall, triage ranking, API harvest screen, weekly roll-up, win-loss tally, price book diff, notice calendar, rights list, scorecard, valuation, scan and analog checkers.

Layers: `pricing` skills do the work; `system` skills (`pd-start`, `pd-setup`, `pd-ratchet`, `pd-skill-author`) run the OS itself.

## Flow of a price

The spine has eleven stages from intake to lessons (`core/methodology/spine.md`). Five rhythms run on a calendar: daily deal desk, weekly review, monthly Council, quarterly review, annual release (`core/methodology/rhythms.md`). List price is set per product from a corridor and is account-blind; the account enters only at the deal desk as a give tied to a get, inside the approved band (`account-price-fit`).

## Hand-offs

Whether we hold a right is not decided here. `rights-handoff` builds the list for the product manager and reads the answers back. The separate Rights Desk package does the assessment.

## Tools

`tools/pdos.py`: validate, build, doctor, lint, evals, notebook-pack, new-instance, upgrade-instance, release, list.
