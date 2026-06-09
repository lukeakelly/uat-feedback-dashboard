from datetime import date

import streamlit as st

from services.access_control import is_admin
from services.database import load_approved_feedback, load_rejected_feedback
from services.export_service import build_excel_export, dataframe_to_csv_bytes
from services.ui import page_intro

page_intro(
    "Export feedback",
    "Download the approved register and rejected-item audit for reporting, "
    "handover or further analysis.",
    "Step 5 of 5",
)

approved = load_approved_feedback()
rejected = load_rejected_feedback()
today = date.today().isoformat()

left, middle, right = st.columns(3)
left.metric("Approved rows", len(approved))
middle.metric("Rejected rows", len(rejected))
right.metric("Export date", today)

st.download_button(
    "Download approved register (CSV)",
    data=dataframe_to_csv_bytes(approved),
    file_name=f"approved_uat_feedback_{today}.csv",
    mime="text/csv",
    disabled=approved.empty,
)

if is_admin():
    st.download_button(
        "Download rejected feedback audit (CSV)",
        data=dataframe_to_csv_bytes(rejected),
        file_name=f"rejected_uat_feedback_{today}.csv",
        mime="text/csv",
        disabled=rejected.empty,
    )

    excel_bytes = build_excel_export(approved, rejected)
    st.download_button(
        "Download complete workbook (Excel)",
        data=excel_bytes,
        file_name=f"uat_feedback_export_{today}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info(
        "Read-only viewers can download the approved register. "
        "Rejected-item audit exports are available to the owner only."
    )

with st.expander("Approved export preview"):
    if approved.empty:
        st.caption("No approved feedback is available.")
    else:
        st.dataframe(approved, hide_index=True, use_container_width=True)

if is_admin():
    with st.expander("Rejected audit preview"):
        if rejected.empty:
            st.caption("No rejected feedback is available.")
        else:
            st.dataframe(rejected, hide_index=True, use_container_width=True)
