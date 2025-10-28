"""Concierge Clinical Review - Overview page."""

import streamlit as st
from datetime import datetime

# --- Helpers ---

def _get_care_summary():
    """Extract care recommendation summary from GCP state.
    
    Returns:
        Tuple of (tier, top_flags)
    """
    g = st.session_state.get("gcp", {}) or {}
    tier = g.get("published_tier") or g.get("final_tier") or "assisted_living"
    flags = g.get("flags") or []
    top_flags = [f.get("label") or f.get("id") for f in flags if f][:4]
    return tier, top_flags


def _get_cost_postcard():
    """Extract cost total and affordability from Cost Planner state.
    
    Returns:
        Tuple of (monthly_total, years_funded)
    """
    cost = st.session_state.get("cost", {}) or {}
    total = cost.get("monthly_total")
    years = None
    aff = cost.get("affordability") or {}
    if isinstance(aff, dict):
        years = aff.get("years_funded")
    return total, years


def _navi_compact_message() -> str:
    """Generate short, context-aware Navi message (no LLM yet)."""
    g_done = bool((st.session_state.get("gcp") or {}).get("summary_ready"))
    c_done = bool((st.session_state.get("cost") or {}).get("completed"))
    if g_done and c_done:
        return ("You've finished your Guided Care Plan and Cost Planner — great work. "
                "This review helps confirm your care level and next steps.")
    if g_done and not c_done:
        return ("Your care plan is ready. Cost Planner will help estimate affordability; "
                "you'll unlock your clinical review next.")
    return ("I can help summarize what your doctor will want to review — or set you up with a specialist.")


def _render_navi_compact():
    """Render Navi compact panel at top (reuse existing style)."""
    st.markdown(
        "<div class='navi-panel-compact'>"
        "<div class='navi-content'>✨ "
        + _navi_compact_message() +
        "</div></div>",
        unsafe_allow_html=True
    )


def _render_summary_card(tier: str, top_flags: list[str], cost_total, years_funded):
    """Render summary glance card (reuse cost-card look)."""
    st.markdown("<div class='cost-card'>", unsafe_allow_html=True)
    # Tier
    nice_tier = ("Assisted Living with Enhanced Cognitive Support"
                 if "assisted" in tier else tier.replace("_", " ").title())
    st.markdown(f"**Recommended Level of Care:** {nice_tier}")
    # Flags as inline chips (simple text; no CSS changes)
    if top_flags:
        chips = " ".join([f"[{f}]" for f in top_flags])
        st.markdown(f"**Top Care Flags:** {chips}")
    # Cost
    if cost_total:
        affix = f" • Funds last ~{int(years_funded)} years" if years_funded else ""
        st.markdown(f"**Cost Snapshot:** ${int(cost_total):,} / month{affix}")
    st.markdown("</div>", unsafe_allow_html=True)


def _generate_overview_paragraph(tier, top_flags, cost_total) -> str:
    """Generate overview paragraph (deterministic scaffold; LLM can replace later)."""
    flags_text = ", ".join([f for f in top_flags if f]) or "key safety and daily living needs"
    cost_line = (f"Sustaining in-home care may be financially challenging at ${int(cost_total):,}/month."
                 if cost_total else "Sustaining in-home care may be financially challenging.")
    tier_text = ("Assisted Living with Enhanced Cognitive Support"
                 if "assisted" in tier else tier.replace("_", " ").title())
    return ("Based on your Guided Care Plan and Cost Planner, your current care needs reflect "
            f"{flags_text}. {cost_line} Considering both safety and affordability, "
            f"{tier_text} appears to be a practical next step.")


def render_overview():
    """Render main overview page with care summary and options."""
    st.markdown("### Concierge Clinical Review")
    st.caption("Validate your care plan with your doctor or a clinical specialist.")

    # Navi (compact) — do not add/modify global CSS
    _render_navi_compact()

    st.markdown("---")

    # Summary glance card
    tier, top_flags = _get_care_summary()
    cost_total, years = _get_cost_postcard()
    _render_summary_card(tier, top_flags, cost_total, years)

    st.markdown("#### Clinical Overview")
    paragraph = _generate_overview_paragraph(tier, top_flags, cost_total)
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
        st.write("Meet with a physician who specializes in senior and memory care to review your plan together.")
        if st.button("Schedule My Review", use_container_width=True, key="ccr_btn_schedule"):
            st.session_state["ccr.view"] = "schedule"
            st.rerun()

    # Navigation back to Waiting Room
    st.markdown("---")
    if st.button("← Back to Waiting Room", use_container_width=True, key="ccr_back_to_hub"):
        from core.nav import route_to
        route_to("hub_waiting")

    st.caption("Not ready yet? You can return anytime — your plan and progress are saved.")
    print("[CCR] opened", datetime.utcnow().isoformat() + "Z")
