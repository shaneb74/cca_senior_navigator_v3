"""Legacy AI Advisor entry point.

This module now redirects to the unified AI Advisor chat experience in
``pages.faq:render`` so any stale bookmarks keep working.
"""

import streamlit as st


def render() -> None:
    """Redirect to the canonical AI Advisor chat page."""
    st.session_state["current_route"] = "faq"
    st.query_params["page"] = "faq"
    st.rerun()
