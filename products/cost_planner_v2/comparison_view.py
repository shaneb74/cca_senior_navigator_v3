"""
Cost Planner v2 - Comparison View (Phase 2)

Side-by-side comparison of Recommended Plan vs In-Home Care.
Uses care-type-specific modifiers and real calculations.
"""

import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from products.cost_planner_v2 import comparison_calcs
from products.cost_planner_v2.comparison_calcs import ScenarioBreakdown

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
# MAIN ENTRY POINT
# ==============================================================================

def render_comparison_view(zip_code: str | None):
    """
    Render comparison view with side-by-side cost breakdowns.
    
    Shows facility (left) vs in-home (right) based on GCP recommendation.
    Includes interactive sliders for home carry cost and in-home hours.
    
    ZIP gating: Layout always renders (controlled by view_mode).
    If ZIP missing, show placeholder cards with warning banner.
    
    Args:
        zip_code: ZIP code for regional pricing (None if not provided yet)
    """
    
    # Check if ZIP is present for compute gating
    has_zip = bool(zip_code and len(str(zip_code)) == 5)
    
    # Render Navi header at top of comparison view
    try:
        from products.gcp_v4.ui_helpers import render_navi_header_message
        # Set header title/subtitle for Cost Planner context
        if "gcp_step_title" not in st.session_state:
            st.session_state["gcp_step_title"] = "Your Cost Estimate"
        if "gcp_step_subtitle" not in st.session_state:
            compare_mode = st.session_state.get("cost.compare_inhome", False)
            if compare_mode:
                st.session_state["gcp_step_subtitle"] = "Compare your options side by side"
            else:
                st.session_state["gcp_step_subtitle"] = "Here's what your recommended plan will cost"
        
        render_navi_header_message()
        
        # Log header render
        gcp_rec = MCIP.get_care_recommendation()
        rec_tier = gcp_rec.tier if gcp_rec and gcp_rec.tier else "assisted_living"
        compare_mode = st.session_state.get("cost.compare_inhome", False)
        print(f"[NAVI_HEADER] rendered step=estimate compare={compare_mode} tier={rec_tier}")
    except Exception as e:
        print(f"[NAVI_HEADER] error rendering: {e}")
        pass

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

    # DEBUG: GCP hours initialization (commented out for production)
    # gcp_data = st.session_state.get("gcp_care_recommendation", {})
    # gcp_hours_category = gcp_data.get("hours_per_day", "not_found")
    # st.write("### 🔍 GCP Hours Debug")
    # st.json({
    #     "gcp_hours_category": gcp_hours_category,
    #     "mapped_initial_hours": st.session_state.get("comparison_hours_gcp_source", "N/A"),
    #     "slider_value_current": st.session_state.comparison_inhome_hours,
    #     "is_24_hour": st.session_state.comparison_inhome_hours == 24.0
    # })
    # st.write("---")

    # Get GCP recommendation
    gcp_rec = MCIP.get_care_recommendation()

    # Determine what to show
    recommended_tier = "assisted_living"  # Default fallback

    if gcp_rec and gcp_rec.tier:
        recommended_tier = gcp_rec.tier

        # NORMALIZE: GCP might return "in_home" but we need "in_home_care"
        if recommended_tier == "in_home":
            recommended_tier = "in_home_care"

    # DEBUG: GCP recommendation (commented out for production)
    # st.write("🔍 **GCP RECOMMENDATION DEBUG:**")
    # st.write(f"  - Raw tier value from GCP: `{gcp_rec.tier if gcp_rec else 'None'}`")
    # st.write(f"  - Normalized tier: `{recommended_tier}`")
    # st.write(f"  - Will use IN-HOME calc: {recommended_tier == 'in_home_care'}")
    # st.write(f"  - Will use FACILITY calc: {recommended_tier != 'in_home_care'}")
    # st.markdown("---")

    # Check if user wants to see comparison (using cost.view_mode as single source of truth)
    view_mode = st.session_state.get("cost.view_mode", "single")
    single_path_tier = st.session_state.get("cost.single_path_tier")  # Explicit single-path tier
    
    # Mirror to compare_inhome for backward compatibility
    compare_inhome = (view_mode == "compare")
    st.session_state["cost.compare_inhome"] = compare_inhome

    # Determine show_both based on view_mode (single source of truth)
    if view_mode == "compare":
        # User explicitly chose compare mode
        show_both = True
        # Clear single-path tier if set
        if single_path_tier:
            st.session_state.pop("cost.single_path_tier", None)
            single_path_tier = None
    elif single_path_tier:
        # Explicit single-path mode (from Continue CTA)
        show_both = False
        recommended_tier = single_path_tier  # Use explicitly set tier
    else:
        # Default behavior for single mode
        show_both = False
    
    # Enhanced logging for view mode decision
    if view_mode == "single":
        print(f"[COST_VIEW] mode=single tier={recommended_tier} view_mode={view_mode} "
              f"single_path_tier={single_path_tier or 'None'} show_both={show_both}")
    else:
        print(f"[COST_VIEW] mode=comparison tier={recommended_tier} view_mode={view_mode} "
              f"single_path_tier={single_path_tier or 'None'} show_both={show_both}")
    
    # Detailed render state logging
    print(f"[COST_RENDER] view_mode={view_mode} zip_present={has_zip} show_both={show_both} "
          f"will_render={'two_cards' if show_both else 'single_card'}")

    # Header (mode-aware)
    if show_both:
        st.markdown("### Compare your recommended plan with staying at home")
        st.markdown(
            """<div style="color: var(--text-secondary); margin-bottom: 2rem; font-size: 0.95rem;">
            <strong>💬 Navi says:</strong> These numbers can be eye-opening. 
            Let's look at each option and figure out how to pay for it.
            </div>""",
            unsafe_allow_html=True
        )
    else:
        # Single-path view header
        care_type_display_map = {
            "assisted_living": "Assisted Living",
            "memory_care": "Memory Care",
            "memory_care_high_acuity": "Memory Care (High Acuity)",
            "in_home_care": "In-Home Care",
        }
        tier_display = care_type_display_map.get(recommended_tier, recommended_tier.replace("_", " ").title())
        st.markdown(f"### Your {tier_display} Cost Estimate")
        st.markdown(
            """<div style="color: var(--text-secondary); margin-bottom: 2rem; font-size: 0.95rem;">
            <strong>💬 Navi says:</strong> Here's what your recommended plan will cost each month.
            </div>""",
            unsafe_allow_html=True
        )

    st.markdown("---")
    
    # ZIP warning banner (shown at top if ZIP missing)
    if not has_zip:
        st.warning("⚠️ **ZIP code required:** Enter your ZIP code above to calculate accurate regional costs.")
        st.markdown("")

    # Calculate and render scenarios based on recommendation
    # Note: If ZIP missing, calculations use national baseline (no regional adjustment)
    # Cards still render to show structure; user sees warning banner above
    
    if recommended_tier == "in_home_care":
        # In-home is recommended
        inhome_breakdown = _calculate_inhome_scenario(zip_code or "00000", debug_label="")  # Use placeholder if ZIP missing
        st.session_state.comparison_inhome_breakdown = inhome_breakdown  # Store for handoff

        if show_both:
            # User wants to see AL comparison
            al_breakdown = _calculate_facility_scenario("assisted_living", zip_code or "00000", debug_label="")
            st.session_state.comparison_facility_breakdown = al_breakdown  # Store for handoff

            _render_two_column_comparison_inhome_primary(
                inhome_breakdown,
                al_breakdown,
                recommended_tier
            )
        else:
            # In-home only
            _render_inhome_primary_view(inhome_breakdown)
    else:
        # Facility is recommended (AL, MC, MC-HA)
        facility_breakdown = _calculate_facility_scenario(recommended_tier, zip_code or "00000", debug_label="")
        st.session_state.comparison_facility_breakdown = facility_breakdown  # Store for handoff

        if show_both:
            # Show facility + in-home comparison
            inhome_breakdown = _calculate_inhome_scenario(zip_code or "00000", debug_label="")
            st.session_state.comparison_inhome_breakdown = inhome_breakdown  # Store for handoff

            _render_two_column_comparison_facility_primary(
                facility_breakdown,
                inhome_breakdown,
                recommended_tier
            )
        else:
            # Facility only
            # _log_calculation_inputs("Facility (Single)", zip_code, facility_breakdown)
            _render_facility_primary_view(facility_breakdown, recommended_tier)

    # Plan selection and CTA
    st.markdown("---")
    
    # HOUSEHOLD DUAL COMPARISON (behind FEATURE_DUAL_COST_PLANNER flag)
    _render_household_dual_comparison_if_applicable(zip_code)
    
    _render_plan_selection_and_cta(recommended_tier, show_both)


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
    from products.cost_planner_v2.utils.regional_data import RegionalDataProvider

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
        from products.cost_planner_v2.comparison_calcs import FACILITY_BASE_RATES
        base_rate = FACILITY_BASE_RATES.get(care_type, 4500)
        st.write(f"  - FACILITY_BASE_RATES lookup for `{care_type}`: **${base_rate:,.0f}**/month")
        if care_type not in FACILITY_BASE_RATES:
            st.write(f"  - ⚠️ `{care_type}` NOT in FACILITY_BASE_RATES dict, using default: $4,500")
        st.write("")

        st.write("**Step 3: Regional Adjustment**")
        from products.cost_planner_v2.utils.regional_data import RegionalDataProvider
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
        from products.cost_planner_v2.comparison_calcs import INHOME_HOURLY_BASE
        from products.cost_planner_v2.utils.regional_data import RegionalDataProvider
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
# RENDERING FUNCTIONS
# ==============================================================================

