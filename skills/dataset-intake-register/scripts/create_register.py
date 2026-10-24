#!/usr/bin/env python3
"""Create an empty data rights register workbook.

Usage: python create_register.py OUTPUT.xlsx

Sheets: Datasets, Use_Rights, Fields, Evidence, Open_Questions, Change_Log, Vocabulary.
Use_Rights holds the rights WE hold on each dataset (what we may do with it). What a customer is
granted on a product is a different thing: it is recorded on the price book as conferred_right.
Dropdown validation is applied to controlled columns. Refuses to overwrite an existing file.
"""
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

VOCAB = {
    "source_type": ["Owned", "Supplier-sourced", "Customer-contributed", "Third-party licensed", "Public", "Derived"],
    "dataset_status": ["Draft", "In legal review", "Approved", "Restricted", "Rejected", "Retired"],
    "yes_no_unknown": ["Yes", "No", "Unknown"],
    "sensitivity": ["Public", "Commercial-confidential", "Supplier-confidential", "Personal"],
    "use_right": [
        "internal_use", "internal_analytics_shared_outputs", "display_to_third_parties",
        "redistribution_resale", "derivative_data_product", "ai_training",
        "ai_fine_tuning", "ai_retrieval_grounding", "ai_evaluation",
    ],
    "use_right_meaning_held": [
        "internal_use: we may use the data in our own operations",
        "internal_analytics_shared_outputs: we may share outputs we derive (reports, aggregates) outside our company, including with customers",
        "display_to_third_parties: we may show the data or substantial extracts to customers and partners",
        "redistribution_resale: we may pass on or resell the data itself",
        "derivative_data_product: we may build and sell a new data product from it",
        "ai_training: we may train or pre-train a model on it",
        "ai_fine_tuning: we may fine-tune a model on it",
        "ai_retrieval_grounding: we may supply it to a model or agent at query time",
        "ai_evaluation: we may benchmark or evaluate a model with it",
    ],
    "right_status": ["Granted", "Conditional", "Prohibited", "Unknown"],
    "yes_no": ["Yes", "No"],
    "document_type": ["Supplier agreement", "Customer agreement", "Terms of service", "Policy", "Email", "Other"],
    "owner_role": ["Legal", "Product", "Data engineering", "Finance", "Sales operations"],
    "priority": ["High", "Medium", "Low"],
    "question_status": ["Open", "Answered", "Closed"],
}

SHEETS = {
    "Datasets": [
        "dataset_id", "name", "description", "owner_role", "source_type", "source_name",
        "parent_dataset_ids", "coverage", "refresh_frequency", "history_depth", "delivery_methods",
        "volume_estimate", "contains_personal_data", "sensitivity", "status", "version",
        "last_reviewed", "next_review", "approved_by", "approved_date", "notes",
    ],
    "Use_Rights": [
        "dataset_id", "use_right", "status", "conditions", "geography", "term_end",
        "evidence_ref", "legal_confirmed", "confirmed_by", "confirmed_date",
    ],
    "Fields": [
        "dataset_id", "field_name", "description", "data_type", "sensitivity", "origin",
        "restricted_uses", "notes",
    ],
    "Evidence": [
        "evidence_id", "dataset_id", "document_name", "document_type", "location", "summary",
        "added_by", "added_date",
    ],
    "Open_Questions": [
        "question_id", "dataset_id", "question", "owner_role", "priority", "status",
        "due_date", "resolution",
    ],
    "Change_Log": ["date", "dataset_id", "change", "changed_by", "reason", "version"],
}

# sheet -> column -> vocabulary key
VALIDATIONS = {
    "Datasets": {
        "source_type": "source_type", "contains_personal_data": "yes_no_unknown",
        "sensitivity": "sensitivity", "status": "dataset_status", "owner_role": None,
    },
    "Use_Rights": {"use_right": "use_right", "status": "right_status", "legal_confirmed": "yes_no"},
    "Fields": {"sensitivity": "sensitivity"},
    "Evidence": {"document_type": "document_type"},
    "Open_Questions": {"owner_role": "owner_role", "priority": "priority", "status": "question_status"},
}

ROWS = 1000


def main(out_path: str) -> None:
    out = Path(out_path)
    if out.exists():
        sys.exit(f"Refusing to overwrite existing file: {out}")

    wb = Workbook()
    wb.remove(wb.active)

    vocab_ws = wb.create_sheet("Vocabulary")
    vocab_ref = {}
    for col, (key, values) in enumerate(VOCAB.items(), start=1):
        vocab_ws.cell(row=1, column=col, value=key).font = Font(bold=True)
        for r, v in enumerate(values, start=2):
            vocab_ws.cell(row=r, column=col, value=v)
        letter = get_column_letter(col)
        vocab_ref[key] = f"=Vocabulary!${letter}$2:${letter}${len(values) + 1}"
        vocab_ws.column_dimensions[letter].width = 34

    header_fill = PatternFill("solid", fgColor="E8EEF5")
    for name, headers in SHEETS.items():
        ws = wb.create_sheet(name, index=len(wb.sheetnames) - 1)
        for c, h in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=c, value=h)
            cell.font = Font(bold=True)
            cell.fill = header_fill
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            ws.column_dimensions[get_column_letter(c)].width = 24 if h not in ("description", "summary", "question", "conditions", "notes") else 48
        ws.freeze_panes = "B2"
        for col_name, vkey in VALIDATIONS.get(name, {}).items():
            if vkey is None:
                continue
            idx = headers.index(col_name) + 1
            letter = get_column_letter(idx)
            dv = DataValidation(type="list", formula1=vocab_ref[vkey], allow_blank=True)
            dv.add(f"{letter}2:{letter}{ROWS}")
            ws.add_data_validation(dv)

    wb.save(out)
    print(f"Created {out} with sheets: {', '.join(wb.sheetnames)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
