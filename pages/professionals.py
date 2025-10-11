import streamlit as st

from ui.welcome_shared import render_welcome_card


def render():
    st.set_page_config(page_title="Concierge Care Senior Navigator", layout="wide")
    render_welcome_card(
        active="pro",
        title="Support your patients and families with coordinated care.",
        placeholder="Patient or client name",
        note="You can assess multiple clients and invite colleagues on the next step.",
        image_path="static/images/contextual_professional.png",
        submit_route="hub_professional",
    )
