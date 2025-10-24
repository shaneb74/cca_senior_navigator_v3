import streamlit as st
import re


# ==============================================================================
# NAVIGATION HELPERS
# ==============================================================================

def go_to_intro():
    """Navigate to Cost Planner Intro (mini-form)."""
    print(f"[NAV] go_to_intro() -> page=cost_intro")
    st.query_params["page"] = "cost_intro"
    st.rerun()


def go_to_quick_estimate():
    """Navigate to Quick Estimate (tabbed comparison)."""
    print(f"[NAV] go_to_quick_estimate() -> page=cost_quick_estimate")
    st.query_params["page"] = "cost_quick_estimate"
    st.rerun()


# ==============================================================================
# SEGMENT CACHE HELPERS
# ==============================================================================

def segcache_get(assessment: str) -> dict | None:
    """Return cached segments for assessment ('home'|'al'|'mc'), or None."""
    return st.session_state.get("cost", {}).get("segments_cache", {}).get(assessment)


def segcache_set(assessment: str, segments: dict[str, float]) -> None:
    """Cache latest segments for assessment; no recompute."""
    cost = st.session_state.setdefault("cost", {})
    segs = cost.setdefault("segments_cache", {})
    segs[assessment] = segments


def totals_set(assessment: str, value: float) -> None:
    """Cache monthly total for assessment; called by card after compute."""
    cost = st.session_state.setdefault("cost", {})
    totals = cost.setdefault("totals_cache", {})
    totals[assessment] = float(value)
    print(f"[CACHE] totals[{assessment}]={value:,.0f}")


def total_to_str(v) -> str:
    """Format total value for display in pills."""
    return "—" if v is None or v == 0 else f"${v:,.0f}"


def money(v: float | None) -> str:
    """Format currency value for display."""
    return "—" if v is None else f"${v:,.0f}"


def parse_hours_band_to_high_end(band: str | None) -> float | None:
    """
    Parse bands like '1-3h', '4-8h', '8-12h' to float high end.
    Returns None if unknown.
    """
    if not band:
        return None
    m = re.match(r"(\d+)\s*-\s*(\d+)\s*h", band)
    if m:
        return float(m.group(2))
    # tolerate single value like '8h'
    m2 = re.match(r"(\d+)\s*h", band)
    if m2:
        return float(m2.group(1))
    return None


def get_llm_hours_high_end_from_gcp() -> float | None:
    """
    Expected GCP state based on logs:
      st.session_state['gcp']['hours_llm']    -> '4-8h'
      or st.session_state['gcp']['hours_band'] -> '4-8h'
    """
    gcp = st.session_state.get("gcp", {})
    band = gcp.get("hours_llm") or gcp.get("hours_band") or gcp.get("hours_assist_band")
    result = parse_hours_band_to_high_end(band)
    print(f"[HOURS_PARSE] gcp_keys={list(gcp.keys())} band={band} result={result}")
    return result


def fmt_hours(h: float | None) -> str:
    """Format hours for display."""
    return f"{h:.1f} h/day" if isinstance(h, (int, float)) else "—"


# ==============================================================================
# HOURS ADVISORY HELPERS (LLM-backed confirmation)
# ==============================================================================

def ensure_home_hours_scalar() -> float | None:
    """
    Ensure cost['home_hours_scalar'] is set from slider or user band.
    Returns the current hours value or None.
    """
    cost = st.session_state.setdefault("cost", {})
    
    # Mirror from slider if set
    v = st.session_state.get("qe_home_hours")
    if isinstance(v, list):
        v = v[0] if v else None
    if isinstance(v, (int, float)):
        cost["home_hours_scalar"] = float(v)
        return float(v)
    
    # Fall back to existing scalar if present
    if "home_hours_scalar" in cost and isinstance(cost["home_hours_scalar"], (int, float)):
        return cost["home_hours_scalar"]
    
    # Fall back to comparison_inhome_hours if present
    v2 = st.session_state.get("comparison_inhome_hours")
    if isinstance(v2, (int, float)):
        cost["home_hours_scalar"] = float(v2)
        return float(v2)
    
    return None


