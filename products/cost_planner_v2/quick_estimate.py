"""
Cost Planner v2 - Quick Estimate (Tabbed Comparison)

Clean tabbed comparison view with:
- Navi blurbs (context-aware per tab)
- Back to Intro navigation
- Interactive tabs (In-Home, AL, MC)
- Exactly one card per tab
- Choose Your Path Forward radios
- Bottom CTAs
"""

import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from core.navi import render_navi_panel
from products.cost_planner_v2 import comparison_calcs
from products.cost_planner_v2.ui_helpers import go_to_intro


# ==============================================================================
# NAVI BLURBS (Tab-Specific)
# ==============================================================================

NAVI_BLURBS = {
    "home": "Adjust daily hours and home expense to see in-home costs.",
    "al": "Adjust facility costs or home carry costs to explore different scenarios.",
    "mc": "Adjust facility costs or home carry costs to explore different scenarios."
}


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def render():
    """Render Quick Estimate tabbed comparison view."""
    
    print("[PAGE_MOUNT] cost_quick_estimate")
    
    # Get ZIP from session state
    zip_code = st.session_state.get("cost.inputs", {}).get("zip") or st.session_state.get("cost_v2_quick_zip")
    has_zip = bool(zip_code and len(str(zip_code)) == 5)
    
    # Single source of truth for active tab
    cost = st.session_state.setdefault("cost", {})
    sel = cost.setdefault("selected_assessment", "home")
    print(f"[QE] selected_assessment={sel}")
    
    # Get GCP recommendation
    gcp_rec = MCIP.get_care_recommendation()
    recommended_tier = "assisted_living"  # Default fallback
    if gcp_rec and gcp_rec.tier:
        recommended_tier = gcp_rec.tier
        if recommended_tier == "in_home":
            recommended_tier = "in_home_care"
    
    # Initialize assessment availability
    mc_allowed = recommended_tier in ("memory_care", "memory_care_high_acuity")
    available = {
        "home": True,
        "al": True,
        "mc": mc_allowed
    }
    st.session_state.setdefault("cost.assessments_available", available)
    
    # Default selected assessment based on recommendation
    if recommended_tier == "in_home_care":
        default_sel = "home"
    elif recommended_tier in ("memory_care", "memory_care_high_acuity") and mc_allowed:
        default_sel = "mc"
    elif recommended_tier in ("assisted_living", "al"):
        default_sel = "al"
    else:
        default_sel = "home"
    
    st.session_state.setdefault("cost.selected_assessment", default_sel)
    
    # Ensure selected points to a visible tab
    sel = st.session_state["cost.selected_assessment"]
    if not available.get(sel, False):
        st.session_state["cost.selected_assessment"] = "al" if available["al"] else "home"
        sel = st.session_state["cost.selected_assessment"]
    
    # Initialize session state for calculations
    if "comparison_selected_plan" not in st.session_state:
        st.session_state.comparison_selected_plan = None
    if "comparison_facility_breakdown" not in st.session_state:
        st.session_state.comparison_facility_breakdown = None
    if "comparison_inhome_breakdown" not in st.session_state:
        st.session_state.comparison_inhome_breakdown = None
    if "comparison_home_carry_cost" not in st.session_state:
        st.session_state.comparison_home_carry_cost = 0.0
    if "comparison_keep_home" not in st.session_state:
        st.session_state.comparison_keep_home = False
    if "comparison_inhome_hours" not in st.session_state:
        st.session_state.comparison_inhome_hours = 8.0
    if "comparison_hours_per_day" not in st.session_state:
        st.session_state.comparison_hours_per_day = 8.0
    
    # Open centered container
    st.markdown("<div class='sn-container'>", unsafe_allow_html=True)
    
    # Render Navi panel (always at top)
    render_navi_panel(location="product", product_key="cost_planner")
    
    # B) Back to Intro
    if st.button("← Back", key="cp_back", help="Return to options"):
        print(f"[QUICK_ESTIMATE] Navigate back to intro")
        go_to_intro()
    
    st.markdown("")
    
    # ZIP warning if missing
    if not has_zip:
        st.warning("⚠️ **ZIP code required:** Return to the previous page to enter your ZIP code.")
        st.markdown("")
    
    # C) Compact cost tabs (horizontal with costs under labels)
    _render_compact_cost_tabs()
    
    # D) Panels - exactly one card per panel
    st.markdown("<div class='cp-panels'>", unsafe_allow_html=True)
    
    if available.get("home"):
        _render_panel("home", lambda: _render_home_card(zip_code or "00000"))
    
    if available.get("al"):
        _render_panel("al", lambda: _render_facility_card("assisted_living", zip_code or "00000", show_keep_home=True))
    
    if available.get("mc"):
        _render_panel("mc", lambda: _render_facility_card("memory_care", zip_code or "00000", show_keep_home=True))
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # E) Choose Your Path Forward (radios)
    st.markdown("---")
    _render_path_selection()
    
    # F) Bottom CTAs
    _render_bottom_ctas()
    
    # Close container
    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# TAB RENDERING
