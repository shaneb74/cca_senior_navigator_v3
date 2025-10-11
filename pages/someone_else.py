import streamlit as st

from layout import render_page
from pages.welcome import render_welcome_card


def _page_content(ctx=None):
    render_welcome_card(
        active="someone",
        title="We’re here to help you find the support your loved ones need.",
        placeholder="What’s their name?",
        note="If you want to assess several people, don’t worry – you can easily move on to the next step!",
        image_path="static/images/welcome_someone_else.png",
        submit_route="hub_concierge",
    )


def render(ctx=None):
    st.set_page_config(page_title="Concierge Care Senior Navigator", layout="wide")
    render_page(_page_content, ctx, show_header=True, show_footer=True)
