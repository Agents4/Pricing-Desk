import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data-rights-register" / "air-shopping-register-example.xlsx"
if OUT.exists():
    OUT.unlink()
subprocess.run(
    [sys.executable, str(ROOT / "skills" / "dataset-intake-register" / "scripts" / "create_register.py"), str(OUT)],
    check=True,
)
wb = load_workbook(OUT)

RIGHTS = [
    "internal_use", "internal_analytics_shared_outputs", "display_to_third_parties",
    "redistribution_resale", "derivative_data_product", "ai_training",
    "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
]
OWNER = "Data owner, Air Distribution"
TODAY = "2026-10-17"

# ---------------------------------------------------------------- Datasets
datasets = [
    dict(
        dataset_id="DS-CUS-001", name="Agency air shopping requests",
        description="Search requests sent by agency customers through the shopping API: origin, destination, dates, passengers, cabin, filters, point of sale, and agency identifier.",
        source_type="Customer-contributed", source_name="Agency API customers", parent_dataset_ids="",
        coverage="All agency channel requests, all points of sale (example)", refresh_frequency="Real time",
        history_depth="To be confirmed", delivery_methods="Log extract", volume_estimate="To be measured",
        contains_personal_data="Unknown", sensitivity="Commercial-confidential",
    ),
    dict(
        dataset_id="DS-SUP-001", name="Supplier published fare responses",
        description="Airline published fares returned in shopping responses: flights, fare basis, booking class, base fare, taxes and fees, total price, currency, and basic rules references.",
        source_type="Supplier-sourced", source_name="Airline suppliers (published fares)", parent_dataset_ids="",
        coverage="All carriers returned in responses (example)", refresh_frequency="Real time",
        history_depth="To be confirmed", delivery_methods="Log extract", volume_estimate="To be measured",
        contains_personal_data="No", sensitivity="Commercial-confidential",
        notes="Terms may differ by airline. Evidence recorded so far is one sample agreement; a per-airline matrix is needed (see Q-0001).",
    ),
    dict(
        dataset_id="DS-SUP-002", name="Supplier private and negotiated fare responses",
        description="Private, negotiated, and agency-specific fares and offers returned in shopping responses, including account or deal codes and discount levels.",
        source_type="Supplier-sourced", source_name="Airline suppliers (private fares)", parent_dataset_ids="",
        coverage="Fares returned to authorized agencies only (example)", refresh_frequency="Real time",
        history_depth="To be confirmed", delivery_methods="Log extract", volume_estimate="To be measured",
        contains_personal_data="No", sensitivity="Supplier-confidential",
    ),
    dict(
        dataset_id="DS-DER-001", name="Air shopping transaction log",
        description="Request and response pairs joined into one record per shopping transaction: what the agency asked for and which supplier fares and rates came back.",
        source_type="Derived", source_name="Internal join of request and response logs",
        parent_dataset_ids="DS-CUS-001;DS-SUP-001;DS-SUP-002",
        coverage="All joined shopping transactions (example)", refresh_frequency="Daily",
        history_depth="To be confirmed", delivery_methods="Internal warehouse only", volume_estimate="To be measured",
        contains_personal_data="Unknown", sensitivity="Supplier-confidential",
        notes="A derived dataset can never have more rights than its most restrictive parent.",
    ),
    dict(
        dataset_id="DS-DER-002", name="Air shopping market insights",
        description="Aggregated and anonymized market views built from the transaction log: fare distributions, search demand, and advance-purchase patterns by market, month, and cabin.",
        source_type="Derived", source_name="Aggregation of DS-DER-001", parent_dataset_ids="DS-DER-001",
        coverage="Market-level (origin and destination, month, cabin) (example)", refresh_frequency="Daily aggregate",
        history_depth="To be confirmed", delivery_methods="API; file", volume_estimate="To be measured",
        contains_personal_data="No", sensitivity="Commercial-confidential",
        notes="This is the dataset pricing would license. It is blocked until the rights above it are confirmed.",
    ),
]
ws = wb["Datasets"]
hdr = [c.value for c in ws[1]]
for d in datasets:
    d.setdefault("owner_role", OWNER)
    d.update(status="In legal review", version=1, last_reviewed=TODAY)
    d.setdefault("notes", "")
    d["notes"] = ("Illustrative example. " + d["notes"]).strip()
    ws.append([d.get(h, "") for h in hdr])

