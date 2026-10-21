const { build } = require('./lib');
const { P } = require('./content');

const B = [];
B.push({ title: 'Copilot Playbooks: Pricing Desk' });
B.push({ sub: 'Add this file to your Pricing Desk notebook. Prices, customers and agreements in examples are invented. Playbooks are drafts for people to review; named people approve and Legal confirms rights.' });

B.push({ h1: 'How to use this file' });
B.push({ numbers: [
  'Add this file to the notebook as a reference.',
  'In a prompt, name the playbook: "Follow Playbook 5: Deal desk review."',
  'Attach or name the input files in the prompt. Do not paste whole contracts.',
  'Check the answer with the "Check before you use it" list, then save the result to a Page.',
] });

B.push({ h1: 'Rules for every playbook' });
B.push({ bullets: [
  '**Inputs:** use only files named in the prompt or in the notebook. If a needed input is missing, list it and stop. Do not guess.',
  '**Evidence:** cite the file and location (sheet and cell, page, clause) for every figure and every contract statement.',
  '**Unknown is the default:** silence in a contract is never permission. Never say a use of data is allowed unless the register shows Granted or Conditional and Legal confirmed is Yes.',
  '**No legal conclusions:** summarize what the document says and where, then write the question for Legal.',
  '**Calculations:** show the inputs, the formula in words, and the result. No estimates in prose. Label every assumption.',
  '**Recommend only:** named people approve. Do not draft anything to send to a customer.',
  '**Confidentiality:** customer-specific figures stay in the request. Do not copy them into general summaries.',
  '**Format:** a one-line headline first, then tables. End with "Inputs and assumptions used" and "Missing".',
] });
B.push({ h2: 'Vocabulary' });
B.push({ table: { headers: ['Term', 'Meaning'], widths: [2600, 6760], rows: [
  ['Use rights (nine)', 'internal_use, internal_analytics_shared_outputs, display_to_third_parties, redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding, ai_evaluation. Each AI use is its own right.'],
  ['Statuses', 'Granted, Conditional (record the conditions), Prohibited, Unknown (the default).'],
  ['Most to least restrictive', 'Prohibited, Unknown, Conditional, Granted.'],
  ['Eligible to sell', 'Granted or Conditional, and legal_confirmed = Yes. Everything else is not for sale.'],
  ['Placeholder approval tiers', 'Use only if the desk has no approval matrix, and say so. Tier 0: discount up to 10 percent. Tier 1: beyond the band. Tier 2: above 250,000 USD total contract value, multi-year, or a cross-family bundle. Tier 3: above 1 million USD, below floor, MFN, exclusivity, or data redistribution rights.'],
] } });

// ---------------------------------------------------------------- 1
B.push({ pagebreak: true });
B.push({ h1: 'Playbook 1: Register intake from agreements' });
B.push({ p: '**Purpose:** turn an agreement and a dataset description into proposed register rows with evidence. Copilot proposes; only Legal confirms.' });
B.push({ p: '**Attach:** the agreement as Word or PDF, a data dictionary if there is one, and the party\'s standard rights profile if you want deviations only.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Identify the agreement: parties, type, effective date, expiry, renewal, amendments, and what it supersedes.',
  'For each of the nine use rights propose Granted, Conditional, Prohibited or Unknown. Granted needs a clear provision. Conditional records the conditions. Silence or ambiguity is Unknown.',
  'Record evidence, one row per provision: document, clause or page, a one or two sentence summary in your own words, and a short quote of 20 words or fewer.',
  'Capture restrictions: redistribution, display, derivatives, each AI use, geography, term, exclusivity, confidentiality, attribution, audit, deletion, personal data, and withdrawal.',
  'Secondary processing: record any term on aggregation, anonymization, combining with other data, or derived products, with its conditions (minimum cohort size, no identification, delay). If the contract says nothing, write Unknown.',
  'If a standard profile is supplied, list only the deviations as exceptions, with the clause, and say whether each loosens or tightens the profile.',
  'List open questions for Legal, grouped, each with a priority.',
] });
B.push({ p: '**Output order:** summary counts by status, use-right table, evidence table, exceptions, open questions, and the decision requested from Legal.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: [
  'Every Granted or Conditional row has a quote and a location.',
  'No AI use is inferred from internal use.',
  'legal_confirmed is blank. Copilot never sets it.',
  'Open questions exist for every Unknown that a live deal depends on.',
] });
B.push({ prompt: P[1] });

