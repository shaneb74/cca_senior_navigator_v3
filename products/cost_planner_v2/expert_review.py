"""Expert Review Step - Cost Planner v2 (Redesigned)

Clean, calm summary page with card-based layout.
No warning banners - just clear information and confident guidance.

Design Philosophy:
- Calm, high-level summary (not a warning screen)
- Clear module completion status without pressure
- Readable financial summary with scannable metrics
- Consistent visual language with Financial Assessment modules
"""

from typing import Dict, Optional, List
import streamlit as st
from datetime import datetime
from core.ui import render_navi_panel_v2


def render():
    """Render expert review with clean card-based layout.
    
    Layout:
    1. Navi Panel (warm, confident guidance)
    2. Module Completion Summary (2-column grid with icons)
    3. Executive Summary (4-metric grid)
    4. Detailed Breakdown (tabs)
    5. Optional Advisor Notes
    6. Fixed Footer Navigation
    """
    
    # Get all module data
    modules = st.session_state.get("cost_v2_modules", {})
    
    # Check if required modules are complete
    income_data = modules.get("income", {}).get("data", {})
    assets_data = modules.get("assets", {}).get("data", {})
    
    if not income_data or not assets_data:
        st.error("⚠️ **Income & Assets modules are required.** Please complete them before accessing Expert Review.")
        if st.button("← Back to Financial Modules"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
        return
    
    # Render sections
    _render_navi_guidance(modules)
    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)  # Spacing
    
    _render_module_completion(modules)
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    
    _render_executive_summary(modules)
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    
    _render_detailed_breakdown(modules)
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    
    _render_advisor_notes()
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    
    _render_footer_navigation()


def _render_navi_guidance(modules: Dict):
    """Render Navi panel with warm, confident tone."""
    
    # Count completed modules
    completed_count = sum([
        1 for module in modules.values()
        if module.get("status") == "completed"
    ])
    total_modules = 6  # Income, Assets, VA, Health Insurance, Life Insurance, Medicaid
    
    # Determine encouragement message
    if completed_count == total_modules:
        encouragement = "You've completed all modules — excellent work! Your financial picture is comprehensive and ready for review."
        icon = "🎉"
        status = "complete"
    elif completed_count >= 2:
        encouragement = "Completing the optional modules gives a clearer financial picture and helps me better estimate how long your assets can pay for care."
        icon = "💡"
        status = "in_progress"
    else:
        encouragement = "Let's get a few more modules done to build a complete financial picture."
        icon = "📋"
        status = "pending"
    
    render_navi_panel_v2(
        title="Your Expert Advisor Review",
        reason="Here's your Expert Advisor Review. I've summarized what you've completed so far and what we still recommend.",
        encouragement={
            "icon": icon,
            "message": encouragement,
            "status": status
        },
        context_chips=[
            {"label": f"{completed_count}/{total_modules} modules completed"},
            {"label": "You can finalize now or go back to add more details"}
        ],
        primary_action=None  # No action in Navi here
    )


def _render_module_completion(modules: Dict):
    """Render module completion summary in 2-column grid."""
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Module Completion Summary")
    
    # Define all modules with their completion status
    module_list = [
        {
            "key": "income",
            "label": "Income Sources",
            "required": True
        },
        {
            "key": "assets",
            "label": "Assets & Resources",
            "required": True
        },
        {
            "key": "va_benefits",
            "label": "VA Benefits",
            "required": False
        },
        {
            "key": "health_insurance",
            "label": "Health & Insurance",
            "required": False
        },
        {
            "key": "life_insurance",
            "label": "Life Insurance",
            "required": False
        },
        {
            "key": "medicaid_navigation",
            "label": "Medicaid Navigation",
            "required": False
        }
    ]
    
    # Add completion status to each module
    for module in module_list:
        module_data = modules.get(module["key"], {})
        module["completed"] = module_data.get("status") == "completed"
    
    # Render 2-column grid
    col1, col2 = st.columns(2, gap="large")
    
    # Split modules into two columns
    left_modules = module_list[::2]  # Every other module starting from 0
    right_modules = module_list[1::2]  # Every other module starting from 1
    
    with col1:
        for module in left_modules:
            _render_module_status_item(module)
    
    with col2:
        for module in right_modules:
            _render_module_status_item(module)
    
    # Legend
    st.markdown('<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(0,0,0,0.08);"></div>', unsafe_allow_html=True)
    st.caption("**Legend:** ✅ Completed • ⚪ Optional / Not Started")
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_module_status_item(module: Dict):
    """Render a single module status item."""
    
    if module["completed"]:
        icon = "✅"
        status_class = "completed"
        status_text = "Completed"
    else:
        icon = "⚪"
        status_class = "optional" if not module["required"] else "incomplete"
        status_text = "Optional" if not module["required"] else "Required"
    
    st.markdown(
        f'<div class="module-status-item {status_class}">'
        f'  <span class="module-icon">{icon}</span>'
        f'  <span class="module-label">{module["label"]}</span>'
        f'  <span class="module-status">{status_text}</span>'
        f'</div>',
        unsafe_allow_html=True
    )


