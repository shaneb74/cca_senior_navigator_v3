"""Expert Review Step - Cost Planner v2

Aggregates all financial module data and presents comprehensive summary
for review. Allows advisor notes and prepares for PFMA handoff.

This is the penultimate step before exit/completion.
"""

from typing import Dict, Optional
import streamlit as st
from datetime import datetime


def render():
    """Render expert review step with comprehensive financial summary.
    
    Displays:
    - Care recommendation context (from GCP)
    - Complete financial summary (from 3 modules)
    - Gap analysis with visual indicators
    - Runway projection
    - Advisor notes section (optional)
    - Actions: Review Modules, Finalize & Continue, Return to Hub
    """
    
    st.markdown("# 📋 Expert Advisor Review")
    
    # Get all module data
    modules = st.session_state.get("cost_v2_modules", {})
    
    # Check if required modules are complete (Income & Assets is required)
    income_data = modules.get("income_assets", {}).get("data", {})
    
    if not income_data:
        st.error("⚠️ **Income & Assets module is required.** Please complete it before accessing Expert Review.")
        if st.button("← Back to Financial Modules"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
        return
    
    # Get other module data (may be incomplete)
    costs_data = modules.get("monthly_costs", {}).get("data", {})
    coverage_data = modules.get("coverage", {}).get("data", {})
    
    # Show warning if other modules incomplete
    if not costs_data or not coverage_data:
        st.warning("""
        ⚠️ **Some modules are incomplete.** 
        
        For the most accurate financial plan, we recommend completing all modules:
        - Income & Assets ✅
        - Monthly Costs """ + ("✅" if costs_data else "❌") + """
        - Coverage & Benefits """ + ("✅" if coverage_data else "❌") + """
        
        You can continue with Expert Review, but estimates may be less accurate.
        """)
    
    # Get care recommendation from MCIP (if available)
    from core.mcip import MCIP
    recommendation = MCIP.get_care_recommendation()
    
    # Show care context
    if recommendation:
        _render_care_context(recommendation)
    
    st.markdown("---")
    
    # Summary sections
    _render_executive_summary(income_data, costs_data, coverage_data)
    
    st.markdown("---")
    
    # Detailed breakdown in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Financial Overview",
        "💰 Monthly Costs",
        "🛡️ Coverage & Benefits",
        "📈 Projections"
    ])
    
    with tab1:
        _render_financial_overview(income_data, costs_data, coverage_data)
    
    with tab2:
        _render_monthly_costs_detail(costs_data)
    
    with tab3:
        _render_coverage_detail(coverage_data)
    
    with tab4:
        _render_projections(income_data, costs_data, coverage_data)
    
    st.markdown("---")
    
    # Advisor notes section (optional)
    _render_advisor_notes()
    
    st.markdown("---")
    
    # Action buttons
    _render_actions()


def _render_care_context(recommendation):
    """Show care recommendation context from GCP."""
    tier_label = recommendation.tier.replace("_", " ").title()
    confidence_pct = int(recommendation.confidence * 100)
    
    st.info(f"""
    **Based on your Guided Care Plan:**
    - 🎯 Recommended Care Level: **{tier_label}**
    - 📊 Confidence: {confidence_pct}%
    
    The financial plan below is tailored to **{tier_label}** care costs.
    """)


