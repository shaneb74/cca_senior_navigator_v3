"""
Central name helpers for robust name handling across all pages and reruns.
"""

from typing import Optional
import streamlit as st


def set_person_name(name: str) -> None:
    """Set the person's name across all legacy keys and profile.
    
    Args:
        name: The person's name (empty string to clear)
    """
    name = str(name).strip() if name else ""
    
    if name:
        # Set name in all legacy locations for backward compatibility
        st.session_state["person_a_name"] = name
        st.session_state["person_name"] = name
        st.session_state["planning_for_name"] = name
        
        # Also set in profile structure
        if "profile" not in st.session_state:
            st.session_state["profile"] = {}
        st.session_state["profile"]["person_name"] = name
    else:
        # Clear all name-related keys
        st.session_state.pop("person_a_name", None)
        st.session_state.pop("person_name", None)
        st.session_state.pop("planning_for_name", None)
        
        # Clear profile name
        if "profile" in st.session_state and isinstance(st.session_state["profile"], dict):
            st.session_state["profile"].pop("person_name", None)


def get_person_name() -> str:
    """Get the person's name from session state (priority order).
    
    Returns:
        The person's name or empty string if not set
    """
    # Check direct keys first (highest priority)
    name_keys = ["person_a_name", "person_name", "planning_for_name"]
    for key in name_keys:
        name = st.session_state.get(key)
        if name and str(name).strip():
            return str(name).strip()
    
    # Check nested structures
    # Check profile.person_name
    profile = st.session_state.get("profile", {})
    if isinstance(profile, dict):
        profile_name = profile.get("person_name")
        if profile_name and str(profile_name).strip():
            return str(profile_name).strip()
    
    # Check gcp.person_a_name  
    gcp_data = st.session_state.get("gcp", {})
    if isinstance(gcp_data, dict):
        gcp_name = gcp_data.get("person_a_name")
        if gcp_name and str(gcp_name).strip():
            return str(gcp_name).strip()
    
    return ""


def clear_person_name() -> None:
    """Clear the person's name from all locations.
    
    Convenience function equivalent to set_person_name("").
    """
    set_person_name("")

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


def get_person_name() -> Optional[str]:
    """Read person name in priority order: person_a_name, person_name, planning_for_name, profile.person_name.
    
    Returns:
        The person's name if found, None otherwise
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
    
    return None