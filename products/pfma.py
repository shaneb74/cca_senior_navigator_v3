import streamlit as st

from core.state import get_module_state, get_user_ctx
from core.ui import hub_section, render_module_tile, tiles_close, tiles_open


def render():
    ctx = get_user_ctx()
    user_id = ctx["auth"].get("user_id", "guest")
    product_key = "pfma"
    
    hub_section("Plan with My Advisor")
    tiles_open()

    # Render module tiles
    modules = ["schedule", "verify_summary", "prep_questions"]
    for module_key in modules:
        state = get_module_state(user_id, product_key, module_key)
        st.markdown('<article class="tile tile--md">', unsafe_allow_html=True)
        render_module_tile(product_key, module_key, state)
        st.markdown('</article>', unsafe_allow_html=True)

    tiles_close()
