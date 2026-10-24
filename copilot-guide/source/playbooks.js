const { build } = require('./lib');
const { P } = require('./content');

const B = [];
B.push({ title: 'Copilot Playbooks: Pricing Desk' });
B.push({ sub: 'Add this file to your Pricing Desk notebook. Prices, customers and agreements in examples are invented. Playbooks are drafts for people to review; named people approve.' });

B.push({ h1: 'How to use this file' });
B.push({ numbers: [
  'Add this file to the notebook as a reference.',
  'In a prompt, name the playbook: "Follow Playbook 4: Deal desk review."',
  'Attach or name the input files in the prompt. Do not paste whole contracts.',
  'Check the answer with the "Check before you use it" list, then save the result to a Page.',
] });

B.push({ h1: 'Rules for every playbook' });
B.push({ bullets: [
  '**Inputs:** use only files named in the prompt or in the notebook. If a needed input is missing, list it and stop. Do not guess.',
  '**Evidence:** cite the file and location (sheet and cell, page, clause) for every figure and every contract statement.',
  '**Price the scope:** every data and API price covers a stated right: what the customer may do with the data or the API responses. A price without a stated right is not a price. Internal use is the base; everything broader is a separate, higher-priced right.',
  '**API access is not a data right:** an API price buys the use it states, normally serving the customer\'s own live bookings. Collecting, keeping or reusing responses, rebuilding or reselling data, and feeding AI are data rights and are priced as such.',
  '**Rights held are not checked here:** the product manager does that in the rights pack. Pass them the question; do not answer it.',
  '**No legal conclusions:** summarize what the document says and where, then write the question for Legal.',
  '**Calculations:** show the inputs, the formula in words, and the result. No estimates in prose. Label every assumption.',
  '**Recommend only:** named people approve. Do not draft anything to send to a customer.',
  '**Confidentiality:** customer-specific figures stay in the request. Do not copy them into general summaries.',
  '**Format:** a one-line headline first, then tables. End with "Inputs and assumptions used" and "Missing".',
] });
B.push({ h2: 'Vocabulary' });
B.push({ table: { headers: ['Term', 'Meaning'], widths: [2600, 6760], rows: [
  ['The nine rights', 'internal_use, internal_analytics_shared_outputs, display_to_third_parties, redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding, ai_evaluation. Each AI use is its own right.'],
  ['Granted right', 'The right a price covers: what the customer may do with the data or the API responses (the conferred_right column). internal_use is the base and the narrowest. Each broader right is a separate line priced above it.'],
  ['Hand-off to the product manager', 'The list of data and API products and the right each one grants. The product manager decides, in the rights pack, whether we hold what each right needs.'],
  ['Placeholder approval tiers', 'Use only if the desk has no approval matrix, and say so. Tier 0: discount up to 10 percent. Tier 1: beyond the band. Tier 2: above 250,000 USD total contract value, multi-year, or a cross-family bundle. Tier 3: above 1 million USD, below floor, MFN, exclusivity, data redistribution rights, or API access that keeps or collects data.'],
] } });

B.push({ pagebreak: true });
B.push({ h1: 'Playbook 1: Price setting' });
B.push({ p: '**Purpose:** work out what to charge for a product, data licence or API use, with a floor, a value cap and a recommended price, before building a price book.' });
B.push({ p: '**Attach:** cost inputs, customer segments with value estimates and their source, market comparables with a comparability score from 0 to 1, willingness-to-pay points if any, and, for data and API products, the right the customer will be granted and any broader rights customers ask for.' });
B.push({ h2: 'Steps and formulas' });
B.push({ numbers: [
  '**Value metric:** pick the unit the price scales with. Test each candidate: does it rise with customer value, can it be metered and verified, is the bill predictable, is it hard to game, does it line up with cost and with what the customer may do with it. Choose one.',
  '**Cost floor per unit** = (annual fixed cost ÷ expected units + variable cost per unit + cannibalization per unit) ÷ (1 − royalty share − margin floor).',
  '**Value per unit** (per segment) = yearly value per customer ÷ units per customer × coverage factor. Coverage factor = current coverage ÷ reference coverage.',
  '**Value-based price** = value per unit × capture share (10 to 30 percent is a typical starting point). **Value cap** = value per unit × maximum capture share (default 50 percent). Weight segments by expected units.',
  '**Market reference** = comparability-weighted average of comparable unit prices. Show the range. Comparables with low comparability are context only.',
  '**WTP median:** use only with 5 or more points; 15 or more to rely on.',
  '**Blend:** 40 percent value-based price, 30 percent market reference, 30 percent WTP median. If an anchor is missing, share its weight across the others. Keep the result between the floor and the cap.',
  '**Realized price** is the blend. **List price** = realized ÷ (1 − expected average discount).',
  '**Extra rights granted to the customer:** price of a right = base price + capture share × extra value per unit + extra cost per unit ÷ (1 − royalty share − margin floor). Each AI use is its own right. For API access, keeping responses, bulk extraction and rebuilding data are rights priced from their value, not at the per-call rate.',
  '**Sensitivity:** value capture ±20 percent, costs +20 percent, demand −30 percent, market reference −20 percent, and wider coverage.',
] });
B.push({ p: '**Reading the result:** if the floor is above the cap there is no viable price (options: cut cost or scope, aim at a higher-value segment or right, spread cost across products, re-check the value estimate). If anchors differ by more than 1.5 times, find out why before averaging. If segment value-based prices differ by more than 1.5 times, consider fenced segment prices.' });
B.push({ p: '**Confidence:** High needs three anchors, value figures from pilots or contract data, 15 or more WTP points and two or more good comparables. Value figures that are only estimates, or fewer than 5 WTP points, mean Low or Medium. Present Low as provisional.' });
B.push({ p: '**Output order:** headline price and confidence, corridor table, segments, granted-right ladder with the reasoning for each step, sensitivity table, flags and next evidence, pilot plan with a decision rule, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: [
  'Recompute the floor and one segment\'s value-based price yourself in Excel.',
  'Every input has a source; invented inputs are labeled as assumptions.',
  'Every price says which right it covers.',
  'For the real price decision, run the price corridor script (ask someone with Python, or use Claude) and compare with this draft.',
] });
B.push({ prompt: P[1] });