def _render_executive_summary(modules: Dict):
    """Render executive summary with 4-metric grid."""
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 💼 Executive Summary")
    
    # Calculate metrics from module data
    metrics = _calculate_financial_metrics(modules)
    
    # 4-column grid for key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Monthly Care Cost",
            value=f"${metrics['monthly_cost']:,.0f}",
            help="Total estimated monthly care costs"
        )
    
    with col2:
        st.metric(
            label="Coverage & Income",
            value=f"${metrics['monthly_coverage']:,.0f}",
            help="Total monthly coverage from all sources"
        )
    
    with col3:
        if metrics['monthly_gap'] > 0:
            st.metric(
                label="Monthly Surplus",
                value=f"+${metrics['monthly_gap']:,.0f}",
                delta=f"+${metrics['monthly_gap']:,.0f}",
                delta_color="normal",
                help="Monthly surplus after all expenses"
            )
        else:
            gap = abs(metrics['monthly_gap'])
            st.metric(
                label="Monthly Gap",
                value=f"${gap:,.0f}",
                delta=f"-${gap:,.0f}",
                delta_color="inverse",
                help="Monthly shortfall to cover from assets"
            )
    
    with col4:
        runway_display = metrics['runway_display']
        st.metric(
            label="Financial Runway",
            value=runway_display,
            help="Estimated time until assets depleted" if runway_display != "Unlimited" else "Sufficient income to cover all costs"
        )
    
    # Context line (care plan reference)
    from core.mcip import MCIP
    recommendation = MCIP.get_care_recommendation()
    if recommendation:
        tier_label = recommendation.tier.replace("_", " ").title()
        confidence_pct = int(recommendation.confidence * 100)
        st.caption(f"Based on: **{tier_label}** care plan, {confidence_pct}% confidence")
    
    st.markdown('</div>', unsafe_allow_html=True)


