# Phase 0: Domain brief

Status: draft for confirmation. Written 2026-10-24.

## User
The pricing desk of a travel-technology (GDS) company: a small team (pricing lead, analysts, deal desk analyst, pricing operations) plus the people who feed it (product managers, sales, Finance, Legal, engineering for metering). The OS is used by the desk and by anyone who needs a pricing answer: an account owner with a deal, a product manager with a new product, a Council member preparing for a decision.

## What it prices
API access (search, price, book, post-booking, insights), premium software, services, and data products and licences. Several of these touch third-party content (airlines, hotels, agencies), so the same data can be sold as an API, a feed, an insight product or an AI-grounding feed. The company is a two-sided marketplace: it holds rights from suppliers and customers and sells products derived from them.

## Decisions the OS supports
1. What to charge for a new product, right or API use (the corridor, the ladder, the fences).
2. Whether a deal is acceptable and who must approve it.
3. Where list price leaks before it is realized, and what to do.
4. Whether an API customer sits in the right plan, or is using the API to collect data.
5. Whether, when and how to change a price.
6. Whether the price book can be released for quoting.

## Deliverables
Corridor memos; the price book; deal packages and counteroffers; weekly realization and usage reviews; monthly Council decision packs; quarterly price reviews; annual price book release; analog and benchmark research; WTP study designs; price change proposals; hand-off lists for the product manager's rights check.

## Frequency
Daily (deal desk), weekly (realization and API usage), monthly (Council), quarterly (price review), annual (release), and event-driven (launch, harvest flag, supplier cost change, competitor move).

## Sensitivity
Customer-specific prices and usage, supplier-confidential terms, internal margins and floors. The company is mid-move from Microsoft to Google, and the lead has limited admin rights on both. No platform-locked builds.

## What success means
- A quote or a price decision comes back with numbers computed, sources shown, and the right the price covers stated.
- Leakage and harvesting are found by a routine, not by luck.
- The Council decides from a pack in one sitting.
- The price book can be released with a clean check, and every change is logged.
- The system improves from each deal and each miss.

## The three costliest mistakes
1. **Pricing the volume and not the scope.** An API or data price that does not say what the customer may do lets a customer pay a booking price and use a data right.
2. **Discounting without a trail.** Approved discount and unexplained discount look the same in the invoice, so leakage cannot be recovered or governed.
3. **Changing price without a test, a notice calendar and a rollback.** Contract notice terms, MFN clauses and price protection turn a good price into a dispute.

## What experts do differently
They start from the customer's value and the value metric, not from cost; they separate list, pocket and realized price; they fence every discount; they run a fixed rhythm so decisions are not ad hoc; they test before they roll out; they write down why. In this domain they also watch search-to-book economics, because the cost of serving a call is real and the value of a call is not equal.

## Existing assets
Nine skills (deal desk review, realization, API tier fit, price change, WTP study design, corridor, import, price book builder, data licence pricing), a price book checker, an importer, a price corridor calculator, a Copilot guide with nine playbooks, a Gemini CLI extension, and a Rights Desk companion (separate repo) for the rights we hold.

## Platforms
Gemini CLI extension (primary), Gemini app and Notebook (Google, the company is moving). Microsoft Copilot Notebooks stay as a legacy adapter for the transition. Claude Code files are generated for the author's use.

## Out of scope
Assessing the rights we hold (Rights Desk). Approving prices (the Pricing Council). Contacting customers. Contract interpretation (Legal). Billing and quote-tool configuration (handed off).
