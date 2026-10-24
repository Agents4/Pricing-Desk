---
name: price-book-release
description: Release a price book for quoting. Runs the checker in release mode, writes the change log against the previous version, builds the customer notice calendar from contract terms, confirms the rights hand-off list is current, and lists what must be approved. Use when doing the annual release, when a new version goes to quoting, or when a Council-approved change takes effect.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill walks the checklist by hand and says the checks were not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Price book release

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A price book is released once, to quoting, with a log of what changed and a calendar of who must be told. This skill prepares the release. A person approves and publishes it.

## When to use

- Annual release, or any new version going to quoting.
- A Council-approved change is about to take effect and customers need notice.

Not for: building or editing lines (`price-book-builder`), importing an old book (`price-book-import`), deciding a change (`price-change-proposal`).

## Inputs

1. The new price book CSV and the previous released version.
2. The Council decision that approved the changes, with date (decision log). Without it the release is a draft.
3. A contracts file for notice: contract id, account, notice days, price protected until. Notice days are contract values; blank is Unknown.
4. The effective date and today's date.
5. `pricing-governance.md` and `product-catalog.md`. If either is still a template, warn at the top: the release cannot be checked against governance.

Ask one question at a time for what is missing.

## Procedure

1. **Check in release mode.** `python price-book-builder/scripts/check_price_book.py --pricebook <new> --mode release`. A missing floor, or a data or API line with no stated granted right, is an error. Do not release with errors.
2. **Write the change log.** `scripts/price_book_diff.py --old <old> --new <new>`. Match every change to a Council decision.
3. **Build the notice calendar.** `scripts/notice_calendar.py --in <contracts> --effective <date> --today <date>`. Show where the effective date cannot be met, where a price protection blocks it, and where notice is Unknown.
4. **Refresh the rights hand-off.** Run `rights-handoff` for the new book and show open rows. Open rows do not block pricing but are listed in the release note.
5. **Independent review.** Run `pricing-stakeholder-review` on the diff, or ask a person to. State which.
6. **Release note.** What changed, effective date, who is told by when, open rights rows, open questions. Status For decision until a person signs off.

## Output

Header; the answer (releasable or not, and why); checker result; change log; notice calendar; rights hand-off status; review note; sign-off line for a named person; four-part handoff.

## Quality gate

- The checker ran in release mode with zero errors, or the release is marked blocked.
- Every change in the log traces to a Council decision, or is flagged unapproved.
- No notice period or protection date is assumed; Unknown is listed for Legal.
- Every data and API line states the granted right.
- The release is never worded as published or approved; a person does that.
- Nothing is sent to a customer.
