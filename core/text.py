"""
Universal text personalization helper.

Provides a simple interface to apply name tokens to any user-visible string.
"""

import streamlit as st
from core.content_contract import build_token_context, interpolate


def personalize_text(value, session_state=None):
    """Apply name personalization to any text value.
    
    Args:
        value: String, list, or dict containing {NAME} or {NAME_POS} tokens
        session_state: Optional session state dict (defaults to st.session_state)
        
    Returns:
        Personalized text with tokens resolved to actual names or fallback terms
    """
    if not value:
        return value
    
    # Use provided session_state or default to Streamlit's session_state
    state = session_state if session_state is not None else st.session_state
    ctx = build_token_context(state, snapshot=None)
    return interpolate(value, ctx)