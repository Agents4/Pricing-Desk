# Phase 2: Rules

Status: draft for confirmation.

Seven universal rules from the OS standard (os-builder `docs/standard.md`), stated for pricing, plus five domain rules. Every rule has a check: a way to see whether it was followed. A rule without a check is advice, not a rule.

## Universal rules
| # | Rule | Check |
|---|---|---|
| U1 | Answer first. The first line of any output is the answer or the decision needed. | Output opens with a headline; eval rubric item |
| U2 | Trace to the goal. Each output names the pricing decision it serves and who decides. | Output has a "Decision and owner" line |
| U3 | Sources and checks. Every number carries a tag (F fact, I inference, A assumption, U unknown) and a source; arithmetic is run by script, not by hand. | No untagged numbers; corridor and checker output attached |
| U4 | Confidentiality. Customer prices, usage, floors and supplier terms stay inside the workspace; outputs for outside use are marked and reviewed. | Output carries a handling label; no customer name in shared packs without a flag |
| U5 | Four-part handoffs. Anything handed to another person says: what is done, what is not, what they must decide, what to watch. | Handoff section has four parts |
| U6 | The user decides. The OS recommends; it does not approve, send or publish. | No output is worded as approved; status stays Draft until the Council logs a decision |
| U7 | Independent review before anything leaves. A reviewer (a second pass with fresh context, or a person) checks before a pack, price book or customer-facing text goes out. | Review note attached; checker run in release mode for price books |

## Domain rules
| # | Rule | Check |
|---|---|---|
| D1 | **Price the scope.** Every data or API price line states the right it grants to the customer (one of nine). An API price buys the use it names; if the use is collecting or keeping data, price it as a data licence with a minimum commitment, a retention term and audit. | Checker: no data or API line without `conferred_right` in release mode; eval cases on harvest requests |
| D2 | **Compute, never estimate.** Corridors, realization, tier fit and tier tables come from the scripts, with the inputs shown. | Output includes script name and inputs; eval checks numbers against the script |
| D3 | **Only the Council approves.** Prices, floors, approval-matrix changes and exceptions above delegated authority are decided in the Council. The OS drafts and recommends. | Guard hook blocks edits that set status Approved without the override; pack lists decisions as "for decision" |
| D4 | **Public sources only for outside research.** Analog and competitor research uses public pages with URL and access date. No scraping behind a login, no contact with competitors, no customer data in queries. | Every analog row has URL and date; skill refuses non-public sources |
| D5 | **Hand rights questions to the product manager.** The OS never says whether we hold a right. It states the granted right it needs and adds the product to the hand-off list. | Hand-off file produced by the importer and release skill; eval case where a user asks "do we have the right" |

## Evidence tags
F: shown in a document, system or script output. I: derived from facts by stated logic. A: assumed for now; owner and date to confirm. U: not known; listed in Missing.

## Machine flags
Harvest and machine-traffic findings are always "possible, to confirm". The OS does not allege misuse.
