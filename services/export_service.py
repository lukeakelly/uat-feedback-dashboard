from __future__ import annotations

from io import BytesIO

import pandas as pd

from services.validation import MUST_FIX_PRIORITIES, OPEN_STATUSES, RESOLVED_STATUSES


def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def build_summary(approved: pd.DataFrame) -> pd.DataFrame:
    if approved.empty:
        values = {
            "Total approved items": 0,
            "Open items": 0,
            "Must-fix items": 0,
            "High severity items": 0,
            "Items awaiting decision": 0,
            "Resolved items": 0,
        }
    else:
        values = {
            "Total approved items": len(approved),
            "Open items": int(approved["status"].isin(OPEN_STATUSES).sum()),
            "Must-fix items": int(approved["priority"].isin(MUST_FIX_PRIORITIES).sum()),
            "High severity items": int(approved["severity"].isin(["Blocker", "High"]).sum()),
            "Items awaiting decision": int(
                approved["human_decision"].isin(["Pending", "Needs clarification"]).sum()
            ),
            "Resolved items": int(approved["status"].isin(RESOLVED_STATUSES).sum()),
        }
    return pd.DataFrame({"Metric": values.keys(), "Value": values.values()})


def build_excel_export(approved: pd.DataFrame, rejected: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        approved.to_excel(writer, sheet_name="Approved Feedback", index=False)
        rejected.to_excel(writer, sheet_name="Rejected Feedback", index=False)
        build_summary(approved).to_excel(writer, sheet_name="Summary", index=False)
    output.seek(0)
    return output.getvalue()
