"""
Household Dual Cost Aggregation

Computes combined costs for households with multiple care plans.
First-pass implementation provides household total and 50/50 split.

Future enhancements:
- Per-person facility vs in-home scenarios
- Shared home carry costs
- Medicare/Medicaid coordination
- Income-based split calculations
"""

import streamlit as st
from typing import Dict, Optional
from core.household import get_careplan_for, ensure_household_state


def compute_household_total(st) -> Dict:
    """Compute household total cost and split for dual care plans.
    
    Reads:
    - Primary and partner CarePlans
    - cost.inputs (zip, keep_home, owner_tenant, hours)
    - Uses existing cost calculation utilities
    
    Returns:
        Dict with:
        - primary_total: float
        - partner_total: float (0.0 if no partner or zero hours)
        - home_carry: float (shared if keeping home)
        - household_total: float
        - split: {"primary": total/2, "partner": total/2}
    """
    # Get household and persons
    try:
        hh = ensure_household_state(st)
    except Exception:
        hh = None
    
    primary_id = st.session_state.get("person.primary_id")
    partner_id = st.session_state.get("person.partner_id")
    
    # Get CarePlans
    cp_primary = get_careplan_for(st, primary_id) if primary_id else None
    cp_partner = get_careplan_for(st, partner_id) if partner_id else None
    
    # Get cost inputs
    inputs = st.session_state.get("cost.inputs", {})
    zip_code = inputs.get("zip") or (hh.zip if hh else None)
    keep_home = inputs.get("keep_home", False)
    owner_tenant = inputs.get("owner_tenant", "unknown")
    hours_band = inputs.get("hours")
    
    # Compute primary cost
    primary_total = 0.0
    if cp_primary:
        # Use existing cost calculation (placeholder for now)
        # In real implementation, call products/cost_planner_v2/utils/cost_calculator.py
        primary_total = _estimate_person_cost(cp_primary, zip_code, hours_band)
    
    # Compute partner cost
    partner_total = 0.0
    if cp_partner:
        partner_hours = cp_partner.hours_user or cp_partner.hours_suggested
        partner_total = _estimate_person_cost(cp_partner, zip_code, partner_hours)
    
    # Compute home carry cost (shared if keeping home)
    home_carry = 0.0
    if keep_home:
        # Use existing home cost calculation
        # Placeholder: $2000/month for homeowner, $1500 for tenant
        if owner_tenant == "owner":
            home_carry = 2000.0
        elif owner_tenant == "tenant":
            home_carry = 1500.0
    
    # Household total
    household_total = primary_total + partner_total + home_carry
    
    # 50/50 split
    split_amount = household_total / 2.0
    
    return {
        "primary_total": primary_total,
        "partner_total": partner_total,
        "home_carry": home_carry,
        "household_total": household_total,
        "split": {
            "primary": split_amount,
            "partner": split_amount
        },
        "has_partner_plan": bool(cp_partner)
    }


def _estimate_person_cost(cp, zip_code: Optional[str], hours: Optional[str]) -> float:
    """Estimate monthly cost for a person's care plan.
    
    Placeholder implementation - in production, would call
    products/cost_planner_v2/utils/cost_calculator.py
    
    Args:
        cp: CarePlan object
        zip_code: ZIP code for regional pricing
        hours: Hours band (e.g., "4-8h", "24h")
        
    Returns:
        Estimated monthly cost
    """
    tier = cp.final_tier or cp.det_tier
    
    # Placeholder facility costs by tier
    facility_costs = {
        "no_care_needed": 0.0,
        "in_home": 0.0,  # Handled by hours calculation
        "assisted_living": 4500.0,
        "memory_care": 6500.0,
        "memory_care_high_acuity": 8500.0
    }
    
    # Placeholder in-home costs by hours
    hourly_costs = {
        "<1h": 500.0,
        "1-3h": 1500.0,
        "4-8h": 3500.0,
        "24h": 8000.0
    }
    
    if tier in facility_costs and tier not in {"no_care_needed", "in_home"}:
        return facility_costs.get(tier, 0.0)
    
    # In-home or hours-based
    if hours:
        return hourly_costs.get(hours, 0.0)
    
    # Default to hours from CarePlan
    hours_band = cp.hours_user or cp.hours_suggested
    return hourly_costs.get(hours_band, 0.0)
