"""
MCIP v2 - Master Care Intelligence Panel

The Conductor: Orchestrates the user journey across all hubs, products, and modules.
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import streamlit as st


@dataclass
class CareRecommendation:
    """Standardized care recommendation contract published by GCP."""
    tier: str  # independent | in_home | assisted_living | memory_care
    tier_score: float  # 0-100 confidence score for recommended tier
    tier_rankings: List[Tuple[str, float]]  # All tiers ranked with scores
    confidence: float  # 0.0-1.0 (percent of required questions answered)
    flags: List[Dict[str, Any]]  # Risk/support flags (falls_risk, memory_support, etc.)
    rationale: List[str]  # Key reasons for recommendation
    generated_at: str  # ISO timestamp
    version: str  # GCP scoring rules version
    input_snapshot_id: str  # Unique ID for this input set
    rule_set: str  # Rule set identifier
    next_step: Dict[str, str]  # Suggested next product
    status: str  # new | in_progress | complete | needs_update
    last_updated: str  # ISO timestamp
    needs_refresh: bool  # True if inputs changed significantly


@dataclass
class FinancialProfile:
    """Standardized financial profile contract published by Cost Planner."""
    estimated_monthly_cost: float  # Monthly cost estimate
    coverage_percentage: float  # Percent covered by income/assets/insurance
    gap_amount: float  # Monthly gap to cover
    runway_months: int  # Months until funds depleted
    confidence: float  # 0.0-1.0 confidence in estimate
    generated_at: str  # ISO timestamp
    status: str  # new | in_progress | complete


@dataclass
class AdvisorAppointment:
    """Standardized appointment contract published by PFMA."""
    scheduled: bool
    date: str
    time: str
    type: str  # phone | video | in_person
    confirmation_id: str
    generated_at: str
    status: str  # scheduled | confirmed | cancelled


class MCIP:
    """Master Care Intelligence Panel - The Conductor.
    
    MCIP is the only system that reads across boundaries.
    - Sees all hubs, products, and outcomes
    - Publishes recommendations to st.session_state["mcip"]
    - Fires events when state changes
    - Maintains clean boundaries between layers
    """
    
    STATE_KEY = "mcip"
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize MCIP state structure if not exists.
        
        Called at app startup to ensure MCIP state is ready.
        """
        if cls.STATE_KEY not in st.session_state:
            st.session_state[cls.STATE_KEY] = {
                "care_recommendation": cls._default_care_recommendation(),
                "financial_profile": None,
                "advisor_appointment": None,
                "journey": {
                    "current_hub": "concierge",
                    "completed_products": [],
                    "unlocked_products": ["gcp"],  # GCP always unlocked
                    "recommended_next": "gcp"
                },
                "events": []
            }
    
    # =========================================================================
    # CARE RECOMMENDATION (Published by GCP)
    # =========================================================================
    
    @classmethod
    def get_care_recommendation(cls) -> Optional[CareRecommendation]:
        """Get the current care recommendation.
        
        Returns:
            CareRecommendation object or None if not generated yet
        """
        cls.initialize()
        rec_data = st.session_state[cls.STATE_KEY].get("care_recommendation")
        
        if rec_data and rec_data.get("status") not in ["new", None]:
            return CareRecommendation(**rec_data)
        return None
    
    @classmethod
    def publish_care_recommendation(cls, recommendation: CareRecommendation) -> None:
        """Publish a new care recommendation (called by GCP).
        
        This is the ONLY way to update care recommendation state.
        
        Args:
            recommendation: CareRecommendation dataclass
        """
        cls.initialize()
        
        # Store recommendation
        st.session_state[cls.STATE_KEY]["care_recommendation"] = asdict(recommendation)
        
        # Fire event
        cls._fire_event("mcip.recommendation.updated", {
            "tier": recommendation.tier,
            "confidence": recommendation.confidence,
            "generated_at": recommendation.generated_at
        })
        
        # Fire flags event if flags present
        if recommendation.flags:
            cls._fire_event("mcip.flags.updated", {
                "flags": [f["id"] for f in recommendation.flags]
            })
        
        # Update journey state
        cls._update_journey_after_recommendation(recommendation)
        
        # Refresh MCIP panels
        cls.refresh_panels()
    
    # =========================================================================
    # FINANCIAL PROFILE (Published by Cost Planner)
    # =========================================================================
    
    @classmethod
    def get_financial_profile(cls) -> Optional[FinancialProfile]:
        """Get the current financial profile.
        
        Returns:
            FinancialProfile object or None if not generated yet
        """
        cls.initialize()
        profile_data = st.session_state[cls.STATE_KEY].get("financial_profile")
        
        if profile_data:
            return FinancialProfile(**profile_data)
        return None
    
    @classmethod
    def publish_financial_profile(cls, profile: FinancialProfile) -> None:
        """Publish financial profile (called by Cost Planner).
        
        Args:
            profile: FinancialProfile dataclass
        """
        cls.initialize()
        st.session_state[cls.STATE_KEY]["financial_profile"] = asdict(profile)
        
        cls._fire_event("mcip.financial.updated", {
            "monthly_cost": profile.estimated_monthly_cost,
            "confidence": profile.confidence,
            "generated_at": profile.generated_at
        })
    
    # =========================================================================
    # ADVISOR APPOINTMENT (Published by PFMA)
    # =========================================================================
    
    @classmethod
    def get_advisor_appointment(cls) -> Optional[AdvisorAppointment]:
        """Get the current advisor appointment.
        
        Returns:
            AdvisorAppointment object or None if not scheduled
        """
        cls.initialize()
        appt_data = st.session_state[cls.STATE_KEY].get("advisor_appointment")
        
        if appt_data:
            return AdvisorAppointment(**appt_data)
        return None
    
    @classmethod
    def publish_appointment(cls, appointment: AdvisorAppointment) -> None:
        """Publish advisor appointment (called by PFMA).
        
        Args:
            appointment: AdvisorAppointment dataclass
        """
        cls.initialize()
        st.session_state[cls.STATE_KEY]["advisor_appointment"] = asdict(appointment)
        
        cls._fire_event("mcip.appointment.scheduled", {
            "date": appointment.date,
            "time": appointment.time,
            "type": appointment.type,
            "confirmation_id": appointment.confirmation_id
        })
    
    # =========================================================================
    # JOURNEY MANAGEMENT
    # =========================================================================
    
    @classmethod
    def get_unlocked_products(cls) -> List[str]:
        """Get list of products user can access.
        
        Returns:
            List of product keys (e.g., ["gcp", "cost_planner", "pfma"])
        """
        cls.initialize()
        return st.session_state[cls.STATE_KEY]["journey"]["unlocked_products"]
    
    @classmethod
    def is_product_unlocked(cls, product_key: str) -> bool:
        """Check if a product is unlocked.
        
        Args:
            product_key: Product identifier (e.g., "cost_planner")
        
        Returns:
            True if unlocked, False otherwise
        """
        return product_key in cls.get_unlocked_products()
    
    @classmethod
    def mark_product_complete(cls, product_key: str) -> None:
        """Mark a product as completed.
        
        Args:
            product_key: Product identifier
        """
        cls.initialize()
        journey = st.session_state[cls.STATE_KEY]["journey"]
        
        if product_key not in journey["completed_products"]:
            journey["completed_products"].append(product_key)
        
        cls._fire_event("mcip.product.completed", {"product": product_key})
    
    @classmethod
    def is_product_complete(cls, product_key: str) -> bool:
        """Check if a product is completed.
        
        Args:
            product_key: Product identifier
        
        Returns:
            True if complete, False otherwise
        """
        cls.initialize()
        journey = st.session_state[cls.STATE_KEY]["journey"]
        return product_key in journey["completed_products"]
    
    @classmethod
    def get_recommended_next_product(cls) -> Optional[str]:
        """Get MCIP's recommended next product.
        
        Returns:
            Product key or None
        """
        cls.initialize()
        return st.session_state[cls.STATE_KEY]["journey"].get("recommended_next")
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    @classmethod
    def refresh_panels(cls) -> None:
        """Clear cached MCIP panel markup to force re-render.
        
        Called after publishing new data to MCIP.
        """
        # Clear any cached components
        cache_keys = ["_mcip_panel_cache", "_hub_guide_cache", "_product_tiles_cache"]
        for key in cache_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    @classmethod
    def get_journey_progress(cls) -> Dict[str, Any]:
        """Get journey progress summary.
        
        Returns:
            Dict with completed count, unlocked count, recommended next
        """
        cls.initialize()
        journey = st.session_state[cls.STATE_KEY]["journey"]
        
        return {
            "completed_count": len(journey["completed_products"]),
            "unlocked_count": len(journey["unlocked_products"]),
            "recommended_next": journey.get("recommended_next"),
            "completed_products": journey["completed_products"],
            "unlocked_products": journey["unlocked_products"]
        }
    
    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================
    
    @classmethod
    def _fire_event(cls, event_type: str, payload: Dict[str, Any]) -> None:
        """Fire an MCIP event.
        
        Args:
            event_type: Event identifier (e.g., "mcip.recommendation.updated")
            payload: Event data
        """
        cls.initialize()
        
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload
        }
        
        st.session_state[cls.STATE_KEY]["events"].append(event)
        
        # Emit to event bus (if implemented)
        try:
            from core.mcip_events import MCIPEventBus
            MCIPEventBus.emit(event_type, payload)
        except ImportError:
            pass  # Event bus not yet implemented
        
        # Log to analytics (if implemented)
        try:
            from core.events import log_event
            log_event(event_type, payload)
        except ImportError:
            pass  # Analytics not yet implemented
    
    @classmethod
    def _update_journey_after_recommendation(cls, recommendation: CareRecommendation) -> None:
        """Update journey state after new recommendation.
        
        Args:
            recommendation: CareRecommendation dataclass
        """
        journey = st.session_state[cls.STATE_KEY]["journey"]
        
        # Mark GCP as complete
        if "gcp" not in journey["completed_products"]:
            journey["completed_products"].append("gcp")
        
        # Unlock next products
        journey["unlocked_products"] = ["gcp", "cost_planner", "pfma"]
        
        # Set recommended next from recommendation
        journey["recommended_next"] = recommendation.next_step.get("product", "cost_planner")
    
    @classmethod
    def _default_care_recommendation(cls) -> Dict[str, Any]:
        """Default care recommendation when GCP hasn't run.
        
        Returns:
            Default recommendation dict
        """
        return {
            "tier": None,
            "tier_score": 0,
            "tier_rankings": [],
            "confidence": 0.0,
            "flags": [],
            "rationale": [],
            "generated_at": None,
            "version": None,
            "input_snapshot_id": None,
            "rule_set": None,
            "next_step": {
                "product": "gcp",
                "route": "gcp",
                "label": "Complete Guided Care Plan",
                "reason": "Get your personalized care recommendation"
            },
            "status": "new",
            "last_updated": None,
            "needs_refresh": False
        }


# =============================================================================
# BACKWARD COMPATIBILITY HELPERS (Temporary during migration)
# =============================================================================

def get_care_tier_legacy_compatible() -> Optional[str]:
    """Get care tier from MCIP or legacy GCP state.
    
    Temporary helper during migration to support both patterns.
    
    Returns:
        Care tier string or None
    """
    # Try MCIP first (v2)
    rec = MCIP.get_care_recommendation()
    if rec:
        return rec.tier
    
    # Fall back to legacy (v1)
    gcp_state = st.session_state.get("gcp", {})
    return gcp_state.get("recommended_tier")


def get_care_confidence_legacy_compatible() -> float:
    """Get care confidence from MCIP or legacy GCP state.
    
    Returns:
        Confidence float (0.0-1.0)
    """
    # Try MCIP first
    rec = MCIP.get_care_recommendation()
    if rec:
        return rec.confidence
    
    # Fall back to legacy
    gcp_state = st.session_state.get("gcp", {})
    return gcp_state.get("confidence", 0.0)
