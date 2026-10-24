# Skill spec: account-price-fit

Status: draft for confirmation. Wave 1. Stage 9 (deal desk). Called by deal-desk-triage and deal-desk-review.

## Purpose
Answer one question: given the whole relationship with this account, how far may the deal price on this product sit below list, and what must we get in return? Modeled on the two-level split in Sales-OS: the account view (Gold Sheet: the relationship) and the deal view (Blue Sheet: this product).

## What the owner told us (the anchor deal)
- The anchor is the GDS economic deal with a travel agency. We pay incentives to the agency.
- The add-on product (the upsell) is priced on look-to-book and other value adds.
- List price is independent of the account. The account is handled by the deal desk through discount.

## Design principle
Two layers. Layer 1, list: set per product from the corridor, account-blind. Layer 2, deal: list minus a discount decided by the deal desk, using account context, inside a Council-approved band. The skill works only in layer 2. Rule D6 (03-rules.md).

## Inputs
Needed: account, the anchor deal (term, volume, incentives paid and how they are tiered, renewal date), the add-on product with its list price and metric, requested price or terms. Helpful: usage history (look-to-book by period), cost to serve, a Sales-OS Gold Sheet for the account if one exists (read only), approval matrix, discount band.

## Procedure
1. **Roles.** Anchor, upsell, sweeteners.
2. **Account envelope.** Anchor value over the term net of incentives paid; add-on revenue; cost to serve, including search load from look-to-book. Label every number F, I, A or U. Place the account as profit maker, neutral or taker where data allows (whale curve idea; needs cost to serve).
3. **Stand-alone price.** List and floor from the corridor for the add-on and its granted right. Not changed here.
4. **Interaction check.** Incentives paid reward bookings; add-on price is driven by look-to-book. Check whether the incentive structure and the look-to-book terms pull against each other for this account. Flag, do not conclude.
5. **Give-get plan.** Gets: term, volume or booking commitment, minimum, look-to-book ceiling or threshold, retention and audit terms, reference. Gives: ramp, allowance on the value metric, pilot with a conversion price, support, credit. Prefer a give through the metric (a larger included allowance, a later threshold) over a cut to the rate card. Non-negotiable: floor, granted right, most-favoured-customer triggers, supplier-driven limits.
6. **Relationship test.** Can the customer decline the add-on without damage to the anchor deal, and would we accept that? State the walk-away for the add-on separately from the anchor.
7. **Precedent check.** Who will see this price: other accounts, public, contracts with most-favoured terms.
8. **Options at account level.** Hold, trade, ramp or pilot, transparent bundle, defer. Each with account-level economics, computed by script where inputs allow.
9. **Recommend** one option, with approvals needed under the approval matrix.

## Output
Account price sheet, one page: roles; envelope; stand-alone price and floor; interaction flags; give-get table; options with numbers; recommendation; approvals; precedent risk; Missing list. Status stays Draft. Four-part handoff.

## Quality gate
- Add-on deal price never below floor without an exception request.
- Every give has a get, or is logged as an unrequited concession with an owner.
- No concession sits inside list price.
- No statement about whether we hold rights; hand-off list updated instead.

## Open items to confirm with the owner
How agency incentives are tiered and measured; whether any look-to-book clause exists in the anchor contract; who may trade incentives against add-on terms; the discount band and who approves above it.

## Sources behind the method
Get-give concession trading (Richardson, page does not address pricing; the pricing use is our extension). Whale curve and cost to serve (Pragmatic Institute article; originator not credited on the page). Account-based pricing with guardrails (Monetizely, practitioner; statistics secondhand and not cited). Sales-OS Gold Sheet and Blue Sheet for the two-level structure.
