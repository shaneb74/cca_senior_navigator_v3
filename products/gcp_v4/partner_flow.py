"""
Partner Flow - Household Dual Assessment

Handles the partner interstitial prompt and compressed GCP flow
for spouses/partners when has_partner flag is set.

Flow:
1. Primary completes GCP → RESULTS
2. If has_partner: show partner interstitial
3. User chooses: Start Partner Plan or Skip
4. If Start: compressed GCP for partner → partner CarePlan
5. Proceed to Cost Planner with both CarePlans
"""

import streamlit as st
from core.household import add_person, ensure_household_state


def _get_partner_flow_enabled() -> bool:
    """Check if household partner flow feature is enabled.
    
    Returns:
        True if enabled (default: on)
    """
    import os
    try:
        v = st.secrets.get("FEATURE_HOUSEHOLD_PARTNER_FLOW")
        if v is not None:
            return str(v).lower() in {"on", "true", "1", "yes"}
    except Exception:
        pass
    
    v = os.getenv("FEATURE_HOUSEHOLD_PARTNER_FLOW", "on")
    return str(v).lower() in {"on", "true", "1", "yes"}


def should_show_partner_interstitial(has_partner: bool) -> bool:
    """Determine if partner interstitial should be shown.
    
    Args:
        has_partner: Whether primary person has a partner
        
    Returns:
        True if interstitial should be displayed
    """
    if not _get_partner_flow_enabled():
        return False
    
    if not has_partner:
        return False
    
    # Don't show if decision has been made (started or explicitly skipped)
    # flow.partner_started will be True (started) or False (skipped) once decided
    if "flow.partner_started" in st.session_state:
        return False
    
    return True


def render_partner_interstitial():
    """Render the partner assessment interstitial prompt.
    
    Shows Navi prompt asking if user wants to assess partner's needs.
    Handles Start and Skip actions with immediate decision persistence.
    """
    st.markdown("---")
    st.markdown("### Partner Assessment")
    
    # Navi prompt
    st.info(
        "👥 You mentioned living with a spouse. Often, when one partner needs care, "
        "it helps to check the other's needs too. Would you like to start a short assessment "
        "for your spouse or partner?"
    )
    
    col1, col2, _ = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Start Partner Plan", type="primary", use_container_width=True):
            # Get household and add partner
            hh = ensure_household_state(st)
            partner = add_person(st, role="partner", zip=hh.zip)
            
            # Persist decision immediately
            st.session_state["flow.partner_started"] = True
            st.session_state["gcp.partner_mode"] = True
            st.session_state["flow.partner_complete"] = False
            
            # Route to GCP for partner
            st.session_state["current_product"] = "gcp_v4"
            st.session_state["gcp_current_step_id"] = None  # Reset to start
            
            print(f"[PARTNER_FLOW] Started: partner={partner.uid}")
            st.rerun()
    
    with col2:
        if st.button("Skip for Now", use_container_width=True):
            # Persist skip decision definitively
            st.session_state["flow.partner_started"] = False
            st.session_state["flow.partner_complete"] = False
            print("[PARTNER_FLOW] Skipped")
            st.rerun()


def is_partner_mode() -> bool:
    """Check if currently in partner assessment mode.
    
    Returns:
        True if assessing partner
    """
    return st.session_state.get("gcp.partner_mode", False)


def complete_partner_flow():
    """Mark partner flow as complete and exit partner mode.
    
    Idempotent: safe to call multiple times without side effects.
    """
    # Set completion flag
    st.session_state["flow.partner_complete"] = True
    
    # Clear partner mode to prevent leakage
    st.session_state["gcp.partner_mode"] = False
    
    print("[PARTNER_FLOW] Complete")
