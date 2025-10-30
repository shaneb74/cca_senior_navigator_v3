"""
Guidance Manager - Retrieves persona-specific contextual guidance messages.

Part of Phase 5: Contextual Guidance Layer
Provides adaptive, empathetic guidance based on current page and user persona.

Phase 5A enhancements:
- get_phase_guidance() for journey phase-aware guidance text
- Integration with core/journeys.py for phase detection
"""

import yaml
from pathlib import Path
from typing import Optional

from apps.navi_core.context_manager import get_current_context, get_phase_tone
from apps.navi_core.profile_manager import ProfileManager
from apps.navi_core.trigger_manager import should_show
from core.journeys import get_current_journey


# Path to guidance configuration file
GUIDANCE_FILE = Path(__file__).parent / "config" / "guidance.yaml"


def load_guidance() -> dict:
    """
    Load guidance templates from YAML configuration file.
    
    Returns:
        Dictionary mapping pages → personas → guidance data
        
    Raises:
        FileNotFoundError: If guidance.yaml doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    if not GUIDANCE_FILE.exists():
        raise FileNotFoundError(f"Guidance config not found: {GUIDANCE_FILE}")
    
    with open(GUIDANCE_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_guidance(page: Optional[str] = None, persona: Optional[str] = None) -> Optional[str]:
    """
    Return persona-specific guidance message for the active page.
    
    Respects smart triggers to avoid showing guidance too frequently.
    Returns None if triggers prevent display.
    
    Args:
        page: Page name (if None, uses get_current_context())
        persona: User persona/role (if None, uses profile_manager)
        
    Returns:
        Guidance message string tailored to page + persona, or None if suppressed by triggers
        
    Example:
        >>> get_guidance(page="Welcome", persona="AdultChild")
        "Welcome! I'll help you explore care options for your parent."
        >>> get_guidance(page="Welcome", persona="AdultChild")  # Second call
        None  # (if show_once_per_session is True)
    """
    data = load_guidance()
    
    # Determine page context
    page = page or get_current_context()
    
    # Check smart triggers - return None if suppressed
    if not should_show(page):
        return None
    
    # Determine user persona
    if persona is None:
        manager = ProfileManager()
        profile = manager.get_profile(user_id="default", create_if_missing=False)
        persona = profile.role if profile else "AdultChild"
    
    # Try to get persona-specific message for this page
    try:
        msg = data[page][persona]["message"]
    except (KeyError, TypeError):
        # Fall back to page default, then global fallback
        try:
            msg = data[page]["Default"]["message"]
        except (KeyError, TypeError):
            msg = "I'm here if you'd like guidance on this step."
    
    return msg


def get_phase_guidance(page: Optional[str] = None) -> Optional[str]:
    """
    Get phase-aware guidance text for the current journey stage.
    
    Phase 5A enhancement: Returns contextual guidance that varies based on
    whether user is in discovery, planning, or post_planning phase.
    
    Args:
        page: Page name (if None, uses get_current_context())
        
    Returns:
        Phase-specific guidance message, or None if no guidance available
        
    Example:
        >>> get_phase_guidance(page="GCP")  # discovery phase
        "Let's start by understanding your care needs. I'll guide you step-by-step."
        >>> get_phase_guidance(page="Cost Planner")  # planning phase
        "Now let's explore cost options together. I'm here to help you understand the numbers."
    """
    journey_stage = get_current_journey()
    page = page or get_current_context()
    tone_guide = get_phase_tone()
    
    # Phase-specific guidance templates
    phase_messages = {
        "discovery": {
            "GCP": "Let's start by understanding your care needs. I'll guide you step-by-step through this assessment.",
            "Learn About My Recommendation": "Great! Let's explore what this care level means and how it can support your needs.",
            "Default": "I'm here to help you understand this important information. Take your time."
        },
        "planning": {
            "Cost Planner": "Now let's explore cost options together. I'm here to help you understand the numbers.",
            "PFMA": "Let's review your financial picture to help you make informed decisions.",
            "My Advisor": "I can help you connect with trusted professionals who specialize in senior care.",
            "Default": "Let's work through this planning step together. I'll help you understand your options."
        },
        "post_planning": {
            "CCR": "You're making excellent progress! Let's look at additional resources that might help.",
            "Additional Services": "Here are some additional services that could support your care plan.",
            "Default": "You're doing great! I'm here to support you through these next steps."
        }
    }
    
    # Get phase-specific message for this page
    try:
        return phase_messages[journey_stage].get(page, phase_messages[journey_stage]["Default"])
    except KeyError:
        # Fallback if journey stage unknown
        return tone_guide["example_phrases"][0] if tone_guide["example_phrases"] else None
