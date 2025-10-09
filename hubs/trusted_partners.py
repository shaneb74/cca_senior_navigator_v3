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
    st.markdown('<h1 class="text-center" style="margin: 16px 0 32px; font-size: 2rem; font-weight: 700; color: #0f172a;">Trusted Partners Hub</h1>', unsafe_allow_html=True)

    # Start the hub grid
    st.markdown('<div class="hub-grid">', unsafe_allow_html=True)

    # Render partner tiles
    render_hub_tile(
        title="Home Care Agencies",
        badge="Agencies",
        label="Verified Partners",
        value="15 agencies",
        status="new",
        primary_label="View agencies",
        secondary_label="Compare services"
    )

    render_hub_tile(
        title="Senior Communities",
        badge="Communities",
        label="Available Options",
        value="8 communities",
        status="new",
        primary_label="Explore options",
        secondary_label="Virtual tours"
    )

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
                Trusted Partners Hub
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Verified care providers and senior living communities in your area.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Hub tiles grid
    st.markdown('<div class="tiles">', unsafe_allow_html=True)

    # Render partner tiles
    render_hub_tile(
        title="Home Care Agencies",
        badge="Agencies",
        label="Verified Partners",
        value="15 agencies",
        status="new",
        primary_label="View agencies",
        secondary_label="Compare services"
    )

    render_hub_tile(
        title="Senior Communities",
        badge="Communities",
        label="Available Options",
        value="8 communities",
        status="new",
        primary_label="Explore options",
        secondary_label="Virtual tours"
    )

    render_hub_tile(
        title="Financial Advisors",
        badge="Finance",
        label="Specialized Help",
        value="6 advisors",
        status="new",
        primary_label="Find advisor",
        secondary_label="Resource center"
    )

    # Close the tiles grid and section
    st.markdown('</div></section>', unsafe_allow_html=True)