def _render_two_column_comparison_facility_primary(
    facility_breakdown: ScenarioBreakdown,
    inhome_breakdown: ScenarioBreakdown,
    recommended_tier: str
):
    """Render side-by-side comparison with facility as recommended.
    
    Args:
        facility_breakdown: Facility care breakdown
        inhome_breakdown: In-home care breakdown
        recommended_tier: The recommended care tier
    """

    # Care type display names
    care_type_display_map = {
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)",
    }

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"#### 🏥 Your Recommended Plan: {care_type_display_map.get(recommended_tier, 'Facility Care')}")
        _render_care_card(
            breakdown=facility_breakdown,
            care_type_display=care_type_display_map.get(recommended_tier, "Facility Care"),
            is_facility=True,
            card_key="facility",
            is_recommended=True
        )

    with col2:
        st.markdown("#### 🏠 Compare: In-Home Care")
        _render_care_card(
            breakdown=inhome_breakdown,
            care_type_display="In-Home Care",
            is_facility=False,
            card_key="inhome",
            is_recommended=False
        )


def _render_two_column_comparison_inhome_primary(
    inhome_breakdown: ScenarioBreakdown,
    al_breakdown: ScenarioBreakdown,
    recommended_tier: str
):
    """Render side-by-side comparison with in-home as recommended.
    
    Args:
        inhome_breakdown: In-home care breakdown (recommended)
        al_breakdown: Assisted Living breakdown (comparison)
        recommended_tier: Should be "in_home_care"
    """

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🏠 Your Recommended Plan: In-Home Care")
        _render_care_card(
            breakdown=inhome_breakdown,
            care_type_display="In-Home Care",
            is_facility=False,
            card_key="inhome_recommended",
            is_recommended=True
        )

    with col2:
        st.markdown("#### 🏥 Compare: Assisted Living")
        _render_care_card(
            breakdown=al_breakdown,
            care_type_display="Assisted Living",
            is_facility=True,
            card_key="al_comparison",
            is_recommended=False
        )


