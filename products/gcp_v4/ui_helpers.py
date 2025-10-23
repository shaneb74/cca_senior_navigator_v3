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


def _play_chime_once():
    """Inject a tiny autoplay audio element to play the navi chime once.
    Adds debug logs for reliability tracing.
    """
    import base64
    import pathlib
    import streamlit as st

    p = pathlib.Path("assets/audio/chime.mp3")
    if not p.exists():
        print("[CHIME] skip: missing assets/audio/chime.mp3")
        return
    try:
        b64 = base64.b64encode(p.read_bytes()).decode()
        st.markdown(
            f"""
            <audio id="navi-chime" autoplay playsinline preload="auto" style="display:none">
              <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
            </audio>
            """,
            unsafe_allow_html=True,
        )
        print("[CHIME] injected")
    except Exception as e:
        print(f"[CHIME] error: {e}")


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
    """Render the single blue Navi header (module variant) with quote + hours hint.

    Inside the blue header panel, show:
    - Step title (or "Your Guided Care Plan") and optional subtitle
    - One-line Navi quote (LLM headline) under title
    - If FEATURE_GCP_HOURS=assist and user under-selected: a single subtle hours hint line

    Below the header (still at top of page), render Accept/Keep hours CTAs ONLY on GCP route.
    Play the chime once when a NEW nudge appears (only on GCP route) and then clear the flag.
    """
    import os
    import streamlit as st
    import base64
    import pathlib
    
    # Single-render guard to prevent recursion/duplication per page
    # Scope by a simple per-page key so a stale flag from a previous page doesn't block first paint
    pending_title = st.session_state.get("gcp_step_title") or ""
    page_key = f"gcp_cp_header::{pending_title}"
    prev_key = st.session_state.get("_gcp_cp_header_key")
    if st.session_state.get("_gcp_cp_header_rendered", False) and prev_key == page_key:
        return
    st.session_state["_gcp_cp_header_rendered"] = True
    st.session_state["_gcp_cp_header_key"] = page_key
    
    # Check if assist mode is enabled
    mode = None
    try:
        mode = st.secrets.get("FEATURE_GCP_HOURS")
    except Exception:
        pass
    if not mode:
        mode = os.getenv("FEATURE_GCP_HOURS", "off")
    
    # Resolve route and page scope
    route = st.session_state.get("route") or st.query_params.get("page") or ""
    is_gcp = (route == "gcp")
    is_cp_intro = bool(st.session_state.get("cp_intro", False))

    # Scope: Only render on GCP pages or CP intro
    if not (is_gcp or is_cp_intro):
        return

    # Build step title/subtitle from session (set by product before calling us)
    step_title = st.session_state.get("gcp_step_title") or "Your Guided Care Plan"
    step_subtitle = st.session_state.get("gcp_step_subtitle") or ""

    # Gather summary advice for inline recommendation
    step_id = str(st.session_state.get("gcp_current_step_id") or st.session_state.get("step_id") or st.session_state.get("current_step") or "")
    is_results = (step_id == "results")
    adv = st.session_state.get("_summary_advice") or {}
    try:
        print(f"[SUMMARY_ADVICE] present={bool(adv)} step={step_id}")
    except Exception:
        pass
    tier_txt = (adv.get("tier") or "—").replace("_", " ").title()
    headline = (adv.get("headline") or f"Based on your answers, I recommend {tier_txt}.").strip()

    # Gather hours suggestion (assist mode only)
    sugg = st.session_state.get("_hours_suggestion") or {}
    band = sugg.get("band")
    user = sugg.get("user") or "-"
    under = bool(sugg.get("under_selected", False))
    nudge_text = (sugg.get("nudge_text") or "").strip() if str(mode).lower() == "assist" else ""
    # Only show hours hint inside header on RESULTS or CP intro
    is_cp_intro = bool(st.session_state.get("cp_intro", False))
    allow_hours_hint = is_results or is_cp_intro
    show_hours_hint = bool(allow_hours_hint and under and nudge_text and not st.session_state.get("_hours_ack"))

    # Compose reason HTML (inside the blue header panel) with Navi recommendation + optional nudge
    navi_text = f"<strong>{headline}</strong>"
    # If advice-level nudge exists, prefer it; else show hours hint when appropriate
    adv_nudge = (adv.get("nudge") or adv.get("nudge_text") or "").strip()
    if adv_nudge:
        navi_text += f"<br>💡 {adv_nudge}"
    elif show_hours_hint:
        navi_text += f"<br>💡 Navi suggests {band} (you selected {user}). {nudge_text}"

    # Add optional subtitle above text if present
    parts: list[str] = []
    if step_subtitle:
        parts.append(step_subtitle)
    parts.append(f"<div id='navi-header-text'>{navi_text}</div>")
    reason_html = "<br/>".join(parts)

    # Render the blue header panel (module variant)
    try:
        from core.ui import render_navi_panel_v2
        render_navi_panel_v2(
            title=step_title,
            reason=reason_html,
            encouragement={"icon": "✨", "text": "You can adjust details anytime.", "status": "in_progress"},
            context_chips=[],
            primary_action={"label": "", "route": ""},
            variant="module",
        )
    except Exception:
        # If blue header unavailable, skip silently (no alternative banners)
        pass
    
    # Render CTA buttons below header ONLY on RESULTS (assist + under-selected and not yet acknowledged)
    if (
        is_results
        and str(mode).lower() == "assist"
        and under
        and not st.session_state.get("_hours_ack")
    ):
        col1, col2, col3 = st.columns([2, 2, 6])

        with col1:
            if st.button(f"✓ Accept {band}", key="hours_accept_btn", use_container_width=True):
                # User accepts suggested hours
                st.session_state["gcp_hours_user_choice"] = band
                st.session_state["_hours_ack"] = True
                st.session_state["_hours_ack_choice"] = "accepted"
                st.session_state["_hours_nudge_new"] = False
                st.session_state["_hours_nudge_key"] = f"{band}->{band}"
                # Force summary to recompute with new hours
                st.session_state.pop("_summary_ready", None)
                print(f"[GCP_HOURS_ACK] action=accepted band={band}")
                st.rerun()

        with col2:
            if st.button("Keep my current selection", key="hours_keep_btn", use_container_width=True):
                # User keeps their selection
                st.session_state["_hours_ack"] = True
                st.session_state["_hours_ack_choice"] = "kept"
                st.session_state["_hours_nudge_new"] = False
                print(f"[GCP_HOURS_ACK] action=kept user={user} suggested={band}")
                st.rerun()
    
    # Play chime once strictly for under-selected hours (assist mode only) on header render
    feat = str(mode).strip('"').lower() if mode else "off"
    ack = bool(st.session_state.get("_hours_ack", False))
    sugg = st.session_state.get("_hours_suggestion") or {}
    under = bool(sugg.get("under_selected", False))
    if (
        feat == "assist" and               # feature enabled
        (is_gcp or is_cp_intro) and        # only GCP/CP intro
        under and                          # user < suggested
        not ack and                        # not acknowledged yet
        st.session_state.get("_hours_nudge_new")  # one-time per key
    ):
        print(
            f"[CHIME] attempt: route={route} cp_intro={is_cp_intro} user={sugg.get('user')} -> sugg={sugg.get('band')}"
        )
        _play_chime_once()
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
    """Render a single, clean paragraph under the Navi header with fallback.

    Shows exactly one concise paragraph. If no LLM advice is available,
    renders a deterministic fallback so the body never appears blank.
    """
    import streamlit as st
    adv = st.session_state.get("_summary_advice") or {}
    tier_txt = (adv.get("tier") or "—").replace("_", " ").title()
    body = (
        (adv.get("what_it_means") or "").strip()
        or " ".join((adv.get("why") or [])[:2]).strip()
    )
    if not body:
        body = f"Based on your answers, {tier_txt} support can help keep things safe and manageable."

    st.markdown("### What this means for you")
    st.markdown(body)

    if adv.get("next_line"):
        st.markdown(
            f"<div style='margin-top:.5rem;color:#0d1f4b'>{adv['next_line']}</div>",
            unsafe_allow_html=True,
        )