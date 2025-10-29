"""
Context Manager - Tracks active page for contextual guidance.

Part of Phase 5: Contextual Guidance Layer
Stores current page context in session_state for use by guidance_manager.
"""

import streamlit as st


def update_context(page_name: str) -> str:
    """
    Store the current page context in session state.
    
    Args:
        page_name: Name of the current active page
        
    Returns:
        The page_name that was stored
        
    Example:
        >>> update_context("Care Preferences")
        'Care Preferences'
    """
    st.session_state["current_page"] = page_name
    return page_name


def get_current_context() -> str:
    """
    Retrieve the current active page name from session state.
    
    Returns:
        Current page name, defaults to "Welcome" if not set
        
    Example:
        >>> get_current_context()
        'Welcome'
    """
    return st.session_state.get("current_page", "Welcome")
