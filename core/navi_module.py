"""
Module-level Navi component for GCP, Cost Planner, CCR, and other products.

Displays compact coaching panel with primary message, optional "Why this question?" 
explanation, and current plan summary (recommendation + care costs).
"""

import streamlit as st


def render_module_navi_coach(primary_msg: str, why_text: str | None = None):
    """Compact module coach with optional 'Why this question?' slot.
    
    Renders a minimal coaching panel with:
    - Primary coach message (≤120 chars)
    - Optional "Why this question?" explanation
    
    No plan summary or additional content - keep it focused and clean.
    This function renders and returns immediately, allowing the page to continue.
    """
    st.markdown("<div class='navi-panel-compact'>", unsafe_allow_html=True)
    st.write(f"✨ {primary_msg}")

    # Why this question? (render only when provided by caller)
    if why_text:
        st.markdown("**[?] Why this question?**")
        st.caption(why_text)

    st.markdown("</div>", unsafe_allow_html=True)
    
    # Function completes and returns control to caller
    print("[NAVI_MODULE] rendered; continuing page content")
