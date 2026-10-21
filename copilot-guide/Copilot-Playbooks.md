# Copilot Playbooks: Pricing Desk

*Add this file to your Pricing Desk notebook. Prices, customers and agreements in examples are invented. Playbooks are drafts for people to review; named people approve and Legal confirms rights.*

## How to use this file

1.  Add this file to the notebook as a reference.
2.  In a prompt, name the playbook: "Follow Playbook 5: Deal desk review."
3.  Attach or name the input files in the prompt. Do not paste whole contracts.
4.  Check the answer with the "Check before you use it" list, then save the result to a Page.

## Rules for every playbook

- **Inputs:** use only files named in the prompt or in the notebook. If a needed input is missing, list it and stop. Do not guess.
- **Evidence:** cite the file and location (sheet and cell, page, clause) for every figure and every contract statement.
- **Unknown is the default:** silence in a contract is never permission. Never say a use of data is allowed unless the register shows Granted or Conditional and Legal confirmed is Yes.
- **No legal conclusions:** summarize what the document says and where, then write the question for Legal.
- **Calculations:** show the inputs, the formula in words, and the result. No estimates in prose. Label every assumption.
- **Recommend only:** named people approve. Do not draft anything to send to a customer.
- **Confidentiality:** customer-specific figures stay in the request. Do not copy them into general summaries.
- **Format:** a one-line headline first, then tables. End with "Inputs and assumptions used" and "Missing".

### Vocabulary

| Term                       | Meaning                                                                                                                                                                                                                                                                                               |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Use rights (nine)          | internal_use, internal_analytics_shared_outputs, display_to_third_parties, redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding, ai_evaluation. Each AI use is its own right.                                                                          |
| Statuses                   | Granted, Conditional (record the conditions), Prohibited, Unknown (the default).                                                                                                                                                                                                                      |
| Most to least restrictive  | Prohibited, Unknown, Conditional, Granted.                                                                                                                                                                                                                                                            |
| Eligible to sell           | Granted or Conditional, and legal_confirmed = Yes. Everything else is not for sale.                                                                                                                                                                                                                   |
| Placeholder approval tiers | Use only if the desk has no approval matrix, and say so. Tier 0: discount up to 10 percent. Tier 1: beyond the band. Tier 2: above 250,000 USD total contract value, multi-year, or a cross-family bundle. Tier 3: above 1 million USD, below floor, MFN, exclusivity, or data redistribution rights. |

## Playbook 1: Register intake from agreements

**Purpose:** turn an agreement and a dataset description into proposed register rows with evidence. Copilot proposes; only Legal confirms.

**Attach:** the agreement as Word or PDF, a data dictionary if there is one, and the party's standard rights profile if you want deviations only.

### Steps

1.  Identify the agreement: parties, type, effective date, expiry, renewal, amendments, and what it supersedes.
2.  For each of the nine use rights propose Granted, Conditional, Prohibited or Unknown. Granted needs a clear provision. Conditional records the conditions. Silence or ambiguity is Unknown.
3.  Record evidence, one row per provision: document, clause or page, a one or two sentence summary in your own words, and a short quote of 20 words or fewer.
4.  Capture restrictions: redistribution, display, derivatives, each AI use, geography, term, exclusivity, confidentiality, attribution, audit, deletion, personal data, and withdrawal.
5.  Secondary processing: record any term on aggregation, anonymization, combining with other data, or derived products, with its conditions (minimum cohort size, no identification, delay). If the contract says nothing, write Unknown.
6.  If a standard profile is supplied, list only the deviations as exceptions, with the clause, and say whether each loosens or tightens the profile.
7.  List open questions for Legal, grouped, each with a priority.

**Output order:** summary counts by status, use-right table, evidence table, exceptions, open questions, and the decision requested from Legal.

### Check before you use it

- Every Granted or Conditional row has a quote and a location.
- No AI use is inferred from internal use.
- legal_confirmed is blank. Copilot never sets it.
- Open questions exist for every Unknown that a live deal depends on.

**Prompt to copy**