B.push({ h1: 'Playbook 2: Price book' });
B.push({ p: '**Purpose:** turn prices into a controlled price book for any product. Data and API lines state the right they grant the customer.' });
B.push({ p: '**Attach:** the corridor results from Playbook 1, existing prices and past deals.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Scope: list the products. For each data or API line, state the right it grants the customer (conferred_right): what they may do with the data or the responses. If the scope is not known, treat it as internal_use only and say so.',
  'API lines: say which use the line sells. Serving the customer\'s own live transactions is the base. Keeping responses beyond the session, bulk analysis, rebuilding or reselling data, and AI use are broader rights with their own lines and prices (data-licence rates, a minimum commitment, a retention limit).',
  'Choose the licensing unit, the delivery dimension only if cost or value differs, and the metering source.',
  'Set three anchors: floor, reference (median and range of realized comparable deals), value ceiling. Put the list price between floor and ceiling.',
  'Set the granted-right ladder from the value each right adds for the customer. Do not apply standard multipliers.',
  'Add volume tiers with a tier model (all_units or graduated), a floor price per line, discount bands with the approval tier each depth triggers, term discounts, minimum commitments, overage, audit rights, and the fences that go with the right (retention limit, look-to-book or distinct-query cap, attribution).',
  'Write the table with columns: line_id, product_id, product_type, conferred_right (data and API lines only), delivery, unit, tier_min, tier_max, list_price, floor_price, currency, term_months, tier_model, status, version. Leave tier_max blank for the last tier. Status is Existing, Draft or Proposed; only the Pricing Council sets Approved.',
  'Run the manual checks below.',
  'List the data and API products with the right each grants. Give the list to the product manager to clear.',
] });
B.push({ h2: 'Manual checks (report pass or fail per line)' });
B.push({ table: { headers: ['Check', 'Rule'], widths: [2800, 6560], rows: [
  ['Scope stated', 'Every data and API line states its conferred_right. For a strategy review a missing one is a flag. Before the price book goes out for quoting it is a failure.'],
  ['Floor and list', 'floor_price is at or below list_price on every line. Before the price book goes out for quoting, every line has a floor.'],
  ['Tier overlaps and gaps', 'Within a line, each tier starts right after the previous one ends. No overlaps, no gaps.'],
  ['Unit price and volume', 'Unit price does not rise as volume rises.'],
  ['Volume cliffs', 'In all_units tiers, total cost at the first unit of a higher tier is not below the total cost at the top of the tier before it.'],
  ['Rights ladder', 'No broader right is priced below internal_use for the same product, delivery, unit and tier.'],
] } });
B.push({ p: '**Output order:** headline, price book table, rationale per line, ladder logic, check results, Council decision list including the products for the product manager to clear, inputs and assumptions.' });
B.push({ prompt: P[2] });

