---
name: api-usage-tier-fit
description: Analyze customer API usage against their plan and the price book to find tier mismatches, overage exposure, look-to-book profile, agent-traffic patterns, and upsell, downgrade, or renewal pricing candidates. Use for monthly usage reviews, renewal prep, and metering design questions.
---

# API Usage and Tier Fit

Show how customers actually use an API product, whether their plan fits, and what pricing action follows.

## Inputs to collect first

1. **Usage data** by customer and day or week: call counts by call class (for example search, price, book, post-booking, insights queries), bookings or conversions, error and throttled calls, peak rate.
2. **Current plan** per customer: tier, commit, included volume, overage rate, rate limits, contract end date.
3. **Price book** with tiers, units, and overage rules.
4. **Unit catalog** (call class definitions), if available.

If call classes are not defined in the data, ask for the mapping before analyzing; do not infer classes from endpoint names without confirmation.

## Process

1. **Validate the data.** Check coverage by day, missing customers, duplicate rows, and unit consistency. Report gaps.
2. **Profile usage with code** per customer: monthly volume by call class, trend (3 and 6 month), peak versus average, look-to-book ratio (search or price calls per booking), and share of calls throttled or erroring.
3. **Tier fit.** Compare actual and projected volume with the plan: utilization of commit, overage incurred, and what the bill would be on each tier at the same usage. Mark each customer: right-sized, under-using (downgrade or churn risk), over-using (upsell or overage exposure), or unusual.
4. **Look-to-book check.** Flag customers whose ratio is far above their segment median; these consume capacity without conversion and may need a ratio-based fee or rate-limit change.
5. **Agent-traffic flags.** Identify patterns that look automated or agent-driven: very high call rates, flat hourly distribution, repeated near-identical queries, large bursts. Mark them as "possible machine traffic, to confirm" and never as fact.
6. **Renewal pricing view.** For customers renewing in the next 180 days, show current spend, usage-implied spend, suggested tier, and the range of price actions that keep the customer on a fair value metric.
7. **Metering questions.** List unit definitions that caused ambiguity in the analysis, for the Pricing Operations Manager.

## Output format

1. **Headline findings** (three to five bullets, each with a number).
2. **Tier-fit summary table**: counts and revenue by status (right-sized, under-using, over-using, unusual).
3. **Top 15 action list**: customer, finding, suggested action, owner role, contract end date.
4. **Look-to-book outliers** and **possible machine traffic** tables.
5. **Renewal pipeline view**.
6. **Metering and data questions.**
7. **Inputs and assumptions used.**

## Rules

- Compute with code; show the figures and source files.
- Recommend actions as options for the account owner to review before any customer outreach. Never draft or send outreach from this skill.
- Do not name a customer as a risk without showing the figures that support it.
- Treat customer usage as confidential: use it only for the analysis requested.
- Do not change plans or prices. Propose tiers within the current price book, and flag when a new tier would be needed.
