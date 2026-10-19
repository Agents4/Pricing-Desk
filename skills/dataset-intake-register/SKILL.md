---
name: dataset-intake-register
description: Onboard a new or existing dataset into a controlled data rights register. Captures source, rights evidence, use-right status, field sensitivity, and open legal questions, then produces a register entry and a Legal review packet. Also creates the register workbook when none exists. Use when a dataset is proposed for licensing and has no approved register entry, or when building the register for the first time.
---

# Dataset Intake and Rights Register

Turn a dataset and its paperwork into a controlled register entry that pricing can rely on. The register is the only source for what may be licensed. This skill gathers evidence and proposes statuses; **only Legal confirms rights and approves entries.**

Read `references/register-schema.md` first. It defines every sheet, column, the use-right vocabulary, and the status rules.

## Modes

- **Bootstrap**: no register exists. Create one, then run intake for the first datasets.
- **Intake**: add one new dataset.
- **Backfill**: add many existing datasets. Work in this priority order: datasets already in customer contracts, datasets in live deals, datasets in planned products, everything else. Report coverage after each batch.

Ask which mode applies if it is unclear.

## Bootstrap

Run `scripts/create_register.py <path>.xlsx` from this skill's folder. It builds the workbook with all sheets and dropdowns and refuses to overwrite an existing file. Tell the owner of the desk where the file should live: one controlled location, with edit access limited to the register steward and Legal, and read access for pricing.

## Intake process

### 1. Collect the request

Ask for anything missing; do not guess.

- Dataset name, business purpose, requester, and the product or deal it supports
- Data owner role and the system it comes from
- Source: owned, supplier-sourced, customer-contributed, third-party licensed, public, or derived (and from which datasets)
- Source documents: supplier or customer agreements, terms of service, internal policies, and relevant emails
- Schema or data dictionary and a small sample (no live personal data)
- Coverage, refresh frequency, history depth, delivery methods, and approximate volume

### 2. Assign identity

Propose a `dataset_id` in the form `DS-<SOURCE>-<NNN>`, using the next free number in the register. Check for duplicates and near-duplicates by name, source, and schema. If a related entry exists, link it through `parent_dataset_ids` or treat the request as a new version.

### 3. Extract the evidence

Read each document and record, in the `Evidence` sheet, one row per relevant provision: document, location (clause or page), and a one or two sentence summary in your own words. Never paste long clause text. Cover:

- What the company is allowed to do with the data and for whom
- Restrictions on redistribution, display, derivative products, and any AI use
- Geographic, term, and exclusivity limits
- Confidentiality, attribution, audit, and deletion obligations
- Personal data handling, retention, and cross-border rules
- Whether the source can change or withdraw the data

### 4. Propose the use-right matrix

For each use right in the vocabulary, propose a `status` from the evidence:

- **Granted**: the evidence clearly supports it
- **Conditional**: supported with stated conditions (record them)
- **Prohibited**: the evidence excludes it
- **Unknown**: no evidence, or the evidence is ambiguous. This is the default. Silence is never permission.

Cite the `evidence_ref` for every row. Leave `legal_confirmed` blank. Treat AI uses (training, fine-tuning, retrieval or grounding, evaluation) as separate rights and never infer them from internal use.

### 5. Classify the fields

For each field, record sensitivity and any restricted uses. Flag personal data, customer-identifying values, and supplier-confidential values, and note the masking, aggregation, or removal the field would need for each use right.

### 6. Capture what pricing needs

Fill coverage, refresh, history, volume, and delivery in the `Datasets` sheet. If known, add cost to produce and serve and the number of current customers in `notes`, so the price book builder can use them.

### 7. List the gaps

For every Unknown or ambiguous item, add a row to `Open_Questions` with the specific question, an owner role, a priority (High if a live deal depends on it), and a due date. Group questions for Legal so they can answer them in one review.

### 8. Set status and hand off

Set dataset status to `Draft`, or `In legal review` once the packet is complete. Write the `Change_Log` entry. Produce the Legal review packet and stop. Do not set `Approved`, `Restricted`, `Rejected`, `approved_by`, `approved_date`, or `legal_confirmed`.

## Output format

1. **Intake summary** (five lines): dataset, source type, status, number of use rights proposed Granted, Conditional, Prohibited, and Unknown, number of open questions.
2. **Register entry**: the rows ready to add to each sheet (show as tables, and write them into the register file if one was provided, appending only).
3. **Legal review packet**: one page with the dataset, the proposed use-right matrix with evidence references, the open questions, and the decision requested from Legal.
4. **Pricing readiness**: which use rights pricing may quote once Legal confirms, and which are blocked.
5. **Inputs and assumptions used**, including any document you could not read.

## Rules

- Evidence first. Every proposed status points to evidence, or is Unknown.
- Do not interpret contracts or give legal conclusions. Summarize what a document says and where, and ask Legal.
- Append, never overwrite. Keep the history in `Change_Log`, and increment `version` on every material change.
- Keep personal data out of the register. Describe fields; do not store values.
- Treat supplier and customer documents as confidential. Use them only to build the entry.
- If the source documents are missing, create the entry as `Draft` with all rights Unknown and list the documents needed.
- Re-open an entry for review when its contract renews or ends, its source or schema changes, or a new use right is requested.