def _render_facility_primary_view(
    facility_breakdown: ScenarioBreakdown,
    recommended_tier: str
):
    """Render facility care as primary view (no comparison).
    
    Args:
        facility_breakdown: Facility care breakdown
        recommended_tier: The recommended care tier
    """

    care_type_display_map = {
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)",
    }

    st.markdown(f"#### 🏥 Your Recommended Plan: {care_type_display_map.get(recommended_tier, 'Facility Care')}")
    _render_care_card(
        breakdown=facility_breakdown,
        care_type_display=care_type_display_map.get(recommended_tier, "Facility Care"),
        is_facility=True,
        card_key="facility_primary"
    )

    st.markdown("---")

    # Show in-home comparison toggle button
    if st.button("📊 Compare with In-Home Care", use_container_width=True, type="secondary"):
        st.session_state["cost.view_mode"] = "compare"
        # Clear single-path tier to enable comparison
        if "cost.single_path_tier" in st.session_state:
            del st.session_state["cost.single_path_tier"]
        print(f"[COST_VIEW] toggle to comparison from single tier={recommended_tier}")
        st.rerun()


def _render_inhome_primary_view(inhome_breakdown: ScenarioBreakdown):
    """Render in-home care as primary view (no comparison).
    
    Args:
        inhome_breakdown: In-home care breakdown
    """

    st.markdown("#### 🏠 Your Recommended Plan: In-Home Care")
    _render_care_card(
        breakdown=inhome_breakdown,
        care_type_display="In-Home Care",
        is_facility=False,
        card_key="inhome_primary"
    )

    st.markdown("---")

    # Show facility comparison toggle button
    if st.button("📊 Compare with Assisted Living", use_container_width=True, type="secondary"):
        st.session_state["cost.view_mode"] = "compare"
        # Clear single-path tier to enable comparison
        if "cost.single_path_tier" in st.session_state:
            del st.session_state["cost.single_path_tier"]
        print(f"[COST_VIEW] toggle to comparison from single tier=in_home_care")
        st.rerun()


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

    # Determine CSS classes
    card_classes = "cost-card"
    if is_recommended:
        card_classes += " cost-card--recommended"

    # Open card container
    st.markdown(f'<div class="{card_classes}">', unsafe_allow_html=True)

    # Location section
    st.markdown("**📍 Location**")
    st.markdown(f"{breakdown.location_label}")

    st.markdown("")

    # Main totals (before interactive controls)
    base_monthly = breakdown.monthly_total

    st.markdown("**💰 Care Costs**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Monthly", f"${base_monthly:,.0f}")
    with col2:
        st.metric("Annual", f"${breakdown.annual_total:,.0f}")

    st.markdown("")

    # Cost breakdown
    with st.expander("📋 Cost Breakdown", expanded=False):
        _render_cost_breakdown(breakdown)

    st.markdown("")

    # Cost threshold advisory (for in-home scenarios only)
    if not is_facility and breakdown.care_type == "in_home_care":
        _render_cost_threshold_advisory(breakdown.monthly_total)
        st.markdown("")

    # Interactive controls for home carry and hours
    if is_facility:
        _render_facility_controls(card_key)
    else:
        _render_inhome_controls(card_key)

    st.markdown("")

    # Notes section (scenario-specific)
    with st.expander("📝 Notes", expanded=False):
        if is_facility:
            st.markdown("""
            **What's Included:**
            - Private or semi-private room
            - Three meals daily plus snacks
            - Basic assistance with daily activities
            - Housekeeping and laundry services
            - Scheduled activities and transportation
            
            **Additional Costs:**
            - Level-of-care adjustments for higher needs
            - Medication management
            - Specialized memory care services
            - Medicare does not cover long-term residential care
            """)
        else:
            st.markdown("""
            **What's Included:**
            - Professional caregiver services
            - Assistance with daily activities (ADLs)
            - Medication reminders
            - Light housekeeping and meal preparation
            - Companionship and supervision
            
            **Considerations:**
            - Care hours vary based on need level (2-24 hrs/day)
            - May need home modifications (grab bars, ramps, etc.)
            - Respite care options available
            - Some services may be covered by Medicare/Medicaid (check eligibility)
            """)

    # Close card container
    st.markdown('</div>', unsafe_allow_html=True)


