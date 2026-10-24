@AGENTS.md

## Claude Code notes

- Edit `core/`, then run `python3 tools/pdos.py build`. Do not edit generated folders (`skills/`, `commands/`, `agents/`, `hooks/`, `GEMINI.md`, `gemini-extension.json`, `.claude/skills`, `.agents/skills`, `dist/`).
- After changing a skill run `python3 tools/pdos.py validate`; `python3 tools/pdos.py doctor` checks health and the registries in `os.manifest.json`.
