---
name: pd-setup
description: Set up the Pricing Desk OS for a company by interviewing one question at a time and writing the context library: business info, governance (Council, approval matrix, discount bands, margin floors), product catalog, deal structures, systems, rights hand-off, guardrails and writing style. Use when starting a new instance, when the context library is empty or template text, or when company facts or thresholds change.
compatibility: "Any Agent Skills client. File access recommended to write the library; otherwise returns each file as text with a filing note."
metadata:
  version: "1.0.0"
  layer: system
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, shared/interview-protocol.md, scaffold/workspace/context-library/business-info.md, scaffold/workspace/context-library/pricing-governance.md, scaffold/workspace/context-library/product-catalog.md, scaffold/workspace/context-library/deal-structures.md, scaffold/workspace/context-library/systems-and-data.md, scaffold/workspace/context-library/rights-handoff.md, scaffold/workspace/context-library/guardrails.md, scaffold/workspace/context-library/writing-style.md"
---

# Pricing Desk setup

Read `references/operating-rules.md`, `references/capabilities.md` and `references/interview-protocol.md`. Outputs carry the header in `references/output-conventions.md`. The files to produce follow the templates `references/business-info.md`, `references/pricing-governance.md`, `references/product-catalog.md`, `references/deal-structures.md`, `references/systems-and-data.md`, `references/rights-handoff.md`, `references/guardrails.md` and `references/writing-style.md`.

Fill the context library so every other skill uses this company's thresholds, Council and systems. Rule 14: nothing here is a default. Write only what the user says.

## When to use

- A new instance, or the context library is empty or `status: template`.
- The Council, bands, floors, products, systems or hand-off route have changed.
- A skill returned Unknown for a company value and the user wants to fill it.

Not for: researching the company (setup records what the user says), or deciding a price.

## Inputs

The user's answers, one at a time. Optional documents they supply: org chart, approval policy, product list, sample packs, a price book. Read the current library files first.

## Procedure

1. **Check state.** Read the existing files. Say which are filled and which are template. Offer to start with the one that unblocks the most (usually governance).
2. **Interview one question at a time**, in this order, following `references/interview-protocol.md`. Give an example of the kind of answer you need. Follow up on a thin answer before moving on.
   - Business and products: what the company sells, to whom, how revenue is earned (including incentives paid to agencies).
   - Governance: Council members and chair; who proposes and who approves each decision; discount bands and margin floors by product family (the floor is a share of price); the largest total discount an account may reach; deal desk authority and escalation path; target response times (label as proposals until agreed). Then the **review parameters**, one at a time, because every flag and window in the skills reads them: trend windows, minimum deals to cite, realization and backtest windows, renewal review window, cost-change threshold, reconciliation tolerance, freshness limit, the harvest-screen settings, and the price-corridor settings (expected discount, value cap, weights, cutoffs). It is fine for the answer to be "we have none yet": record Unknown.
   - Deal structures: how anchor deals work, incentives paid and how they are tiered and measured, look-to-book clauses, notice and price-protection terms, what is normally traded, the value of each get the Council would accept, and what each give costs us.
   - Systems: where the price book, usage, invoices, deal log, cost to serve and CRM live now and after the move; export formats; approved tools; who owns metering and unit definitions; who signs off data checks.
   - Rights hand-off: product manager contact, how lists are sent, how answers return.
   - Guardrails and writing style: what must never leave, who reviews packs; two or three examples they are proud of and rules, not adjectives.
3. **Summarize after each section** in two to four lines and ask to confirm or correct. List what is still Unknown.
4. **Draft the file** with the template headings. Use the user's words. Mark anything not said as Unknown. Keep `status: template` until every required field in the file is answered or explicitly Unknown by the user; then set `status: filled` and the review date.
5. **Approval gate.** Show the file. Write it to `workspace/context-library/` only after the user approves. Without file access, return it with a FILING NOTE.
6. **Close.** List the five most important items still Unknown and who could answer. Offer the next step: a first deal review, the price book import, or the weekly review.

## Output

Header, then the files written (or the text), what changed, and the five Unknowns. No other analysis.

## Quality gate

- Nothing invented about the company, its people or its thresholds. Gaps say Unknown.
- One question per turn; the user approved the final text before it was written.
- No customer-specific prices, usage or credentials recorded.
- Proposed time targets are labeled proposals until the user agrees them.
