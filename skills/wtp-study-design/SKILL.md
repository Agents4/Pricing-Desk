---
name: wtp-study-design
description: Design and analyze willingness-to-pay and value research for travel technology products such as APIs, software, and data products. Chooses the method, drafts the questionnaire and sampling plan, then analyzes results into price ranges and packaging implications. Use when launching a product, redesigning packaging, or validating a price.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted data and says the check was not run."
metadata:
  version: "1.1.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md, shared/interview-protocol.md, methodology/frameworks.md"
---

# Willingness-to-Pay Study Design

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`. Ask questions one at a time, as in `references/interview-protocol.md`.

Plan a pricing study that can change a decision, and analyze the results honestly. Two modes: **design** (before fieldwork) and **analyze** (after data arrives). Ask which one is needed if unclear.

## When to use

- Launching a product, redesigning packaging, or validating a price.
- A pricing decision depends on customer willingness to pay.
- Results from a study need analysis.

Not for: pricing from existing evidence only (`data-price-setting`).

## Inputs

Context library files read: `business-info.md`, `guardrails.md`. If a file still says `status: template`, treat its values as Unknown.

Design mode:

1. **The pricing decision** the study must inform (launch price, tier boundaries, bundle, new value metric, price increase).
2. **Product concept**: what it does, who uses it, how it is delivered, current alternatives.
3. **Target segments** and who in each buys or influences the decision (developer, product owner, procurement, agency owner).
4. **Hypotheses** about value drivers, price levels and value metrics.
5. **Constraints**: budget, timeline, access to customers, anything customers must not be asked.

Analyze mode: raw responses or interview notes, the instrument, the sample plan and the current price book.

## Procedure

### Design mode

1. **State the decision and the hypotheses** in two or three sentences each. If the study will not change the decision, say so and propose a cheaper method.
2. **Choose the method** and say why. Interviews and value-driver quantification suit early, enterprise, small samples. Van Westendorp (1976) or Gabor-Granger give a price range for a defined product. Conjoint or max-diff suit packaging, feature and tier trade-offs and need enough respondents. Past deals and win-loss are cheap and grounded in behavior. Prefer a combination when samples are small, which is usual in B2B travel technology. A practitioner suggestion: Van Westendorp for the range, Gabor-Granger for tier prices (see `references/frameworks.md`; originals "to verify").
3. **Plan the sample**: segments, quotas, how to recruit, the minimum useful size per cell, and what can and cannot be concluded at that size.
4. **Draft the instrument**: interview guide or questionnaire with neutral wording, no leading price anchors, screening questions, and value-metric questions (what unit should they pay for: calls, bookings, seats, records).
5. **Plan the analysis**: charts and tests, and what result would change the recommendation.
6. **Flag risks**: stated versus actual willingness to pay, buyer-user gaps, confidentiality, competition-law concerns when asking customers about competitors, and contact fatigue.
7. **Write the decision rule**: "if X, recommend Y."

### Analyze mode

1. **Check the data with code**: sample sizes by segment, completion, straight-lining, outliers, bias risks. Report these first.
2. **Compute results with code**: for Van Westendorp, the four price curves and the acceptable range; for Gabor-Granger, the demand curve and revenue-maximizing point; for conjoint, part-worths and simulated shares; for interviews, coded themes with counts and short quotes.
3. **Segment the results** and show where segments disagree.
4. **Translate to recommendations**: price range and recommended starting point, value metric, tier or bundle structure and fences. State confidence and what would raise it.
5. **List limits**: sample size, sampling bias, hypothetical bias, and what to test next in market.

## Output

Design mode: study brief (one page), instrument, sample plan, analysis plan, timeline and decision rule.

Analyze mode, in order: the answer to the decision, supporting figures, segment differences, recommended price and packaging, confidence and limits, a proposed in-market test.

File to `workspace/outputs/<yyyy-mm>/`. End with Missing items and the next step.

## Quality gate

Confirm each before finishing.

- All statistics computed with code, with sample sizes beside every figure.
- No stated willingness to pay presented as a demand forecast.
- No fabricated respondent data or benchmark. If no benchmark is supplied, none is cited.
- The research analyst fields the study and approves the findings. No customer is contacted from this skill.
- Respondent identities and customer-specific answers stay out of any summary.