Follow Playbook 1: Register intake. Agreement: \[file name\]. Party: \[name\], type \[agency or supplier\]. Dataset: \[name and description\]. For each of the nine use rights give the status (Granted, Conditional, Prohibited, Unknown), a short quote of 20 words or fewer, the clause or page, and any conditions. If the agreement is silent or ambiguous, write Unknown. Add term, expiry, termination, audit, deletion, personal data, and change or withdrawal rights. Record any terms on aggregation, anonymization, combining or derived products. List open questions for Legal. Leave legal_confirmed blank. Output in this order: summary counts, use-right table, evidence table, open questions.

## Playbook 2: Price setting

**Purpose:** work out what to charge for a data product, with a floor, a value cap and a recommended price, before building a price book.

**Attach:** cost inputs, customer segments with value estimates and their source, market comparables with a comparability score from 0 to 1, willingness-to-pay points if any, and the list of eligible use rights from the register.

### Steps and formulas

1.  **Value metric:** pick the unit the price scales with. Test each candidate: does it rise with customer value, can it be metered and verified, is the bill predictable, is it hard to game, does it line up with cost and use rights. Choose one.
2.  **Cost floor per unit** = (annual fixed cost ÷ expected units + variable cost per unit + cannibalization per unit) ÷ (1 − royalty share − margin floor).
3.  **Value per unit** (per segment) = yearly value per customer ÷ units per customer × coverage factor. Coverage factor = current coverage ÷ reference coverage.
4.  **Value-based price** = value per unit × capture share (10 to 30 percent is a typical starting point). **Value cap** = value per unit × maximum capture share (default 50 percent). Weight segments by expected units.
5.  **Market reference** = comparability-weighted average of comparable unit prices. Show the range. Comparables with low comparability are context only.
6.  **WTP median:** use only with 5 or more points; 15 or more to rely on.
7.  **Blend:** 40 percent value-based price, 30 percent market reference, 30 percent WTP median. If an anchor is missing, share its weight across the others. Keep the result between the floor and the cap.
8.  **Realized price** is the blend. **List price** = realized ÷ (1 − expected average discount).
9.  **Extra use rights:** price of a right = base price + capture share × extra value per unit + extra cost per unit ÷ (1 − royalty share − margin floor). Price only rights that are eligible; list the rest as blocked.
10. **Sensitivity:** value capture ±20 percent, costs +20 percent, demand −30 percent, market reference −20 percent, and coverage if open rights items are resolved.

**Reading the result:** if the floor is above the cap there is no viable price (options: cut cost or scope, aim at a higher-value segment or right, spread cost across products, re-check the value estimate). If anchors differ by more than 1.5 times, find out why before averaging. If segment value-based prices differ by more than 1.5 times, consider fenced segment prices.

**Confidence:** High needs three anchors, value figures from pilots or contract data, 15 or more WTP points and two or more good comparables. Value figures that are only estimates, or fewer than 5 WTP points, mean Low or Medium. Present Low as provisional.

**Output order:** headline price and confidence, corridor table, segments, use-right ladder with blocked rights, sensitivity table, flags and next evidence, pilot plan with a decision rule, inputs and assumptions.

### Check before you use it

- Recompute the floor and one segment's value-based price yourself in Excel.
- Every input has a source; invented inputs are labeled as assumptions.
- No right is priced unless the register lists it as eligible.
- For the real price decision, run the price corridor script (ask someone with Python, or use Claude) and compare with this draft.

**Prompt to copy**

Follow Playbook 2: Price setting. Product: \[name\]. Inputs: \[file\]. Eligible use rights from the register: \[list or file\]. Build one table with: cost floor, value-based price and cap per segment, market reference, WTP median (only with 5 or more points), blended realized price, and list price at \[15\] percent discount. Write each formula in words and show the inputs next to each result. If the floor is above the cap, say there is no viable price and list options. Price extra use rights only if they are eligible. End with confidence (high, medium, low), the weakest input, and the evidence to collect next.

## Playbook 3: Price book

**Purpose:** turn prices into a controlled price book where every line is tied to a dataset and an eligible use right.

**Attach:** the corridor results from Playbook 2, the register export of eligible rights, existing prices and past deals.

### Steps