# ==============================================================================

def _render_compact_cost_tabs():
    """Render compact horizontal cost tabs with costs under labels."""
    from products.cost_planner_v2.ui_helpers import get_cached_monthly_total, format_currency
    
    cost = st.session_state.get("cost", {})
    available = cost.get("assessments_available", {"home": True, "al": True, "mc": False})
    sel = cost.get("selected_assessment", "home")
    
    # Diagnostic print
    print(f"[COMPACT_TABS] render strip sel={sel} totals={cost.get('totals_cache', {})}")
    
    # Get visible tabs in order
    order = [k for k in ("home", "al", "mc") if available.get(k)]
    
    if not order:
        return
    
    label_map = {"home": "In-Home Care", "al": "Assisted Living", "mc": "Memory Care"}
    
    # Render tab container
    st.markdown('<div class="cp-cost-tabs" role="tablist" aria-label="Cost options">', unsafe_allow_html=True)
    
    # Build columns for clickable tabs
    tab_cols = st.columns(len(order))
    
    for idx, assessment in enumerate(order):
        with tab_cols[idx]:
            total = get_cached_monthly_total(assessment)
            total_str = format_currency(total) if total else "—"
            is_active = (assessment == sel)
            label = label_map[assessment]
            
            # Render tab as button with label + cost
            button_label = f"{label}\n{total_str}"
            
            if st.button(
                button_label,
                key=f"cp_tab_{assessment}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                help=f"View {label} details"
            ):
                if not is_active:
                    st.session_state["cost"]["selected_assessment"] = assessment
                    print(f"[COMPACT_TABS] Switched to {assessment}")
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PANEL RENDERING
# ==============================================================================

def _render_panel(assessment: str, render_card_fn):
    """Render a single panel with conditional visibility."""
    # Single source of truth: cost.selected_assessment
    active = (st.session_state["cost"]["selected_assessment"] == assessment)
    clz = "cp-panel is-active" if active else "cp-panel"
    
    st.markdown(f'<div class="{clz}" id="cp-panel-{assessment}" role="tabpanel">', unsafe_allow_html=True)
    if active:  # Only render content for active panel
        render_card_fn()
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# CARD RENDERING
# ==============================================================================

