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
