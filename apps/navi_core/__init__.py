"""
NAVI Core - Tiered AI Answer System with Profile-Driven Personalization

Public API for NAVI (Navigational AI) with emotional intelligence and
persona-aware journey tracking.
"""

__version__ = "0.4.1"

from apps.navi_core.api import get_answer, reload_config, clear_conversation
from apps.navi_core.models import NaviAnswer, ValidationResult, ChunkMetadata, UserProfile, JourneyEvent
from apps.navi_core.tone_adapter import ToneAdapter
from apps.navi_core.sentiment import SentimentAnalyzer
from apps.navi_core.persona_adapter import PersonaAdapter, RoleDetection, PERSONA_CHOICES
from apps.navi_core.journey_manager import JourneyManager
from apps.navi_core.profile_manager import ProfileManager
from apps.navi_core.context_manager import update_context, get_current_context
from apps.navi_core.guidance_manager import get_guidance, load_guidance
from apps.navi_core.trigger_manager import should_show, reset_triggers, get_trigger_stats

__all__ = [
    "get_answer",
    "reload_config", 
    "clear_conversation",
    "NaviAnswer",
    "ValidationResult",
    "ChunkMetadata",
    "UserProfile",
    "JourneyEvent",
    "ToneAdapter",
    "SentimentAnalyzer",
    "PersonaAdapter",
    "RoleDetection",
    "PERSONA_CHOICES",
    "JourneyManager",
    "ProfileManager",
    "update_context",
    "get_current_context",
    "get_guidance",
    "load_guidance",
    "should_show",
    "reset_triggers",
    "get_trigger_stats",
]
