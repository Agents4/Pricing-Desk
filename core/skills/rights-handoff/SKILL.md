---
name: rights-handoff
description: Build the hand-off list of data and API products and the right each price grants, send it by the route in the context library, and read the product manager's answers back against the price book. Use when a price book is imported or released, when a new product or right is priced, when a customer asks for a wider use, or when asked whether we may grant a right.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill builds the list by hand from pasted lines and says the script was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Rights hand-off

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Pricing states the right it grants. The product manager decides whether we hold what that right needs. This skill is the bridge: it asks, and it reads the answer back. It never answers.

## When to use

- A price book is imported, released or changed.
- A new product, or a wider right on an existing one, is being priced.
- A customer asks for more than the price grants.
- Someone asks "do we have the right to...". The answer is: that is the product manager's call; here is the list entry.

Not for: assessing rights held (the separate Rights Desk), pricing the right (`data-license-pricing`).

## Inputs

The price book (`conferred_right` on every data and API line). The route from `rights-handoff.md` in the context library: contact, how lists are sent, how answers return, planned response time. Blank is Unknown; ask one question at a time. Optionally `rights_answers.csv`: product_id, conferred_right, answer, date, who.

## Procedure

1. **Build the list.** `scripts/rights_list.py --pricebook <file> [--answers <file>] [--out product_rights_handoff.csv]`. One row per product and right, ranked by revenue where known.
2. **List the gaps.** Data or API lines with no stated granted right cannot be asked about. Send them back to `price-book-builder`.
3. **Send by the route on file.** Prepare the message and the file; ask before sending anything. If the route is Unknown, say so and offer `pd-setup`.
4. **Read the answers back.** Show each answer exactly as written, with date and author. Do not summarise it into cleared or not cleared; the product manager's wording stands. If a line's right was answered as not grantable, tell the user and recommend removing the line; the Council decides.
5. **Update the status** on the pack or release that waits for it: open, answer on file, not needed.
6. **Keep pricing moving.** An open row does not block pricing work; a price is labelled pending the rights answer.

## Output

Header; the answer (open rows and rows with an answer); the list table; gaps; draft message to the product manager (not sent); four-part handoff.

## Quality gate

- The skill never states whether we hold a right.
- Every row names a product, a right granted from the nine, and an answer or Open.
- Answers are shown verbatim with date and author.
- The message is a draft; nothing was sent without approval.
- Customer names do not appear in the list; products and rights do.