1.  Scope: list priceable rights (Granted or Conditional, Legal confirmed) and blocked rights, with the question blocking each.
2.  Choose the licensing unit, the delivery dimension only if cost or value differs, and the metering source.
3.  For each dataset set three anchors: floor, reference (median and range of realized comparable deals), value ceiling. Put the list price between floor and ceiling.
4.  Set the use-right ladder from the value each right adds. Do not apply standard multipliers.
5.  Add volume tiers with a tier model (all_units or graduated), a floor price per line, discount bands with the approval tier each depth triggers, term discounts, minimum commitments, overage, audit rights, and the conditions that travel with Conditional rights.
6.  Write the table with columns: line_id, dataset_id, use_right, delivery, unit, tier_min, tier_max, list_price, floor_price, currency, term_months, tier_model, status, version. Leave tier_max blank for the last tier. Status is Draft or Proposed; only the Pricing Council sets Approved.
7.  Run the manual checks below.

### Manual checks (report pass or fail per line)

| Check                  | Rule                                                                                                                            |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Register linkage       | Every line has a dataset_id and use_right that exist in the register as Granted or Conditional with Legal confirmed.            |
| Floor and list         | floor_price is at or below list_price on every line.                                                                            |
| Tier overlaps and gaps | Within a line, each tier starts right after the previous one ends. No overlaps, no gaps.                                        |
| Unit price and volume  | Unit price does not rise as volume rises.                                                                                       |
| Volume cliffs          | In all_units tiers, total cost at the first unit of a higher tier is not below the total cost at the top of the tier before it. |
| Rights ladder          | No broader right is priced below internal_use for the same dataset.                                                             |

**Output order:** headline, price book table, rationale per line, ladder logic, blocked list with owners, check results, Council decision list, inputs and assumptions.

**Prompt to copy**

Follow Playbook 3: Price book. Priceable rights: \[register export, only Granted or Conditional with Legal confirmed\]. Corridor results: \[file\]. Produce the price book table with columns line_id, dataset_id, use_right, delivery, unit, tier_min, tier_max, list_price, floor_price, currency, term_months, tier_model, status (Draft), version. Then run every manual check in the playbook and report pass or fail for each line with the numbers. List blocked rights with the question that blocks each.

## Playbook 4: Data licence pricing request

**Purpose:** decide what is being licensed, whether the desk is allowed to license it, and what to charge. The price is proposed; Legal confirms the rights before any quote.

**Attach:** the request, the register export, the price book, and customer context.

### Steps

1.  Restate the request in a table: dataset, fields, coverage, frequency, term, delivery, intended use.
2.  Classify each intended use as a use right, quoting the customer's words. Mark ambiguous cases. Show, resell, combine, and any training, retrieval or agent use are separate questions.
3.  Check each right against the register: allowed, allowed with conditions, not allowed, unknown. Include the register reference.
4.  Check personal data and supplier-confidential fields that need removal or aggregation.
5.  Only then price from the price book: base subscription, volume tier, use-right uplift, term discount, approved exception band. Show the waterfall. If no rule fits, give a range labeled as a proposal.
6.  Route: standard, Tier 1 or 2 for non-standard terms, Tier 3 for redistribution, AI use, exclusivity or a rights conflict.
7.  Draft the Legal escalation note: dataset, proposed use, register entry, the question, the deadline.

**Output order:** recommendation (quote, quote with conditions, escalate, decline) and tier, request table, use-right classification, rights check, price and waterfall or the reason none is given, conditions to request from Legal, escalation note, inputs and assumptions.

### Check before you use it

- If the register is silent, the answer is "rights unknown, escalate", not a price.
- No contract clauses are drafted.

**Prompt to copy**

Follow Playbook 4: Data licence pricing. Request: \[file or pasted text\]. Register export: \[file\]. Price book: \[file\]. Restate the request, classify each intended use as a use right quoting the customer's words, check each against the register (allowed, allowed with conditions, not allowed, unknown), and only then price from the price book with the waterfall. If any right is unknown, do not price it: write the Legal escalation note instead. Recommend the approval tier and name the rule.

## Playbook 5: Deal desk review

**Purpose:** turn a deal request into a decision-ready package for the approver. You recommend; a named person approves.

**Attach:** the deal request, price book, approval matrix, at least five comparable deals if available, and customer context.

### Steps

