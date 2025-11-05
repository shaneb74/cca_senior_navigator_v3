"""Exit Step - Cost Planner v2 (Redesigned)

Final celebration and next steps page.
Clean, calm completion with clear actionable next steps.

Design Philosophy:
- Celebrate completion in a calm, confident way
- Summarize accomplishments clearly
- Offer actionable next steps
- Visually cohesive with Expert Advisor Review
"""

import streamlit as st

from core.ui import render_navi_panel_v2
from products.cost_planner_v2.utils.financial_helpers import (
    calculate_total_asset_debt,
    calculate_total_asset_value,
    calculate_total_monthly_income,
    normalize_asset_data,
    normalize_income_data,
)


def render():
    """Render exit step with clean, modern completion layout."""

    # Clear restart flag so user can restart again after completing
    if "_cost_v2_restart_handled" in st.session_state:
        del st.session_state._cost_v2_restart_handled

    # Set canonical completion flag (gate contract for CCR tile)
    c = st.session_state.setdefault("cost", {})
    c["completed"] = True
    print("[COST_V2_EXIT] Set cost.completed=True (canonical gate)")
    
    # Mark Cost Planner as complete in MCIP
    from core.mcip import MCIP
    MCIP.mark_product_complete("cost_planner_v2")  # Will normalize to "cost_planner"
    print("[COST_EXIT] Marked Cost Planner complete via MCIP")

    # Apply clean modern CSS
    st.markdown(
        """
        <style>
        /* Clean modern card styling */
        .exit-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 24px;
        }
        
        .exit-card h3 {
            font-size: 20px;
            font-weight: 600;
            color: #111827;
            margin: 0 0 20px 0;
        }
        
        .accomplishment-item {
            font-size: 15px;
            color: #374151;
            line-height: 1.8;
            margin-bottom: 8px;
        }
        
        .highlight-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .highlight-row:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }
        
        .highlight-label {
            font-size: 14px;
            color: #6b7280;
        }
        
        .highlight-value {
            font-size: 16px;
            font-weight: 600;
            color: #111827;
        }
        
        .next-step-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 28px;
            height: 100%;
            min-height: 220px;
            display: flex;
            flex-direction: column;
        }
        
        .next-step-card h3 {
            font-size: 18px;
            font-weight: 600;
            color: #111827;
            margin: 0 0 12px 0;
        }
        
        .next-step-card p {
            font-size: 14px;
            color: #6b7280;
            line-height: 1.6;
            margin: 0 0 20px 0;
            flex-grow: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Compact Navi panel at top
    from core.navi_module import render_module_navi_coach
    render_module_navi_coach(
        title_text="Your Financial Plan is Complete!",
        body_text="You can download a copy, share it with your family, or review it with an advisor.",
        tip_text=None,
    )

    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)

    _render_accomplishments_card()
    _render_plan_highlights_card()
    st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
    _render_whats_next_section()


def _render_navi_completion():
    """DEPRECATED - Replaced by compact Navi at page top.
    
    Old function that rendered full Navi panel with celebratory tone.
    Now using render_module_navi_coach() instead.
    """
    pass  # No longer used


def _render_accomplishments_card():
    """Render accomplishments checklist card with clean styling."""

    st.markdown('<div class="exit-card">', unsafe_allow_html=True)
    st.markdown("<h3>✓ Summary of What You've Accomplished</h3>", unsafe_allow_html=True)

    accomplishments = [
        "Authenticated and secured your account",
        "Completed your Guided Care Plan",
        "Assessed income and available assets",
        "Calculated care costs and coverage",
        "Reviewed your financial runway",
        "Had expert review of your financial plan",
    ]

    for item in accomplishments:
        st.markdown(f'<div class="accomplishment-item">• {item}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_plan_highlights_card():
    """Render plan highlights with clean two-column layout."""

    st.markdown('<div class="exit-card">', unsafe_allow_html=True)
    st.markdown("<h3>💡 Plan Highlights</h3>", unsafe_allow_html=True)

    # Get care recommendation
    from core.mcip import MCIP

    recommendation = MCIP.get_care_recommendation()

    # Get financial metrics
    metrics = _calculate_completion_metrics()

    # Extract base_care, home_carry, combined using persisted selection
    ss = st.session_state
    cost = ss.get("cost", {}) or {}
    
    # Use the user's choice from Quick Estimate
    active = ss.get("cp.persisted_selection") or ss.get("cp_selected_assessment")
    
    # Fallback: map GCP tier -> cp key only if needed
    if not active:
        gcp_tier = (ss.get("gcp") or {}).get("published_tier")
        if gcp_tier in ("memory_care", "memory_care_high_acuity"):
            active = "mc"
        elif gcp_tier == "assisted_living":
            active = "al"
        else:
            active = "home"
    
    # Base comparator: CARE ONLY
    base_care = cost.get("monthly_total")
    
    # Fallbacks
    if base_care is None and isinstance(cost.get("last_totals"), dict):
        lt = cost["last_totals"].get(active)
        if isinstance(lt, dict):
            base_care = lt.get("care")
    if base_care is None and isinstance(ss.get("_qe_totals"), dict):
        base_care = ss["_qe_totals"].get(active)
    
    try:
        base_care = float(base_care) if base_care is not None else metrics['monthly_cost']
    except Exception:
        base_care = metrics['monthly_cost']
    
    # Carry for display and optional combined
    home_carry = cost.get("home_carry_monthly")
    try:
        home_carry = float(home_carry) if home_carry is not None else 0.0
    except Exception:
        home_carry = 0.0
    
    combined = (base_care or 0.0) + home_carry

    # Display highlights in clean rows
    if recommendation:
        tier_label = recommendation.tier.replace("_", " ").title()
        confidence_pct = int(recommendation.confidence * 100)
        
        st.markdown(
            f"""
            <div class="highlight-row">
                <div class="highlight-label">Recommended Care Plan</div>
                <div class="highlight-value">{tier_label}</div>
            </div>
            <div class="highlight-row">
                <div class="highlight-label">Confidence Level</div>
                <div class="highlight-value">{confidence_pct}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Monthly costs
    st.markdown(
        f"""
        <div class="highlight-row">
            <div class="highlight-label">Monthly Care Cost</div>
            <div class="highlight-value">${base_care:,.0f}/mo</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if home_carry and home_carry > 0:
        st.markdown(
            f"""
            <div class="highlight-row">
                <div class="highlight-label">Home Carrying Cost</div>
                <div class="highlight-value">+${home_carry:,.0f}/mo</div>
            </div>
            <div class="highlight-row">
                <div class="highlight-label">Combined Monthly Cost</div>
                <div class="highlight-value">${combined:,.0f}/mo</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Monthly gap/surplus
    if metrics["monthly_gap"] >= 0:
        gap_label = "Monthly Surplus"
        gap_value = f"+${metrics['monthly_gap']:,.0f}"
    else:
        gap_label = "Monthly Gap"
        gap_value = f"${abs(metrics['monthly_gap']):,.0f}"
    
    st.markdown(
        f"""
        <div class="highlight-row">
            <div class="highlight-label">{gap_label}</div>
            <div class="highlight-value">{gap_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def _calculate_completion_metrics() -> dict:
    """Calculate financial metrics for completion summary.

    Returns dict with:
    - monthly_cost
    - monthly_coverage
    - monthly_gap (positive = surplus, negative = shortfall)
    - total_assets
    """

    modules = st.session_state.get("cost_v2_modules", {})

    # Get module data
    income_data = modules.get("income", {}).get("data", {})
    assets_data = modules.get("assets", {}).get("data", {})
    va_data = modules.get("va_benefits", {}).get("data", {})
    insurance_data = modules.get("health_insurance", {}).get("data", {})
    life_insurance_data = modules.get("life_insurance", {}).get("data", {})

    # Normalize income and asset data for consistent calculations
    normalized_income = normalize_income_data(income_data)
    normalized_assets = normalize_asset_data(assets_data)

    base_monthly_income = calculate_total_monthly_income(normalized_income)

    va_monthly_benefit = 0.0
    if va_data:
        va_monthly_benefit = (
            va_data.get("va_disability_monthly", 0.0)
            + va_data.get("aid_attendance_monthly", 0.0)
        )

    # Include VA benefits in total monthly income
    total_monthly_income = base_monthly_income + va_monthly_benefit

    total_assets = calculate_total_asset_value(normalized_assets)
    total_asset_debt = calculate_total_asset_debt(normalized_assets)
    net_assets = max(total_assets - total_asset_debt, 0.0)

    # Get monthly care cost from MCIP
    from core.mcip import MCIP

    estimated_monthly_cost = 0
    recommendation = MCIP.get_care_recommendation()

    financial_profile = MCIP.get_financial_profile()
    if financial_profile and hasattr(financial_profile, "estimated_monthly_cost"):
        estimated_monthly_cost = financial_profile.estimated_monthly_cost
    elif recommendation:
        tier_defaults = {
            "independent": 2500,
            "in_home": 4500,
            "assisted_living": 5000,
            "memory_care": 7000,
            "memory_care_high_acuity": 9000,
        }
        estimated_monthly_cost = tier_defaults.get(recommendation.tier, 5000)

    # Calculate total coverage
    ltc_monthly = (
        insurance_data.get("ltc_daily_benefit", 0) * 30
        if insurance_data and insurance_data.get("has_ltc_insurance")
        else 0
    )
    life_monthly = life_insurance_data.get("monthly_benefit", 0) if life_insurance_data else 0

    total_coverage = ltc_monthly + life_monthly + va_monthly_benefit

    # Calculate gap
    monthly_coverage = total_monthly_income + total_coverage
    monthly_gap = monthly_coverage - estimated_monthly_cost

    return {
        "monthly_cost": estimated_monthly_cost,
        "monthly_coverage": monthly_coverage,
        "monthly_gap": monthly_gap,
        "total_assets": total_assets,
        "net_assets": net_assets,
        "va_monthly_benefit": va_monthly_benefit,
        "base_monthly_income": base_monthly_income,
    }


def _render_whats_next_section():
    """Render What's Next section with clean 3-column card grid."""

    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 32px;">
            <h2 style="font-size: 28px; font-weight: 700; color: #111827; margin: 0;">
                🚀 What's Next
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3-column grid
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown('<div class="next-step-card">', unsafe_allow_html=True)
        st.markdown("<h3>📅 Meet with an Advisor</h3>", unsafe_allow_html=True)
        st.markdown("<p>Review your plan with a certified senior care advisor</p>", unsafe_allow_html=True)
        if st.button(
            "Schedule Meeting", use_container_width=True, type="primary", key="schedule_advisor_btn"
        ):
            from core.nav import route_to

            st.session_state.cost_planner_v2_complete = True
            route_to("pfma_v3")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="next-step-card">', unsafe_allow_html=True)
        st.markdown("<h3>📄 Download Your Plan</h3>", unsafe_allow_html=True)
        st.markdown("<p>Get a PDF copy of your comprehensive financial plan</p>", unsafe_allow_html=True)
        if st.button("Download PDF", use_container_width=True, key="download_pdf_btn"):
            st.info("📄 PDF generation coming soon!")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="next-step-card">', unsafe_allow_html=True)
        st.markdown("<h3>🏠 Return to Lobby</h3>", unsafe_allow_html=True)
        st.markdown("<p>Explore other tools and resources in your dashboard</p>", unsafe_allow_html=True)
        if st.button("Go to Lobby", use_container_width=True, key="goto_lobby_btn"):
            from core.url_helpers import back_to_lobby

            st.session_state.cost_planner_v2_complete = True
            back_to_lobby()
        st.markdown("</div>", unsafe_allow_html=True)


def _clear_all_data():
    """Clear all Cost Planner v2 session data."""
    keys_to_clear = [
        "cost_v2_step",
        "cost_v2_guest_mode",
        "cost_v2_triage",
        "cost_v2_current_module",
        "cost_v2_modules",
        "cost_v2_income",
        "cost_v2_assets",
        "cost_v2_va_benefits",
        "cost_v2_health_insurance",
        "cost_v2_life_insurance",
        "cost_v2_advisor_notes",
        "cost_v2_schedule_advisor",
        "cost_v2_show_restart_confirm",
        "cost_planner_v2_published",
        "cost_planner_v2_complete",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Reset to intro step
    st.session_state.cost_v2_step = "intro"
