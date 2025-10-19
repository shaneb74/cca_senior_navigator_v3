"""
GCP v4 Product Router - Guided Care Plan with MCIP Integration

Runs the care_recommendation module using the module engine, then publishes
the CareRecommendation contract to MCIP for consumption by other products.

Uses Navi as the single intelligence layer for guidance and progress.
"""

from datetime import datetime

import streamlit as st

from core.mcip import MCIP, CareRecommendation
from core.modules.engine import run_module
from core.modules.schema import ModuleConfig
from core.navi import render_navi_panel
from ui.product_shell import product_shell_end, product_shell_start


def render():
    """Render GCP v4 product.

    Flow:
    1. Check for restart intent (when complete and re-entering)
    2. Render Navi panel (single intelligence layer)
    3. Run care_recommendation module via module engine
    4. Module engine handles all UI and navigation
    5. When complete, publish CareRecommendation to MCIP
    6. Show completion screen with recommendation
    """

    # Load module config
    config = _load_module_config()

    # Check if user is restarting (clicking "Restart" when GCP is complete)
    # This happens when: GCP complete + returning from hub + at step 0 or results
    _handle_restart_if_needed(config)

    product_shell_start()

    try:
        # Check if we're CURRENTLY VIEWING the results step
        # Need to check BOTH session state AND tile state (for resume functionality)
        state_key = config.state_key

        # Check tile state first (takes priority for resume)
        tiles = st.session_state.setdefault("tiles", {})
        tile_state = tiles.setdefault(config.product, {})
        saved_step = tile_state.get("last_step")

        # Determine current step index (same logic as run_module)
        if saved_step is not None and saved_step >= 0:
            current_step_index = saved_step
        else:
            current_step_index = int(st.session_state.get(f"{state_key}._step", 0))

        # Clamp to valid range
        current_step_index = max(0, min(current_step_index, len(config.steps) - 1))

        # Safely get current step
        current_step = None
        if 0 <= current_step_index < len(config.steps):
            current_step = config.steps[current_step_index]

        # Check if current step is the results step
        is_on_results_step = (
            current_step is not None
            and config.results_step_id
            and current_step.id == config.results_step_id
        )

        # Render Navi panel (THE single intelligence layer) UNLESS actively on results step
        # Provides module-level guidance, progress, contextual help
        # Results step has its own Navi announcement, so we skip here
        if not is_on_results_step:
            render_navi_panel(location="product", product_key="gcp_v4", module_config=config)

        # Run module engine (handles all rendering and navigation)
        # The engine stores state in st.session_state[config.state_key]
        # and outcomes in st.session_state[f"{config.state_key}._outcomes"]
        module_state = run_module(config)

        # Check if outcome exists for publishing
        outcome_key = f"{state_key}._outcomes"
        outcome = st.session_state.get(outcome_key)

        # If outcome exists and we haven't published yet, publish to MCIP
        # NOTE: The outcome may be wrapped in OutcomeContract format, but our
        # derive_outcome() returns GCP-specific fields (tier, tier_score, etc)
        # We need to call derive_outcome directly to get the proper format
        if outcome and not _already_published():
            # Re-compute outcome directly to get proper GCP format
            try:
                from products.gcp_v4.modules.care_recommendation.logic import derive_outcome

                gcp_outcome = derive_outcome(module_state)
                _publish_to_mcip(gcp_outcome, module_state)
                _mark_published()
            except Exception as e:
                st.error(f"❌ Error saving recommendation: {e}")
                import traceback

                st.error(traceback.format_exc())

        # Calculate Costs button removed - only appears on results page via Navi panel
        # Results page includes this as a primary action after seeing recommendation

    finally:
        product_shell_end()


def _load_module_config() -> ModuleConfig:
    """Load module configuration from JSON.

    Returns:
        ModuleConfig for care_recommendation module
    """
    from products.gcp_v4.modules.care_recommendation import config

    return config.get_config()


def _already_published() -> bool:
    """Check if recommendation already published to MCIP.

    Returns:
        True if already published
    """
    return st.session_state.get("gcp_v4_published", False)


def _mark_published() -> None:
    """Mark recommendation as published."""
    st.session_state["gcp_v4_published"] = True


