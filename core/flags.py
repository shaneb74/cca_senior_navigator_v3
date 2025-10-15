"""
Centralized Flag Registry and Aggregation

This module defines ALL valid flags that can be set by products/modules.
It serves as the single source of truth for flag definitions and validation.

Flags drive:
- Additional Services personalization
- Navi guidance and recommendations
- Cost adjustments in Cost Planner
- Resource routing (Learning Center, Partners)

IMPORTANT: All flags must be registered in FLAG_REGISTRY below.
If a module tries to set an undefined flag, a validation warning will appear.
"""

from typing import Dict, List, Set, Optional
import streamlit as st


# ==============================================================================
# CENTRAL FLAG REGISTRY
# ==============================================================================
# This is the authoritative list of ALL valid flags in the system.
# Source: Extracted from products/gcp_v4/modules/care_recommendation/module.json
# Last Updated: 2025-10-14
#
# RULE: Any flag set by a module MUST exist in this registry.
# RULE: Flags should be descriptive snake_case names (e.g., "falls_multiple")
# ==============================================================================

FLAG_REGISTRY: Dict[str, Dict[str, str]] = {
    # COGNITIVE & MEMORY FLAGS
    "mild_cognitive_decline": {
        "category": "cognitive",
        "severity": "low",
        "description": "Occasional forgetfulness or mild memory issues",
    },
    "moderate_cognitive_decline": {
        "category": "cognitive",
        "severity": "moderate",
        "description": "Moderate memory or thinking difficulties",
    },
    "severe_cognitive_risk": {
        "category": "cognitive",
        "severity": "high",
        "description": "Severe memory issues, dementia, or Alzheimer's diagnosis",
    },
    
    # FALL & SAFETY FLAGS
    "moderate_safety_concern": {
        "category": "safety",
        "severity": "moderate",
        "description": "One fall in past year or behavioral safety concerns",
    },
    "high_safety_concern": {
        "category": "safety",
        "severity": "high",
        "description": "Multiple falls or significant safety risks",
    },
    "falls_multiple": {
        "category": "safety",
        "severity": "high",
        "description": "Multiple falls in the past year",
    },
    
    # MOBILITY FLAGS
    "moderate_mobility": {
        "category": "mobility",
        "severity": "moderate",
        "description": "Uses cane or walker for mobility",
    },
    "high_mobility_dependence": {
        "category": "mobility",
        "severity": "high",
        "description": "Wheelchair-bound or bedbound",
    },
    
    # DEPENDENCE & ADL FLAGS
    "moderate_dependence": {
        "category": "adl",
        "severity": "moderate",
        "description": "Needs regular assistance with daily activities",
    },
    "high_dependence": {
        "category": "adl",
        "severity": "high",
        "description": "Needs extensive full-time support with ADLs",
    },
    "veteran_aanda_risk": {
        "category": "adl",
        "severity": "moderate",
        "description": "Veteran with Aid & Attendance benefit eligibility indicators",
    },
    
    # MENTAL HEALTH FLAGS
    "moderate_risk": {
        "category": "mental_health",
        "severity": "moderate",
        "description": "Emotional ups and downs, occasionally feeling down",
    },
    "high_risk": {
        "category": "mental_health",
        "severity": "high",
        "description": "Frequently feeling down or depressed",
    },
    "mental_health_concern": {
        "category": "mental_health",
        "severity": "high",
        "description": "Significant mental health concerns requiring attention",
    },
    
    # CHRONIC CONDITION FLAGS
    "chronic_present": {
        "category": "health",
        "severity": "moderate",
        "description": "One or more chronic health conditions present",
    },
    
    # SUPPORT SYSTEM FLAGS
    "no_support": {
        "category": "caregiver",
        "severity": "high",
        "description": "No regular caregiver support available",
    },
    "limited_support": {
        "category": "caregiver",
        "severity": "moderate",
        "description": "Limited caregiver support (1-3 hours/day)",
    },
    
    # GEOGRAPHIC FLAGS
    "low_access": {
        "category": "geographic",
        "severity": "low",
        "description": "Somewhat isolated location with limited service access",
    },
    "very_low_access": {
        "category": "geographic",
        "severity": "moderate",
        "description": "Very isolated location with minimal service access",
    },
    "geo_isolated": {
        "category": "geographic",
        "severity": "high",
        "description": "Geographic isolation requiring special accommodation",
    },
}

