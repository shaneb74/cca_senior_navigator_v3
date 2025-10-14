"""
Cost Planner - Regional Cost Estimation Engine (v2)

Provides quick estimates and detailed cost calculations for different care types with:
- Regional pricing based on ZIP code
- GCP recommendation integration
- Flag-based health/safety modifiers
"""

from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
import json
from pathlib import Path


# ==============================================================================
# CONFIGURATION LOADER
# ==============================================================================

def load_regional_config() -> Dict[str, Any]:
    """Load regional cost configuration from JSON file."""
    config_path = Path("config/regional_cost_config.json")
    with open(config_path, "r") as f:
        return json.load(f)


# Cache the config to avoid repeated file reads
@st.cache_data
def get_cost_config() -> Dict[str, Any]:
    return load_regional_config()


# ==============================================================================
# GCP INTEGRATION
# ==============================================================================

def get_gcp_recommendation() -> Optional[str]:
    """Extract care recommendation from GCP handoff data."""
    handoff = st.session_state.get("handoff", {}).get("gcp", {})
    return handoff.get("recommendation")


def get_gcp_recommendation_display() -> str:
    """Get formatted GCP recommendation for display."""
    rec = get_gcp_recommendation()
    return rec if rec else "your personalized care needs"


def get_gcp_flags() -> Dict[str, Any]:
    """Extract all flags from GCP handoff data."""
    handoff = st.session_state.get("handoff", {}).get("gcp", {})
    return handoff.get("flags", {})


# Map GCP care recommendation tiers to cost planner care types
TIER_TO_CARE_TYPE = {
    "No Care Needed": "no_care",
    "In-Home Care": "in_home_care",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "Memory Care — High Acuity": "memory_care_high_acuity",
}


def map_recommendation_to_care_type(recommendation: Optional[str]) -> str:
    """Convert GCP recommendation to Cost Planner care type key."""
    if not recommendation:
        return "no_care"
    return TIER_TO_CARE_TYPE.get(recommendation, "no_care")


def get_recommended_care_type() -> str:
    """Get the care type recommended by GCP, or default to no_care."""
    recommendation = get_gcp_recommendation()
    return map_recommendation_to_care_type(recommendation)


# ==============================================================================
# REGIONAL PRICING LOGIC
# ==============================================================================

def resolve_regional_multiplier(zip_code: Optional[str]) -> Tuple[float, str]:
    """
    Resolve regional cost multiplier based on ZIP code using priority order.
    
    Returns:
        (multiplier, match_type) where match_type describes how it was matched
    """
    config = get_cost_config()
    multipliers = config["zip_multipliers"]
    
    if not zip_code or len(zip_code) < 3:
        return (multipliers["default"], "default")
    
    # Normalize zip code
    zip5 = zip_code[:5]
    zip3 = zip_code[:3]
    
    # Determine if this is a WA ZIP (980-994)
    is_wa_zip = zip3.isdigit() and 980 <= int(zip3) <= 994
    
    # Resolution order per config
    resolution_order = config["rules"]["effective_multiplier_resolution_order"]
    
    for rule in resolution_order:
        if rule == "zip_exact_wa" and is_wa_zip:
            for entry in multipliers.get("by_zip_wa", []):
                if entry["zip"] == zip5:
                    return (entry["multiplier"], f"WA ZIP exact ({entry['notes']})")
        
        elif rule == "zip3_wa" and is_wa_zip:
            for entry in multipliers.get("by_zip3_wa", []):
                if entry["zip3"] == zip3:
                    return (entry["multiplier"], f"WA ZIP3 ({entry['notes']})")
        
        elif rule == "state_wa" and is_wa_zip:
            for entry in multipliers.get("by_state_wa", []):
                if entry["state"] == "WA":
                    return (entry["multiplier"], "WA state fallback")
        
        elif rule == "zip_exact" and not is_wa_zip:
            for entry in multipliers.get("by_zip", []):
                if entry["zip"] == zip5:
                    return (entry["multiplier"], f"ZIP exact ({entry.get('notes', '')})")
        
        elif rule == "zip3" and not is_wa_zip:
            for entry in multipliers.get("by_zip3", []):
                if entry["zip3"] == zip3:
                    return (entry["multiplier"], f"ZIP3 ({entry.get('notes', '')})")
        
        elif rule == "state" and not is_wa_zip:
            # Try to infer state from ZIP3 (simplified - would need full ZIP-to-state map)
            pass
        
        elif rule == "default":
            return (multipliers["default"], "national average")
    
    return (multipliers["default"], "national average")


# ==============================================================================
# COST CALCULATION ENGINE
# ==============================================================================

