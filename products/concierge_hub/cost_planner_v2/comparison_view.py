"""
Cost Planner v2 - Comparison View (Phase 2)

Side-by-side comparison of Recommended Plan vs In-Home Care.
Uses care-type-specific modifiers and real calculations.
"""

import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from products.concierge_hub.cost_planner_v2 import comparison_calcs
from products.concierge_hub.cost_planner_v2.comparison_calcs import ScenarioBreakdown

# ==============================================================================
# GCP HOURS MAPPING
# ==============================================================================

def _get_gcp_hours_per_day() -> float:
    """Get hours per day from GCP recommendation, with categorical mapping.
    
    GCP provides categorical answers which map to numeric hours:
    - "Less than 1 hour" → 1
    - "1–3 hours" → 2
    - "4–8 hours" → 8
    - "24-hour support" → 24
    
    Returns:
        Float hours per day (default: 8.0 if not found)
    """
    # Try to get from GCP data structure
    gcp_data = st.session_state.get("gcp_care_recommendation", {})
    hours_category = gcp_data.get("hours_per_day", "")

    # Mapping dictionary (handles various formats)
    hours_map = {
        # Standard formats
        "less than 1 hour": 1.0,
        "<1h": 1.0,
        "1-3h": 2.0,
        "1–3 hours": 2.0,
        "4-8h": 8.0,
        "4–8 hours": 8.0,
        "24h": 24.0,
        "24-hour support": 24.0,
        # Additional variations
        "less_than_1": 1.0,
        "1_to_3": 2.0,
        "4_to_8": 8.0,
        "24_hour": 24.0,
    }

    # Normalize and lookup
    hours_normalized = str(hours_category).lower().strip()
    mapped_hours = hours_map.get(hours_normalized, 8.0)

    return mapped_hours


# ==============================================================================
# NAVI BLURBS (Compare Stage)
# ==============================================================================

