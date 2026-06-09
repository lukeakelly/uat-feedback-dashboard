from pathlib import Path

import streamlit as st

from services.access_control import require_admin
from services.database import insert_source_file, list_source_files
from services.file_ingestion import extract_content
from services.ui import page_intro
from services.validation import SOURCE_TYPES, UAT_ROUNDS

require_admin()

page_intro(
    "Upload feedback",
    "Add one UAT feedback file and record enough source information for reviewers "
    "to understand where each item came from.",
    "Step 1 of 5",
)

with st.form("upload_feedback_form", clear_on_submit=False):
    uploaded_file = st.file_uploader(
        "Feedback file",
        type=["docx", "xlsx", "csv", "txt"],
        accept_multiple_files=False,
    )
    left, right = st.columns(2)
    with left:
        uat_round = st.selectbox("UAT round", UAT_ROUNDS)
        session_name = st.text_input("Session name")
        participant_role = st.text_input("Participant role (optional)")
    with right:
        source_type = st.selectbox("Source type", SOURCE_TYPES)
        test_scenario = st.text_input("Test scenario (optional)")
        notes = st.text_area("Notes (optional)")
    submitted = st.form_submit_button("Upload and read file", type="primary")

if submitted:
    if uploaded_file is None:
        st.error("Choose a feedback file first.")
    elif not session_name.strip():
        st.error("Enter a session name.")
    else:
        try:
            content = extract_content(uploaded_file)
            metadata = {
                "filename": uploaded_file.name,
                "file_type": Path(uploaded_file.name).suffix.lower().lstrip("."),
                "uat_round": uat_round,
                "session_name": session_name.strip(),
                "source_type": source_type,
                "participant_role_default": participant_role.strip(),
                "test_scenario_default": test_scenario.strip(),
                "notes": notes.strip(),
            }
            source_file_id = insert_source_file(metadata, content)
            st.session_state["last_source_file_id"] = source_file_id
            st.success(
                f"Uploaded {uploaded_file.name}. "
                "It is ready for extraction on the Extract Feedback page."
            )
            st.subheader("Content preview")
            st.text_area(
                "Read-only preview",
                content["preview"] or "No readable content found.",
                height=260,
                disabled=True,
            )
        except Exception as exc:
            st.error(f"The file could not be read: {exc}")

with st.expander("Recent uploads"):
    sources = list_source_files()
    if sources.empty:
        st.caption("No files have been uploaded yet.")
    else:
        st.dataframe(sources, hide_index=True, use_container_width=True)
