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
    
    if not band:
        return  # No band to suggest
    
    # Map band to friendly text
    band_text = {
        "<1h": "less than 1 hour",
        "1-3h": "1–3 hours",
        "4-8h": "4–8 hours",
        "24h": "24-hour support",
    }.get(band, band)
    
    # Render suggestion (compact, non-intrusive)
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
