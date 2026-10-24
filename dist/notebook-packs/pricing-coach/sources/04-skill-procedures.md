# Pricing skill procedures

What each skill does, step by step. A notebook cannot run these skills or their scripts.

---

## Document: account-price-fit

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

---

## Document: analog-research

# Analog research

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A new construct has no price history. Similar products, inside or outside the industry, show what units, metrics and fences others have tried and what happened. They are evidence about structure, not a price to copy.

## When to use

- A new product, metric or right has no price history (`data-price-setting`, `packaging-design`).
- A competitor or adjacent market moved (`competitive-price-scan`).
- The quarterly review (`quarterly-price-review`) refreshes the library.

Not for: dated competitor price checks on our own market (`competitive-price-scan`), or willingness-to-pay evidence from our customers (`wtp-study-design`).

## Inputs

The construct to price in one sentence: product, buyer, use, candidate unit. Where to look is the analyst's choice: same industry, adjacent (other data and API businesses), or far (other machine-access pricing). Existing entries in `workspace/context-library/analogs/`. Ask one question at a time.

## Procedure

1. **Public sources only** (rule 11). Search the open web; no logins, no contact with competitors, no customer data in queries. Prefer the company's own pricing or announcement page; otherwise press or analyst coverage, marked secondary.
2. **Fetch the page** and read it. A search result is not a source. If a page cannot be reached, say so, write the entry as to verify, and never fill gaps from memory.
3. **Record each analog** with `assets/analog-entry.md`: source URL, published and access dates, unit, metric, right or use granted, comparability 1 to 5 with the reason. Quote numbers exactly and tag them F with the source.
4. **Say what it suggests (I) and what it does not show.** One analog is an anecdote. Name the structure, not the price.
5. **Check the library** with `scripts/check_analogs.py --dir workspace/context-library/analogs`, adding `--today` and `--max-age-days` only if the company has a re-check rule.
6. **Summarise** the structures seen, the ones to test, and the ones to avoid, with the analogs behind each. See `references/frameworks.md` for the named methods and their verification status.

## Output

Header; the finding in one line; a table of analogs (name, unit, metric, right, comparability, date); structures worth testing; what could not be verified; four-part handoff. Entries saved to the analog folder after the user agrees.

## Quality gate

- Every entry has a web address and an access date, and the checker passes.
- Numbers are quoted from the page, not remembered.
- Secondary sources are marked secondary; no claim goes further than the source.
- Comparability is scored with a reason, and the buyer, use and unit are compared, not just the product.
- No price is recommended from analogs alone.

---

## Document: api-access-request

# API access request

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

An API key is sometimes asked for to serve bookings and sometimes to collect data. They are different products with different rights and prices. This skill finds out which, and prices the scope that fits.

## When to use

- A customer or rep asks for a new key, a higher limit, a new endpoint or an expanded use.
- Usage on an existing key looks unlike its segment.
- `deal-desk-triage` routes an `api_data_request` here.

Not for: tier design (`api-usage-tier-fit`), a data licence the customer asked for by name (`data-license-pricing`), whether we hold the right (`rights-handoff`).

## Inputs

1. **Purpose**, in the requester's words: what will be done with the responses, for whom, and how long they are kept. Ask when the request does not say. One question at a time.
2. **Usage**, if a key exists: searches, bookings, distinct queries, retention if known (CSV, see `examples/keys.csv`).
3. **Segment median look-to-book** and the **screen multiple**. Both are company values from `pricing-governance.md` or the API policy in `systems-and-data.md`. There is no default. If the multiple is Unknown, ratios are shown and nothing is flagged.
4. The nine rights in `references/operating-rules.md` (rule 8): which does the stated purpose need?

## Procedure

1. **Classify the purpose.** Serving the customer's own booking traffic is standard API use. Collecting, storing, analysing in bulk, rebuilding, reselling or feeding AI is a data right and is priced as one.
2. **Screen usage** with `scripts/harvest_screen.py --in <file> --segment-median-l2b N [--multiple X]`. The screen reports look-to-book, the multiple of the segment median, and the share of distinct queries. A high distinct-query share with a high ratio is a pattern worth a question. A flag reads "possible data collection, to confirm". It is never a finding against the customer.
3. **Ask the account owner** for any flagged key, without accusing. Record the answer.
4. **Name the granted right** the request needs. If it is more than API serving, price it with `data-license-pricing` and hand the rights question to the product manager with `rights-handoff`.
5. **Price the scope.** Standard API use goes to the tier in the price book (`api-usage-tier-fit`). Anything wider is a different line with a different price. Never quote bulk or retention use at a per-call booking rate.
6. **Account context.** If the account has an anchor deal, run `account-price-fit` before offering any concession.
7. **Recommend**: approve standard access, approve with a limit or term, price as a data right, or decline. Name the approver from the approval matrix, or Unknown.

## Output

Header; recommendation in one line; purpose and right table; screen results; open questions (product manager, Legal, account owner); proposed scope and price line, if any; four-part handoff. Status Draft.

## Quality gate

- The purpose is stated, or the first open question is the purpose.
- Every ratio came from the script or is shown with its inputs.
- No threshold appears that did not come from the context library or the user.
- Flags are worded as questions to confirm, not conclusions.
- A right wider than API serving is never priced as API serving.
- Nothing is sent to the customer; no key is issued or revoked by this skill.

---

## Document: api-usage-tier-fit

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

---

## Document: competitive-price-scan

# Competitive price scan

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A rival's price is a claim until it has a source and a date. A price without the unit or the right it covers cannot be compared. This skill keeps a log that is safe to quote.

## When to use

- A deal cites a competitor price (see `deal-desk-review`).
- A competitor changed price or packaging.
- Before a price change proposal goes to the Council.
- The quarterly review.

Not for: structure research across other markets (`analog-research`), willingness to pay (`wtp-study-design`).

## Inputs

The competitors and products to check. Previous scan log in `workspace/outputs/`. For a deal-driven check: what the rep or customer said, who said it and when. That is a lead (U), not a price, until a public page confirms it. Ask one question at a time.

## Procedure

1. **Public pages only** (rule 11): the competitor's pricing, documentation, announcement or terms pages. No logins, no contacting competitors, no customer data in queries.
2. **Fetch and read** each page. Record price, currency, unit, what it includes and the right or scope it covers (what the buyer may do). If scope is not stated, write Unknown and do not call the price comparable.
3. **Log one row per price** in a CSV with competitor, product, unit, price, currency, right_or_scope, source_url, access_date, notes (see `examples/scan.csv`).
4. **Check the log** with `scripts/check_scan_log.py --in <file> --today <date>`, adding `--max-age-days N` only if the company has a freshness rule. Unverified rows are not quoted.
5. **Compare like with like**: same unit, same scope. Show where ours sits and what differs. If a unit differs, convert with a script and show the inputs.
6. **Say what changed** since the last scan, and what was unreachable.

## Output

Header; the finding in one line; comparison table of verified rows only; a list of unverified leads with who said them; changes since last scan; four-part handoff. Status Draft.

## Quality gate

- Every quoted price has a web address and an access date, and the checker passes for those rows.
- Hearsay is listed as a lead, never in the comparison table.
- Prices are compared only when unit and scope match, or the difference is stated.
- Vendor pages are dated snapshots; the output says so.
- Nothing is attributed to a competitor that the page does not state.

---

## Document: council-decision-pack

# Council decision pack

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

The Council reads decisions, not history. The pack puts the decisions first and lets a member decide each in a few minutes. Only the Council approves; the pack recommends.

## When to use

- A Council meeting is scheduled and a pack is due (lead time is in `pricing-governance.md`; Unknown if blank).
- A price change, new product or construct price, approval-matrix change or exception above delegated authority needs a decision.

