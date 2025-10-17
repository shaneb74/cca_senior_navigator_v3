"""
Advisor Prep Prefill Logic

Centralized prefill and derivation logic for Advisor Prep sections.
Uses existing data sources only - no new flags or persistence keys created.

Data Sources:
- Flag Manager: flags.active[] + provenance
- Conditions Registry: medical.conditions.chronic[]
- Cost Planner: tiles.cost_planner_v2.assessments.{income, assets}
- MCIP: Financial Profile contract
"""

from typing import Dict, Any, List, Optional, Tuple
import streamlit as st

import core.flag_manager as flag_manager
from core.mcip import MCIP


def get_financial_prefill() -> Dict[str, Any]:
    """
    Get prefill data for Financial Overview section.
    
    Returns:
        Dict with:
            monthly_income: float or None
            total_assets: float or None
            insurance_coverage: list or []
            primary_concern: str or None
            primary_concern_reason: str or None (provenance hint)
    """
    result = {
        "monthly_income": None,
        "total_assets": None,
        "insurance_coverage": [],
        "primary_concern": None,
        "primary_concern_reason": None
    }
    
    # Try to get from Financial Profile (MCIP contract)
    financial_profile = MCIP.get_financial_profile()
    
    if financial_profile:
        # Use gap and runway from Financial Profile for derivation
        gap = financial_profile.gap_amount
        runway = financial_profile.runway_months
        
        # Derive primary concern if obvious
        if gap > 500:  # Meaningful monthly gap
            result["primary_concern"] = "Affordability / Monthly gap"
            result["primary_concern_reason"] = f"Estimated gap: ${gap:,.0f}/month"
        elif runway > 0 and runway < 36:  # Less than 3 years runway
            result["primary_concern"] = "Limited runway / Asset depletion risk"
            result["primary_concern_reason"] = f"Estimated runway: {runway} months"
    
    # Try to get from Cost Planner assessments
    tiles = st.session_state.get("tiles", {})
    cp_tiles = tiles.get("cost_planner_v2", {})
    assessments = cp_tiles.get("assessments", {})
    
    # Get income data
    income_data = assessments.get("income", {})
    if income_data:
        # Sum up all income sources
        monthly_income = 0.0
        for key, value in income_data.items():
            if key.startswith(("social_security", "pension", "employment", "investment", "annuity", "other")):
                if isinstance(value, (int, float)):
                    monthly_income += value
        
        if monthly_income > 0:
            result["monthly_income"] = monthly_income
    
    # Get assets data
    assets_data = assessments.get("assets", {})
    if assets_data:
        # Sum up all asset categories
        total_assets = 0.0
        for key, value in assets_data.items():
            if key.startswith(("savings", "checking", "cd", "money_market", "401k", "ira", 
                             "pension_value", "stocks", "bonds", "mutual_funds", "home_value", 
                             "rental", "life_insurance", "annuity_value")):
                if isinstance(value, (int, float)):
                    total_assets += value
        
        if total_assets > 0:
            result["total_assets"] = total_assets
    
    # Check for insurance coverage indicators
    # Look for LTC insurance flag or data
    active_flags = flag_manager.get_active()
    if "ltc_insurance" in active_flags:
        result["insurance_coverage"].append("Long-Term Care Insurance")
    
    # Check for Medicaid/VA flags for concern derivation
    if "medicaid_pending" in active_flags or "medicaid_qualified" in active_flags:
        if not result["primary_concern"]:
            result["primary_concern"] = "Benefits navigation (Medicaid)"
            result["primary_concern_reason"] = "Medicaid application in progress"
    
    if "va_eligible" in active_flags or "va_aid_attendance" in active_flags:
        if not result["primary_concern"]:
            result["primary_concern"] = "Benefits navigation (VA Aid & Attendance)"
            result["primary_concern_reason"] = "VA benefits available"
    
    return result