1.  Restate the request in a table: product, unit, quantity, list price, requested price, term, ramp, commit, overage.
2.  Build the waterfall: list value, each discount layer (volume, term, bundle, special), net price, total contract value, annualized value. For usage pricing, model commit, expected usage and overage at low, base and high usage.
3.  Check guardrails per line: discount versus band, price versus floor, margin versus family floor if cost is given, term and payment terms, non-standard clauses (MFN, exclusivity, price protection, redistribution or AI rights for data).
4.  Compare with similar deals on net price per unit and discount depth. Flag if this would become the new low.
5.  Assign the approval tier by the first rule tripped, and name the rule.
6.  List risks and open questions for Finance, Legal and Product.
7.  Draft two or three counteroffers that trade value for concessions (bigger commit for a deeper tier, longer term for a lower rate, smaller start with a ramp, removal of a clause), each with a waterfall.

**Output order:** one-line recommendation and tier, deal and waterfall tables, guardrail results, comparables, risks and questions, counteroffers, approval memo under 150 words, inputs and assumptions.

### Check before you use it

- Recompute the waterfall total in Excel.
- The tier is the first rule tripped, and the rule is named.
- Competitor prices appear only if supplied with a source; otherwise marked unverified.
- Nothing was sent to the customer.

**Prompt to copy**

Follow Playbook 5: Deal desk review. Deal request: \[file\]. Price book: \[file\]. Approval matrix: \[file or "use the placeholder tiers"\]. Comparable deals: \[file\]. Restate the deal, build the waterfall with every layer and formula shown, check guardrails (discount versus band, price versus floor, non-standard terms, data rights), compare with the deals, assign the approval tier by the first rule tripped and name it, list risks and questions for Finance, Legal and Product, give two counteroffers with waterfalls, and write an approval memo under 150 words. Do not contact the customer.

## Playbook 6: Price realization

**Purpose:** explain the gap between the price book and what customers pay, find where it leaks, and say what to do.

**Attach:** billing lines for the period, the price book version in force (with effective dates), the deal log or contract terms. Large files: ask for row counts first, then work month by month, or use Excel.

### Steps

1.  Reconcile first: row counts, nulls, duplicates, unmatched products, and the total against finance revenue. Stop and report if the gap is over 1 percent of billed revenue. Label later results provisional.
2.  Rebuild list value for each line from the price book version in force on the invoice date.
3.  Build the waterfall: list value, approved discounts, unapproved or unexplained discount, credits and adjustments, billing and metering gaps, realized revenue. Show USD and percent of list.
4.  Cut by product family, segment, discount tier, top 20 customers, contract vintage.
5.  Classify drivers: approved discount beyond guardrail, discount with no recorded approval, expired promotions still applied, unbilled usage, tier mismatch, credits and write-offs, price book errors, unit definition problems.
6.  Size and rank each driver by annual value and recoverability (easy fix, needs a customer conversation, needs a contract change).
7.  Recommend actions per top driver: owner role, step, expected recovery range, how it will be verified.

**Output order:** headline realization rate and largest driver, waterfall, top five drivers, customers and segments to review, recovery plan, data quality notes, inputs and assumptions.

### Check before you use it

- Approved discount is kept separate from unexplained discount; not all discount is leakage.
- No individual sales rep is named in broad summaries.
- The Analytics Lead signs off the data checks before results leave the desk.

**Prompt to copy**

Follow Playbook 6: Price realization. Files: billing lines \[file\], price book \[file\], deal log \[file\]. Period: \[month\]. First reconcile: row counts, nulls, duplicates, unmatched products, and total versus \[finance revenue\]. If the gap is over 1 percent, stop and report it. Then build the list-to-realized waterfall, separate approved discount from unexplained discount, rank the top five leakage drivers by annual value and how recoverable they are, and propose recovery actions with an owner role.

## Playbook 7: API tier fit

**Purpose:** show how customers use an API product, whether their plan fits, and what pricing action follows.

**Attach:** usage by customer and day or week by call class, current plans (tier, commit, included volume, overage rate, contract end), the price book, and call class definitions. If call classes are not defined, ask for the mapping; do not infer classes from endpoint names.

### Steps

