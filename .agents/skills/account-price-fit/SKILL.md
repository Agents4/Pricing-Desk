---
name: account-price-fit
description: Decide how far one product may sit below list inside a whole account relationship, and what must be gotten in return. Builds the account price sheet with the anchor deal, add-on economics, give-get plan, relationship test and options with computed numbers. Use when an add-on, upsell or renewal is priced for an account that already has an anchor deal such as a GDS agency agreement with incentives.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted data and says the check was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, templates/account-price-sheet.md"
---

# Account price fit

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

List price is account-blind. The account enters only here, through the deal desk, as a give tied to a get inside a Council-approved band. This skill never changes a list price.

## When to use

- An add-on or upsell is priced for an account that has an anchor deal (for example the GDS economic deal with a travel agency, where we pay incentives).
- A renewal bundles the anchor and one or more add-ons.
- `deal-desk-triage` routes a request here before `deal-desk-review`.

Not for: setting a list price (`data-price-setting`), a price change for the Council (`price-change-proposal`), a discount on an account with no anchor (use `deal-desk-review`).

## Inputs

Read `pricing-governance.md` (band, floors, approvers), `deal-structures.md` (how incentives are tiered and measured) and `product-catalog.md`. A file that says `status: template` means Unknown.

Ask one question at a time for what is missing:

1. Account and the anchor deal: term, annual revenue, incentives paid and how they are tiered, renewal date.
2. The add-on: product, unit, list price, floor, granted right (required for data and API), annual units, unit cost.
3. What the account asked for, and by when.
4. Usage history, for example look-to-book by period, and cost to serve.
5. Concessions already given to this account on any product.

## Procedure

1. **Roles.** Name the anchor, the upsell and the sweeteners available.
2. **Envelope.** Anchor revenue net of incentives and cost to serve; add-on revenue. Tag every figure F, I, A or U. Place the account as profit maker, neutral or taker only where cost to serve is supplied.
3. **Stand-alone price.** Take list and floor from the price book. Do not change them.
4. **Interaction check.** Incentives reward bookings; the add-on is priced on look-to-book and other value adds. Flag where the two pull against each other for this account. Flag, do not conclude.
5. **Give-get plan.** Every give has a get. Prefer a give through the value metric (a larger included allowance, a later threshold, a ramp) over a cut to the rate card. Floor, granted right, most-favoured-customer triggers and supplier-driven limits are not traded.
6. **Relationship test.** Can the customer decline the add-on without damage to the anchor, and would we accept that? State the add-on walk-away apart from the anchor.
7. **Precedent check.** Who will see the price; contracts with most-favoured terms; earlier concessions to this account.
8. **Options.** Write an input JSON like `scripts/account_waterfall.py` expects (see `examples/atlas-example.json`) and run it. Options: hold, trade, ramp or pilot, transparent bundle, defer. Do not compute by hand.
9. **Recommend one option** and the approvals the approval matrix requires. If the band or matrix is Unknown, say so; do not supply a figure.

## Output

Fill `assets/account-price-sheet.md`. One page: roles, envelope, stand-alone price and floor, interaction flags, give-get table, options with computed numbers, recommendation, approvals, precedent risk, Missing list. Status stays Draft. End with the four-part handoff.

## Quality gate

- Deal price on the add-on is never below floor without an exception request in the exception log.
- Every give has a get, or is logged as an unrequited concession with an owner.
- No concession is written into the list price.
- Data and API lines state the granted right. Whether we hold the right goes to the product manager (`rights-handoff`), not decided here.
- No band, floor or threshold appears that did not come from the context library or the user.