// ---------------------------------------------------------------- 2
B.push({ h1: 'Playbook 2: Price setting' });
B.push({ p: '**Purpose:** work out what to charge for a data product, with a floor, a value cap and a recommended price, before building a price book.' });
B.push({ p: '**Attach:** cost inputs, customer segments with value estimates and their source, market comparables with a comparability score from 0 to 1, willingness-to-pay points if any, and the list of eligible use rights from the register.' });
B.push({ h2: 'Steps and formulas' });
B.push({ numbers: [
  '**Value metric:** pick the unit the price scales with. Test each candidate: does it rise with customer value, can it be metered and verified, is the bill predictable, is it hard to game, does it line up with cost and use rights. Choose one.',
  '**Cost floor per unit** = (annual fixed cost ÷ expected units + variable cost per unit + cannibalization per unit) ÷ (1 − royalty share − margin floor).',
  '**Value per unit** (per segment) = yearly value per customer ÷ units per customer × coverage factor. Coverage factor = current coverage ÷ reference coverage.',
  '**Value-based price** = value per unit × capture share (10 to 30 percent is a typical starting point). **Value cap** = value per unit × maximum capture share (default 50 percent). Weight segments by expected units.',
  '**Market reference** = comparability-weighted average of comparable unit prices. Show the range. Comparables with low comparability are context only.',
  '**WTP median:** use only with 5 or more points; 15 or more to rely on.',
  '**Blend:** 40 percent value-based price, 30 percent market reference, 30 percent WTP median. If an anchor is missing, share its weight across the others. Keep the result between the floor and the cap.',
  '**Realized price** is the blend. **List price** = realized ÷ (1 − expected average discount).',
  '**Extra use rights:** price of a right = base price + capture share × extra value per unit + extra cost per unit ÷ (1 − royalty share − margin floor). Price only rights that are eligible; list the rest as blocked.',
  '**Sensitivity:** value capture ±20 percent, costs +20 percent, demand −30 percent, market reference −20 percent, and coverage if open rights items are resolved.',
] });
B.push({ p: '**Reading the result:** if the floor is above the cap there is no viable price (options: cut cost or scope, aim at a higher-value segment or right, spread cost across products, re-check the value estimate). If anchors differ by more than 1.5 times, find out why before averaging. If segment value-based prices differ by more than 1.5 times, consider fenced segment prices.' });
B.push({ p: '**Confidence:** High needs three anchors, value figures from pilots or contract data, 15 or more WTP points and two or more good comparables. Value figures that are only estimates, or fewer than 5 WTP points, mean Low or Medium. Present Low as provisional.' });
B.push({ p: '**Output order:** headline price and confidence, corridor table, segments, use-right ladder with blocked rights, sensitivity table, flags and next evidence, pilot plan with a decision rule, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: [
  'Recompute the floor and one segment\'s value-based price yourself in Excel.',
  'Every input has a source; invented inputs are labeled as assumptions.',
  'No right is priced unless the register lists it as eligible.',
  'For the real price decision, run the price corridor script (ask someone with Python, or use Claude) and compare with this draft.',
] });
B.push({ prompt: P[2] });

// ---------------------------------------------------------------- 3
B.push({ h1: 'Playbook 3: Price book' });
B.push({ p: '**Purpose:** turn prices into a controlled price book where every line is tied to a dataset and an eligible use right.' });
B.push({ p: '**Attach:** the corridor results from Playbook 2, the register export of eligible rights, existing prices and past deals.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Scope: list priceable rights (Granted or Conditional, Legal confirmed) and blocked rights, with the question blocking each.',
  'Choose the licensing unit, the delivery dimension only if cost or value differs, and the metering source.',
  'For each dataset set three anchors: floor, reference (median and range of realized comparable deals), value ceiling. Put the list price between floor and ceiling.',
  'Set the use-right ladder from the value each right adds. Do not apply standard multipliers.',
  'Add volume tiers with a tier model (all_units or graduated), a floor price per line, discount bands with the approval tier each depth triggers, term discounts, minimum commitments, overage, audit rights, and the conditions that travel with Conditional rights.',
  'Write the table with columns: line_id, dataset_id, use_right, delivery, unit, tier_min, tier_max, list_price, floor_price, currency, term_months, tier_model, status, version. Leave tier_max blank for the last tier. Status is Draft or Proposed; only the Pricing Council sets Approved.',
  'Run the manual checks below.',
] });
B.push({ h2: 'Manual checks (report pass or fail per line)' });
B.push({ table: { headers: ['Check', 'Rule'], widths: [2800, 6560], rows: [
  ['Register linkage', 'Every line has a dataset_id and use_right that exist in the register as Granted or Conditional with Legal confirmed.'],
  ['Floor and list', 'floor_price is at or below list_price on every line.'],
  ['Tier overlaps and gaps', 'Within a line, each tier starts right after the previous one ends. No overlaps, no gaps.'],
  ['Unit price and volume', 'Unit price does not rise as volume rises.'],
  ['Volume cliffs', 'In all_units tiers, total cost at the first unit of a higher tier is not below the total cost at the top of the tier before it.'],
  ['Rights ladder', 'No broader right is priced below internal_use for the same dataset.'],
] } });
B.push({ p: '**Output order:** headline, price book table, rationale per line, ladder logic, blocked list with owners, check results, Council decision list, inputs and assumptions.' });
B.push({ prompt: P[3] });

