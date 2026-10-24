---
name: pd-skill-author
description: Add or change a Pricing Desk OS skill under the OS conventions: interview for the job, draft SKILL.md in the standard shape, add references, templates and an eval case, update the routing registries, then validate and build. Use when a pricing task recurs and has no skill, or when an existing skill needs a step added or fixed.
compatibility: "Any Agent Skills client. Needs file access and a shell to validate and build; without them it returns the files as text and the commands to run."
metadata:
  version: "1.0.0"
  layer: system
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, shared/interview-protocol.md, shared/skill-authoring.md"
---

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
