import streamlit as st

from core.data import load_blurbs


def render():
    st.header("Plan with My Advisor")
    blurbs = load_blurbs()

    profile = st.session_state.get("care_profile", {})
    answers = profile.get("answers", {})
    if answers.get("medicaid_status") in ("yes", "unsure"):
        notice = blurbs.get(
            "pfma_medicaid_notice",
            "If you’re on Medicaid or unsure, our team can’t schedule appointments because Medicaid offers its own long-term care programs. You can still review your plan and resources, but appointment scheduling is limited to non-Medicaid cases.",
        )
        st.warning(notice)

    st.write("Advisor planning tools coming soon.")
