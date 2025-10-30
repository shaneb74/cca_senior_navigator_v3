"""Journey phase detection helper.

Determines the current journey phase (discovery, planning, post-planning) based
on user state and MCIP completion flags.

Used by hub_lobby.py to determine which tiles appear active, locked, or completed.

Phase 5A enhancements:
- get_phase_completion() for phase-based progress tracking
- advance_to() for explicit phase transitions
- get_current_journey() for session-based phase reading
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from typing import Any
    
import streamlit as st

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


# ==============================================================================
# PHASE 5A ENHANCEMENTS: Phase completion tracking and transitions
# ==============================================================================

def get_phase_completion(phase: str) -> float:
    """Return percentage of completion within a given journey phase.
    
    Args:
        phase: Journey phase ("discovery", "planning", "post_planning")
        
    Returns:
        float: Completion percentage (0.0 to 1.0)
        
    Phase 5A Logic:
        Calculates completion based on tiles registered and completed within
        the specified phase.
        
    Examples:
        >>> get_phase_completion("discovery")
        0.5  # 50% of discovery tiles completed
    """
    # Get registered tiles for this phase from session
    registered_tiles = st.session_state.get("registered_tiles", [])
    completed_tiles = st.session_state.get("completed_tiles", [])
    
    # Filter by phase
    phase_tiles = [t for t in registered_tiles if t.get("phase") == phase]
    phase_completed = [t for t in completed_tiles if t.get("phase") == phase]
    
    # Calculate percentage
    if not phase_tiles:
        return 0.0
    
    return len(phase_completed) / len(phase_tiles)


def advance_to(stage: str) -> None:
    """Advance the user to a specific journey stage.
    
    Args:
        stage: Journey stage to advance to ("discovery", "planning", "post_planning")
        
    Phase 5A Enhancement:
        Sets journey_stage in session state and provides user feedback via toast.
    """
    st.session_state["journey_stage"] = stage
    st.toast(f"🧭 Journey advanced to: {stage.replace('_', ' ').title()}")
    print(f"[JOURNEY] Advanced to stage: {stage}")


def get_current_journey() -> str:
    """Return the current user journey stage from session state.
    
    Returns:
        str: Current journey stage ("discovery", "planning", "post_planning")
        
    Phase 5A Enhancement:
        Reads from journey_stage in session state, defaults to "discovery".
    """
    return st.session_state.get("journey_stage", "discovery")


def mark_tile_complete(key: str, phase: str) -> None:
    """Add a completed tile entry for the phase.
    
    Args:
        key: Tile/product key (e.g., "discovery_learning", "learn_recommendation")
        phase: Journey phase ("discovery", "planning", "post_planning")
        
    Phase 5B Enhancement:
        Tracks completion of learning tiles and updates journey stage.
        Used by learning_template.py for completion tracking.
    
    Examples:
        >>> mark_tile_complete("discovery_learning", "discovery")
        # Adds to completed_tiles and sets journey_stage
    """
    # Initialize completed_tiles list if not exists
    if "completed_tiles" not in st.session_state:
        st.session_state["completed_tiles"] = []
    
    # Add completion entry
    completed = st.session_state["completed_tiles"]
    
    # Avoid duplicates
    if not any(t.get("key") == key for t in completed):
        completed.append({"key": key, "phase": phase})
    
    # Update journey stage to current phase
    st.session_state["journey_stage"] = phase
    
    print(f"[JOURNEY] Tile '{key}' marked complete in phase '{phase}'")


def mark_journey_complete(journey_phase: str) -> None:
    """Mark an entire journey phase as complete.
    
    Args:
        journey_phase: Journey phase to complete ("discovery", "planning", "post_planning")
        
    Phase 5D Enhancement:
        Marks entire journey phase as complete and advances user to next phase.
        Used after critical milestones (e.g., appointment booking completes Planning).
        
    Examples:
        >>> mark_journey_complete("planning")
        # Marks planning complete, advances to post_planning
    """
    # Initialize completed_journeys list if not exists
    if "completed_journeys" not in st.session_state:
        st.session_state["completed_journeys"] = []
    
    completed_journeys = st.session_state["completed_journeys"]
    
    # Add journey to completed list (avoid duplicates)
    if journey_phase not in completed_journeys:
        completed_journeys.append(journey_phase)
        st.toast(f"✅ {journey_phase.replace('_', ' ').title()} Journey Complete!")
        print(f"[JOURNEY] Journey '{journey_phase}' marked complete")
    
    # Advance to next phase
    phase_progression = {
        "discovery": "planning",
        "planning": "post_planning",
        "post_planning": "post_planning"  # Stay in final phase
    }
    
    next_phase = phase_progression.get(journey_phase, journey_phase)
    if next_phase != journey_phase:
        advance_to(next_phase)


def is_journey_complete(journey_phase: str) -> bool:
    """Check if a journey phase has been completed.
    
    Args:
        journey_phase: Journey phase to check ("discovery", "planning", "post_planning")
        
    Returns:
        bool: True if journey phase is complete, False otherwise
        
    Phase 5D Enhancement:
        Used by hub_lobby.py to display completed journeys in separate section.
    """
    completed_journeys = st.session_state.get("completed_journeys", [])
    return journey_phase in completed_journeys


__all__ = [
    "get_journey_phase",
    "is_tile_active",
    "JourneyPhase",
    "get_phase_completion",  # Phase 5A
    "advance_to",  # Phase 5A
    "get_current_journey",  # Phase 5A
    "mark_tile_complete",  # Phase 5B
    "mark_journey_complete",  # Phase 5D
    "is_journey_complete",  # Phase 5D
]