NAVI_BLURBS = {
    "home": "Adjust daily hours and home expense to see in-home costs.",
    "al": "If you'll keep the home during a move, toggle 'Keep Home?' and adjust the amount.",
    "mc": "Memory care includes specialized support; toggle 'Keep Home?' if you'll keep the home."
}

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def render_comparison_view(zip_code: str | None):
    """
    Render tabbed comparison view with minimal cards (presentation-only).
    
    TWO-STAGE FLOW:
    - Stage 1 (tabs_revealed=False): Show mini-form + CTA only
    - Stage 2 (tabs_revealed=True): Show Navi + back + tabs + radios + CTAs
    
    Tabs: In-Home Care, Assisted Living, Memory Care (conditionally visible).
    Each tab shows its minimal card (HomeCard or FacilityCard).
    
    ZIP gating: If ZIP missing, show placeholder cards with warning banner.
    
    Args:
        zip_code: ZIP code for regional pricing (None if not provided yet)
    """

    # Initialize two-stage state keys
    st.session_state.setdefault("cost.tabs_revealed", False)
    st.session_state.setdefault("cost.compare_breadcrumb", False)

    # Check if tabs should be shown
    tabs_revealed = st.session_state.get("cost.tabs_revealed", False)

    # Check if ZIP is present for compute gating
    has_zip = bool(zip_code and len(str(zip_code)) == 5)

    # Single source of truth for active tab
    cost = st.session_state.setdefault("cost", {})
    sel = cost.get("selected_assessment", "home")
    print(f"[COMPARISON_VIEW] selected_assessment={sel}")

    # Get GCP recommendation to determine Memory Care availability
    gcp_rec = MCIP.get_care_recommendation()
    recommended_tier = "assisted_living"  # Default fallback
    if gcp_rec and gcp_rec.tier:
        recommended_tier = gcp_rec.tier
        # NORMALIZE: GCP might return "in_home" but we need "in_home_care"
        if recommended_tier == "in_home":
            recommended_tier = "in_home_care"

    # // reason: Initialize assessment availability and selection (state mgmt for tabs)
    # Memory Care is available if recommended or if user has MC-qualifying conditions
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
    elif recommended_tier in ("memory_care", "memory_care_high_acuity"):
        default_sel = "mc"
    else:
        default_sel = "al"

    st.session_state.setdefault("cost.selected_assessment", default_sel)

    # Ensure selected always points to a visible tab
    sel = st.session_state["cost.selected_assessment"]
    if not available.get(sel, False):
        st.session_state["cost.selected_assessment"] = "al" if available["al"] else "home"
        sel = st.session_state["cost.selected_assessment"]

    # Initialize session state for selected plan
    if "comparison_selected_plan" not in st.session_state:
        st.session_state.comparison_selected_plan = None

    # Initialize storage for calculated scenarios (for later handoff to FA)
    if "comparison_facility_breakdown" not in st.session_state:
        st.session_state.comparison_facility_breakdown = None
    if "comparison_inhome_breakdown" not in st.session_state:
        st.session_state.comparison_inhome_breakdown = None

    # Initialize home carry cost and keep home flag
    if "comparison_home_carry_cost" not in st.session_state:
        st.session_state.comparison_home_carry_cost = 0.0
    if "comparison_keep_home" not in st.session_state:
        st.session_state.comparison_keep_home = False

    # Initialize hours from GCP (only on first load)
    if "comparison_inhome_hours" not in st.session_state:
        gcp_hours = _get_gcp_hours_per_day()
        st.session_state.comparison_inhome_hours = gcp_hours
        st.session_state.comparison_hours_gcp_source = gcp_hours  # Track original GCP value

    # Also ensure comparison_hours_per_day is synced (used in calculations)
    if "comparison_hours_per_day" not in st.session_state:
        st.session_state.comparison_hours_per_day = st.session_state.comparison_inhome_hours

    # ==============================================================================
    # TWO-STAGE CONDITIONAL RENDERING
    # ==============================================================================

    if not tabs_revealed:
        # STAGE 1: Mini-form + CTA only (prepare gate handles this, nothing to render here)
        # The prepare gate is rendered in intro.py before this function is called
        # Return early so tabs/cards don't render
        return

    # STAGE 2: Navi + back + tabs + cards + radios + CTAs

    # Render Navi blurb based on selected assessment
    navi_blurb = NAVI_BLURBS.get(sel, "Adjust your inputs to see how costs change.")
    st.markdown(f'<div class="navi-tip" style="margin-bottom: 16px; color: var(--text-600); font-size: 0.95rem;">{navi_blurb}</div>', unsafe_allow_html=True)

    # Render back button
    if st.session_state.get("cost.compare_breadcrumb", False):
        if st.button("← Back", key="cp_back_to_form", help="Return to options"):
            st.session_state["cost.tabs_revealed"] = False
            st.session_state["cost.compare_breadcrumb"] = False
            st.rerun()
        st.markdown("")

    # ZIP warning banner (shown at top if ZIP missing)
    if not has_zip:
        st.warning("⚠️ **ZIP code required:** Enter your ZIP code above to calculate accurate regional costs.")
        st.markdown("")

    # // reason: Render interactive tabbed comparison section
    from products.concierge_hub.cost_planner_v2.ui_helpers import render_cp_panel, render_cp_tabs

    render_cp_tabs()

    st.markdown("<div class='cp-panels'>", unsafe_allow_html=True)

    # Render only available panels; each panel renders its own card
    if available.get("home"):
        def render_home_card():
            inhome_breakdown = _calculate_inhome_scenario(zip_code or "00000", debug_label="")
            st.session_state.comparison_inhome_breakdown = inhome_breakdown
            _render_care_card(
                breakdown=inhome_breakdown,
                care_type_display="In-Home Care",
                is_facility=False,
                card_key="inhome_main"
            )
        render_cp_panel("home", render_home_card)

    if available.get("al"):
        def render_al_card():
            al_breakdown = _calculate_facility_scenario("assisted_living", zip_code or "00000", debug_label="")
            st.session_state.comparison_facility_breakdown = al_breakdown
            _render_care_card(
                breakdown=al_breakdown,
                care_type_display="Assisted Living",
                is_facility=True,
                card_key="al_main"
            )
        render_cp_panel("al", render_al_card)

    if available.get("mc"):
        def render_mc_card():
            mc_breakdown = _calculate_facility_scenario("memory_care", zip_code or "00000", debug_label="")
            _render_care_card(
                breakdown=mc_breakdown,
                care_type_display="Memory Care",
                is_facility=True,
                card_key="mc_main"
            )
        render_cp_panel("mc", render_mc_card)

    st.markdown("</div>", unsafe_allow_html=True)

    # Plan selection and CTA
    st.markdown("---")

    # HOUSEHOLD DUAL COMPARISON (behind FEATURE_DUAL_COST_PLANNER flag)
    _render_household_dual_comparison_if_applicable(zip_code)

    _render_plan_selection_and_cta("assisted_living", show_both=True)


