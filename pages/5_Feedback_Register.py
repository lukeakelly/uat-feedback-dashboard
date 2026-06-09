import streamlit as st

from services.database import (
    archive_approved_feedback,
    load_approved_feedback,
    update_approved_feedback,
)
from services.validation import (
    APPROVED_EDITABLE_FIELDS,
    FEATURE_AREAS,
    FEEDBACK_TYPES,
    HUMAN_DECISIONS,
    OWNERS,
    PRIORITIES,
    SEVERITIES,
    STATUSES,
    UAT_ROUNDS,
)
from services.ui import page_intro

page_intro(
    "Feedback register",
    "Maintain the approved UAT record, update delivery details and archive items "
    "that are no longer active without removing their history.",
    "Step 4 of 5",
)

approved = load_approved_feedback()
if approved.empty:
    st.info("No feedback has been approved yet.")
    st.stop()

filter_fields = [
    "uat_round",
    "feature_area",
    "type",
    "severity",
    "priority",
    "status",
    "owner",
    "human_decision",
]
filtered = approved.copy()

with st.expander("Filters", expanded=True):
    filter_columns = st.columns(4)
    for index, field in enumerate(filter_fields):
        values = sorted(value for value in approved[field].dropna().unique() if str(value))
        selected = filter_columns[index % 4].multiselect(
            field.replace("_", " ").title(),
            values,
            key=f"register_filter_{field}",
        )
        if selected:
            filtered = filtered[filtered[field].isin(selected)]

if filtered.empty:
    st.warning("No approved items match the selected filters.")
    st.stop()

editor_data = filtered.copy()
editor_data.insert(0, "Archive", False)
editable = ["Archive", *APPROVED_EDITABLE_FIELDS]
disabled = [column for column in editor_data.columns if column not in editable]

column_config = {
    "Archive": st.column_config.CheckboxColumn("Archive"),
    "uat_round": st.column_config.SelectboxColumn("UAT round", options=UAT_ROUNDS),
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
    height=560,
    num_rows="fixed",
    disabled=disabled,
    column_config=column_config,
    key="approved_editor",
)

left, right = st.columns(2)
with left:
    if st.button("Save register changes", type="primary"):
        update_approved_feedback(edited.to_dict("records"))
        st.success(f"Saved {len(edited)} approved item(s).")
        st.rerun()

with right:
    archive_ids = edited.loc[edited["Archive"], "id"].astype(int).tolist()
    if st.button("Archive selected", disabled=not archive_ids):
        update_approved_feedback(edited.to_dict("records"))
        count = archive_approved_feedback(archive_ids)
        st.success(f"Archived {count} item(s).")
        st.rerun()
