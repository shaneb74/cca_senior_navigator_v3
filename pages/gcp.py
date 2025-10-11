import streamlit as st

from core.nav import route_to
from pages._stubs import _page


def render():
    """Temporary landing page for the Guided Care Plan experience."""
    _page(
        title="Guided Care Plan",
        desc="A full decision-support experience is on the way. For now, expect a curated care assessment tailored to your family.",
        ctas=[
            ("Return to Concierge Hub", "hub_concierge"),
        ],
    )

    with st.expander("Need to continue the existing version?"):
        st.write(
            "Launch the current Guided Care Plan module if you have in-progress answers you need to access."
        )
        if st.button("Open Guided Care Plan", key="gcp_open"):
            route_to("gcp")