# Quick lookup set for validation
VALID_FLAGS: Set[str] = set(FLAG_REGISTRY.keys())


def get_flag_info(flag_id: str) -> Optional[Dict[str, str]]:
    """Get metadata for a specific flag.
    
    Args:
        flag_id: Flag identifier (e.g., "falls_multiple")
    
    Returns:
        Dict with category, severity, description or None if not found
    """
    return FLAG_REGISTRY.get(flag_id)


def validate_flags(flags: List[str], module_name: str = "unknown") -> List[str]:
    """Validate that all flags are registered in FLAG_REGISTRY.
    
    Args:
        flags: List of flag IDs to validate
        module_name: Name of module setting these flags (for error messages)
    
    Returns:
        List of invalid flag IDs (empty if all valid)
    """
    invalid = []
    for flag in flags:
        if flag not in VALID_FLAGS:
            invalid.append(flag)
            print(f"⚠️  WARNING: Module '{module_name}' tried to set undefined flag: '{flag}'")
            print(f"    Valid flags must be registered in core/flags.py FLAG_REGISTRY")
    
    return invalid


def get_flags_by_category(category: str) -> List[str]:
    """Get all flag IDs in a specific category.
    
    Args:
        category: One of: cognitive, safety, mobility, adl, mental_health, 
                  health, caregiver, geographic
    
    Returns:
        List of flag IDs in that category
    """
    return [
        flag_id 
        for flag_id, info in FLAG_REGISTRY.items() 
        if info["category"] == category
    ]


def get_flags_by_severity(severity: str) -> List[str]:
    """Get all flag IDs at a specific severity level.
    
    Args:
        severity: One of: low, moderate, high
    
    Returns:
        List of flag IDs at that severity
    """
    return [
        flag_id 
        for flag_id, info in FLAG_REGISTRY.items() 
        if info["severity"] == severity
    ]


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
            # Handle both dict and list of dicts
            if isinstance(care_rec.flags, dict):
                flags.update(care_rec.flags)
            elif isinstance(care_rec.flags, list):
                # Merge list of dicts into single dict
                for flag_dict in care_rec.flags:
                    if isinstance(flag_dict, dict):
                        flags.update(flag_dict)
    except:
        pass
    
    # Aggregate from Cost Planner (financial profile)
    try:
        financial = MCIP.get_financial_profile()
        if financial and hasattr(financial, 'flags') and financial.flags:
            # Handle both dict and list of dicts
            if isinstance(financial.flags, dict):
                flags.update(financial.flags)
            elif isinstance(financial.flags, list):
                # Merge list of dicts into single dict
                for flag_dict in financial.flags:
                    if isinstance(flag_dict, dict):
                        flags.update(flag_dict)
    except:
        pass
    
    # Aggregate from PFMA (appointment)
    try:
        appointment = MCIP.get_advisor_appointment()
        if appointment and hasattr(appointment, 'flags') and appointment.flags:
            # Handle both dict and list of dicts
            if isinstance(appointment.flags, dict):
                flags.update(appointment.flags)
            elif isinstance(appointment.flags, list):
                # Merge list of dicts into single dict
                for flag_dict in appointment.flags:
                    if isinstance(flag_dict, dict):
                        flags.update(flag_dict)
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
    "FLAG_REGISTRY",
    "VALID_FLAGS",
    "get_flag_info",
    "validate_flags",
    "get_flags_by_category",
    "get_flags_by_severity",
    "get_all_flags",
    "get_flag",
    "has_any_flags",
    "has_all_flags",
]
