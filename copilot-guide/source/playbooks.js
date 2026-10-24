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
  '**Unknown is the default:** silence in a contract is never permission. Never say we may grant a right to a customer unless the register shows the held rights it needs as Granted or Conditional and Legal confirmed is Yes. You may still price an unconfirmed right as a strategy: label it Provisional and say it is not cleared to quote.',
  '**Rights apply only to data:** software, services and API access with no third-party content do not need the rights register.',
  '**No legal conclusions:** summarize what the document says and where, then write the question for Legal.',
  '**Calculations:** show the inputs, the formula in words, and the result. No estimates in prose. Label every assumption.',
  '**Recommend only:** named people approve. Do not draft anything to send to a customer.',
  '**Confidentiality:** customer-specific figures stay in the request. Do not copy them into general summaries.',
  '**Format:** a one-line headline first, then tables. End with "Inputs and assumptions used" and "Missing".',
] });
B.push({ h2: 'Vocabulary' });
B.push({ table: { headers: ['Term', 'Meaning'], widths: [2600, 6760], rows: [
  ['The nine rights', 'internal_use, internal_analytics_shared_outputs, display_to_third_parties, redistribution_resale, derivative_data_product, ai_training, ai_fine_tuning, ai_retrieval_grounding, ai_evaluation. Each AI use is its own right.'],
  ['Held and conferred rights', 'The same nine rights are used in two places. The register lists the rights WE HOLD on a dataset: what we may do with it, given our suppliers, contributing customers and the derivative products we may create. The price book lists the rights we GRANT the customer on a product (conferred_right): what they may do with it. We can grant only what we hold. Never read a register row as the customer\'s right, or a price book right as something we hold.'],
  ['Statuses', 'Granted, Conditional (record the conditions), Prohibited, Unknown (the default).'],
  ['Most to least restrictive', 'Prohibited, Unknown, Conditional, Granted.'],
  ['Rights basis', 'Of a price book line, based on the held rights it needs (take the worst). Confirmed: every needed held right is Granted or Conditional, and legal_confirmed = Yes. Provisional: anything else, including Unknown and not yet in the register. Contradicted: a needed held right is Prohibited in the evidence but Legal has not confirmed. Blocked: Legal confirmed a needed held right as Prohibited. Confirmed is cleared to quote. Provisional and Contradicted may be priced as a strategy but are not cleared to quote. Blocked is not priced.'],
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
  'For each of the nine rights WE HOLD propose Granted, Conditional, Prohibited or Unknown. The question is what we may do with this data, including supplying outputs to customers and building derivative products, not what a customer will be allowed to do. Granted needs a clear provision. Conditional records the conditions. Silence or ambiguity is Unknown.',
  'Record evidence, one row per provision: document, clause or page, a one or two sentence summary in your own words, and a short quote of 20 words or fewer.',
  'Capture restrictions: redistribution, display, derivatives, each AI use, geography, term, exclusivity, confidentiality, attribution, audit, deletion, personal data, and withdrawal.',
  'Secondary processing: record any term on aggregation, anonymization, combining with other data, or derived products, with its conditions (minimum cohort size, no identification, delay). If the contract says nothing, write Unknown.',
  'If a standard profile is supplied, list only the deviations as exceptions, with the clause, and say whether each loosens or tightens the profile.',
  'List open questions for Legal, grouped, each with a priority.',
] });
B.push({ p: '**Output order:** summary counts by status, held-rights table, evidence table, exceptions, open questions, and the decision requested from Legal.' });
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
B.push({ p: '**Purpose:** work out what to charge for a product or data licence, with a floor, a value cap and a recommended price, before building a price book.' });
B.push({ p: '**Attach:** cost inputs, customer segments with value estimates and their source, market comparables with a comparability score from 0 to 1, willingness-to-pay points if any, and, for data products, which rights the customer will be granted and whether all the held rights they need are confirmed by Legal (the rest are Provisional).' });
B.push({ h2: 'Steps and formulas' });
B.push({ numbers: [
  '**Value metric:** pick the unit the price scales with. Test each candidate: does it rise with customer value, can it be metered and verified, is the bill predictable, is it hard to game, does it line up with cost and with the rights we hold. Choose one.',
  '**Cost floor per unit** = (annual fixed cost ÷ expected units + variable cost per unit + cannibalization per unit) ÷ (1 − royalty share − margin floor).',
  '**Value per unit** (per segment) = yearly value per customer ÷ units per customer × coverage factor. Coverage factor = current coverage ÷ reference coverage.',
  '**Value-based price** = value per unit × capture share (10 to 30 percent is a typical starting point). **Value cap** = value per unit × maximum capture share (default 50 percent). Weight segments by expected units.',
  '**Market reference** = comparability-weighted average of comparable unit prices. Show the range. Comparables with low comparability are context only.',
  '**WTP median:** use only with 5 or more points; 15 or more to rely on.',
  '**Blend:** 40 percent value-based price, 30 percent market reference, 30 percent WTP median. If an anchor is missing, share its weight across the others. Keep the result between the floor and the cap.',
  '**Realized price** is the blend. **List price** = realized ÷ (1 − expected average discount).',
  '**Extra rights granted to the customer:** price of a right = base price + capture share × extra value per unit + extra cost per unit ÷ (1 − royalty share − margin floor). Price rights whose held rights are confirmed. Price the others too, labeled Provisional. Do not price a right when Legal has confirmed we do not hold what it needs.',
  '**Sensitivity:** value capture ±20 percent, costs +20 percent, demand −30 percent, market reference −20 percent, and coverage if open rights items are resolved.',
] });
B.push({ p: '**Reading the result:** if the floor is above the cap there is no viable price (options: cut cost or scope, aim at a higher-value segment or right, spread cost across products, re-check the value estimate). If anchors differ by more than 1.5 times, find out why before averaging. If segment value-based prices differ by more than 1.5 times, consider fenced segment prices.' });
B.push({ p: '**Confidence:** High needs three anchors, value figures from pilots or contract data, 15 or more WTP points and two or more good comparables. Value figures that are only estimates, or fewer than 5 WTP points, mean Low or Medium. Present Low as provisional.' });
B.push({ p: '**Output order:** headline price and confidence, corridor table, segments, conferred-right ladder with the rights basis of each step, sensitivity table, flags and next evidence, pilot plan with a decision rule, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: [
  'Recompute the floor and one segment\'s value-based price yourself in Excel.',
  'Every input has a source; invented inputs are labeled as assumptions.',
  'Every right whose held rights are not all confirmed by Legal is labeled Provisional. Nothing is priced for a right when Legal has confirmed we do not hold what it needs.',
  'For the real price decision, run the price corridor script (ask someone with Python, or use Claude) and compare with this draft.',
] });
B.push({ prompt: P[2] });