def get_care_context_for_llm() -> dict:
    """Extract stable, non-PII signals from GCP state for LLM context."""
    g = st.session_state.get("gcp", {})
    return {
        "cognition_level": g.get("cognition_level"),
        "behaviors": g.get("behaviors", []),
        "adl_count": g.get("adl_count"),
        "iadl_count": g.get("iadl_count"),
        "falls_risk": g.get("falls_risk"),
        "mobility_level": g.get("mobility_level"),
        "meds_complexity": g.get("meds_complexity"),
        "isolation": g.get("isolation"),
    }


def _hours_advice_cache():
    """Get or create the hours advice cache dict."""
    meta = st.session_state.setdefault("cost", {}).setdefault("meta", {})
    return meta.setdefault("hours_advice_cache", {})


def get_cached_hours_advice(key: str) -> str | None:
    """Retrieve cached LLM-generated hours advice."""
    return _hours_advice_cache().get(key)


def cache_hours_advice(key: str, text: str):
    """Store LLM-generated hours advice in session cache."""
    _hours_advice_cache()[key] = text


def request_llm_hours_advice(ctx: dict, user_hours: float, llm_high: float) -> str | None:
    """
    Generate empathetic Cost Planner hours advisory using LLM.
    Returns 2-3 sentence explanation of why higher hours are recommended.
    Non-blocking, returns None on error/timeout.
    
    Args:
        ctx: Care context dict with cognition_level, behaviors, adl_count, etc.
        user_hours: User's currently selected hours
        llm_high: LLM-suggested hours (high end of band)
    
    Returns:
        HTML-formatted paragraph or None if LLM unavailable
    """
    try:
        from ai.llm_client import get_client
        
        # Get LLM client
        client = get_client(timeout=5)
        if not client:
            print("[HOURS_ADVISORY_LLM] No LLM client available")
            return None
        
        # Build specific care details from context
        care_details = []
        
        if ctx.get("adl_count", 0) >= 3:
            care_details.append(f"assistance with {ctx.get('adl_count')} daily activities")
        elif ctx.get("adl_count", 0) > 0:
            care_details.append(f"help with {ctx.get('adl_count')} daily activities")
        
        if ctx.get("iadl_count", 0) >= 3:
            care_details.append(f"{ctx.get('iadl_count')} instrumental activities")
        
        if ctx.get("falls_risk") == "multiple":
            care_details.append("multiple falls")
        elif ctx.get("falls_risk") == "recent":
            care_details.append("recent fall history")
        
        if ctx.get("cognition_level") in [2, 3]:  # moderate/high
            care_details.append("memory challenges")
        
        if ctx.get("behaviors") and len(ctx.get("behaviors", [])) > 0:
            care_details.append("behavioral support needs")
        
        if ctx.get("mobility_level") in ["walker", "wheelchair"]:
            care_details.append(f"mobility support ({ctx.get('mobility_level')})")
        
        # Build prompt
        care_context = ", ".join(care_details) if care_details else "multiple care needs"
        
        system_prompt = """You are a compassionate care planning advisor helping families understand realistic care hour requirements for in-home care."""
        
        user_prompt = f"""The user selected {user_hours:.1f} hours/day of in-home care, but based on their care needs ({care_context}), we recommend {llm_high:.1f} hours/day.

Write a warm, empathetic 2-3 sentence explanation that:
1. Acknowledges the specific care needs they mentioned
2. Explains that in-home care can be a significant expense and adequate planning prevents cost surprises
3. Mentions that families in similar situations often need around {llm_high:.1f} hours for safe, consistent care

IMPORTANT FORMATTING:
- Use <strong></strong> tags around the phrase "In-home care can be one of the most significant expenses for families"
- Keep it to 2-3 sentences maximum
- Tone: supportive, practical, cost-aware (not scary)
- Return ONLY the paragraph text with HTML tags (no JSON, no preamble)"""
        
        # Call LLM
        text = client.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        if text:
            # Clean up any markdown or extra formatting
            text = text.strip()
            if text.startswith("```"):
                # Remove markdown code blocks
                parts = text.split("```")
                if len(parts) >= 3:
                    text = parts[1].strip()
                    if text.startswith("html"):
                        text = text[4:].strip()
            print(f"[HOURS_ADVISORY_LLM] Generated {len(text)} chars")
            return text
        else:
            print("[HOURS_ADVISORY_LLM] No response from LLM")
            return None
            
    except Exception as e:
        print(f"[HOURS_ADVISORY_LLM_ERR] {e}")
        return None