# ---------------------------------------------------------------- Evidence (all illustrative)
evidence = [
    ("EV-0001", "DS-SUP-001", "Sample Airline Content Agreement (illustrative)", "Supplier agreement", "Section 4.2",
     "Company may display and distribute the airline's published fares to authorized subscribers to search and book. Other uses need the airline's written consent."),
    ("EV-0002", "DS-SUP-001", "Sample Airline Content Agreement (illustrative)", "Supplier agreement", "Section 7.1",
     "Transaction and shopping data may be used in aggregated, non-identifiable form for market analytics and product development. Airline-identifiable data may not be shared with other airlines."),
    ("EV-0003", "DS-CUS-001", "Sample Agency Distribution Agreement (illustrative)", "Customer agreement", "Section 9.3",
     "Agency search and booking data is the agency's confidential information. Company may use it in aggregated and anonymized form to improve services and develop products, and may not disclose agency-identifiable data to third parties."),
    ("EV-0004", "DS-CUS-001", "Sample Agency Distribution Agreement (illustrative)", "Customer agreement", "Section 9.5",
     "Traveler personal data is processed on the agency's behalf and only to provide the services."),
    ("EV-0005", "DS-SUP-002", "Sample Private Fare Addendum (illustrative)", "Supplier agreement", "Section 2",
     "Private and negotiated fares are confidential to the airline and the authorized agency, and may be displayed only to that agency."),
    ("EV-0006", "DS-SUP-001", "Sample Developer API Terms of Use (illustrative)", "Terms of service", "Section 3.4",
     "API customers may not store responses beyond the booking session or use them to build a competing shopping service."),
    ("EV-0007", "DS-CUS-001", "Sample Internal Data Governance Policy (illustrative)", "Policy", "Section 2.1",
     "Use of customer or supplier data for AI model training or retrieval requires documented approval from Legal and the data owner."),
]
ws = wb["Evidence"]
for ev in evidence:
    ws.append(list(ev) + ["Register steward", TODAY])

# ---------------------------------------------------------------- Use rights (proposed; legal_confirmed left blank)
AI_UNK = ("Unknown", "No evidence in the agreements. Internal policy requires Legal and owner approval.", "EV-0007")


def ai_rows():
    return {r: AI_UNK for r in RIGHTS if r.startswith("ai_")}