def _render_executive_summary(income_data: Dict, costs_data: Dict, coverage_data: Dict):
    """Render executive summary with key metrics."""
    
    st.markdown("### 📊 Executive Summary")
    
    # Calculate key metrics
    total_monthly_income = income_data.get("total_monthly_income", 0)
    total_assets = income_data.get("total_assets", 0)
    total_monthly_cost = costs_data.get("total_monthly_cost", 0)
    total_coverage = coverage_data.get("total_coverage", 0)
    
    monthly_gap = total_monthly_cost - total_coverage - total_monthly_income
    coverage_percentage = int((total_coverage / total_monthly_cost * 100)) if total_monthly_cost > 0 else 0
    
    # Financial runway
    if monthly_gap > 0 and total_assets > 0:
        runway_months = int(total_assets / monthly_gap)
        runway_years = runway_months / 12
    else:
        runway_months = 999
        runway_years = 999
    
    # Display in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Monthly Care Cost",
            value=f"${total_monthly_cost:,.0f}",
            help="Total estimated monthly care costs"
        )
    
    with col2:
        st.metric(
            label="Coverage & Income",
            value=f"${total_coverage + total_monthly_income:,.0f}",
            help="Total monthly coverage from all sources"
        )
    
    with col3:
        if monthly_gap > 0:
            st.metric(
                label="Monthly Gap",
                value=f"${monthly_gap:,.0f}",
                delta=f"-${monthly_gap:,.0f}",
                delta_color="inverse",
                help="Monthly shortfall to cover from assets"
            )
        else:
            surplus = abs(monthly_gap)
            st.metric(
                label="Monthly Surplus",
                value=f"${surplus:,.0f}",
                delta=f"+${surplus:,.0f}",
                delta_color="normal",
                help="Monthly surplus after all expenses"
            )
    
    with col4:
        if runway_years < 999:
            years_label = f"{runway_years:.1f} years"
            if runway_years < 2:
                delta_color = "inverse"
            elif runway_years < 5:
                delta_color = "off"
            else:
                delta_color = "normal"
            
            st.metric(
                label="Financial Runway",
                value=years_label,
                help="Estimated time until assets depleted"
            )
        else:
            st.metric(
                label="Financial Runway",
                value="Unlimited",
                help="Sufficient income to cover all costs"
            )
    
    # Gap indicator
    if monthly_gap > 0:
        gap_pct = int((monthly_gap / total_monthly_cost) * 100)
        if gap_pct > 50:
            st.error(f"⚠️ **Significant Funding Gap:** ${monthly_gap:,.0f}/month ({gap_pct}% of total cost)")
            st.markdown("💡 **Recommendation:** Schedule consultation with financial advisor to explore additional funding options.")
        elif gap_pct > 25:
            st.warning(f"⚠️ **Moderate Funding Gap:** ${monthly_gap:,.0f}/month ({gap_pct}% of total cost)")
            st.markdown("💡 **Recommendation:** Review asset liquidation timeline and consider cost-reduction strategies.")
        else:
            st.info(f"ℹ️ **Minor Funding Gap:** ${monthly_gap:,.0f}/month ({gap_pct}% of total cost)")
            st.markdown("💡 **Recommendation:** Monitor expenses and optimize coverage sources.")
    else:
        st.success(f"✅ **Fully Funded:** All care costs covered by income and benefits!")


def _render_financial_overview(income_data: Dict, costs_data: Dict, coverage_data: Dict):
    """Render detailed financial overview."""
    
    st.markdown("### Income Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Monthly Income:**")
        ss_income = income_data.get("ss_monthly", 0)
        pension_income = income_data.get("pension_monthly", 0)
        other_income = income_data.get("other_income", 0)
        total_income = income_data.get("total_monthly_income", 0)
        
        if ss_income > 0:
            st.markdown(f"- Social Security: ${ss_income:,.0f}")
        if pension_income > 0:
            st.markdown(f"- Pension: ${pension_income:,.0f}")
        if other_income > 0:
            st.markdown(f"- Other Income: ${other_income:,.0f}")
        
        st.markdown(f"**Total Monthly: ${total_income:,.0f}**")
    
    with col2:
        st.markdown("**Available Assets:**")
        liquid = income_data.get("liquid_assets", 0)
        property_val = income_data.get("property_value", 0)
        retirement = income_data.get("retirement_accounts", 0)
        other_assets = income_data.get("other_assets", 0)
        total_assets = income_data.get("total_assets", 0)
        
        if liquid > 0:
            st.markdown(f"- Liquid Assets: ${liquid:,.0f}")
        if property_val > 0:
            st.markdown(f"- Property Value: ${property_val:,.0f}")
        if retirement > 0:
            st.markdown(f"- Retirement Accounts: ${retirement:,.0f}")
        if other_assets > 0:
            st.markdown(f"- Other Assets: ${other_assets:,.0f}")
        
        st.markdown(f"**Total Assets: ${total_assets:,.0f}**")


