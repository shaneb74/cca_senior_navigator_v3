import streamlit as st
from core.ui import render_hub_tile


def render():
    # Import the theme CSS and apply new styling
    st.markdown(
        """
        <link rel='stylesheet' href='/assets/css/theme.css'>
        <style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        /* New styling overrides */
        .stButton > button {
            background: #3B82F6 !important;
            color: white !important;
            border-radius: 5px !important;
            border: none !important;
        }
        .stButton > button:hover {
            background: #2563EB !important;
        }
        .stRadio label[data-baseweb="radio"] input:checked + div {
            color: black !important;
        }
        .stRadio label[data-baseweb="radio"] input:not(:checked) + div {
            color: gray !important;
        }
        .stTextInput > div > div, .stNumberInput > div > div, .stSelectbox > div > div, .stTextArea > div > div {
            border-radius: 5px !important;
            padding: 10px !important;
        }
        .container {
            padding: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main content container
    st.markdown('<section class="container section">', unsafe_allow_html=True)

    # Hero section with icon and title
    st.markdown(
        """
        <div class="text-center" style="margin-bottom: var(--space-10);">
            <div style="font-size: 3rem; margin-bottom: var(--space-4);">🤝</div>
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
    st.markdown('<div class="tiles" style="padding: 10px;">', unsafe_allow_html=True)

    # Render partner tiles
    st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)
    render_hub_tile(
        title="Home Care Agencies",
        badge="Agencies",
        label="Verified Partners",
        value="15 agencies",
        status="new",
        primary_label="View agencies",
        secondary_label="Compare services"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)
    render_hub_tile(
        title="Senior Communities",
        badge="Communities",
        label="Available Options",
        value="8 communities",
        status="new",
        primary_label="Explore options",
        secondary_label="Virtual tours"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)
    render_hub_tile(
        title="Financial Advisors",
        badge="Finance",
        label="Specialized Help",
        value="6 advisors",
        status="new",
        primary_label="Find advisor",
        secondary_label="Resource center"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Close the tiles grid and section
    st.markdown('</div></section>', unsafe_allow_html=True)</content>
<parameter name="filePath">/Users/shane/Desktop/cca_senior_navigator_v3/hubs/trusted_partners.py