Not for: writing the change itself (`price-change-proposal`), reviewing one deal (`deal-desk-review`), the weekly review (`weekly-pricing-review`).

## Inputs

Read `pricing-governance.md` for the Council, decision rights and pack lead time. Gather: proposals ready for decision (from `price-change-proposal`, `data-price-setting`, `deal-desk-review`), the latest weekly reviews, the exception log, the rights hand-off status (`rights-handoff`), and the decision log. Ask one question at a time for what is missing. A proposal with no named proposer or no computed numbers is not ready: list it under Missing, not under Decisions.

## Procedure

1. **List the decisions.** One row per decision with its recommendation, proposer and the approver the decision-rights table names. If the table is a template, write Unknown and name the file.
2. **Check readiness of each.** Numbers computed by script with inputs named; granted right stated for every data and API line; rights hand-off status shown (open, answer on file, not needed); stakeholder review run for changes with customer effect (`pricing-stakeholder-review`).
3. **Write each decision** in the template: ask, options with numbers, recommendation, risks and what would change our mind.
4. **Add information items**: weekly headlines, exceptions, flags.
5. **Order by consequence**, not by date received.
6. **Leave the decision log entry blank** for a person to fill after the meeting. Never write Approved.

## Output

Fill `assets/council-pack.md`. Decisions table first, then one section per decision, information items, Missing, four-part handoff. Status For decision, never Decided.

## Quality gate

- The first screen shows every decision and what is asked.
- No number is uncomputed or untagged; each option names its script and inputs.
- Every data and API line states the granted right and the hand-off status.
- No approver, threshold or membership appears that did not come from the context library.
- The pack never says a decision is made; the log entry is for a person.
- Customer names appear only where the decision needs them, and the pack is marked Internal.

---

## Document: data-license-pricing

# Data License Pricing

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Decide what the customer wants to do with the data, and what to charge for that. Price the right they are asking for, not just the volume. Pricing proposes; the Pricing Council approves. Whether we may grant a right is the product manager's call, using the rights pack.

## When to use

- A customer asks to license a travel data product, or asks for API access to pull data in bulk.
- A custom data deal needs pricing by the right granted.
- An API request mentions keeping, analysing, reselling or AI use of responses.

Not for: a standard quote inside the price book (`deal-desk-review`), or whether we hold a right (the product manager answers that).

## Inputs

Context library files read: `pricing-governance.md`, `product-catalog.md`, `rights-handoff.md`. If a file still says `status: template`, treat its values as Unknown.

1. **The request**: customer, dataset, feed or API, fields and coverage (markets, carriers, properties, time range), refresh frequency, delivery method, term.
2. **What the customer will do with it**, in their words: use it in their own business, show it to their own customers, resell it, combine it with other data, keep it, or use it for model training, retrieval, or agent grounding. For API requests, how long they will keep responses and how many calls they expect against how many bookings.
3. **Price book** (built with the `price-book-builder` skill): subscription prices, volume tiers, uplifts by right granted. If a product or right is not there, use the `data-price-setting` skill.
4. **Customer context**: current spend, products held, strategic importance.

If the customer will not say what they will do with the data, do not price it as internal use. Price the broadest plausible use, or decline.

## Procedure

1. **Restate the request** in a table: dataset or API, fields, coverage, frequency, term, delivery, intended use.
2. **Classify the right to grant** for each dataset: internal use only, internal analytics with outputs shared, display to third parties, redistribution, derivative data product, AI or model use (training, fine-tuning, retrieval, agent grounding). Quote the customer's own words that led to each classification and mark ambiguous cases.
3. **For API requests, apply the harvest test.** Read `../price-book-builder/references/api-access-scope.md`. If the purpose is to collect, keep, analyse in bulk, rebuild or feed AI, it is a data right: price at the data-licence rate for that right, with a minimum commitment, a retention term and audit rights, not at the per-call booking rate.
4. **Check sensitivity.** Flag personal data, customer-contributed data, or supplier-confidential fields that need removal, aggregation or consent. These are questions for the product manager and Legal.
5. **Price with code, from the price book or the `data-price-setting` skill.** Base subscription by coverage and frequency, volume tier, uplift for each right granted, term discount, and any approved exception band. Show the waterfall. Where no price book rule fits, say so and give a range with the reasoning, labeled as a proposal for the council.
6. **Route** by the approval matrix in `pricing-governance.md`: standard (inside the price book) or non-standard. Redistribution, AI use, keeping or rebuilding data and exclusivity are the broad-right cases. If the matrix is not filled, the route is Unknown.
7. **Hand off to the product manager.** Add the product and the right to the hand-off list (see `rights-handoff` when available, otherwise `rights-handoff.md` in the context library). Never say whether we hold the right. Draft the price meanwhile; label it pending the rights answer. The Council note says whether the right has been cleared.

## Output

1. **Recommendation** (one line): standard quote, quote with conditions, or decline, the approval route, and whether the product manager has cleared the right to grant (Unknown until they answer).
2. **Request table** and **classification of the rights to grant** with quotes.
3. **Price proposal and waterfall**, line by line, with the right each line covers.
4. **Conditions to request**: retention limit, attribution, audit, volume fences, no resale to named competitors (a list for Legal, not contract language).
5. **Question for the product manager.**
6. **Inputs and assumptions used.**

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Price by the right granted, not by volume alone.
- Treat AI and model use as its own right; never assume it is covered by internal use.
- API access priced at the booking rate buys the booking use only. Collecting data is a data right.
- Do not draft contract clauses or interpret contracts; list questions for Legal.
- Do not copy customer-specific terms or supplier-confidential details into general summaries.
- Pricing recommends. The Pricing Council approves the price; the product manager and Legal decide whether we may grant the right.

---

## Document: data-price-setting

# Data Price Setting

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Answer one question: **what should we charge, and how sure are we?** The `price-book-builder` skill turns prices into a controlled price book; this skill finds the prices. Do this first.

This skill prices what we **grant** the customer: for a data product or API access, the rights they get (internal use, display, redistribution, retention, AI uses). The price assumes we may grant them. The product manager assesses that separately with the rights pack, so do not look for it here. The corridor method works for any product (API access, software, services, data); the right-by-right ladder applies to data and API products.

## When to use

- Launching a product, pricing a new customer right or API use, or when list prices lack a defensible basis.
- A price corridor with floor, value cap, market and willingness-to-pay anchors is needed.
- Coverage, cost or a pilot result has changed the evidence.

Not for: building the price book (`price-book-builder`) or one customer's deal (`deal-desk-review`). List price is set here without any account in mind.

## Inputs

Context library files read: `pricing-governance.md` (margin floor), `product-catalog.md`, `business-info.md`. If a file still says `status: template`, treat its values as Unknown.

1. **Product**: what a buyer receives, delivery, refresh, history. For a data or API product, the right the customer is granted (`base_right`): what they may do with the data or responses, and for how long they may keep them.
2. **Rights to price as options** (data and API products): the broader rights customers ask for, such as display to third parties, redistribution, keeping and building on responses, and each AI use. Each is its own line with its own value case.
3. **Coverage**: the share of the market, volume or parties the product includes, the coverage the value estimates assume, and the coverage if it widens.
4. **Cost**: fixed annual cost to produce and run, variable cost per unit, supplier royalties or revenue share (as a percent of price), cannibalization of existing products, and Finance's margin floor.
5. **Customers and value**: segments, how many, how much each would use, and what the product is worth to each per year. Record the source of each estimate: estimate, interview, pilot, or contract data.
6. **Market**: comparable products with a public or customer-supplied price and a comparability score from 0 to 1.
7. **Willingness-to-pay points**: the highest price each interviewed buyer would pay, from a study or interviews.

