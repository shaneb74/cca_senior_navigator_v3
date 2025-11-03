"""
MCIP v2 - Master Care Intelligence Panel

The Conductor: Orchestrates the user journey across all hubs, products, and modules.
"""

from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from typing import Any, Optional

import streamlit as st


@dataclass
class CareRecommendation:
    """Standardized care recommendation contract published by GCP."""

    tier: str  # independent | in_home | assisted_living | memory_care
    tier_score: float  # 0-100 confidence score for recommended tier
    tier_rankings: list[tuple[str, float]]  # All tiers ranked with scores
    confidence: float  # 0.0-1.0 (percent of required questions answered)
    flags: list[dict[str, Any]]  # Risk/support flags (falls_risk, memory_support, etc.)
    rationale: list[str]  # Key reasons for recommendation
    generated_at: str  # ISO timestamp
    version: str  # GCP scoring rules version
    input_snapshot_id: str  # Unique ID for this input set
    rule_set: str  # Rule set identifier
    next_step: dict[str, str]  # Suggested next product
    status: str  # new | in_progress | complete | needs_update
    last_updated: str  # ISO timestamp
    needs_refresh: bool  # True if inputs changed significantly
    allowed_tiers: Optional[list[str]] = field(default=None)  # Tiers allowed after gates
    schema_version: int = 2  # Contract version for backward compatibility


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
    """Standardized appointment contract published by PFMA v3."""

    scheduled: bool
    date: str
    time: str
    type: str  # phone | video | in_person
    confirmation_id: str
    contact_email: str
    contact_phone: str
    timezone: str
    notes: str
    generated_at: str
    status: str  # scheduled | confirmed | cancelled
    prep_sections_complete: list  # ["personal", "financial", ...]
    prep_progress: int  # 0-100


