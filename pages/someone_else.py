import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from core.state import is_authenticated
from layout import render_page
from pages.welcome import render_welcome_card


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
        active="someone",
        title="We're here to help you find the support your loved ones need.",
        placeholder="What's their name?",
        note="If you want to assess several people, don't worry – you can easily move on to the next step!",
        image_path="static/images/welcome_someone_else.png",
        submit_route="hub_concierge",
    )


def render(ctx=None):
    render_page(_page_content, ctx, active_route="someone_else")