If an input is missing, say what you cannot do without it. Run the calculator with what exists and let it report low confidence. Do not invent values.

## Procedure

### 1. Choose the value metric (what the price scales with)

Test each candidate unit against five questions. Choose the one that passes the most, and say which it fails.

1. Does it rise with the value the customer gets?
2. Can we meter it reliably and let the customer verify it?
3. Can the customer predict their bill?
4. Is it hard to game or split to avoid paying?
5. Does it line up with our costs, and with what the customer is allowed to do with it?

Typical candidates for travel data: markets or routes covered, queries or records, entities tracked (properties, carriers, agencies), users, or a share of the revenue the data enables. Keep one metric per product; add a second only when value and cost split clearly.

### 2. Build the cost floor

Floor per unit = (fixed cost spread over expected units + variable cost + cannibalization) ÷ (1 − royalty percent − margin floor). It is the deal-desk walk-away price, not a target. If expected units are uncertain, run the demand sensitivity.

### 3. Quantify customer value

For each segment, estimate the yearly value one buyer gets at the usage you expect. Follow `references/value-quantification.md`. Start from a measurable outcome (cost avoided, revenue enabled, time saved), not from the data's features. State the capture share (the part of the value you charge for). It is the Council's or the requester's call: do not assume a typical figure, and show the corridor at the shares they name. Customers need a clear return to buy. Mark the source of each figure, and push estimates toward interviews and pilots.

Value depends on coverage. Express value at a reference coverage and let the calculator scale it to the coverage you can actually deliver.

### 4. Gather market and willingness-to-pay evidence

- Comparables: public price lists, published rate cards, customer-supplied quotes. Score comparability honestly: same buyer, same unit, same coverage, same rights. Weak comps are context.
- Never use competitor pricing obtained from a competitor, and never share your pricing with a competitor.
- Willingness to pay: five points are the minimum to use, fifteen to rely on. For a proper study, use `wtp-study-design`.

### 5. Run the corridor calculator

Write the inputs as JSON (see `references/input-schema.md` and `examples/air-shopping-insights.json`) and run:

`python scripts/price_corridor.py --in input.json --md report.md --csv lines.csv`

It returns the floor, the value-based price and cap, the market and willingness-to-pay anchors, a blended recommendation clamped between floor and cap, a list price that allows for the expected discount, prices for extra rights granted, sensitivities, a confidence rating, and flags. Report its numbers; do not recompute them by hand.

### 6. Read the result like a pricer

- **Not viable** (floor above value cap): no price works. Offer options: cut cost or scope, aim at a higher-value segment or right, spread cost across products, or re-check the value estimate.
- **Anchors differ by more than 1.5x**: find out why. Usually a wrong unit, a weak comp, or a value estimate that is too low or too high. Do not average away a disagreement.
- **Segment value-based prices differ by more than 1.5x**: consider fenced segment prices, with fences customers accept (use case, customer type, rights) and that cannot be arbitraged.
- **Priced at the floor or at the cap**: the evidence does not support the target. Say so.
- **Low confidence**: present as provisional, a range to test, with the next evidence to collect.

### 7. Price the granted-right ladder from value

Price each additional right the customer is granted as base price + capture share × the extra value per unit that right creates + its extra risk and supplier cost. Do not use standard multipliers. Treat each AI use as its own right, with its own value case. For API access, the base right is serving the customer's own live transactions; keeping responses, bulk extraction, rebuilding or reselling the data, and feeding AI are broader rights priced from their value, not at the per-call rate (see `price-book-builder/references/api-access-scope.md`). A customer who asks for API access only to collect data is asking for a data right.

### 8. Design the test

Set a pilot plan: three to five design partners across segments, the recommended price, and the outcome of each conversation (accept, counter, decline) with the reason. Define the decision rule up front: for example, "if fewer than half accept at list within the discount band, revisit the value metric before cutting the price." Feed the results back as willingness-to-pay points and rerun.

### 9. Hand off

Give the Pricing Council the memo, the CSV lines (Draft, single tier), and the open evidence list. Then use `price-book-builder` to add volume tiers, discount bands, terms, and the validation check. Reopen this skill when coverage changes, costs move beyond the change threshold in `pricing-governance.md` (Unknown if blank), or a pilot result disagrees with the corridor.

## Output

1. **Headline**: the recommended realized price and list price per unit, the confidence, and the one thing that would change the answer.
2. **Corridor table** and **segments**.
3. **Granted-right ladder** with the reasoning for each step.
4. **Sensitivity table**, including the value of wider coverage.
5. **Flags and next evidence**.
6. **Pilot plan and decision rule.**
7. **Inputs and assumptions**, with each source.

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute with `scripts/price_corridor.py`. Show the inputs next to the result.
- Say which right every price covers. A price without a stated right is not a price.
- Whether we may grant a right is the product manager's check in the rights pack. If the product manager tells you a right cannot be granted, drop that line; do not price around it.
- Label invented, illustrative, or assumed inputs. A worked example is not a quote.
- Do not present a price as certain when confidence is Low.
- Prices are proposals. The Pricing Council approves them and Finance confirms margin floors.
- Keep customer-specific data (individual willingness to pay, contract prices) out of general outputs.

---

## Document: data-product-valuation

# Data product valuation

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Three approaches give three readings. A wide gap is a finding about what we know, not a failure. The result is a value anchor for the corridor in `data-price-setting`, not a price. See `references/frameworks.md` for the named methods and their status.

## When to use

- A data product has no price history.
- The corridor needs a value anchor.
- A large licence or a buyer's dispute justifies a valuation.

Not for: setting the price (`data-price-setting`), pricing a right (`data-license-pricing`).

## Inputs

1. **Cost:** build cost, annual run cost, the horizon in years. From Finance or the product owner; label F with source, or A.
2. **Market:** comparable products with prices, unit, scope and source (`analog-research`, `competitive-price-scan`). Only verified rows.
3. **Income:** the buyer's annual net benefit and how it was estimated, the horizon, and the discount rate. The rate and horizon are the user's or Finance's; none is assumed.
4. The right the product grants (the value changes with the right).

Ask one question at a time. A missing input skips that approach and the output says so.

## Procedure

1. **Gather the inputs** and tag each F, I, A or U with a source.
2. **Run** `scripts/valuation.py --in <file>` (see `examples/input.json`).
3. **Read the range.** Which approach is lowest and highest, and why. The cost approach is what recreation costs; the market approach depends on comparability; the income approach depends on the benefit estimate, usually the weakest input.
4. **State the right** each value assumes, and how the value would change with a narrower or wider right.
5. **Pass the anchor on** to `data-price-setting`. State that the price must sit between the cost floor and the customer value, and who decides.

## Output

Header; the range in one line; table of approaches with basis; what is weak; the right assumed; handoff for the corridor; four-part handoff. Status Draft.

## Quality gate

- Every value comes from the script with its inputs shown.
- Discount rate and horizon are the user's, or the approach is skipped.
- Comparables carry a source and date or are excluded.
- The output states the right the value assumes.
- The range is not turned into a price.

---

## Document: deal-desk-review

# Deal Desk Review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Turn a deal request into a decision-ready package for the approver. You recommend; a named person approves. Never send anything to a customer.

## When to use

- A rep or deal desk analyst submits a non-standard quote for API access, premium software or data products.
- A requested discount is outside the band, or a non-standard term is asked for.
- New or expanded API access is requested (the purpose question applies).

Not for: a new list price (`data-price-setting`), a price change for the Council (`price-change-proposal`), or a data licence request (`data-license-pricing`).