def render_confirm_hours_if_needed(current_hours_key: str = "qe_home_hours"):
    """Render Navi-style hours confirmation advisory when LLM suggestion differs from current hours."""
    cost = st.session_state.setdefault("cost", {})
    meta = cost.setdefault("meta", {})
    sel = cost.get("selected_assessment", "home")
    
    print(f"[HOURS_CHECK] sel={sel}")
    if sel != "home":
        return  # only in the In-Home assessment

    # 1) LLM suggested hours (high end of band)
    llm_high = get_llm_hours_high_end_from_gcp()
    print(f"[HOURS_CHECK] llm_high={llm_high}")
    if llm_high is None:
        return

    # 2) Current hours value (use new helper)
    current = ensure_home_hours_scalar()
    print(f"[HOURS_CHECK] current={current} key={current_hours_key}")

    # 3) Don't show if close enough or already accepted/dismissed
    if current is None or not isinstance(current, (int, float)):
        print(f"[HOURS_CHECK] current not a number, returning")
        return
    if abs(current - llm_high) < 0.5:
        print(f"[HOURS_CHECK] current close to llm_high (diff={abs(current - llm_high)}), returning")
        return

    # Show only if the user hasn't decided for this llm_high yet
    decision_key = f"home_hours_decided_{llm_high}"
    if meta.get(decision_key):
        print(f"[HOURS_CHECK] already decided {decision_key}, returning")
        return
    
    print(f"[HOURS_ADVISORY] show user={current} suggested={llm_high}")

    # 4) Get or generate LLM advice (empathetic, personalized)
    advice_key = f"home_hours_{llm_high}"
    advice = get_cached_hours_advice(advice_key)
    
    if not advice:
        # Build context for LLM
        ctx = get_care_context_for_llm()
        
        # Request LLM-generated advice
        advice = request_llm_hours_advice(ctx, user_hours=current, llm_high=llm_high)
        
        if advice:
            cache_hours_advice(advice_key, advice)
            print(f"[HOURS_ADVISORY] LLM advice generated and cached")
        else:
            print(f"[HOURS_ADVISORY] LLM unavailable, building fallback")
    
    # 5) Use LLM advice or fallback
    if not advice:
        # Fallback: Build from actual GCP data
        g = st.session_state.get("gcp", {})
        needs_list = []
        
        # Extract specific care needs from GCP state
        adl_needs = g.get("adl_needs", [])
        iadl_needs = g.get("iadl_needs", [])
        behaviors = g.get("behaviors", [])
        
        # Build natural needs phrase from actual selections
        if adl_needs:
            needs_list.extend([n.replace("_", " ") for n in adl_needs[:3]])
        if iadl_needs:
            needs_list.extend([n.replace("_", " ") for n in iadl_needs[:2]])
        
        # Build natural language list
        if needs_list:
            if len(needs_list) == 1:
                needs_phrase = needs_list[0]
            elif len(needs_list) == 2:
                needs_phrase = f"{needs_list[0]} and {needs_list[1]}"
            else:
                needs_phrase = ", ".join(needs_list[:-1]) + f", and {needs_list[-1]}"
        else:
            needs_phrase = "bathing, dressing, meals, medication, and mobility"
        
        # Add memory/behavior context if applicable
        context_phrase = ""
        cognition_level = g.get("cognition_level")
        has_memory = cognition_level in [2, 3] if cognition_level else False
        has_behaviors = len(behaviors) > 0
        
        if has_memory and has_behaviors:
            context_phrase = ", along with some memory and decision-making challenges"
        elif has_memory:
            context_phrase = ", along with some memory challenges"
        elif has_behaviors:
            context_phrase = ", along with some behavioral support needs"
        
        # Construct the empathetic paragraph
        advice = f"""You mentioned needing help with {needs_phrase}{context_phrase}. That level of daily support often means several hours of hands-on care each day. <strong>In-home care can be one of the most significant expenses for families</strong>, and if those hours aren't planned for, the costs can rise quickly. Many families in similar situations find that planning for around {fmt_hours(llm_high)} of support a day gives a more realistic picture of what safe, consistent care at home will cost."""
    
    print(f"[HOURS_ADVISORY] rendered=True user={current} suggested={llm_high} llm_advice={bool(advice)}")

    # 6) Render Navi-style advisory UI
    st.markdown(
        f"""
        <div class="hours-advisory">
          <div class="hours-advisory__navi-title">✨ Navi says</div>
          <p class="hours-advisory__text">{advice}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 7) Two elegant buttons (primary = accept; secondary = keep)
    st.markdown('<div class="hours-actions">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        if st.button(f"Update Hours to {fmt_hours(llm_high)}", key=f"btn_accept_{llm_high}", use_container_width=True):
            # Update the comparison values (not the widget key directly)
            st.session_state["comparison_inhome_hours"] = float(llm_high)
            st.session_state["comparison_hours_per_day"] = float(llm_high)
            cost["home_hours_scalar"] = float(llm_high)
            meta[decision_key] = "accepted"
            print(f"[HOURS_CONFIRM] accept={llm_high}")
            
            # Persist hours decision
            try:
                from core.user_persist import persist_costplan, get_current_user_id
                persist_costplan(get_current_user_id(), {
                    "event": "hours_confirm_accept",
                    "corr_id": st.session_state.get("corr_id", "unknown"),
                    "home_hours": float(llm_high),
                    "previous_hours": float(current),
                })
            except Exception as e:
                print(f"[USER_PERSIST_ERR] hours_confirm_accept failed: {e}")
            
            st.rerun()
    with col2:
        if st.button(f"Keep {fmt_hours(current)}", key=f"btn_keep_{llm_high}", use_container_width=True):
            meta[decision_key] = "kept"
            print(f"[HOURS_CONFIRM] keep={current} (llm={llm_high})")
            
            # Persist hours decision
            try:
                from core.user_persist import persist_costplan, get_current_user_id
                persist_costplan(get_current_user_id(), {
                    "event": "hours_confirm_keep",
                    "corr_id": st.session_state.get("corr_id", "unknown"),
                    "home_hours": float(current),
                    "suggested_hours": float(llm_high),
                })
            except Exception as e:
                print(f"[USER_PERSIST_ERR] hours_confirm_keep failed: {e}")
            
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # Close hours-actions div


def donut_cost_chart(segments: dict[str, float], total_label: str, emphasize: str = "Care Services"):
    """
    Render a compact donut showing monthly composition.
    
    Args:
        segments: {"Housing/Room": x, "Care Services": y, "Home Carry": z}
        total_label: "$6,750/mo" (displayed in center)
        emphasize: label to visually emphasize (default: "Care Services")
    """
    try:
        import plotly.express as px
    except Exception as e:
        # graceful fallback: just show the pills/labels
        st.caption("Monthly total composition")
        for lbl, val in (segments or {}).items():
            st.markdown(f"- **{lbl}** {money(val)}")
        print(f"[DONUT_FALLBACK] plotly import failed: {e}")
        return

    # rest of your existing plotly chart code follows here ↓
    segs = {k: float(v) for k, v in segments.items() if v and float(v) > 0}
    if not segs:
        return

    labels = list(segs.keys())
    values = list(segs.values())

    # Emphasize care wedge with saturated brand palette
    base_colors = {
        "Housing/Room": "#CBD5E1",  # slate-300
        "Care Services": "#0f2a5f", # brand navy (emphasize)
        "Home Carry": "#7aa2ff"    # light brand blue
    }
    colors = [base_colors.get(l, "#A3BFFA") for l in labels]

    # Ensure emphasized label gets the darkest color
    for i, l in enumerate(labels):
        if l.lower() == emphasize.lower():
            colors[i] = "#0f2a5f"  # darkest
        elif l == "Housing/Room":
            colors[i] = "#CBD5E1"
        elif l == "Home Carry":
            colors[i] = "#7aa2ff"

    fig = px.pie(values=values, names=labels, hole=0.72, color=labels, color_discrete_sequence=colors)
    fig.update_traces(
        textinfo="none",
        hovertemplate="%{label}<br>$%{value:,.0f}/mo<extra></extra>",
        sort=False
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=220,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=total_label, showarrow=False, font=dict(size=20, color="#0f2a5f"))]
    )
    st.plotly_chart(fig, use_container_width=True)


def render_care_chunk_compare_blurb(active: str):
    """Render care chunk comparison when both home and AL segments are cached."""
    home = segcache_get("home") or {}
    al = segcache_get("al") or {}
    home_care = float(home.get("Care Services", 0))
    al_care = float(al.get("Care Services", 0))
    
    if home_care > 0 and al_care > 0:
        ratio = home_care / al_care
        st.caption(f"💡 Care at home (~{money(home_care)}/mo) is **{ratio:,.1f}×** the care portion in Assisted Living (~{money(al_care)}/mo).")


# ==============================================================================
# NAVI RENDERING HELPERS
# ==============================================================================

def render_intro_navi(title: str = "Let's look at costs", reason: str = None) -> str:
    """Render Navi tip for intro page.
    
    Args:
        title: Header title text
        reason: Optional reason text (auto-generated if None)
    
    Returns:
        HTML string for Navi tip
    """
    from core.mcip import MCIP
    
    if reason is None:
        # Auto-generate reason from GCP recommendation
        gcp_rec = MCIP.get_care_recommendation()
        rec_tier = None
        if gcp_rec and hasattr(gcp_rec, 'tier'):
            rec_tier = gcp_rec.tier
        
        tier_display = None
        if rec_tier:
            tier_display = rec_tier.replace("_", " ").title()
        
        reason = (
            f"I've pre-selected {tier_display} from your Guided Care Plan. You can explore other scenarios too."
            if tier_display
            else "We'll help you explore different care options and their costs."
        )
    
    return f"""<div class="navi-tip" style="background: #f0f7ff; border-left: 4px solid #2563eb; padding: 1rem; margin-bottom: 1.5rem; border-radius: 4px;">
        <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">💡 {title}</div>
        <div style="color: #475569;">{reason}</div>
        </div>"""


# ==============================================================================
# COST CACHE HELPERS
# ==============================================================================

def get_cached_monthly_total(assessment: str) -> float | None:
    """
    Returns the most recently computed monthly total for a given assessment type.
    Reads from session cache; does not recalculate.
    
    Args:
        assessment: Assessment key ("home", "al", or "mc")
        
    Returns:
        Float monthly total or None if not cached
    """
    cost = st.session_state.get("cost", {})
    totals = cost.get("totals_cache", {})
    value = totals.get(assessment)
    if value is not None:
        try:
            return float(value)
        except Exception:
            return None
    return None


def format_currency(value: float | None) -> str:
    """Format currency value for display.
    
    Args:
        value: Float value or None
        
    Returns:
        Formatted string (e.g., "$5,000" or "—")
    """
    if value is None or value == 0:
        return "—"
    return f"${value:,.0f}"


# ==============================================================================
# PRESENTATIONAL HELPERS
# ==============================================================================

def render_cp_hint(text: str, kind: str = "info"):
    """Render a compact inline hint as HTML (presentation-only).
    
    Args:
        text: The hint text to display
        kind: Visual variant, e.g., 'info', 'warn', 'success'
    """
    html = f"<div class='cp-hint cp-hint--{kind}'>{text}</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_cp_section_title(text: str):
    """Render a compact section title with consistent sizing.
    
    Args:
        text: The title text to display
    """
    st.markdown(f"<div class='cp-section-title'>{text}</div>", unsafe_allow_html=True)


def render_cp_tabs():
    """Render interactive three-tab bar (wired to cost.selected_assessment).
    
    Tabs: In-Home Care, Assisted Living, Memory Care (conditionally visible).
    Clicking a tab updates cost.selected_assessment and reruns.
    """
    import streamlit as st
    
    available = st.session_state.get("cost.assessments_available", {"home": True, "al": True, "mc": False})
    sel = st.session_state.get("cost.selected_assessment", "home")
    
    st.markdown('<div class="cp-tabs" role="tablist" aria-label="Cost options">', unsafe_allow_html=True)
    
    # Render only available tabs
    cols = []
    if available.get("home"):
        cols.append("home")
    if available.get("al"):
        cols.append("al")
    if available.get("mc"):
        cols.append("mc")
    
    tab_cols = st.columns(len(cols))
    
    for idx, assessment in enumerate(cols):
        with tab_cols[idx]:
            is_active = (sel == assessment)
            label_map = {"home": "In-Home Care", "al": "Assisted Living", "mc": "Memory Care"}
            label = label_map.get(assessment, assessment)
            
            # Render as a styled button
            if st.button(
                label,
                key=f"cp_tab_{assessment}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                if not is_active:
                    st.session_state["cost.selected_assessment"] = assessment
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_cp_panel(assessment: str, render_card_fn):
    """Render a single panel with is-active class based on cost.selected_assessment.
    
    Args:
        assessment: Panel key ('home', 'al', or 'mc')
        render_card_fn: Function to call to render the card content
    """
    import streamlit as st
    
    # Single source of truth: cost["selected_assessment"]
    sel = st.session_state.get("cost", {}).get("selected_assessment", "home")
    is_active = (sel == assessment)
    panel_class = "cp-panel is-active" if is_active else "cp-panel"
    
    st.markdown(f'<div class="{panel_class}" id="cp-panel-{assessment}" role="tabpanel">', unsafe_allow_html=True)
    if is_active:  # Only render content for active panel to save compute
        render_card_fn()
    st.markdown('</div>', unsafe_allow_html=True)


def render_cost_composition_bar(assessment: str):
    """Render compact stacked horizontal bar + pills showing cost composition.
    
    Visualizes cost breakdown with 2-3 segments:
    - In-Home: Care Services + Home Carry
    - Facility: Housing/Room + Care Services (+ Home Carry if toggled)
    
    Args:
        assessment: Assessment key ('home', 'al', or 'mc')
    """
    import altair as alt
    import pandas as pd
    
    segs = segcache_get(assessment) or {}
    # Filter to only non-zero segments
    segs = {k: float(v or 0) for k, v in segs.items() if v and float(v) > 0}
    
    if not segs:
        # Graceful fallback: nothing to show yet
        return
    
    # Build dataframe with segments
    df = pd.DataFrame({"label": list(segs.keys()), "value": list(segs.values())})
    df["bar"] = "total"  # ← Force single row
    
    # Create compact stacked bar chart (thicker and rounded for visibility)
    bar = alt.Chart(df).mark_bar(cornerRadius=4).encode(
        x=alt.X("value:Q", stack="zero", axis=None),
        y=alt.Y("bar:N", axis=None),  # Single row using constant "bar" field
        color=alt.Color(
            "label:N",
            scale=alt.Scale(range=["#0f2a5f", "#3b6ae0", "#7aa2ff"]),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("label:N", title="Component"),
            alt.Tooltip("value:Q", format=",.0f", title="Amount")
        ]
    ).properties(height=28)  # Increased from 22 to 28 for better visibility
    
    # Render chart with clean styling
    chart = bar.configure_view(stroke=None)
    st.altair_chart(chart, use_container_width=True)
    
    # Pills under the bar
    st.markdown('<div class="cp-seg-pills">', unsafe_allow_html=True)
    for lbl, val in segs.items():
        st.markdown(
            f'<span class="cp-pill">{lbl} ${val:,.0f}</span>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    print(f"[BAR_RENDER] {assessment} labels={list(segs.keys())} values={list(segs.values())}")
