---
name: skill-authoring
description: How to write or change a Pricing Desk OS skill, with a checklist
---

# Skill authoring

A skill is a folder: `core/skills/<name>/SKILL.md`, optional `scripts/`, `references/`, `examples/`, `assets/`. One skill does one job. Detail goes in `references/`, templates in `assets/`.

## Shape (60 to 150 lines; never past 500)

1. Frontmatter: `name` (equals the folder), `description` (what it does and `Use when ...`; at most 1024 characters), `compatibility`, `metadata` (`version`, `layer`, `last_reviewed`, `includes`, optional `command`).
2. Title and one purpose sentence. Read the operating rules and capabilities references.
3. `## When to use`, with a `Not for:` line that names the neighbor skill.
4. `## Inputs`: needed and helpful, including which context library files are read.
5. `## Procedure`: numbered; each step names its output.
6. `## Output`: file path, and what the reply says.
7. `## Quality gate`: checks to pass before finishing, including the rules it can break.

## Naming

Lowercase letters, digits, single hyphens, at most 64 characters. System skills start with `pd-`. The slash command is the name without `pd-`, or `metadata.command` when the old command name differs.

## Includes

`metadata.includes` lists shared files relative to `core/`. Files under `templates/` land in `assets/`; others land in `references/`. Every skill includes `shared/operating-rules.md` and `shared/capabilities.md`. Reference an include in the body (`references/operating-rules.md`) or doctor warns.

## Checklist when adding a skill

1. Create the folder and `SKILL.md`. Copy the shape from `core/skills/deal-desk-review`.
2. Add templates, rubrics and scripts it needs. Scripts use only the standard library and print their inputs.
3. Add a row to the routing table in `AGENTS.md` and bump counts in `README.md`.
4. Add an eval case in `evals/cases/` that starts with `Skill: <name>`.
5. Add a line under Unreleased in `CHANGELOG.md`.
6. Run `python3 tools/pdos.py validate`, then `build`, then `doctor`.

Never edit generated folders. Never put a company value (threshold, name, floor) in a skill; read it from the context library.