# ==============================================================================
# CALCULATION HELPERS
# ==============================================================================

def _log_calculation_inputs(label: str, zip_code: str, breakdown: ScenarioBreakdown):
    """Log calculation inputs and outputs for development consistency checks.
    
    Args:
        label: Descriptive label (e.g., "LEFT (In-Home)")
        zip_code: ZIP code used
        breakdown: The calculated scenario breakdown
    """
    from products.concierge_hub.cost_planner_v2.utils.regional_data import RegionalDataProvider

    regional = RegionalDataProvider.get_multiplier(zip_code=zip_code)

    st.write(f"### 📊 Calculation Summary: {label}")
    st.json({
        "scenario": breakdown.care_type,
        "region": regional.region_name,
        "region_multiplier": round(regional.multiplier, 2),
        "hours_per_day": st.session_state.get("comparison_hours_per_day", "N/A"),
        "home_carry_amount": st.session_state.get("comparison_home_carry_cost", 0),
        "keep_home": st.session_state.get("comparison_keep_home", False),
        "monthly_total": breakdown.monthly_total,
        "annual_total": breakdown.annual_total
    })
    st.write("---")


def _calculate_facility_scenario(care_type, zip_code, debug_label=""):
    """Calculate facility scenario with detailed step-by-step debug output."""
    if debug_label:
        st.write(f"### 🔍 DEBUG: {debug_label} - FACILITY Calculation")
        st.write("**Step 1: Inputs**")
        st.write(f"  - care_type: `{care_type}`")
        st.write(f"  - ZIP: `{zip_code}`")
        st.write(f"  - keep_home: `{st.session_state.get('comparison_keep_home', False)}`")
        st.write(f"  - home_carry: `${st.session_state.get('comparison_home_carry_cost', 0):,.0f}`")
        st.write("")

    result = comparison_calcs.calculate_facility_scenario(
        care_type=care_type,
        zip_code=zip_code,
        keep_home=st.session_state.get("comparison_keep_home", False),
        home_carry_override=st.session_state.get("comparison_home_carry_cost", 0) or None
    )

    if debug_label:
        st.write("**Step 2: Base Facility Rate Lookup**")
        from products.concierge_hub.cost_planner_v2.comparison_calcs import FACILITY_BASE_RATES
        base_rate = FACILITY_BASE_RATES.get(care_type, 4500)
        st.write(f"  - FACILITY_BASE_RATES lookup for `{care_type}`: **${base_rate:,.0f}**/month")
        if care_type not in FACILITY_BASE_RATES:
            st.write(f"  - ⚠️ `{care_type}` NOT in FACILITY_BASE_RATES dict, using default: $4,500")
        st.write("")

        st.write("**Step 3: Regional Adjustment**")
        from products.concierge_hub.cost_planner_v2.utils.regional_data import RegionalDataProvider
        regional = RegionalDataProvider.get_multiplier(zip_code=zip_code)
        multiplier = regional.multiplier
        region_label = regional.region_name
        base_after_regional = base_rate * multiplier
        st.write(f"  - Region: {region_label}")
        st.write(f"  - Regional multiplier: {multiplier:.2f}")
        st.write(f"  - Base × Regional: ${base_rate:,.0f} × {multiplier:.2f} = **${base_after_regional:,.0f}**")
        st.write("")

        st.write("**Step 4: Care Modifiers**")
        running_total = base_after_regional
        for line in result.lines:
            if line.label not in ['Base Cost', 'Regional Adjustment', 'Home Carry Cost'] and line.applied and line.value > 0:
                prev_total = running_total
                running_total += line.value
                st.write(f"  - {line.label}: +${line.value:,.0f}")
                st.write(f"    Running total: ${prev_total:,.0f} → **${running_total:,.0f}**")
        st.write("")

        home_carry = st.session_state.get('comparison_home_carry_cost', 0)
        if home_carry > 0 and st.session_state.get('comparison_keep_home', False):
            st.write("**Step 5: Home Carry Cost**")
            st.write(f"  - Home carry: +${home_carry:,.0f}")
            st.write(f"  - Running total: ${running_total:,.0f} → **${running_total + home_carry:,.0f}**")
            running_total += home_carry
            st.write("")

        st.write(f"**Final Monthly Total: ${result.monthly_total:,.0f}**")
        st.write("---")

    return result