B.push({ h1: 'Playbook 3: Data licence or data-access request' });
B.push({ p: '**Purpose:** decide what the customer wants to do with the data, and what to charge for that. This covers a data licence request and an API request that would collect data. The price is proposed; the product manager decides whether we may grant the right.' });
B.push({ p: '**Attach:** the request, the price book, and customer context.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Restate the request in a table: dataset or API, fields, coverage, frequency, term, delivery, intended use.',
  'Classify each right the customer wants as one of the nine, quoting the customer\'s words. Mark ambiguous cases. Show, resell, combine, keep, and any training, retrieval or agent use are separate questions.',
  'For an API request, apply the harvest test. Ask what they will do with the responses and how long they will keep them. Serving their own live bookings is the base API use. Collecting, keeping or analysing responses in bulk, rebuilding or reselling the data, or feeding AI is a data right. If the customer will not say, do not price it as internal use.',
  'Check personal data and supplier-confidential fields that need removal or aggregation. These are questions for the product manager and Legal.',
  'Price from the price book: base subscription, volume tier, uplift for each right granted, term discount, approved exception band. Show the waterfall. A data right asked for through an API is priced at the data-licence rate with a minimum commitment, a retention term and audit rights, not at the per-call rate. If no rule fits, give a range labeled as a proposal.',
  'Route: standard, Tier 1 or 2 for non-standard terms, Tier 3 for redistribution, AI use, keeping or rebuilding data, or exclusivity.',
  'Write the question for the product manager: the dataset, the right asked for, the deal and the deadline.',
] });
B.push({ p: '**Output order:** recommendation (standard quote, quote with conditions, or decline), the tier, and whether the product manager has cleared the right; request table; classification of the rights to grant with quotes; price and waterfall by line; conditions to request (retention, attribution, audit, fences); the question for the product manager; inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['The recommendation says whether the product manager has cleared the right to grant.', 'An API request to collect data is not priced at the booking rate.', 'No contract clauses are drafted.'] });
B.push({ prompt: P[3] });

B.push({ h1: 'Playbook 4: Deal desk review' });
B.push({ p: '**Purpose:** turn a deal request into a decision-ready package for the approver. You recommend; a named person approves.' });
B.push({ p: '**Attach:** the deal request, price book, approval matrix, at least five comparable deals if available, and customer context.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Restate the request in a table: product, unit, quantity, list price, requested price, term, ramp, commit, overage.',
  'Build the waterfall: list value, each discount layer (volume, term, bundle, special), net price, total contract value, annualized value. For usage pricing, model commit, expected usage and overage at low, base and high usage.',
  'Check guardrails per line: discount versus band, price versus floor, margin versus family floor if cost is given, term and payment terms, non-standard clauses (MFN, exclusivity, price protection, redistribution or AI rights for data, and for API access, a request to keep or collect responses).',
  'Compare with similar deals on net price per unit and discount depth. Flag if this would become the new low.',
  'Assign the approval tier by the first rule tripped, and name the rule.',
  'For new or expanded API access, ask what the customer will do with the responses and how long they will keep them. Data and API lines must be priced for the right the quote grants. List risks and open questions for Finance, Legal and Product, including whether the product manager has cleared each data right.',
  'Draft two or three counteroffers that trade value for concessions (bigger commit for a deeper tier, longer term for a lower rate, smaller start with a ramp, removal of a clause), each with a waterfall.',
] });
B.push({ p: '**Output order:** one-line recommendation and tier, deal and waterfall tables, guardrail results, comparables, risks and questions, counteroffers, approval memo under 150 words, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Recompute the waterfall total in Excel.', 'The tier is the first rule tripped, and the rule is named.', 'Competitor prices appear only if supplied with a source; otherwise marked unverified.', 'Nothing was sent to the customer.'] });
B.push({ prompt: P[4] });

B.push({ h1: 'Playbook 5: Price realization' });
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
B.push({ prompt: P[5] });

B.push({ h1: 'Playbook 6: API tier fit' });
B.push({ p: '**Purpose:** show how customers use an API product, whether their plan fits, and what pricing action follows.' });
B.push({ p: '**Attach:** usage by customer and day or week by call class, current plans (tier, commit, included volume, overage rate, contract end), the price book, and call class definitions. If call classes are not defined, ask for the mapping; do not infer classes from endpoint names.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Validate data: coverage by day, missing customers, duplicates, unit consistency.',
  'Profile each customer: monthly volume by call class, 3 and 6 month trend, peak versus average, look-to-book ratio, share of calls throttled or erroring.',
  'Tier fit: commit utilization, overage incurred, bill on each tier at the same usage. Mark right-sized, under-using, over-using or unusual.',
  'Look-to-book outliers: far above the segment median.',
  'Possible machine traffic: very high rates, flat hourly pattern, near-identical queries, big bursts. Label "possible machine traffic, to confirm".',
  'Possible data collection: per customer, the distinct-query ratio (distinct origin, destination and date combinations over total searches), look-to-book against the segment median, calls per key against bookings, how much of the market is swept, and the share of calls with no booking behind them. Label "possible data collection, to confirm". It is a question for the account owner, never an accusation. Options: price the use as a data licence with a minimum commitment, add a look-to-book or distinct-query cap with an overage rate, set a retention term, or move the customer to a data product.',
  'Renewal view for contracts ending in 180 days: current spend, usage-implied spend, suggested tier, range of price actions.',
  'List metering questions where unit definitions were ambiguous.',
] });
B.push({ p: '**Output order:** headline findings with numbers, tier-fit summary, top 15 actions, outliers, possible data collection, renewal view, metering questions, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Each customer named as a risk has the figures that support it.', 'Actions are options for the account owner. No outreach is drafted.', 'Tiers proposed exist in the price book; a new tier is flagged as needed.'] });
B.push({ prompt: P[6] });

