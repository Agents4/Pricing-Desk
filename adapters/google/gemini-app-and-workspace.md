# Gemini app and Workspace

Skills in the Gemini app are reusable instructions run inside chat. Upload one zip per skill from `dist/gemini-app/zips/` (SKILL.md is at the zip root). `dist/gemini-app/INSTALL.md` has the steps and sizes.

## Limits that matter here

- Scripts in uploaded skills cannot reach the internet and may not run at all. Every pricing skill with a script says what to do without it, and says the check was not run. Treat any figure produced without the script as unconfirmed.
- Plain-text files only: no Office binaries. The price book goes in as CSV or pasted tables.
- Skills do not sync between the Gemini app and Workspace apps: upload in each place.
- Skills availability on Workspace accounts and the admin switch for sharing vary (`platform-facts.md`, facts 8 and 9). Verify before promising a rollout.

## Which skills to upload first

`pd-start`, `deal-desk-triage`, `deal-desk-review`, `account-price-fit`, `api-access-request`, `weekly-pricing-review`, `council-decision-pack`. The context library cannot be uploaded as a skill: paste the files you need into the chat, or use a company notebook (`gemini-notebook.md`) for lookup.

## Data

Pricing material is confidential. Use only accounts and tools the company has approved for it. See `docs/security-and-governance.md`.