matrix = {
    "DS-CUS-001": {
        "internal_use": ("Conditional", "To provide and improve services. Agency-identifiable data stays internal.", "EV-0003"),
        "internal_analytics_shared_outputs": ("Conditional", "Shared outputs must be aggregated and anonymized, with no agency identifiers.", "EV-0003"),
        "display_to_third_parties": ("Prohibited", "Agency-identifiable data may not be disclosed.", "EV-0003"),
        "redistribution_resale": ("Prohibited", "Agency-identifiable data may not be disclosed.", "EV-0003"),
        "derivative_data_product": ("Conditional", "Only from aggregated and anonymized data. Threshold to be defined (Q-0004).", "EV-0003"),
        **ai_rows(),
    },
    "DS-SUP-001": {
        "internal_use": ("Conditional", "To provide search and booking services to subscribers.", "EV-0001"),
        "internal_analytics_shared_outputs": ("Unknown", "Booking is the stated purpose. No written airline consent for analytics found yet (Q-0001).", "EV-0001"),
        "display_to_third_parties": ("Conditional", "Display to authorized subscribers for search and booking only.", "EV-0001"),
        "redistribution_resale": ("Prohibited", "Not permitted beyond authorized subscribers without airline consent. API terms limit storage and reuse by customers.", "EV-0001;EV-0006"),
        "derivative_data_product": ("Conditional", "Aggregated, non-identifiable market analytics only. No airline-identifiable data shared with other airlines.", "EV-0002"),
        **ai_rows(),
    },
    "DS-SUP-002": {
        "internal_use": ("Conditional", "Only for display to the authorized agency.", "EV-0005"),
        "internal_analytics_shared_outputs": ("Unknown", "Unclear whether aggregated outputs are covered (Q-0002).", "EV-0002;EV-0005"),
        "display_to_third_parties": ("Prohibited", "May be shown only to the authorized agency.", "EV-0005"),
        "redistribution_resale": ("Prohibited", "Confidential to the airline and the authorized agency.", "EV-0005"),
        "derivative_data_product": ("Unknown", "Aggregation clause may not cover private fares (Q-0002).", "EV-0002;EV-0005"),
        **ai_rows(),
    },
    "DS-DER-001": {
        "internal_use": ("Conditional", "Inherits the strictest parent conditions.", "EV-0001;EV-0003;EV-0005"),
        "internal_analytics_shared_outputs": ("Unknown", "Depends on Q-0001 and Q-0002.", "EV-0002;EV-0003"),
        "display_to_third_parties": ("Prohibited", "Parents prohibit disclosure of identifiable agency or private fare data.", "EV-0003;EV-0005"),
        "redistribution_resale": ("Prohibited", "Parents prohibit it.", "EV-0003;EV-0005"),
        "derivative_data_product": ("Conditional", "Only through the aggregated and anonymized dataset DS-DER-002.", "EV-0002;EV-0003"),
        **ai_rows(),
    },
    "DS-DER-002": {
        "internal_use": ("Conditional", "We may use it in our own products and services if aggregation and anonymization standards are met (Q-0004).", "EV-0002;EV-0003"),
        "internal_analytics_shared_outputs": ("Conditional", "We may supply outputs to customers only if they stay market-level; no airline or agency identifiable.", "EV-0002;EV-0003"),
        "display_to_third_parties": ("Unknown", "Depends on whether carrier-level benchmarks identify an airline (Q-0006).", "EV-0002"),
        "redistribution_resale": ("Unknown", "Agreements are silent on onward redistribution of aggregated output (Q-0005).", "EV-0003"),
        "derivative_data_product": ("Conditional", "Permitted for aggregated, non-identifiable use.", "EV-0002;EV-0003"),
        **ai_rows(),
    },
}
ws = wb["Use_Rights"]
hdr = [c.value for c in ws[1]]
for ds, rows in matrix.items():
    for right in RIGHTS:
        status, cond, ev = rows[right]
        rec = dict(dataset_id=ds, use_right=right, status=status, conditions=cond, evidence_ref=ev)
        ws.append([rec.get(h, "") for h in hdr])

# ---------------------------------------------------------------- Fields
F = []


def f(ds, name, desc, dtype, sens, origin, restricted="", notes=""):
    F.append((ds, name, desc, dtype, sens, origin, restricted, notes))


req = "Agency request"
f("DS-CUS-001", "request_id", "Unique ID of the search request", "string", "Commercial-confidential", req)
f("DS-CUS-001", "agency_id", "Identifier of the requesting agency", "string", "Commercial-confidential", req,
  "display_to_third_parties;redistribution_resale", "Remove or hash before any aggregated output.")
f("DS-CUS-001", "point_of_sale", "Country or market the request was sold from", "string", "Commercial-confidential", req)
f("DS-CUS-001", "origin", "Origin airport or city", "string", "Public", req)
f("DS-CUS-001", "destination", "Destination airport or city", "string", "Public", req)
f("DS-CUS-001", "departure_date", "Requested outbound date", "date", "Public", req)
f("DS-CUS-001", "return_date", "Requested return date", "date", "Public", req)
f("DS-CUS-001", "passenger_counts", "Passengers by type", "JSON", "Public", req)
f("DS-CUS-001", "cabin", "Requested cabin", "string", "Public", req)
f("DS-CUS-001", "request_timestamp", "Time the request was received", "date", "Commercial-confidential", req)
f("DS-CUS-001", "traveler_profile_token", "Token or corporate ID tied to a traveler or account, if sent", "string", "Personal", req,
  "all outputs until cleared", "Confirm presence (Q-0003). Exclude from any shared output.")
f("DS-CUS-001", "client_ip", "Network address of the caller, if logged", "string", "Personal", "System log",
  "all outputs until cleared", "Confirm presence (Q-0003). Drop before analytics.")

