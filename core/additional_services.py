from __future__ import annotations

import json
from pathlib import Path
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
# PARTNER INTEGRATION:
# - Dynamically loads partners from config/partners.json
# - Checks unlock_requires against GCP completion and flags
# - Converts partner data to service tiles
# - Only shows partners when unlock requirements are met
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

# Path to partners configuration
PARTNERS_FILE = Path(__file__).resolve().parents[1] / "config" / "partners.json"


def _load_partners() -> List[Dict[str, Any]]:
    """Load partner configurations from partners.json.
    
    Returns:
        List of partner dictionaries
    """
    if not PARTNERS_FILE.exists():
        return []
    
    try:
        with PARTNERS_FILE.open() as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  ERROR loading partners.json: {e}")
        return []


def _parse_unlock_requirement(req: str, ctx: Dict[str, Any]) -> bool:
    """Parse and evaluate a single unlock requirement.
    
    Formats:
    - "gcp:complete" - GCP must be 100% complete
    - "gcp:>=50" - GCP must be at least 50% complete
    - "flag:flag_name" - Single flag must be True
    - "flag:flag1|flag2|flag3" - ANY of the flags must be True (OR logic)
    
    Args:
        req: Unlock requirement string
        ctx: Context with progress and flags
    
    Returns:
        True if requirement is met
    """
    if req.startswith("gcp:"):
        gcp_req = req.replace("gcp:", "")
        gcp_progress = _get(ctx, "progress.gcp", 0)
        
        if gcp_req == "complete":
            return gcp_progress >= 100
        elif gcp_req.startswith(">="):
            threshold = int(gcp_req.replace(">=", ""))
            return gcp_progress >= threshold
        else:
            return False
    
    elif req.startswith("flag:"):
        flag_expr = req.replace("flag:", "")
        flags = _get(ctx, "flags", {})
        
        # Handle OR logic (flag1|flag2|flag3)
        if "|" in flag_expr:
            flag_names = flag_expr.split("|")
            return any(flags.get(flag_name.strip(), False) for flag_name in flag_names)
        else:
            return flags.get(flag_expr, False)
    
    return False


