import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from core.state import is_authenticated
from pages.welcome import render_welcome_card
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def _page_content(ctx=None):
    # Check if authenticated user already has planning context
    if is_authenticated():
        has_context = (
            st.session_state.get("planning_for_name")
            or st.session_state.get("person_name")
        )
        if has_context:
            # Skip contextual welcome - go directly to Navi's recommended route
            next_action = MCIP.get_recommended_next_action()
            route_to(next_action.get("route", "hub_concierge"))
            return
    
    render_welcome_card(
        active="self",
        title="We're here to help you find the support you're looking for.",
        placeholder="What's your name?",
        note="",
        image_path="static/images/welcome_self.png",
        submit_route="hub_concierge",
    )


def render(ctx=None):
    # Render with simple header/footer
    render_header_simple(active_route="self")
    _page_content(ctx)
    render_footer_simple()
