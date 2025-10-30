"""Journey phase detection helper.

Determines the current journey phase (discovery, planning, post-planning) based
on user state and MCIP completion flags.

Used by hub_lobby.py to determine which tiles appear active, locked, or completed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from typing import Any

JourneyPhase = Literal["discovery", "planning", "post_planning"]


def get_journey_phase(user_state: dict[str, Any]) -> JourneyPhase:
    """Return the current journey phase: discovery, planning, or post-planning.
    
    Args:
        user_state: Session state dictionary containing user progress flags
        
    Returns:
        JourneyPhase: One of "discovery", "planning", or "post_planning"
        
    Phase Logic:
        - discovery: User has not completed Guided Care Plan
        - planning: GCP completed, but advisor not yet booked
        - post_planning: Advisor session booked/completed
        
    Examples:
        >>> state = {"guided_care_completed": False}
        >>> get_journey_phase(state)
        "discovery"
        
        >>> state = {"guided_care_completed": True, "advisor_booked": False}
        >>> get_journey_phase(state)
        "planning"
        
        >>> state = {"guided_care_completed": True, "advisor_booked": True}
        >>> get_journey_phase(state)
        "post_planning"
    """
    # Discovery phase: Haven't completed Guided Care Plan yet
    if not user_state.get("guided_care_completed"):
        return "discovery"
    
    # Planning phase: GCP done, but advisor not booked
    elif not user_state.get("advisor_booked"):
        return "planning"
    
    # Post-planning phase: Advisor session scheduled/completed
    return "post_planning"


def is_tile_active(tile_key: str, journey_phase: JourneyPhase) -> bool:
    """Determine if a tile should be active/unlocked based on journey phase.
    
    Args:
        tile_key: Product tile key (e.g., "gcp_v4", "cost_v2", "trivia")
        journey_phase: Current journey phase from get_journey_phase()
        
    Returns:
        bool: True if tile should be active/unlocked, False if locked
        
    Tile Unlock Logic:
        - Discovery tiles: Always unlocked
        - Planning tiles: Unlocked after GCP completed
        - Engagement tiles: Always unlocked (Trivia, CCR)
        - Additional services: Always available
    """
    # Discovery journey tiles - always unlocked
    discovery_tiles = {"gcp_v4", "gcp"}
    if tile_key in discovery_tiles:
        return True
    
    # Engagement products - always unlocked (Trivia, Concierge Clinical Review)
    engagement_tiles = {"senior_trivia", "ccr_overview", "ccr_checklist", "ccr_schedule"}
    if tile_key in engagement_tiles:
        return True
    
    # Additional services - always available
    additional_services = {
        "omcare", "seniorlife", "va_aa", "elderlaw", 
        "fall_risk", "disease_mgmt", "home_safety", "home_health", "dme", "med_manage"
    }
    if tile_key in additional_services:
        return True
    
    # Planning tiles - require GCP completion
    planning_tiles = {"cost_v2", "cost_intro", "pfma_v3", "fa_intro", "advisor_prep"}
    if tile_key in planning_tiles:
        return journey_phase in ("planning", "post_planning")
    
    # Default: locked
    return False


__all__ = ["get_journey_phase", "is_tile_active", "JourneyPhase"]
