from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

Tile = Dict[str, Any]
Rule = Dict[str, Any]

# ==============================================================================
# ADDITIONAL SERVICES CONFIGURATION
# ==============================================================================
#
# This module defines flag-based and product-based additional service tiles
# that appear in various hubs (concierge, waiting_room, trusted_partners, etc.)
#
# MCIP v2 INTEGRATION:
# - Reads care recommendation from MCIP.get_care_recommendation()
# - Reads financial profile from MCIP.get_financial_profile()
# - Uses structured flags from CareRecommendation.flags
# - Personalizes recommendations based on tier, confidence, and financial data
# - Falls back to legacy handoff for backwards compatibility
#
# RULE TYPES:
# - equals: path equals value
# - includes: value in container (list/dict for flags)
# - exists: path exists and is not None
# - min_progress: numeric value >= threshold
# - role_in: role in list of allowed roles
# - cost_gap: financial gap >= threshold (MCIP financial profile)
# - runway_low: runway months <= threshold (MCIP financial profile)
#
# HIDDEN SERVICES:
# - cost_planner_recommend: Hidden until MCIP approves. To enable, add this
#   to your session state setup or flag system:
#       st.session_state.setdefault("handoff", {})["flags"] = {
#           "cost_planner_enabled": True
#       }
#
# ==============================================================================



def _get(ctx: Dict[str, Any], dotted: str, default: Any = None) -> Any:
    cur: Any = ctx
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def _ctx() -> Dict[str, Any]:
    """Build context from MCIP v2 and session state.
    
    MCIP Integration:
    - Reads care recommendation from MCIP.get_care_recommendation()
    - Reads financial profile from MCIP.get_financial_profile()
    - Uses structured flags from CareRecommendation.flags
    - Falls back to legacy handoff for backwards compatibility
    """
    from core.mcip import MCIP
    
    ss = st.session_state
    
    # Get flags from MCIP v2 (primary source)
    all_flags = {}
    
    # Primary: Get flags from MCIP CareRecommendation
    care_rec = MCIP.get_care_recommendation()
    if care_rec and care_rec.flags:
        # Convert structured flags list to dict {flag_id: True}
        for flag in care_rec.flags:
            flag_id = flag.get("id")
            if flag_id:
                all_flags[flag_id] = True
    
    # Backwards compatibility: Merge with legacy handoff flags if present
    handoff = ss.get("handoff", {})
    for product_key, product_data in handoff.items():
        if isinstance(product_data, dict):
            product_flags = product_data.get("flags", {})
            if isinstance(product_flags, dict):
                all_flags.update(product_flags)
    
    # Build context with MCIP data
    financial_profile = MCIP.get_financial_profile()
    
    return {
        "role": ss.get("role", "consumer"),
        "person_name": ss.get("person_name", ""),
        "gcp": ss.get("gcp", {}),  # Legacy compatibility
        "cost": ss.get("cost", {}),  # Legacy compatibility
        "flags": all_flags,  # Unified flags from MCIP + legacy
        "mcip": {
            "care_recommendation": care_rec,
            "financial_profile": financial_profile,
            "tier": care_rec.tier if care_rec else None,
            "confidence": care_rec.confidence if care_rec else 0.0,
        }
    }


def _passes(rule: Rule, ctx: Dict[str, Any]) -> bool:
    """Check if a visibility rule passes.
    
    Rule Types:
    - equals: path equals value
    - includes: value in container (list/dict)
    - exists: path exists and is not None
    - min_progress: numeric value >= threshold
    - role_in: role in list of allowed roles
    - cost_gap: financial gap >= threshold (uses MCIP financial profile)
    - runway_low: runway months <= threshold (uses MCIP financial profile)
    """
    if not rule:
        return True
    
    if "equals" in rule:
        spec = rule["equals"]
        return _get(ctx, spec["path"]) == spec.get("value")
    
    if "includes" in rule:
        spec = rule["includes"]
        # Handle both lists and dicts (for flags)
        container = _get(ctx, spec["path"], [])
        value = spec.get("value")
        if isinstance(container, dict):
            # For flags dict, check if flag key exists and is truthy
            return container.get(value, False)
        elif isinstance(container, (list, tuple, set)):
            return value in container
        return False
    
    if "exists" in rule:
        spec = rule["exists"]
        return _get(ctx, spec["path"]) is not None
    
    if "min_progress" in rule:
        spec = rule["min_progress"]
        try:
            return float(_get(ctx, spec["path"], 0)) >= float(spec.get("value", 0))
        except Exception:
            return False
    
    if "role_in" in rule:
        roles = rule["role_in"] or []
        return _get(ctx, "role") in roles
    
    # MCIP Financial Profile Rules
    if "cost_gap" in rule:
        spec = rule["cost_gap"]
        financial = _get(ctx, "mcip.financial_profile")
        if not financial:
            return False
        try:
            gap = financial.gap_amount
            threshold = float(spec.get("value", 0))
            return gap >= threshold
        except Exception:
            return False
    
    if "runway_low" in rule:
        spec = rule["runway_low"]
        financial = _get(ctx, "mcip.financial_profile")
        if not financial:
            return False
        try:
            runway = financial.runway_months
            threshold = float(spec.get("value", 0))
            return runway <= threshold
        except Exception:
            return False
    
    return False