## Inputs

Context library files read: `pricing-governance.md` (approval matrix, bands, floors), `product-catalog.md`, `deal-structures.md`. If a file still says `status: template`, treat its values as Unknown.

Ask for anything missing before analyzing. Do not guess.

1. **Deal request**: customer, segment, products and families (API, software, data), volumes or seats, term, requested price or discount, requested non-standard terms, deadline, competing alternative if known.
2. **Price book**: current list prices, tiers, units, and fences (file or pasted table).
3. **Approval matrix**: tier triggers, approvers, margin floors per product family.
4. **Comparable deals**: recent deals from the deal log with similar product, size, and segment (at least 5 if available).
5. **Customer context**: current spend, usage history, renewal date, open disputes, strategic notes.
6. **For new or expanded API access: the purpose.** What will the customer do with the responses, and for how long will they keep them? Ask when the request does not say. Booking and serving their own traffic is the standard API use. Collecting, storing or analysing data in bulk, rebuilding it, reselling it or feeding AI is a data right and is priced as one (see `price-book-builder/references/api-access-scope.md`).

If the price book or approval matrix is missing or still a template, say so at the top of the answer. Mark the approval route Unknown, name `pricing-governance.md` as the file to fill, and offer `pd-setup`. Do not use remembered or example tiers or thresholds. Still compute the waterfall and the guardrails that need only the price book.

## Procedure

1. **Normalize the request.** Restate the deal in a table: product, unit, quantity, list price, requested price, term, ramp, commit, overage.
2. **Compute the waterfall with code.** Use a script on the provided data; do not do arithmetic in prose. Show list value, each discount layer (volume, term, bundle, special), net price, total contract value, and annualized value. For usage-based pricing, model commit, expected usage, and overage at low, base, and high usage.
3. **Check guardrails.** For each line: discount versus band, price versus floor, margin versus family floor (if cost data is supplied), term and payment terms versus standard, and non-standard clauses (MFN, exclusivity, price protection, redistribution or AI-use rights for data). For data and API lines, state the right the quote grants the customer (`conferred_right`) and check it matches the price: a data right sold at an API booking rate, or a retention or bulk-use request on a per-call price, is a fail. Whether we may grant the right is the product manager's question; list it as an open question.
4. **Compare with similar deals.** Show where this deal sits against comparables on net price per unit and discount depth. Flag if it would become the new low.
5. **Assign the approval route** from the approval matrix in `pricing-governance.md` by the first rule tripped, and name the rule. If the matrix is not filled, write Unknown.
6. **Flag risks.** Precedent risk, cross-family cannibalization, metering or unit ambiguity, supplier-data questions for the product manager, revenue recognition questions for Finance, legal terms for Legal.
7. **Draft two or three counteroffers** that trade value for concessions: for example a larger commit for a deeper tier, a longer term for a lower rate, a smaller starting scope with a ramp, or removal of a clause. Show the waterfall for each.

## Output

Deliver in this order, kept short enough to read in two minutes:

1. **Recommendation** (one line): approve as requested, approve with changes, counter, or decline; plus the approval route.
2. **Deal summary table** and **waterfall table**.
3. **Guardrail results**: pass or fail per check, with the numbers.
4. **Comparables**: small table.
5. **Risks and open questions** for Finance, Legal, Product.
6. **Counteroffers** with their waterfalls.
7. **Approval memo** (under 150 words) the analyst can paste into the approval request: ask, rationale, tier, risks, recommendation.
8. **Inputs and assumptions used**: files, date ranges, assumptions, and anything missing.

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute figures with code and show their source; never estimate in prose.
- Do not invent list prices, floors, or approval rules. If missing, say so.
- Do not approve exceptions or tell the customer anything. Output is for the approver.
- Use customer-specific prices only for this request; do not copy them into general summaries.
- Treat competitor pricing as valid only if the rep supplied it with a source; mark it unverified otherwise.
- If a clause or data right looks like a legal question, escalate it as an open question rather than interpreting it.

---

## Document: deal-desk-triage

# Deal desk triage

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

The daily rhythm of the deal desk. It decides the order of work and who handles each request. It does not price anything itself.

## When to use

- Start of the working day, or when more than one request is open.
- A new request arrives and the desk must decide what handles it.
- Someone asks what is overdue or what to work on first.

Not for: reviewing one deal in depth (`deal-desk-review`), a data licence (`data-license-pricing`), the weekly realization review (`price-realization-analysis`).

## Inputs

A list of open requests: id, account, product, request type, total contract value, requested discount, received and due dates. A CSV is best (see `examples/requests.csv`). Read `pricing-governance.md` for the discount band the desk may approve alone; if it is a template, the band is Unknown. Read the exception log in `workspace/` if one exists.

## Procedure

1. **Rank with the script.** Run `scripts/triage_rank.py --in <file> --today <date>`; add `--band-pct N` only when the band is known from the context library. Order: overdue first, then due soonest, then larger value.
2. **Confirm the route** for each row: non-standard quote to `deal-desk-review`; API or data access request to `api-access-request`; data licence to `data-license-pricing`; renewal to `deal-desk-review` with `account-price-fit`; standard quote from the price book with no review.
3. **Anchor-deal accounts.** If the account has an anchor deal (see `deal-structures.md`), run `account-price-fit` before `deal-desk-review`. Do not review an add-on in isolation.
4. **Check the exception log.** Mark rows whose exception has expired or whose get has not arrived. List unrequited concessions with owner and date.
5. **Name what blocks.** For each request, the missing input and who supplies it. A rights question goes to `rights-handoff`.
6. **Do not approve.** The desk recommends; the approver named in `pricing-governance.md` decides. If it is Unknown, say so.

## Output

1. **Today in one line**: how many open, how many overdue, the first request to work.
2. **Ranked table**: request, account, route, due, band flag, blocker.
3. **Exception log changes**: rows to add, close or chase (use `assets/exception-log.md`).
4. For any request ready to move, start `assets/deal-package.md`.
5. Four-part handoff.

## Quality gate

- The ranking came from the script, or the response says it was ranked by hand.
- Band flags appear only when the band came from the context library or the user.
- Every request has a route and an owner, or is marked Unknown with the question.
- No request is marked Approved. Status stays Draft or For decision.
- Customer-specific prices stay in this output and are not copied into general summaries.

---

## Document: packaging-design

# Packaging design

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A package is a price, a unit, an allowance, a right and the fences that stop customers using a cheaper tier for a dearer use. See `references/frameworks.md` for named methods and their status.

## When to use

- A product needs tiers or packages after the metric is chosen (`value-metric-design`).
- Tiers overlap, have gaps, or let a heavy user sit in a light tier.
- A price book is being rebuilt or released.

Not for: the price level in each tier (`data-price-setting`), checking live customers against tiers (`api-usage-tier-fit`).

## Inputs

The value metric, the corridor or price points from `data-price-setting`, segments and what each does with the product, the rights to offer, usage distribution if known. Ask one question at a time.

## Procedure

1. **Segments to tiers.** Name the segments and what each needs. Give each tier a plain purpose.
2. **Allowances.** Set included amounts on the metric from usage data. If distribution is unknown, mark the boundaries A and name the data that would settle them.
3. **Fences.** What stops a heavy or different use from sitting in a light tier: usage caps, look-to-book bands, retention terms, rights granted, term, audit. Fences sit on the right and the metric, not on the account.
4. **Good, better, best.** Each option states the right it grants. A tier that allows retention, display, resale or AI use is a different right and a different price, never a larger allowance of the same one.
5. **Write the price book lines** in the standard columns with `conferred_right` on every data and API line.
6. **Check**: run `price-book-builder/scripts/check_price_book.py --pricebook <file>` and fix overlaps, gaps and prices that rise with volume.
7. **Test the fences** by asking what a customer wanting the best tier's use at the cheapest tier's price would do.