// ---------------------------------------------------------------- 4
B.push({ h1: 'Playbook 4: Data licence pricing request' });
B.push({ p: '**Purpose:** decide what is being licensed, whether the desk is allowed to license it, and what to charge. The price is proposed; Legal confirms the rights before any quote.' });
B.push({ p: '**Attach:** the request, the register export, the price book, and customer context.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Restate the request in a table: dataset, fields, coverage, frequency, term, delivery, intended use.',
  'Classify each intended use as a use right, quoting the customer\'s words. Mark ambiguous cases. Show, resell, combine, and any training, retrieval or agent use are separate questions.',
  'Check each right against the register: allowed, allowed with conditions, not allowed, unknown. Include the register reference.',
  'Check personal data and supplier-confidential fields that need removal or aggregation.',
  'Only then price from the price book: base subscription, volume tier, use-right uplift, term discount, approved exception band. Show the waterfall. If no rule fits, give a range labeled as a proposal.',
  'Route: standard, Tier 1 or 2 for non-standard terms, Tier 3 for redistribution, AI use, exclusivity or a rights conflict.',
  'Draft the Legal escalation note: dataset, proposed use, register entry, the question, the deadline.',
] });
B.push({ p: '**Output order:** recommendation (quote, quote with conditions, escalate, decline) and tier, request table, use-right classification, rights check, price and waterfall or the reason none is given, conditions to request from Legal, escalation note, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['If the register is silent, the answer is "rights unknown, escalate", not a price.', 'No contract clauses are drafted.'] });
B.push({ prompt: P[4] });

// ---------------------------------------------------------------- 5
B.push({ h1: 'Playbook 5: Deal desk review' });
B.push({ p: '**Purpose:** turn a deal request into a decision-ready package for the approver. You recommend; a named person approves.' });
B.push({ p: '**Attach:** the deal request, price book, approval matrix, at least five comparable deals if available, and customer context.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Restate the request in a table: product, unit, quantity, list price, requested price, term, ramp, commit, overage.',
  'Build the waterfall: list value, each discount layer (volume, term, bundle, special), net price, total contract value, annualized value. For usage pricing, model commit, expected usage and overage at low, base and high usage.',
  'Check guardrails per line: discount versus band, price versus floor, margin versus family floor if cost is given, term and payment terms, non-standard clauses (MFN, exclusivity, price protection, redistribution or AI rights for data).',
  'Compare with similar deals on net price per unit and discount depth. Flag if this would become the new low.',
  'Assign the approval tier by the first rule tripped, and name the rule.',
  'List risks and open questions for Finance, Legal and Product.',
  'Draft two or three counteroffers that trade value for concessions (bigger commit for a deeper tier, longer term for a lower rate, smaller start with a ramp, removal of a clause), each with a waterfall.',
] });
B.push({ p: '**Output order:** one-line recommendation and tier, deal and waterfall tables, guardrail results, comparables, risks and questions, counteroffers, approval memo under 150 words, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Recompute the waterfall total in Excel.', 'The tier is the first rule tripped, and the rule is named.', 'Competitor prices appear only if supplied with a source; otherwise marked unverified.', 'Nothing was sent to the customer.'] });
B.push({ prompt: P[5] });

