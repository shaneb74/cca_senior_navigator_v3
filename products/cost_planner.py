from __future__ import annotations

import streamlit as st

from core.events import log_event

BASE_MONTHLY = {
    "In-Home Care": 3200.0,
    "Assisted Living": 5200.0,
    "Memory Care": 6800.0,
    "Memory Care High Acuity": 8200.0,
}


def _ensure_state():
    st.session_state.setdefault("cost_planner", {"inputs": {}, "summary": None})


def render():
    _ensure_state()
    st.header("Cost Planner")

    profile = st.session_state.get("care_profile", {})
    rec_setting = profile.get("care_setting", "In-Home Care")
    st.info(f"Starting from Guided Care Plan recommendation: **{rec_setting}**")

    col1, col2 = st.columns(2)
    settings_list = list(BASE_MONTHLY.keys())
    with col1:
        setting = st.selectbox(
            "Care setting",
            settings_list,
            index=settings_list.index(rec_setting) if rec_setting in settings_list else 0,
        )
        hours_per_day = st.slider("Hours of paid care per day (In-Home only)", 0, 24, 4)
        days_per_week = st.slider("Days per week", 0, 7, 4)
    with col2:
        region_multiplier = st.slider("Regional cost multiplier", 0.6, 1.8, 1.0, 0.05)
        benefits_offset = st.number_input(
            "Monthly benefits offset (VA, pension, etc.)",
            min_value=0.0,
            value=0.0,
            step=50.0,
        )

    monthly = BASE_MONTHLY[setting]
    if setting == "In-Home Care":
        hourly_rate = 28.0 * region_multiplier
        monthly = hourly_rate * hours_per_day * days_per_week * 4.345

    monthly *= region_multiplier
    total = max(monthly - benefits_offset, 0.0)

    st.subheader("Estimate")
    st.metric("Estimated monthly cost", f"${total:,.0f}")

    if st.button("Save & complete"):
        st.session_state["cost_planner_completed"] = True
        summary = {
            "setting": setting,
            "monthly": round(total, 2),
            "region_multiplier": region_multiplier,
            "benefits_offset": benefits_offset,
        }
        st.session_state["cost_planner"]["summary"] = summary
        st.session_state["plan_packet"] = {
            "care_profile": profile,
            "cost_estimate": summary,
        }
        log_event("cost_planner.completed", {"setting": setting, "monthly": total})
        st.success("Saved. You can continue to Plan with My Advisor or return to the Hub.")
        st.markdown(
            '<div class="kit-row">'
            '<a class="btn btn--secondary" href="?page=hub_concierge">Back to Hub</a>'
            '<a class="btn btn--primary" href="?page=waiting_room">Plan with my advisor</a>'
            '</div>',
            unsafe_allow_html=True,
        )
