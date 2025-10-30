"""
Context Manager - Tracks active page for contextual guidance.

Part of Phase 5: Contextual Guidance Layer
Stores current page context in session_state for use by guidance_manager.

Phase 5A enhancements:
- get_phase_tone() for journey phase-aware NAVI tone adjustments
"""

import streamlit as st
from core.journeys import get_current_journey


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


def get_phase_tone() -> dict:
    """
    Get phase-aware NAVI tone adjustments based on journey stage.
    
    Phase 5A enhancement: Returns tone guidance for NAVI dialogue based on
    current journey phase (discovery/planning/post_planning).
    
    Returns:
        Dictionary with tone, emphasis, and example_phrases
        
    Example:
        >>> get_phase_tone()
        {
            'tone': 'encouraging',
            'emphasis': 'orientation',
            'example_phrases': ['Let me help you understand...', ...]
        }
    """
    journey_stage = get_current_journey()
    
    if journey_stage == "discovery":
        return {
            "tone": "encouraging",
            "emphasis": "orientation",
            "example_phrases": [
                "Let me help you understand...",
                "We'll take this step by step together.",
                "I'm here to guide you through this process."
            ]
        }
    elif journey_stage == "planning":
        return {
            "tone": "helpful",
            "emphasis": "decision_support",
            "example_phrases": [
                "Let's explore your options together.",
                "Here's what I recommend considering...",
                "This information will help you make informed decisions."
            ]
        }
    else:  # post_planning
        return {
            "tone": "supportive",
            "emphasis": "implementation",
            "example_phrases": [
                "You're making great progress!",
                "Let me help you with the next steps...",
                "I'm here to support you through this transition."
            ]
        }