// ---------------------------------------------------------------- 6
B.push({ h1: 'Playbook 6: Price realization' });
B.push({ p: '**Purpose:** explain the gap between the price book and what customers pay, find where it leaks, and say what to do.' });
B.push({ p: '**Attach:** billing lines for the period, the price book version in force (with effective dates), the deal log or contract terms. Large files: ask for row counts first, then work month by month, or use Excel.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Reconcile first: row counts, nulls, duplicates, unmatched products, and the total against finance revenue. Stop and report if the gap is over 1 percent of billed revenue. Label later results provisional.',
  'Rebuild list value for each line from the price book version in force on the invoice date.',
  'Build the waterfall: list value, approved discounts, unapproved or unexplained discount, credits and adjustments, billing and metering gaps, realized revenue. Show USD and percent of list.',
  'Cut by product family, segment, discount tier, top 20 customers, contract vintage.',
  'Classify drivers: approved discount beyond guardrail, discount with no recorded approval, expired promotions still applied, unbilled usage, tier mismatch, credits and write-offs, price book errors, unit definition problems.',
  'Size and rank each driver by annual value and recoverability (easy fix, needs a customer conversation, needs a contract change).',
  'Recommend actions per top driver: owner role, step, expected recovery range, how it will be verified.',
] });
B.push({ p: '**Output order:** headline realization rate and largest driver, waterfall, top five drivers, customers and segments to review, recovery plan, data quality notes, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Approved discount is kept separate from unexplained discount; not all discount is leakage.', 'No individual sales rep is named in broad summaries.', 'The Analytics Lead signs off the data checks before results leave the desk.'] });
B.push({ prompt: P[6] });

// ---------------------------------------------------------------- 7
B.push({ h1: 'Playbook 7: API tier fit' });
B.push({ p: '**Purpose:** show how customers use an API product, whether their plan fits, and what pricing action follows.' });
B.push({ p: '**Attach:** usage by customer and day or week by call class, current plans (tier, commit, included volume, overage rate, contract end), the price book, and call class definitions. If call classes are not defined, ask for the mapping; do not infer classes from endpoint names.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Validate data: coverage by day, missing customers, duplicates, unit consistency.',
  'Profile each customer: monthly volume by call class, 3 and 6 month trend, peak versus average, look-to-book ratio, share of calls throttled or erroring.',
  'Tier fit: commit utilization, overage incurred, bill on each tier at the same usage. Mark right-sized, under-using, over-using or unusual.',
  'Look-to-book outliers: far above the segment median.',
  'Possible machine traffic: very high rates, flat hourly pattern, near-identical queries, big bursts. Label "possible machine traffic, to confirm".',
  'Renewal view for contracts ending in 180 days: current spend, usage-implied spend, suggested tier, range of price actions.',
  'List metering questions where unit definitions were ambiguous.',
] });
B.push({ p: '**Output order:** headline findings with numbers, tier-fit summary, top 15 actions, outliers, renewal view, metering questions, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Each customer named as a risk has the figures that support it.', 'Actions are options for the account owner. No outreach is drafted.', 'Tiers proposed exist in the price book; a new tier is flagged as needed.'] });
B.push({ prompt: P[7] });

// ---------------------------------------------------------------- 8
B.push({ h1: 'Playbook 8: Price change proposal' });
B.push({ p: '**Purpose:** turn a proposed price or packaging change into a decision package for the Pricing Council. The council decides; Legal confirms notice terms.' });
B.push({ p: '**Attach:** the change, customer base (plan, price, volume, contract end, segment), a contract terms summary (price protection, notice, MFN, renewal), the price book, and volume and churn assumptions.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Restate the change: before and after by plan and unit.',
  'Segment customers: unaffected, increase, decrease, and size of change.',
  'Check contracts: can the change take effect at the proposed date, only at renewal, or only after notice. Show the earliest date per group and the revenue share in each. Quote clause references and escalate MFN or price-protection conflicts to Legal. Do not interpret contract language.',
  'Model base, low and high scenarios for 12 months by segment with the assumptions in a table: revenue, margin if cost is given, customers lost or downgraded.',
  'Sensitivities: which assumption moves the result most.',
  'Notice calendar: contract notice deadlines, internal approvals, communication dates, effective dates.',
  'Risk register: churn in key accounts, win-rate effect, partner reaction, billing readiness, legal exposure, perception. Mitigation and owner role for each.',
  'Communication outline (not final copy): audiences, key message, what changes and what does not, timing, who speaks to strategic accounts.',
] });
B.push({ p: '**Output order:** one-page council memo (decision requested, change, rationale, scenario table, top three risks, recommendation, conditions), scenario summary and assumptions, impacted customers (top 25 and counts), contract and notice summary, notice calendar, risk register, communication outline, 30/60/90 day monitoring plan, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Every scenario shows a range, never a single point.', 'Nothing says a change is allowed under a contract; it lists what Legal must confirm.', 'No customer-facing final copy.'] });
B.push({ prompt: P[8] });