# Cost modifiers based on health/safety flags (percentage adjustments)
FLAG_MODIFIERS = {
    "fall_risk": {
        "adjustment": 0.15,  # +15%
        "reason": "Fall prevention monitoring and safety equipment",
        "applies_to": ["in_home_care", "assisted_living", "memory_care", "memory_care_high_acuity"],
    },
    "cognitive_risk": {
        "adjustment": 0.20,  # +20%
        "reason": "Enhanced supervision and specialized cognitive care",
        "applies_to": ["in_home_care", "assisted_living", "memory_care", "memory_care_high_acuity"],
    },
    "meds_management_needed": {
        "adjustment": 0.10,  # +10%
        "reason": "Medication management and adherence monitoring",
        "applies_to": ["in_home_care", "assisted_living", "memory_care", "memory_care_high_acuity"],
    },
    "isolation_risk": {
        "adjustment": 0.05,  # +5%
        "reason": "Additional companionship and social engagement services",
        "applies_to": ["in_home_care", "no_care"],
    },
    "mobility_impaired": {
        "adjustment": 0.12,  # +12%
        "reason": "Mobility assistance and adaptive equipment",
        "applies_to": ["in_home_care", "assisted_living", "memory_care", "memory_care_high_acuity"],
    },
    "emotional_support_risk": {
        "adjustment": 0.08,  # +8%
        "reason": "Wellness counseling and emotional support services",
        "applies_to": ["in_home_care", "no_care"],
    },
}


def calculate_cost_estimate(
    care_type: str,
    zip_code: Optional[str] = None,
    flags: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate cost estimate for a given care type with regional and flag-based modifiers.
    
    Args:
        care_type: One of the care type keys from config
        zip_code: ZIP code for regional pricing
        flags: Dictionary of active flags (from GCP or manually set)
    
    Returns:
        Dictionary with base_cost, regional_multiplier, modifiers, total_cost, and breakdown
    """
    config = get_cost_config()
    categories = config["categories"]
    
    if care_type not in categories:
        raise ValueError(f"Invalid care type: {care_type}. Must be one of {list(categories.keys())}")
    
    care_info = categories[care_type]
    base_cost = care_info["base_monthly_usd"]
    care_label = care_info["label"]
    
    # Get regional multiplier
    regional_multiplier, region_match = resolve_regional_multiplier(zip_code)
    regional_cost = base_cost * regional_multiplier
    
    # Gather applicable flags
    if flags is None:
        flags = get_gcp_flags()
    
    flag_adjustments = []
    total_flag_adjustment = 0.0
    
    for flag_key, flag_config in FLAG_MODIFIERS.items():
        # Check if flag exists and is truthy
        if flags.get(flag_key):
            # Check if this modifier applies to this care type
            if care_type in flag_config["applies_to"]:
                adjustment = flag_config["adjustment"]
                total_flag_adjustment += adjustment
                flag_adjustments.append({
                    "flag": flag_key,
                    "reason": flag_config["reason"],
                    "adjustment_pct": adjustment * 100,
                    "adjustment_amount": regional_cost * adjustment,
                })
    
    flag_modifier_total = regional_cost * total_flag_adjustment
    total_cost = regional_cost + flag_modifier_total
    
    return {
        "care_type": care_type,
        "care_label": care_label,
        "base_cost_national": base_cost,
        "regional_multiplier": regional_multiplier,
        "regional_match_type": region_match,
        "regional_cost": regional_cost,
        "flag_adjustments": flag_adjustments,
        "flag_modifier_total": flag_modifier_total,
        "total_flag_adjustment_pct": total_flag_adjustment * 100,
        "total_cost": total_cost,
        "zip_code": zip_code or "Not specified",
    }


def format_currency(amount: float) -> str:
    """Format number as US currency."""
    return f"${amount:,.0f}"


def render_cost_breakdown(estimate: Dict[str, Any], show_details: bool = True) -> None:
    """
    Render a formatted cost breakdown in Streamlit.
    
    Args:
        estimate: Result from calculate_cost_estimate()
        show_details: Whether to show detailed modifier breakdown
    """
    st.markdown(f"### {estimate['care_label']}")
    
    # Base cost
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("**Base monthly cost (national average):**")
    with col2:
        st.write(f"{format_currency(estimate['base_cost_national'])}")
    
    # Regional adjustment
    if estimate['regional_multiplier'] != 1.0:
        col1, col2 = st.columns([3, 1])
        with col1:
            regional_pct = (estimate['regional_multiplier'] - 1.0) * 100
            sign = "+" if regional_pct > 0 else ""
            st.write(f"**Regional adjustment** ({estimate['regional_match_type']})")
            st.caption(f"{sign}{regional_pct:.0f}% for ZIP: {estimate['zip_code']}")
        with col2:
            regional_diff = estimate['regional_cost'] - estimate['base_cost_national']
            sign = "+" if regional_diff > 0 else ""
            st.write(f"{sign}{format_currency(regional_diff)}")
    
    st.divider()
    
    # Regional subtotal
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("**Regional monthly cost:**")
    with col2:
        st.write(f"**{format_currency(estimate['regional_cost'])}**")
    
    # Flag-based modifiers
    if estimate['flag_adjustments'] and show_details:
        st.markdown("#### Additional Care Needs")
        for mod in estimate['flag_adjustments']:
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
        "💡 **Note:** Costs vary by provider, individual needs, and room type. "
        "This estimate combines regional pricing with your specific care needs. "
        "Use for planning purposes only."
    )


def get_care_type_options() -> List[Dict[str, str]]:
    """
    Get list of care type options for selection UI.
    
    Returns:
        List of dicts with 'value' and 'label'
    """
    config = get_cost_config()
    categories = config["categories"]
    
    return [
        {
            "value": key,
            "label": info["label"],
        }
        for key, info in categories.items()
    ]
