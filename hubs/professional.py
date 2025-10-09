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
    st.markdown('<h2 class="text-center" style="margin: 8px 0 24px;">Professional Hub</h2>', unsafe_allow_html=True)

    # Start the hub grid
    st.markdown('<div class="hub-grid">', unsafe_allow_html=True)

    # Render professional service tiles
    render_hub_tile(
        title="Care Coordination",
        badge="Coordination",
        label="Service Status",
        value="Available",
        status="new",
        primary_label="Schedule consultation",
        secondary_label="Learn more"
    )

    render_hub_tile(
        title="Legal Services",
        badge="Legal",
        label="Estate Planning",
        value="Specialized help",
        status="new",
        primary_label="Find attorney",
        secondary_label="Document prep"
    )

    render_hub_tile(
        title="Financial Planning",
        badge="Finance",
        label="Senior Finance",
        value="Expert guidance",
        status="new",
        primary_label="Book appointment",
        secondary_label="Resource center"
    )

    # Close the hub grid and page wrapper
    st.markdown('</div></section>', unsafe_allow_html=True)
