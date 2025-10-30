"""
NAVI Core API - Public interface for question answering.
"""

from typing import Optional, List
from apps.navi_core.models import NaviAnswer
from apps.navi_core.orchestrator import NaviOrchestrator

# Global orchestrator instance
_orchestrator: Optional[NaviOrchestrator] = None


def _get_orchestrator() -> NaviOrchestrator:
    """Get or create global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = NaviOrchestrator()
    return _orchestrator


def get_answer(question: str, name: Optional[str] = None, tags: Optional[List[str]] = None,
               source: Optional[str] = None, conversation_id: Optional[str] = None, mode: str = "assist",
               enable_tone: bool = True) -> NaviAnswer:
    """Get answer from NAVI Core with tone personalization.
    
    Primary entry point for NAVI question answering.
    Routes through multi-tier pipeline (FAQ → RAG → LLM) with emotional adaptation.
    
    Args:
        question: User's question
        name: User's name for personalization (optional)
        tags: Context tags like ["gcp", "cost_planner"] (optional)
        source: Source of question, e.g., "hub", "faq_page" (optional)
        conversation_id: Conversation ID for context tracking (optional)
        mode: Operation mode - "assist", "adjust", or "shadow" (default: "assist")
        enable_tone: Enable tone personalization based on sentiment (default: True)
    
    Returns:
        NaviAnswer with answer text, tier used, confidence, validation, and sources
    
    Example:
        >>> # Basic usage with tone personalization
        >>> answer = get_answer("I'm worried about moving my mom to assisted living")
        >>> print(answer.answer)  # Empathetic tone applied
        
        >>> # Disable tone personalization for clinical responses
        >>> answer = get_answer("What is assisted living?", enable_tone=False)
    """
    orch = _get_orchestrator()
    return orch.answer(question, name, tags, source, conversation_id, mode, enable_tone)


def reload_config() -> None:
    """Reload configuration (FAQ, prompts, tones) from disk."""
    global _orchestrator
    if _orchestrator is not None:
        _orchestrator.faq.reload()
        _orchestrator.prompt_manager.reload()
        _orchestrator.tone_adapter.reload()
        print("[NAVI_API] Configuration reloaded (FAQ, prompts, tones)")
    else:
        print("[NAVI_API] No orchestrator to reload")


def clear_conversation(conversation_id: str) -> None:
    """Clear conversation history for a given conversation ID."""
    orch = _get_orchestrator()
    orch.clear_conversation(conversation_id)