def _render_facility_controls(card_key: str):
    """Render facility-specific controls (keep home toggle).
    
    Args:
        card_key: Unique key for widgets
    """
    from products.cost_planner_v2.utils.home_costs import lookup_zip

    st.markdown("**🏡 Home Costs**")

    keep_home = st.checkbox(
        "Keep Home (spouse/partner remains)",
        value=st.session_state.comparison_keep_home,
        key=f"{card_key}_keep_home",
        help="Check if you need to maintain your current home while in facility care"
    )

    if keep_home != st.session_state.comparison_keep_home:
        st.session_state.comparison_keep_home = keep_home
        st.rerun()

    if keep_home:
        # Try ZIP-based prefill if available and home carry cost not yet set
        prefill_value = st.session_state.comparison_home_carry_cost
        prefill_caption = None
        
        if prefill_value == 0.0:  # Only prefill if not already set
            zip_code = st.session_state.get("cost_v2_zip")
            if zip_code:
                lookup_result = lookup_zip(zip_code, kind="owner")
                if lookup_result:
                    prefill_value = lookup_result["amount"]
                    confidence_pct = int(lookup_result["confidence"] * 100)
                    prefill_caption = f"💡 Prefilled from {lookup_result['source']} · {confidence_pct}% confidence"
                    print(f"[HOME_COST_PREFILL] zip={zip_code} amount=${prefill_value:,.0f} conf={lookup_result['confidence']:.1%}")
        
        home_carry = st.number_input(
            "Monthly home expense",
            min_value=0.0,
            value=prefill_value,
            step=100.0,
            help="Mortgage, rent, property tax, insurance, maintenance",
            key=f"{card_key}_home_carry"
        )

        if home_carry != st.session_state.comparison_home_carry_cost:
            st.session_state.comparison_home_carry_cost = home_carry
            st.rerun()

        if prefill_caption:
            st.caption(prefill_caption)
        st.caption(f"✓ Added to total (${home_carry:,.0f}/mo)")
    else:
        st.caption("Home expenses not included")