1.  Validate data: coverage by day, missing customers, duplicates, unit consistency.
2.  Profile each customer: monthly volume by call class, 3 and 6 month trend, peak versus average, look-to-book ratio, share of calls throttled or erroring.
3.  Tier fit: commit utilization, overage incurred, bill on each tier at the same usage. Mark right-sized, under-using, over-using or unusual.
4.  Look-to-book outliers: far above the segment median.
5.  Possible machine traffic: very high rates, flat hourly pattern, near-identical queries, big bursts. Label "possible machine traffic, to confirm".
6.  Renewal view for contracts ending in 180 days: current spend, usage-implied spend, suggested tier, range of price actions.
7.  List metering questions where unit definitions were ambiguous.

**Output order:** headline findings with numbers, tier-fit summary, top 15 actions, outliers, renewal view, metering questions, inputs and assumptions.

### Check before you use it

- Each customer named as a risk has the figures that support it.
- Actions are options for the account owner. No outreach is drafted.
- Tiers proposed exist in the price book; a new tier is flagged as needed.

**Prompt to copy**

Follow Playbook 7: API tier fit. Files: usage \[file\], plans \[file\], price book \[file\], call class definitions \[file\]. Check coverage and duplicates first. For each customer show monthly volume by call class, 3 and 6 month trend, peak versus average, look-to-book ratio, commit utilization, and the bill on each tier at the same usage. Mark each customer right-sized, under-using, over-using or unusual. Label machine traffic as "possible, to confirm". Give the top 15 actions as options for the account owner, with no customer outreach.

## Playbook 8: Price change proposal

**Purpose:** turn a proposed price or packaging change into a decision package for the Pricing Council. The council decides; Legal confirms notice terms.

**Attach:** the change, customer base (plan, price, volume, contract end, segment), a contract terms summary (price protection, notice, MFN, renewal), the price book, and volume and churn assumptions.

### Steps

1.  Restate the change: before and after by plan and unit.
2.  Segment customers: unaffected, increase, decrease, and size of change.
3.  Check contracts: can the change take effect at the proposed date, only at renewal, or only after notice. Show the earliest date per group and the revenue share in each. Quote clause references and escalate MFN or price-protection conflicts to Legal. Do not interpret contract language.
4.  Model base, low and high scenarios for 12 months by segment with the assumptions in a table: revenue, margin if cost is given, customers lost or downgraded.
5.  Sensitivities: which assumption moves the result most.
6.  Notice calendar: contract notice deadlines, internal approvals, communication dates, effective dates.
7.  Risk register: churn in key accounts, win-rate effect, partner reaction, billing readiness, legal exposure, perception. Mitigation and owner role for each.
8.  Communication outline (not final copy): audiences, key message, what changes and what does not, timing, who speaks to strategic accounts.

**Output order:** one-page council memo (decision requested, change, rationale, scenario table, top three risks, recommendation, conditions), scenario summary and assumptions, impacted customers (top 25 and counts), contract and notice summary, notice calendar, risk register, communication outline, 30/60/90 day monitoring plan, inputs and assumptions.

### Check before you use it

- Every scenario shows a range, never a single point.
- Nothing says a change is allowed under a contract; it lists what Legal must confirm.
- No customer-facing final copy.

**Prompt to copy**

Follow Playbook 8: Price change proposal. Change: \[describe or file\]. Customers: \[file\]. Contract summary: \[file\]. Price book: \[file\]. Volume and churn assumptions: \[file, or "propose ranges and label them as assumptions"\]. Show before and after by plan, group customers by effect, mark when the change can take effect (proposed date, renewal only, or after notice) quoting clause references and escalating any MFN or price-protection conflict to Legal, build base, low and high 12-month scenarios with their assumptions, and write a one-page council memo, a risk register and a notice calendar.

## Playbook 9: Willingness-to-pay study

**Purpose:** plan a pricing study that can change a decision, then analyze the results honestly. Two modes: design and analyze.

### Design mode

1.  State the decision and the hypotheses. If the study would not change the decision, say so and propose a cheaper method.
2.  Choose the method: interviews and value-driver quantification (early, small samples), Van Westendorp or Gabor-Granger (price range for a defined product), conjoint or max-diff (packaging and tier trade-offs, needs larger samples), or analysis of past deals and win-loss. Prefer a combination when samples are small.
3.  Plan the sample: segments, quotas, recruiting, minimum useful size per cell, and what can and cannot be concluded.
4.  Draft the instrument with neutral wording, no price anchors, screening questions, and value-metric questions.
5.  Plan the analysis and the decision rule: if X, recommend Y.
6.  Flag risks: stated versus actual willingness to pay, buyer and user gaps, confidentiality, competition-law concerns when asking about competitors, customer fatigue.

