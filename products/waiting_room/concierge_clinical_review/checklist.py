"""Concierge Clinical Review - Provider checklist page."""

import streamlit as st
from datetime import datetime


def _doctor_questions(flags) -> list[str]:
    """Generate doctor discussion questions (deterministic; can be LLM-driven later).
    
    Args:
        flags: List of care flags
    
    Returns:
        List of question strings
    """
    # Simple, deterministic set; can be LLM-driven later
    qs = [
        "Should we adjust medications that may impact cognition or balance?",
        "Are there assessments we should complete to confirm support level?",
        "What safety changes would you recommend at home or in a community?",
        "Would PT/OT help with mobility, fall risk, or daily routines?",
        "What should we monitor over the next 3–6 months?"
    ]
    return qs


def render_checklist():
    """Render provider checklist page."""
    g = st.session_state.get("gcp", {})
    tier = g.get("published_tier") or "assisted_living"
    flags = [f.get("label") or f.get("id") for f in (g.get("flags") or [])][:6]
    cost_total = st.session_state.get("cost", {}).get("monthly_total")

    st.markdown("### Provider Checklist")
    st.caption("Bring this summary to your doctor to discuss next steps.")

    st.write(f"**Care Recommendation:** {tier.replace('_',' ').title()}")
    if flags:
        st.write("**Top Care Flags:** " + ", ".join(flags))
    if cost_total:
        st.write(f"**Estimated Cost Context:** ${int(cost_total):,}/month")

    st.markdown("#### Questions to Discuss")
    for q in _doctor_questions(flags):
        st.write(f"- {q}")

    st.markdown("#### Provider Notes")
    st.text_area("Use this space for provider notes during the visit", key="ccr.provider_notes", height=140)

    # Completion flag
    st.session_state.setdefault("ccr", {})
    st.session_state["ccr"]["checklist_generated"] = True
    print("[CCR] checklist.created", datetime.utcnow().isoformat() + "Z")

    c1, c2, c3 = st.columns(3)
    if c1.button("Download (HTML)", use_container_width=True, key="ccr_dl_html"):
        # Future: export to PDF/HTML; for now just acknowledge
        st.success("Checklist generated. (Export scaffolding can be added later.)")
    if c2.button("Back to Review", use_container_width=True, key="ccr_back_overview"):
        st.session_state["ccr.view"] = "overview"
        st.rerun()
    if c3.button("← Waiting Room", use_container_width=True, key="ccr_checklist_to_hub"):
        from core.nav import route_to
        route_to("hub_lobby")