def get_care_needs_prefill() -> Dict[str, Any]:
    """
    Get prefill data for Medical & Care Needs section.
    
    Returns:
        Dict with:
            chronic_conditions: List[str] - condition codes
            care_needs: Dict[str, Dict] - {
                "medication_management": {"enabled": bool, "reason": str},
                "mobility_assistance": {"enabled": bool, "reason": str},
                ...
            }
    """
    result = {
        "chronic_conditions": [],
        "care_needs": {}
    }
    
    # Get chronic conditions from Flag Manager
    chronic_records = flag_manager.get_chronic_conditions()
    result["chronic_conditions"] = [rec["code"] for rec in chronic_records]
    
    # Get active flags
    active_flags = flag_manager.get_active()
    
    # Derive care needs toggles from existing signals
    # Each toggle: name → {enabled: bool, reason: str}
    
    # 1. Medication Management
    if "medication_management" in active_flags:
        result["care_needs"]["medication_management"] = {
            "enabled": True,
            "reason": "From your care plan"
        }
    else:
        result["care_needs"]["medication_management"] = {"enabled": False, "reason": None}
    
    # 2. Mobility Assistance
    mobility_flags = ["mobility_limited", "high_mobility_dependence", "moderate_mobility"]
    if any(flag in active_flags for flag in mobility_flags):
        matching_flag = next(f for f in mobility_flags if f in active_flags)
        result["care_needs"]["mobility_assistance"] = {
            "enabled": True,
            "reason": f"From mobility assessment"
        }
    else:
        result["care_needs"]["mobility_assistance"] = {"enabled": False, "reason": None}
    
    # 3. Diabetic Care
    if "diabetes" in result["chronic_conditions"]:
        result["care_needs"]["diabetic_care"] = {
            "enabled": True,
            "reason": "From chronic conditions (Diabetes)"
        }
    else:
        result["care_needs"]["diabetic_care"] = {"enabled": False, "reason": None}
    
    # 4. Behavioral Support
    if "behavioral_concerns" in active_flags:
        result["care_needs"]["behavioral_support"] = {
            "enabled": True,
            "reason": "From your care plan"
        }
    else:
        result["care_needs"]["behavioral_support"] = {"enabled": False, "reason": None}
    
    # 5. Memory Support
    cognitive_flags = ["memory_support", "mild_cognitive_decline", 
                      "moderate_cognitive_decline", "severe_cognitive_risk"]
    if any(flag in active_flags for flag in cognitive_flags):
        result["care_needs"]["memory_support"] = {
            "enabled": True,
            "reason": "From cognitive assessment"
        }
    else:
        result["care_needs"]["memory_support"] = {"enabled": False, "reason": None}
    
    # 6. Oxygen Therapy
    if "copd" in result["chronic_conditions"]:
        result["care_needs"]["oxygen_therapy"] = {
            "enabled": True,
            "reason": "From chronic conditions (COPD)"
        }
    else:
        result["care_needs"]["oxygen_therapy"] = {"enabled": False, "reason": None}
    
    # 7. Wound Care (only if explicit signal exists)
    if "wound_care" in active_flags:
        result["care_needs"]["wound_care"] = {
            "enabled": True,
            "reason": "From your care plan"
        }
    else:
        result["care_needs"]["wound_care"] = {"enabled": False, "reason": None}
    
    # 8. Hospice/Palliative Care (only if explicit signal exists)
    if "hospice_palliative" in active_flags:
        result["care_needs"]["hospice_palliative"] = {
            "enabled": True,
            "reason": "From your care plan"
        }
    else:
        result["care_needs"]["hospice_palliative"] = {"enabled": False, "reason": None}
    
    return result


def update_care_need_flag(care_need_key: str, enabled: bool) -> None:
    """
    Update a care need flag when user changes a toggle.
    
    Only updates flags that have canonical mappings in Flag Manager.
    UI-only toggles are not persisted as flags.
    
    Args:
        care_need_key: Key like "medication_management", "mobility_assistance", etc.
        enabled: Whether the toggle is enabled
    """
    # Canonical flag mappings (only these get persisted to Flag Manager)
    FLAG_MAPPINGS = {
        "medication_management": "medication_management",
        "behavioral_support": "behavioral_concerns",
        "memory_support": "memory_support",
        "wound_care": "wound_care",
        "hospice_palliative": "hospice_palliative"
    }
    
    # Check if this toggle has a canonical flag mapping
    if care_need_key in FLAG_MAPPINGS:
        flag_id = FLAG_MAPPINGS[care_need_key]
        
        if enabled:
            flag_manager.activate(flag_id, source="advisor_prep.medical", 
                                 context=f"User enabled {care_need_key}")
        else:
            flag_manager.deactivate(flag_id, source="advisor_prep.medical",
                                   context=f"User disabled {care_need_key}")
    
    # For toggles without canonical flags (mobility_assistance, diabetic_care, oxygen_therapy),
    # these are derived from other signals and don't create new flags.
    # The user's selection is saved in session state only.


__all__ = [
    "get_financial_prefill",
    "get_care_needs_prefill", 
    "update_care_need_flag"
]
