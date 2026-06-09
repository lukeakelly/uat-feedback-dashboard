from __future__ import annotations

import hmac
import os

import streamlit as st

ADMIN_SESSION_KEY = "govai_owner_authenticated"


def get_admin_password() -> str:
    password = os.getenv("APP_ADMIN_PASSWORD", "").strip()
    if password:
        return password
    try:
        return str(st.secrets.get("APP_ADMIN_PASSWORD", "")).strip()
    except (FileNotFoundError, KeyError):
        return ""


def admin_access_is_configured() -> bool:
    return bool(get_admin_password())


def is_admin() -> bool:
    return bool(st.session_state.get(ADMIN_SESSION_KEY, False))


def authenticate_admin(password: str) -> bool:
    expected = get_admin_password()
    authenticated = bool(expected) and hmac.compare_digest(password, expected)
    st.session_state[ADMIN_SESSION_KEY] = authenticated
    return authenticated


def sign_out_admin() -> None:
    st.session_state[ADMIN_SESSION_KEY] = False


def require_admin() -> None:
    if is_admin():
        return
    st.error("Owner access is required for this page.")
    st.info("Use the Owner password panel in the sidebar to unlock editing.")
    st.stop()


def render_access_panel() -> None:
    with st.sidebar:
        st.divider()
        st.markdown("#### Access")
        if is_admin():
            st.success("Owner mode")
            st.caption("Editing and approval controls are available.")
            if st.button("Return to read-only mode", use_container_width=True):
                sign_out_admin()
                st.rerun()
            return

        st.info("Read-only mode")
        st.caption("You can view approved feedback, dashboards and exports.")
        if not admin_access_is_configured():
            st.caption("Owner access has not been configured for this deployment.")
            return

        with st.form("owner_access_form"):
            password = st.text_input("Owner password", type="password")
            submitted = st.form_submit_button(
                "Unlock owner mode",
                use_container_width=True,
            )
        if submitted:
            if authenticate_admin(password):
                st.rerun()
            st.error("The owner password is incorrect.")
