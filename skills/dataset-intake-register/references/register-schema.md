# Data Rights Register: Schema

The register is a workbook with six sheets plus a Vocabulary sheet. One dataset has one row in `Datasets`, many rows in `Use_Rights`, `Fields`, `Evidence`, and `Open_Questions`, and every change is logged in `Change_Log`.

## Datasets

| Column | Meaning |
| --- | --- |
| dataset_id | Stable ID, format `DS-<SOURCE>-<NNN>` (for example DS-OWN-001, DS-SUP-014). Never reused. |
| name | Short business name |
| description | What the data is, in one or two sentences |
| owner_role | Accountable data owner (a role, not a person) |
| source_type | Owned, Supplier-sourced, Customer-contributed, Third-party licensed, Public, Derived |
| source_name | Supplier, customer, or system the data comes from |
| parent_dataset_ids | For Derived datasets, the datasets it is built from (semicolon separated) |
| coverage | Markets, carriers, properties, or entities covered |
| refresh_frequency | Real time, hourly, daily, weekly, monthly, static |
| history_depth | How far back the data goes |
| delivery_methods | API, file, feed, dashboard (semicolon separated) |
| volume_estimate | Rows or records, with the date measured |
| contains_personal_data | Yes, No, Unknown |
| sensitivity | Public, Commercial-confidential, Supplier-confidential, Personal |
| status | Draft, In legal review, Approved, Restricted, Rejected, Retired |
| version | Integer, increments on every material change |
| last_reviewed | Date |
| next_review | Date, no later than 12 months after last_reviewed, or at contract expiry if sooner |
| approved_by | Legal approver role (set by Legal only) |
| approved_date | Date (set by Legal only) |
| notes | Free text |

## Use_Rights

One row per dataset and use right.

| Column | Meaning |
| --- | --- |
| dataset_id | Link to Datasets |
| use_right | See vocabulary below |
| status | Granted, Conditional, Prohibited, Unknown (proposed by intake from the evidence) |
| conditions | Conditions, limits, or restrictions as stated in the evidence |
| geography | Where the right applies, if limited |
| term_end | Date the right ends, if stated |
| evidence_ref | One or more evidence_id values |
| legal_confirmed | Yes or No. Set by Legal only. Anything other than Yes is treated as Unknown downstream. |
| confirmed_by | Legal approver role |
| confirmed_date | Date |

### Use-right vocabulary

- `internal_use`: use inside the licensee's own business operations
- `internal_analytics_shared_outputs`: internal analytics where derived outputs (reports, charts) are shared outside the licensee
- `display_to_third_parties`: showing the data or substantial extracts to the licensee's own customers or partners
- `redistribution_resale`: passing on or reselling the data itself
- `derivative_data_product`: building a new data product from this data
- `ai_training`: training or pre-training a model
- `ai_fine_tuning`: fine-tuning a model
- `ai_retrieval_grounding`: supplying the data to a model or agent at query time
- `ai_evaluation`: benchmarking or evaluating a model

## Fields

| Column | Meaning |
| --- | --- |
| dataset_id | Link to Datasets |
| field_name | Column or attribute name |
| description | Meaning of the field |
| data_type | String, number, date, boolean, JSON, other |
| sensitivity | Public, Commercial-confidential, Supplier-confidential, Personal |
| origin | Where the value comes from |
| restricted_uses | Use rights that do not apply to this field |
| notes | Masking, aggregation, or removal requirements |

## Evidence

Record a pointer and a short plain-language summary. Do not paste long clause text.

| Column | Meaning |
| --- | --- |
| evidence_id | Format `EV-NNNN` |
| dataset_id | Link to Datasets |
| document_name | Contract, terms, policy, or message |
| document_type | Supplier agreement, Customer agreement, Terms of service, Policy, Email, Other |
| location | Section, clause number, or page |
| summary | One or two sentences in your own words, as stated by the document |
| added_by | Role |
| added_date | Date |

## Open_Questions

| Column | Meaning |
| --- | --- |
| question_id | Format `Q-NNNN` |
| dataset_id | Link to Datasets |
| question | The specific question |
| owner_role | Legal, Product, Data engineering, Finance, Sales operations |
| priority | High, Medium, Low |
| status | Open, Answered, Closed |
| due_date | Date |
| resolution | The answer and where it is recorded |

## Change_Log

| Column | Meaning |
| --- | --- |
| date | Date of change |
| dataset_id | Link to Datasets |
| change | What changed |
| changed_by | Role |
| reason | Why |
| version | Dataset version after the change |

## Status rules

- A dataset moves Draft, then In legal review, then Approved. Only Legal sets Approved, Restricted, or Rejected.
- Approved means the Use_Rights rows with legal_confirmed = Yes are authoritative. All other rows count as Unknown.
- A dataset returns to In legal review when its contract is renewed or ends, its source changes, its schema changes materially, or a new use right is requested.