## Output

Header; the recommendation; a table of packages with unit, allowance, right, fences and price points; checker result; fence test; open questions; four-part handoff. Status Draft.

## Quality gate

- Every data and API package states its granted right.
- The checker ran without errors, or the output says it did not run.
- Boundaries based on assumed usage are tagged A with the data needed.
- Fences are on the metric or the right, not on a named account.
- No list price depends on an account (rule 13).

---

## Document: price-book-builder

# Price Book Builder

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Create list prices that the desk can quote without a custom study each time. Prices come from evidence. Every data and API line says what the customer may do with what they buy (the **granted right**). That scope is part of the product: the same volume sells at a different price for internal use, for keeping the data, or for reselling it. Read `references/granted-scope.md`, and for API lines `references/api-access-scope.md`.

The desk assumes we hold the rights to grant what it prices. The product manager checks that separately with the rights pack. If an existing price book needs to be brought in first, use the `price-book-import` skill.

## When to use

- Creating or revising a price book for API access, software, services or data licences.
- After an import, to set floors, tiers, terms and granted rights.
- A price book must pass the checker before release.

Not for: finding the prices (`data-price-setting`) or releasing the book (`price-book-release`).

## Inputs

Context library files read: `pricing-governance.md` (margin floors, bands), `product-catalog.md`. If a file still says `status: template`, treat its values as Unknown.

1. **Products and scope**: for each data or API product, what the customer receives and what they may do with it. If the scope is not known, price `internal_use` only and say so.
2. **Product attributes**: coverage, refresh frequency, history depth, delivery methods, volume, and number of current customers.
3. **Cost data** if available: cost to produce, source fees owed to suppliers, cost to serve (delivery and support). Ask Finance for the margin floor per family.
4. **Existing prices**: past data deals, quotes, and renewals, with realized price, volume, term, and use.
5. **Value evidence**: willingness-to-pay research, win and loss reasons, and customer value drivers (revenue enabled, cost avoided, time saved).
6. **Benchmarks**: public price lists and published information only, with sources. Never use competitor information obtained directly from a competitor.
7. **Goals and constraints**: penetration targets, strategic accounts, existing contract price protections.

If an input is missing, say what you cannot do without it and what you can do with assumptions that you label clearly.

## Procedure

### 1. Scope the price book

List products and the right each line grants. For API products, decide which of the five uses the line sells (own live transactions, short retention, bulk analysis, rebuilding or reselling, AI) and whether any customer is already using the API for a broader purpose than the price covers.

### 2. Choose the licensing units and structure

Decide, with the evidence, the unit that best tracks value and is easy to meter and audit: calls and bookings for API access, coverage (markets, carriers, properties), records or rows, queries, entities refreshed, or users. Prefer a simple structure: **base annual fee by dataset and coverage** plus a **volume component** where usage varies widely. Choose a delivery dimension (file, API, feed, dashboard) only when delivery cost or value differs. Note the metering source for each unit.

### 3. Build three price anchors per dataset family

For a new product or a new granted right, run the `data-price-setting` skill first and use its corridor, ladder, and confidence as the starting point for each line. Keep this step for refreshing anchors from realized deals.

Compute with code and show the inputs.

- **Floor**: cost to produce and serve, plus any supplier fee, plus the margin floor.
- **Reference**: realized prices from comparable past deals (median and range, by size band), and public benchmarks with sources.
- **Value ceiling**: customer value drivers or willingness-to-pay results, expressed as a share of the value created.

Set the list price inside the range between floor and ceiling, near the reference, and state the reasoning. Where evidence is thin, give a range and mark the line **hypothesis, to test**.

### 4. Set the granted-right ladder

The rights we grant the customer are priced as a ladder relative to `internal_use`. Broader rights (display to third parties, redistribution or resale, derivative products, keeping and reusing responses, AI training, fine-tuning, retrieval or grounding, evaluation) carry higher prices because they create more value and more risk. Derive each uplift from the evidence (value created, reduced exclusivity, supplier fees, risk) and show the logic. Do not apply standard multipliers without evidence. Treat each AI use as its own right. For API access, price collecting or keeping data at the data-licence rate for that right, not at the per-call rate.

### 5. Add tiers, fences, and terms

- Volume tiers with a stated tier model: `all_units` (the tier price applies to all units) or `graduated`
- Floor price per line, discount bands, and the approval tier each discount depth triggers (align with the approval matrix)
- Term discounts and renewal uplift caps
- Minimum commitments, overage rate, true-up, audit rights, and what happens when the licence ends
- Conditions that travel with the right: retention limit, attribution, audit, look-to-book or distinct-query fences, no resale to named competitors

### 6. Write the price book file

Create a CSV with these columns, one row per priced line: `line_id, product_id, product_type, conferred_right, delivery, unit, tier_min, tier_max, list_price, floor_price, currency, term_months, tier_model, status, version` (plus optional `product_name, product_family, annual_revenue, customers, notes`; see `price-book-import/references/standard-price-book.md`). `conferred_right` is for data and API lines: what the customer may do. Leave `tier_max` blank for the last tier. `status` is Existing, Draft or Proposed; only the Pricing Council sets Approved. Keep a second sheet or file for rationale: one row per product and right with the anchors, reasoning, evidence sources, and confidence.

### 7. Validate

Run `scripts/check_price_book.py --pricebook <price-book.csv> [--mode release]` from this skill's folder.

- **Strategy mode (default).** A missing floor, or a data or API line with no stated right, is a warning. Use this while building.
- **Release mode (`--mode release`).** Those two are errors. Run it before a price book goes out for quoting.

The script also checks tier overlaps and gaps, unit price versus volume, volume cliffs, floor above list, duplicates, and that broader rights are not priced below internal use. Fix every error before presenting. Then backtest: re-quote the last 12 months of deals at the new list prices and show the difference against realized prices, by customer size.

### 8. Prepare the decision

Summarize what the Pricing Council must decide: list prices, tiers, floors, approval triggers, fences, and the data and API products the product manager needs to clear (`product_rights_handoff.csv` from the importer, or the list of data and API lines). Note the next review date and what reopens pricing: a new product, a new right requested, or a change in how customers use an API.

### Worked example

`examples/price-book-example.csv` has data, API and software lines. L005 prices the Shopping API for live booking use only. L006 prices bulk retention of the same responses at a much higher rate, with a minimum commitment. Run it in release mode: no issues.

## Output

1. **Headline**: lines priced by type, data and API lines by granted right, and the main uncertainty.
2. **Price book table** (summary) and the CSV file.
3. **Rationale table**: anchors, chosen price, reasoning, evidence, confidence.
4. **Granted-right ladder** with the reasoning for each uplift.
5. **Validation results** and **backtest**.
6. **Council decision list**, including data and API products for the product manager to clear.
7. **Inputs and assumptions used.**

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute figures with code. Show inputs next to every result.
- Say which right every data and API line grants. A line without it is not a priced product.
- An API price covers the use it states. Collecting, keeping or reusing responses is a separate, higher-priced right.
- Never invent costs, benchmarks, or past prices. Mark assumptions and hypotheses.
- Benchmarks come from public or customer-supplied sources with citations; do not infer competitor prices from private conversations.
- Prices are proposals. The Pricing Council approves the price book, and Finance confirms the margin floors.
- Whether we may grant a right is the product manager's check in the rights pack. If it says a right cannot be granted, remove the line.
- Customer-specific past prices are used only to set the reference range; do not reproduce them in general outputs.

