import streamlit as st

from layout import render_page
from pages.welcome import render_welcome_card


def _page_content(ctx=None):
    render_welcome_card(
        active="self",
        title="We're here to help you find the support you're looking for.",
        placeholder="What's your name?",
        note="",
        image_path="static/images/welcome_self.png",
        submit_route="hub_concierge",
    )


def render(ctx=None):
    st.set_page_config(page_title="Concierge Care Senior Navigator", layout="wide")
    render_page(_page_content, ctx, show_header=True, show_footer=True)
