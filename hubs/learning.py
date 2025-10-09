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
                Learning & Resources Hub
            </h1>
            <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
                Educational content and tools to support your senior care journey.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Hub tiles grid
    st.markdown('<div class="tiles">', unsafe_allow_html=True)

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

    # Close the tiles grid and section
    st.markdown('</div></section>', unsafe_allow_html=True)
