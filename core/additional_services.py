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
    ss = st.session_state
    
    # Get flags from handoff (union of all product flags)
    all_flags = {}
    handoff = ss.get("handoff", {})
    
    for product_key, product_data in handoff.items():
        if isinstance(product_data, dict):
            product_flags = product_data.get("flags", {})
            if isinstance(product_flags, dict):
                all_flags.update(product_flags)
    
    return {
        "role": ss.get("role", "consumer"),
        "person_name": ss.get("person_name", ""),
        "gcp": ss.get("gcp", {}),
        "cost": ss.get("cost", {}),
        "flags": all_flags,  # Now contains actual flags from module outcomes
    }


def _passes(rule: Rule, ctx: Dict[str, Any]) -> bool:
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
        "order": 20,
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
        "order": 30,
        "hubs": ["concierge", "trusted_partners", "waiting_room"],
        "visible_when": [
            {"min_progress": {"path": "cost.progress", "value": 0}},
        ],
    },
]


def get_additional_services(hub: str = "concierge", limit: Optional[int] = None) -> List[Tile]:
    ctx = _ctx()
    name = ctx.get("person_name") or "your plan"
    
    # Get recommendation for subtitle interpolation
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
