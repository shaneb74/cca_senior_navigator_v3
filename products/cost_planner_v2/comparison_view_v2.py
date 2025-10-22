"""
Cost Planner v2 - Comparison View (Phase 2)

Side-by-side comparison of Recommended Plan vs In-Home Care.
Uses care-type-specific modifiers and real calculations.
"""

from typing import Optional
import streamlit as st

from core.mcip import MCIP
from products.cost_planner_v2 import comparison_calcs
from products.cost_planner_v2.comparison_calcs import ScenarioBreakdown


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def render_comparison_view(zip_code: Optional[str] = None):
    """Render side-by-side comparison of recommended plan vs in-home care.
    
    Args:
        zip_code: Optional ZIP code for regional adjustment
    """
    
    # Initialize session state
    if "comparison_home_carry_cost" not in st.session_state:
        st.session_state.comparison_home_carry_cost = 4500.0
    
    if "comparison_keep_home" not in st.session_state:
        st.session_state.comparison_keep_home = False
    
    if "comparison_selected_plan" not in st.session_state:
        st.session_state.comparison_selected_plan = None
    
    if "comparison_inhome_hours" not in st.session_state:
        st.session_state.comparison_inhome_hours = 8.0
    
    # Get GCP recommendation
    gcp_rec = MCIP.get_care_recommendation()
    
    # Determine what to show
    show_both = True
    recommended_tier = "assisted_living"  # Default fallback
    
    if gcp_rec and gcp_rec.tier:
        recommended_tier = gcp_rec.tier
        # Only show one column if recommendation is in-home
        if recommended_tier == "in_home_care":
            show_both = False
    
    # Header
    st.markdown("### Compare your recommended plan with staying at home")
    st.markdown(
        """<div style="color: var(--text-secondary); margin-bottom: 2rem; font-size: 0.95rem;">
        <strong>💬 Navi says:</strong> These numbers can be eye-opening. 
        Let's look at each option and figure out how to pay for it.
        </div>""",
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Calculate both scenarios
    if show_both:
        # Facility recommendation - show both scenarios
        facility_breakdown = _calculate_facility_scenario(recommended_tier, zip_code)
        inhome_breakdown = _calculate_inhome_scenario(zip_code)
        
        _render_two_column_comparison(
            facility_breakdown,
            inhome_breakdown,
            recommended_tier
        )
    else:
        # In-home recommendation - show in-home only
        inhome_breakdown = _calculate_inhome_scenario(zip_code)
        _render_inhome_primary_view(inhome_breakdown)
    
    # Plan selection and CTA
    st.markdown("---")
    _render_plan_selection_and_cta(recommended_tier, show_both)


# ==============================================================================
# CALCULATION HELPERS
# ==============================================================================

def _calculate_facility_scenario(care_type: str, zip_code: Optional[str]) -> ScenarioBreakdown:
    """Calculate facility care scenario.
    
    Args:
        care_type: assisted_living, memory_care, or memory_care_high_acuity
        zip_code: ZIP code for regional adjustment
        
    Returns:
        ScenarioBreakdown object
    """
    return comparison_calcs.calculate_facility_scenario(
        care_type=care_type,
        zip_code=zip_code,
        keep_home=st.session_state.comparison_keep_home,
        home_carry_override=st.session_state.comparison_home_carry_cost
    )


def _calculate_inhome_scenario(zip_code: Optional[str]) -> ScenarioBreakdown:
    """Calculate in-home care scenario.
    
    Args:
        zip_code: ZIP code for regional adjustment
        
    Returns:
        ScenarioBreakdown object
    """
    return comparison_calcs.calculate_inhome_scenario(
        zip_code=zip_code,
        hours_per_day=st.session_state.comparison_inhome_hours,
        home_carry_override=st.session_state.comparison_home_carry_cost
    )


# ==============================================================================
# RENDERING FUNCTIONS
# ==============================================================================

def _render_two_column_comparison(
    facility_breakdown: ScenarioBreakdown,
    inhome_breakdown: ScenarioBreakdown,
    recommended_tier: str
):
    """Render side-by-side comparison.
    
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
        st.markdown("#### 🏥 Your Recommended Plan")
        _render_care_card(
            breakdown=facility_breakdown,
            care_type_display=care_type_display_map.get(recommended_tier, "Facility Care"),
            is_facility=True,
            card_key="facility"
        )
    
    with col2:
        st.markdown("#### 🏠 Compare: In-Home Care")
        _render_care_card(
            breakdown=inhome_breakdown,
            care_type_display="In-Home Care",
            is_facility=False,
            card_key="inhome"
        )


def _render_inhome_primary_view(inhome_breakdown: ScenarioBreakdown):
    """Render in-home care as primary view.
    
    Args:
        inhome_breakdown: In-home care breakdown
    """
    
    st.markdown("#### 🏠 In-Home Care Plan")
    _render_care_card(
        breakdown=inhome_breakdown,
        care_type_display="In-Home Care",
        is_facility=False,
        card_key="inhome_primary"
    )
    
    st.markdown("---")
    
    # Optional: Show facility comparison button
    if st.button("📊 Show Assisted Living Comparison", use_container_width=True):
        st.info("💡 Click 'Back' and complete the Guided Care Plan to see facility comparisons.")


def _render_care_card(
    breakdown: ScenarioBreakdown,
    care_type_display: str,
    is_facility: bool,
    card_key: str
):
    """Render a single care scenario card.
    
    Args:
        breakdown: ScenarioBreakdown object
        care_type_display: Display name for care type
        is_facility: Whether this is facility care
        card_key: Unique key for widgets
    """
    
    # Location section
    st.markdown("**📍 Location**")
    st.markdown(f"{breakdown.location_label}")
    
    st.markdown("")
    
    # Main totals (before interactive controls)
    base_monthly = breakdown.monthly_total
    
    st.markdown("**💰 Care Costs**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly", f"${base_monthly:,.0f}")
    with col2:
        st.metric("Annual", f"${breakdown.annual_total:,.0f}")
    with col3:
        st.metric("3-Year", f"${breakdown.three_year_total:,.0f}")
    
    st.markdown("")
    
    # Cost breakdown
    with st.expander("📋 Cost Breakdown", expanded=False):
        _render_cost_breakdown(breakdown)
    
    st.markdown("")
    
    # Interactive controls for home carry and hours
    if is_facility:
        _render_facility_controls(card_key)
    else:
        _render_inhome_controls(card_key)
    
    st.markdown("")
    
    # Notes section
    with st.expander("📝 Notes", expanded=False):
        if is_facility:
            st.markdown("""
            - Facility costs include room, meals, basic care
            - Additional services may apply
            - Medicare does not cover long-term care
            """)
        else:
            st.markdown("""
            - In-home care hours vary by need level
            - May include respite care, home modifications
            - Some services covered by Medicare/Medicaid
            """)


def _render_facility_controls(card_key: str):
    """Render facility-specific controls (keep home toggle).
    
    Args:
        card_key: Unique key for widgets
    """
    
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
        home_carry = st.number_input(
            "Monthly home expense",
            min_value=0.0,
            value=st.session_state.comparison_home_carry_cost,
            step=100.0,
            help="Mortgage, rent, property tax, insurance, maintenance",
            key=f"{card_key}_home_carry"
        )
        
        if home_carry != st.session_state.comparison_home_carry_cost:
            st.session_state.comparison_home_carry_cost = home_carry
            st.rerun()
        
        st.caption(f"✓ Added to total (${home_carry:,.0f}/mo)")
    else:
        st.caption("Home expenses not included")


def _render_inhome_controls(card_key: str):
    """Render in-home-specific controls (hours per day, home carry).
    
    Args:
        card_key: Unique key for widgets
    """
    
    st.markdown("**⏰ Care Hours**")
    
    hours = st.slider(
        "Hours per day",
        min_value=2.0,
        max_value=24.0,
        value=st.session_state.comparison_inhome_hours,
        step=1.0,
        key=f"{card_key}_hours",
        help="Adjust based on care needs"
    )
    
    if hours != st.session_state.comparison_inhome_hours:
        st.session_state.comparison_inhome_hours = hours
        st.rerun()
    
    st.markdown("")
    
    st.markdown("**🏡 Home Costs**")
    
    home_carry = st.number_input(
        "Monthly home expense",
        min_value=0.0,
        value=st.session_state.comparison_home_carry_cost,
        step=100.0,
        help="Mortgage, rent, property tax, insurance, maintenance",
        key=f"{card_key}_home_carry"
    )
    
    if home_carry != st.session_state.comparison_home_carry_cost:
        st.session_state.comparison_home_carry_cost = home_carry
        st.rerun()
    
    st.caption(f"✓ Always included (${home_carry:,.0f}/mo)")


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
            st.switch_page("pages/_stubs.py")
        st.markdown("</div>", unsafe_allow_html=True)
