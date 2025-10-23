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
    - User hasn't acknowledged the nudge yet
    
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
    
    # Suppress if already acknowledged (to avoid duplication with top header)
    if st.session_state.get("_hours_ack"):
        return
    
    # Get user selection
    user = st.session_state.get("gcp_hours_user_choice") or "-"
    
    # Check if nudge exists and user has made a selection
    if not sugg.get("nudge_text") or user == "-":
        return
    
    # Render warning card with nudge (bottom card - optional, kept for context)
    st.warning(
        f"💡 Navi suggests **{sugg['band']} hours per day** instead of **{user}**, "
        f"based on {', '.join(sugg.get('reasons', [])[:2]) or 'your care needs'}. \n\n"
        f"{sugg['nudge_text']}"
    )


def render_navi_header_message():
    """Render hours/day nudge in TOP Navi header with CTA buttons.
    
    Displays a compact nudge message with Accept/Keep action buttons when:
    - FEATURE_GCP_HOURS = "assist"
    - User under-selected hours per day
    - Nudge text has been generated
    - User hasn't acknowledged yet
    
    Also plays a one-time chime when a new nudge appears (optional, graceful if audio missing).
    """
    import os
    import streamlit as st
    import base64
    import pathlib
    
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
    
    sugg = st.session_state.get("_hours_suggestion")
    if not sugg:
        return
    
    nudge = (sugg.get("nudge_text") or "").strip()
    if not nudge:
        return
    
    # Check if already acknowledged
    if st.session_state.get("_hours_ack"):
        return  # Don't show nudge if already acknowledged
    
    # Compose the compact header message (one short sentence)
    band = sugg.get("band")
    user = sugg.get("user") or "-"
    header_line = f"**Navi** suggests **{band}** (you selected **{user}**). {nudge}"
    
    # Render inside the top Navi dialog with compact styling
    st.markdown(
        f"<div id='navi-header-hours' style='margin-top:0.5rem; padding:12px 16px; "
        f"background:#e3f2fd; border:1px solid #2196f3; border-radius:8px; color:#0d47a1; "
        f"font-size:14px; line-height:1.5;'>"
        f"{header_line}</div>",
        unsafe_allow_html=True
    )
    
    # Render CTA buttons in a row
    col1, col2, col3 = st.columns([2, 2, 6])
    
    with col1:
        if st.button(f"✓ Accept {band}", key="hours_accept_btn", use_container_width=True):
            # User accepts suggested hours
            st.session_state["gcp_hours_user_choice"] = band
            st.session_state["_hours_ack"] = True
            st.session_state["_hours_ack_choice"] = "accepted"
            st.session_state["_hours_nudge_new"] = False
            print(f"[GCP_HOURS_ACK] action=accepted band={band}")
            st.rerun()
    
    with col2:
        if st.button("Keep my selection", key="hours_keep_btn", use_container_width=True):
            # User keeps their selection
            st.session_state["_hours_ack"] = True
            st.session_state["_hours_ack_choice"] = "kept"
            st.session_state["_hours_nudge_new"] = False
            print(f"[GCP_HOURS_ACK] action=kept user={user} suggested={band}")
            st.success("✓ We'll stick with your chosen hours.")
            # Note: We don't rerun here, just show success message
    
    # Play chime once when a new nudge appears (optional) - only if not acknowledged
    if st.session_state.get("_hours_nudge_new") and not st.session_state.get("_hours_ack"):
        try:
            p = pathlib.Path('assets/audio/chime.mp3')
            if p.exists():
                data = p.read_bytes()
                b64 = base64.b64encode(data).decode()
                # Autoplay audio via tiny HTML block; one-time per new nudge key
                st.markdown(
                    f"""
                    <audio autoplay style="display:none">
                      <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
                    </audio>
                    """,
                    unsafe_allow_html=True
                )
        except Exception:
            pass
        # Immediately clear the new flag so it won't replay on minor reruns
        st.session_state["_hours_nudge_new"] = False