---

## Document: price-book-import

# Price Book Import

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Start from the price book the business already uses. Import it, check consistency, and find the lines whose scope (what the customer may do) is not stated.

The pricing desk prices API access, software, services and data. It assumes we hold the rights to sell what the price book sells. The product manager checks that separately with the rights pack. This skill does not look at rights held.

## When to use

- The desk already prices established products and needs to start from that price book.
- A quote tool or spreadsheet export must become the standard format.
- You need the list of data and API lines whose granted scope is not stated.

Not for: building a new price book (`price-book-builder`) or assessing rights held (the product manager).

## Inputs

Context library files read: `systems-and-data.md`, `rights-handoff.md`. If a file still says `status: template`, treat its values as Unknown.

1. **The existing price book**: .xlsx or .csv. Any layout. Say which sheet if there are several.
2. Optional but valuable: **annual revenue and customer counts per product** (even rough). They rank the hand-off list.
3. Optional: which product is which type, if the words in the file are not clear.

If the file cannot be read, or has no price column, say so and stop. Do not invent prices.

## Procedure

### 1. Run the importer

`python scripts/import_price_book.py --in FILE --out-dir OUT [--sheet NAME] [--map map.json] [--default-currency USD] [--version legacy-YYYY-MM] [--tier-model all_units|graduated]`

It finds the header row, maps columns by common names (and by `--map` when the names are unusual), reads prices written as "$1,200", bands written as "0 - 1M" or "10M+", and terms written as "12 mo" or "one-time". It writes `price_book.csv`, `import_report.md` and `product_rights_handoff.csv` (the data and API products and the right each grants, ranked by revenue).

If you cannot run code, do the same steps by hand with a table and label the result as unchecked. Read `references/standard-price-book.md` for the columns.

### 2. Review the report with the person

Show the import report headline and these items, and ask them to correct what is wrong:

- **Column mapping**: right columns for list price, floor, unit, bands, term?
- **Product types** inferred with less than high confidence. Fix with `--map` ("types") and re-run.
- **Tier model**: `all_units` is assumed. If the tiers actually bill graduated, re-run with `--tier-model graduated`, because the volume-cliff check depends on it.
- **Missing floors**: not invented. They come from the `data-price-setting` skill (cost floor) or Finance.
- **Granted scope** on data and API lines: legacy price books rarely say what the customer may do with the data or responses (use it internally, show it, resell it, keep it, train a model). The importer infers a right only from clear words (resale, redistribution) and flags it. Everything else is "not stated": find it in the customer contracts or API terms. Until then treat the line as `internal_use` only. API lines matter most here: ask whether any customer keeps or collects responses, because that is a data right priced at the API rate. Read `../price-book-builder/references/api-access-scope.md`. Set rights per product with `--map` ("rights") and re-run.

### 3. Check consistency

`python ../price-book-builder/scripts/check_price_book.py --pricebook OUT/price_book.csv`

Strategy mode is the default. The checker finds real pricing problems: tiers that overlap or leave gaps, unit price rising with volume, volume cliffs, floor above list, duplicates, and a broader right priced below internal use. Report these as findings about the existing book, not as mistakes of the import.

### 4. Hand off to the product manager

Give `product_rights_handoff.csv` to the product manager. It lists each data and API product with the right it grants, revenue and customers. The product manager adds the source datasets and decides whether we hold what each right needs. This does not block pricing work. Do not guess the source datasets.

## Output

1. **Headline**: lines imported, products by type, data and API lines with no stated scope, lines with errors.
2. **Consistency findings** on the existing price book.
3. **Hand-off list** (top products by revenue and the right each grants).
4. **Decisions needed** from the person (types, tier model, floors, granted scope, API retention).
5. **Files written** and **Inputs and assumptions used**.

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Never invent a price, floor, term, revenue figure or right. Blank stays blank and is reported.
- Imported lines have status Existing. Nothing is Approved. Only the Pricing Council sets Approved.
- Do not assess rights held. That is the product manager's work in the rights pack.
- Customer-specific revenue stays in the working files and is not copied into general summaries.

---

## Document: price-book-release

# Price book release

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

A price book is released once, to quoting, with a log of what changed and a calendar of who must be told. This skill prepares the release. A person approves and publishes it.

## When to use

- Annual release, or any new version going to quoting.
- A Council-approved change is about to take effect and customers need notice.

Not for: building or editing lines (`price-book-builder`), importing an old book (`price-book-import`), deciding a change (`price-change-proposal`).

## Inputs

1. The new price book CSV and the previous released version.
2. The Council decision that approved the changes, with date (decision log). Without it the release is a draft.
3. A contracts file for notice: contract id, account, notice days, price protected until. Notice days are contract values; blank is Unknown.
4. The effective date and today's date.
5. `pricing-governance.md` and `product-catalog.md`. If either is still a template, warn at the top: the release cannot be checked against governance.

Ask one question at a time for what is missing.

## Procedure

1. **Check in release mode.** `python price-book-builder/scripts/check_price_book.py --pricebook <new> --mode release`. A missing floor, or a data or API line with no stated granted right, is an error. Do not release with errors.
2. **Write the change log.** `scripts/price_book_diff.py --old <old> --new <new>`. Match every change to a Council decision.
3. **Build the notice calendar.** `scripts/notice_calendar.py --in <contracts> --effective <date> --today <date>`. Show where the effective date cannot be met, where a price protection blocks it, and where notice is Unknown.
4. **Refresh the rights hand-off.** Run `rights-handoff` for the new book and show open rows. Open rows do not block pricing but are listed in the release note.
5. **Independent review.** Run `pricing-stakeholder-review` on the diff, or ask a person to. State which.
6. **Release note.** What changed, effective date, who is told by when, open rights rows, open questions. Status For decision until a person signs off.

## Output

Header; the answer (releasable or not, and why); checker result; change log; notice calendar; rights hand-off status; review note; sign-off line for a named person; four-part handoff.

## Quality gate

- The checker ran in release mode with zero errors, or the release is marked blocked.
- Every change in the log traces to a Council decision, or is flagged unapproved.
- No notice period or protection date is assumed; Unknown is listed for Legal.
- Every data and API line states the granted right.
- The release is never worded as published or approved; a person does that.
- Nothing is sent to a customer.

---

## Document: price-change-proposal

# Price Change Proposal

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Turn a proposed price or packaging change into a decision package for the Pricing Council. The council decides; Legal confirms notice terms.

## When to use

- Proposing a change to list price, tiers, units, a fee, or packaging.
- A cost or supplier change forces a price move.
- A renewal needs a price increase and the notice terms matter.

Not for: setting a price for a new product (`data-price-setting`) or one account's concession (`deal-desk-review`).

## Inputs

Context library files read: `pricing-governance.md`, `deal-structures.md` (notice and price protection terms), `systems-and-data.md`. If a file still says `status: template`, treat its values as Unknown.

1. **The change**: product family, what changes (list price, tier boundaries, unit definition, new fee, discontinued plan), proposed effective date, rationale.
2. **Customer base**: customer, plan, current price, volume, contract end date, segment.
3. **Contract terms**: price-protection periods, notice periods, MFN clauses, renewal terms (a summary table is fine).
4. **Price book** (current version).
5. **Elasticity or churn assumptions**: from past price changes, research, or the desk's estimates. If none exist, say so and use stated ranges, clearly labeled as assumptions.
6. **Competitive context**, if available, with sources.

## Procedure