def _render_inhome_controls(card_key: str):
    """Render in-home-specific controls (hours per day, home carry).
    
    Args:
        card_key: Unique key for widgets
    """
    from products.cost_planner_v2.utils.home_costs import lookup_zip

    # Check if hours should be shown (only for in_home tier OR when compare_inhome is enabled)
    gcp_rec = MCIP.get_care_recommendation()
    rec_tier = gcp_rec.tier if gcp_rec and gcp_rec.tier else "assisted_living"
    
    # Normalize tier name
    if rec_tier == "in_home":
        rec_tier = "in_home_care"
        
    compare_inhome = st.session_state.get("cost.compare_inhome", False)
    show_hours = (rec_tier == "in_home_care") or compare_inhome
    
    if show_hours:
        st.markdown("**⏰ Care Hours**")

        # Check if 24-hour care (lock slider)
        is_24_hour = st.session_state.comparison_inhome_hours == 24.0

        if is_24_hour:
            # Show locked 24-hour display
            st.info("🔒 **24-hour support** (as recommended in your care plan)")
            st.caption("This setting cannot be adjusted - 24-hour care is required based on your assessment.")
        else:
            # Editable slider
            hours = st.slider(
                "Hours per day",
                min_value=1.0,
                max_value=24.0,
                value=st.session_state.comparison_inhome_hours,
                step=1.0,
                key=f"{card_key}_hours",
                help="Adjust based on care needs (from your Guided Care Plan recommendation)"
            )

            if hours != st.session_state.comparison_inhome_hours:
                st.session_state.comparison_inhome_hours = hours
                st.session_state.comparison_hours_per_day = hours  # Keep synced
                st.rerun()

        st.markdown("")
        
        # Add 48-hour hint for higher support needs (only in in-home context)
        _render_48_hour_hint_if_applicable()
        
    else:
        # Hours not shown - add CTA for facility tiers
        if rec_tier in ["assisted_living", "memory_care", "memory_care_high_acuity"]:
            st.markdown("**⏰ Care Hours**")
            st.info("💡 Hours of care are included in your facility recommendation.")
            st.caption("Assisted Living and Memory Care provide 24/7 staff availability as needed.")
            
            if st.button("Compare with staying home", key=f"{card_key}_compare_cta", use_container_width=True):
                st.session_state["cost.compare_inhome"] = True
                st.rerun()
            st.markdown("")

    st.markdown("**🏡 Home Costs**")

    # Try ZIP-based prefill if available and home carry cost not yet set
    prefill_value = st.session_state.comparison_home_carry_cost
    prefill_caption = None
    
    if prefill_value == 0.0:  # Only prefill if not already set
        zip_code = st.session_state.get("cost_v2_zip")
        if zip_code:
            lookup_result = lookup_zip(zip_code, kind="owner")
            if lookup_result:
                prefill_value = lookup_result["amount"]
                confidence_pct = int(lookup_result["confidence"] * 100)
                prefill_caption = f"💡 Prefilled from {lookup_result['source']} · {confidence_pct}% confidence"
                print(f"[HOME_COST_PREFILL] zip={zip_code} amount=${prefill_value:,.0f} conf={lookup_result['confidence']:.1%}")
    
    home_carry = st.number_input(
        "Monthly home expense",
        min_value=0.0,
        value=prefill_value,
        step=100.0,
        help="Mortgage, rent, property tax, insurance, maintenance",
        key=f"{card_key}_home_carry"
    )

    if home_carry != st.session_state.comparison_home_carry_cost:
        st.session_state.comparison_home_carry_cost = home_carry
        st.rerun()

    if prefill_caption:
        st.caption(prefill_caption)
    st.caption(f"✓ Always included (${home_carry:,.0f}/mo)")


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
        st.caption("💡 Based on your answers, many families need close to 48 hours/week of paid help to stay safely at home. Actual needs vary—adjust hours to see the impact.")