def render_navi_header_and_summary():
    """Render Navi's conversational explanation on GCP summary page.
    
    Shows LLM-generated summary advice below the top header:
    - Headline (1 sentence)
    - What it means (1-2 sentences)
    - Next steps (1-3 bullets)
    - Next line (transition to cost view)
    
    Only renders if _summary_advice is available in session state.
    """
    import streamlit as st
    
    adv = st.session_state.get("_summary_advice")
    if not adv:
        return
    
    # Add spacing
    st.markdown("<div style='margin-top:.5rem'></div>", unsafe_allow_html=True)
    
    # Show headline
    st.markdown(f"**{adv['headline']}**")
    
    # Show explanation (what_it_means or fallback to first 2 why items)
    body = adv.get("what_it_means") or " ".join(adv.get("why", [])[:2])
    if body:
        st.markdown(body)
    
    # Show next steps if available
    if adv.get("next_steps"):
        st.markdown("**Next steps**")
        for step in adv["next_steps"][:3]:
            st.markdown(f"- {step}")
    
    # Show transition line if available
    if adv.get("next_line"):
        st.markdown(
            f"<div style='margin-top:.5rem;color:#0d1f4b'>{adv['next_line']}</div>",
            unsafe_allow_html=True
        )


def render_clean_summary():
    """Render clean, conversational summary layout for GCP results page.
    
    Shows:
    - Bordered Navi box with user name, tier, quote, and evolution note
    - Two short paragraphs: "What this means for you" and "When it's a good fit"
    - Clean section headers with horizontal rules
    
    Uses LLM-generated summary advice from session state.
    """
    import streamlit as st
    import os
    
    # Pull the LLM summary output
    advice = st.session_state.get("_summary_advice")
    tier = st.session_state.get("gcp.final_tier", "assisted_living").replace("_", " ").title()
    navi_quote = advice.get("headline") if advice else None
    what_it_means = advice.get("what_it_means") if advice else None
    
    # Build richer "When it's a good fit" from why array
    when_best = None
    if advice and advice.get("why"):
        # Join 2-4 why items into one paragraph
        why_items = advice.get("why", [])
        when_best = " ".join(why_items[:4])
    
    # Get user name if available
    user_name = st.session_state.get("senior_name") or st.session_state.get("user_name")
    greeting = f"Great job{', ' + user_name if user_name else ''}."
    
    # Check for hours hint (if user under-selected)
    hours_hint = None
    try:
        mode = None
        try:
            mode = st.secrets.get("FEATURE_GCP_HOURS")
        except Exception:
            pass
        if not mode:
            mode = os.getenv("FEATURE_GCP_HOURS", "off")
        
        if str(mode).lower() == "assist":
            sugg = st.session_state.get("_hours_suggestion")
            if sugg:
                user_band = sugg.get("user")
                suggested_band = sugg.get("band")
                if user_band and suggested_band and user_band != suggested_band:
                    hours_hint = f"💡 Navi suggests {suggested_band} hours/day based on care needs."
    except Exception:
        pass
    
    # Build quote block
    quote_html = ""
    if navi_quote:
        quote_html = f'<p style="margin:1rem 0; padding-left:1rem; border-left:3px solid #3b82f6; font-style:italic; color:#4b5563;">💬 "{navi_quote}"</p>'
    
    # BORDERED NAVI BOX
    navi_box_html = f"""
    <div style="border:2px solid #cbd5e1; border-radius:8px; padding:1.5rem; margin-bottom:2rem; background:#ffffff;">
        <div style="font-size:1.1rem; font-weight:600; margin-bottom:1rem; padding-bottom:.5rem; border-bottom:1px solid #e2e8f0;">
            ✨ NAVI
        </div>
        <p style="margin-bottom:.75rem; color:#374151;">{greeting}</p>
        <p style="margin-bottom:1rem; color:#374151;">Based on your answers, here's the plan that fits best right now:</p>
        <p style="font-size:1.2rem; font-weight:600; margin:1rem 0; color:#0d1f4b;">🏡 {tier}</p>
        {quote_html}
        {f'<p style="margin:.75rem 0; color:#0369a1;">{hours_hint}</p>' if hours_hint else ''}
        <p style="margin-top:1rem; color:#6b7280; font-size:.95rem;">▸ Your plan can evolve as your needs change—you can revisit it anytime.</p>
    </div>
    """
    st.markdown(navi_box_html, unsafe_allow_html=True)
    
    # HORIZONTAL RULE
    st.markdown("---")
    
    # WHAT IT MEANS
    if what_it_means:
        st.markdown("**What this means for you**")
        st.markdown(what_it_means)
        st.markdown("")
    
    # WHEN IT'S A GOOD FIT (richer paragraph)
    if when_best:
        st.markdown("**When it's a good fit**")
        st.markdown(when_best)
        st.markdown("")
    
    # HORIZONTAL RULE BEFORE BUTTONS
    st.markdown("---")
    st.markdown("🔘 **Choose what to do next:**")
    st.markdown("")