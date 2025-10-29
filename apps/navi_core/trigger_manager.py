"""
Trigger Manager - Smart display rules for contextual guidance.

Part of Phase 5.1: Smart Triggers Layer
Decides WHEN guidance appears based on behavioral rules and user context.
"""

import streamlit as st
import yaml
import time
from pathlib import Path
from typing import Optional


# Path to trigger configuration file
TRIGGER_FILE = Path(__file__).parent / "config" / "triggers.yaml"


def load_triggers() -> dict:
    """
    Load trigger rules from YAML configuration file.
    
    Returns:
        Dictionary mapping pages → trigger rules
        
    Raises:
        FileNotFoundError: If triggers.yaml doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    if not TRIGGER_FILE.exists():
        raise FileNotFoundError(f"Trigger config not found: {TRIGGER_FILE}")
    
    with open(TRIGGER_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def should_show(page: str, user_stage: Optional[str] = None) -> bool:
    """
    Evaluate whether guidance for a page should be displayed.
    
    Applies multiple rule types in order:
    1. show_once_per_session: Hide after first display
    2. cool_down_seconds: Throttle repeated displays
    3. stage_allowed: Show only for specific journey stages
    
    Args:
        page: Page name to check rules for
        user_stage: Current journey stage (optional, reads from session if None)
        
    Returns:
        True if guidance should be shown, False otherwise
        
    Example:
        >>> should_show("Welcome")
        True
        >>> should_show("Welcome")  # Second call
        False  # (if show_once_per_session is True)
    """
    rules = load_triggers()
    rule = rules.get(page, rules.get("Default", {}))
    
    # Rule 1: show_once_per_session
    if rule.get("show_once_per_session", True):
        seen_pages = st.session_state.get("_guidance_seen_pages", set())
        if page in seen_pages:
            return False
        # Mark as seen
        seen_pages = seen_pages.copy()  # Create new set to trigger session_state update
        seen_pages.add(page)
        st.session_state["_guidance_seen_pages"] = seen_pages
    
    # Rule 2: cool_down_seconds
    cooldown = rule.get("cool_down_seconds", 0)
    if cooldown > 0:
        last_time = st.session_state.get("_guidance_last_time", 0)
        current_time = time.time()
        if (current_time - last_time) < cooldown:
            return False
        st.session_state["_guidance_last_time"] = current_time
    
    # Rule 3: stage_allowed (conditional based on journey stage)
    stage_rules = rule.get("stage_allowed", [])
    if stage_rules:
        # Get current stage from parameter or session
        if user_stage is None:
            # Try to get from user profile in session
            profile = st.session_state.get("user_profile")
            if profile:
                user_stage = getattr(profile, "stage", "Awareness")
            else:
                user_stage = "Awareness"  # Default stage
        
        if user_stage not in stage_rules:
            return False
    
    return True


def reset_triggers() -> None:
    """
    Reset all trigger state (for testing or new session).
    
    Clears:
    - Seen pages tracking
    - Last display timestamp
    """
    if "_guidance_seen_pages" in st.session_state:
        del st.session_state["_guidance_seen_pages"]
    if "_guidance_last_time" in st.session_state:
        del st.session_state["_guidance_last_time"]


def get_trigger_stats() -> dict:
    """
    Get current trigger state for debugging/analytics.
    
    Returns:
        Dictionary with seen_pages set and last_time timestamp
    """
    return {
        "seen_pages": st.session_state.get("_guidance_seen_pages", set()),
        "last_time": st.session_state.get("_guidance_last_time", 0),
    }