def _visible(tile: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    rules = tile.get("visible_when", [])
    
    if not rules:
        return True
    
    # OR logic: Any rule satisfied → visible
    for rule in rules:
        if _passes(rule, ctx):
            return True
    
    return False


REGISTRY: List[Tile] = [
    # === FLAG-BASED PARTNER SERVICES ===
    {
        "key": "omcare",
        "type": "partner",
        "title": "Omcare Medication Management",
        "subtitle": "Remote medication dispensing and adherence monitoring for {name}.",
        "cta": "Learn more",
        "go": "partner_omcare",
        "order": 5,
        "hubs": ["concierge", "trusted_partners"],
        "tags": ["meds_mgmt"],
        "visible_when": [
            # Trigger on moderate-to-severe medication complexity
            # GCP sets meds_management_needed=True for "Moderate (5-10 meds)" OR "Complex (10+ meds)"
            {"includes": {"path": "flags", "value": "meds_management_needed"}},
            # Keep these for compatibility with other products/future flags
            {"includes": {"path": "flags", "value": "medication_risk"}},
            {"includes": {"path": "flags", "value": "medication_adherence_risk"}},
        ],
    },
    {
        "key": "seniorlife_ai",
        "type": "partner",
        "title": "SeniorLife AI",
        "subtitle": "Wellness insights and proactive monitoring tailored for {name}.",
        "cta": "Explore",
        "go": "svc_seniorlife_ai",
        "order": 6,
        "hubs": ["concierge", "waiting_room"],
        "tags": ["ai", "monitoring"],
        "visible_when": [
            # Trigger on moderate-to-severe cognitive or fall risk
            # GCP sets cognitive_risk=True for "Moderate" OR "Severe" memory changes
            {"includes": {"path": "flags", "value": "cognitive_risk"}},
            # GCP sets fall_risk=True for "Multiple times per month" falls
            {"includes": {"path": "flags", "value": "fall_risk"}},
            # Keep these for compatibility with other products/future granular flags
            {"includes": {"path": "flags", "value": "cognition_risk_mild"}},
            {"includes": {"path": "flags", "value": "cognition_risk_moderate"}},
            {"includes": {"path": "flags", "value": "cognition_risk_severe"}},
            {"includes": {"path": "flags", "value": "cognitive_safety_risk"}},
        ],
    },
    {
        "key": "fall_prevention",
        "type": "partner",
        "title": "Fall Prevention & Safety",
        "subtitle": "Home safety assessment and monitoring solutions.",
        "cta": "Get assessment",
        "go": "partner_fall_prevention",
        "order": 7,
        "hubs": ["concierge", "trusted_partners"],
        "tags": ["fall_risk"],
        "visible_when": [
            {"includes": {"path": "flags", "value": "fall_risk"}},
        ],
    },
    {
        "key": "companion_care",
        "type": "partner",
        "title": "Companion Care Services",
        "subtitle": "Social engagement and companionship for isolated seniors.",
        "cta": "Find companions",
        "go": "partner_companion",
        "order": 8,
        "hubs": ["concierge", "trusted_partners"],
        "tags": ["companion", "isolation"],
        "visible_when": [
            {"includes": {"path": "flags", "value": "isolation_risk"}},
        ],
    },
    {
        "key": "memory_care",
        "type": "partner",
        "title": "Memory Care Specialists",
        "subtitle": "Specialized support for cognitive impairment and dementia care.",
        "cta": "Connect now",
        "go": "partner_memory_care",
        "order": 9,
        "hubs": ["concierge", "trusted_partners"],
        "tags": ["cognition"],
        "visible_when": [
            # Trigger on moderate-to-severe cognitive impairment
            # GCP sets cognitive_risk=True for "Moderate" OR "Severe" memory changes
            {"includes": {"path": "flags", "value": "cognitive_risk"}},
            # Keep these for compatibility with other products/future granular flags
            {"includes": {"path": "flags", "value": "cognition_risk_moderate"}},
            {"includes": {"path": "flags", "value": "cognition_risk_severe"}},
            {"includes": {"path": "flags", "value": "cognitive_safety_risk"}},
        ],
    },
    {
        "key": "wellness_coach",
        "type": "partner",
        "title": "Wellness & Emotional Support",
        "subtitle": "Professional counseling and emotional wellbeing services.",
        "cta": "Book session",
        "go": "partner_wellness",
        "order": 10,
        "hubs": ["concierge", "trusted_partners"],
        "tags": ["wellbeing"],
        "visible_when": [
            {"includes": {"path": "flags", "value": "emotional_support_risk"}},
            {"includes": {"path": "flags", "value": "health_management_risk"}},
        ],
    },
    {
        "key": "caregiver_support",
        "type": "partner",
        "title": "Caregiver Support & Respite",
        "subtitle": "Resources and relief for family caregivers.",
        "cta": "Get support",
        "go": "partner_caregiver",
        "order": 11,
        "hubs": ["concierge", "trusted_partners"],
        "tags": ["caregiver"],
        "visible_when": [
            {"includes": {"path": "flags", "value": "caregiver_burnout"}},
        ],
    },
    
    # === PRODUCT RECOMMENDATIONS ===
    {
        "key": "cost_planner_recommend",
        "type": "product",
        "title": "Cost Planner",
        "subtitle": "Estimate monthly costs based on your {recommendation} recommendation.",
        "cta": "Start planning",
        "go": "cost_open",
        "order": 15,
        "hubs": ["concierge"],
        "visible_when": [
            # Hidden until MCIP approves activation
            # To enable: set flag cost_planner_enabled=True in session state
            {"includes": {"path": "flags", "value": "cost_planner_enabled"}},
        ],
    },
    {
        "key": "pfma_recommend",
        "type": "product",
        "title": "Plan with My Advisor",
        "subtitle": "Schedule a 1:1 session to coordinate next steps.",
        "cta": "Book now",
        "go": "pfma_start",
        "order": 16,
        "hubs": ["concierge"],
        "visible_when": [
            # Show after Cost Planner is 100% complete
            {"min_progress": {"path": "cost.progress", "value": 100}},
        ],
    },
    
    # === MODULE RECOMMENDATIONS ===
    {
        "key": "va_benefits_module",
        "type": "module",
        "title": "VA Aid & Attendance Benefits",
        "subtitle": "Check eligibility for veteran benefits and services based on care needs.",
        "cta": "Check eligibility",
        "go": "module_va_benefits",
        "order": 17,
        "hubs": ["concierge"],
        "visible_when": [
            # Trigger on veteran_aanda_risk flag (ADL/IADL impairments)
            {"includes": {"path": "flags", "value": "veteran_aanda_risk"}},
        ],
    },
    {
        "key": "medicaid_planning",
        "type": "module",
        "title": "Medicaid Planning",
        "subtitle": "Explore Medicaid eligibility and spend-down strategies.",
        "cta": "Learn options",
        "go": "module_medicaid",
        "order": 18,
        "hubs": ["concierge"],
        "visible_when": [
            {"includes": {"path": "flags", "value": "medicaid_likely"}},
            # Show if financial gap is significant (>$1000/month uncovered)
            {"cost_gap": {"value": 1000}},
            # Show if runway is critically low (<24 months)
            {"runway_low": {"value": 24}},
        ],
    },
    
    # === FINANCIAL PLANNING SERVICES (MCIP Financial Profile Integration) ===
    {
        "key": "reverse_mortgage",
        "type": "partner",
        "title": "Reverse Mortgage Options",
        "subtitle": "Unlock home equity to fund care costs for {name}.",
        "cta": "Explore options",
        "go": "partner_reverse_mortgage",
        "order": 19,
        "hubs": ["concierge", "trusted_partners"],
        "tags": ["financing"],
        "visible_when": [
            # Show if runway is low (<36 months) - suggests need for additional funding
            {"runway_low": {"value": 36}},
        ],
    },
    {
        "key": "elder_law_attorney",
        "type": "partner",
        "title": "Elder Law Attorney",
        "subtitle": "Protect assets and plan for long-term care expenses.",
        "cta": "Schedule consultation",
        "go": "partner_elder_law",
        "order": 20,
        "hubs": ["concierge", "trusted_partners"],
        "tags": ["legal", "financing"],
        "visible_when": [
            # Show if there's a significant cost gap (>$500/month)
            {"cost_gap": {"value": 500}},
        ],
    },
    
    # === ALWAYS-AVAILABLE SERVICES ===
    {
        "key": "learning_center",
        "type": "content",
        "title": "Learning Center",
        "subtitle": "Short lessons and guides to stay ahead of every decision.",
        "cta": "Browse library",
        "go": "svc_learning",
        "order": 30,
        "hubs": ["concierge", "learning", "waiting_room"],
        "visible_when": [],
    },
    {
        "key": "care_network",
        "type": "partner",
        "title": "Care Coordination Network",
        "subtitle": "Connect with vetted professionals when you need extra hands.",
        "cta": "Find partners",
        "go": "svc_partners",
        "order": 40,
        "hubs": ["concierge", "trusted_partners", "waiting_room"],
        "visible_when": [
            {"min_progress": {"path": "cost.progress", "value": 0}},
        ],
    },
    
    # === FUTURE SERVICE CATEGORIES (Currently Disabled) ===
    # Uncomment when respective hubs are implemented
    
    # Estate Planning Services (Future Hub: hubs/estate_planning.py)
    # {
    #     "key": "estate_planning_suite",
    #     "type": "service",
    #     "title": "Estate Planning Services",
    #     "subtitle": "Protect assets and plan for {name}'s legacy.",
    #     "cta": "Start planning",
    #     "go": "hub_estate_planning",
    #     "order": 50,
    #     "hubs": ["concierge", "estate_planning"],
    #     "visible_when": [
    #         {"runway_low": {"value": 60}},  # Have substantial assets (60+ months)
    #     ],
    # },
    
    # Retirement Planning Services (Future Hub: hubs/retirement_planning.py)
    # {
    #     "key": "social_security_optimizer",
    #     "type": "service",
    #     "title": "Social Security Optimization",
    #     "subtitle": "Maximize retirement benefits for {name}.",
    #     "cta": "Get analysis",
    #     "go": "hub_retirement_planning",
    #     "order": 51,
    #     "hubs": ["concierge", "retirement_planning"],
    #     "visible_when": [
    #         {"includes": {"path": "flags", "value": "retirement_age"}},
    #     ],
    # },
    
    # Care Coordination Services (Future Hub: hubs/care_coordination.py)
    # {
    #     "key": "professional_care_manager",
    #     "type": "service",
    #     "title": "Professional Care Manager",
    #     "subtitle": "Coordinate all aspects of care for {name}.",
    #     "cta": "Connect now",
    #     "go": "hub_care_coordination",
    #     "order": 52,
    #     "hubs": ["concierge", "care_coordination"],
    #     "visible_when": [
    #         {"includes": {"path": "flags", "value": "caregiver_burnout"}},
    #         {"includes": {"path": "flags", "value": "complex_care_needs"}},
    #     ],
    # },
]


def get_additional_services(hub: str = "concierge", limit: Optional[int] = None) -> List[Tile]:
    """Get additional service tiles for a hub, filtered by MCIP data and flags.
    
    MCIP Integration:
    - Uses MCIP.get_care_recommendation() for tier and flags
    - Uses MCIP.get_financial_profile() for cost-based filtering
    - Personalizes subtitles with user name and care tier
    - Falls back to legacy handoff for backwards compatibility
    
    Args:
        hub: Hub identifier (concierge, trusted_partners, etc.)
        limit: Optional max number of tiles to return
    
    Returns:
        List of visible service tiles for the hub
    """
    from core.mcip import MCIP
    
    ctx = _ctx()
    name = ctx.get("person_name") or "your plan"
    
    # Get recommendation from MCIP v2 (primary source)
    care_rec = MCIP.get_care_recommendation()
    if care_rec and care_rec.tier:
        recommendation_display = care_rec.tier.replace("_", " ").title()
    else:
        # Fall back to legacy handoff
        handoff = st.session_state.get("handoff", {}).get("gcp", {})
        recommendation = handoff.get("recommendation", "")
        recommendation_display = recommendation.replace("_", " ").title() if recommendation else "personalized"
    
    tiles: List[Tile] = []

    for tile in REGISTRY:
        hubs = tile.get("hubs")
        if hubs and hub not in hubs:
            continue
        if not _visible(tile, ctx):
            continue
        
        # Interpolate subtitle with context
        subtitle = (tile.get("subtitle") or "")
        subtitle = subtitle.replace("{name}", name)
        subtitle = subtitle.replace("{recommendation}", recommendation_display)
        
        tiles.append(
            {
                "key": tile["key"],
                "type": tile.get("type", "partner"),  # Default to partner for backwards compatibility
                "title": tile["title"],
                "subtitle": subtitle,
                "cta": tile.get("cta", "Open"),
                "go": tile.get("go", tile["key"]),
                "order": tile.get("order", 100),
                "tags": tile.get("tags", []),
            }
        )

    tiles.sort(key=lambda x: (x.get("order", 100), x.get("title", "").casefold()))
    if limit is not None:
        tiles = tiles[:limit]
    
    return tiles
