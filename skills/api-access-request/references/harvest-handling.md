# Handling a usage pattern that may be data collection

A pattern in the usage screen is a question. It is not a finding, and nothing here is sent to the customer by the desk. Use it when `scripts/harvest_screen.py` shows a signal, or when a request describes bulk use.

## 1. Preserve the evidence before anyone calls the customer

- Save the screen output with its date, the CSV it ran on and the company values it used (segment medians, multiple, distinct-query share, retention, minimum volume).
- Ask the data owner in `systems-and-data.md` (Unknown if blank) to keep the underlying logs for the period. Do not alter or delete anything.
- Note what the desk does not know: the customer's purpose, the contract's retention and reuse terms, whether several keys belong to one customer.

## 2. Read the contract before the conversation

- Find what the contract and API terms say about caching, storing, reuse, redistribution and AI use. Quote clause references; do not interpret them.
- If the terms are unclear or a breach is possible, stop here and take it to the approver for contract questions in `pricing-governance.md` (Unknown if blank). Legal is consulted **before** the first contact with the customer, not after.

## 3. First contact: a neutral question, from the account owner

The account owner asks. The desk does not. Suggested script, adapted:

> We are reviewing how API access is used across our customers so that each plan fits how it is used. Your usage on [keys] looks different from other [segment] customers. Could you tell us what the responses are used for and how long they are kept? If the use is wider than live bookings, we can look at a plan that fits it.

Do not say or imply that the customer has done something wrong. Do not name the signals. Do not threaten a key or a price.

## 4. Record the answer and place it in the nine rights

- Booking only, responses dropped after the session: `internal_use`. Standard API price. No change.
- Keeping, bulk analysis, rebuilding, reselling or AI: a wider right. Name it from the nine rights and price it as a data licence with a minimum commitment, a retention term and an audit right (`data-license-pricing`).
- Will not say, or the answer conflicts with the logs: do not price as booking use. Hold the quote and take it to the approver in `pricing-governance.md`.
- Whether we may grant the wider right goes to the product manager (`rights-handoff`). The desk prices; it does not decide that.

## 5. A path that keeps the customer

If the customer wants the wider use and we can grant it, offer a **capped no-retention trial** with a **priced step-up**:

- A capped volume, no retention beyond the session, a fixed period.
- The step-up price for the wider right is stated up front, so that the customer knows the price of continuing.
- Run `account-price-fit` first if the account has an anchor deal; any concession is a give tied to a get, inside the approved band, and logged.

Rate limits alone are a technical control. They are not a price and they do not change what the customer may do with the data.

## 6. Close

Record the outcome in the exception log (if a concession was made) and in `lessons.md` if the screen's values need changing (`pd-ratchet`). Status stays Draft until the approver decides.
