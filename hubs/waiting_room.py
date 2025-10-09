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
    st.markdown('<h1 class="text-center" style="margin: 16px 0 32px; font-size: 2rem; font-weight: 700; color: #0f172a;">Waiting Room Hub</h1>', unsafe_allow_html=True)

    # Start the hub grid
    st.markdown('<div class="hub-grid">', unsafe_allow_html=True)

    # Render waiting room tiles
    render_hub_tile(
        title="Appointment Status",
        badge="Status",
        label="Next Appointment",
        value="Dr. Smith - Oct 15",
        status="new",
        primary_label="View details",
        secondary_label="Reschedule"
    )

    render_hub_tile(
        title="Preparation Guide",
        badge="Prep",
        label="What to Bring",
        value="Documents ready",
        status="new",
        primary_label="Check list",
        secondary_label="Questions"
    )

    render_hub_tile(
        title="Virtual Waiting",
        badge="Virtual",
        label="Current Status",
        value="Room 204",
        status="doing",
        primary_label="Join call",
        secondary_label="Estimated wait"
    )

    # Close the hub grid and page wrapper
    st.markdown('</div></section>', unsafe_allow_html=True)
