---
name: competitive-price-scan
description: Make a dated, sourced check of competitor prices from public pages, log each price with its unit and the right or scope it covers, and refuse to quote anything without a source and access date. Use when a competitor moves, when a deal cites a rival price, before a price change goes to the Council, or at the quarterly review.
compatibility: "Any Agent Skills client with web search and fetch. Scripts need Python 3.8+; without web access the skill logs what the user supplies and marks it unverified."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# Competitive price scan

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A rival's price is a claim until it has a source and a date. A price without the unit or the right it covers cannot be compared. This skill keeps a log that is safe to quote.

## When to use

- A deal cites a competitor price (see `deal-desk-review`).
- A competitor changed price or packaging.
- Before a price change proposal goes to the Council.
- The quarterly review.

Not for: structure research across other markets (`analog-research`), willingness to pay (`wtp-study-design`).

## Inputs

The competitors and products to check. Previous scan log in `workspace/outputs/`. For a deal-driven check: what the rep or customer said, who said it and when. That is a lead (U), not a price, until a public page confirms it. Ask one question at a time.

## Procedure

1. **Public pages only** (rule 11): the competitor's pricing, documentation, announcement or terms pages. No logins, no contacting competitors, no customer data in queries.
2. **Fetch and read** each page. Record price, currency, unit, what it includes and the right or scope it covers (what the buyer may do). If scope is not stated, write Unknown and do not call the price comparable.
3. **Log one row per price** in a CSV with competitor, product, unit, price, currency, right_or_scope, source_url, access_date, notes (see `examples/scan.csv`).
4. **Check the log** with `scripts/check_scan_log.py --in <file> --today <date>`, adding `--max-age-days N` only if the company has a freshness rule. Unverified rows are not quoted.
5. **Compare like with like**: same unit, same scope. Show where ours sits and what differs. If a unit differs, convert with a script and show the inputs.
6. **Say what changed** since the last scan, and what was unreachable.

## Output

Header; the finding in one line; comparison table of verified rows only; a list of unverified leads with who said them; changes since last scan; four-part handoff. Status Draft.

## Quality gate

- Every quoted price has a web address and an access date, and the checker passes for those rows.
- Hearsay is listed as a lead, never in the comparison table.
- Prices are compared only when unit and scope match, or the difference is stated.
- Vendor pages are dated snapshots; the output says so.
- Nothing is attributed to a competitor that the page does not state.