// ---------------------------------------------------------------- 3
B.push({ h1: 'Playbook 3: Price book' });
B.push({ p: '**Purpose:** turn prices into a controlled price book for any product. Data lines are tied to a dataset and to the right they grant the customer, and carry a rights basis worked out from the rights we hold.' });
B.push({ p: '**Attach:** the corridor results from Playbook 2, the register export if there is one, existing prices and past deals.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Scope: for each data line name the dataset it is built from (for a derivative product, the Derived entry in the register), the right it grants the customer (conferred_right), and its form: derived (an aggregate, benchmark or insight built from the dataset; the default) or passthrough (the customer receives the data itself).',
  'Rights check: look up in the table below which held rights the dataset must carry for that conferred right, find each in the register, and take the worst result as the line\'s rights basis (Confirmed, Provisional, Contradicted or Blocked). Write the open question behind each Provisional line as: dataset, held right needed. Price Confirmed and Provisional lines. Do not price Blocked lines.',
  'Choose the licensing unit, the delivery dimension only if cost or value differs, and the metering source.',
  'For each dataset set three anchors: floor, reference (median and range of realized comparable deals), value ceiling. Put the list price between floor and ceiling.',
  'Set the conferred-right ladder from the value each right adds for the customer. Do not apply standard multipliers.',
  'Add volume tiers with a tier model (all_units or graduated), a floor price per line, discount bands with the approval tier each depth triggers, term discounts, minimum commitments, overage, audit rights, and the conditions that travel with Conditional rights.',
  'Write the table with columns: line_id, product_id, product_type, dataset_id (data lines only), conferred_right (data lines only), data_form (data lines only), delivery, unit, tier_min, tier_max, list_price, floor_price, currency, term_months, tier_model, status, version. Leave tier_max blank for the last tier. Status is Existing, Draft or Proposed; only the Pricing Council sets Approved.',
  'Run the manual checks below.',
] });
B.push({ h2: 'Held rights each granted right needs' });
B.push({ p: 'Default table for Legal and the Pricing Council to confirm or change. Every listed held right is needed on the dataset. A derived product built directly on a source dataset (not on a Derived register entry) also needs derivative_data_product held on that dataset.' });
B.push({ table: { headers: ['Right granted to the customer', 'Derived product needs held', 'Passthrough data needs held'], widths: [3300, 3030, 3030], rows: [
  ['internal_use', 'internal_analytics_shared_outputs', 'redistribution_resale'],
  ['internal_analytics_shared_outputs', 'internal_analytics_shared_outputs', 'redistribution_resale'],
  ['display_to_third_parties', 'internal_analytics_shared_outputs and display_to_third_parties', 'redistribution_resale and display_to_third_parties'],
  ['redistribution_resale', 'internal_analytics_shared_outputs and redistribution_resale', 'redistribution_resale'],
  ['derivative_data_product', 'internal_analytics_shared_outputs and derivative_data_product', 'redistribution_resale and derivative_data_product'],
  ['Each AI right (ai_training, ai_fine_tuning, ai_retrieval_grounding, ai_evaluation)', 'internal_analytics_shared_outputs and the same AI right', 'redistribution_resale and the same AI right'],
] } });
B.push({ p: 'Example: a derived product grants display_to_third_parties on dataset DS-DER-002. The register must show internal_analytics_shared_outputs (we may supply the outputs) and display_to_third_parties (we may let them be shown) for DS-DER-002. If the first is Conditional and the second Unknown, and Legal has confirmed neither, the line is Provisional and the open question is "DS-DER-002: display_to_third_parties".' });
B.push({ h2: 'Manual checks (report pass or fail per line)' });
B.push({ table: { headers: ['Check', 'Rule'], widths: [2800, 6560], rows: [
  ['Rights basis', 'Every data line has a rights basis, worked out from the held rights it needs. For a strategy review, Provisional lines pass with a flag. Before the price book goes out for quoting, every data line must be Confirmed. No line is Blocked.'],
  ['Right and form stated', 'Every data line names its dataset, its conferred_right and its data_form. A line missing any of them is Provisional.'],
  ['Floor and list', 'floor_price is at or below list_price on every line.'],
  ['Tier overlaps and gaps', 'Within a line, each tier starts right after the previous one ends. No overlaps, no gaps.'],
  ['Unit price and volume', 'Unit price does not rise as volume rises.'],
  ['Volume cliffs', 'In all_units tiers, total cost at the first unit of a higher tier is not below the total cost at the top of the tier before it.'],
  ['Rights ladder', 'No broader conferred right is priced below internal_use for the same dataset.'],
] } });
B.push({ p: '**Output order:** headline, price book table, rationale per line, ladder logic, rights basis by line with the held rights needed and owners for open questions, check results, Council decision list, inputs and assumptions.' });
B.push({ prompt: P[3] });

