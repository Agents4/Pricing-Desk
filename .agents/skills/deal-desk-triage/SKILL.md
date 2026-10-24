---
name: deal-desk-triage
description: Run the daily deal desk. Ranks open pricing requests by overdue and due date, routes each to the right skill, runs account price fit for anchor-deal accounts, and keeps the exception log current. Use when starting the day on the deal desk, when several requests are open, or when someone asks what to work on first.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill ranks the pasted list by hand and says the script was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, templates/exception-log.md, templates/deal-package.md"
---

# Deal desk triage

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

The daily rhythm of the deal desk. It decides the order of work and who handles each request. It does not price anything itself.

## When to use

- Start of the working day, or when more than one request is open.
- A new request arrives and the desk must decide what handles it.
- Someone asks what is overdue or what to work on first.

Not for: reviewing one deal in depth (`deal-desk-review`), a data licence (`data-license-pricing`), the weekly realization review (`price-realization-analysis`).

## Inputs

A list of open requests: id, account, product, request type, total contract value, requested discount, received and due dates. A CSV is best (see `examples/requests.csv`). Read `pricing-governance.md` for the discount band the desk may approve alone; if it is a template, the band is Unknown. Read the exception log in `workspace/` if one exists.

## Procedure

1. **Rank with the script.** Run `scripts/triage_rank.py --in <file> --today <date>`; add `--band-pct N` only when the band is known from the context library. Order: overdue first, then due soonest, then larger value.
2. **Confirm the route** for each row: non-standard quote to `deal-desk-review`; API or data access request to `api-access-request`; data licence to `data-license-pricing`; renewal to `deal-desk-review` with `account-price-fit`; standard quote from the price book with no review.
3. **Anchor-deal accounts.** If the account has an anchor deal (see `deal-structures.md`), run `account-price-fit` before `deal-desk-review`. Do not review an add-on in isolation.
4. **Check the exception log.** Mark rows whose exception has expired or whose get has not arrived. List unrequited concessions with owner and date.
5. **Name what blocks.** For each request, the missing input and who supplies it. A rights question goes to `rights-handoff`.
6. **Do not approve.** The desk recommends; the approver named in `pricing-governance.md` decides. If it is Unknown, say so.

## Output

1. **Today in one line**: how many open, how many overdue, the first request to work.
2. **Ranked table**: request, account, route, due, band flag, blocker.
3. **Exception log changes**: rows to add, close or chase (use `assets/exception-log.md`).
4. For any request ready to move, start `assets/deal-package.md`.
5. Four-part handoff.

## Quality gate

- The ranking came from the script, or the response says it was ranked by hand.
- Band flags appear only when the band came from the context library or the user.
- Every request has a route and an owner, or is marked Unknown with the question.
- No request is marked Approved. Status stays Draft or For decision.
- Customer-specific prices stay in this output and are not copied into general summaries.
