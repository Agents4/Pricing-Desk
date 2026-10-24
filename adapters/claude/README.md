# Claude Code and Claude

Skills load from `.claude/skills/` (generated from `core/skills/`). `CLAUDE.md` imports `AGENTS.md`, so the routing table and non-negotiables are always in context. Start with the `pd-start` skill or ask in plain language.

Edit `core/`, then `python3 tools/pdos.py build`. Do not edit generated folders. `python3 tools/pdos.py doctor` checks the registries; `validate` checks skills; `evals --coverage` shows skills without an eval case; `lint <file>` checks an output against the checkable rules.

Claude apps accept the zips in `dist/gemini-app/zips/`, one skill per upload; scripts may not run there.
