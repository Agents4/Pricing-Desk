---
name: operating-rules
description: The rules every Pricing Desk OS skill follows, and the checks that show a rule was followed
---

# Operating rules

Seven rules for every output, seven rules for pricing. Each has a check. A rule with no check is advice.

## Every output

1. **Answer first.** Line one is the answer or the decision needed. Detail follows.
2. **Trace to the goal.** Each output names the pricing decision it serves and who decides: a `Decision and owner:` line near the top.
3. **Sources and checks.** Tag every number F (fact, with a source), I (inference, with the logic), A (assumption, with owner and date to confirm) or U (unknown). Numbers that come from arithmetic come from a script, not from the model.
4. **Confidentiality.** Customer prices, usage, floors, incentive terms and supplier terms stay in the workspace. Mark each output `Handling: Internal` or `Handling: Shareable` and never put a customer name in a Shareable output without saying so.
5. **Four-part handoffs.** Anything handed to a person says what is done, what is not, what they must decide, and what to watch.
6. **The user decides.** Recommend, never approve, send, publish or change a system of record. Status stays `Draft` until the Council logs a decision.
7. **Independent review before anything leaves.** A pack, a price book or any customer-facing text gets a second pass (a person, or a fresh reviewer with the rubric in `references/output-check.md`) before it is used. Price books also pass the checker in release mode.

## Pricing

8. **Price the scope.** Every data or API price line states the right it grants to the customer, one of nine: internal_use, internal_analytics_shared_outputs, display_to_third_parties, redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding, ai_evaluation. An API price buys the use it names. If the use is collecting or keeping data, price it as a data licence with a minimum commitment, a retention term and audit.
9. **Compute, never estimate.** Corridors, realization, tier fit and tier tables come from the scripts, with inputs shown. If a script cannot run, say so and mark the number A.
10. **Only the Council approves.** Prices, floors, approval-matrix changes and exceptions above delegated authority are decided by the Pricing Council. Skills draft and recommend. The guard hook blocks edits that set a status to Approved.
11. **Public sources only for outside research.** Analogs and competitor checks use public pages with URL and access date. No login-gated scraping, no contact with competitors, no customer data in a search.
12. **Hand rights questions to the product manager.** Never say whether we hold a right. State the right the price needs and add the product to the hand-off list (`rights-handoff`).
13. **List is independent; the account enters through the deal desk.** List price and corridor are set per product with no knowledge of any account. Account context moves a deal price only through the deal desk, inside the approved discount band, as a give tied to a get, and logged. Never hide a concession in a list price.
14. **Company values come from the context library.** Council members, thresholds, discount bands, margin floors, notice terms, systems and contacts are read from `workspace/context-library/`. If a value is blank, write `Unknown` and name the file to fill. Never use a default threshold.

Usage-pattern and machine-traffic signals are always "usage pattern to confirm with the account owner". Never allege misuse and never assume intent.

## Checks

| Rule | How it is checked |
|---|---|
| 1, 2 | `pdos.py lint` on the output file; eval rubric |
| 3 | lint: no number in a table without a tag; script name and inputs shown |
| 4 | lint: Handling line present |
| 5 | lint: handoff section has four parts when present |
| 6, 10 | lint: Status is Draft or For decision (Approved and Decided are errors); the guard hook blocks adding either to a pricing artifact |
| 7 | review note attached; checker run in release mode for price books |
| 8 | checker: data or API line without a granted right is an error in release mode |
| 9 | the scripts compute and unit tests cover them; eval cases describe the expected behavior for a reviewer, they are not run automatically |
| 11 | lint: every analog row has a URL and an access date |
| 12 | eval case "do we hold the right" expects a hand-off, not an answer (read by a reviewer, not run automatically) |
| 13 | `account_waterfall.py` flags a discount with no valued get and routes a concession through the anchor to escalation; eval cases for the rest are read by a reviewer |
| 14 | scripts stop with exit 2 when a company value is missing and `pdos validate` flags numeric thresholds in skills and defaults in scripts (SK090, SK091); eval cases with an empty context library are read by a reviewer |

## Evidence tags in practice

`F`: shown in a document, system or script output, with where. `I`: derived from facts by stated logic. `A`: assumed for now; who confirms and by when. `U`: not known; listed under Missing with the question that would resolve it. One data point is low confidence, whatever its tag.
