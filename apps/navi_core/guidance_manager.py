"""
Guidance Manager - Retrieves persona-specific contextual guidance messages.

Part of Phase 5: Contextual Guidance Layer
Provides adaptive, empathetic guidance based on current page and user persona.
"""

import yaml
from pathlib import Path
from typing import Optional

from apps.navi_core.context_manager import get_current_context
from apps.navi_core.profile_manager import ProfileManager


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


def get_guidance(page: Optional[str] = None, persona: Optional[str] = None) -> str:
    """
    Return persona-specific guidance message for the active page.
    
    Args:
        page: Page name (if None, uses get_current_context())
        persona: User persona/role (if None, uses profile_manager)
        
    Returns:
        Guidance message string tailored to page + persona
        
    Example:
        >>> get_guidance(page="Welcome", persona="AdultChild")
        "Welcome! I'll help you explore care options for your parent."
    """
    data = load_guidance()
    
    # Determine page context
    page = page or get_current_context()
    
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