def _calculate_financial_metrics(modules: Dict) -> Dict:
    """Calculate all financial metrics from module data.
    
    Returns dict with:
    - monthly_cost: Total monthly care cost
    - monthly_coverage: Total monthly coverage (income + benefits)
    - monthly_gap: Surplus (positive) or gap (negative)
    - total_assets: Total available assets
    - runway_years: Years until assets depleted
    - runway_display: Display string for runway metric
    """
    
    # Get module data
    income_data = modules.get("income", {}).get("data", {})
    assets_data = modules.get("assets", {}).get("data", {})
    va_data = modules.get("va_benefits", {}).get("data", {})
    insurance_data = modules.get("health_insurance", {}).get("data", {})
    life_insurance_data = modules.get("life_insurance", {}).get("data", {})
    
    # Calculate total monthly income
    total_monthly_income = (
        income_data.get("ss_monthly", 0) +
        income_data.get("pension_monthly", 0) +
        income_data.get("employment_monthly", 0) +
        income_data.get("investment_monthly", 0) +
        income_data.get("other_monthly", 0) +
        (va_data.get("va_disability_monthly", 0) if va_data else 0) +
        (va_data.get("aid_attendance_monthly", 0) if va_data else 0)
    )
    
    # Calculate total assets
    total_assets = (
        assets_data.get("checking_savings", 0) +
        assets_data.get("investment_accounts", 0) +
        assets_data.get("primary_residence_value", 0) +
        assets_data.get("other_real_estate", 0) +
        assets_data.get("other_resources", 0)
    )
    
    # Get monthly care cost from MCIP
    from core.mcip import MCIP
    estimated_monthly_cost = 0
    recommendation = MCIP.get_care_recommendation()
    
    financial_profile = MCIP.get_financial_profile()
    if financial_profile and hasattr(financial_profile, 'estimated_monthly_cost'):
        estimated_monthly_cost = financial_profile.estimated_monthly_cost
    elif recommendation:
        # Fallback: tier-based defaults
        tier_defaults = {
            'independent': 2500,
            'in_home': 4500,
            'assisted_living': 5000,
            'memory_care': 7000,
            'memory_care_high_acuity': 9000
        }
        estimated_monthly_cost = tier_defaults.get(recommendation.tier, 5000)
    
    # Calculate total coverage
    total_coverage = (
        (insurance_data.get("ltc_daily_benefit", 0) * 30 if insurance_data and insurance_data.get("has_ltc_insurance") else 0) +
        (life_insurance_data.get("monthly_benefit", 0) if life_insurance_data else 0)
    )
    
    # Calculate gap (positive = surplus, negative = shortfall)
    monthly_coverage = total_monthly_income + total_coverage
    monthly_gap = monthly_coverage - estimated_monthly_cost
    
    # Calculate runway
    if monthly_gap < 0 and total_assets > 0:
        shortfall = abs(monthly_gap)
        runway_months = int(total_assets / shortfall)
        runway_years = runway_months / 12
        runway_display = f"{runway_years:.1f} years"
    else:
        runway_years = 999
        runway_display = "Unlimited"
    
    return {
        "monthly_cost": estimated_monthly_cost,
        "monthly_coverage": monthly_coverage,
        "monthly_gap": monthly_gap,
        "total_assets": total_assets,
        "runway_years": runway_years,
        "runway_display": runway_display
    }


def _render_detailed_breakdown(modules: Dict):
    """Render detailed financial breakdown in tabs."""
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Detailed Breakdown")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Financial Overview",
        "📊 Monthly Costs",
        "🛡️ Coverage & Benefits",
        "📈 Projections"
    ])
    
    with tab1:
        _render_financial_overview_tab(modules)
    
    with tab2:
        _render_monthly_costs_tab(modules)
    
    with tab3:
        _render_coverage_tab(modules)
    
    with tab4:
        _render_projections_tab(modules)
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_financial_overview_tab(modules: Dict):
    """Render financial overview tab content."""
    
    income_data = modules.get("income", {}).get("data", {})
    assets_data = modules.get("assets", {}).get("data", {})
    va_data = modules.get("va_benefits", {}).get("data", {})
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("#### Monthly Income Sources")
        
        # Social Security
        ss_monthly = income_data.get("ss_monthly", 0)
        if ss_monthly > 0:
            st.markdown(f"**Social Security:** ${ss_monthly:,.0f}")
        
        # Pension
        pension_monthly = income_data.get("pension_monthly", 0)
        if pension_monthly > 0:
            st.markdown(f"**Pension:** ${pension_monthly:,.0f}")
        
        # Employment
        employment_monthly = income_data.get("employment_monthly", 0)
        if employment_monthly > 0:
            st.markdown(f"**Employment:** ${employment_monthly:,.0f}")
        
        # Investment
        investment_monthly = income_data.get("investment_monthly", 0)
        if investment_monthly > 0:
            st.markdown(f"**Investment Income:** ${investment_monthly:,.0f}")
        
        # Other
        other_monthly = income_data.get("other_monthly", 0)
        if other_monthly > 0:
            st.markdown(f"**Other Income:** ${other_monthly:,.0f}")
        
        # VA Benefits
        if va_data:
            va_disability = va_data.get("va_disability_monthly", 0)
            aid_attendance = va_data.get("aid_attendance_monthly", 0)
            if va_disability > 0:
                st.markdown(f"**VA Disability:** ${va_disability:,.0f}")
            if aid_attendance > 0:
                st.markdown(f"**Aid & Attendance:** ${aid_attendance:,.0f}")
        
        # Total
        total_income = (
            ss_monthly + pension_monthly + employment_monthly +
            investment_monthly + other_monthly +
            (va_data.get("va_disability_monthly", 0) if va_data else 0) +
            (va_data.get("aid_attendance_monthly", 0) if va_data else 0)
        )
        st.markdown(f"---")
        st.markdown(f"**Total Monthly Income:** ${total_income:,.0f}")
    
    with col2:
        st.markdown("#### Available Assets")
        
        # Checking & Savings
        checking_savings = assets_data.get("checking_savings", 0)
        if checking_savings > 0:
            st.markdown(f"**Checking & Savings:** ${checking_savings:,.0f}")
        
        # Investment Accounts
        investment_accounts = assets_data.get("investment_accounts", 0)
        if investment_accounts > 0:
            st.markdown(f"**Investment Accounts:** ${investment_accounts:,.0f}")
        
        # Primary Residence
        primary_residence = assets_data.get("primary_residence_value", 0)
        if primary_residence > 0:
            st.markdown(f"**Primary Residence:** ${primary_residence:,.0f}")
        
        # Other Real Estate
        other_re = assets_data.get("other_real_estate", 0)
        if other_re > 0:
            st.markdown(f"**Other Real Estate:** ${other_re:,.0f}")
        
        # Other Resources
        other_resources = assets_data.get("other_resources", 0)
        if other_resources > 0:
            st.markdown(f"**Other Resources:** ${other_resources:,.0f}")
        
        # Total
        total_assets = (
            checking_savings + investment_accounts + primary_residence +
            other_re + other_resources
        )
        st.markdown(f"---")
        st.markdown(f"**Total Assets:** ${total_assets:,.0f}")


