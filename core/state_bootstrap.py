"""
Early rehydration for name state from snapshots.
"""

from typing import Optional

import streamlit as st
from core.state_name import set_person_name


def rehydrate_name_from_snapshot(snapshot: Optional[dict]) -> None:
    """If the snapshot contains any name, call set_person_name to restore it.
    
    Args:
        snapshot: Dictionary that may contain name data from previous session
    """
    if not snapshot or not isinstance(snapshot, dict):
        return
    
    # Check direct keys first
    name_keys = ["person_a_name", "person_name", "planning_for_name"]
    for key in name_keys:
        name = snapshot.get(key)
        if name and str(name).strip():
            set_person_name(str(name).strip())
            return
    
    # Check nested structures
    # Check gcp.person_a_name
    gcp_data = snapshot.get("gcp", {})
    if isinstance(gcp_data, dict):
        gcp_name = gcp_data.get("person_a_name")
        if gcp_name and str(gcp_name).strip():
            set_person_name(str(gcp_name).strip())
            return
    
    # Check profile.person_name
    profile_data = snapshot.get("profile", {})
    if isinstance(profile_data, dict):
        profile_name = profile_data.get("person_name")
        if profile_name and str(profile_name).strip():
            set_person_name(str(profile_name).strip())
            return