class MCIP:
    """Master Care Intelligence Panel - The Conductor.

    MCIP is the only system that reads across boundaries.
    - Sees all hubs, products, and outcomes
    - Publishes recommendations to st.session_state["mcip"]
    - Fires events when state changes
    - Maintains clean boundaries between layers
    
    Product Completion Coordination:
        All products mark completion through MCIP.mark_product_complete(key).
        Keys are automatically normalized to canonical forms:
        - "gcp_v4", "guided_care_plan" → "gcp"
        - "cost_v2", "cost_planner_v2", "cost_intro" → "cost_planner"
        - "pfma_v3", "my_advisor" → "pfma"
        
        Example:
            MCIP.mark_product_complete("gcp_v4")  # Stored as "gcp"
    """

    STATE_KEY = "mcip"
    
    # Product key normalization map - canonical keys for completion tracking
    PRODUCT_KEY_MAP = {
        # GCP aliases
        "gcp_v4": "gcp",
        "gcp": "gcp",
        "guided_care_plan": "gcp",
        
        # Cost Planner aliases
        "cost_v2": "cost_planner",
        "cost_planner_v2": "cost_planner",
        "cost_intro": "cost_planner",
        "cost_planner": "cost_planner",
        
        # PFMA aliases
        "pfma_v3": "pfma",
        "pfma": "pfma",
        "my_advisor": "pfma",
        
        # Learning products (already canonical)
        "discovery_learning": "discovery_learning",
        "learn_recommendation": "learn_recommendation",
    }

    @classmethod
    def _normalize_product_key(cls, product_key: str) -> str:
        """Normalize product key to canonical form.
        
        Args:
            product_key: Raw product key from caller
            
        Returns:
            Normalized canonical key
            
        Examples:
            >>> MCIP._normalize_product_key("gcp_v4")
            "gcp"
            >>> MCIP._normalize_product_key("cost_v2")
            "cost_planner"
        """
        return cls.PRODUCT_KEY_MAP.get(product_key, product_key)

    @classmethod
    def initialize(cls) -> None:
        """Initialize MCIP state structure if not exists.

        Called at app startup to ensure MCIP state is ready.
        Handles partial state from persistence by filling in missing keys.
        Restores contracts from mcip_contracts if available.
        """
        # Default structure
        default_state = {
            "care_recommendation": cls._default_care_recommendation(),
            "financial_profile": None,
            "advisor_appointment": None,
            "journey": {
                "current_hub": "concierge",
                "completed_products": [],
                "unlocked_products": ["gcp"],  # GCP always unlocked
                "recommended_next": "gcp",
            },
            "waiting_room": {
                "advisor_prep_status": "not_started",  # not_started | in_progress | complete
                "trivia_status": "not_started",  # not_started | in_progress | complete
                "current_focus": "advisor_prep",  # advisor_prep | trivia | learning
            },
            "events": [],
        }

        if cls.STATE_KEY not in st.session_state:
            # Fresh initialization
            st.session_state[cls.STATE_KEY] = default_state
        else:
            # Merge with existing state (fill in missing keys)
            existing = st.session_state[cls.STATE_KEY]

            # Ensure all top-level keys exist
            for key, default_value in default_state.items():
                if key not in existing:
                    existing[key] = default_value
                elif key == "journey" and isinstance(existing[key], dict):
                    # Ensure all journey sub-keys exist
                    for journey_key, journey_default in default_state["journey"].items():
                        if journey_key not in existing[key]:
                            existing[key][journey_key] = journey_default
                elif key == "waiting_room" and isinstance(existing[key], dict):
                    # Ensure all waiting_room sub-keys exist
                    for wr_key, wr_default in default_state["waiting_room"].items():
                        if wr_key not in existing[key]:
                            existing[key][wr_key] = wr_default

        # CRITICAL FIX: Always restore from mcip_contracts if available
        # This ensures that completion state persists even if mcip state exists
        # but has stale/incomplete data (e.g., after navigating between pages)
        # IMPORTANT: Use deepcopy for ALL nested dicts/lists to prevent shared references
        restored_from_contracts = False
        if "mcip_contracts" in st.session_state:
            import copy

            contracts = st.session_state["mcip_contracts"]

            if "care_recommendation" in contracts and contracts["care_recommendation"]:
                st.session_state[cls.STATE_KEY]["care_recommendation"] = copy.deepcopy(
                    contracts["care_recommendation"]
                )

            if "financial_profile" in contracts and contracts["financial_profile"]:
                st.session_state[cls.STATE_KEY]["financial_profile"] = copy.deepcopy(
                    contracts["financial_profile"]
                )

            if "advisor_appointment" in contracts and contracts["advisor_appointment"]:
                st.session_state[cls.STATE_KEY]["advisor_appointment"] = copy.deepcopy(
                    contracts["advisor_appointment"]
                )

            if "journey" in contracts and contracts["journey"]:
                # CRITICAL: Always restore journey state from contracts
                # Use deepcopy to avoid shared references between mcip and mcip_contracts
                # This ensures modifying mcip["journey"] doesn't corrupt mcip_contracts["journey"]
                st.session_state[cls.STATE_KEY]["journey"] = copy.deepcopy(contracts["journey"])

            if "waiting_room" in contracts and contracts["waiting_room"]:
                # Restore waiting room tracking state
                st.session_state[cls.STATE_KEY]["waiting_room"] = copy.deepcopy(
                    contracts["waiting_room"]
                )

            restored_from_contracts = True
        else:
            # Preserve existing journey data when no contracts found
            existing_journey = st.session_state[cls.STATE_KEY].get("journey", {})
            existing_unlocked = existing_journey.get("unlocked_products", [])
            existing_completed = existing_journey.get("completed_products", [])
            should_preserve = len(existing_unlocked) > 1 or len(existing_completed) > 0

        # CRITICAL FIX: Only save contracts if we created fresh state (NOT if we restored)
        # If we restored from contracts, those contracts are already the source of truth
        # Saving here would be redundant and could overwrite in-memory updates
        if not restored_from_contracts:
            cls._save_contracts_for_persistence()

    # =========================================================================
    # CARE RECOMMENDATION (Published by GCP)
    # =========================================================================

    @classmethod
    def get_care_recommendation(cls) -> CareRecommendation | None:
        """Get the current care recommendation.

        Returns:
            CareRecommendation object or None if not generated yet
        """
        cls.initialize()
        rec_data = st.session_state[cls.STATE_KEY].get("care_recommendation")

        if rec_data and rec_data.get("status") not in ["new", None]:
            # Filter to only the fields expected by CareRecommendation dataclass
            # This handles demo profiles with extra fields (assessment_data, scores, etc.)
            valid_fields = {f.name for f in fields(CareRecommendation)}
            filtered_data = {k: v for k, v in rec_data.items() if k in valid_fields}
            
            # DEBUG: Check for missing required fields
            missing_fields = valid_fields - set(filtered_data.keys())
            if missing_fields:
                print(f"[MCIP WARNING] Missing CareRecommendation fields: {missing_fields}")
                print(f"[MCIP] Available fields: {list(filtered_data.keys())}")
                print(f"[MCIP] rec_data keys: {list(rec_data.keys())}")
            
            return CareRecommendation(**filtered_data)
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

        # Save for persistence
        cls._save_contracts_for_persistence()

        # Fire event
        cls._fire_event(
            "mcip.recommendation.updated",
            {
                "tier": recommendation.tier,
                "confidence": recommendation.confidence,
                "generated_at": recommendation.generated_at,
            },
        )

        # Fire flags event if flags present
        if recommendation.flags:
            cls._fire_event(
                "mcip.flags.updated", {"flags": [f["id"] for f in recommendation.flags]}
            )

        # Update journey state
        cls._update_journey_after_recommendation(recommendation)

        # Refresh MCIP panels
        cls.refresh_panels()

    # =========================================================================
    # FINANCIAL PROFILE (Published by Cost Planner)
    # =========================================================================

    @classmethod
    def get_financial_profile(cls) -> FinancialProfile | None:
        """Get the current financial profile.

        Returns:
            FinancialProfile object or None if not generated yet
        """
        cls.initialize()
        profile_data = st.session_state[cls.STATE_KEY].get("financial_profile")

        if profile_data:
            # Filter to only the fields expected by FinancialProfile dataclass
            # This handles demo profiles with extra fields (monthly_income, total_liquid_assets, etc.)
            valid_fields = {f.name for f in fields(FinancialProfile)}
            filtered_data = {k: v for k, v in profile_data.items() if k in valid_fields}
            return FinancialProfile(**filtered_data)
        return None

    @classmethod
    def publish_financial_profile(cls, profile: FinancialProfile) -> None:
        """Publish financial profile (called by Cost Planner).

        Args:
            profile: FinancialProfile dataclass
        """
        cls.initialize()
        st.session_state[cls.STATE_KEY]["financial_profile"] = asdict(profile)

        # Save for persistence
        cls._save_contracts_for_persistence()

        cls._fire_event(
            "mcip.financial.updated",
            {
                "monthly_cost": profile.estimated_monthly_cost,
                "confidence": profile.confidence,
                "generated_at": profile.generated_at,
            },
        )

    # =========================================================================
    # ADVISOR APPOINTMENT (Published by PFMA)
    # =========================================================================

    @classmethod
    def get_advisor_appointment(cls) -> AdvisorAppointment | None:
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

        # Save for persistence
        cls._save_contracts_for_persistence()

        cls._fire_event(
            "mcip.appointment.scheduled",
            {
                "date": appointment.date,
                "time": appointment.time,
                "type": appointment.type,
                "confirmation_id": appointment.confirmation_id,
            },
        )

    @classmethod
    def set_advisor_appointment(cls, appointment: AdvisorAppointment) -> None:
        """Alias for publish_appointment (used by PFMA v3 and Advisor Prep).

        Args:
            appointment: AdvisorAppointment dataclass
        """
        cls.publish_appointment(appointment)

    @classmethod
    def get_pfma_summary(cls) -> dict:
        """Get PFMA booking status for Concierge tile display.

        Returns:
            {
                "booked": bool,
                "appointment_date": str,
                "appointment_time": str,
                "confirmation_id": str,
                "route": str,  # "pfma_v3" or "advisor_prep"
                "next_action": str,  # "Book Appointment" or "View Prep"
                "prep_progress": int  # 0-100
            }
        """
        cls.initialize()
        appt = cls.get_advisor_appointment()

        if not appt or not appt.scheduled:
            return {
                "booked": False,
                "route": "pfma_v3",
                "next_action": "Book Appointment",
                "prep_progress": 0,
            }

        return {
            "booked": True,
            "appointment_date": appt.date,
            "appointment_time": appt.time,
            "confirmation_id": appt.confirmation_id,
            "route": "advisor_prep" if appt.prep_progress < 100 else "hub_lobby",
            "next_action": "Complete Prep" if appt.prep_progress < 100 else "All Set",
            "prep_progress": appt.prep_progress,
        }

    @classmethod
    def get_advisor_prep_summary(cls) -> dict:
        """Get Advisor Prep status for Waiting Room tile.

        Returns:
            {
                "available": bool,
                "sections_complete": list,
                "progress": int,  # 0-100
                "next_section": str,  # "personal" | "financial" | etc.
                "appointment_context": str  # "Your appointment is in 8 days"
            }
        """
        cls.initialize()
        appt = cls.get_advisor_appointment()

        if not appt or not appt.scheduled:
            return {"available": False}

        sections_complete = appt.prep_sections_complete or []
        progress = appt.prep_progress or 0

        all_sections = ["personal", "financial", "housing", "medical"]
        remaining = [s for s in all_sections if s not in sections_complete]
        next_section = remaining[0] if remaining else None

        # Calculate days until appointment
        from datetime import datetime

        try:
            appt_date = datetime.fromisoformat(appt.date)
            days_until = (appt_date - datetime.now()).days
            if days_until == 0:
                context = f"Your appointment is today at {appt.time}"
            elif days_until == 1:
                context = f"Your appointment is tomorrow at {appt.time}"
            elif days_until > 1:
                context = f"Your appointment is in {days_until} days"
            else:
                context = f"Your appointment: {appt.date} at {appt.time}"
        except:
            context = f"Your appointment: {appt.date} at {appt.time}"

        return {
            "available": True,
            "sections_complete": sections_complete,
            "progress": progress,
            "next_section": next_section,
            "appointment_context": context,
        }

    # =========================================================================
    # WAITING ROOM TRACKING (Progress across Advisor Prep → Trivia → Learning)
    # =========================================================================

    @classmethod
    def get_waiting_room_state(cls) -> dict:
        """Get current Waiting Room progress state.

        Returns:
            {
                "advisor_prep_status": "not_started" | "in_progress" | "complete",
                "trivia_status": "not_started" | "in_progress" | "complete",
                "current_focus": "advisor_prep" | "trivia" | "learning"
            }
        """
        cls.initialize()
        return st.session_state[cls.STATE_KEY].get(
            "waiting_room",
            {
                "advisor_prep_status": "not_started",
                "trivia_status": "not_started",
                "current_focus": "advisor_prep",
            },
        )

    @classmethod
    def update_advisor_prep_status(cls, status: str) -> None:
        """Update Advisor Prep status and adjust current_focus if needed.

        Args:
            status: "not_started" | "in_progress" | "complete"
        """
        cls.initialize()
        waiting_room = st.session_state[cls.STATE_KEY]["waiting_room"]
        waiting_room["advisor_prep_status"] = status

        # If Advisor Prep is complete, shift focus to Trivia
        if status == "complete" and waiting_room["current_focus"] == "advisor_prep":
            waiting_room["current_focus"] = "trivia"

        # Save for persistence
        cls._save_contracts_for_persistence()

        cls._fire_event("mcip.waiting_room.advisor_prep_updated", {"status": status})

    @classmethod
    def update_trivia_status(cls, status: str) -> None:
        """Update Trivia status and adjust current_focus if needed.

        Args:
            status: "not_started" | "in_progress" | "complete"
        """
        cls.initialize()
        waiting_room = st.session_state[cls.STATE_KEY]["waiting_room"]
        waiting_room["trivia_status"] = status

        # If Trivia is complete, shift focus to Learning
        if status == "complete" and waiting_room["current_focus"] == "trivia":
            waiting_room["current_focus"] = "learning"

        # Save for persistence
        cls._save_contracts_for_persistence()

        cls._fire_event("mcip.waiting_room.trivia_updated", {"status": status})

    @classmethod
    def set_waiting_room_focus(cls, focus: str) -> None:
        """Manually set Waiting Room current focus.

        Args:
            focus: "advisor_prep" | "trivia" | "learning"
        """
        cls.initialize()
        st.session_state[cls.STATE_KEY]["waiting_room"]["current_focus"] = focus
        cls._save_contracts_for_persistence()

    # =========================================================================
    # JOURNEY MANAGEMENT
    # =========================================================================

    @classmethod
    def _save_contracts_for_persistence(cls) -> None:
        """Save MCIP contracts to session state for persistence.

        This allows session_store to persist contracts separately from
        the full MCIP state structure (which is reconstructed on load).

        Also saves journey state (unlocked_products, completed_products)
        so progress is preserved across sessions.

        CRITICAL: Uses deepcopy for ALL contracts to prevent shared references.
        Without this, modifying mcip data would also modify mcip_contracts data.
        """
        if cls.STATE_KEY in st.session_state:
            import copy

            contracts = {
                "care_recommendation": copy.deepcopy(
                    st.session_state[cls.STATE_KEY].get("care_recommendation")
                ),
                "financial_profile": copy.deepcopy(
                    st.session_state[cls.STATE_KEY].get("financial_profile")
                ),
                "advisor_appointment": copy.deepcopy(
                    st.session_state[cls.STATE_KEY].get("advisor_appointment")
                ),
                "journey": copy.deepcopy(
                    st.session_state[cls.STATE_KEY].get("journey")
                ),  # CRITICAL: deepcopy to prevent shared reference
                "waiting_room": copy.deepcopy(
                    st.session_state[cls.STATE_KEY].get("waiting_room")
                ),  # Track Waiting Room progress
            }
            st.session_state["mcip_contracts"] = contracts

    @classmethod
    def get_unlocked_products(cls) -> list[str]:
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
            product_key: Product identifier (will be normalized)

        Returns:
            True if unlocked, False otherwise
        """
        normalized_key = cls._normalize_product_key(product_key)
        return normalized_key in cls.get_unlocked_products()

    @classmethod
    def mark_product_complete(cls, product_key: str) -> None:
        """Mark a product as completed.

        Args:
            product_key: Product identifier (will be normalized to canonical form)
            
        Note:
            Keys are automatically normalized:
            - "gcp_v4" → "gcp"
            - "cost_v2", "cost_planner_v2" → "cost_planner"
            - "pfma_v3" → "pfma"
        """
        cls.initialize()
        
        # Normalize key to canonical form
        normalized_key = cls._normalize_product_key(product_key)
        
        journey = st.session_state[cls.STATE_KEY]["journey"]

        if normalized_key not in journey["completed_products"]:
            journey["completed_products"].append(normalized_key)
            print(f"[MCIP] Product '{product_key}' → '{normalized_key}' marked complete")

        # Save journey state for persistence
        cls._save_contracts_for_persistence()

        cls._fire_event("mcip.product.completed", {
            "product": normalized_key,
            "original_key": product_key
        })

    @classmethod
    def is_product_complete(cls, product_key: str) -> bool:
        """Check if a product is completed.

        Args:
            product_key: Product identifier (will be normalized)

        Returns:
            True if complete, False otherwise
        """
        cls.initialize()
        
        # Normalize key to canonical form
        normalized_key = cls._normalize_product_key(product_key)
        
        journey = st.session_state[cls.STATE_KEY]["journey"]
        return normalized_key in journey["completed_products"]

    @classmethod
    def get_recommended_next_product(cls) -> str | None:
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
    def get_journey_progress(cls) -> dict[str, Any]:
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
            "unlocked_products": journey["unlocked_products"],
        }

    @classmethod
    def get_recommended_next_action(cls) -> dict[str, str]:
        """Get user-friendly guidance for what to do next.

        Returns MCIP's recommendation with:
        - action: What to do ("Complete your care plan", "Calculate costs", etc.)
        - reason: Why they should do it
        - route: Where to navigate
        - status: Journey phase (getting_started | in_progress | nearly_there | complete)

        Returns:
            Dict with action, reason, route, status
        """
        cls.initialize()
        journey = st.session_state[cls.STATE_KEY]["journey"]
        completed = journey["completed_products"]
        tiles = st.session_state.get("tiles", {})

        def _get_tile(*keys: str) -> dict[str, Any]:
            for key in keys:
                tile = tiles.get(key)
                if isinstance(tile, dict):
                    return tile
            return {}

        def _tile_has_progress(tile: dict[str, Any]) -> bool:
            if not tile:
                return False
            try:
                if float(tile.get("progress", 0) or 0) > 0:
                    return True
            except Exception:
                pass
            try:
                if int(tile.get("last_step", 0) or 0) > 0:
                    return True
            except Exception:
                pass
            return False

        gcp_tile = _get_tile("gcp_v4", "gcp")
        cost_tile = _get_tile("cost_v2", "cost_planner", "cost")
        pfma_tile = _get_tile("pfma_v2", "pfma")

        # Complete - All done!
        if "gcp" in completed and "cost_planner" in completed and "pfma_v2" in completed:
            return {
                "action": "🎉 Journey Complete!",
                "reason": "You've completed your care plan, cost analysis, and scheduled your advisor appointment.",
                "route": "hub_lobby",
                "status": "complete",
            }

        # Nearly there - Just PFMA left
        if "gcp" in completed and "cost_planner" in completed:
            if _tile_has_progress(pfma_tile) and "pfma_v2" not in completed:
                return {
                    "action": "📅 Resume Plan with My Advisor",
                    "reason": "Pick up where you left off to finish scheduling with your advisor.",
                    "route": "pfma_v2",
                    "status": "in_progress",
                }
            return {
                "action": "📅 Schedule Your Advisor Appointment",
                "reason": "Meet with an advisor to finalize your plan and answer questions.",
                "route": "pfma_v2",
                "status": "nearly_there",
            }

        # In progress - GCP done, Cost Planner next
        if "gcp" in completed:
            if _tile_has_progress(cost_tile) and "cost_planner" not in completed:
                return {
                    "action": "💰 Resume Your Cost Planner",
                    "reason": "Continue estimating monthly costs with your saved answers.",
                    "route": "cost_intro",
                    "status": "in_progress",
                }
            return {
                "action": "💰 Calculate Your Care Costs",
                "reason": "Understand the financial side of your care plan.",
                "route": "cost_intro",
                "status": "in_progress",
            }

        # Guided Care Plan started but not finished
        if _tile_has_progress(gcp_tile):
            return {
                "action": "🧭 Resume Your Guided Care Plan",
                "reason": "Pick up where you left off. We saved your progress.",
                "route": "gcp_v4",
                "status": "in_progress",
            }

        # Getting started - Start with GCP
        return {
            "action": "🧭 Create Your Guided Care Plan",
            "reason": "Get a personalized care recommendation based on your needs.",
            "route": "gcp_v4",
            "status": "getting_started",
        }

    @classmethod
    def get_product_summary(cls, product_key: str) -> dict[str, Any] | None:
        """Get summary info for a product tile.

        Pulls relevant data from MCIP contracts to show on product tiles.

        Args:
            product_key: "gcp", "cost_planner", or "pfma"

        Returns:
            Dict with title, status, summary_line, icon, or None if not available
        """
        cls.initialize()

        if product_key in ["gcp", "gcp_v4"]:
            rec = cls.get_care_recommendation()
            if rec and rec.tier:
                # CRITICAL: These are the ONLY 5 allowed tier display names
                tier_map = {
                    "no_care_needed": "No Care Needed",
                    "in_home": "In-Home Care",
                    "assisted_living": "Assisted Living",
                    "memory_care": "Memory Care",
                    "memory_care_high_acuity": "Memory Care (High Acuity)",
                }
                tier_label = tier_map.get(rec.tier, rec.tier.replace("_", " ").title())
                # Use confidence (0-1 decimal) not tier_score (raw score 0-100)
                confidence_pct = int(rec.confidence * 100)

                return {
                    "title": "Guided Care Plan",
                    "status": "complete",
                    "summary_line": f"✅ {tier_label} ({confidence_pct}% confidence)",
                    "icon": "🧭",
                    "route": "gcp_v4",
                }
            else:
                return {
                    "title": "Guided Care Plan",
                    "status": "not_started",
                    "summary_line": "Get your personalized care recommendation",
                    "icon": "🧭",
                    "route": "gcp_v4",
                }

        elif product_key in ["cost_planner", "cost_v2"]:
            profile = cls.get_financial_profile()
            if profile:
                # Get the detailed summary message from session state if available
                financial_data = st.session_state.get("financial_assessment_complete", {})
                timeline = financial_data.get("timeline", {})
                summary_message = timeline.get("summary_message")

                if summary_message:
                    # Use the detailed, user-friendly message
                    return {
                        "title": "Cost Planner",
                        "status": "complete",
                        "summary_line": f"✅ {summary_message}",
                        "icon": "💰",
                        "route": "cost_intro",
                    }
                else:
                    # Fallback to old format
                    cost_str = f"${profile.estimated_monthly_cost:,.0f}/month"
                    runway_str = (
                        f"{profile.runway_months} month runway"
                        if profile.runway_months > 0
                        else "Review needed"
                    )

                    return {
                        "title": "Cost Planner",
                        "status": "complete",
                        "summary_line": f"✅ {cost_str} ({runway_str})",
                        "icon": "💰",
                        "route": "cost_intro",
                    }
            else:
                # Check if product is unlocked (either via GCP completion OR via direct access)
                unlocked_products = cls.get_unlocked_products()
                is_unlocked = "cost_planner" in unlocked_products or "cost_v2" in unlocked_products

                # Also check if GCP is complete (legacy check)
                rec = cls.get_care_recommendation()
                if is_unlocked or (rec and rec.tier):
                    return {
                        "title": "Cost Planner",
                        "status": "unlocked",
                        "summary_line": "Calculate your care costs",
                        "icon": "💰",
                        "route": "cost_intro",
                    }
                else:
                    return {
                        "title": "Cost Planner",
                        "status": "locked",
                        "summary_line": "Complete Guided Care Plan first",
                        "icon": "🔒",
                        "route": None,
                    }

        elif product_key in ["pfma", "pfma_v2"]:
            appt = cls.get_advisor_appointment()
            if appt and appt.scheduled:
                type_map = {"phone": "Phone", "video": "Video", "in_person": "In-Person"}
                type_label = type_map.get(appt.type, appt.type.title())

                return {
                    "title": "Plan with My Advisor",
                    "status": "complete",
                    "summary_line": f"✅ {type_label} Appt - {appt.date}",
                    "icon": "📅",
                    "route": "pfma_v2",
                }
            else:
                # Check if product is unlocked (either via Cost Planner completion OR via direct access)
                unlocked_products = cls.get_unlocked_products()
                is_unlocked = "pfma" in unlocked_products or "pfma_v2" in unlocked_products

                # Also check if Cost Planner is complete (legacy check)
                profile = cls.get_financial_profile()
                if is_unlocked or profile:
                    return {
                        "title": "Plan with My Advisor",
                        "status": "unlocked",
                        "summary_line": "Schedule your advisor appointment",
                        "icon": "📅",
                        "route": "pfma_v2",
                    }
                else:
                    return {
                        "title": "Plan with My Advisor",
                        "status": "locked",
                        "summary_line": "Complete Cost Planner first",
                        "icon": "🔒",
                        "route": None,
                    }

        return None

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    @classmethod
    def _fire_event(cls, event_type: str, payload: dict[str, Any]) -> None:
        """Fire an MCIP event.

        Args:
            event_type: Event identifier (e.g., "mcip.recommendation.updated")
            payload: Event data
        """
        cls.initialize()

        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload,
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

        # Unlock next products (including learn_recommendation after GCP)
        journey["unlocked_products"] = ["gcp", "learn_recommendation", "cost_planner", "pfma"]

        # Set recommended next from recommendation
        journey["recommended_next"] = recommendation.next_step.get("product", "cost_planner")

        # Save journey state for persistence (already called in publish_care_recommendation, but ensure it's saved)
        cls._save_contracts_for_persistence()

    @classmethod
    def _default_care_recommendation(cls) -> dict[str, Any]:
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
                "reason": "Get your personalized care recommendation",
            },
            "status": "new",
            "last_updated": None,
            "needs_refresh": False,
        }


# =============================================================================
# BACKWARD COMPATIBILITY HELPERS (Temporary during migration)
# =============================================================================


def get_care_tier_legacy_compatible() -> str | None:
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
