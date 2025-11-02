"""
Cached computation engine for Cost Planner v2.

Persistent, parameterized caching of heavy calculations keyed by inputs.
Prevents recomputation on reruns and route changes when inputs unchanged.
"""

from __future__ import annotations

import streamlit as st


@st.cache_data(ttl=1800, show_spinner=False)
def compute_totals_cached(
    assessment: str,
    *,
    zip_code: str,
    hours_per_day: float = 8.0,
    home_carry: float = 0.0,
    keep_home: bool = False,
) -> dict:
    """Cache heavy totals computation keyed by all inputs.
    
    Cached for 30 minutes. Returns total + segments for rendering.
    
    Args:
        assessment: Assessment key ("home", "al", "mc")
        zip_code: ZIP code for regional pricing
        hours_per_day: Hours of care per day (home only)
        home_carry: Monthly home expense override
        keep_home: Whether keeping home (facility only)
        
    Returns:
        Dict with {"total": float, "segments": dict}
    """
    from products.cost_planner_v2.comparison_calcs import (
        calculate_facility_scenario,
        calculate_inhome_scenario,
    )
    
    # Compute breakdown based on assessment type
    if assessment == "home":
        breakdown = calculate_inhome_scenario(
            zip_code=zip_code,
            hours_per_day=hours_per_day,
            home_carry_override=home_carry or None,
        )
    elif assessment in ("al", "mc"):
        care_type = "assisted_living" if assessment == "al" else "memory_care"
        breakdown = calculate_facility_scenario(
            care_type=care_type,
            zip_code=zip_code,
            keep_home=keep_home,
            home_carry_override=home_carry or None,
        )
    else:
        return {"total": 0.0, "segments": {}}
    
    # Extract segments from breakdown
    segments = {}
    housing_amt = 0.0
    care_amt = 0.0
    home_carry_amt = 0.0
    
    for line in breakdown.lines:
        label_lower = line.label.lower()
        if not line.applied or line.value <= 0:
            continue
            
        if "home carry" in label_lower:
            home_carry_amt += line.value
        elif assessment == "home":
            # Home: all non-carry is care
            care_amt += line.value
        else:
            # Facility: base cost + regional = housing, rest is care
            if "base cost" in label_lower or "regional adjustment" in label_lower:
                housing_amt += line.value
            else:
                care_amt += line.value
    
    # Build segments dict
    if assessment == "home":
        if care_amt > 0:
            segments["Care Services"] = float(care_amt)
        if home_carry_amt > 0:
            segments["Home Carry"] = float(home_carry_amt)
    else:
        if housing_amt > 0:
            segments["Housing/Room"] = float(housing_amt)
        if care_amt > 0:
            segments["Care Services"] = float(care_amt)
        if home_carry_amt > 0:
            segments["Home Carry"] = float(home_carry_amt)
    
    return {
        "total": float(breakdown.monthly_total),
        "segments": segments,
    }