def _partner_unlocked(partner: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    """Check if partner unlock requirements are met.
    
    Args:
        partner: Partner configuration dict
        ctx: Context with progress and flags
    
    Returns:
        True if ALL unlock requirements are met (AND logic across requirements)
    """
    unlock_requires = partner.get("unlock_requires", [])
    
    # No requirements = always unlocked
    if not unlock_requires:
        return True
    
    # ALL requirements must be met (AND logic)
    return all(_parse_unlock_requirement(req, ctx) for req in unlock_requires)


def _convert_partner_to_tile(partner: Dict[str, Any], order: int) -> Tile:
    """Convert partner configuration to service tile format.
    
    Args:
        partner: Partner dict from partners.json
        order: Display order for tile
    
    Returns:
        Service tile dict
    """
    partner_id = partner.get("id", "unknown")
    primary_cta = partner.get("primary_cta", {})
    
    # Extract route - handle both direct routes and /partner/connect URLs
    route = primary_cta.get("route", f"partner_{partner_id}")
    
    return {
        "key": f"partner_{partner_id}",
        "type": "partner",
        "id": partner_id,  # Add explicit id field
        "title": partner.get("name", "Partner"),
        "subtitle": partner.get("headline", ""),
        "cta": primary_cta.get("label", "Connect"),
        "go": route,  # Use partner's CTA route directly
        "order": order,
        "hubs": ["concierge", "trusted_partners"],  # Partners show in both hubs
        "tags": partner.get("tags", []),
        "partner_id": partner_id,  # Store original partner ID for reference
        "rating": partner.get("rating"),  # Include rating if present
        "_raw_partner_data": partner,  # Pass complete partner config for connection rendering
    }


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
    
    # Get progress from MCIP journey state
    # GCP progress is 100 if complete, 0 otherwise (MCIP tracks completion not percentage)
    # For granular progress during GCP, we'd need to check module engine state
    gcp_complete = MCIP.is_product_complete("gcp")
    cost_complete = MCIP.is_product_complete("cost_planner")
    
    progress = {
        "gcp": 100 if gcp_complete else 0,  # Binary: complete or not
        "cost": 100 if cost_complete else 0,
    }
    
    return {
        "role": ss.get("role", "consumer"),
        "person_name": ss.get("person_name", ""),
        "gcp": ss.get("gcp", {}),  # Legacy compatibility
        "cost": ss.get("cost", {}),  # Legacy compatibility
        "progress": progress,  # Add progress dict for unlock requirements
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
            # HIGH PRIORITY: Critical medication safety needs
            # ADL/IADL dependence (includes medication management)
            {"includes": {"path": "flags", "value": "moderate_dependence"}},
            {"includes": {"path": "flags", "value": "high_dependence"}},
            # Chronic conditions requiring medication regimens
            {"includes": {"path": "flags", "value": "chronic_present"}},
            # Cognitive decline (medication adherence risk)
            {"includes": {"path": "flags", "value": "moderate_cognitive_decline"}},
            {"includes": {"path": "flags", "value": "severe_cognitive_risk"}},
            # No caregiver support (no one to help with meds)
            {"includes": {"path": "flags", "value": "no_support"}},
            # Severe mobility limitations (can't get to pharmacy)
            {"includes": {"path": "flags", "value": "high_mobility_dependence"}},
            
            # MEDIUM PRIORITY: Medication adherence risk factors
            # Early cognitive decline (preventive intervention)
            {"includes": {"path": "flags", "value": "mild_cognitive_decline"}},
            # Moderate mobility issues (difficulty accessing pharmacy)
            {"includes": {"path": "flags", "value": "moderate_mobility"}},
            # Limited caregiver support (intermittent help)
            {"includes": {"path": "flags", "value": "limited_support"}},
            # Geographic isolation (medication delivery needs)
            {"includes": {"path": "flags", "value": "geo_isolated"}},
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
            # Fall risk
            {"includes": {"path": "flags", "value": "falls_multiple"}},
            {"includes": {"path": "flags", "value": "moderate_safety_concern"}},
            {"includes": {"path": "flags", "value": "high_safety_concern"}},
            # Cognitive decline (any level)
            {"includes": {"path": "flags", "value": "mild_cognitive_decline"}},
            {"includes": {"path": "flags", "value": "moderate_cognitive_decline"}},
            {"includes": {"path": "flags", "value": "severe_cognitive_risk"}},
            # Mental health / behavioral concerns
            {"includes": {"path": "flags", "value": "mental_health_concern"}},
        ],
    },
    
    # === PLACEHOLDER PARTNER SERVICES (DISABLED - NO CONTRACTS YET) ===
    # Uncomment and add to partners.json when contracts are in place
    # {
    #     "key": "fall_prevention",
    #     "type": "placeholder",
    #     "title": "Fall Prevention & Safety",
    #     "subtitle": "Home safety assessment and monitoring solutions.",
    #     "cta": "Get assessment",
    #     "go": "partner_fall_prevention",
    #     "order": 7,
    #     "hubs": ["concierge", "trusted_partners"],
    #     "tags": ["fall_risk"],
    #     "visible_when": [
    #         {"includes": {"path": "flags", "value": "falls_multiple"}},
    #         {"includes": {"path": "flags", "value": "high_safety_concern"}},
    #         {"includes": {"path": "flags", "value": "moderate_safety_concern"}},
    #     ],
    # },
    # {
    #     "key": "companion_care",
    #     "type": "placeholder",
    #     "title": "Companion Care Services",
    #     "subtitle": "Social engagement and companionship for isolated seniors.",
    #     "cta": "Find companions",
    #     "go": "partner_companion",
    #     "order": 8,
    #     "hubs": ["concierge", "trusted_partners"],
    #     "tags": ["companion", "isolation"],
    #     "visible_when": [
    #         {"includes": {"path": "flags", "value": "geo_isolated"}},
    #         {"includes": {"path": "flags", "value": "very_low_access"}},
    #         {"includes": {"path": "flags", "value": "no_support"}},
    #     ],
    # },
    # {
    #     "key": "memory_care",
    #     "type": "placeholder",
    #     "title": "Memory Care Specialists",
    #     "subtitle": "Specialized support for cognitive impairment and dementia care.",
    #     "cta": "Connect now",
    #     "go": "partner_memory_care",
    #     "order": 9,
    #     "hubs": ["concierge", "trusted_partners"],
    #     "tags": ["cognition"],
    #     "visible_when": [
    #         {"includes": {"path": "flags", "value": "moderate_cognitive_decline"}},
    #         {"includes": {"path": "flags", "value": "severe_cognitive_risk"}},
    #     ],
    # },
    # {
    #     "key": "wellness_coach",
    #     "type": "placeholder",
    #     "title": "Wellness & Emotional Support",
    #     "subtitle": "Professional counseling and emotional wellbeing services.",
    #     "cta": "Book session",
    #     "go": "partner_wellness",
    #     "order": 10,
    #     "hubs": ["concierge", "trusted_partners"],
    #     "tags": ["wellbeing"],
    #     "visible_when": [
    #         {"includes": {"path": "flags", "value": "mental_health_concern"}},
    #         {"includes": {"path": "flags", "value": "high_risk"}},
    #         {"includes": {"path": "flags", "value": "moderate_risk"}},
    #     ],
    # },
    # {
    #     "key": "caregiver_support",
    #     "type": "placeholder",
    #     "title": "Caregiver Support & Respite",
    #     "subtitle": "Resources and relief for family caregivers.",
    #     "cta": "Get support",
    #     "go": "partner_caregiver",
    #     "order": 11,
    #     "hubs": ["concierge", "trusted_partners"],
    #     "tags": ["caregiver"],
    #     "visible_when": [
    #         {"includes": {"path": "flags", "value": "limited_support"}},
    #         {"includes": {"path": "flags", "value": "no_support"}},
    #     ],
    # },
    
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
    
    PARTNER INTEGRATION:
    - Dynamically loads partners from config/partners.json
    - Only includes partners matching hub and unlock requirements
    - Omcare and SeniorLife.AI loaded from partners.json (not REGISTRY)
    - Other services still loaded from REGISTRY
    
    MCIP Integration:
    - Uses MCIP.get_care_recommendation() for tier and flags
    - Uses MCIP.get_financial_profile() for cost-based filtering
    - Personalizes subtitles with user name and care tier
    - Detects personalization: "personalized" if triggered by GCP flags, "navi" otherwise
    - Falls back to legacy handoff for backwards compatibility
    
    Args:
        hub: Hub identifier (concierge, trusted_partners, etc.)
        limit: Optional max number of tiles to return
    
    Returns:
        List of visible service tiles with personalization metadata
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
    
    # DYNAMIC PARTNERS: Load from partners.json
    partners = _load_partners()
    partner_order = 500  # Start partners at order 500
    
    for partner in partners:
        partner_id = partner.get("id")
        
        # Check visibility rules:
        # 1. If visible: false, only show if unlocked by flags
        # 2. If visible: true or missing, always check unlock_requires
        is_visible_by_default = partner.get("visible", True)
        
        if not is_visible_by_default:
            # Hidden by default - only show if unlock requirements met
            if not _partner_unlocked(partner, ctx):
                continue
        else:
            # Visible by default - still check unlock requirements (for progressive disclosure)
            if not _partner_unlocked(partner, ctx):
                continue
        
        # Convert partner to tile
        partner_tile = _convert_partner_to_tile(partner, partner_order)
        partner_order += 10
        
        # Check hub filtering (partners appear in concierge and trusted_partners by default)
        tile_hubs = partner_tile.get("hubs", [])
        if tile_hubs and hub not in tile_hubs:
            continue
        
        # Interpolate subtitle
        subtitle = partner_tile.get("subtitle", "")
        subtitle = subtitle.replace("{name}", name)
        subtitle = subtitle.replace("{recommendation}", recommendation_display)
        partner_tile["subtitle"] = subtitle
        
        # Determine personalization:
        # CRITICAL: ONLY Omcare and SeniorLife.AI get "Navi Recommended" label
        # All other partners get no personalization label
        if partner_id in ["omcare", "seniorlife_ai"] and not is_visible_by_default:
            partner_tile["personalization"] = "personalized"  # Flag-triggered, Navi Recommended
        else:
            partner_tile["personalization"] = None  # No label
        
        tiles.append(partner_tile)
    
    # STATIC SERVICES: Load from REGISTRY (non-partner services)
    for tile in REGISTRY:
        # Skip ALL partner services that are now dynamically loaded from partners.json
        # Partners: hpone, omcare, seniorlife_ai, lantern, ncoa, home_instead
        partner_keys = ["hpone", "omcare", "seniorlife_ai", "lantern", "ncoa", "home_instead"]
        if tile.get("key") in partner_keys:
            continue
        
        hubs = tile.get("hubs")
        if hubs and hub not in hubs:
            continue
        if not _visible(tile, ctx):
            continue
        
        # Interpolate subtitle with context
        subtitle = (tile.get("subtitle") or "")
        subtitle = subtitle.replace("{name}", name)
        subtitle = subtitle.replace("{recommendation}", recommendation_display)
        
        # Detect personalization type
        personalization = _detect_personalization(tile, ctx)
        
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
                "personalization": personalization,  # "personalized", "navi", or None
            }
        )

    # Sort tiles with Navi Recommended on top
    # Priority: 1) Personalized tiles first, 2) Then by order, 3) Then alphabetically
    def sort_key(tile):
        # Personalization priority: "personalized" = 0 (top), None = 1 (bottom)
        personalization_priority = 0 if tile.get("personalization") == "personalized" else 1
        return (personalization_priority, tile.get("order", 100), tile.get("title", "").casefold())
    
    tiles.sort(key=sort_key)
    if limit is not None:
        tiles = tiles[:limit]
    
    return tiles


