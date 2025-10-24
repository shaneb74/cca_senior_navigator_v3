import streamlit as st


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
    
    # Create compact stacked bar chart
    bar = alt.Chart(df).mark_bar().encode(
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
    ).properties(height=22)
    
    # Render chart with clean styling
    chart = bar.configure_view(stroke=None)
    st.altair_chart(chart, use_container_width=True)
    
    # Pills under the bar
    st.markdown('<div class="cp-seg-pills">', unsafe_allow_html=True)
    for lbl, val in segs.items():
        st.markdown(
            f'<span class="cp-pill">{lbl} {total_to_str(val)}</span>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    print(f"[BAR_RENDER] {assessment} labels={list(segs.keys())} values={list(segs.values())}")
