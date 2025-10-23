"""
GCP LLM Navi UI Component - Renders additive LLM advice in assist mode.

This component displays LLM-generated Navi messages and reasons when
FEATURE_LLM_GCP is set to "assist". The deterministic recommendation
remains the primary display; this is additive context only.
"""

import streamlit as st

from ai.llm_client import get_feature_gcp_mode


def render_gcp_navi_card():
    """Render Navi advice card if LLM assist mode is enabled.
    
    This should be called in the GCP results/summary view to display
    additive LLM-generated advice alongside the deterministic recommendation.
    
    Shows:
    - Up to 2 Navi messages (empathetic, conversational)
    - Up to 2 key reasons (factual, evidence-based)
    
    Only renders if:
    - FEATURE_LLM_GCP = "assist"
    - LLM advice available in session state
    """
    # Check if assist mode is enabled
    llm_mode = get_feature_gcp_mode()
    if llm_mode != "assist":
        return  # Don't render in off/shadow modes
    
    # Check if LLM advice is available
    llm_advice = st.session_state.get("_gcp_llm_advice")
    if not llm_advice:
        return  # No advice to display
    
    # Extract data
    navi_messages = llm_advice.get("navi_messages", [])
    reasons = llm_advice.get("reasons", [])
    
    # Only render if we have content
    if not navi_messages and not reasons:
        return
    
    # Render Navi card (additive, non-intrusive)
    st.markdown("---")
    st.markdown("### 💡 Navi thinks...")
    st.markdown(
        "<div style='background-color: #f0f7ff; padding: 1rem; border-radius: 0.5rem; "
        "border-left: 4px solid #4a90e2;'>",
        unsafe_allow_html=True,
    )
    
    # Show up to 2 Navi messages
    if navi_messages:
        for i, msg in enumerate(navi_messages[:2], 1):
            st.markdown(f"**Message {i}:** {msg}")
            if i < min(2, len(navi_messages)):
                st.markdown("")  # Spacing
    
    # Show up to 2 reasons
    if reasons:
        st.markdown("**Key factors considered:**")
        for reason in reasons[:2]:
            st.markdown(f"- {reason}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("")  # Spacing after card


def render_hours_suggestion():
    """Render hours/day suggestion if enabled in assist mode.
    
    Displays a brief suggestion line for hours per day based on:
    - Transparent baseline rules (ADLs, falls, mobility, safety)
    - Optional LLM refinement (when available)
    - Nudge if user under-selected (picks lower than suggested)
    
    Only renders if:
    - FEATURE_GCP_HOURS = "assist"
    - Hours suggestion available in session state
    - User hasn't answered hours_per_day yet (or is reviewing)
    
    The suggestion is NON-BINDING - user remains in full control.
    """
    # Check if feature is enabled
    try:
        from products.gcp_v4.modules.care_recommendation.logic import gcp_hours_mode
        mode = gcp_hours_mode()
    except Exception:
        return  # Can't check mode, skip
    
    if mode != "assist":
        return  # Only render in assist mode
    
    # Check if suggestion is available
    suggestion = st.session_state.get("_hours_suggestion")
    if not suggestion:
        return  # No suggestion to display
    
    # Extract data
    band = suggestion.get("band")
    baseline = suggestion.get("base")
    confidence = suggestion.get("conf")
    reasons = suggestion.get("reasons", [])
    user_band = suggestion.get("user")
    nudge_text = suggestion.get("nudge_text")
    severity = suggestion.get("severity")
    
    if not band:
        return  # No band to suggest
    
    # Map band to friendly text
    band_text = {
        "<1h": "less than 1 hour",
        "1-3h": "1–3 hours",
        "4-8h": "4–8 hours",
        "24h": "24-hour support",
    }.get(band, band)
    
    # If there's a nudge (user under-selected), show warning-style card
    if nudge_text and user_band:
        st.markdown(
            f"<div style='background-color: #fff3cd; padding: 0.75rem 1rem; border-radius: 0.5rem; "
            f"border-left: 4px solid #ffc107; margin-bottom: 1rem;'>",
            unsafe_allow_html=True,
        )
        
        st.markdown(f"⚠️ **Please reconsider your hours selection**", unsafe_allow_html=True)
        st.markdown(f"<p style='margin-top: 0.5rem; margin-bottom: 0.5rem;'>{nudge_text}</p>", unsafe_allow_html=True)
        
        # Show what they selected vs. what's suggested
        user_text = {
            "<1h": "less than 1 hour",
            "1-3h": "1–3 hours",
            "4-8h": "4–8 hours",
            "24h": "24-hour support",
        }.get(user_band, user_band)
        
        st.markdown(
            f"<small style='color: #856404;'>You selected: <strong>{user_text}/day</strong> | "
            f"Navi recommends: <strong>{band_text}/day</strong></small>",
            unsafe_allow_html=True,
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # Normal suggestion (no nudge) - compact, non-intrusive
        st.markdown(
            f"<div style='background-color: #f9f9f9; padding: 0.75rem 1rem; border-radius: 0.5rem; "
            f"border-left: 3px solid #6c757d; margin-bottom: 1rem;'>",
            unsafe_allow_html=True,
        )
        
        # Main suggestion line
        st.markdown(f"💡 **Navi suggests {band_text}/day** based on your answers", unsafe_allow_html=True)
        
        # Show top reason if available
        if reasons and len(reasons) > 0:
            st.markdown(f"<small style='color: #6c757d;'>• {reasons[0]}</small>", unsafe_allow_html=True)
        
        # Show confidence if LLM refined (not baseline fallback)
        if confidence is not None and confidence > 0:
            conf_pct = int(confidence * 100)
            st.markdown(
            f"<small style='color: #6c757d;'>Confidence: {conf_pct}%</small>",
            unsafe_allow_html=True,
        )
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_hours_nudge():
    """Render hours/day nudge card in assist mode when user under-selects.
    
    Displays a warning-style card with personalized nudge text when:
    - FEATURE_GCP_HOURS = "assist"
    - User has selected hours per day
    - User's selection is lower than suggested band
    - Nudge text has been generated by LLM
    
    The nudge is advisory only - does not change user's selection.
    """
    import streamlit as st
    import os
    
    sugg = st.session_state.get("_hours_suggestion")
    if not sugg:
        return
    
    # Check if assist mode is enabled
    mode = None
    try:
        mode = st.secrets.get("FEATURE_GCP_HOURS")
    except Exception:
        pass
    if not mode:
        mode = os.getenv("FEATURE_GCP_HOURS", "off")
    
    if str(mode).lower() != "assist":
        return
    
    # Get user selection
    user = st.session_state.get("gcp_hours_user_choice") or "-"
    
    # Check if nudge exists and user has made a selection
    if not sugg.get("nudge_text") or user == "-":
        return
    
    # Render warning card with nudge
    st.warning(
        f"💡 Navi suggests **{sugg['band']} hours per day** instead of **{user}**, "
        f"based on {', '.join(sugg.get('reasons', [])[:2]) or 'your care needs'}. \n\n"
        f"{sugg['nudge_text']}"
    )