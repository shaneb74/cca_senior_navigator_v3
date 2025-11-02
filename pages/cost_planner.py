import streamlit as st

from core.nav import route_to
from pages.stubs import _page


def render():
    """Placeholder Cost Planner landing page."""
    _page(
        title="Cost Planner",
        desc="Project monthly costs, compare funding options, and keep your runway crystal-clear. A refreshed experience is nearly ready.",
        ctas=[
            ("Back to Lobby", "hub_lobby"),
        ],
    )

    with st.expander("Preview the current planner prototype"):
        st.info("The next iteration keeps all of your saved answers.")
        if st.button("Open Cost Planner", key="cost_planner_open"):
            route_to("cost_planner")