def _render_monthly_costs_tab(modules: Dict):
    """Render monthly costs tab content."""
    
    from core.mcip import MCIP
    
    # Get care recommendation
    recommendation = MCIP.get_care_recommendation()
    if not recommendation:
        st.info("Complete your Guided Care Plan to see detailed cost breakdown.")
        return
    
    # Get estimated cost
    financial_profile = MCIP.get_financial_profile()
    if financial_profile and hasattr(financial_profile, 'estimated_monthly_cost'):
        monthly_cost = financial_profile.estimated_monthly_cost
    else:
        tier_defaults = {
            'independent': 2500,
            'in_home': 4500,
            'assisted_living': 5000,
            'memory_care': 7000,
            'memory_care_high_acuity': 9000
        }
        monthly_cost = tier_defaults.get(recommendation.tier, 5000)
    
    # Display care tier
    tier_label = recommendation.tier.replace("_", " ").title()
    st.markdown(f"#### {tier_label} Care Costs")
    
    st.metric("Base Monthly Cost", f"${monthly_cost:,.0f}")
    st.metric("Annual Cost", f"${monthly_cost * 12:,.0f}")
    
    # Show flags if any
    if recommendation.flags:
        st.markdown("---")
        st.markdown("**Care Complexity Factors:**")
        for flag in recommendation.flags:
            flag_id = flag.get('id') if isinstance(flag, dict) else flag
            st.markdown(f"- {flag_id.replace('_', ' ').title()}")


def _render_coverage_tab(modules: Dict):
    """Render coverage & benefits tab content."""
    
    insurance_data = modules.get("health_insurance", {}).get("data", {})
    life_insurance_data = modules.get("life_insurance", {}).get("data", {})
    va_data = modules.get("va_benefits", {}).get("data", {})
    
    st.markdown("#### Coverage Sources")
    
    has_coverage = False
    
    # Medicare
    if insurance_data and insurance_data.get("has_medicare"):
        st.markdown("**Medicare:** ✅ Enrolled")
        has_coverage = True
    
    # Long-Term Care Insurance
    if insurance_data and insurance_data.get("has_ltc_insurance"):
        daily_benefit = insurance_data.get("ltc_daily_benefit", 0)
        monthly_benefit = daily_benefit * 30
        st.markdown(f"**Long-Term Care Insurance:** ${monthly_benefit:,.0f}/month")
        st.caption(f"Daily benefit: ${daily_benefit:.0f}")
        has_coverage = True
    
    # Life Insurance
    if life_insurance_data:
        monthly_benefit = life_insurance_data.get("monthly_benefit", 0)
        if monthly_benefit > 0:
            st.markdown(f"**Life Insurance Benefit:** ${monthly_benefit:,.0f}/month")
            has_coverage = True
    
    # VA Benefits
    if va_data:
        va_disability = va_data.get("va_disability_monthly", 0)
        aid_attendance = va_data.get("aid_attendance_monthly", 0)
        if va_disability > 0:
            st.markdown(f"**VA Disability:** ${va_disability:,.0f}/month")
            has_coverage = True
        if aid_attendance > 0:
            st.markdown(f"**Aid & Attendance:** ${aid_attendance:,.0f}/month")
            has_coverage = True
    
    if not has_coverage:
        st.info("Complete optional modules to add coverage sources.")


