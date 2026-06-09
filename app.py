from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from services.access_control import is_admin, render_access_panel
from services.database import create_tables
from services.ui import apply_govai_branding

load_dotenv()
create_tables()

st.set_page_config(
    page_title="GovAI UAT Feedback Dashboard",
    page_icon=":material/check_circle:",
    layout="wide",
)

apply_govai_branding()
render_access_panel()

pages_dir = Path(__file__).parent / "pages"

viewer_pages = [
    st.Page(pages_dir / "1_Home.py", title="Home", icon=":material/home:"),
    st.Page(
        pages_dir / "5_Feedback_Register.py",
        title="Feedback Register",
        icon=":material/list_alt:",
    ),
    st.Page(
        pages_dir / "6_Dashboard.py",
        title="Dashboard",
        icon=":material/bar_chart:",
    ),
    st.Page(
        pages_dir / "7_Export.py",
        title="Export",
        icon=":material/download:",
    ),
]

owner_pages = [
    viewer_pages[0],
    st.Page(
        pages_dir / "2_Upload_Feedback.py",
        title="Upload Feedback",
        icon=":material/upload:",
    ),
    st.Page(
        pages_dir / "3_Extract_Feedback.py",
        title="Extract Feedback",
        icon=":material/data_object:",
    ),
    st.Page(
        pages_dir / "4_Review_Extracted_Items.py",
        title="Review Extracted Items",
        icon=":material/edit:",
    ),
    *viewer_pages[1:],
]

navigation = st.navigation(
    owner_pages if is_admin() else viewer_pages
)
navigation.run()
