---
name: pd-ratchet
description: Turn a pricing miss into an improvement. Traces a wrong, late, overruled or disputed pricing output to the stage and rule involved, decides whether to change a rule, a skill, an eval case or a context file, and logs the lesson. Use when a deal outcome, Council decision, realization review or user correction shows the OS should have done better, and at the quarterly and annual reviews.
compatibility: "Any Agent Skills client. File access recommended to append to the lessons file; otherwise returns the entry as text."
metadata:
  version: "1.0.0"
  layer: system
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

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
