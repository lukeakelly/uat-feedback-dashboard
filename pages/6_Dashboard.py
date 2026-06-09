import pandas as pd
import plotly.express as px
import streamlit as st

from services.dashboard import count_by, dashboard_metrics
from services.database import load_approved_feedback
from services.validation import MUST_FIX_PRIORITIES, OPEN_STATUSES

st.title("Dashboard")
st.caption("All metrics and charts use approved, non-archived feedback only.")

approved = load_approved_feedback()
metrics = dashboard_metrics(approved)

kpi_columns = st.columns(6)
kpi_columns[0].metric("Total approved", metrics["total"])
kpi_columns[1].metric("Open", metrics["open"])
kpi_columns[2].metric("Must-fix", metrics["must_fix"])
kpi_columns[3].metric("High severity", metrics["high_severity"])
kpi_columns[4].metric("Awaiting decision", metrics["awaiting_decision"])
kpi_columns[5].metric("Resolved", metrics["resolved"])

if approved.empty:
    st.info("Approve feedback items to populate the dashboard.")
    st.stop()

chart_fields = [
    ("severity", "Feedback by severity"),
    ("priority", "Feedback by priority"),
    ("feature_area", "Feedback by feature area"),
    ("type", "Feedback by type"),
    ("status", "Feedback by status"),
    ("owner", "Feedback by owner"),
    ("uat_round", "Feedback by UAT round"),
]

for index in range(0, len(chart_fields), 2):
    columns = st.columns(2)
    for offset, (field, title) in enumerate(chart_fields[index : index + 2]):
        counts = count_by(approved, field)
        figure = px.bar(
            counts,
            x="count",
            y=field,
            orientation="h",
            title=title,
            labels={"count": "Items", field: ""},
        )
        figure.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        columns[offset].plotly_chart(figure, use_container_width=True)

st.subheader("Priority review tables")
must_fix = approved[approved["priority"].isin(MUST_FIX_PRIORITIES)]
high_open = approved[
    approved["severity"].isin(["Blocker", "High"])
    & approved["status"].isin(OPEN_STATUSES)
]
awaiting = approved[
    approved["human_decision"].isin(["Pending", "Needs clarification"])
]
unresolved = approved[approved["status"].isin(OPEN_STATUSES)].copy()
unresolved["created_at"] = pd.to_datetime(unresolved["created_at"], errors="coerce")
unresolved = unresolved.sort_values("created_at").head(20)

tables = [
    ("Must-fix items", must_fix),
    ("High severity open items", high_open),
    ("Items awaiting decision", awaiting),
    ("Oldest unresolved items", unresolved),
]
display_columns = [
    "feedback_id",
    "feature_area",
    "interpreted_issue",
    "severity",
    "priority",
    "status",
    "owner",
]
for title, dataframe in tables:
    with st.expander(f"{title} ({len(dataframe)})"):
        st.dataframe(
            dataframe[[column for column in display_columns if column in dataframe]],
            hide_index=True,
            use_container_width=True,
        )

themes = count_by(approved[approved["theme"].ne("Needs review")], "theme").head(10)
with st.expander("Top recurring themes"):
    if themes.empty:
        st.caption("No reviewed themes are available yet.")
    else:
        st.dataframe(themes, hide_index=True, use_container_width=True)
