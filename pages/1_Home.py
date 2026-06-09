import streamlit as st

from services.dashboard import count_by, dashboard_metrics
from services.database import load_approved_feedback

st.title("UAT Feedback Dashboard")
st.write(
    "Upload UAT feedback, extract structured items, review each item, "
    "and report on the approved register."
)

st.info(
    "Extracted items are always held for human review. "
    "Only approved items appear in dashboard metrics and exports."
)

approved = load_approved_feedback()
metrics = dashboard_metrics(approved)

columns = st.columns(4)
columns[0].metric("Total approved items", metrics["total"])
columns[1].metric("Open items", metrics["open"])
columns[2].metric("Must-fix items", metrics["must_fix"])
columns[3].metric("Awaiting decision", metrics["awaiting_decision"])

st.subheader("Items by severity")
severity = count_by(approved, "severity")
if severity.empty:
    st.caption("No approved feedback has been added yet.")
else:
    st.bar_chart(severity.set_index("severity"))

st.subheader("Workflow")
st.markdown(
    """
1. **Upload Feedback** and add source details.
2. **Extract Feedback** using AI or the local fallback.
3. **Review Extracted Items** and approve or reject each row.
4. Use the **Feedback Register** and **Dashboard** to manage approved items.
5. Download the register from **Export**.
"""
)
