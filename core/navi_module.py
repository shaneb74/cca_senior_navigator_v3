"""
Module-level Navi component for GCP, Cost Planner, CCR, and other products.

Displays compact coaching panel with primary message, optional "Why this question?" 
explanation, and current plan summary (recommendation + care costs).
"""

import streamlit as st


def render_module_navi_coach(title_text: str, body_text: str, tip_text: str | None = None):
    """Compact module coach with title, body, and optional tip.
    
    Renders a minimal coaching panel with:
    - Title text with ✨ emoji (h4 weight via st.write)
    - One-sentence body text (≤120 chars)
    - Optional small tip (caption)
    
    Uses standard navi-panel-compact styling (blue left border, white card, rounded corners).
    This function renders and returns immediately, allowing the page to continue.
    """
    # Open container
    st.markdown("<div class='navi-panel-compact'>", unsafe_allow_html=True)
    
    # Title (h4 weight)
    st.write(f"✨ {title_text}")
    
    # One-sentence body
    st.write(body_text)
    
    # Optional small tip
    if tip_text:
        st.caption(tip_text)
    
    # Close container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Function completes and returns control to caller
    print("[NAVI_MODULE] rendered; continuing page content")