// ---------------------------------------------------------------- 9
B.push({ h1: 'Playbook 9: Willingness-to-pay study' });
B.push({ p: '**Purpose:** plan a pricing study that can change a decision, then analyze the results honestly. Two modes: design and analyze.' });
B.push({ h2: 'Design mode' });
B.push({ numbers: [
  'State the decision and the hypotheses. If the study would not change the decision, say so and propose a cheaper method.',
  'Choose the method: interviews and value-driver quantification (early, small samples), Van Westendorp or Gabor-Granger (price range for a defined product), conjoint or max-diff (packaging and tier trade-offs, needs larger samples), or analysis of past deals and win-loss. Prefer a combination when samples are small.',
  'Plan the sample: segments, quotas, recruiting, minimum useful size per cell, and what can and cannot be concluded.',
  'Draft the instrument with neutral wording, no price anchors, screening questions, and value-metric questions.',
  'Plan the analysis and the decision rule: if X, recommend Y.',
  'Flag risks: stated versus actual willingness to pay, buyer and user gaps, confidentiality, competition-law concerns when asking about competitors, customer fatigue.',
] });
B.push({ prompt: P['9a'] });
B.push({ h2: 'Analyze mode' });
B.push({ numbers: [
  'Check the data: sample sizes by segment, completion, straight-lining, outliers, bias risks. Report them first.',
  'Compute: Van Westendorp price curves and acceptable range; Gabor-Granger demand curve and revenue-maximizing point; conjoint part-worths and simulated shares; interview themes with counts and short quotes.',
  'Segment the results and show where segments disagree.',
  'Recommend a price range, a starting point, the value metric, tier or bundle structure and fences. State confidence and what would raise it.',
  'List limits and the next in-market test.',
] });
B.push({ prompt: P['9b'] });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Sample size sits next to every figure.', 'Stated willingness to pay is not presented as a forecast.', 'No respondent data or benchmarks are invented. Respondents are not identified.'] });

// ---------------------------------------------------------------- 10
B.push({ h1: 'Playbook 10: Rights lookup for one dataset, agency and supplier' });
B.push({ p: '**Purpose:** answer "what may we do with this dataset for this agency and this supplier today?" for a single case. For many cases at once use the resolver script in the SharePoint kit.' });
B.push({ p: '**Attach:** exports of agreements, exceptions, profile terms and dataset ceilings, and the dataset list with derivation modes.' });
B.push({ h2: 'Steps (in this order, for each use right)' });
B.push({ numbers: [
  'Find the party\'s agreement that is Active and in force on the date. Superseded, expired and terminated agreements do not count. If none, the result is Unknown ("no active agreement").',
  'The agreement and its rights profile must be Legal confirmed. If not, Unknown.',
  'Start from the profile term for the use right.',
  'If a dated exception applies (to this dataset or to all datasets), it replaces the profile term and can loosen or tighten it. An unconfirmed exception makes the result Unknown. If several apply, take the most restrictive.',
  'Cap by the dataset ceiling: take the more restrictive of the contract result and the ceiling. A missing or unconfirmed ceiling is Unknown.',
  'Derived datasets. **Inherit:** take the most restrictive result across the parent datasets for the same use right, then cap by the derived dataset\'s own ceiling. **Transform** (aggregated or anonymized): the parents decide only whether the party\'s data may be included, using derivative_data_product (or the specific processing right) for each contributing party; output rights come from the derived dataset\'s own ceiling. An open processing term is Unknown, so the party is excluded.',
] });
B.push({ p: '**Output:** a table with one row per use right: the result of each step, the final status, and the reason. Anything not confirmed is Unknown. Most to least restrictive: Prohibited, Unknown, Conditional, Granted. Eligible means Granted or Conditional.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Dates: the as-of date is stated and agreements are tested against it.', 'No step was skipped; an Unknown at any step carries through.', 'For anything bigger than a handful of cases, run the resolver instead.'] });
B.push({ prompt: P[10] });

B.push({ h1: 'Calculations Copilot should not do alone' });
B.push({ bullets: [
  'The price corridor and use-right ladder for a real decision (use the script or an Excel model, then compare).',
  'Effective rights and coverage across many parties (use the resolver).',
  'Totals over large billing or usage files (use Excel, and ask Copilot for formulas, not values).',
  'Anything where two runs give different numbers. Do not use either.',
] });

build(B, 'Copilot Playbooks: Pricing Desk', process.argv[2]).then(() => console.log('playbooks written'));