def _render_monthly_costs_detail(costs_data: Dict):
    """Render detailed monthly costs breakdown."""
    
    st.markdown("### Cost Breakdown")
    
    base_cost = costs_data.get("base_care_cost", 0)
    monthly_care_cost = costs_data.get("monthly_care_cost", 0)
    additional_services = costs_data.get("additional_services_cost", 0)
    total_cost = costs_data.get("total_monthly_cost", 0)
    
    # Base care
    st.markdown(f"**Base Care Cost:** ${base_cost:,.0f}/month")
    
    # Care hours (if in-home)
    care_hours = costs_data.get("care_hours_per_week")
    if care_hours and care_hours > 0:
        hourly_rate = costs_data.get("hourly_rate", 25)
        st.markdown(f"- Care hours: {care_hours} hours/week @ ${hourly_rate:.2f}/hour")
        st.markdown(f"- Monthly care cost: ${monthly_care_cost:,.0f}")
    
    # Regional adjustment
    regional_multiplier = costs_data.get("regional_multiplier")
    if regional_multiplier and regional_multiplier != 1.0:
        pct_diff = int((regional_multiplier - 1.0) * 100)
        if pct_diff > 0:
            st.info(f"📍 Regional adjustment: +{pct_diff}% higher than national average")
        else:
            st.success(f"📍 Regional adjustment: {pct_diff}% lower than national average")
    
    # Additional services
    if additional_services > 0:
        st.markdown(f"**Additional Services:** ${additional_services:,.0f}/month")
        selected_services = costs_data.get("selected_services", [])
        if selected_services:
            for service in selected_services:
                st.markdown(f"- {service}")
    
    st.markdown(f"### **Total Monthly Cost: ${total_cost:,.0f}**")
    st.markdown(f"**Annual Cost: ${total_cost * 12:,.0f}**")


def _render_coverage_detail(coverage_data: Dict):
    """Render detailed coverage breakdown."""
    
    st.markdown("### Coverage Sources")
    
    ltc_benefit = coverage_data.get("ltc_monthly_benefit", 0)
    va_benefit = coverage_data.get("va_monthly_benefit", 0)
    medicare = coverage_data.get("medicare_coverage", 0)
    medicaid = coverage_data.get("medicaid_coverage", 0)
    other_coverage = coverage_data.get("other_coverage", 0)
    total_coverage = coverage_data.get("total_coverage", 0)
    
    if ltc_benefit > 0:
        st.markdown(f"**Long-Term Care Insurance:** ${ltc_benefit:,.0f}/month")
        ltc_daily = coverage_data.get("ltc_daily_benefit", 0)
        ltc_max_days = coverage_data.get("ltc_max_benefit_days", 0)
        if ltc_daily > 0:
            st.caption(f"Daily benefit: ${ltc_daily:.0f} | Max days: {ltc_max_days}")
    
    if va_benefit > 0:
        st.markdown(f"**VA Aid & Attendance:** ${va_benefit:,.0f}/month")
        va_category = coverage_data.get("va_benefit_category", "")
        if va_category:
            st.caption(f"Category: {va_category}")
    
    if medicare > 0:
        st.markdown(f"**Medicare Coverage:** ${medicare:,.0f}/month")
    
    if medicaid > 0:
        st.markdown(f"**Medicaid Coverage:** ${medicaid:,.0f}/month")
    
    if other_coverage > 0:
        st.markdown(f"**Other Insurance:** ${other_coverage:,.0f}/month")
    
    st.markdown(f"### **Total Coverage: ${total_coverage:,.0f}/month**")


