"""
Hub-level Navi component for Concierge and Waiting Room.

Displays "What's Next" panel with current plan summary, Clinical Review status,
Advisor appointments, and optional single CTA when there's one clear next step.
"""

import streamlit as st


def render_hub_navi_next():
    """Minimal 'What's Next' panel for hubs (Concierge/Waiting)."""
    ss = st.session_state
    gcp = ss.get("gcp") or {}
    ccr = ss.get("ccr") or {}
    appt = ss.get("advisor_appointment")

    tier = gcp.get("published_tier")
    plan = (
        "Assisted Living (memory support)"
        if tier == "assisted_living"
        else (tier or "").replace("_", " ").title()
    )

    # Panel shell
    st.markdown("<div class='navi-panel-v2'>", unsafe_allow_html=True)
    st.markdown("### ✨ NAVI — What's Next")

    if plan:
        st.write(f"**Recommendation:** {plan}")
    # Clinical Review
    cr = "Not yet scheduled" if not ccr.get("appt_scheduled") else "Scheduled"
    st.write(f"**Clinical Review:** {cr}")
    # Advisor (upcoming)
    if isinstance(appt, dict) and appt.get("date") and appt.get("time"):
        st.write(
            f"**Advisor:** {appt['date']} · {appt['time']} · {appt.get('type', '')}".strip()
        )

    # Rotating tip (placeholder; later LLM)
    st.caption("Tip: You can confirm your plan with a brief clinical review.")

    # Optional single CTA (only if a single clear action exists)
    next_route = None
    if not ccr.get("appt_scheduled"):
        next_route = "ccr_overview"
    if next_route:
        if st.button("Next Step", key="navi_hub_next"):
            ss["route"] = next_route
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
