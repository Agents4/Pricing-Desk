# System skill procedures

---

## Document: pd-ratchet

# Ratchet: learn from a miss

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A miss is only useful if it changes something that stops the next miss. Each lesson ends in a change, or in a written reason there is none.

## When to use

- A price, quote or recommendation was wrong, late, overruled by the Council, or disputed by the customer.
- The user corrected an output and the correction should become standing.
- The quarterly or annual review of the OS (rules, skills, evals).

Not for: fixing the output itself (rerun the skill), or changing a price (`price-change-proposal`).

## Inputs

What happened (one or two sentences), the output or decision involved, what was expected. Read `workspace/context-library/lessons.md`, and the rule and skill involved.

## Procedure

1. **State the miss** in one sentence with the evidence (F/I/A/U). Do not blame a person.
2. **Trace to a stage** of the life of a price: intake, fact base, value, research, architecture, test, govern, release, deal desk, monitor, learn.
3. **Trace to the cause**, pick one: a rule was missing; a rule existed but had no check; a skill step was missing or unclear; a company value was wrong or Unknown; an input was bad; the model estimated instead of computing; the user's context was not loaded.
4. **Choose the smallest change that would have caught it**, from this list: add an eval case (always, if the miss can be written as input and expected checks); change a skill step; add or sharpen a rule and its check; fix a context library value (needs the user's approval); or no change, with the reason.
5. **Draft the change.** For an instance, skill changes go in `local/skills/`; changes to the product (`core/`) are proposed as text for the product owner. Never edit `core/` from an instance.
6. **Log the lesson**: append one row to `workspace/context-library/lessons.md`: date, what happened, stage, what changed. Ask before writing.
7. **Check repeats.** If the same cause appears twice in the lessons file, say so and recommend the stronger fix (a check that fails, not a note).

## Output

Header, then the lesson row, the eval case (input and expected, ready to save under `evals/cases/` or the instance's evals folder) and the proposed change. Handoff block.

## Quality gate

- Exactly one cause chosen, one smallest change proposed.
- An eval case is included unless the miss cannot be expressed as one, and the output says why.
- No change to a context value or core file without approval. No person blamed.

---

## Document: pd-setup

# Pricing Desk setup

Read `references/operating-rules.md`, `references/capabilities.md` and `references/interview-protocol.md`. Outputs carry the header in `references/output-conventions.md`. The files to produce follow the templates `references/business-info.md`, `references/pricing-governance.md`, `references/product-catalog.md`, `references/deal-structures.md`, `references/systems-and-data.md`, `references/rights-handoff.md`, `references/guardrails.md` and `references/writing-style.md`.

Fill the context library so every other skill uses this company's thresholds, Council and systems. Rule 14: nothing here is a default. Write only what the user says.

## When to use

- A new instance, or the context library is empty or `status: template`.
- The Council, bands, floors, products, systems or hand-off route have changed.
- A skill returned Unknown for a company value and the user wants to fill it.

Not for: researching the company (setup records what the user says), or deciding a price.

## Inputs

The user's answers, one at a time. Optional documents they supply: org chart, approval policy, product list, sample packs, a price book. Read the current library files first.

## Procedure

1. **Check state.** Read the existing files. Say which are filled and which are template. Offer to start with the one that unblocks the most (usually governance).
2. **Interview one question at a time**, in this order, following `references/interview-protocol.md`. Give an example of the kind of answer you need. Follow up on a thin answer before moving on.
   - Business and products: what the company sells, to whom, how revenue is earned (including incentives paid to agencies).
   - Governance: Council members and chair; who proposes and who approves each decision; discount bands and margin floors by product family; deal desk authority; target response times (label as proposals until agreed).
   - Deal structures: how anchor deals work, incentives paid and how they are tiered and measured, look-to-book clauses, notice and price-protection terms, what is normally traded.
   - Systems: where the price book, usage, invoices, deal log, cost to serve and CRM live now and after the move; export formats; approved tools.
   - Rights hand-off: product manager contact, how lists are sent, how answers return.
   - Guardrails and writing style: what must never leave, who reviews packs; two or three examples they are proud of and rules, not adjectives.
3. **Summarize after each section** in two to four lines and ask to confirm or correct. List what is still Unknown.
4. **Draft the file** with the template headings. Use the user's words. Mark anything not said as Unknown. Keep `status: template` until every required field in the file is answered or explicitly Unknown by the user; then set `status: filled` and the review date.
5. **Approval gate.** Show the file. Write it to `workspace/context-library/` only after the user approves. Without file access, return it with a FILING NOTE.
6. **Close.** List the five most important items still Unknown and who could answer. Offer the next step: a first deal review, the price book import, or the weekly review.

## Output

Header, then the files written (or the text), what changed, and the five Unknowns. No other analysis.

## Quality gate

- Nothing invented about the company, its people or its thresholds. Gaps say Unknown.
- One question per turn; the user approved the final text before it was written.
- No customer-specific prices, usage or credentials recorded.
- Proposed time targets are labeled proposals until the user agrees them.

---

## Document: pd-skill-author

# Skill author

Read `references/operating-rules.md`, `references/capabilities.md` and `references/skill-authoring.md` (shape, naming, includes, checklist). Outputs carry the header in `references/output-conventions.md`.

Turn a recurring pricing task into a lean skill that another person or agent can run.

## When to use

- The same multi-step pricing task has been done by hand two or more times.
- An existing skill is missing a step, or a lesson from `pd-ratchet` calls for a skill change.

Not for: one-off work, or changing company values (`pd-setup`).

## Inputs

The task in the user's words, one or two real examples of it done, and who runs it and how often. For a change: the skill and the miss.

## Procedure

1. **Interview one question at a time** (see `references/interview-protocol.md`): what triggers the task, what comes in, what comes out and who reads it, what makes it wrong, what must never happen.
2. **Check for overlap.** List the current skills (`python3 tools/pdos.py list`) and say whether an existing skill should be extended instead. Prefer extending.
3. **Pick the place.** In an instance: `local/skills/<name>/`. In the product repo: `core/skills/<name>/`. Name it per `references/skill-authoring.md`.
4. **Draft `SKILL.md`** in the standard shape: frontmatter with `Use when ...`, When to use with a Not-for line, Inputs (with context library files read), Procedure with named outputs, Output, Quality gate that names the rules it can break. Aim for 60 to 150 lines; move detail to `references/`.
5. **Add what it needs**: a template in `assets/` or `core/templates/`, a script only if arithmetic is involved (standard library, prints its inputs), and an eval case `Skill: <name>` with input and expected checks.
6. **Update registries**: the routing table in `AGENTS.md`, skill counts in `README.md`, a line under Unreleased in `CHANGELOG.md`.
7. **Run** `python3 tools/pdos.py validate`, `build`, `evals` and `doctor`. Fix every error. Report warnings.

## Output

Header, then the files written (paths), the validation result, and a handoff block listing what the user must review.

## Quality gate

- The skill contains no company-specific value; it reads the context library.
- Every rule it can break is named in its Quality gate.
- It has an eval case; validate, build and doctor pass.
- It overlaps no existing skill, or says how it differs.

---

## Document: pd-start

# Pricing Desk start

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Find out where the user is, then send them to the one skill that moves the work.

## When to use

- The user is new, unsure, or says "help me with pricing".
- The user asks what is due: deals today, the weekly review, the Council pack, the quarter review, the annual release.
- A request fits no skill: answer from the rules and say which skill would come closest.

Not for: doing the work itself. Route and stop.

## Inputs

Read if present: `workspace/context-library/pricing-governance.md`, `product-catalog.md`, `systems-and-data.md`, `lessons.md`; `workspace/price-book/`; the newest files in `workspace/outputs/`. If a library file says `status: template`, it counts as empty.

## Procedure

1. **Check state.** Report in three lines: context library (filled, partly, template), price book (present, version, last checker run), tools (files, shell, web). If you cannot look, ask one question: what exists?
2. **Ask one question** (see `references/interview-protocol.md`): what do you need to decide or produce? Offer the common answers from the table below.
3. **Route.** Name the skill and what it needs from the user. If the context library is a template and the work needs thresholds or the Council, route to `pd-setup` first and say why in one line.
4. **Rhythm check.** Given today's date, say which rhythms are due: daily deal desk, weekly review (same weekday each week), monthly Council pack, quarter-end review, annual release. Use dates in `workspace/outputs/`; if none exist, say "no history yet".

| The user wants to | Skill |
|---|---|
| Set up the context library for a company | `pd-setup` |
| Decide what to charge for a new product, right or API use | `data-price-setting` (after `analog-research` if there is no price history) |
| Handle today's quote requests | `deal-desk-triage` |
| Review one deal | `deal-desk-review`, with `account-price-fit` when there is an anchor deal |
| Price a data licence or an API request that would collect data | `data-license-pricing`, `api-access-request` |
| Run the weekly realization and API usage review | `weekly-pricing-review` |
| Prepare the Council | `council-decision-pack` |
| Release the price book | `price-book-release` |
| Turn a miss into an improvement | `pd-ratchet` |

The full routing table is in `AGENTS.md`.

## Output

The header, then: state (three lines), the one skill to run next with what it needs, rhythms due, and the single question you still have. Do not file anything.

## Quality gate

- One next step only, not a menu of five.
- Nothing about thresholds, the Council or floors stated from memory; Unknown if the library is a template.
- No work done that belongs to the routed skill.
