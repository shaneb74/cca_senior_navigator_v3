"""
MCIP Event Bus - Event-driven integration for MCIP v2

Provides pub/sub pattern for MCIP events so hubs and products can
react to state changes without tight coupling.
"""

from typing import Callable, Dict, List, Any, Optional


class MCIPEventBus:
    """Simple event bus for MCIP event subscriptions.
    
    Usage:
        # Subscribe
        MCIPEventBus.subscribe("mcip.recommendation.updated", my_callback)
        
        # Emit
        MCIPEventBus.emit("mcip.recommendation.updated", {"tier": "assisted_living"})
    """
    
    _listeners: Dict[str, List[Callable]] = {}
    
    @classmethod
    def subscribe(cls, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to an MCIP event.
        
        Args:
            event_type: Event identifier (e.g., "mcip.recommendation.updated")
            callback: Function to call when event fires, receives payload dict
        """
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        
        if callback not in cls._listeners[event_type]:
            cls._listeners[event_type].append(callback)
    
    @classmethod
    def unsubscribe(cls, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an MCIP event.
        
        Args:
            event_type: Event identifier
            callback: Previously subscribed callback function
        """
        if event_type in cls._listeners:
            try:
                cls._listeners[event_type].remove(callback)
            except ValueError:
                pass  # Callback not in list
    
    @classmethod
    def emit(cls, event_type: str, payload: Dict[str, Any]) -> None:
        """Emit an MCIP event to all subscribers.
        
        Args:
            event_type: Event identifier
            payload: Event data
        """
        if event_type in cls._listeners:
            for callback in cls._listeners[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    # Log error but don't crash
                    print(f"[MCIPEventBus] Error in listener for {event_type}: {e}")
    
    @classmethod
    def clear(cls, event_type: Optional[str] = None) -> None:
        """Clear event listeners.
        
        Args:
            event_type: Optional specific event type to clear, or None to clear all
        """
        if event_type:
            if event_type in cls._listeners:
                cls._listeners[event_type] = []
        else:
            cls._listeners = {}
    
    @classmethod
    def get_listeners(cls, event_type: str) -> List[Callable]:
        """Get all listeners for an event type.
        
        Args:
            event_type: Event identifier
        
        Returns:
            List of callback functions
        """
        return cls._listeners.get(event_type, [])


# =============================================================================
# COMMON EVENT LISTENERS (Register at app startup)
# =============================================================================

def on_recommendation_updated(payload: Dict[str, Any]) -> None:
    """Called when care recommendation changes.
    
    Clears cached hub guide panels and logs analytics.
    """
    import streamlit as st
    
    # Clear cached guide panel
    if "_hub_guide_cache" in st.session_state:
        del st.session_state["_hub_guide_cache"]
    
    # Clear product tiles cache
    if "_product_tiles_cache" in st.session_state:
        del st.session_state["_product_tiles_cache"]
    
    # Log analytics (if available)
    try:
        from core.events import log_event
        log_event("mcip.recommendation.viewed", {
            "tier": payload.get("tier"),
            "confidence": payload.get("confidence")
        })
    except ImportError:
        pass


def on_flags_updated(payload: Dict[str, Any]) -> None:
    """Called when risk/support flags change.
    
    Can trigger notifications to Learning Hub, Partners Hub, etc.
    """
    flags = payload.get("flags", [])
    
    # Log flag detection
    try:
        from core.events import log_event
        for flag_id in flags:
            log_event("mcip.flag.detected", {"flag_id": flag_id})
    except ImportError:
        pass


def on_financial_updated(payload: Dict[str, Any]) -> None:
    """Called when financial profile is published."""
    try:
        from core.events import log_event
        log_event("mcip.financial.completed", {
            "monthly_cost": payload.get("monthly_cost"),
            "confidence": payload.get("confidence")
        })
    except ImportError:
        pass


def on_appointment_scheduled(payload: Dict[str, Any]) -> None:
    """Called when advisor appointment is scheduled."""
    try:
        from core.events import log_event
        log_event("mcip.appointment.completed", {
            "date": payload.get("date"),
            "type": payload.get("type")
        })
    except ImportError:
        pass


def register_default_listeners() -> None:
    """Register default MCIP event listeners.
    
    Call this at app startup after MCIP.initialize().
    """
    MCIPEventBus.subscribe("mcip.recommendation.updated", on_recommendation_updated)
    MCIPEventBus.subscribe("mcip.flags.updated", on_flags_updated)
    MCIPEventBus.subscribe("mcip.financial.updated", on_financial_updated)
    MCIPEventBus.subscribe("mcip.appointment.scheduled", on_appointment_scheduled)
