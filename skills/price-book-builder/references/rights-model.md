# Held rights and conferred rights

Two different things share one vocabulary. Keep them apart.

| | Held rights | Conferred rights |
|---|---|---|
| Question | What may **we** do with this dataset? | What do we **grant the customer** on the product they buy? |
| Where it lives | The data rights register (`Use_Rights` sheet, `use_right` column) | The price book (`conferred_right` column) |
| About | A dataset, and the agreements behind it: our marketplace suppliers, contributing customers and licensors | A product line: the derivative product, API, feed or file we sell |
| Set by | Evidence from agreements; **only Legal** confirms (`legal_confirmed`) | Pricing and Product propose; the Pricing Council approves the price book |
| Changes when | A contract changes, a party opts out, a new source joins | We change what a product lets the customer do |

We can only confer what we hold. The price book never says what we may do; the register never says what a customer may do.

## The nine rights, in both directions

| Right | Held (register): we may | Conferred (price book): the customer may |
|---|---|---|
| internal_use | use the data in our own operations | use the product inside its own business |
| internal_analytics_shared_outputs | share outputs we derive (reports, aggregates, benchmarks) outside our company | share outputs it derives from the product with others |
| display_to_third_parties | show the data or substantial extracts to customers and partners | show the product or extracts to its own customers and partners |
| redistribution_resale | pass on or resell the data itself | pass on or resell the product |
| derivative_data_product | build and sell a new data product from it | build its own data product from ours |
| ai_training | train or pre-train a model | train or pre-train a model on the product |
| ai_fine_tuning | fine-tune a model | fine-tune a model on the product |
| ai_retrieval_grounding | supply it to a model or agent at query time | supply the product to a model or agent at query time |
| ai_evaluation | benchmark or evaluate a model | benchmark or evaluate a model with the product |

Each AI use is its own right in both directions.

## How a price book line is checked

Each data line says three things: the dataset or datasets the product is built from or delivers (`dataset_id`, several separated by `;`), the right it **confers** (`conferred_right`), and the form of the product (`data_form`).

- `derived` (default): the product is an aggregate, benchmark, insight or other derivative of the dataset. The dataset is usually a Derived register entry, and the register already limits it to what its parents allow.
- `passthrough`: the customer receives the underlying data itself, as a file, feed or extract.

`rights-coverage.csv` maps the conferred right and the form to the held rights the dataset must carry. Every listed held right is needed. The defaults are a working assumption for Legal and the Pricing Council to confirm or change; edit the CSV and the checker follows. Two further rules:

- A `derived` product built directly on a source dataset (Supplier-sourced, Customer-contributed, Owned, and so on) also needs `derivative_data_product` on that dataset. A product built on a Derived register entry does not, because that entry exists only after the derivation was allowed.
- A line with no dataset, or no conferred right, is Provisional: there is nothing to check yet.

For each (dataset, held right) pair the register gives a status. The line takes the **worst** pair:

| Basis | Meaning |
|---|---|
| N/A | The line carries no data or third-party content |
| Confirmed | Every needed held right is Granted or Conditional and Legal has confirmed it |
| Provisional | Anything else: no register, dataset or row missing, Unknown, or not yet confirmed |
| Contradicted | A needed held right is Prohibited in the register but Legal has not confirmed it |
| Blocked | Legal confirmed a needed held right as Prohibited. We cannot confer this right |

Worked example. Air Shopping Market Insights is built on DS-DER-002. A line confers `display_to_third_parties` on it. The default map requires `internal_analytics_shared_outputs` and `display_to_third_parties` held on DS-DER-002. The register has the first as Conditional and the second as Unknown, neither confirmed. The line is Provisional, and the exposure report asks the intake team to settle `display_to_third_parties` on DS-DER-002 first.

## Conditions travel downstream

A Conditional held right passes its conditions to the product: the product design must meet them (for example "outputs stay market-level") and the customer terms must carry them. The checker warns on every Conditional pair.