B.push({ h1: 'Playbook 7: Price change proposal' });
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
B.push({ prompt: P[7] });

B.push({ h1: 'Playbook 8: Willingness-to-pay study' });
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
B.push({ prompt: P['8a'] });
B.push({ h2: 'Analyze mode' });
B.push({ numbers: [
  'Check the data: sample sizes by segment, completion, straight-lining, outliers, bias risks. Report them first.',
  'Compute: Van Westendorp price curves and acceptable range; Gabor-Granger demand curve and revenue-maximizing point; conjoint part-worths and simulated shares; interview themes with counts and short quotes.',
  'Segment the results and show where segments disagree.',
  'Recommend a price range, a starting point, the value metric, tier or bundle structure and fences. State confidence and what would raise it.',
  'List limits and the next in-market test.',
] });
B.push({ prompt: P['8b'] });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Sample size sits next to every figure.', 'Stated willingness to pay is not presented as a forecast.', 'No respondent data or benchmarks are invented. Respondents are not identified.'] });

B.push({ h1: 'Playbook 9: Import an existing price book' });
B.push({ p: '**Purpose:** start from the price book the business already uses. Bring it into the standard format, check it, and list the data and API products for the product manager.' });
B.push({ p: '**Attach:** the price book as Excel or CSV (one sheet), and revenue and customer counts per product if you have them. For a big price book, ask someone to run the import script instead (see the repo), and use this playbook to review the result.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Map the columns: product, category, unit, volume band, list price, floor price, term, revenue, customers. Show the mapping and ask for corrections.',
  'Set product_type for each product: data_license, api_access, software, service or other. Give the words that led to each, and mark any guess as low confidence.',
  'Write one row per tier with the standard columns (see Playbook 2). Prices written as "$1,200" become numbers. Bands such as "0 - 1M" and "1M - 10M" become tier_min and tier_max, with the higher tier starting one unit above the boundary. Status is Existing.',
  'Never invent a price, a floor, a term or a conferred right. Leave it blank and list it under Missing. Say which tier model you assumed (all_units unless told otherwise).',
  'For each data or API line, fill conferred_right only if it is clearly stated or the product name says it (resale, redistribution, derivative, AI training). Everything else is "not stated": treat it as internal_use only until the contracts or API terms say otherwise. Ask whether any API customer keeps or collects responses.',
  'Run the manual checks from Playbook 2 (floor and list, tier overlaps and gaps, unit price and volume, volume cliffs). Report them as findings about the existing price book.',
  'List the data and API products with annual revenue, customers and the right granted (or "not stated"). Rank by annual revenue, putting resale, redistribution, derivative and AI rights ahead of internal use when revenue is similar. This is the hand-off for the product manager. Do not guess source datasets.',
] });
B.push({ p: '**Output order:** headline (lines imported, products by type, data and API lines with no stated scope), the mapping, the standard table, product types with low-confidence guesses, check results, hand-off list, decisions needed, inputs and assumptions, missing.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: [
  'Row counts and total revenue match the source file.',
  'Nothing was invented: every blank in the source is still blank, and listed.',
  'Product types are confirmed by someone who knows the products.',
  'Nothing is marked Approved.',
] });
B.push({ prompt: P[9] });

B.push({ h1: 'Calculations Copilot should not do alone' });
B.push({ bullets: [
  'The price corridor and granted-right ladder for a real decision (use the script or an Excel model, then compare).',
  'Importing a large price book, or checking one for tier cliffs across hundreds of lines (use the import and checker scripts).',
  'Totals over large billing or usage files (use Excel, and ask Copilot for formulas, not values).',
  'Anything where two runs give different numbers. Do not use either.',
] });

build(B, 'Copilot Playbooks: Pricing Desk', process.argv[2]).then(() => console.log('playbooks written'));
