import streamlit as st

from core.state import get_module_state, get_user_ctx
from core.ui import hub_section, render_module_tile, tiles_close, tiles_open


def render():
    # Import the theme CSS and apply new styling
    st.markdown(
        """
        <link rel='stylesheet' href='/assets/css/global.css'>
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
            color: black;
        }
        .stRadio label[data-baseweb="radio"] input:not(:checked) + div {
            color: gray;
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
        unsafe_allow_html=True,
    )

    # Main content container
    st.markdown(
        '<section class="container section" style="padding: 10px;">',
        unsafe_allow_html=True,
    )

    ctx = get_user_ctx()
    user_id = ctx["auth"].get("user_id", "guest")
    product_key = "pfma"

    hub_section("Plan with My Advisor")
    tiles_open()

    # Render module tiles
    modules = ["schedule", "verify_summary", "prep_questions"]
    for module_key in modules:
        state = get_module_state(user_id, product_key, module_key)
        st.markdown(
            '<article class="tile tile--md" style="padding: 10px;">',
            unsafe_allow_html=True,
        )
        render_module_tile(product_key, module_key, state)
        st.markdown("</article>", unsafe_allow_html=True)

    tiles_close()

    # Close section
    st.markdown("</section>", unsafe_allow_html=True)
