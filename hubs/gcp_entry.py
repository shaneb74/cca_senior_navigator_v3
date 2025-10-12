from __future__ import annotations

from textwrap import dedent

import streamlit as st

from core.modules import run_module
from layout import render_page
from products.gcp.module_config import get_config

INTRO_STATE_KEY = "gcp_intro_started"
INTRO_COPY = dedent(
    """
    We’ll match you to the best living options based on daily needs, safety, cognition, and more. Takes about two minutes.

    - Personalized guidance rooted in your answers
    - No data loss — you can pause and return anytime
    - Unlock curated partners once you are halfway through
    """
).strip()


def page_gcp_entry() -> None:
    config = get_config()

    if st.session_state.get(config.state_key):
        st.session_state[INTRO_STATE_KEY] = True

    def _content() -> None:
        if st.session_state.get(INTRO_STATE_KEY):
            run_module(config)
            return

        st.markdown(INTRO_COPY)
        if st.button("Start Guided Care Plan", key="gcp_intro_start", type="primary"):
            st.session_state[INTRO_STATE_KEY] = True
            step_key = f"{config.state_key}._step"
            if st.session_state.get(step_key, 0) == 0:
                st.session_state[step_key] = 1
            _rerun()

    render_page(content=_content, active_route="gcp", title="Find the Right Senior Care")


render = page_gcp_entry


__all__ = ["page_gcp_entry", "render"]


def _rerun() -> None:
    rerun = getattr(st, "rerun", None)
    if callable(rerun):
        rerun()
        return
    legacy = getattr(st, "experimental_rerun", None)
    if callable(legacy):
        legacy()
