"""
GCP v4 Product Router - Guided Care Plan with MCIP Integration

Runs the care_recommendation module using the module engine, then publishes
the CareRecommendation contract to MCIP for consumption by other products.
"""

import streamlit as st
from datetime import datetime
from core.mcip import MCIP, CareRecommendation
from core.modules.engine import run_module_engine
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
    module_state = run_module_engine(config, "gcp_v4")
    
    # Check if module is complete
    if module_state and module_state.get("status") == "complete":
        # Publish to MCIP (only once per completion)
        if not _already_published(module_state):
            _publish_to_mcip(module_state)
            _mark_published(module_state)
        
        # Show completion screen
        _render_completion_screen()


def _load_module_config() -> ModuleConfig:
    """Load module configuration from JSON.
    
    Returns:
        ModuleConfig for care_recommendation module
    """
    from products.gcp_v4.modules.care_recommendation import config
    return config.get_config()


def _already_published(module_state: dict) -> bool:
    """Check if recommendation already published to MCIP.
    
    Args:
        module_state: Module state dict
    
    Returns:
        True if already published
    """
    # Check if we've marked this session as published
    return st.session_state.get("gcp_v4_published", False)


def _mark_published(module_state: dict) -> None:
    """Mark recommendation as published.
    
    Args:
        module_state: Module state dict
    """
    st.session_state["gcp_v4_published"] = True


def _publish_to_mcip(module_state: dict) -> None:
    """Compute recommendation and publish to MCIP.
    
    Args:
        module_state: Completed module state with answers and outcome
    """
    
    # Get outcome from module (computed by logic.py)
    outcome = module_state.get("outcome", {})
    
    if not outcome:
        st.error("❌ Unable to generate recommendation - no outcome from module")
        return
    
    # Build CareRecommendation contract
    try:
        recommendation = CareRecommendation(
            # Core recommendation
            tier=outcome["tier"],
            tier_score=float(outcome["tier_score"]),
            tier_rankings=outcome["tier_rankings"],
            confidence=float(outcome["confidence"]),
            flags=outcome.get("flags", []),
            rationale=outcome.get("rationale", []),
            
            # Provenance
            generated_at=datetime.utcnow().isoformat() + "Z",
            version="4.0.0",
            input_snapshot_id=_generate_snapshot_id(),
            rule_set="standard_2025_q4",
            
            # Next step
            next_step={
                "product": outcome.get("suggested_next_product", "cost_planner"),
                "route": "cost" if outcome.get("suggested_next_product") == "cost_planner" else "gcp",
                "label": "See Cost Estimate" if outcome.get("suggested_next_product") == "cost_planner" else "Complete Assessment",
                "reason": _build_next_step_reason(outcome)
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
        
        st.success("✅ Recommendation published to care intelligence system")
        
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


def _render_completion_screen() -> None:
    """Render completion screen after recommendation published."""
    
    # Get recommendation from MCIP
    recommendation = MCIP.get_care_recommendation()
    
    if not recommendation:
        st.info("🔄 Generating your personalized care recommendation...")
        return
    
    st.success("✅ **Your Guided Care Plan is Complete!**")
    
    st.markdown("---")
    
    # Show recommendation
    tier_label = recommendation.tier.replace("_", " ").title()
    st.markdown(f"### 🎯 Recommended Care Level: **{tier_label}**")
    
    # Show confidence
    confidence_pct = int(recommendation.confidence * 100)
    st.progress(recommendation.confidence)
    st.caption(f"Confidence: {confidence_pct}% (based on your answers)")
    
    st.markdown("---")
    
    # Show rationale
    if recommendation.rationale:
        st.markdown("### 📋 Key Factors in Your Recommendation")
        for idx, reason in enumerate(recommendation.rationale[:5], 1):
            st.markdown(f"{idx}. {reason}")
        
        st.markdown("---")
    
    # Show flags with CTAs
    if recommendation.flags:
        st.markdown("### ⚠️ Important Considerations")
        
        # Sort flags by priority
        sorted_flags = sorted(recommendation.flags, key=lambda f: f.get("priority", 99))
        
        for flag in sorted_flags:
            tone_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
            emoji = tone_emoji.get(flag.get("tone"), "ℹ️")
            
            with st.expander(f"{emoji} {flag['label']}"):
                st.markdown(flag["description"])
                
                if flag.get("cta"):
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button(flag["cta"]["label"], key=f"flag_{flag['id']}", use_container_width=True):
                            from core.nav import route_to
                            route_to(flag["cta"]["route"])
        
        st.markdown("---")
    
    # Next steps
    st.markdown("### 🚀 Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💰 Calculate Monthly Costs", type="primary", use_container_width=True, key="next_cost"):
            from core.nav import route_to
            route_to("cost")
    
    with col2:
        if st.button("🏠 Return to Hub", use_container_width=True, key="next_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    # Debug info (if enabled)
    if st.session_state.get("debug_mode"):
        with st.expander("🔧 Debug Info"):
            st.json({
                "tier": recommendation.tier,
                "tier_score": recommendation.tier_score,
                "confidence": recommendation.confidence,
                "tier_rankings": recommendation.tier_rankings,
                "flags": [f["id"] for f in recommendation.flags],
                "version": recommendation.version,
                "generated_at": recommendation.generated_at
            })
