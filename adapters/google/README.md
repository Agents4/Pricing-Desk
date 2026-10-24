# Pricing Desk on Google

Two surfaces matter: the **Gemini CLI extension** (skills, commands, subagent, guard hook, scripts) and the **Gemini app / Gemini Notebook** (skills as uploads, notebooks as read-only Q&A). Microsoft Copilot material in `copilot-guide/` is kept for reference only.

| Surface | What you get | Scripts run? | Guide |
|---|---|---|---|
| Gemini CLI extension | All 28 skills, `/pricing:*` commands, hook that blocks Approved, checker subagent | Yes | `gemini-cli.md` |
| Antigravity CLI | Same skills from `.agents/skills/` | Yes | `gemini-cli.md` (end) |
| Gemini app skills | One zip per skill from `dist/gemini-app/zips/` | No: scripts cannot run, so the skill says what to do without one | `gemini-app-and-workspace.md` |
| Gemini Notebook | Source packs and chat instructions: coach, company, account | No | `gemini-notebook.md` |

Numbers that matter (corridors, waterfalls, tier tables, realization, look-to-book screens, notice dates) are computed by scripts. On surfaces that cannot run scripts, the output says the check was not run, and the numbers are to be confirmed with the script before use.

Platform facts and the verify list: `platform-facts.md`.
