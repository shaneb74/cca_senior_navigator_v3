"""
GCP v4 Product Router - Guided Care Plan with MCIP Integration

Runs the care_recommendation module using the module engine, then publishes
the CareRecommendation contract to MCIP for consumption by other products.
"""

import streamlit as st
from datetime import datetime
from core.mcip import MCIP, CareRecommendation
from core.modules.engine import run_module
from core.modules.schema import ModuleConfig


def render():
    """Render GCP v4 product.
    
    Flow:
    1. Run care_recommendation module via module engine
    2. Module engine handles all UI, navigation, progress
    3. When complete, publish CareRecommendation to MCIP
    4. Show completion screen with recommendation
    """
    
    # Load module config
    config = _load_module_config()
    
    # Run module engine (handles all rendering and navigation)
    # The engine stores state in st.session_state[config.state_key]
    # and outcomes in st.session_state[f"{config.state_key}._outcomes"]
    module_state = run_module(config)
    
    # Check if module has computed outcomes (means we're on results step)
    outcome_key = f"{config.state_key}._outcomes"
    outcome = st.session_state.get(outcome_key)
    
    # If outcome exists and we haven't published yet, publish to MCIP
    if outcome and not _already_published():
        _publish_to_mcip(outcome, module_state)
        _mark_published()
        
        # Show completion message (engine already rendered results step)
        st.success("✅ Your care recommendation has been saved!")
        
        # Add next steps buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💰 Calculate Costs", type="primary", use_container_width=True, key="gcp_next_cost"):
                from core.nav import route_to
                route_to("cost_v2")
        with col2:
            if st.button("🏠 Return to Hub", use_container_width=True, key="gcp_next_hub"):
                from core.nav import route_to
                route_to("hub_concierge")


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
            "suggested_next_product": getattr(outcome, "suggested_next_product", "cost_planner")
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
                "route": "cost_v2" if outcome_data.get("suggested_next_product") == "cost_planner" else "gcp_v4",
                "label": "Calculate Costs" if outcome_data.get("suggested_next_product") == "cost_planner" else "Complete Assessment",
                "reason": _build_next_step_reason(outcome_data)
            },
            
            # Status
            status="complete",
            last_updated=datetime.utcnow().isoformat() + "Z",
            needs_refresh=False
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
