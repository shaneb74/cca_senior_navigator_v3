"""
Advisor Prep Utilities

Duck Badge System - tracks completion of prep sections with duck icons.
Mirrors the trivia badge system but for Advisor Prep sections.
"""

import streamlit as st

# Duck section mapping
DUCK_SECTIONS = {
    "personal": {"name": "Personal Info", "icon": "🦆"},
    "financial": {"name": "Financial Details", "icon": "🦆"},
    "housing": {"name": "Housing Preferences", "icon": "🦆"},
    "medical": {"name": "Medical & Care Needs", "icon": "🦆"},
}


def _initialize_duck_progress():
    """Initialize duck badge progress in session state if not exists."""
    if "product_tiles_v2" not in st.session_state:
        st.session_state["product_tiles_v2"] = {}

    if "advisor_prep" not in st.session_state["product_tiles_v2"]:
        st.session_state["product_tiles_v2"]["advisor_prep"] = {
            "ducks_earned": {},  # {section_key: {name, timestamp}}
            "progress": 0,  # 0-100
            "status": "not_started",
        }


def award_duck(section_key: str) -> bool:
    """
    Award a duck badge for completing a prep section.

    Args:
        section_key: One of 'personal', 'financial', 'housing', 'medical'

    Returns:
        True if this is a new duck (first time earning), False if already earned
    """
    _initialize_duck_progress()

    if section_key not in DUCK_SECTIONS:
        return False

    progress = st.session_state["product_tiles_v2"]["advisor_prep"]

    # Check if already earned
    if section_key in progress["ducks_earned"]:
        return False  # Already earned this duck

    # Award the duck
    from datetime import datetime

    progress["ducks_earned"][section_key] = {
        "name": DUCK_SECTIONS[section_key]["name"],
        "timestamp": datetime.now().isoformat(),
    }

    # Update progress percentage (25% per section)
    ducks_count = len(progress["ducks_earned"])
    progress["progress"] = ducks_count * 25

    # Update status
    if ducks_count == 0:
        progress["status"] = "not_started"
    elif ducks_count < 4:
        progress["status"] = "in_progress"
    else:
        progress["status"] = "complete"

    return True  # New duck earned!


def get_duck_badges() -> list[str]:
    """
    Get list of earned duck badges for display.

    Returns:
        List of badge strings (e.g., ['Personal Info 🦆', 'Financial Details 🦆'])
    """
    _initialize_duck_progress()

    progress = st.session_state["product_tiles_v2"]["advisor_prep"]
    ducks_earned = progress.get("ducks_earned", {})

    if not ducks_earned:
        return ["new"]  # No ducks earned yet

    # If all 4 ducks earned, show special "All Ducks in a Row" badge
    if len(ducks_earned) == 4:
        return ["All Ducks in a Row 🦆🦆🦆🦆"]

    # Otherwise, show earned duck names
    badges = []
    for section_key in ["personal", "financial", "housing", "medical"]:
        if section_key in ducks_earned:
            duck_info = ducks_earned[section_key]
            badges.append(f"{duck_info['name']} 🦆")

    return badges if badges else ["new"]


def get_duck_count() -> int:
    """
    Get count of earned ducks (0-4).

    Returns:
        Number of ducks earned
    """
    _initialize_duck_progress()

    progress = st.session_state["product_tiles_v2"]["advisor_prep"]
    return len(progress.get("ducks_earned", {}))


def is_all_ducks_complete() -> bool:
    """
    Check if all 4 ducks have been earned.

    Returns:
        True if all 4 sections complete
    """
    return get_duck_count() == 4


def get_duck_progress_text() -> str:
    """
    Get progress text for display (e.g., '2/4 Ducks').

    Returns:
        Formatted progress string
    """
    count = get_duck_count()
    return f"🦆 {count}/4 Ducks"