def _render_home_card(zip_code: str):
    """Render In-Home Care card (hours + home expense, no Keep Home toggle)."""
    from products.cost_planner_v2.comparison_calcs import calculate_inhome_scenario
    from products.cost_planner_v2.ui_helpers import totals_set, segcache_set, segcache_get, render_cost_composition_bar
    
    # Calculate scenario
    breakdown = calculate_inhome_scenario(
        zip_code=zip_code,
        hours_per_day=st.session_state.get("comparison_hours_per_day", 8),
        home_carry_override=st.session_state.get("comparison_home_carry_cost", 0) or None
    )
    st.session_state.comparison_inhome_breakdown = breakdown
    
    # Extract segments from breakdown
    care_amt = 0.0
    home_carry_amt = 0.0
    for line in breakdown.lines:
        label_lower = line.label.lower()
        if "home carry" in label_lower:
            if line.applied:
                home_carry_amt += line.value
        else:
            if line.applied and line.value > 0:
                care_amt += line.value
    
    # Cache monthly total and segments
    monthly_total = breakdown.monthly_total
    totals_set("home", monthly_total)
    
    segments = {}
    if care_amt > 0:
        segments["Care Services"] = care_amt
    if home_carry_amt > 0:
        segments["Home Carry"] = home_carry_amt
    segcache_set("home", segments)
    
    print(f"[CARD] rendered home monthly={monthly_total:,.0f}")
    print(f"[COMPOSE] home segs={segcache_get('home')} total={monthly_total:,.0f}")
    
    # Card container
    st.markdown('<div class="cost-card">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="cost-card__title">In-Home Care</div>', unsafe_allow_html=True)
    st.markdown('<div class="cost-card__caption">Estimated monthly total</div>', unsafe_allow_html=True)
    
    # Totals
    st.markdown(f'<div class="cost-total">${breakdown.monthly_total:,.0f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cost-annual">${breakdown.annual_total:,.0f} / yr</div>', unsafe_allow_html=True)
    
    # Composition bar (right after totals)
    render_cost_composition_bar("home")
    
    # Controls: Hours slider
    st.markdown('<div class="cost-section__label">Daily Support Hours</div>', unsafe_allow_html=True)
    current_hours = st.session_state.comparison_inhome_hours
    hours = st.slider(
        "Hours per day",
        min_value=1.0,
        max_value=24.0,
        value=current_hours,
        step=1.0,
        key="qe_home_hours",
        help="Adjust based on care needs",
        label_visibility="collapsed"
    )
    st.markdown(f'<div class="cp-hint">{hours:.1f} h/day</div>', unsafe_allow_html=True)
    
    if hours != st.session_state.comparison_inhome_hours:
        st.session_state.comparison_inhome_hours = hours
        st.session_state.comparison_hours_per_day = hours
        st.rerun()
    
    st.markdown("")
    
    # Home Expense (always included for in-home)
    st.markdown('<div class="cost-section__label">🏠 Home Expense</div>', unsafe_allow_html=True)
    prefill_value = st.session_state.comparison_home_carry_cost
    
    home_carry = st.number_input(
        "Monthly home expense",
        min_value=0.0,
        value=prefill_value,
        step=100.0,
        help="Mortgage, rent, property tax, insurance, maintenance",
        key="qe_home_carry",
        label_visibility="visible"
    )
    
    if home_carry != st.session_state.comparison_home_carry_cost:
        st.session_state.comparison_home_carry_cost = home_carry
        st.rerun()
    
    st.markdown(f'<span class="cp-chip">✓ Included in total (${home_carry:,.0f}/mo)</span>', unsafe_allow_html=True)
    
    st.markdown("")
    st.caption("Actual costs vary by caregiver rates and location.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_facility_card(tier: str, zip_code: str, show_keep_home: bool = False):
    """Render facility card (AL or MC) with optional Keep Home toggle."""
    from products.cost_planner_v2.comparison_calcs import calculate_facility_scenario
    from products.cost_planner_v2.ui_helpers import totals_set, segcache_set, segcache_get, render_cost_composition_bar
    
    # Calculate scenario
    breakdown = calculate_facility_scenario(
        care_type=tier,
        zip_code=zip_code,
        keep_home=st.session_state.get("comparison_keep_home", False),
        home_carry_override=st.session_state.get("comparison_home_carry_cost", 0) or None
    )
    st.session_state.comparison_facility_breakdown = breakdown
    
    # Extract segments from breakdown
    housing_amt = 0.0
    care_amt = 0.0
    home_carry_amt = 0.0
    
    for line in breakdown.lines:
        label_lower = line.label.lower()
        # Base cost + regional = housing/room
        if "base cost" in label_lower or "regional adjustment" in label_lower:
            if line.applied:
                housing_amt += line.value
        # Home carry is separate
        elif "home carry" in label_lower:
            if line.applied:
                home_carry_amt += line.value
        # Everything else is care services
        else:
            if line.applied and line.value > 0:
                care_amt += line.value
    
    # Cache monthly total and segments
    assessment_key = "mc" if tier == "memory_care" else "al"
    monthly_total = breakdown.monthly_total
    totals_set(assessment_key, monthly_total)
    
    segments = {}
    if housing_amt > 0:
        segments["Housing/Room"] = housing_amt
    if care_amt > 0:
        segments["Care Services"] = care_amt
    if home_carry_amt > 0:
        segments["Home Carry"] = home_carry_amt
    segcache_set(assessment_key, segments)
    
    print(f"[CARD] rendered {assessment_key} monthly={monthly_total:,.0f}")
    print(f"[COMPOSE] {assessment_key} segs={segcache_get(assessment_key)} total={monthly_total:,.0f}")
    
    # Card container
    st.markdown('<div class="cost-card">', unsafe_allow_html=True)
    
    # Header
    display_name = "Assisted Living" if tier == "assisted_living" else "Memory Care"
    st.markdown(f'<div class="cost-card__title">{display_name}</div>', unsafe_allow_html=True)
    st.markdown('<div class="cost-card__caption">Estimated monthly total</div>', unsafe_allow_html=True)
    
    # Totals
    st.markdown(f'<div class="cost-total">${breakdown.monthly_total:,.0f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cost-annual">${breakdown.annual_total:,.0f} / yr</div>', unsafe_allow_html=True)
    
    # Composition bar (right after totals)
    render_cost_composition_bar(assessment_key)
    
    # Keep Home toggle (only if show_keep_home=True)
    if show_keep_home:
        st.markdown('<div class="cost-section__label">🏠 Keep Home?</div>', unsafe_allow_html=True)
        
        keep_home = st.checkbox(
            "Keep Home (spouse/partner remains)",
            value=st.session_state.comparison_keep_home,
            key=f"qe_{tier}_keep_home",
            help="Check if you need to maintain your current home while in facility care"
        )
        
        if keep_home != st.session_state.comparison_keep_home:
            st.session_state.comparison_keep_home = keep_home
            st.rerun()
        
        if keep_home:
            prefill_value = st.session_state.comparison_home_carry_cost
            
            home_carry = st.number_input(
                "Monthly home expense",
                min_value=0.0,
                value=prefill_value,
                step=100.0,
                help="Mortgage, rent, property tax, insurance, maintenance",
                key=f"qe_{tier}_home_carry",
                label_visibility="visible"
            )
            
            if home_carry != st.session_state.comparison_home_carry_cost:
                st.session_state.comparison_home_carry_cost = home_carry
                st.rerun()
            
            st.markdown(f'<span class="cp-chip">✓ Added to total (${home_carry:,.0f}/mo)</span>', unsafe_allow_html=True)
        
        st.markdown("")
    
    st.caption("Costs vary by community and level of care.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# PATH SELECTION
# ==============================================================================

def _render_path_selection():
    """Render Choose Your Path Forward radios."""
    st.markdown("### Choose Your Path Forward")
    
    available = st.session_state.get("cost.assessments_available", {"home": True, "al": True, "mc": False})
    sel = st.session_state.get("cost.selected_assessment", "home")
    
    labels = {"home": "In-Home Care", "al": "Assisted Living", "mc": "Memory Care"}
    choices = [k for k, v in available.items() if v]
    
    if not choices:
        return
    
    current_index = choices.index(sel) if sel in choices else 0
    
    new_sel = st.radio(
        "Which scenario would you like to explore in detail?",
        options=choices,
        format_func=lambda k: labels.get(k, k),
        index=current_index,
        key="qe_path_choice",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if new_sel != sel:
        st.session_state["cost.selected_assessment"] = new_sel
        st.rerun()
    
    # Update selected plan for handoff to FA
    plan_key_map = {
        "home": "inhome_in_home_care",
        "al": "facility_assisted_living",
        "mc": "facility_memory_care"
    }
    st.session_state.comparison_selected_plan = plan_key_map.get(new_sel, "inhome_in_home_care")


# ==============================================================================
# BOTTOM CTAs
# ==============================================================================

def _render_bottom_ctas():
    """Render bottom CTA row with optional back link."""
    st.markdown("")
    
    # Optional: Duplicate back link above CTAs for convenience
    if st.button("← Back to Options", key="cp_back_bottom", help="Return to intro page"):
        go_to_intro()
    
    st.markdown("")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button(
            "Help Me Figure Out How to Pay for This ▶",
            type="primary",
            use_container_width=True,
            key="qe_continue"
        ):
            # Store selected breakdown for FA handoff
            selected_plan_key = st.session_state.comparison_selected_plan
            
            if selected_plan_key.startswith("facility_"):
                selected_breakdown = st.session_state.comparison_facility_breakdown
                is_facility = True
            else:
                selected_breakdown = st.session_state.comparison_inhome_breakdown
                is_facility = False
            
            care_cost_monthly = selected_breakdown.monthly_total
            home_carry_monthly = 0.0
            
            if is_facility:
                # Subtract home carry for facility care
                for line in selected_breakdown.lines:
                    if line.label == "Home Carry Cost" and line.applied:
                        home_carry_monthly = line.value
                        care_cost_monthly -= line.value
                        break
            
            # Store for expert_review.py
            st.session_state.cost_v2_quick_estimate = {
                "estimate": {
                    "monthly_adjusted": care_cost_monthly,
                    "monthly_total": selected_breakdown.monthly_total,
                    "care_type": selected_breakdown.care_type,
                    "selected_plan": selected_plan_key,
                }
            }
            
            # Navigate to financial assessment
            st.session_state.cost_v2_step = "auth"
            st.rerun()
    
    with col2:
        if st.button("💾 Save Both", use_container_width=True, key="qe_save_both"):
            st.info("💡 Sign in to save scenarios")
    
    with col3:
        if st.button("← Back to Hub", use_container_width=True, key="qe_back_hub"):
            route_to("hub_concierge")