def _render_projections(income_data: Dict, costs_data: Dict, coverage_data: Dict):
    """Render long-term financial projections."""
    
    st.markdown("### Long-Term Projections")
    
    total_monthly_income = income_data.get("total_monthly_income", 0)
    total_assets = income_data.get("total_assets", 0)
    total_monthly_cost = costs_data.get("total_monthly_cost", 0)
    total_coverage = coverage_data.get("total_coverage", 0)
    
    monthly_gap = total_monthly_cost - total_coverage - total_monthly_income
    
    # Annual projection
    annual_cost = total_monthly_cost * 12
    annual_coverage = total_coverage * 12
    annual_income = total_monthly_income * 12
    annual_gap = monthly_gap * 12
    
    st.markdown("#### 1-Year Projection")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Annual Costs", f"${annual_cost:,.0f}")
    with col2:
        st.metric("Annual Coverage + Income", f"${annual_coverage + annual_income:,.0f}")
    with col3:
        if annual_gap > 0:
            st.metric("Annual Gap", f"${annual_gap:,.0f}", delta=f"-${annual_gap:,.0f}", delta_color="inverse")
        else:
            st.metric("Annual Surplus", f"${abs(annual_gap):,.0f}", delta=f"+${abs(annual_gap):,.0f}")
    
    # 3-year projection (with inflation)
    st.markdown("#### 3-Year Projection (3% annual inflation)")
    three_year_cost = annual_cost * 3 * 1.03
    three_year_gap = annual_gap * 3 * 1.03 if annual_gap > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("3-Year Total Costs", f"${three_year_cost:,.0f}")
    with col2:
        if three_year_gap > 0:
            st.metric("3-Year Gap from Assets", f"${three_year_gap:,.0f}")
            remaining = total_assets - three_year_gap
            if remaining > 0:
                st.success(f"Remaining assets after 3 years: ${remaining:,.0f}")
            else:
                st.error(f"⚠️ Assets insufficient for 3 years (shortfall: ${abs(remaining):,.0f})")
    
    # 5-year projection
    st.markdown("#### 5-Year Projection (5% total inflation)")
    five_year_cost = annual_cost * 5 * 1.05
    five_year_gap = annual_gap * 5 * 1.05 if annual_gap > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("5-Year Total Costs", f"${five_year_cost:,.0f}")
    with col2:
        if five_year_gap > 0:
            st.metric("5-Year Gap from Assets", f"${five_year_gap:,.0f}")
            remaining = total_assets - five_year_gap
            if remaining > 0:
                st.success(f"Remaining assets after 5 years: ${remaining:,.0f}")
            else:
                st.error(f"⚠️ Assets insufficient for 5 years (shortfall: ${abs(remaining):,.0f})")


def _render_advisor_notes():
    """Render advisor notes section (optional)."""
    
    st.markdown("### 📝 Advisor Notes (Optional)")
    
    # Initialize notes in session state
    if "cost_v2_advisor_notes" not in st.session_state:
        st.session_state.cost_v2_advisor_notes = ""
    
    notes = st.text_area(
        "Add notes or recommendations for your financial advisor:",
        value=st.session_state.cost_v2_advisor_notes,
        height=150,
        placeholder="E.g., 'Would like to discuss Medicaid planning options' or 'Interested in annuity products to extend runway'",
        key="advisor_notes_input"
    )
    
    st.session_state.cost_v2_advisor_notes = notes
    
    if notes:
        st.caption(f"✍️ Notes saved: {len(notes)} characters")


def _render_actions():
    """Render action buttons."""
    
    st.markdown("### 🎯 Next Steps")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("� Review Modules", use_container_width=True, key="review_modules"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col2:
        if st.button("✅ Finalize & Continue", use_container_width=True, type="primary", key="finalize_continue"):
            # Mark plan complete and go to exit
            st.session_state.cost_v2_step = "exit"
            st.rerun()
    
    with col3:
        if st.button("🏠 Return to Hub", use_container_width=True, key="return_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
