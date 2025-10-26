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
    - Recommendation is for in-home care (not facility-based)
    
    The suggestion is NON-BINDING - user remains in full control.
    """
    # Check if feature is enabled
    try:
        from products.concierge_hub.gcp_v4.modules.care_recommendation.logic import gcp_hours_mode
        mode = gcp_hours_mode()
    except Exception:
        return  # Can't check mode, skip

    if mode != "assist":
        return  # Only render in assist mode

    # Check the care tier - only show hours for in-home recommendations
    summary_advice = st.session_state.get("_summary_advice", {})
    care_tier = summary_advice.get("tier", "")

    # Show hours for in-home tiers OR when comparing with staying home
    facility_tiers = ["assisted_living", "memory_care", "memory_care_high_acuity"]
    compare_inhome = st.session_state.get("cost.compare_inhome", False)

    # Diagnostic log
    try:
        print(f"[HOURS_SUGGEST_CHECK] tier={care_tier} is_facility={care_tier in facility_tiers} compare={compare_inhome}")
    except Exception:
        pass

    if care_tier in facility_tiers and not compare_inhome:
        return  # Don't show hours for facility-based care unless comparing with home

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
            "<div style='background-color: #fff3cd; padding: 0.75rem 1rem; border-radius: 0.5rem; "
            "border-left: 4px solid #ffc107; margin-bottom: 1rem;'>",
            unsafe_allow_html=True,
        )

        st.markdown("⚠️ **Please reconsider your hours selection**", unsafe_allow_html=True)
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
            "<div style='background-color: #f9f9f9; padding: 0.75rem 1rem; border-radius: 0.5rem; "
            "border-left: 3px solid #6c757d; margin-bottom: 1rem;'>",
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
    - Recommendation is for in-home care (not facility-based)
    
    The nudge is advisory only - does not change user's selection.
    """
    import os

    import streamlit as st

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

    # Check the care tier - only show hours for in-home recommendations
    summary_advice = st.session_state.get("_summary_advice", {})
    care_tier = summary_advice.get("tier", "")

    # Show hours for in-home tiers OR when comparing with staying home
    facility_tiers = ["assisted_living", "memory_care", "memory_care_high_acuity"]
    compare_inhome = st.session_state.get("cost.compare_inhome", False)

    # Diagnostic log
    try:
        print(f"[HOURS_WARNING_CHECK] tier={care_tier} is_facility={care_tier in facility_tiers} compare={compare_inhome}")
    except Exception:
        pass

    if care_tier in facility_tiers and not compare_inhome:
        return  # Don't show hours for facility-based care unless comparing with home

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
    
    # IMPORTANT: Don't duplicate page title in Navi on intro step
    step_id = str(st.session_state.get("gcp_current_step_id") or "")
    if step_id == "intro":
        step_title = None  # Let module header handle the single page title

    # Gather summary advice for inline recommendation
    step_id = str(st.session_state.get("gcp_current_step_id") or st.session_state.get("step_id") or st.session_state.get("current_step") or "")
    is_results = (step_id == "results")
    adv = st.session_state.get("_summary_advice") or {}

    # Guard against tier=None: Use published tier as fallback to prevent flicker
    tier_from_advice = adv.get("tier")
    if not tier_from_advice:
        # Fallback chain: gcp.final_tier → careplan → None
        tier_from_advice = st.session_state.get("gcp.final_tier")
        if not tier_from_advice:
            try:
                from core.household import get_careplan_for
                person_id = st.session_state.get("person_id", "self")
                careplan = get_careplan_for(person_id)
                if careplan and hasattr(careplan, 'tier'):
                    tier_from_advice = careplan.tier
            except Exception:
                pass

    tier_txt = (tier_from_advice or "—").replace("_", " ").title()

    # Log tier resolution for debugging first-click flicker
    try:
        print(f"[SUMMARY_ADVICE] present={bool(adv)} step={step_id} tier={tier_from_advice or 'None'}")
    except Exception:
        pass

    # Stable header strategy: Always show something to prevent first-click flicker
    # Track if user has provided ANY answers yet to determine readiness
    module_state = st.session_state.get("gcp_v4_care_recommendation_module", {})
    has_answers = bool(module_state and len([k for k in module_state.keys() if not k.startswith("_")]) > 0)

    # Only show recommendations on RESULTS step or when summary is ready
    summary_ready = st.session_state.get("summary_ready", False)
    can_recommend = is_results or summary_ready

    # Log readiness for first-click flicker debugging
    if step_id in ("about_you", "daily_living"):
        is_first_answer = has_answers and not st.session_state.get(f"_navi_step_{step_id}_logged", False)
        if is_first_answer:
            print(f"[NAVI_STEP] step={step_id} ready={has_answers} event=first_click")
            st.session_state[f"_navi_step_{step_id}_logged"] = True

    # Use personalized intro copy for intro step
    if step_id == "intro":
        try:
            from products.concierge_hub.gcp_v4.modules.care_recommendation.intro import load_intro_overrides
            from core.text import personalize_text
            overrides = load_intro_overrides()
            copy = overrides.get("copy", {})
            headline = personalize_text(copy.get("navi_subtitle", "I'm here to guide you through each question."))
            navi_body = personalize_text(copy.get("navi_body", ""))
            navi_info = personalize_text(copy.get("navi_info", ""))
        except Exception:
            headline = "I'm here to guide you through each question."
            navi_body = ""
            navi_info = ""
    elif can_recommend:
        headline = (adv.get("headline") or f"Based on your answers, I recommend {tier_txt}.").strip()
    else:
        # Use neutral anticipatory copy for early steps - ALWAYS show this until results ready
        # This prevents the header from disappearing on first widget interaction
        headline = (adv.get("headline") or "I'm here to guide you through each question.").strip()

    # Gather hours suggestion (assist mode only)
    sugg = st.session_state.get("_hours_suggestion") or {}
    band = sugg.get("band")
    user = sugg.get("user") or "-"
    under = bool(sugg.get("under_selected", False))
    nudge_text = (sugg.get("nudge_text") or "").strip() if str(mode).lower() == "assist" else ""
    # Only show hours hint inside header on RESULTS or CP intro
    is_cp_intro = bool(st.session_state.get("cp_intro", False))
    allow_hours_hint = is_results or is_cp_intro

    # Check care tier - show hours for in-home OR when comparing with staying home
    # Use tier_from_advice (already guarded against None above) instead of reading from adv again
    care_tier = tier_from_advice or ""
    facility_tiers = ["assisted_living", "memory_care", "memory_care_high_acuity"]
    compare_inhome = st.session_state.get("cost.compare_inhome", False)
    hours_for_facility = care_tier in facility_tiers and not compare_inhome

    # Diagnostic log with guarded tier
    try:
        print(f"[HOURS_HEADER_CHECK] tier={care_tier or 'None'} is_facility={care_tier in facility_tiers} "
              f"compare={compare_inhome} hide_hours={hours_for_facility}")
    except Exception:
        pass

    show_hours_hint = bool(allow_hours_hint and under and nudge_text and not st.session_state.get("_hours_ack") and not hours_for_facility)

    # Compose reason HTML (inside the blue header panel) with Navi recommendation + optional nudge
    if step_id == "intro":
        # For intro, render subtitle/body/info from overrides (no title)
        parts: list[str] = []
        parts.append(f"<div id='navi-header-text'><strong>{headline}</strong></div>")
        if navi_body:
            parts.append(f"<div>{navi_body}</div>")
        if navi_info:
            parts.append(f"<div><small>{navi_info}</small></div>")
        reason_html = "<br/>".join(parts)
    else:
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

    # Log navigation render state
    try:
        import uuid
        nav_id = str(uuid.uuid4())[:12]
        has_text = bool(headline and len(headline) > 0)
        ready = st.session_state.get("summary_ready", False)
        print(f"[NAV_RENDER] tier={tier_txt} has_text={has_text} ready={ready} id={nav_id}")
    except Exception:
        pass

    # Render the blue header panel (module variant) with LLM enhancement
    try:
        from core.ui import render_navi_panel_v2
        from core.flags import get_flag_value
        
        # Check if LLM enhancement is enabled
        llm_mode = get_flag_value("FEATURE_LLM_NAVI", "off")
        
        # Default encouragement
        encouragement = {"icon": "✨", "text": "You can adjust details anytime.", "status": "in_progress"}
        enhanced_reason = reason_html
        
        # Try LLM enhancement if enabled
        if llm_mode in ["assist", "adjust"]:
            try:
                from ai.navi_llm_engine import NaviLLMEngine, build_navi_context_from_session
                
                # Build context for LLM
                navi_context = build_navi_context_from_session()
                navi_context.current_location = "gcp_v4"
                navi_context.product_context = {
                    "product": "gcp_v4",
                    "module": "care_recommendation",
                    "step_title": step_title,
                    "step_type": "module_assessment"
                }
                
                # Generate contextual advice
                advice = NaviLLMEngine.generate_advice(navi_context)
                if advice:
                    # Enhance encouragement with LLM content
                    encouragement = {
                        "icon": "🌟", 
                        "text": advice.message or "You can adjust details anytime.",
                        "status": "in_progress"
                    }
                    
                    # Enhance reason with guidance if available
                    if advice.guidance and advice.guidance.strip():
                        enhanced_reason = f"{reason_html}<br><em>{advice.guidance}</em>"
                        
            except Exception as e:
                print(f"[GCP_LLM] Enhancement failed, using static content: {e}")
                # Fall back to static content
                pass
        
        render_navi_panel_v2(
            title=step_title,
            reason=enhanced_reason,
            encouragement=encouragement,
            context_chips=[],
            primary_action={"label": "", "route": ""},
            variant="module",
        )
    except Exception:
        # If blue header unavailable, skip silently (no alternative banners)
        pass

    # Render CTA buttons below header ONLY on RESULTS (assist + under-selected and not yet acknowledged + not facility-based)
    if (
        is_results
        and str(mode).lower() == "assist"
        and under
        and not st.session_state.get("_hours_ack")
        and not hours_for_facility
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
        not hours_for_facility and         # not facility-based care
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
    
    Dynamically generates the "costs" line based on the final tier to ensure
    it matches the post-adjudication recommendation.
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

    # ========================================
    # DYNAMIC COSTS LINE: Follows final tier (post-adjudication)
    # ========================================
    # Get the final tier from canonical location (after adjudication)
    final_tier = st.session_state.get("gcp", {}).get("published_tier", "")
    interim = bool(st.session_state.get("_show_mc_interim_advice", False))
    
    # Generate costs line based on final tier
    if interim or final_tier == "assisted_living":
        cost_line = "Let's explore the costs associated with assisted living options."
    elif final_tier in ("memory_care", "memory_care_high_acuity"):
        cost_line = "Let's explore the costs associated with memory care options."
    elif final_tier in ("in_home", "in_home_care"):
        cost_line = "Let's explore the costs for in-home care and support."
    else:
        # Fallback from LLM advice or generic
        cost_line = adv.get("next_line") or "Let's explore the costs and see how to make it work for you."
    
    st.markdown(
        f"<div style='margin-top:.5rem;color:#0d1f4b'>{cost_line}</div>",
        unsafe_allow_html=True,
    )


def render_interim_al_callout():
    """
    Render interim Assisted Living callout card when Memory Care is recommended
    but no formal diagnosis is present. Provides clear guidance on the interim step.
    """
    st.markdown("""
<div class="interim-callout" role="note" aria-live="polite">
  <div class="interim-callout__eyebrow">Interim next step</div>
  <h4 class="interim-callout__title">Assisted Living is recommended while you seek a formal diagnosis</h4>
  <p class="interim-callout__body">
    Many Memory Care communities ask for a confirmed dementia/Alzheimer's (or related) diagnosis to enroll.
    While you arrange an evaluation, Assisted Living with memory support can provide safety, structure, and continuity.
  </p>
</div>
""", unsafe_allow_html=True)


def vrhythm(section: str):
    """
    Render named vertical rhythm spacer for predictable layout spacing.
    Use instead of st.write("") or st.markdown("") for consistency.
    """
    st.markdown(f'<div class="vr vr--{section}"></div>', unsafe_allow_html=True)
