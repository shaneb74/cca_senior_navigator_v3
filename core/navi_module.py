"""
Module-level Navi component for GCP, Cost Planner, CCR, and other products.

Displays compact coaching panel with primary message, optional "Why this question?" 
explanation, and current plan summary (recommendation + care costs).
"""

import streamlit as st


def render_module_navi_coach(primary_msg: str, why_text: str | None = None):
    """Compact module coach with optional 'Why this question?' slot and plan summary."""
    ss = st.session_state
    gcp = ss.get("gcp") or {}
    cost = ss.get("cost") or {}

    tier = gcp.get("published_tier")
    plan = (
        "Assisted Living (memory support)"
        if tier == "assisted_living"
        else (tier or "").replace("_", " ").title()
    )
    care = cost.get("monthly_total")

    st.markdown("<div class='navi-panel-compact'>", unsafe_allow_html=True)
    st.write(f"✨ {primary_msg}")

    # Why this question? (render only when provided by caller)
    if why_text:
        st.markdown("**[?] Why this question?**")
        st.caption(why_text)

    # Prominent current plan summary (always present if available)
    if plan or care:
        line = "**Current Plan:** "
        if plan:
            line += plan
        if care:
            line += f" · Care: ${int(care):,}/mo"
        st.markdown(line)
        st.caption("(Home carry tracked separately if you keep your home.)")

    st.markdown("</div>", unsafe_allow_html=True)
