"""
Cost Planner - Cost Estimation Engine

Provides quick estimates and detailed cost calculations for different care types,
applying modifiers based on health/safety flags from the Guided Care Plan.
"""

from typing import Dict, List, Any, Optional
import streamlit as st


# ==============================================================================
# NATIONAL AVERAGE COSTS (2025 estimates)
# ==============================================================================

# Base monthly costs by care type (national median)
CARE_TYPE_COSTS = {
    "no_care": {
        "label": "No Care Needed",
        "base_cost": 0,
        "description": "Living independently with no regular care services",
    },
    "in_home": {
        "label": "In-Home Care",
        "base_cost": 4500,  # ~20 hrs/week at $25/hr
        "description": "Part-time in-home care assistance (20 hrs/week)",
    },
    "assisted_living": {
        "label": "Assisted Living",
        "base_cost": 5500,
        "description": "Residential community with 24/7 support and activities",
    },
    "memory_care": {
        "label": "Memory Care",
        "base_cost": 7500,
        "description": "Specialized care for cognitive impairment with enhanced security",
    },
    "memory_care_high": {
        "label": "Memory Care (High Acuity)",
        "base_cost": 10500,
        "description": "Intensive memory care with skilled nursing support",
    },
}


# Map GCP care recommendation tiers to cost planner care types
TIER_TO_CARE_TYPE = {
    "Independent / In-Home": "no_care",
    "In-Home Care": "in_home",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "High-Acuity Memory Care": "memory_care_high",
    "Skilled Nursing": "memory_care_high",  # Same tier
}


# Cost modifiers based on health/safety flags (percentage adjustments)
FLAG_MODIFIERS = {
    "fall_risk": {
        "adjustment": 0.15,  # +15%
        "reason": "Fall prevention monitoring and safety equipment",
        "applies_to": ["in_home", "assisted_living", "memory_care", "memory_care_high"],
    },
    "cognitive_risk": {
        "adjustment": 0.20,  # +20%
        "reason": "Enhanced supervision and specialized cognitive care",
        "applies_to": ["in_home", "assisted_living", "memory_care", "memory_care_high"],
    },
    "meds_management_needed": {
        "adjustment": 0.10,  # +10%
        "reason": "Medication management and adherence monitoring",
        "applies_to": ["in_home", "assisted_living", "memory_care", "memory_care_high"],
    },
    "isolation_risk": {
        "adjustment": 0.05,  # +5%
        "reason": "Additional companionship and social engagement services",
        "applies_to": ["in_home", "no_care"],
    },
    "mobility_impaired": {
        "adjustment": 0.12,  # +12%
        "reason": "Mobility assistance and adaptive equipment",
        "applies_to": ["in_home", "assisted_living", "memory_care", "memory_care_high"],
    },
    "emotional_support_risk": {
        "adjustment": 0.08,  # +8%
        "reason": "Wellness counseling and emotional support services",
        "applies_to": ["in_home", "no_care"],
    },
}


# ==============================================================================
# COST CALCULATION ENGINE
# ==============================================================================

def get_gcp_recommendation() -> Optional[str]:
    """Extract care recommendation from GCP handoff data."""
    handoff = st.session_state.get("handoff", {}).get("gcp", {})
    return handoff.get("recommendation")


def get_gcp_flags() -> Dict[str, Any]:
    """Extract all flags from GCP handoff data."""
    handoff = st.session_state.get("handoff", {}).get("gcp", {})
    return handoff.get("flags", {})


def map_recommendation_to_care_type(recommendation: str) -> str:
    """Convert GCP recommendation to Cost Planner care type key."""
    return TIER_TO_CARE_TYPE.get(recommendation, "no_care")