def _publish_to_mcip(outcome, module_state: dict) -> None:
    """Compute recommendation and publish to MCIP.

    Args:
        outcome: OutcomeContract or dict from logic.py
        module_state: Module state with answers
    """

    # Extract outcome data (handle both OutcomeContract and dict)
    if hasattr(outcome, "__dict__"):
        # It's an OutcomeContract object
        outcome_data = {
            "tier": getattr(outcome, "tier", None),
            "tier_score": getattr(outcome, "tier_score", 0.0),
            "tier_rankings": getattr(outcome, "tier_rankings", []),
            "confidence": getattr(outcome, "confidence", 0.0),
            "flags": getattr(outcome, "flags", []),
            "rationale": getattr(outcome, "rationale", []),
            "suggested_next_product": getattr(outcome, "suggested_next_product", "cost_planner"),
        }
    elif isinstance(outcome, dict):
        outcome_data = outcome
    else:
        st.error("❌ Unable to generate recommendation - invalid outcome format")
        return

    # Validate required fields
    if not outcome_data.get("tier"):
        st.error("❌ Unable to generate recommendation - missing tier")
        return

    # Build CareRecommendation contract
    try:
        recommendation = CareRecommendation(
            # Core recommendation
            tier=outcome_data["tier"],
            tier_score=float(outcome_data.get("tier_score", 0.0)),
            tier_rankings=outcome_data.get("tier_rankings", []),
            confidence=float(outcome_data.get("confidence", 0.0)),
            flags=outcome_data.get("flags", []),
            rationale=outcome_data.get("rationale", []),
            # Provenance
            generated_at=datetime.utcnow().isoformat() + "Z",
            version="4.0.0",
            input_snapshot_id=_generate_snapshot_id(),
            rule_set="standard_2025_q4",
            # Next step
            next_step={
                "product": outcome_data.get("suggested_next_product", "cost_planner"),
                "route": "cost_v2"
                if outcome_data.get("suggested_next_product") == "cost_planner"
                else "gcp_v4",
                "label": "Calculate Costs"
                if outcome_data.get("suggested_next_product") == "cost_planner"
                else "Complete Assessment",
                "reason": _build_next_step_reason(outcome_data),
            },
            # Status
            status="complete",
            last_updated=datetime.utcnow().isoformat() + "Z",
            needs_refresh=False,
        )

        # Publish to MCIP (single source of truth)
        MCIP.publish_care_recommendation(recommendation)

        # Mark GCP as complete in journey
        MCIP.mark_product_complete("gcp")

    except Exception as e:
        st.error(f"❌ Error publishing recommendation: {e}")
        import traceback

        st.error(traceback.format_exc())


def _generate_snapshot_id() -> str:
    """Generate unique snapshot ID for this recommendation.

    Returns:
        Snapshot ID string
    """
    user_id = st.session_state.get("user_id", "anon")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"gcp_v4_{user_id}_{timestamp}"


def _build_next_step_reason(outcome: dict) -> str:
    """Build reason text for next step.

    Args:
        outcome: Outcome dict from logic.py

    Returns:
        Reason string
    """
    tier = outcome.get("tier", "").replace("_", " ").title()
    suggested = outcome.get("suggested_next_product", "cost_planner")

    if suggested == "cost_planner":
        return f"Calculate financial impact of {tier} care"
    else:
        return "Complete your care assessment for a personalized recommendation"


def _handle_restart_if_needed(config: ModuleConfig) -> None:
    """Handle restart when user clicks 'Restart' button on completed GCP.

    Clears GCP state to start fresh, but preserves Cost Planner progress.
    Only triggers when GCP is complete and user is re-entering.

    Args:
        config: Module configuration
    """
    # CRITICAL FIX: Only restart if user explicitly requested it via query param
    # Don't auto-restart just because step is 0 - that's the default on fresh login!
    restart_requested = st.query_params.get("restart") == "true"
    if not restart_requested:
        return  # No explicit restart request, preserve existing state
    
    # Check if GCP is complete
    try:
        from core.mcip import MCIP

        if not MCIP.is_product_complete("gcp"):
            return  # Not complete, no restart needed
    except Exception:
        return  # Error checking MCIP, skip restart

    # Get current state
    state_key = config.state_key
    tiles = st.session_state.setdefault("tiles", {})
    tile_state = tiles.setdefault(config.product, {})

    # Check if we're at the beginning or end (restart scenario)
    current_step = st.session_state.get(f"{state_key}._step", 0)

    # Only restart if at step 0 (user clicked Restart button from hub)
    # Don't auto-restart if they're reviewing answers mid-flow
    if current_step != 0:
        return

    # RESTART: Clear GCP state but preserve Cost Planner
    # 1. Clear module state
    if state_key in st.session_state:
        del st.session_state[state_key]

    # 2. Clear tile state
    if config.product in tiles:
        tiles[config.product] = {}

    # 3. Clear outcomes
    outcome_key = f"{state_key}._outcomes"
    if outcome_key in st.session_state:
        del st.session_state[outcome_key]

    # 4. Clear published flag
    if "gcp_v4_published" in st.session_state:
        del st.session_state["gcp_v4_published"]

    # 5. Reset MCIP GCP completion (but preserve Cost Planner!)
    try:
        from core.mcip import MCIP

        # Clear GCP recommendation so it shows as not complete
        if hasattr(MCIP, "_data") and "care_recommendation" in MCIP._data:
            del MCIP._data["care_recommendation"]
        # Mark GCP as not complete in journey
        if hasattr(MCIP, "_data") and "journey_progress" in MCIP._data:
            if "gcp" in MCIP._data["journey_progress"]:
                MCIP._data["journey_progress"]["gcp"] = 0
    except Exception:
        pass  # If MCIP clear fails, state is already cleared above

    # Note: Cost Planner state preserved automatically because we only cleared GCP keys
