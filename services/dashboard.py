from __future__ import annotations

import pandas as pd

from services.validation import MUST_FIX_PRIORITIES, OPEN_STATUSES, RESOLVED_STATUSES


def dashboard_metrics(dataframe: pd.DataFrame) -> dict[str, int]:
    if dataframe.empty:
        return {
            "total": 0,
            "open": 0,
            "must_fix": 0,
            "high_severity": 0,
            "awaiting_decision": 0,
            "resolved": 0,
        }
    return {
        "total": len(dataframe),
        "open": int(dataframe["status"].isin(OPEN_STATUSES).sum()),
        "must_fix": int(dataframe["priority"].isin(MUST_FIX_PRIORITIES).sum()),
        "high_severity": int(dataframe["severity"].isin(["Blocker", "High"]).sum()),
        "awaiting_decision": int(
            dataframe["human_decision"].isin(["Pending", "Needs clarification"]).sum()
        ),
        "resolved": int(dataframe["status"].isin(RESOLVED_STATUSES).sum()),
    }


def count_by(dataframe: pd.DataFrame, column: str) -> pd.DataFrame:
    if dataframe.empty or column not in dataframe:
        return pd.DataFrame(columns=[column, "count"])
    values = dataframe[column].fillna("Not set").replace("", "Not set")
    return values.value_counts().rename_axis(column).reset_index(name="count")
