"""Concierge Clinical Review - Overview page."""

import streamlit as st
from datetime import datetime


def _get_care_summary():
    """Extract care recommendation summary from GCP state.
    
    Returns:
        Tuple of (tier, top_flags)
    """
    g = st.session_state.get("gcp", {})
    tier = g.get("published_tier") or g.get("final_tier") or "assisted_living"
    flags = g.get("flags") or []
    top_flags = [f.get("label") or f.get("id") for f in flags][:4]
    return tier, top_flags


def _get_cost_postcard():
    """Extract cost total from Cost Planner state.
    
    Returns:
        Monthly total or None
    """
    cost = st.session_state.get("cost", {})
    total = cost.get("monthly_total")
    return total


def _generate_llm_overview_paragraph(tier, top_flags, cost_total) -> str:
    """Generate overview paragraph (deterministic for now; LLM placeholder).
    
    Args:
        tier: Care recommendation tier
        top_flags: List of top care flags
        cost_total: Monthly cost total
    
    Returns:
        Overview paragraph text
    """
    # Placeholder/deterministic text; real LLM wiring can replace this later
    flags_text = ", ".join([f for f in top_flags if f]) or "key safety and daily living needs"
    cost_line = f"Sustaining in-home care may exceed ${int(cost_total):,}/month" if cost_total else "Sustaining in-home care may be financially challenging"
    tier_text = "Assisted Living with Enhanced Cognitive Support" if "assisted" in tier else tier.replace("_", " ").title()
    return (
        f"Based on your Guided Care Plan and Cost Planner, your current care needs reflect {flags_text}. "
        f"{cost_line}. Considering both safety and affordability, {tier_text} appears to be a practical next step."
    )


def render_overview():
    """Render main overview page with care summary and options."""
    st.markdown("### Concierge Clinical Review")
    st.caption("Validate your care plan with your doctor or a clinical specialist.")

    # Optional Navi line (placeholder; no LLM)
    st.info("I can help summarize what your doctor will want to review, or you can meet with a specialist for a clinical review.")

    tier, top_flags = _get_care_summary()
    cost_total = _get_cost_postcard()

    st.markdown("#### Your Current Care Recommendation")
    st.write(f"**Recommended Level of Care:** {tier.replace('_',' ').title()}")
    if top_flags:
        st.write("**Top Care Flags:** " + ", ".join(top_flags))
    if cost_total:
        st.write(f"**Estimated Cost Context:** ${int(cost_total):,}/month")

    st.markdown("#### Clinical Overview")
    paragraph = _generate_llm_overview_paragraph(tier, top_flags, cost_total)
    st.write(paragraph)

    st.markdown("---")
    st.markdown("#### Choose How You'd Like to Proceed")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Bring to My Doctor**")
        st.write("Create a personalized checklist to review with your provider. Includes your plan, top flags, and cost outlook.")
        if st.button("Create My Checklist", use_container_width=True, key="ccr_btn_checklist"):
            st.session_state["ccr.view"] = "checklist"
            st.rerun()

    with col2:
        st.markdown("**Schedule with a Specialist**")
        st.write("Meet with a physician who specializes in senior care and memory-related conditions.")
        if st.button("Schedule My Review", use_container_width=True, key="ccr_btn_schedule"):
            st.session_state["ccr.view"] = "schedule"
            st.rerun()

    print("[CCR] opened", datetime.utcnow().isoformat() + "Z")
