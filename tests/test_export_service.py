from io import BytesIO

import pandas as pd

from services.export_service import build_excel_export, dataframe_to_csv_bytes


def test_csv_and_excel_exports_are_created():
    approved = pd.DataFrame(
        [
            {
                "feedback_id": "UAT-0001",
                "status": "New",
                "priority": "Should fix",
                "severity": "Medium",
                "human_decision": "Accepted",
            }
        ]
    )
    rejected = pd.DataFrame([{"raw_feedback": "Duplicate item"}])

    csv_bytes = dataframe_to_csv_bytes(approved)
    excel_bytes = build_excel_export(approved, rejected)

    assert b"UAT-0001" in csv_bytes
    workbook = pd.ExcelFile(BytesIO(excel_bytes))
    assert workbook.sheet_names == [
        "Approved Feedback",
        "Rejected Feedback",
        "Summary",
    ]
