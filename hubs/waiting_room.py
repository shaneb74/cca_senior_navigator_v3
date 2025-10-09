import streamlit as st
from core.ui import render_hub_tile


def render():
    # Import the theme CSS
    st.markdown(
        "<link rel='stylesheet' href='/assets/css/theme.css'>",
        unsafe_allow_html=True
    )

    # Apply canvas background like welcome pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)
    
    # Hero section with title
    st.markdown(
        f"""
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
                Waiting Room Hub
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Track your appointment status and complete pre-visit tasks.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Hub tiles grid
    st.markdown('<div class="tiles">', unsafe_allow_html=True)

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

    # Close the tiles grid and section
    st.markdown('</div></section>', unsafe_allow_html=True)