**Prompt to copy**

Follow Playbook 9: WTP study, design mode. Decision to inform: \[launch price, tiers, bundle or value metric\]. Product concept: \[text\]. Segments: \[list\]. Constraints: \[budget, time, access\]. Recommend a method (interviews, Van Westendorp, Gabor-Granger, conjoint or a mix) and why, a sample plan with the minimum size per segment and what can and cannot be concluded, a neutral questionnaire or interview guide with no price anchors, an analysis plan, and a decision rule: if X then Y.

### Analyze mode

1.  Check the data: sample sizes by segment, completion, straight-lining, outliers, bias risks. Report them first.
2.  Compute: Van Westendorp price curves and acceptable range; Gabor-Granger demand curve and revenue-maximizing point; conjoint part-worths and simulated shares; interview themes with counts and short quotes.
3.  Segment the results and show where segments disagree.
4.  Recommend a price range, a starting point, the value metric, tier or bundle structure and fences. State confidence and what would raise it.
5.  List limits and the next in-market test.

**Prompt to copy**

Follow Playbook 9: WTP study, analyze mode. Responses: \[file\]. Instrument: \[file\]. Check sample sizes, completion and outliers first. Compute the price curves or demand curve with formulas shown, split by segment, and give a recommended range and starting price, confidence and limits, and an in-market test. Show sample size next to every figure. Stated willingness to pay is not a forecast.

### Check before you use it

- Sample size sits next to every figure.
- Stated willingness to pay is not presented as a forecast.
- No respondent data or benchmarks are invented. Respondents are not identified.

## Playbook 10: Rights lookup for one dataset, agency and supplier

**Purpose:** answer "what may we do with this dataset for this agency and this supplier today?" for a single case. For many cases at once use the resolver script in the SharePoint kit.

**Attach:** exports of agreements, exceptions, profile terms and dataset ceilings, and the dataset list with derivation modes.

### Steps (in this order, for each use right)

1.  Find the party's agreement that is Active and in force on the date. Superseded, expired and terminated agreements do not count. If none, the result is Unknown ("no active agreement").
2.  The agreement and its rights profile must be Legal confirmed. If not, Unknown.
3.  Start from the profile term for the use right.
4.  If a dated exception applies (to this dataset or to all datasets), it replaces the profile term and can loosen or tighten it. An unconfirmed exception makes the result Unknown. If several apply, take the most restrictive.
5.  Cap by the dataset ceiling: take the more restrictive of the contract result and the ceiling. A missing or unconfirmed ceiling is Unknown.
6.  Derived datasets. **Inherit:** take the most restrictive result across the parent datasets for the same use right, then cap by the derived dataset's own ceiling. **Transform** (aggregated or anonymized): the parents decide only whether the party's data may be included, using derivative_data_product (or the specific processing right) for each contributing party; output rights come from the derived dataset's own ceiling. An open processing term is Unknown, so the party is excluded.

**Output:** a table with one row per use right: the result of each step, the final status, and the reason. Anything not confirmed is Unknown. Most to least restrictive: Prohibited, Unknown, Conditional, Granted. Eligible means Granted or Conditional.

### Check before you use it

- Dates: the as-of date is stated and agreements are tested against it.
- No step was skipped; an Unknown at any step carries through.
- For anything bigger than a handful of cases, run the resolver instead.

**Prompt to copy**

Follow Playbook 10: Rights lookup. Dataset: \[id\]. Agency: \[id or name\]. Supplier: \[id or name\]. Date: \[today\]. Use right: \[name or "all nine"\]. Files: agreements, exceptions, profile terms and dataset ceilings \[exports\]. Walk the steps in order and show the result of each: active agreement in force, confirmed, profile term, exception override, dataset ceiling, derived-dataset rule. Give the final status per use right and the reason. Anything not confirmed is Unknown.

## Calculations Copilot should not do alone

- The price corridor and use-right ladder for a real decision (use the script or an Excel model, then compare).
- Effective rights and coverage across many parties (use the resolver).
- Totals over large billing or usage files (use Excel, and ask Copilot for formulas, not values).
- Anything where two runs give different numbers. Do not use either.
