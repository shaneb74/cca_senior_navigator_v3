"""Concierge Clinical Review - Specialist scheduling page."""

import streamlit as st
from datetime import datetime


def render_schedule():
    """Render mock scheduling page."""
    st.markdown("### Schedule a Specialist Review")
    st.caption("Mock scheduling for demo purposes.")

    visit = st.radio("Visit Type", ["Virtual (30 minutes)", "In-Clinic"], index=0, key="ccr.visit_type")
    st.write("**Available Times**")
    slot = st.selectbox("Choose a time", [
        "Wednesday, 10:00 AM",
        "Thursday, 2:30 PM",
        "Friday, 9:00 AM"
    ], key="ccr.slot")

    c1, c2 = st.columns(2)
    if c1.button("Confirm Appointment", use_container_width=True, key="ccr_confirm"):
        st.session_state.setdefault("ccr", {})
        st.session_state["ccr"]["appt_scheduled"] = True
        print("[CCR] schedule.mock_submitted", datetime.utcnow().isoformat() + "Z")
        st.success("Your Concierge Clinical Review has been scheduled. A care coordinator will follow up with details.")

    if c2.button("Back to Review", use_container_width=True, key="ccr_back2"):
        st.session_state["ccr.view"] = "overview"
        st.rerun()