def _render_projections_tab(modules: Dict):
    """Render projections tab content."""
    
    metrics = _calculate_financial_metrics(modules)
    
    st.markdown("#### 30-Year Financial Runway")
    
    # Show key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly Care Cost", f"${metrics['monthly_cost']:,.0f}")
    with col2:
        st.metric("Monthly Coverage + Income", f"${metrics['monthly_coverage']:,.0f}")
    with col3:
        if metrics['monthly_gap'] >= 0:
            st.metric("Monthly Surplus", f"+${metrics['monthly_gap']:,.0f}")
        else:
            st.metric("Monthly Gap", f"${abs(metrics['monthly_gap']):,.0f}")
    
    st.markdown("---")
    
    # Calculate runway
    if metrics['monthly_gap'] < 0 and metrics['total_assets'] > 0:
        shortfall = abs(metrics['monthly_gap'])
        runway_years = metrics['runway_years']
        
        st.markdown(f"**Asset Runway:** {runway_years:.1f} years")
        st.markdown(f"**Total Assets Available:** ${metrics['total_assets']:,.0f}")
        
        # Simple projection
        st.markdown("---")
        st.markdown("**Projection (with 3% annual inflation):**")
        
        # Calculate year-by-year
        inflation_rate = 0.03
        remaining_assets = metrics['total_assets']
        years_to_show = min(10, int(runway_years) + 2)
        
        for year in range(1, years_to_show + 1):
            inflation_multiplier = (1 + inflation_rate) ** year
            inflated_gap = shortfall * inflation_multiplier
            annual_gap = inflated_gap * 12
            remaining_assets -= annual_gap
            
            if remaining_assets > 0:
                st.markdown(f"**Year {year}:** ${remaining_assets:,.0f} remaining")
            else:
                st.markdown(f"**Year {year}:** ⚠️ Assets depleted")
                break
    
    elif metrics['monthly_gap'] >= 0:
        st.success("✅ Your income and coverage fully cover care costs. Assets remain intact.")
    else:
        st.info("Complete financial modules to see detailed projections.")


def _render_advisor_notes():
    """Render optional advisor notes section."""
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 💬 Advisor Notes (Optional)")
    
    # Initialize in session state
    if "cost_v2_advisor_notes" not in st.session_state:
        st.session_state.cost_v2_advisor_notes = ""
    
    notes = st.text_area(
        "Add notes for your financial advisor or care planner:",
        value=st.session_state.cost_v2_advisor_notes,
        height=100,
        placeholder="E.g., 'Would like to discuss Medicaid options' or 'Interested in home equity planning'",
        key="advisor_notes_input",
        label_visibility="collapsed"
    )
    
    st.session_state.cost_v2_advisor_notes = notes
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_footer_navigation():
    """Render fixed footer navigation."""
    
    st.markdown("---")
    
    # Footer with auto-save message
    st.caption("✅ Your progress is automatically saved")
    
    # Three-column layout for buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Review Modules", use_container_width=True, key="review_modules_btn"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col2:
        if st.button("✅ Finalize & Continue", use_container_width=True, type="primary", key="finalize_btn"):
            st.session_state.cost_v2_step = "exit"
            st.rerun()
    
    with col3:
        if st.button("🏠 Return to Hub", use_container_width=True, key="return_hub_btn"):
            from core.nav import route_to
            route_to("hub_concierge")
