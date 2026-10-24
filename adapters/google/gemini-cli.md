# Gemini CLI

Install the extension, then restart the CLI:

```
gemini extensions install https://github.com/Agents4/Pricing-Desk
gemini extensions update pricing-desk      # after a new version
gemini extensions link .                   # from a clone, for development
```

## What loads

- `GEMINI.md`: the standing rules (answer first, tag numbers, price the scope, compute never estimate, recommend only, list independent of account, company values from the context library).
- `skills/`: all skills, loaded on demand by name and description.
- `commands/pricing/`: one slash command per skill. `/pricing:start` is the front door; `/pricing:setup` interviews you one question at a time and fills the context library.
- `agents/`: `price-book-checker`, which runs the checker script only. Gemini CLI marks subagents as preview; they may need enabling in settings.
- `hooks/`: a BeforeTool guard that blocks edits setting a price book line to Approved. It guards against model mistakes, not against a person; it does not see shell commands. The Pricing Council sets `PRICING_DESK_COUNCIL=1` to override.

## First session

1. Create a company instance: `python3 tools/pdos.py new-instance <folder> --client "<Company>"`, open the folder, and run `/pricing:setup`.
2. `/pricing:start` shows what is due today, this week and this month from the rhythms.
3. Work in `workspace/`. Upgrades never touch `workspace/` or `local/`.

## Conflicts

If the CLI warns about a skill conflict, an older copy is in `~/.gemini/skills`; move it out. If you upgraded from 0.2.0, the rights work moved to the separate Rights Desk (see the README).

## Antigravity CLI

Antigravity keeps Agent Skills; extensions become plugins. Workspace skills load from `.agents/skills/`, which this repo generates. Custom commands may not carry over: use the skill names in plain language (`platform-facts.md`, facts 3, 4 and the verify list).