def _calculate_inhome_scenario(zip_code, debug_label=""):
    """Calculate in-home scenario with detailed step-by-step debug output."""

    # Ensure comparison_hours_per_day is synced with slider
    if "comparison_hours_per_day" not in st.session_state:
        st.session_state.comparison_hours_per_day = st.session_state.get("comparison_inhome_hours", 8.0)
    elif st.session_state.comparison_hours_per_day != st.session_state.comparison_inhome_hours:
        # Sync if out of sync
        st.session_state.comparison_hours_per_day = st.session_state.comparison_inhome_hours

    if debug_label:
        st.write(f"### 🔍 DEBUG: {debug_label} - IN-HOME Calculation")
        st.write("**Step 1: Inputs**")
        st.write(f"  - ZIP: `{zip_code}`")
        st.write(f"  - hours_per_day: `{st.session_state.get('comparison_hours_per_day', 8)}`")
        st.write(f"  - home_carry: `${st.session_state.get('comparison_home_carry_cost', 0):,.0f}`")
        st.write("")

    result = comparison_calcs.calculate_inhome_scenario(
        zip_code=zip_code,
        hours_per_day=st.session_state.get("comparison_hours_per_day", 8),
        home_carry_override=st.session_state.get("comparison_home_carry_cost", 0) or None
    )

    if debug_label:
        st.write("**Step 2: Base Hourly Rate Calculation**")
        from products.concierge_hub.cost_planner_v2.comparison_calcs import INHOME_HOURLY_BASE
        from products.concierge_hub.cost_planner_v2.utils.regional_data import RegionalDataProvider
        regional = RegionalDataProvider.get_multiplier(zip_code=zip_code)
        multiplier = regional.multiplier
        region_label = regional.region_name
        hourly_rate = INHOME_HOURLY_BASE * multiplier
        st.write(f"  - Region: {region_label}")
        st.write(f"  - Regional multiplier: {multiplier:.2f}")
        st.write(f"  - Base hourly rate: ${INHOME_HOURLY_BASE:.2f}/hr")
        st.write(f"  - Regional hourly rate: ${INHOME_HOURLY_BASE:.2f} × {multiplier:.2f} = **${hourly_rate:.2f}/hr**")
        st.write("")

        st.write("**Step 3: Monthly Base Cost**")
        hours_per_day = st.session_state.get('comparison_hours_per_day', 8)
        hours_per_month = hours_per_day * 30
        base_cost = hourly_rate * hours_per_month
        st.write(f"  - Hours per day: {hours_per_day}")
        st.write(f"  - Hours per month: {hours_per_day} × 30 = {hours_per_month}")
        st.write(f"  - Base monthly cost: ${hourly_rate:.2f}/hr × {hours_per_month} hrs = **${base_cost:,.0f}**")
        st.write("")

        st.write("**Step 4: Care Modifiers**")
        running_total = base_cost
        for line in result.lines:
            if line.label not in ['Base Hourly Cost', 'Regional Adjustment', 'Home Carry Cost'] and line.applied and line.value > 0:
                prev_total = running_total
                running_total += line.value
                st.write(f"  - {line.label}: +${line.value:,.0f}")
                st.write(f"    Running total: ${prev_total:,.0f} → **${running_total:,.0f}**")
        st.write("")

        home_carry = st.session_state.get('comparison_home_carry_cost', 0)
        if home_carry > 0:
            st.write("**Step 5: Home Carry Cost**")
            st.write(f"  - Home carry (always included for in-home): +${home_carry:,.0f}")
            st.write(f"  - Running total: ${running_total:,.0f} → **${running_total + home_carry:,.0f}**")
            running_total += home_carry
            st.write("")

        st.write(f"**Final Monthly Total: ${result.monthly_total:,.0f}**")
        st.write("---")

    return result


# ==============================================================================
# RENDERING FUNCTIONS (DEPRECATED - kept for reference only)
# ==============================================================================
# Legacy two-column and single-path views removed in favor of tabbed shell above.
# All rendering now handled by render_comparison_view() → tabbed panels → _render_care_card().


