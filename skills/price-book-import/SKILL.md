---
name: price-book-import
description: Bring an existing price book (spreadsheet, CSV export, quote tool dump) into the standard price book format when its products are not yet in the data rights register. Classifies each line as data, API, software, service or other, finds the lines that need a rights check, and ranks the datasets to take through intake first. Use when the desk already prices established products and needs to start from that price book.
---

# Price Book Import

Start from the price book the business already uses. Do not wait for the register or for Legal. Import first, check consistency, then use the revenue at stake to decide which rights questions to work first.

Not every line is a data licence. The pricing desk prices API access, software, services and data. Only the lines that carry data or third-party content need the rights register. The rest are imported and checked like any other price.

## What this skill needs

1. **The existing price book**: .xlsx or .csv. Any layout. Say which sheet if there are several.
2. Optional but valuable: **annual revenue and customer counts per product** (even rough). They turn the intake list into a ranked list.
3. Optional: which product is which type, if the words in the file are not clear.

If the file cannot be read, or has no price column, say so and stop. Do not invent prices.

## Process

### 1. Run the importer

`python scripts/import_price_book.py --in FILE --out-dir OUT [--sheet NAME] [--map map.json] [--default-currency USD] [--version legacy-YYYY-MM] [--tier-model all_units|graduated]`

It finds the header row, maps columns by common names (and by `--map` when the names are unusual), reads prices written as "$1,200", bands written as "0 - 1M" or "10M+", and terms written as "12 mo" or "one-time". It writes `price_book.csv`, `import_report.md`, `dataset_candidates.csv` and `register_backfill.csv`.

If you cannot run code, do the same steps by hand with a table and label the result as unchecked. Read `references/standard-price-book.md` for the columns.

### 2. Review the report with the person

Show the import report headline and these items, and ask them to correct what is wrong:

- **Column mapping**: right columns for list price, floor, unit, bands, term?
- **Product types** inferred with less than high confidence. Fix with `--map` ("types") and re-run.
- **Tier model**: `all_units` is assumed. If the tiers actually bill graduated, re-run with `--tier-model graduated`, because the volume-cliff check depends on it.
- **Missing floors**: not invented. They come from the `data-price-setting` skill (cost floor) or Finance.
- **Use rights**: legacy price books rarely say which use right a price covers. The importer infers a right only from clear words (resale, redistribution) and flags it. Everything else is "not stated".

### 3. Check consistency, with no register

`python ../price-book-builder/scripts/check_price_book.py --pricebook OUT/price_book.csv --exposure-csv OUT/exposure.csv`

Strategy mode is the default: lines that carry data are labelled Provisional, not errors. The checker still finds real pricing problems: tiers that overlap or leave gaps, unit price rising with volume, volume cliffs, floor above list, and duplicates. Report these as findings about the existing book, not as mistakes of the import.

### 4. Rank the rights work

Use `dataset_candidates.csv` and `exposure.csv`. They rank by annual revenue (or line count if no revenue is given) weighted by how risky the use right is. Present the top items and what is at stake, and propose the order to take them through the `dataset-intake-register` skill. The ranking is a proposal; ask the person to adjust it for live deals and renewals.

### 5. Start the register

`register_backfill.csv` has one row per candidate dataset and use right, all Unknown, with no `legal_confirmed`. Candidate ids (DS-CAND-...) are placeholders: replace them with real register ids as each dataset goes through intake. Leave Legal's columns blank.

### 6. Decide on API lines

API products are marked rights relevance Possible. Ask: do responses carry supplier or third-party content (for example fares from airlines)? If yes, name the dataset behind it and add it to the candidates. If no, record that decision.

## Output format

1. **Headline**: lines imported, products by type, lines that need a rights check, revenue at stake in Provisional lines, the top three intake priorities.
2. **Consistency findings** on the existing price book.
3. **Intake priority table** (rank, dataset, use rights stated, revenue, why it ranks there).
4. **Decisions needed** from the person (types, tier model, floors, API content question).
5. **Files written** and **Inputs and assumptions used**.

## Rules

- Never invent a price, floor, term, revenue figure or use right. Blank stays blank and is reported.
- Imported lines have status Existing. Nothing is Approved. Only the Pricing Council sets Approved.
- Do not set `legal_confirmed` or any Legal column. Rights stay Unknown until Legal confirms.
- Provisional pricing is allowed and useful. It is not clearance to quote: a quote needs confirmed rights, which the release check enforces.
- Customer-specific revenue stays in the working files and is not copied into general summaries.
