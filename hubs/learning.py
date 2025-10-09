import streamlit as st
from core.ui import render_hub_tile


def render():
    # Import the hub grid CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>"
        "<link rel='stylesheet' href='/assets/css/hub_grid.css'>",
        unsafe_allow_html=True
    )

    # Wrap the entire hub content
    st.markdown('<section class="hub-page">', unsafe_allow_html=True)
    st.markdown('<h1 class="text-center" style="margin: 16px 0 32px; font-size: 2rem; font-weight: 700; color: #0f172a;">Learning & Resources Hub</h1>', unsafe_allow_html=True)

    # Start the hub grid
    st.markdown('<div class="hub-grid">', unsafe_allow_html=True)

    # Render learning resource tiles
    render_hub_tile(
        title="Caregiver Guides",
        badge="Guides",
        label="Available Resources",
        value="12 articles",
        status="new",
        primary_label="Browse guides",
        secondary_label="Most popular"
    )

    render_hub_tile(
        title="Video Library",
        badge="Videos",
        label="Educational Content",
        value="8 videos",
        status="new",
        primary_label="Watch now",
        secondary_label="Categories"
    )

    render_hub_tile(
        title="FAQ Center",
        badge="FAQ",
        label="Common Questions",
        value="25 topics",
        status="new",
        primary_label="Search FAQs",
        secondary_label="Contact support"
    )

    # Close the hub grid and page wrapper
    st.markdown('</div></section>', unsafe_allow_html=True)
