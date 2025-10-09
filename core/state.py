from copy import deepcopy

import streamlit as st

DEFAULT_CTX = {
    "auth": {"is_authenticated": False, "user_id": None, "role": "guest"},
    "flags": {},
}


def ensure_session():
    if "ctx" not in st.session_state:
        st.session_state.ctx = deepcopy(DEFAULT_CTX)


def get_user_ctx():
    return st.session_state.ctx


def set_module_status(module_key: str, status: str):
    """Set the status of a module (e.g., 'done', 'in_progress')."""
    if "module_status" not in st.session_state:
        st.session_state.module_status = {}
    st.session_state.module_status[module_key] = status


def get_module_status(module_key: str) -> str:
    """Get the status of a module."""
    return st.session_state.get("module_status", {}).get(module_key, "")
