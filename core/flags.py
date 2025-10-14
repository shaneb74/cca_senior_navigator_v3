"""
Centralized Flag Aggregation

Single source of truth for all flags across products and modules.
Navi uses this to drive Additional Services and dynamic Q&A.
"""

from typing import Dict
import streamlit as st


def get_all_flags() -> Dict[str, bool]:
    """Aggregate flags from all products and modules.
    
    This is the SINGLE accessor for flags in the system.
    Navi uses this to:
    - Recommend Additional Services
    - Generate dynamic suggested questions
    - Provide context-aware guidance
    
    Returns:
        Dict mapping flag names to boolean values
    """
    from core.mcip import MCIP
    
    flags = {}
    
    # Aggregate from GCP (care recommendation)
    try:
        care_rec = MCIP.get_care_recommendation()
        if care_rec and hasattr(care_rec, 'flags') and care_rec.flags:
            flags.update(care_rec.flags)
    except:
        pass
    
    # Aggregate from Cost Planner (financial profile)
    try:
        financial = MCIP.get_financial_profile()
        if financial and hasattr(financial, 'flags') and financial.flags:
            flags.update(financial.flags)
    except:
        pass
    
    # Aggregate from PFMA (appointment)
    try:
        appointment = MCIP.get_advisor_appointment()
        if appointment and hasattr(appointment, 'flags') and appointment.flags:
            flags.update(appointment.flags)
    except:
        pass
    
    # Aggregate from module states (if products expose flags via session state)
    # This allows modules to contribute flags even before publishing to MCIP
    for key in st.session_state:
        if key.endswith('_flags') and isinstance(st.session_state[key], dict):
            flags.update(st.session_state[key])
    
    return flags


def get_flag(flag_name: str, default: bool = False) -> bool:
    """Get a single flag value.
    
    Args:
        flag_name: Name of the flag to retrieve
        default: Default value if flag not found
    
    Returns:
        Flag value or default
    """
    flags = get_all_flags()
    return flags.get(flag_name, default)


def has_any_flags(flag_names: list) -> bool:
    """Check if any of the given flags are True.
    
    Args:
        flag_names: List of flag names to check
    
    Returns:
        True if any flag is True
    """
    flags = get_all_flags()
    return any(flags.get(flag_name, False) for flag_name in flag_names)


def has_all_flags(flag_names: list) -> bool:
    """Check if all of the given flags are True.
    
    Args:
        flag_names: List of flag names to check
    
    Returns:
        True if all flags are True
    """
    flags = get_all_flags()
    return all(flags.get(flag_name, False) for flag_name in flag_names)


__all__ = [
    "get_all_flags",
    "get_flag",
    "has_any_flags",
    "has_all_flags"
]
