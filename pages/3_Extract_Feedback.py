import streamlit as st

from services.access_control import require_admin
from services.ai_extractor import ai_is_available, extract_with_ai
from services.database import (
    get_source_file,
    insert_pending_feedback,
    list_source_files,
)
from services.fallback_extractor import extract_fallback
from services.ui import page_intro

require_admin()

page_intro(
    "Extract feedback",
    "Create structured, pending feedback items from an uploaded source. "
    "Use AI assistance when approved, or the local fallback extractor.",
    "Step 2 of 5",
)
st.warning("Extracted rows are not approved. Review them before they enter the register.")

sources = list_source_files()
if sources.empty:
    st.info("Upload a feedback file before running extraction.")
    st.stop()

source_options = {
    int(row.id): f"{row.filename} — {row.session_name} ({row.uat_round})"
    for row in sources.itertuples()
}
default_source = st.session_state.get("last_source_file_id")
source_ids = list(source_options)
default_index = source_ids.index(default_source) if default_source in source_ids else 0
source_id = st.selectbox(
    "Uploaded source",
    source_ids,
    index=default_index,
    format_func=lambda value: source_options[value],
)

source = get_source_file(source_id)
if source is None:
    st.error("The selected source could not be found.")
    st.stop()

with st.expander("Source preview", expanded=False):
    st.text_area(
        "Content",
        source.get("content_preview", "") or "No readable content found.",
        height=240,
        disabled=True,
    )

available = ai_is_available()
if available:
    mode = st.radio(
        "Extraction mode",
        ["AI extraction", "Simple fallback extraction"],
        horizontal=True,
    )
    st.caption("AI output will still require human review.")
else:
    mode = "Simple fallback extraction"
    st.info(
        "No OpenAI API key was found. The local fallback extractor will create "
        "one pending item per paragraph, line, or non-empty table row."
    )

if st.button("Extract pending items", type="primary"):
    content = {
        "text": source.get("content_text", ""),
        "records": source.get("records", []),
    }
    metadata = {
        "uat_round": source.get("uat_round", ""),
        "session_name": source.get("session_name", ""),
        "participant_role_default": source.get("participant_role_default", ""),
        "test_scenario_default": source.get("test_scenario_default", ""),
    }
    try:
        if mode == "AI extraction":
            items = extract_with_ai(content, metadata)
        else:
            items = extract_fallback(content, metadata)
        count = insert_pending_feedback(source_id, items)
        st.success(f"Created {count} pending feedback item(s).")
        if count:
            st.dataframe(items, hide_index=True, use_container_width=True)
    except Exception as exc:
        st.error(f"Extraction failed: {exc}")
        if mode == "AI extraction":
            st.caption("Choose Simple fallback extraction to continue without AI.")
