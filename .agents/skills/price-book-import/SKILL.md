---
name: price-book-import
description: Bring an existing price book (spreadsheet, CSV export, quote tool dump) into the standard price book format. Classifies each line as data, API, software, service or other, finds the lines that do not say what the customer may do with the data or API responses, checks consistency, and writes a hand-off list for the product manager's rights check. Use when the desk already prices established products and needs to start from that price book.
compatibility: "Any Agent Skills client. Scripts need Python 3.8+; without a shell the skill works from pasted data and says the check was not run."
metadata:
  version: "1.1.0"
  layer: pricing
  last_reviewed: "2026-10-24"
  includes: "shared/operating-rules.md, shared/capabilities.md, shared/output-conventions.md"
---

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