1. **Restate the change** in one table: before and after, by plan and unit.
2. **Segment customers** by how the change affects them: unaffected, increase, decrease, and by size of change. Compute with code.
3. **Check contracts.** Mark each customer: change can take effect at the proposed date, only at renewal, or only after notice. Show the earliest effective date per group and the share of revenue in each. Flag MFN or price-protection conflicts for Legal. Do not interpret contract language; quote the clause reference and escalate.
4. **Model scenarios with code**: base, low, and high, varying volume response and churn by segment. Show revenue, margin if cost is supplied, and customers lost or downgraded, month by month for 12 months, with the assumptions in a table.
5. **Compute sensitivities**: which assumption moves the result most.
6. **Build the notice calendar**: contract notice deadlines, internal approval dates, communication dates, effective dates.
7. **Draft a risk register**: churn in key accounts, win-rate effect, partner or channel reaction, billing and system readiness, legal exposure, and perception risk. Give each a mitigation and owner role.
8. **Outline communications** (not final copy): audiences, key message, what changes, what does not, timing, and who speaks to strategic accounts.

## Output

1. **One-page council memo**: decision requested, change, rationale, scenario results in a small table, top three risks, recommendation, and the conditions for approval.
2. **Scenario model summary** and **assumptions table**.
3. **Impacted customer list** (top 25 by revenue plus counts by group).
4. **Contract and notice summary** with items escalated to Legal.
5. **Notice calendar**.
6. **Risk register.**
7. **Communication outline.**
8. **Post-change monitoring plan**: metrics, checkpoints and thresholds agreed with the Council (Unknown until set).
9. **Inputs and assumptions used.**

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute all figures with code; show the assumptions behind every scenario.
- Never present a point estimate without the range.
- Do not state that a change is allowed under a contract; list what Legal must confirm.
- Do not contact customers or draft customer-facing final copy from this skill.
- Keep customer-specific figures inside the proposal; do not copy them into general summaries.

---

## Document: price-realization-analysis

# Price Realization Analysis

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Explain the gap between what the price book says and what customers actually pay, find where it leaks, and say what to do about it.

## When to use

- The weekly or monthly pricing review.
- Realized price is below plan or a customer's invoice is far below list.
- Revenue leakage needs sizing and an owner.

Not for: judging a single deal (`deal-desk-review`) or API tier fit (`api-usage-tier-fit`).

## Inputs

Context library files read: `systems-and-data.md`, `pricing-governance.md`. If a file still says `status: template`, treat its values as Unknown.

1. **Billing lines** for the period: customer, product, unit, quantity, billed amount, invoice date, credits and adjustments.
2. **Price book** (versioned, with effective dates) so list value can be rebuilt for each line.
3. **Deal log or contract terms**: approved discounts, commits, ramps, tier, approver.
4. **Optional**: metered usage for the same period, to test billing against usage.

If the price book version or deal log is missing, state which analyses you can and cannot run.

## Procedure

1. **Reconcile first.** Check totals against finance revenue if provided. Report row counts, nulls, duplicates, and unmatched products. Stop and report if the reconciliation gap exceeds the tolerance set in `pricing-governance.md` or by the user (ask if Unknown), since every later figure inherits it.
2. **Rebuild list value** for each line from the price book version in force on the invoice date.
3. **Build the waterfall with code**: list value, then approved discounts, then unapproved or unexplained discount, then credits and adjustments, then billing and metering gaps, to realized revenue. Report in USD and as a percent of list.
4. **Cut it** by product family, segment, discount tier, customer (top 20), contract vintage, and sales owner if provided.
5. **Classify leakage drivers**: approved discount beyond guardrail, discount with no recorded approval, expired promotions still applied, unbilled overage or usage, tier mismatch, credits and write-offs, price book errors, unit definition problems.
6. **Size and rank** each driver by monthly and annualized value, and by recoverability (easy fix, needs customer conversation, needs contract change).
7. **Recommend actions** per top driver: owner role, step, expected recovery range, and how it would be verified.

## Output

1. **Headline**: realization rate for the period, change versus prior period if data allows, and the largest driver in one sentence.
2. **Waterfall** (chart or table) with list, each step, and realized.
3. **Top five leakage drivers** table: driver, value, share, recoverability, owner.
4. **Customers and segments to review** (top 10), each with the reason.
5. **Recovery plan**: actions in priority order.
6. **Data quality notes**: reconciliation result, rows excluded and why.
7. **Inputs and assumptions used.**

## Quality gate

Before finishing, confirm each. They also bind every step above.


- Compute everything with code. Show the script's key figures and where they come from.
- Never present unreconciled data as final; label it provisional.
- Separate approved discount (policy working as designed) from unexplained discount (a control gap). Do not treat all discount as leakage.
- Do not name individual sales reps in broad summaries; give owners at role or team level unless the Analytics Lead asks for detail.
- Hand the Analytics Lead the data checks to sign off before the results go beyond the desk.

---

## Document: pricing-stakeholder-review

# Pricing stakeholder review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

The proposer cannot see their own blind spots. Each lens reads the proposal as someone who was not in the room, and says what they would ask, object to and need. The lenses are in `references/stakeholder-lenses.md`.

## When to use

- A proposal is heading to the Council (`council-decision-pack`).
- Before a price book release (`price-book-release`).
- Any time rule 7 applies: independent review before anything leaves the desk.

Not for: sales-side stakeholder maps of a customer's buying group (use Sales-OS), or a replacement for a real person's sign-off.

## Inputs

The proposal (price change, new construct, deal package, price book diff) and its computed numbers. Roles and names for each lens come from the context library; if absent, use role names only. Ask one question at a time for what is missing.

## Procedure

1. **Pick the lenses** the proposal touches and say which are skipped and why. A data or API line always includes product manager and Legal.
2. **Run each lens fresh.** With subagents, run each lens on its own with only the proposal and the lens definition, so one reading does not colour another. Without subagents, run them in turn and say the review was not independent.
3. **Each lens returns** three lines: top question, top objection, what would change the proposal. Tag every statement I (inference) unless a real person has given a view; then quote it with date and source and tag F.
4. **Show conflicts** between lenses side by side. Do not resolve them.
5. **Sort the findings**: must fix before the Council; should answer in the pack; note only.
6. **Rights questions** go to `rights-handoff`. Clause questions go to Legal as questions, not interpretations.

## Output

Header; the finding in one line (the number of must-fix items); a table with one row per lens; conflicts; findings sorted by must fix, should answer, note; four-part handoff. Status Draft.

## Quality gate

- Every lens statement is tagged I, or F with a dated source.
- No lens invents a named person's opinion.
- Skipped lenses are listed with the reason.
- The review says whether it was independent (separate runs) or sequential.
- Findings are not softened to match the recommendation.
- Nothing in the review approves or rejects the proposal.

---

## Document: pricing-win-loss

# Pricing win and loss review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

"We lost on price" is a hypothesis. This skill tests it against the deal record and separates price from value, packaging, terms and a competitor.

## When to use

- Quarter end, as an input to `quarterly-price-review`.
- After a notable loss or a run of wins at deep discount.
- When sales says price is why deals are lost.

Not for: a sales-side win-loss on selling behavior (use Sales-OS), or reviewing a live deal (`deal-desk-review`).

## Inputs

A deal list with outcome, price cause, discount and competitor (CSV, see `examples/deals.csv`). Where available: the final quote, the deal desk package, and the buyer's stated reason. Causes entered by sellers are their reading; ask for the buyer's words when they exist.

Read `pricing-governance.md` for the band. Unknown is a valid answer. Ask one question at a time for what is missing.

## Procedure