def _extract_segments_from_breakdown(breakdown: ScenarioBreakdown, is_facility: bool) -> dict[str, float]:
    """Extract cost segments from breakdown for composition bar.
    
    Extracts 2-3 segments in fixed order:
    - In-Home: Care Services + Home Carry
    - Facility: Housing/Room + Care Services (+ Home Carry if present)
    
    Args:
        breakdown: ScenarioBreakdown object with line items
        is_facility: Whether this is facility care
        
    Returns:
        Dict mapping segment label to amount (only non-zero segments)
    """
    segments = {}

    if is_facility:
        # Facility: Housing/Room (base + regional) + Care Services (modifiers) + Home Carry (optional)
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

        if housing_amt > 0:
            segments["Housing/Room"] = housing_amt
        if care_amt > 0:
            segments["Care Services"] = care_amt
        if home_carry_amt > 0:
            segments["Home Carry"] = home_carry_amt

    else:
        # In-Home: Care Services (base + regional + modifiers) + Home Carry (always present)
        care_amt = 0.0
        home_carry_amt = 0.0

        for line in breakdown.lines:
            label_lower = line.label.lower()

            # Home carry is separate
            if "home carry" in label_lower:
                if line.applied:
                    home_carry_amt += line.value
            # Everything else is care services
            else:
                if line.applied and line.value > 0:
                    care_amt += line.value

        if care_amt > 0:
            segments["Care Services"] = care_amt
        if home_carry_amt > 0:
            segments["Home Carry"] = home_carry_amt

    return segments


def _get_assessment_key_from_breakdown(breakdown: ScenarioBreakdown, is_facility: bool) -> str:
    """Map breakdown to assessment key for caching.
    
    Args:
        breakdown: ScenarioBreakdown object
        is_facility: Whether this is facility care
        
    Returns:
        Assessment key ('home', 'al', or 'mc')
    """
    if not is_facility:
        return "home"

    care_type = breakdown.care_type
    if "memory_care" in care_type:
        return "mc"
    else:
        return "al"


def _render_care_card(
    breakdown: ScenarioBreakdown,
    care_type_display: str,
    is_facility: bool,
    card_key: str,
    is_recommended: bool = False
):
    """Render a single care scenario card with visual container.
    
    Args:
        breakdown: ScenarioBreakdown object
        care_type_display: Display name for care type
        is_facility: Whether this is facility care
        card_key: Unique key for widgets
        is_recommended: Whether this is the recommended plan (adds visual accent)
    """
    from products.concierge_hub.cost_planner_v2.ui_helpers import (
        donut_cost_chart,
        money,
        render_care_chunk_compare_blurb,
        segcache_get,
        segcache_set,
        totals_set,
    )

    # Extract segments from breakdown for visualization (no new math)
    segments = _extract_segments_from_breakdown(breakdown, is_facility)

    # Determine assessment key for caching
    assessment_key = _get_assessment_key_from_breakdown(breakdown, is_facility)

    # Cache segments and total using helpers
    segcache_set(assessment_key, segments)
    monthly_total = breakdown.monthly_total
    totals_set(assessment_key, monthly_total)
    print(f"[CARD] rendered {assessment_key} monthly={monthly_total:,.0f}")
    print(f"[COMPOSE] {assessment_key} segs={segcache_get(assessment_key)} total={monthly_total:,.0f}")

    # Minimal card structure (clean base design)
    card_classes = "cost-card"
    if is_recommended:
        card_classes += " cost-card--recommended"

    st.markdown(f'<div class="{card_classes}">', unsafe_allow_html=True)

    # Header
    st.markdown(f"<div class='cost-card__title'>{care_type_display}</div>", unsafe_allow_html=True)
    st.markdown("<div class='cost-card__caption'>Estimated monthly total</div>", unsafe_allow_html=True)

    # Totals display removed - now shown in donut center

    # Donut chart (replaces bar + shows total in center)
    donut_cost_chart(segments, total_label=money(monthly_total), emphasize="Care Services")

    # Care chunk comparison (when both cached)
    render_care_chunk_compare_blurb(assessment_key)

    # Controls
    if is_facility:
        _render_facility_controls(card_key)
        st.caption("Costs vary by community and level of care.")
    else:
        _render_inhome_controls(card_key)
        st.caption("Actual costs vary by caregiver rates and location.")

    st.markdown('</div>', unsafe_allow_html=True)