resp = "Supplier response"
for ds, sens, extra in (("DS-SUP-001", "Commercial-confidential", False), ("DS-SUP-002", "Supplier-confidential", True)):
    f(ds, "response_id", "Unique ID of the response, linked to request_id", "string", "Commercial-confidential", resp)
    f(ds, "carrier", "Marketing airline", "string", sens, resp, "", "Airline identifying; see Q-0006." if not extra else "Airline identifying.")
    f(ds, "flight_numbers", "Flight numbers and itinerary segments", "string", "Public", resp)
    f(ds, "fare_basis", "Fare basis code", "string", sens, resp)
    f(ds, "booking_class", "Booking class", "string", "Public", resp)
    f(ds, "base_fare", "Base fare amount", "number", sens, resp)
    f(ds, "taxes_fees", "Taxes and fees", "number", "Public", resp)
    f(ds, "total_fare", "Total price returned", "number", sens, resp)
    f(ds, "currency", "Currency of the amounts", "string", "Public", resp)
    f(ds, "fare_rules_ref", "Reference to fare conditions", "string", sens, resp)
    if extra:
        f(ds, "negotiated_account_code", "Account or deal code that unlocked the fare", "string", "Supplier-confidential", resp,
          "all outputs", "Never include in any shared output.")
        f(ds, "discount_level", "Discount or markdown against a published fare", "number", "Supplier-confidential", resp,
          "all outputs", "Never include in any shared output.")

f("DS-DER-001", "request_id", "Join key to the request", "string", "Commercial-confidential", "Join")
f("DS-DER-001", "response_id", "Join key to the response", "string", "Commercial-confidential", "Join")
f("DS-DER-001", "all parent fields", "All fields of DS-CUS-001, DS-SUP-001, and DS-SUP-002", "other", "Supplier-confidential", "Join",
  "display_to_third_parties;redistribution_resale", "Field list is the union of the parents. Keep internal.")

agg = "Aggregation"
f("DS-DER-002", "origin_destination_market", "Market defined by origin and destination", "string", "Public", agg)
f("DS-DER-002", "travel_month", "Month of travel", "date", "Public", agg)
f("DS-DER-002", "cabin", "Cabin", "string", "Public", agg)
f("DS-DER-002", "advance_purchase_bucket", "Days between search and travel, in buckets", "string", "Public", agg)
f("DS-DER-002", "fare_percentiles", "Distribution of total fares across all carriers", "number", "Commercial-confidential", agg, "",
  "Market-level only. Needs a minimum aggregation threshold (Q-0004).")
f("DS-DER-002", "search_volume_index", "Relative search demand", "number", "Commercial-confidential", agg, "",
  "Index, not counts. No agency identifiable.")
f("DS-DER-002", "carrier_level_fare_benchmark", "Fare benchmark for a single airline", "number", "Supplier-confidential", agg,
  "display_to_third_parties", "Hold back until Q-0006 is answered.")
ws = wb["Fields"]
for row in F:
    ws.append(list(row))

# ---------------------------------------------------------------- Open questions
Q = [
    ("Q-0001", "DS-SUP-001", "Is written airline consent on file for market analytics and other uses beyond booking? Do terms differ by airline? If so, build a per-airline rights matrix.", "Legal", "High", "2026-10-31"),
    ("Q-0002", "DS-SUP-002", "Does the aggregated analytics clause apply to private and negotiated fares, or do the private fare restrictions take precedence?", "Legal", "High", "2026-10-31"),
    ("Q-0003", "DS-CUS-001", "Do requests contain personal data such as traveler profile tokens, loyalty numbers, or client network addresses? Confirm field by field.", "Data engineering", "High", "2026-10-31"),
    ("Q-0004", "DS-CUS-001", "What aggregation threshold and anonymization standard satisfy 'aggregated and anonymized' in the agency agreement?", "Legal", "High", "2026-10-31"),
    ("Q-0005", "DS-DER-002", "May we let customers redistribute the insights or embed them in their own products, and under what conditions?", "Legal", "Medium", "2026-11-14"),
    ("Q-0006", "DS-DER-002", "Can carrier-level fare benchmarks be shown, or must output stay at market level so that no airline can be identified?", "Product", "Medium", "2026-11-14"),
    ("Q-0007", "DS-DER-001", "Which AI uses (retrieval, evaluation, fine-tuning, training) can be approved under the governance policy, and by whom?", "Legal", "High", "2026-10-31"),
    ("Q-0008", "DS-DER-002", "Confirm the cost to produce and serve this dataset so pricing can set a floor.", "Finance", "Low", "2026-11-14"),
]
ws = wb["Open_Questions"]
for q in Q:
    ws.append([q[0], q[1], q[2], q[3], q[4], "Open", q[5], ""])