// ---------------------------------------------------------------- 4
B.push({ h1: 'Playbook 4: Data licence pricing request' });
B.push({ p: '**Purpose:** decide what is being licensed, whether we hold the rights to grant it and they are confirmed, and what to charge. The price is proposed and may be provisional; Legal confirms the rights before any quote goes to the customer.' });
B.push({ p: '**Attach:** the request, the register export, the price book, and customer context.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Restate the request in a table: dataset, fields, coverage, frequency, term, delivery, intended use.',
  'Classify each right the customer wants as one of the nine, quoting the customer\'s words. Mark ambiguous cases. Show, resell, combine, and any training, retrieval or agent use are separate questions.',
  'For each right to grant, use the Playbook 3 table to list the held rights the dataset must carry. Check each in the register: Confirmed, Provisional (unknown or unconfirmed), Contradicted or Blocked. The request takes the worst. Include the register reference.',
  'Check personal data and supplier-confidential fields that need removal or aggregation.',
  'Then price from the price book: base subscription, volume tier, uplift for each right granted, term discount, approved exception band. Show the waterfall. Label the price Provisional if any held right it needs is not Confirmed. If no rule fits, give a range labeled as a proposal.',
  'Route: standard, Tier 1 or 2 for non-standard terms, Tier 3 for redistribution, AI use, exclusivity or a rights conflict.',
  'Draft the Legal escalation note: dataset, proposed use, register entry, the question, the deadline.',
] });
B.push({ p: '**Output order:** recommendation (quote, quote with conditions, provisional price while Legal confirms, decline), whether it is cleared to quote, and tier, request table, classification of the rights to grant, rights check (right to grant, held rights needed, basis), price and waterfall with the rights basis of each line, conditions to request from Legal, escalation note, inputs and assumptions.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['If the register is silent, the answer is a Provisional price and "rights unknown, escalate", never "allowed".', 'The recommendation says whether the price is cleared to quote.', 'No contract clauses are drafted.'] });
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
B.push({ p: '**Purpose:** answer "what may we do with this dataset for this agency and this supplier today?" for a single case. The answer is the rights we hold, which feed the register. For many cases at once use the resolver script in the SharePoint kit.' });
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
B.push({ p: '**Output:** a table with one row per use right: the result of each step, the final status, and the reason. Anything not confirmed is Unknown. Most to least restrictive: Prohibited, Unknown, Conditional, Granted. Confirmed means Granted or Conditional with Legal confirmed.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: ['Dates: the as-of date is stated and agreements are tested against it.', 'No step was skipped; an Unknown at any step carries through.', 'For anything bigger than a handful of cases, run the resolver instead.'] });
B.push({ prompt: P[10] });

// ---------------------------------------------------------------- 11
B.push({ h1: 'Playbook 11: Import an existing price book' });
B.push({ p: '**Purpose:** start from the price book the business already uses. Bring it into the standard format, check it, and rank the register questions behind the data products by the revenue at risk. Do not wait for the register or for Legal.' });
B.push({ p: '**Attach:** the price book as Excel or CSV (one sheet), and revenue and customer counts per product if you have them. For a big price book, ask someone to run the import script instead (see the repo), and use this playbook to review the result.' });
B.push({ h2: 'Steps' });
B.push({ numbers: [
  'Map the columns: product, category, unit, volume band, list price, floor price, term, revenue, customers. Show the mapping and ask for corrections.',
  'Set product_type for each product: data_license, api_access, software, service or other. Give the words that led to each, and mark any guess as low confidence.',
  'Write one row per tier with the standard columns (see Playbook 3). Prices written as "$1,200" become numbers. Bands such as "0 - 1M" and "1M - 10M" become tier_min and tier_max, with the higher tier starting one unit above the boundary. Status is Existing.',
  'Never invent a price, a floor, a term or a conferred right. Leave it blank and list it under Missing. Say which tier model you assumed (all_units unless told otherwise).',
  'Mark rights relevance: data_license = Required. api_access = Possible (do responses carry supplier or third-party content? ask). Software and services = None.',
  'Run the manual checks from Playbook 3 (floor and list, tier overlaps and gaps, unit price and volume, volume cliffs). Report them as findings about the existing price book.',
  'For each data product, guess the dataset it is built from (a placeholder such as DS-CAND-name) and ask whether it is a derived product or passthrough data. Use the Playbook 3 table to list the held rights the register will need, from the conferred rights the price book states.',
  'List the data products and the possible-data API products, with annual revenue, customers, the rights granted to customers that the price book states, and the held rights needed. Rank by annual revenue, putting resale, redistribution, derivative and AI rights ahead of internal use when revenue is similar. This is the proposed order for register intake.',
] });
B.push({ p: '**Output order:** headline (lines imported, products by type, revenue on lines that need a rights check), the mapping, the standard table, product types with low-confidence guesses, check results, intake priority table, decisions needed, inputs and assumptions, missing.' });
B.push({ h2: 'Check before you use it' });
B.push({ bullets: [
  'Row counts and total revenue match the source file.',
  'Nothing was invented: every blank in the source is still blank, and listed.',
  'Product types are confirmed by someone who knows the products.',
  'Nothing is marked Approved and no Legal column is filled in.',
] });
B.push({ prompt: P[11] });

B.push({ h1: 'Calculations Copilot should not do alone' });
B.push({ bullets: [
  'The price corridor and conferred-right ladder for a real decision (use the script or an Excel model, then compare).',
  'Effective rights and coverage across many parties (use the resolver).',
  'Importing a large price book, or checking one for tier cliffs across hundreds of lines (use the import and checker scripts).',
  'Totals over large billing or usage files (use Excel, and ask Copilot for formulas, not values).',
  'Anything where two runs give different numbers. Do not use either.',
] });

build(B, 'Copilot Playbooks: Pricing Desk', process.argv[2]).then(() => console.log('playbooks written'));
