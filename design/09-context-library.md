# Context library and setup

Status: draft for confirmation. Mirrors the Sales-OS pattern (`workspace/context-library/`, `sos-setup`, read-mostly, people approve changes).

## Principle
The product is the same for every company. Everything that differs lives in the instance: `workspace/context-library/`. Council members, thresholds, floors, systems and contacts are never written into skills. Skills read the library; blank values come back as Unknown with the file to fill. Rule D7.

## Files (workspace/context-library/)
| File | What it holds | Read by |
|---|---|---|
| business-info.md | Company, product families, customer segments (TMC, OTA, airline, hotel, corporate), competitors, how revenue is earned | all skills |
| pricing-governance.md | Council: members, chair, quorum, cadence. Decision rights. Approval matrix: discount bands, margin floors, who approves each. Delegated deal desk authority. Escalation. Override authority. Time targets (marked proposed until agreed) | deal-desk-triage, deal-desk-review, account-price-fit, council-decision-pack |
| product-catalog.md | Product ids, type, unit, value metric, owner (product manager), cost-to-serve source, status | corridor, price book, release |
| deal-structures.md | How anchor deals work at this company: incentive types and tiers paid to agencies, term, renewal, notice terms, price protection and most-favoured clauses, what is normally traded | account-price-fit, price-change-proposal |
| systems-and-data.md | Where the price book, usage, invoices, CRM and billing live; export formats; approved tools; platform now and after the move | all skills that need data |
| rights-handoff.md | Product manager contact, how hand-off lists are sent, how answers come back, format | rights-handoff, price-book-release |
| guardrails.md | What must not leave the workspace; approved tools for customer data; rules for outside research | all skills |
| writing-style.md | Examples and rules for packs, memos and customer-facing text | council-decision-pack, deal packages |
| lessons.md | Learning log written by pd-ratchet | pd-ratchet, pd-start |
| analogs/ | Dated analog entries (public sources only), seeded from the product's verified items | analog-research |

Other instance folders: `accounts/<account>/` (account price sheets, deal packages), `price-book/` (current CSV, change log, notice calendar), `outputs/` (reviews, packs, decision log).

## pd-setup interview
Order, three questions a turn, summary after each section, Unknown is a valid answer, nothing written until the user approves:
1. Business and products: what is sold, to whom, how revenue is earned.
2. Governance: Council members and chair, who decides what, discount bands and margin floors, deal desk authority, target response times.
3. Deal structures: anchor deal mechanics, incentives paid, tiers, notice and protection terms, what is usually traded.
4. Systems: where price book, usage and invoice data live; export formats; platform now and after the move.
5. Rights hand-off route with the product manager.
6. Guardrails and writing style.
Output: the files above, a list of what changed, and the five most important items still Unknown.

## Release gate link
price-book-release warns when pricing-governance.md or product-catalog.md still contains template text, because approval routes and floors cannot be checked against nothing.

## Different per company
A second company gets its own instance (new-instance), its own library, and the same product. Upgrades never touch `workspace/` or `local/`.
