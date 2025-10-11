import streamlit as st

from ui.welcome_shared import render_welcome_card


def render():
    st.set_page_config(page_title="Concierge Care Senior Navigator", layout="wide")
    render_welcome_card(
        active="someone",
        title="We're here to help you find the support your loved ones need.",
        placeholder="What’s their name?",
        note="If you want to assess several people, don’t worry — you can easily move on to the next step!",
        image_path="static/images/welcome_someone_else.png",
        submit_route="hub_concierge",
    )
