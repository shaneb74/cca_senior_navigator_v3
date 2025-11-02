"""Concierge Clinical Review - Main product dispatcher."""

import streamlit as st
from .overview import render_overview
from .checklist import render_checklist
from .schedule import render_schedule


def render():
    """Main entry point for Concierge Clinical Review."""
    view = st.session_state.get("ccr.view", "overview")
    if view == "checklist":
        render_checklist()
    elif view == "schedule":
        render_schedule()
    else:
        render_overview()