def _render_cost_breakdown(breakdown: ScenarioBreakdown):
    """Render detailed cost breakdown.
    
    Args:
        breakdown: ScenarioBreakdown object
    """

    for line in breakdown.lines:
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
    
    if threshold_crossed:
        st.info(f"{person_prefix}In-home care is feasible, but based on the level of help you'll likely need, the monthly cost (~${inhome_estimate:,.0f}/mo) approaches or exceeds what families often pay for Assisted Living. Consider touring Assisted Living communities as a more predictable alternative.")
    else:
        st.success(f"{person_prefix}In-home care appears workable at ~${inhome_estimate:,.0f}/mo. Adjust weekly hours to see how costs change.")


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
        from products.cost_planner_v2.household import compute_household_total
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

    # Radio selection for which plan to continue with
    if show_both:
        care_type_display_map = {
            "assisted_living": "Assisted Living",
            "memory_care": "Memory Care",
            "memory_care_high_acuity": "Memory Care (High Acuity)",
        }
        recommended_display = care_type_display_map.get(recommended_tier, "Recommended Plan")

        selected_plan = st.radio(
            "Which scenario would you like to explore in detail?",
            options=[
                f"facility_{recommended_tier}",
                "inhome_in_home_care"
            ],
            format_func=lambda x: recommended_display if x.startswith("facility") else "In-Home Care",
            key="comparison_plan_radio",
            horizontal=True
        )

        # Store selection
        st.session_state.comparison_selected_plan = selected_plan
    else:
        # Only in-home shown, auto-select it
        st.session_state.comparison_selected_plan = "inhome_in_home_care"
        st.info("📋 **Selected Plan:** In-Home Care")

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
            if st.session_state.comparison_selected_plan is None and show_both:
                st.error("Please select which plan you'd like to explore.")
            else:
                # [FA_DEBUG] Handoff: Store selected plan's care cost for Financial Assessment
                selected_plan_key = st.session_state.comparison_selected_plan

                # Determine which breakdown to use based on selection
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

                # [FA_DEBUG] Log what we're passing (quieted - uncomment block below to see details)
                print("[FA_DEBUG] FA_DEBUG AVAILABLE - uncomment in comparison_view.py:799 for details")
                # print("\n[FA_DEBUG] ========== QUICK ESTIMATE → FA HANDOFF ==========")
                # print(f"[FA_DEBUG] Selected Plan: {selected_plan_key}")
                # print(f"[FA_DEBUG] Care Type: {selected_breakdown.care_type}")
                # print(f"[FA_DEBUG] Is Facility: {is_facility}")
                # print(f"[FA_DEBUG] Monthly Total: ${selected_breakdown.monthly_total:,.0f}")
                # print(f"[FA_DEBUG] Home Carry Cost: ${home_carry_monthly:,.0f}")
                # if is_facility:
                #     print(f"[FA_DEBUG] Care Cost (facility only, home excluded): ${care_cost_monthly:,.0f}")
                # else:
                #     print(f"[FA_DEBUG] Care Cost (in-home, includes home): ${care_cost_monthly:,.0f}")
                # print("[FA_DEBUG] ")
                # print("[FA_DEBUG] Breakdown lines:")
                # for line in selected_breakdown.lines:
                #     print(f"[FA_DEBUG]   - {line.label}: ${line.value:,.0f} (applied: {line.applied})")
                # print("[FA_DEBUG] =====================================================")

                # Store in expected format for expert_review.py
                st.session_state.cost_v2_quick_estimate = {
                    "estimate": {
                        "monthly_adjusted": care_cost_monthly,
                        "monthly_total": selected_breakdown.monthly_total,
                        "care_type": selected_breakdown.care_type,
                        "selected_plan": selected_plan_key,
                    }
                }

                # ============================================================
                # LLM SHADOW MODE: Generate contextual Navi advice (read-only)
                # ============================================================
                # Read FEATURE_LLM_NAVI flag from session state
                # Values: off|shadow|assist|adjust (default: off)
                llm_mode = st.session_state.get("FEATURE_LLM_NAVI", "off")
                
                if llm_mode == "shadow":
                    try:
                        from ai.navi_engine import generate_safe_with_normalization
                        
                        # Build context from available data
                        gcp_rec = st.session_state.get("gcp_care_recommendation", {})
                        qualifiers = st.session_state.get("cost_v2_qualifiers", {})
                        triage = st.session_state.get("cost_v2_triage", {})
                        
                        # Extract context variables
                        tier = selected_breakdown.care_type or "assisted_living"
                        has_partner = qualifiers.get("has_partner", False)
                        move_pref = triage.get("move_preference")
                        keep_home = qualifiers.get("keep_home", False)
                        region = "national"  # TODO: Extract from zip_code region mapping
                        
                        # Build flags list
                        flags = []
                        if qualifiers.get("is_veteran"):
                            flags.append("veteran")
                        if qualifiers.get("is_homeowner"):
                            flags.append("homeowner")
                        if qualifiers.get("medicaid_planning"):
                            flags.append("medicaid_planning_needed")
                        
                        # Add in-home cost context for in_home_care tier
                        inhome_context = ""
                        if tier == "in_home_care":
                            # Calculate intensity and threshold for context
                            intensity_score = _calculate_support_intensity()
                            threshold = _get_cost_threshold(intensity_score)
                            threshold_crossed = care_cost_monthly >= threshold
                            
                            # Map intensity to label
                            if intensity_score <= 1:
                                intensity_label = "low"
                            elif intensity_score <= 3:
                                intensity_label = "medium"
                            else:
                                intensity_label = "high"
                            
                            inhome_context = f"""INHOME_ESTIMATE: ${care_cost_monthly:,.0f}
CARE_INTENSITY: {intensity_label}
THRESHOLD: ${threshold:,.0f}
THRESHOLD_CROSSED: {str(threshold_crossed).lower()}

"""
                        
                        # Build top reasons from GCP if available
                        top_reasons = []
                        if isinstance(gcp_rec, dict) and "top_reasons" in gcp_rec:
                            top_reasons = gcp_rec.get("top_reasons", [])[:3]
                        
                        # Generate advice with normalization (shadow mode - no UI changes)
                        # This handles tier aliases and skips if tier is invalid
                        # Pass inhome_context as an additional parameter if needed
                        
                        # For now, store the context in session state so navi_engine can access it
                        if inhome_context:
                            st.session_state["_llm_inhome_context"] = inhome_context
                        else:
                            st.session_state.pop("_llm_inhome_context", None)
                        
                        success, advice = generate_safe_with_normalization(
                            tier=tier,
                            has_partner=has_partner,
                            move_preference=move_pref,
                            keep_home=keep_home,
                            monthly_adjusted=float(care_cost_monthly),
                            region=region,
                            flags=flags,
                            top_reasons=top_reasons,
                            mode="shadow",
                        )
                        
                        # Clean up temporary session state
                        st.session_state.pop("_llm_inhome_context", None)
                        
                        # Log for dev diagnostics only
                        if success and advice:
                            print(
                                f"[LLM_SHADOW] advice_valid=True "
                                f"messages={len(advice.messages)} "
                                f"insights={len(advice.insights)} "
                                f"questions={len(advice.questions_next)} "
                                f"adjustments={len(advice.proposed_adjustments or {})} "
                                f"confidence={advice.confidence:.2f}"
                            )
                        else:
                            print("[LLM_SHADOW] advice_valid=False (generation failed or disabled)")
                    
                    except Exception as e:
                        # Silent failure - shadow mode must not affect user flow
                        print(f"[LLM_SHADOW] Exception (silent): {e}")
                # ============================================================

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
