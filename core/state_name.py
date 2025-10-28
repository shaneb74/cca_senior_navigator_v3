"""
Central name helpers for robust name handling across all pages and reruns.
"""

import streamlit as st


def set_person_name(name: str) -> None:
    """Write the trimmed name to all legacy keys and mirror into profile.person_name.
    
    Args:
        name: The person's name to store across all name keys
    """
    if not name:
        return
    
    trimmed_name = name.strip()
    if not trimmed_name:
        return
    
    # Write to all legacy keys
    st.session_state["person_a_name"] = trimmed_name
    st.session_state["person_name"] = trimmed_name
    st.session_state["planning_for_name"] = trimmed_name
    
    # Mirror into profile.person_name
    if "profile" not in st.session_state:
        st.session_state["profile"] = {}
    st.session_state["profile"]["person_name"] = trimmed_name


def get_person_name() -> str:
    """Read person name in priority order: person_a_name, person_name, planning_for_name, profile.person_name.
    
    Returns:
        The person's name or empty string if not set
    """
    # Priority order: person_a_name, person_name, planning_for_name, profile.person_name
    name_keys = ["person_a_name", "person_name", "planning_for_name"]
    
    # Check direct session state keys first
    for key in name_keys:
        name = st.session_state.get(key)
        if name and str(name).strip():
            return str(name).strip()
    
    # Check profile.person_name
    profile = st.session_state.get("profile", {})
    if isinstance(profile, dict):
        profile_name = profile.get("person_name")
        if profile_name and str(profile_name).strip():
            return str(profile_name).strip()
    
    return ""


def clear_person_name() -> None:
    """Clear the person's name from all locations.
    
    Convenience function equivalent to set_person_name("").
    """
    set_person_name("")