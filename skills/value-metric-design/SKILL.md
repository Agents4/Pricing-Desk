---
name: value-metric-design
description: Choose what to charge on. Lists candidate value metrics such as per search, per booking, look-to-book band, seats or data volume, scores them for visibility to the customer, meterability, scaling with value, predictability and resistance to gaming, and recommends one to test. Use when pricing a new product, when usage and value have drifted apart, or when look-to-book and value adds should drive an add-on price.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill scores by hand and says the script was not run."
metadata:
  version: "1.0.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, methodology/frameworks.md"
---

# Value metric design

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

The metric is what the price scales with. A good one rises when the customer gets more value, is visible to them, and is one we can meter. The wrong metric makes every discount conversation harder. See `references/frameworks.md` for the named methods and their verification status.

## When to use

- A new product or add-on needs a price structure.
- Usage and customer value have drifted apart (heavy callers who book little).
- The add-on is to be priced on look-to-book and other value adds.

Not for: the price level (`data-price-setting`), tier boundaries (`packaging-design`), cost to meter (ask engineering through `pricing-stakeholder-review`).

## Inputs

The product and what the customer does with it; who pays and who benefits; what we can already meter and how reliably; the cost drivers on our side; current metric if any; the rights granted. Evidence for each score: usage data, customer interviews, analogs (`analog-research`). Ask one question at a time.

## Procedure

1. **List candidates.** Include the current metric, a usage metric (per call), an outcome metric (per booking), a ratio or band (look-to-book), a capacity metric (seats, keys) and a flat fee.
2. **Score each** 1 to 5 against: visible to the customer, meterable by us, scales with value received, predictable for the customer, hard to game. Write the evidence behind each score. A missing score is Unknown, not zero.
3. **Run the scorecard**: `scripts/metric_scorecard.py --in <file>` (see `examples/metrics.json`). Weights are the user's; if none are given, the output says weights are equal and why that is an assumption.
4. **Check the interaction** with the account deal: if incentives reward bookings, say how the metric moves with them (`account-price-fit`).
5. **Check the right.** A volume metric on data that can be kept or reused prices the volume, not the use. State the right the metric covers.
6. **Recommend one metric and one fallback**, with the test that would show it wrong (`wtp-study-design`, a pilot) and the metering lead time engineering must confirm.

## Output

Header; the recommendation in one line; the scorecard with evidence; interaction and right notes; the test; open questions for engineering and the product manager; four-part handoff.

## Quality gate

- Scores have evidence or are marked Unknown; weights are the user's or declared equal.
- The metric is something the customer can see and we can meter; engineering confirms metering as a question.
- The granted right is stated for data and API metrics.
- A recommendation names what would make it wrong.
- No price level is set here.
