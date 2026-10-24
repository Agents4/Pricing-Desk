---
name: api-usage-tier-fit
description: Analyze customer API usage against their plan and the price book to find tier mismatches, overage exposure, look-to-book profile, agent-traffic patterns, signs that customers collect data through the API, and upsell, downgrade, or renewal pricing candidates. Use when monthly usage reviews, renewal prep, and metering design questions.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted data and says the check was not run."
metadata:
  version: "1.1.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

# API Usage and Tier Fit

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Show how customers actually use an API product, whether their plan fits, and what pricing action follows.

## When to use

- Monthly or weekly API usage reviews, renewal preparation, and metering design questions.
- A customer's plan looks wrong for the way they use the API.
- Usage looks like machine traffic or like collecting data.

Not for: pricing a data licence request (`data-license-pricing`) or reviewing a quote (`deal-desk-review`).

## Inputs

Context library files read: `product-catalog.md`, `systems-and-data.md`. If a file still says `status: template`, treat its values as Unknown.

1. **Usage data** by customer and day or week: call counts by call class (for example search, price, book, post-booking, insights queries), bookings or conversions, error and throttled calls, peak rate.
2. **Current plan** per customer: tier, commit, included volume, overage rate, rate limits, contract end date.
3. **Price book** with tiers, units, and overage rules.
4. **Unit catalog** (call class definitions), if available.

If call classes are not defined in the data, ask for the mapping before analyzing; do not infer classes from endpoint names without confirmation.

## Procedure

1. **Validate the data.** Check coverage by day, missing customers, duplicate rows, and unit consistency. Report gaps.
2. **Profile usage with code** per customer: monthly volume by call class, trend (3 and 6 month), peak versus average, look-to-book ratio (search or price calls per booking), and share of calls throttled or erroring.
3. **Tier fit.** Compare actual and projected volume with the plan: utilization of commit, overage incurred, and what the bill would be on each tier at the same usage. Mark each customer: right-sized, under-using (downgrade or churn risk), over-using (upsell or overage exposure), or unusual.
4. **Look-to-book check.** Flag customers whose ratio is far above their segment median; these consume capacity without conversion and may need a ratio-based fee or rate-limit change.
5. **Agent-traffic flags.** Identify patterns that look automated or agent-driven: very high call rates, flat hourly distribution, repeated near-identical queries, large bursts. Mark them as "possible machine traffic, to confirm" and never as fact.
6. **Harvest check.** For each customer, compute: distinct-query ratio (distinct origin, destination and date combinations over total search calls), look-to-book against the segment median, calls per key against bookings, coverage of the market swept, and the share of calls with no booking behind them. Read `../price-book-builder/references/api-access-scope.md`. Flag customers whose pattern looks like collecting data rather than serving bookings as "possible data collection, to confirm". Never call it misuse. A flagged customer is buying the booking right and using a data right. Options for the account owner: price the use as a data licence with a minimum commitment, add a look-to-book or distinct-query fence with an overage rate, set a retention term, or move them to a data product. Rate limits alone are not a price.
7. **Renewal pricing view.** For customers renewing within the renewal review window set in `pricing-governance.md` (ask if it is Unknown), show current spend, usage-implied spend, suggested tier, and the range of price actions that keep the customer on a fair value metric.
8. **Metering questions.** List unit definitions that caused ambiguity in the analysis, for the Pricing Operations Manager.

## Output

1. **Headline findings** (three to five bullets, each with a number).
2. **Tier-fit summary table**: counts and revenue by status (right-sized, under-using, over-using, unusual).
3. **Top 15 action list**: customer, finding, suggested action, owner role, contract end date.
4. **Look-to-book outliers**, **possible machine traffic** and **possible data collection** tables (with the figures behind each flag).
5. **Renewal pipeline view**.
6. **Metering and data questions.**
7. **Inputs and assumptions used.**

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute with code; show the figures and source files.
- Recommend actions as options for the account owner to review before any customer outreach. Never draft or send outreach from this skill.
- Do not name a customer as a risk without showing the figures that support it.
- Treat customer usage as confidential: use it only for the analysis requested.
- A flag is a question for the account owner, not a finding against the customer.
- Do not change plans or prices. Propose tiers within the current price book, and flag when a new tier would be needed.