def _detect_personalization(tile: Dict[str, Any], ctx: Dict[str, Any]) -> Optional[str]:
    """Detect whether a tile is Navi-recommended based on care/cost flags.
    
    CRITICAL RULES:
    - Only flag-triggered services get "personalized" → Shows "Navi Recommended" label + blue gradient
    - General utilities (Learning Center, Care Network) → No label, no gradient
    - Care flags come from GCP care_recommendation
    - Cost flags will come from Cost Planner (not yet implemented)
    
    Returns:
        - "personalized": Triggered by specific care/cost flags → "Navi Recommended"
        - None: General utility or always-visible service → No label/gradient
    """
    rules = tile.get("visible_when", [])
    
    # No rules OR min_progress rules only → General utility (no label/gradient)
    if not rules:
        return None
    
    # Check if ALL rules are just min_progress (utility services like care_network)
    if all("min_progress" in rule for rule in rules):
        return None
    
    # CARE FLAGS (from GCP - these trigger personalized services)
    # These match the actual flag IDs in core/flags.py FLAG_REGISTRY
    # Source: products/gcp_v4/modules/care_recommendation/module.json
    care_flags = [
        # Cognitive & Memory
        "mild_cognitive_decline",
        "moderate_cognitive_decline", 
        "severe_cognitive_risk",
        # Fall & Safety
        "moderate_safety_concern",
        "high_safety_concern",
        "falls_multiple",
        # Mobility
        "moderate_mobility",
        "high_mobility_dependence",
        # Dependence & ADL
        "moderate_dependence",
        "high_dependence",
        "veteran_aanda_risk",
        # Mental Health
        "moderate_risk",
        "high_risk",
        "mental_health_concern",
        # Health
        "chronic_present",
        # Support System
        "no_support",
        "limited_support",
        # Geographic
        "low_access",
        "very_low_access",
        "geo_isolated",
    ]
    
    # COST FLAGS (to be added later - cost-based personalization)
    cost_flag_rules = ["cost_gap", "runway_low"]
    
    # Check if tile was triggered by care or cost flags
    for rule in rules:
        if "includes" in rule:
            flag_value = rule["includes"].get("value")
            if flag_value in care_flags:
                # Check if this flag is actually present in context
                if _passes(rule, ctx):
                    return "personalized"
        elif any(cost_rule in rule for cost_rule in cost_flag_rules):
            # Financial triggers are also personalized
            if _passes(rule, ctx):
                return "personalized"
    
    # If tile is visible but not triggered by care/cost flags → No label (general utility)
    return None
