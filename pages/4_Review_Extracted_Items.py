import pandas as pd
import streamlit as st

from services.database import (
    approve_pending_feedback,
    load_pending_feedback,
    reject_pending_feedback,
    update_pending_feedback,
)
from services.validation import (
    FEATURE_AREAS,
    FEEDBACK_TYPES,
    HUMAN_DECISIONS,
    OWNERS,
    PENDING_FIELDS,
    PRIORITIES,
    SEVERITIES,
    STATUSES,
    validate_feedback_item,
)

st.title("Review Extracted Items")
st.write("Edit the extracted rows, select the rows you have reviewed, then approve or reject them.")
st.warning("Pending rows do not appear in the dashboard or approved register.")

pending = load_pending_feedback()
if pending.empty:
    st.info("There are no pending feedback items to review.")
    st.stop()

editor_data = pending.copy()
editor_data.insert(0, "Select", False)

editable_columns = ["Select", *PENDING_FIELDS]
disabled_columns = [column for column in editor_data.columns if column not in editable_columns]

column_config = {
    "Select": st.column_config.CheckboxColumn("Select", help="Select for approval or rejection"),
    "feature_area": st.column_config.SelectboxColumn("Feature area", options=FEATURE_AREAS),
    "type": st.column_config.SelectboxColumn("Type", options=FEEDBACK_TYPES),
    "severity": st.column_config.SelectboxColumn("Severity", options=SEVERITIES),
    "priority": st.column_config.SelectboxColumn("Priority", options=PRIORITIES),
    "status": st.column_config.SelectboxColumn("Status", options=STATUSES),
    "owner": st.column_config.SelectboxColumn("Owner", options=OWNERS),
    "human_decision": st.column_config.SelectboxColumn(
        "Human decision", options=HUMAN_DECISIONS
    ),
}

edited = st.data_editor(
    editor_data,
    hide_index=True,
    use_container_width=True,
    height=520,
    num_rows="fixed",
    disabled=disabled_columns,
    column_config=column_config,
    key="pending_editor",
)


def save_editor_rows(dataframe: pd.DataFrame) -> list[dict]:
    records = []
    for row in dataframe.to_dict("records"):
        validated = validate_feedback_item(row)
        validated["id"] = int(row["id"])
        records.append(validated)
    update_pending_feedback(records)
    return records


selected_ids = edited.loc[edited["Select"], "id"].astype(int).tolist()
button_columns = st.columns([1, 1, 2])

with button_columns[0]:
    if st.button("Save edits"):
        try:
            save_editor_rows(edited)
            st.success("Pending feedback edits saved.")
        except ValueError as exc:
            st.error(str(exc))

with button_columns[1]:
    if st.button("Approve selected", type="primary", disabled=not selected_ids):
        try:
            save_editor_rows(edited)
            feedback_ids = approve_pending_feedback(selected_ids)
            st.success(f"Approved {len(feedback_ids)} item(s): {', '.join(feedback_ids)}")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

with button_columns[2]:
    rejection_reason = st.text_input(
        "Rejection reason",
        value="Rejected during human review",
        label_visibility="collapsed",
        placeholder="Rejection reason",
    )
    if st.button("Reject selected", disabled=not selected_ids):
        try:
            save_editor_rows(edited)
            count = reject_pending_feedback(selected_ids, rejection_reason.strip())
            st.success(f"Rejected {count} item(s).")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
