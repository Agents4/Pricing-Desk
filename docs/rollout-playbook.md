# Rollout playbook

A staged start. Each step ends with something the desk can use and something it can check.

## Week 0: decide where it runs

Pick the surface (`adapters/google/README.md`): Gemini CLI for the analysts who run scripts, Gemini app skills for people who only need the method, notebooks for lookup. Confirm the data policy for each. Verify the platform list in `platform-facts.md`.

## Week 1: set up

Create the instance and run `pd-setup`. It asks one question at a time and fills the context library: business info, governance (Council, decision rights, bands, floors), product catalog with the granted right per line, deal structures including the anchor GDS deal and how incentives work, systems and data, the hand-off route to the product manager, guardrails, writing style. Blanks stay Unknown. The check: no skill output contains a number the library did not supply.

## Weeks 2 to 3: the deal desk

Start the daily rhythm with `deal-desk-triage` on real open requests. Use `account-price-fit` for accounts with an anchor deal. Use `api-access-request` for any request for new or expanded API access, asking the purpose first. Keep the exception log. Check: every request has a route and an owner; every concession has a get.

## Week 4: the weekly review

Run `weekly-pricing-review` on the same day each week from billing lines and API usage. Check: realization against last week is shown, causes are labeled, and three actions have owners.

## Month 2: the Council

Issue the first `council-decision-pack` with the lead time the Council sets. Run `pricing-stakeholder-review` on each proposal. Check: decisions are made in the meeting and logged by a person.

## Quarter 1: review and release

Run `quarterly-price-review`; import the existing price book with `price-book-import` if one exists, then `price-book-builder`, then `price-book-release` with the checker in release mode and the notice calendar. Hand the rights list to the product manager with `rights-handoff`. Check: zero data or API lines without a stated granted right.

## Always

After any miss, run `pd-ratchet`. Keep eval cases for each lesson. Re-check analog and competitor entries on the schedule the company sets.

## Not decided here

Time targets, thresholds and the Council calendar are the company's. This playbook names none.
