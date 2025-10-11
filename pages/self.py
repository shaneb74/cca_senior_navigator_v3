import streamlit as st

from ui.welcome_shared import render_welcome_card


def render():
    st.set_page_config(page_title="Concierge Care Senior Navigator", layout="wide")
    render_welcome_card(
        active="self",
        title="We're here to help you find the support you need.",
        placeholder="What’s your name?",
        note="You’ll be able to adjust details in the next step.",
        image_path="static/images/welcome_self.png",
        submit_route="hub_concierge",
    )
