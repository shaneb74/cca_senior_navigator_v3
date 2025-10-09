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
                Professional Hub
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Tools and resources for discharge planners, social workers, and care partners.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Hub tiles grid
    st.markdown('<div class="tiles">', unsafe_allow_html=True)

    # Render professional service tiles
    render_hub_tile(
        title="Care Coordination",
        badge="Coordination",
        label="Service Status",
        value="Available",
        status="new",
        primary_label="Schedule consultation"
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

    # Close the tiles grid and section
    st.markdown('</div></section>', unsafe_allow_html=True)
