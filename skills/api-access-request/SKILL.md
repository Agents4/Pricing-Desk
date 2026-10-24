---
name: api-access-request
description: Handle a request for new or expanded API access by asking what the customer will do with the responses, screening usage for patterns that look like collecting data rather than serving bookings, and pricing the scope that fits. Use when a customer or rep asks for an API key, a limit increase, a new endpoint, or when usage suggests bulk collection.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted figures and says the screen was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# API access request

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

An API key is sometimes asked for to serve bookings and sometimes to collect data. They are different products with different rights and prices. This skill finds out which, and prices the scope that fits.

## When to use

- A customer or rep asks for a new key, a higher limit, a new endpoint or an expanded use.
- Usage on an existing key looks unlike its segment.
- `deal-desk-triage` routes an `api_data_request` here.

Not for: tier design (`api-usage-tier-fit`), a data licence the customer asked for by name (`data-license-pricing`), whether we hold the right (`rights-handoff`).

## Inputs

1. **Purpose**, in the requester's words: what will be done with the responses, for whom, and how long they are kept. Ask when the request does not say. One question at a time.
2. **Usage**, if a key exists: searches, bookings, distinct queries, retention if known (CSV, see `examples/keys.csv`).
3. **Segment median look-to-book** and the **screen multiple**. Both are company values from `pricing-governance.md` or the API policy in `systems-and-data.md`. There is no default. If the multiple is Unknown, ratios are shown and nothing is flagged.
4. The nine rights in `references/operating-rules.md` (rule 8): which does the stated purpose need?

## Procedure

1. **Classify the purpose.** Serving the customer's own booking traffic is standard API use. Collecting, storing, analysing in bulk, rebuilding, reselling or feeding AI is a data right and is priced as one.
2. **Screen usage** with `scripts/harvest_screen.py --in <file> --segment-median-l2b N [--multiple X]`. The screen reports look-to-book, the multiple of the segment median, and the share of distinct queries. A high distinct-query share with a high ratio is a pattern worth a question. A flag reads "possible data collection, to confirm". It is never a finding against the customer.
3. **Ask the account owner** for any flagged key, without accusing. Record the answer.
4. **Name the granted right** the request needs. If it is more than API serving, price it with `data-license-pricing` and hand the rights question to the product manager with `rights-handoff`.
5. **Price the scope.** Standard API use goes to the tier in the price book (`api-usage-tier-fit`). Anything wider is a different line with a different price. Never quote bulk or retention use at a per-call booking rate.
6. **Account context.** If the account has an anchor deal, run `account-price-fit` before offering any concession.
7. **Recommend**: approve standard access, approve with a limit or term, price as a data right, or decline. Name the approver from the approval matrix, or Unknown.

## Output

Header; recommendation in one line; purpose and right table; screen results; open questions (product manager, Legal, account owner); proposed scope and price line, if any; four-part handoff. Status Draft.

## Quality gate

- The purpose is stated, or the first open question is the purpose.
- Every ratio came from the script or is shown with its inputs.
- No threshold appears that did not come from the context library or the user.
- Flags are worded as questions to confirm, not conclusions.
- A right wider than API serving is never priced as API serving.
- Nothing is sent to the customer; no key is issued or revoked by this skill.