# ---------------------------------------------------------------- Change log
ws = wb["Change_Log"]
for d in datasets:
    ws.append([TODAY, d["dataset_id"], "Entry created from initial intake (illustrative example)", "Register steward", "Initial intake", 1])

# ---------------------------------------------------------------- Matrix view
mv = wb.create_sheet("Rights_Matrix_View", 0)
mv.append(["Dataset", "Name"] + RIGHTS)
for c in mv[1]:
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="E8EEF5")
    c.alignment = Alignment(wrap_text=True, vertical="top")
fills = {"Granted": "C6E5C9", "Conditional": "FBE7B0", "Prohibited": "F2B8B5", "Unknown": "E3E3E3"}
for d in datasets:
    mv.append([d["dataset_id"], d["name"]] + [matrix[d["dataset_id"]][r][0] for r in RIGHTS])
for row in mv.iter_rows(min_row=2, min_col=3):
    for cell in row:
        cell.fill = PatternFill("solid", fgColor=fills[cell.value])
mv.append([])
mv.append(["Legend: Granted, Conditional, Prohibited, Unknown are proposed from evidence. None is confirmed by Legal, so pricing treats every cell as Unknown until legal_confirmed = Yes on the Use_Rights sheet."])
mv.append(["This sheet is a generated view. Regenerate it from the Use_Rights sheet; do not edit it by hand."])
mv.column_dimensions["A"].width = 14
mv.column_dimensions["B"].width = 40
for col in "CDEFGHIJK":
    mv.column_dimensions[col].width = 20
mv.row_dimensions[1].height = 48
mv.freeze_panes = "C2"

# ---------------------------------------------------------------- Read me
rd = wb.create_sheet("README_EXAMPLE", 0)
lines = [
    "EXAMPLE ONLY: illustrative air shopping data rights register",
    "",
    "All agreements, clause numbers, and terms below are invented to show how the register works. They are not real contracts and not legal conclusions.",
    "",
    "What the example shows:",
    "1. Air shopping is five datasets, not one: agency requests, supplier published fares, supplier private fares, the joined transaction log, and the aggregated market insights.",
    "2. Rights differ by component. Requests belong to the agency, fares to the airlines, and private fares are the most restricted.",
    "3. A derived dataset inherits the strictest rights of its parents. The aggregated insights (DS-DER-002) are the product we sell, and they depend on questions still open above them.",
    "4. Every proposed status points to evidence. Where evidence is silent, the status is Unknown. AI uses are separate rights and are Unknown everywhere.",
    "5. legal_confirmed is blank on every row. Only Legal sets it. Until then pricing can price products that rely on these rows only as Provisional, and cannot release them for quoting.",
    "6. Shared evidence is recorded once, under the first dataset it applies to, and referenced by evidence ID from other rows.",
    "7. Every row here is a right WE HOLD on the dataset: what we may do with it. What a customer is granted on a product is set separately in the price book (conferred_right) and is checked against these rows through the coverage table in the price-book-builder skill.",
    "",
    "Sheets: Rights_Matrix_View, Datasets, Use_Rights, Fields, Evidence, Open_Questions, Change_Log, Vocabulary.",
]
for i, line in enumerate(lines, start=1):
    rd.cell(row=i, column=1, value=line).alignment = Alignment(wrap_text=True, vertical="top")
rd["A1"].font = Font(bold=True, size=13)
rd.column_dimensions["A"].width = 120

wb.active = 0
wb.save(OUT)
print("saved", OUT)
