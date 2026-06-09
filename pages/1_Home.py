import streamlit as st

from services.dashboard import count_by, dashboard_metrics
from services.database import load_approved_feedback
from services.ui import page_intro

page_intro(
    "UAT feedback dashboard",
    "Turn testing feedback into a clear, reviewed register for the GovAI Library. "
    "Upload source material, check every extracted item and track approved feedback.",
    "GovAI Library",
)

st.info(
    "Human review is required. Extracted items remain pending until a reviewer "
    "approves or rejects them."
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