def _render_facility_controls(card_key: str):
    """Render facility-specific controls (keep home toggle).
    
    Args:
        card_key: Unique key for widgets
    """
    # Minimal "Keep Home" section (presentation only)
    from products.concierge_hub.cost_planner_v2.ui_helpers import render_cp_hint
    st.markdown("<div class='cost-section__label'>� Keep Home?</div>", unsafe_allow_html=True)

    keep_home = st.checkbox(
        "Keep Home (spouse/partner remains)",
        value=st.session_state.comparison_keep_home,
        key=f"{card_key}_keep_home",
        help="Check if you need to maintain your current home while in facility care"
    )

    # Inline chip when included
    if keep_home:
        current_carry = st.session_state.comparison_home_carry_cost
        st.markdown(f"<span class='cp-chip'>✓ Added to total (${current_carry:,.0f}/mo)</span>", unsafe_allow_html=True)

    if keep_home != st.session_state.comparison_keep_home:
        st.session_state.comparison_keep_home = keep_home
        st.rerun()

    if keep_home:
        prefill_value = st.session_state.comparison_home_carry_cost
        st.markdown("<div class='cp-homecarry'>", unsafe_allow_html=True)
        home_carry = st.number_input(
            "Monthly home expense",
            min_value=0.0,
            value=prefill_value,
            step=100.0,
            help="Mortgage, rent, property tax, insurance, maintenance",
            key=f"{card_key}_home_carry",
            label_visibility="visible"
        )

        if home_carry != st.session_state.comparison_home_carry_cost:
            st.session_state.comparison_home_carry_cost = home_carry
            st.rerun()

        render_cp_hint("ZIP-based estimate — adjust to your actual monthly amount.")
        st.markdown(f"<span class='cp-chip'>✓ Added to total (${home_carry:,.0f}/mo)</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        pass


def _render_inhome_controls(card_key: str):
    """Render in-home-specific controls (hours per day, home carry).
    
    Args:
        card_key: Unique key for widgets
    """
    from products.concierge_hub.cost_planner_v2.ui_helpers import render_cp_hint

    # Care Hours (minimal)
    current_hours = st.session_state.comparison_inhome_hours
    st.markdown("<div class='cost-section__label'>Daily Support Hours</div>", unsafe_allow_html=True)
    hours = st.slider(
        "Hours per day",
        min_value=1.0,
        max_value=24.0,
        value=current_hours,
        step=1.0,
        key=f"{card_key}_hours",
        help="Adjust based on care needs"
    )
    # Numeric value beside slider (simple line)
    st.markdown(f"<div class='cp-hint'>{hours:.1f} h/day</div>", unsafe_allow_html=True)
    render_cp_hint("Adjust hours to see how in-home costs change.")

    # Home Expense (minimal)
    st.markdown("<div class='cost-section__label'>🏠 Home Expense</div>", unsafe_allow_html=True)

    # Try ZIP-based prefill if available and home carry cost not yet set
    prefill_value = st.session_state.comparison_home_carry_cost
    prefill_caption = None

    # Prefill logic omitted in clean base design (presentation only)

    st.markdown("<div class='cp-homecarry'>", unsafe_allow_html=True)
    home_carry = st.number_input(
        "Monthly home expense",
        min_value=0.0,
        value=prefill_value,
        step=100.0,
        help="Mortgage, rent, property tax, insurance, maintenance",
        key=f"{card_key}_home_carry",
        label_visibility="visible"
    )

    if home_carry != st.session_state.comparison_home_carry_cost:
        st.session_state.comparison_home_carry_cost = home_carry
        st.rerun()

    if prefill_caption:
        render_cp_hint(prefill_caption)
    render_cp_hint("ZIP-based estimate — adjust to your actual monthly amount.")
    st.markdown(f"<span class='cp-chip'>✓ Included in total (${home_carry:,.0f}/mo)</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_48_hour_hint_if_applicable():
    """Render 48-hour hint when higher support flags are present."""
    from core.flags import get_all_flags

    # Check for higher support flags
    flags = get_all_flags()
    higher_support_flags = [
        "moderate_dependence", "high_dependence", "moderate_cognitive_decline",
        "severe_cognitive_risk", "falls_multiple", "medication_management",
        "chronic_present", "behavioral_concerns"
    ]

    has_higher_support = any(flags.get(flag, False) for flag in higher_support_flags)

    if has_higher_support:
        from products.concierge_hub.cost_planner_v2.ui_helpers import render_cp_hint
        render_cp_hint("💡 Based on your answers, many families need close to 48 hours/week of paid help to stay safely at home. Actual needs vary—adjust hours to see the impact.")


def _render_cost_breakdown(breakdown: ScenarioBreakdown):
    """Render detailed cost breakdown.
    
    Args:
        breakdown: ScenarioBreakdown object
    """

    for line in breakdown.lines:
        # Presentation-only: hide any explicit Home Carry line from this section
        if str(line.label).strip().lower() in {"home carry", "home carry cost", "home expense"}:
            continue
        if line.applied:
            st.markdown(f"**{line.label}:** ${line.value:,.0f}")
        else:
            st.markdown(f"**{line.label}:** ${line.value:,.0f} *(not included)*")

    st.markdown("---")
    st.markdown(f"**Monthly Total:** ${breakdown.monthly_total:,.0f}")


def _calculate_support_intensity() -> int:
    """Calculate support intensity score from care flags.
    
    Returns:
        Support intensity score (0-5)
    """
    from core.flags import get_all_flags

    flags = get_all_flags()
    score = 0

    # Add +1 for each present, cap total at 5
    intensity_flags = [
        "moderate_dependence",
        "mobility_limited",
        "moderate_cognitive_decline",
        "chronic_present"
    ]

    for flag in intensity_flags:
        if flags.get(flag, False):
            score += 1

    # Add +1 for falls_risk OR medication_management (max +1 for "extras")
    if flags.get("falls_risk", False) or flags.get("medication_management", False):
        score += 1

    return min(score, 5)


def _get_cost_threshold(intensity_score: int) -> float:
    """Map intensity score to cost threshold.
    
    Args:
        intensity_score: Support intensity score (0-5)
        
    Returns:
        Monthly cost threshold in dollars
    """
    if intensity_score <= 1:
        return 7000.0
    elif intensity_score <= 3:
        return 7500.0
    else:  # 4-5
        return 8000.0


def _render_cost_threshold_advisory(inhome_estimate: float, person_label: str = ""):
    """Render cost threshold advisory message.
    
    Args:
        inhome_estimate: Monthly in-home cost estimate
        person_label: Label for person (e.g., "Primary", "Partner") for dual mode
    """
    intensity = _calculate_support_intensity()
    threshold = _get_cost_threshold(intensity)
    threshold_crossed = inhome_estimate >= threshold

    person_prefix = f"**{person_label}:** " if person_label else ""

    from products.concierge_hub.cost_planner_v2.ui_helpers import render_cp_hint
    if threshold_crossed:
        render_cp_hint(f"{person_prefix}In-home care is feasible, but based on the level of help you'll likely need, the monthly cost (~${inhome_estimate:,.0f}/mo) approaches or exceeds what families often pay for Assisted Living. Consider touring Assisted Living communities as a more predictable alternative.")
    else:
        render_cp_hint(f"{person_prefix}In-home care appears workable at ~${inhome_estimate:,.0f}/mo. Adjust weekly hours to see how costs change.")


def _render_household_dual_comparison_if_applicable(zip_code: str):
    """Render compact household dual comparison if both CarePlans exist.
    
    Gated by FEATURE_DUAL_COST_PLANNER flag (default: shadow).
    Shows: Primary | Partner | Household Total | 50/50 Split
    
    Args:
        zip_code: ZIP code for cost calculations
    """
    import os

    # Check feature flag
    try:
        flag_value = st.secrets.get("FEATURE_DUAL_COST_PLANNER", "shadow")
    except Exception:
        flag_value = os.getenv("FEATURE_DUAL_COST_PLANNER", "shadow")

    if str(flag_value).lower() not in {"on", "shadow"}:
        return

    # Check if dual mode is enabled
    dual_mode = st.session_state.get("cost.dual_mode", False)
    if not dual_mode:
        return

    # Get household data
    try:
        from products.concierge_hub.cost_planner_v2.household import compute_household_total
        result = compute_household_total(st)

        if not result.get("has_partner_plan"):
            # Show inline note if partner is expected but missing
            has_partner = st.session_state.get("has_partner", False)
            if has_partner:
                st.info("👥 **Add partner assessment** to see combined household costs.")
            return

        # Render compact dual comparison
        st.markdown("---")
        st.markdown("### 👥 Household Cost Summary")

        # Display in compact columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Primary Monthly", f"${result['primary_total']:,.0f}")

        with col2:
            st.metric("Partner Monthly", f"${result['partner_total']:,.0f}")

        with col3:
            st.metric("Household Total", f"${result['household_total']:,.0f}")

        with col4:
            st.metric("50/50 Split", f"${result['split']['primary']:,.0f} each")

        # Keep-home toggle affects home_carry
        if result.get("home_carry", 0) > 0:
            st.caption(f"💡 Includes ${result['home_carry']:,.0f}/mo home carry cost")

        # Per-person advisories (only for in-home scenarios)
        primary_tier = result.get("primary_tier", "")
        partner_tier = result.get("partner_tier", "")

        if primary_tier == "in_home_care" or partner_tier == "in_home_care":
            st.markdown("**Cost Analysis:**")

            if primary_tier == "in_home_care":
                _render_cost_threshold_advisory(result['primary_total'], "Primary")

            if partner_tier == "in_home_care":
                _render_cost_threshold_advisory(result['partner_total'], "Partner")

        # Shadow mode logging
        if str(flag_value).lower() == "shadow":
            print(f"[DUAL_COST_SHADOW] household={result['household_total']:.0f} primary={result['primary_total']:.0f} partner={result['partner_total']:.0f}")

    except Exception as e:
        # Never fail the UI
        print(f"[DUAL_COST_ERROR] {e}")
        pass


def _render_plan_selection_and_cta(recommended_tier: str, show_both: bool):
    """Render plan selection radio buttons and primary CTA.
    
    Args:
        recommended_tier: The recommended care tier
        show_both: Whether both plans are shown
    """

    st.markdown("### Choose Your Path Forward")

    # // reason: Radio mirrors available tabs and syncs with cost.selected_assessment
    available = st.session_state.get("cost.assessments_available", {"home": True, "al": True, "mc": False})
    sel = st.session_state.get("cost.selected_assessment", "home")

    # Build choices from available assessments
    choices = []
    labels_map = {"home": "In-Home Care", "al": "Assisted Living", "mc": "Memory Care"}
    if available.get("home"):
        choices.append("home")
    if available.get("al"):
        choices.append("al")
    if available.get("mc"):
        choices.append("mc")

    # Radio that mirrors tab selection
    current_index = choices.index(sel) if sel in choices else 0
    new_sel = st.radio(
        "Which scenario would you like to explore in detail?",
        options=choices,
        format_func=lambda k: labels_map.get(k, k),
        index=current_index,
        key="comparison_plan_radio",
        horizontal=True,
        label_visibility="collapsed"
    )

    # Sync selection if changed
    if new_sel != sel:
        st.session_state["cost.selected_assessment"] = new_sel
        st.rerun()

    # Map to plan key for handoff to FA
    plan_key_map = {
        "home": "inhome_in_home_care",
        "al": "facility_assisted_living",
        "mc": "facility_memory_care"
    }
    st.session_state.comparison_selected_plan = plan_key_map.get(new_sel, "inhome_in_home_care")

    st.markdown("")

    # Primary CTA
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown('<div data-role="primary">', unsafe_allow_html=True)
        if st.button(
            "Help Me Figure Out How to Pay for This ▶",
            type="primary",
            use_container_width=True,
            key="comparison_continue"
        ):
            # Determine which breakdown to use based on selection
            selected_plan_key = st.session_state.comparison_selected_plan

            if selected_plan_key.startswith("facility_"):
                selected_breakdown = st.session_state.comparison_facility_breakdown
                is_facility = True
            else:  # inhome_*
                selected_breakdown = st.session_state.comparison_inhome_breakdown
                is_facility = False

            # For FACILITY care: exclude home carry (it's optional, user choice to keep home)
            # For IN-HOME care: include home carry (it's inherent to the scenario)
            care_cost_monthly = selected_breakdown.monthly_total
            home_carry_monthly = 0.0

            if is_facility:
                # Subtract home carry if present (for facility care only)
                for line in selected_breakdown.lines:
                    if line.label == "Home Carry Cost" and line.applied:
                        home_carry_monthly = line.value
                        care_cost_monthly -= line.value
                        break

            # Store in expected format for expert_review.py
            st.session_state.cost_v2_quick_estimate = {
                "estimate": {
                    "monthly_adjusted": care_cost_monthly,
                    "monthly_total": selected_breakdown.monthly_total,
                    "care_type": selected_breakdown.care_type,
                    "selected_plan": selected_plan_key,
                }
            }

            # Navigate to financial assessment
            if "step" in st.query_params:
                del st.query_params["step"]

            st.session_state.cost_v2_step = "auth"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button("💾 Save Both", use_container_width=True, key="save_both"):
            st.info("💡 Sign in to save scenarios (Phase 3)")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button("← Back to Hub", use_container_width=True, key="comparison_back"):
            user_id = st.session_state.get("user_id", "unknown")
            print(f"[CTA_NAV] action=back_to_hub dest=hub_concierge uid={user_id}")
            route_to("hub_concierge")
        st.markdown("</div>", unsafe_allow_html=True)