def calculate_cost_estimate(
    care_type: str,
    flags: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate cost estimate for a given care type with flag-based modifiers.
    
    Args:
        care_type: One of the CARE_TYPE_COSTS keys
        flags: Dictionary of active flags (from GCP or manually set)
    
    Returns:
        Dictionary with base_cost, modifiers, total_cost, and breakdown
    """
    if care_type not in CARE_TYPE_COSTS:
        raise ValueError(f"Invalid care type: {care_type}")
    
    care_info = CARE_TYPE_COSTS[care_type]
    base_cost = care_info["base_cost"]
    
    # Gather applicable flags
    if flags is None:
        flags = get_gcp_flags()
    
    modifiers = []
    total_adjustment = 0.0
    
    for flag_key, flag_config in FLAG_MODIFIERS.items():
        # Check if flag exists and is truthy
        if flags.get(flag_key):
            # Check if this modifier applies to this care type
            if care_type in flag_config["applies_to"]:
                adjustment = flag_config["adjustment"]
                total_adjustment += adjustment
                modifiers.append({
                    "flag": flag_key,
                    "reason": flag_config["reason"],
                    "adjustment_pct": adjustment * 100,
                    "adjustment_amount": base_cost * adjustment,
                })
    
    modifier_total = base_cost * total_adjustment
    total_cost = base_cost + modifier_total
    
    return {
        "care_type": care_type,
        "care_label": care_info["label"],
        "care_description": care_info["description"],
        "base_cost": base_cost,
        "modifiers": modifiers,
        "modifier_total": modifier_total,
        "total_adjustment_pct": total_adjustment * 100,
        "total_cost": total_cost,
    }


def format_currency(amount: float) -> str:
    """Format number as US currency."""
    return f"${amount:,.0f}"


def get_cost_comparison_table(flags: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Generate a comparison table of all care types with cost estimates.
    
    Returns:
        List of dictionaries, one per care type, sorted by cost
    """
    if flags is None:
        flags = get_gcp_flags()
    
    results = []
    for care_type in CARE_TYPE_COSTS.keys():
        estimate = calculate_cost_estimate(care_type, flags)
        results.append(estimate)
    
    # Sort by total cost
    results.sort(key=lambda x: x["total_cost"])
    
    return results


def render_cost_breakdown(estimate: Dict[str, Any], show_details: bool = True) -> None:
    """
    Render a formatted cost breakdown in Streamlit.
    
    Args:
        estimate: Result from calculate_cost_estimate()
        show_details: Whether to show modifier details
    """
    st.markdown(f"### {estimate['care_label']}")
    st.caption(estimate['care_description'])
    
    # Base cost
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("**Base monthly cost:**")
    with col2:
        st.write(f"**{format_currency(estimate['base_cost'])}**")
    
    # Modifiers
    if estimate['modifiers'] and show_details:
        st.markdown("#### Cost Adjustments")
        for mod in estimate['modifiers']:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {mod['reason']}")
                st.caption(f"({mod['adjustment_pct']:.0f}% increase)")
            with col2:
                st.write(f"+{format_currency(mod['adjustment_amount'])}")
    
    # Total
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("**Estimated monthly total:**")
    with col2:
        st.markdown(f"### {format_currency(estimate['total_cost'])}")
    
    # Disclaimer
    st.caption(
        "💡 **Note:** Costs vary significantly by location, provider, and individual needs. "
        "This estimate uses national averages and should be used for planning purposes only."
    )


# ==============================================================================
# QUICK ESTIMATE HELPERS
# ==============================================================================

def get_recommended_care_type() -> str:
    """Get the care type recommended by GCP, or default to no_care."""
    recommendation = get_gcp_recommendation()
    if recommendation:
        return map_recommendation_to_care_type(recommendation)
    return "no_care"


def get_care_type_options() -> List[Dict[str, str]]:
    """
    Get list of care type options for selection UI.
    
    Returns:
        List of dicts with 'value', 'label', and 'description'
    """
    return [
        {
            "value": key,
            "label": info["label"],
            "description": info["description"],
        }
        for key, info in CARE_TYPE_COSTS.items()
    ]
