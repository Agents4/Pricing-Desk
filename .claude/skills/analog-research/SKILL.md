---
name: analog-research
description: Research how similar products are priced, inside or outside travel, using public sources only. Finds analogs, records each with URL, access date, unit, metric, granted right and a comparability score, and says what each suggests and does not show. Use when pricing a new construct with no history, when a competitor or adjacent market moves, or at the quarterly review to refresh the analog library.
compatibility: "Any Agent Skills client with web search and fetch. Scripts need Python 3.8+; without web access the skill works from sources the user pastes and says nothing was verified."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, methodology/frameworks.md, templates/analog-entry.md"
---

# Analog research

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A new construct has no price history. Similar products, inside or outside the industry, show what units, metrics and fences others have tried and what happened. They are evidence about structure, not a price to copy.

## When to use

- A new product, metric or right has no price history (`data-price-setting`, `packaging-design`).
- A competitor or adjacent market moved (`competitive-price-scan`).
- The quarterly review (`quarterly-price-review`) refreshes the library.

Not for: dated competitor price checks on our own market (`competitive-price-scan`), or willingness-to-pay evidence from our customers (`wtp-study-design`).

## Inputs

The construct to price in one sentence: product, buyer, use, candidate unit. Where to look is the analyst's choice: same industry, adjacent (other data and API businesses), or far (other machine-access pricing). Existing entries in `workspace/context-library/analogs/`. Ask one question at a time.

## Procedure

1. **Public sources only** (rule 11). Search the open web; no logins, no contact with competitors, no customer data in queries. Prefer the company's own pricing or announcement page; otherwise press or analyst coverage, marked secondary.
2. **Fetch the page** and read it. A search result is not a source. If a page cannot be reached, say so, write the entry as to verify, and never fill gaps from memory.
3. **Record each analog** with `assets/analog-entry.md`: source URL, published and access dates, unit, metric, right or use granted, comparability as "N of 5" with the reason (1 to 5; when an analog becomes a market comparable in `data-price-setting`, it is entered as N ÷ 5). Quote numbers exactly and tag them F with the source.
4. **Say what it suggests (I) and what it does not show.** One analog is an anecdote. Name the structure, not the price.
5. **Check the library** with `scripts/check_analogs.py --dir workspace/context-library/analogs`, adding `--today` and `--max-age-days` only if the company has a re-check rule.
6. **Summarise** the structures seen, the ones to test, and the ones to avoid, with the analogs behind each. See `references/frameworks.md` for the named methods and their verification status.

## Output

Header; the finding in one line; a table of analogs (name, unit, metric, right, comparability, date); structures worth testing; what could not be verified; four-part handoff. Entries saved to the analog folder after the user agrees.

## Quality gate

- Every entry has a web address and an access date, and the checker passes.
- Numbers are quoted from the page, not remembered.
- Secondary sources are marked secondary; no claim goes further than the source.
- Comparability is scored with a reason, and the buyer, use and unit are compared, not just the product.
- No price is recommended from analogs alone.
