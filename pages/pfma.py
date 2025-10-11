import streamlit as st

from core.nav import route_to
from pages._stubs import _page


def render():
    """Stub for the Plan with My Advisor flow."""
    _page(
        title="Plan with My Advisor",
        desc="Schedule time with a concierge advisor and get matched to the right professional support.",
        ctas=[
            ("Return to Concierge Hub", "hub_concierge"),
        ],
    )

    with st.expander("Need to talk sooner?"):
        st.write("Jump into the current experience to see availability and request a call.")
        if st.button("Get connected", key="pfma_open"):
            route_to("pfma")
