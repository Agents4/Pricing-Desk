# API access: what the call may be used for

An API call is not only a transaction. The same call can serve a live booking, or it can be one of ten million calls that rebuild our data in someone else's database. Some customers ask for API access only to harvest data. The price book must say which of these it sells.

## Five uses of an API, in order of what they take from us

| Use | Conferred right | What it looks like | How to price |
|---|---|---|---|
| Serve their own live transactions | internal_use | A search leads to a booking. Responses are shown to a traveller, held for the session, then dropped | Per-call tiers. This is the standard API price |
| Keep responses for their own operations | internal_use plus a retention term | Caching for latency, storing booked itineraries, audit trail | Included up to a stated retention period (for example the session, or 24 hours). Longer is a priced option |
| Bulk extraction for analysis | internal_analytics_shared_outputs, or internal_use with a volume fence | Pulling far more than they book, to analyse | Data-licence rate, not the per-call rate. Minimum commitment |
| Rebuild or resell the data | derivative_data_product, redistribution_resale | Storing responses to build their own fare database, feed or benchmark | Data-licence price for that right, with a minimum commitment and audit |
| Feed AI systems | ai_retrieval_grounding, ai_training, ai_fine_tuning, ai_evaluation | An agent that calls the API for answers, or a model trained on responses | Each AI use is its own line. Agent traffic is priced for its volume, which is higher and less tied to bookings |

If the line does not say which row it is, the customer is buying the first row and nothing else.

## Signs a request is about the data, not the booking

Treat these as questions to confirm, not as findings:

- Look-to-book ratio far above the segment norm. Compute it per key and compare with the median.
- Distinct-query ratio: many different origins, destinations and dates with no repeat, and no bookings behind them. Sweeping the whole market is a harvest pattern.
- Retention: the contract or the integration description mentions storing, caching beyond the session, replicating or a "data lake".
- Volume per key is far above what their booking volume could need.
- The stated use case is analytics, pricing intelligence, benchmarking, or "AI".
- Requests concentrate off-peak or on one route family, in a scheduled pattern.
- Traffic from many keys or addresses that act as one customer.

Machine traffic is not misuse by itself. Agents and scrapers are legitimate customers when they buy the right scope. The point is to price the scope they actually use.

## Fences and metrics to put in the price book

- Retention limit in the notes and the contract (for example "session only").
- Look-to-book cap or a distinct-query cap, with an overage rate and a review trigger.
- Volume per key and per customer, with a commitment above a threshold.
- Rate limits are a technical control. They do not replace a price.
- Measure from the logs: calls, bookings, distinct queries, response size, keys per customer.

## Pricing a harvest request

1. Ask what they will do with the responses and how long they will keep them. Record the answer.
2. If the answer is outside the first two rows, do not quote the per-call price. Quote the data-licence rate for that right (`data-license-pricing`), with a minimum commitment, a retention term and audit.
3. Give the product manager the request. They decide whether we can grant it. The pricing desk does not decide that.
4. Where the customer will not say, price the call at the harvest rate or decline. Do not default to the booking rate.