1. **Tally with the script.** `scripts/winloss_tally.py --in <file>` counts causes by outcome and gives average discounts. Always report n. Make no significance claim.
2. **Separate the causes.** Price level, value gap, packaging or metric, terms, competitor price, no price reason. A loss with a deep discount offered is not a price-level loss.
3. **Check discount against outcome.** Did deeper discount buy wins, or did the same deals win anyway? Show the evidence, tagged F, I, A or U.
4. **Competitor claims.** Competitor prices are valid only with a source and date (see `competitive-price-scan`); otherwise mark them unverified.
5. **Propose changes** by lever: list, packaging, value metric, band, terms, fences. Each names the evidence and what would disprove it. Send accepted ideas to `price-change-proposal`.
6. **Say what the record cannot show.** Missing causes, thin counts, sellers' reading only.

## Output

Header; the finding in one line; tally table with n; discount against outcome; competitor table with sources; proposed changes with evidence and disproof; limits of the data; four-part handoff. Status Draft.

## Quality gate

- Counts and averages came from the script or the input; n is shown everywhere.
- Seller opinion is tagged I, not F.
- No conclusion that price caused a loss when the record shows a discount was offered and refused for another reason.
- Competitor prices carry a source and date, or are marked unverified.
- No change is recommended from fewer deals than the user would trust; say the count and let the user decide.

---

## Document: quarterly-price-review

# Quarterly price review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Once a quarter, every line gets the same questions: is it priced to value, to the market, and does it realize? The review ends in proposals for the Council, each with evidence and a test that would prove it wrong.

## When to use

- The quarter has closed.
- Before the Council meeting that follows it.
- Someone asks which lines to change, hold or retire.

Not for: the weekly view (`weekly-pricing-review`), one change in depth (`price-change-proposal`), the annual release (`price-book-release`).

## Inputs

The price book; three months of weekly reviews and realization (`price-realization-analysis`); win-loss for the quarter (`pricing-win-loss`); the latest competitor scan (`competitive-price-scan`); willingness-to-pay evidence (`wtp-study-design`); the decision log with earlier changes and their forecasts; the exception log. Ask one question at a time for what is missing and list gaps in the review.

## Procedure

1. **List the lines** from the price book, with the granted right for each data and API line. A line with no stated right is a finding.
2. **Gather the three readings per line:** value (WTP, `data-product-valuation`), market (scan, analogs), realization (weekly roll-ups, `price-realization-analysis`). Run the scripts; do not estimate.
3. **Add win-loss and usage fit** (`pricing-win-loss`, `api-usage-tier-fit`).
4. **Close the loop:** for each change approved in the last four quarters, compare forecast with realized effect and name the gap and likely cause. Send repeated misses to `pd-ratchet`.
5. **Refresh analogs.** Re-check entries and add new ones (`analog-research`).
6. **Recommend** change, hold or retire for each line, with the evidence and a disproof test. Changes go to `price-change-proposal` and `council-decision-pack`.
7. **Review the exceptions.** Concessions still open without a get; accounts whose anchor deal is up for renewal.

## Output

Fill `assets/quarterly-review.md`: the line table, proposed changes, forecast against realized, analog library changes, Missing, four-part handoff. Status Draft.

## Quality gate

- Every line appears, even if only to say hold and why.
- All figures come from scripts or sources named in the review.
- Every change proposal carries evidence and a disproof test.
- Forecast against realized is shown for earlier changes, or the output says no forecast was recorded.
- No threshold or target appears that the context library or the user did not supply.
- Nothing is marked Approved.

---

## Document: rights-handoff

# Rights hand-off

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

Pricing states the right it grants. The product manager decides whether we hold what that right needs. This skill is the bridge: it asks, and it reads the answer back. It never answers.

## When to use

- A price book is imported, released or changed.
- A new product, or a wider right on an existing one, is being priced.
- A customer asks for more than the price grants.
- Someone asks "do we have the right to...". The answer is: that is the product manager's call; here is the list entry.

Not for: assessing rights held (the separate Rights Desk), pricing the right (`data-license-pricing`).

## Inputs

The price book (`conferred_right` on every data and API line). The route from `rights-handoff.md` in the context library: contact, how lists are sent, how answers return, planned response time. Blank is Unknown; ask one question at a time. Optionally `rights_answers.csv`: product_id, conferred_right, answer, date, who.

## Procedure

1. **Build the list.** `scripts/rights_list.py --pricebook <file> [--answers <file>] [--out product_rights_handoff.csv]`. One row per product and right, ranked by revenue where known.
2. **List the gaps.** Data or API lines with no stated granted right cannot be asked about. Send them back to `price-book-builder`.
3. **Send by the route on file.** Prepare the message and the file; ask before sending anything. If the route is Unknown, say so and offer `pd-setup`.
4. **Read the answers back.** Show each answer exactly as written, with date and author. Do not summarise it into cleared or not cleared; the product manager's wording stands. If a line's right was answered as not grantable, tell the user and recommend removing the line; the Council decides.
5. **Update the status** on the pack or release that waits for it: open, answer on file, not needed.
6. **Keep pricing moving.** An open row does not block pricing work; a price is labelled pending the rights answer.

## Output

Header; the answer (open rows and rows with an answer); the list table; gaps; draft message to the product manager (not sent); four-part handoff.

## Quality gate

- The skill never states whether we hold a right.
- Every row names a product, a right granted from the nine, and an answer or Open.
- Answers are shown verbatim with date and author.
- The message is a draft; nothing was sent without approval.
- Customer names do not appear in the list; products and rights do.

---

## Document: value-metric-design

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

---

## Document: weekly-pricing-review

# Weekly pricing review

Read `references/operating-rules.md` and `references/capabilities.md` first. Start every output with the header in `references/output-conventions.md`.

One page, same day each week. It tells the desk where money leaked, which accounts need a conversation, and what to do before next week.

## When to use

- The weekly review day.
- Realized price fell and someone asks why.
- Input to the monthly Council pack (`council-decision-pack`).

Not for: a deep leakage study by customer and segment (`price-realization-analysis`), a single deal (`deal-desk-review`), tier design (`api-usage-tier-fit`).

## Inputs

1. Billing lines for the week and at least the prior week: week, family, list value, realized value, cause (CSV, see `examples/lines.csv`).
2. API usage by key, if available (searches, bookings, distinct queries). The screen and its threshold come from `api-access-request`; the threshold is a company value and may be Unknown.
3. The exception log from `workspace/`.
4. A plan or target for realization, only if the user supplies it. None is assumed.

Ask one question at a time for what is missing. Say which sections are skipped for lack of data.

## Procedure

1. **Roll up with the script.** `scripts/weekly_roll.py --in <file> [--week YYYY-MM-DD]` gives the realization rate against the prior week, by family and by cause.
2. **Read the gap.** Name the largest cause and the family with the largest change. Treat Unlabeled causes as a finding: someone must label them.
3. **Usage fit.** For API keys, apply `api-usage-tier-fit` and, for a flagged pattern, the screen in `api-access-request`. Word every flag as "possible data collection, to confirm".
4. **Exceptions.** Count new, expiring and unrequited concessions from the exception log.
5. **Choose three actions**, each with an owner and a date. If an owner is not known, write Unknown and ask.
6. **Route.** Rights questions to `rights-handoff`. Price changes to `price-change-proposal`. Large exceptions to `deal-desk-review`.

## Output

Header; one line on the week; realization table; leakage by cause; usage fit and flags; exceptions; three actions with owners and dates; Missing list; four-part handoff. Status Draft. Keep to one page.

## Quality gate

- Every number came from the script or the input and says so.
- No target or threshold is shown that the user or the context library did not supply.
- Flags are questions to confirm, never findings against a customer.
- Exactly three actions, each with an owner and date, or a stated reason there are fewer.
- Customer names stay in this internal review and are not copied into broader summaries.

---

## Document: wtp-study-design

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
