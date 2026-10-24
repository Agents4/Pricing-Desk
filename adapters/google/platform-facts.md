# Platform facts (carried from Sales-OS, dated 2026-10-17)

These facts were gathered for Sales-OS on 2026-10-17 and are carried here unchanged. The Pricing Desk project has not re-fetched them. Google changes these products often: re-check the verify list before a client session. Nothing in this repo depends on a fact here except where the guides in this folder say so.

## Facts and sources

| # | Fact | Source | Confidence |
|---|---|---|---|
| 1 | Gemini CLI stopped serving Google AI Pro, Ultra and free individual accounts on 2026-06-18; the terminal experience moved to Antigravity CLI (announced 2026-05-19). | Gemini CLI GitHub discussion #27274 (maintainer announcement) | High |
| 2 | Gemini Code Assist Standard and Enterprise licenses, Google Cloud usage, and paid API keys keep Gemini CLI access. Vertex AI and Google One were not named. | Same | High for what it names; unknown otherwise |
| 3 | Antigravity CLI keeps Agent Skills, hooks and subagents. Extensions are renamed plugins. The installer imports skills, MCP configs and agent profiles. | Same, plus a third-party migration guide (June 2026) | Medium: the third-party details (paths, `agy` commands, quota) are not official |
| 4 | Workspace skills move from `.gemini/skills/` to `.agents/skills/` for Antigravity; global skills to `~/.gemini/antigravity-cli/skills/`. | Third-party migration guide | Medium |
| 5 | Gemini app: skills replace Gems. Skills are reusable instructions run inside chat, called with a slash (to move to `@`), also applied automatically. Unlimited skills, 100 active at once. | Gemini Apps Help: "About the transition from Gems to skills" and "Create and manage skills" | High |
| 6 | Skills import: a single `SKILL.md`, or a folder or zip with `SKILL.md` at the root. Plain-text-based files, rich media like PDFs and images; no Office binaries; 100 MB combined; scripts cannot reach the internet. Upload to create is limited to the Mac app and web app. | Gemini Apps Help: "Create and manage skills" | High |
| 7 | Skills may include reference files from 2026-09-30. Drive and Notebook file support for skills was announced as coming. | Gemini Apps Help | Medium |
| 8 | Gems retirement and conversion: November 2026 personal accounts; March 2027 Workspace business, enterprise and nonprofit; June 2027 education. Skills available first to adults on personal accounts; Workspace accounts later. | Gemini Apps Help: transition page | High for dates stated; Workspace skills availability must be verified |
| 9 | Gemini Enterprise: custom skills generally available (2026-08-13). Admins enable skills and skill sharing in Feature Management and can approve sharing requests. | Gemini Enterprise release notes | High |
| 10 | Workflow Builder (formerly Agent Designer) generally available (2026-09-03). Connectors include Drive, Gmail, Calendar, Chat, Slack, Jira; Teams, Notion, Salesforce added 2026-10-13. | Gemini Enterprise release notes | High |
| 11 | Custom MCP server data stores generally available (2026-08-07), off by default and gated by an organization policy. | Gemini Enterprise release notes | High |
| 12 | Gemini Notebook Enterprise integration in Gemini Enterprise: sharing, sensitive data protection policies, CMEK, quizzes and flashcards generally available. | Gemini Enterprise release notes | High |
| 13 | Google describes agent skills as reusable packages of instructions loaded by progressive disclosure, based on an open specification (SKILL.md with name and description up to 1,024 characters; optional `scripts/`, `references/`, `assets/`). Works across Antigravity CLI, Claude Code, VS Code, Cursor and others. | Google Cloud: AI agent skills | High |
| 14 | Google announced a unified Gemini agent for businesses on 2026-10-08, with skills, connectors, MCP and a tasks inbox; business first, consumers later; no general availability date or pricing stated. | TechCrunch, 2026-10-08 | Medium |
| 15 | Gemini CLI extension layout: `gemini-extension.json`, `commands/`, `skills/`, `agents/`, `hooks/`, `policies/`; extensions load from `~/.gemini/extensions`. Custom commands are TOML files, `/gcs:sync` from `gcs/sync.toml`. | geminicli.com extension reference | High |
| 16 | Gemini Notebook source and chat limits: about 50 sources on the consumer tier; 300 sources, 500,000 words or 500 MB per source on Enterprise; a short chat-instruction limit. | Carried from Sales-OS, itself not re-verified | Low: verify |

## Verify list (do before a client session)

1. Which license and account type the company holds (Workspace edition, Gemini Enterprise, Gemini Code Assist). This decides whether the Gemini CLI or the Antigravity CLI applies, and whether skills are enabled for users (facts 2, 8, 9).
2. Whether skills are enabled in the Gemini app for Workspace users today or only for personal accounts (fact 8). Test with a real user account.
3. Whether the admin setting for skills and skill sharing is on, and who approves sharing (fact 9).
4. Current Notebook source and chat-instruction limits (fact 16).
5. Whether slash commands in `commands/` still work in the company's CLI (fact 15), and whether Antigravity supports custom commands.
6. Whether the Gemini app trigger changed from `/` to `@` (fact 5).
7. The company's data policy for consumer versus Workspace accounts. The pricing material is confidential (see `docs/security-and-governance.md`).

## Sources (as listed in Sales-OS; not re-fetched here)

- Gemini CLI transition announcement: github.com/google-gemini/gemini-cli/discussions/27274
- Gemini Apps Help, transition from Gems to skills: support.google.com/gemini/answer/18560919
- Gemini Apps Help, create and manage skills: support.google.com/gemini/answer/17094296
- Google Cloud, AI agent skills: cloud.google.com/discover/ai-agent-skills
- Gemini Enterprise release notes: docs.cloud.google.com/gemini/enterprise/docs/release-notes
- Gemini CLI extensions reference: geminicli.com/docs/extensions/reference/
- Third-party migration guide (unofficial): digitalapplied.com blog, June 2026
- TechCrunch, 2026-10-08, Google's agentic Gemini for businesses
