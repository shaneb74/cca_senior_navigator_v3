import streamlit as st

from layout import render_page
from pages.welcome import render_welcome_card


def _page_content(ctx=None):
    render_welcome_card(
        active="pro",
        title="Support your patients and families with coordinated care.",
        placeholder="Patient or client name",
        note="You can assess multiple clients and invite colleagues on the next step.",
        image_path="static/images/contextual_professional.png",
        submit_route="hub_professional",
    )


def render(ctx=None):
    st.set_page_config(page_title="Concierge Care Senior Navigator", layout="wide")
    render_page(_page_content, ctx, show_header=True, show_footer=True)
