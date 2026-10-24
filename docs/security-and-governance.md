# Security and governance

## What the data is

Prices, floors, discount bands, incentives, customer volumes, usage by key, supplier terms and contract notice terms. This is commercially sensitive. Examples in this repo are invented.

## Controls in the product

- **Recommend only.** No skill approves, publishes or sends. Status is Draft or For decision; the Council logs Decided. A guard hook blocks edits that set a price book line to Approved; the Council overrides with `PRICING_DESK_COUNCIL=1`. The hook is a guardrail against model mistakes, not a security control.
- **Confidentiality.** Every output carries a Handling label (Internal or Shareable). Customer-specific prices are not copied into general summaries.
- **Public sources only** for outside research, with URL and access date. No logins, no contact with competitors, no customer data in queries.
- **Flags are questions.** API usage screens say "possible data collection, to confirm". They never allege misuse.
- **Rights.** The desk states the right a price grants and hands the question on; it never says whether a right is held.
- **Protected paths.** Upgrades never touch `workspace/` or `local/`.

## Controls the company must set

- Which tools may receive pricing data (consumer Gemini, Workspace, Enterprise, notebooks). Company and account notebook packs contain floors and customer prices and must be shared only with the deal desk and the Council.
- Who sits on the Council, who may approve what, and the discount bands. These go in `pricing-governance.md` through `pd-setup`; until then they are Unknown.
- Retention of the decision log and exception log.
- Whether competitor and analog research is allowed to use the web, and who reviews it.

## Independent review

Rule 7: before a Council pack, price book release or customer-facing text leaves the desk, a second pass with fresh context or a person reviews it (`pricing-stakeholder-review`). The review states whether it was independent.

## Honest limits

Skills that cannot run scripts say so and mark figures unconfirmed. Platform facts about Google products are carried from another project and are not re-verified here (`adapters/google/platform-facts.md`).
