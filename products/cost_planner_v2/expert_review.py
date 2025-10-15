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
    
    # Check if required modules are complete (Income & Assets are required)
    income_data = modules.get("income", {}).get("data", {})
    assets_data = modules.get("assets", {}).get("data", {})
    
    if not income_data or not assets_data:
        st.error("⚠️ **Income & Assets modules are required.** Please complete them before accessing Expert Review.")
        if st.button("← Back to Financial Modules"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
        return
    
    # Get optional module data
    va_data = modules.get("va_benefits", {}).get("data", {})
    insurance_data = modules.get("health_insurance", {}).get("data", {})
    life_insurance_data = modules.get("life_insurance", {}).get("data", {})
    medicaid_data = modules.get("medicaid_navigation", {}).get("data", {})
    
    # Aggregate new 6-module data into old 3-module format for backward compatibility
    # This allows the rest of the file to work without major rewrites
    aggregated_income_assets = {
        # Income fields
        "total_monthly_income": (
            income_data.get("ss_monthly", 0) +
            income_data.get("pension_monthly", 0) +
            income_data.get("employment_monthly", 0) +
            income_data.get("investment_monthly", 0) +
            income_data.get("other_monthly", 0) +
            (va_data.get("va_disability_monthly", 0) if va_data else 0) +
            (va_data.get("aid_attendance_monthly", 0) if va_data else 0)
        ),
        # Asset fields
        "total_assets": (
            assets_data.get("checking_savings", 0) +
            assets_data.get("cds_money_market", 0) +
            assets_data.get("ira_traditional", 0) +
            assets_data.get("ira_roth", 0) +
            assets_data.get("k401_403b", 0) +
            assets_data.get("other_retirement", 0) +
            assets_data.get("stocks_bonds", 0) +
            assets_data.get("mutual_funds", 0) +
            assets_data.get("investment_property", 0) +
            assets_data.get("business_value", 0) +
            assets_data.get("other_assets_value", 0)
        ),
        # Keep original data for detailed views
        "_income_data": income_data,
        "_assets_data": assets_data,
        "_va_data": va_data
    }
    
    # Monthly costs - use MCIP financial profile if available
    from core.mcip import MCIP
    estimated_monthly_cost = 0
    recommendation = MCIP.get_care_recommendation()
    
    # Try to get cost from financial profile first
    financial_profile = MCIP.get_financial_profile()
    if financial_profile and hasattr(financial_profile, 'estimated_monthly_cost'):
        estimated_monthly_cost = financial_profile.estimated_monthly_cost
    elif recommendation:
        # Fallback: use tier-based defaults if no financial profile yet
        tier_defaults = {
            'independent': 2500,
            'in_home': 4500,
            'assisted_living': 5000,
            'memory_care': 7000,
            'memory_care_high_acuity': 9000
        }
        estimated_monthly_cost = tier_defaults.get(recommendation.tier, 5000)
    
    aggregated_costs = {
        "total_monthly_cost": estimated_monthly_cost,
        "_source": "mcip" if estimated_monthly_cost > 0 else "estimated"
    }
    
    # Coverage - aggregate from insurance modules
    aggregated_coverage = {
        "total_coverage": (
            (insurance_data.get("ltc_daily_benefit", 0) * 30 if insurance_data and insurance_data.get("has_ltc_insurance") else 0) +
            (life_insurance_data.get("monthly_benefit", 0) if life_insurance_data else 0)
        ),
        "has_medicare": insurance_data.get("has_medicare", False) if insurance_data else False,
        "has_ltc_insurance": insurance_data.get("has_ltc_insurance", False) if insurance_data else False,
        "_insurance_data": insurance_data,
        "_life_insurance_data": life_insurance_data,
        "_medicaid_data": medicaid_data
    }
    
    # Show warning if optional modules incomplete
    optional_count = sum([bool(va_data), bool(insurance_data), bool(life_insurance_data), bool(medicaid_data)])
    if optional_count < 4:
        st.warning(f"""
        ⚠️ **Some optional modules are incomplete ({optional_count}/4 completed).** 
        
        For the most comprehensive financial plan, consider completing:
        - Income ✅
        - Assets ✅
        - VA Benefits """ + ("✅" if va_data else "❌") + """
        - Health Insurance """ + ("✅" if insurance_data else "❌") + """
        - Life Insurance """ + ("✅" if life_insurance_data else "❌") + """
        - Medicaid Navigation """ + ("✅" if medicaid_data else "❌") + """
        
        You can continue with Expert Review, but estimates may be less comprehensive.
        """)
    
    # Show care context
    if recommendation:
        _render_care_context(recommendation)
    
    st.markdown("---")
    
    # Summary sections - use aggregated data
    _render_executive_summary(aggregated_income_assets, aggregated_costs, aggregated_coverage)
    
    st.markdown("---")
    
    # Detailed breakdown in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Financial Overview",
        "💰 Monthly Costs",
        "🛡️ Coverage & Benefits",
        "📈 Projections"
    ])
    
    with tab1:
        _render_financial_overview(aggregated_income_assets, aggregated_costs, aggregated_coverage)
    
    with tab2:
        _render_monthly_costs_detail(aggregated_costs)
    
    with tab3:
        _render_coverage_detail(aggregated_coverage)
    
    with tab4:
        _render_projections(aggregated_income_assets, aggregated_costs, aggregated_coverage)
    
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
    
    # Cost adjustments table (flag-based add-ons)
    _render_cost_adjustments_table()
    
    # Additional services
    if additional_services > 0:
        st.markdown(f"**Additional Services:** ${additional_services:,.0f}/month")
        selected_services = costs_data.get("selected_services", [])
        if selected_services:
            for service in selected_services:
                st.markdown(f"- {service}")
    
    st.markdown(f"### **Total Monthly Cost: ${total_cost:,.0f}**")
    st.markdown(f"**Annual Cost: ${total_cost * 12:,.0f}**")


def _render_cost_adjustments_table():
    """Render cost adjustments table showing flag-based add-ons.
    
    Displays:
    - Condition label
    - Add-on percentage
    - Monthly increase amount
    - Rationale
    """
    from core.mcip import MCIP
    from products.cost_planner_v2.utils.cost_calculator import CostCalculator
    
    # Get GCP flags
    recommendation = MCIP.get_care_recommendation()
    if not recommendation or not recommendation.flags:
        return  # No flags, no adjustments
    
    flags = [f.get('id') if isinstance(f, dict) else f for f in recommendation.flags]
    care_tier = recommendation.tier
    
    # Get base cost (before adjustments)
    modules = st.session_state.get("cost_v2_modules", {})
    costs_data = modules.get("monthly_costs", {}).get("data", {})
    base_cost = costs_data.get("base_care_cost", 0)
    
    # Get regional multiplier
    regional_multiplier = costs_data.get("regional_multiplier", 1.0)
    base_with_regional = base_cost * regional_multiplier
    
    # Get active adjustments
    adjustments = CostCalculator.get_active_adjustments(flags, care_tier, base_with_regional)
    
    if not adjustments:
        return  # No adjustments applied
    
    st.markdown("---")
    st.markdown("### 💡 Care Complexity Adjustments")
    st.caption("Based on your Guided Care Plan, these factors increase the cost of care:")
    
    # Build table HTML
    table_html = """
    <style>
    .cost-adjustments-table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 14px;
    }
    .cost-adjustments-table th {
        background: #f1f5f9;
        color: #0f172a;
        font-weight: 700;
        padding: 12px;
        text-align: left;
        border-bottom: 2px solid #cbd5e1;
    }
    .cost-adjustments-table td {
        padding: 12px;
        border-bottom: 1px solid #e2e8f0;
        vertical-align: top;
    }
    .cost-adjustments-table tr:hover {
        background: #f8fafc;
    }
    .adjustment-label {
        font-weight: 600;
        color: #0f172a;
    }
    .adjustment-percentage {
        color: #dc2626;
        font-weight: 600;
    }
    .adjustment-amount {
        color: #0f172a;
        font-weight: 600;
    }
    .adjustment-rationale {
        color: #64748b;
        font-size: 13px;
        line-height: 1.5;
    }
    </style>
    <table class="cost-adjustments-table">
        <thead>
            <tr>
                <th>Condition</th>
                <th style="text-align: right;">Add-On %</th>
                <th style="text-align: right;">Monthly Increase</th>
                <th>Rationale</th>
            </tr>
        </thead>
        <tbody>
    """
    
    total_increase = 0
    for adj in adjustments:
        table_html += f"""
            <tr>
                <td class="adjustment-label">{adj['label']}</td>
                <td class="adjustment-percentage" style="text-align: right;">+{adj['percentage']:.0f}%</td>
                <td class="adjustment-amount" style="text-align: right;">${adj['amount']:,.0f}</td>
                <td class="adjustment-rationale">{adj['rationale']}</td>
            </tr>
        """
        total_increase += adj['amount']
    
    # Add total row
    table_html += f"""
        </tbody>
        <tfoot>
            <tr style="font-weight: 700; background: #fef3c7; border-top: 2px solid #fde68a;">
                <td>Total Adjustments</td>
                <td></td>
                <td style="text-align: right; color: #dc2626;">+${total_increase:,.0f}/mo</td>
                <td style="color: #78350f;">Cumulative impact from all conditions</td>
            </tr>
        </tfoot>
    </table>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Show explanation
    st.info("""
    **Why these adjustments?** 
    
    Care costs increase with complexity. Each condition requires additional staff time, specialized training, 
    or enhanced safety measures. These percentages reflect real-world care cost data and are applied 
    cumulatively (each builds on the previous adjustment).
    """)
    
    st.markdown("---")


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
    """Render long-term financial projections with detailed timeline."""
    
    st.markdown("### 📈 Financial Timeline & Asset Runway")
    
    total_monthly_income = income_data.get("total_monthly_income", 0)
    total_assets = income_data.get("total_assets", 0)
    total_monthly_cost = costs_data.get("total_monthly_cost", 0)
    total_coverage = coverage_data.get("total_coverage", 0)
    
    monthly_gap = total_monthly_cost - total_coverage - total_monthly_income
    
    # Show key metrics at the top
    st.markdown("#### Key Financial Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Monthly Care Cost", f"${total_monthly_cost:,.0f}")
    with col2:
        st.metric("Monthly Coverage + Income", f"${total_coverage + total_monthly_income:,.0f}")
    with col3:
        if monthly_gap > 0:
            st.metric("Monthly Gap", f"${monthly_gap:,.0f}", delta=f"-${monthly_gap:,.0f}", delta_color="inverse")
        else:
            st.metric("Monthly Surplus", f"${abs(monthly_gap):,.0f}", delta=f"+${abs(monthly_gap):,.0f}")
    with col4:
        st.metric("Available Assets", f"${total_assets:,.0f}")
    
    st.markdown("---")
    
    # Calculate asset runway with 3% annual inflation
    if monthly_gap > 0 and total_assets > 0:
        st.markdown("#### 📊 Asset Runway Timeline (30-Year Projection)")
        st.markdown("""
        This timeline shows how long your assets will last to cover the monthly gap between 
        care costs and your income/coverage. **Includes 3% annual inflation on care costs.**
        """)
        
        # Calculate year-by-year projections with inflation
        inflation_rate = 0.03  # 3% annual inflation
        remaining_assets = total_assets
        years_data = []
        assets_depleted_year = None
        
        for year in range(1, 31):  # Cap at 30 years
            # Calculate inflated monthly gap for this year
            inflation_multiplier = (1 + inflation_rate) ** year
            inflated_monthly_gap = monthly_gap * inflation_multiplier
            annual_gap = inflated_monthly_gap * 12
            
            # Calculate remaining assets
            remaining_assets -= annual_gap
            
            years_data.append({
                "year": year,
                "annual_cost": total_monthly_cost * 12 * inflation_multiplier,
                "annual_gap": annual_gap,
                "remaining_assets": max(0, remaining_assets)
            })
            
            # Track when assets are depleted
            if remaining_assets <= 0 and assets_depleted_year is None:
                assets_depleted_year = year
                break
        
        # Display runway summary
        if assets_depleted_year:
            st.error(f"""
            ### ⚠️ Asset Runway: {assets_depleted_year} Year{'s' if assets_depleted_year > 1 else ''}
            
            Based on current care costs, income, and coverage, your assets will be depleted in **Year {assets_depleted_year}**.
            """)
        else:
            st.success(f"""
            ### ✅ Asset Runway: 30+ Years
            
            Your assets are projected to last **beyond 30 years** at current care costs with 3% annual inflation.
            """)
        
        # Create timeline table
        st.markdown("#### Year-by-Year Financial Timeline")
        
        # Show first 10 years or until depletion
        display_years = min(len(years_data), 10) if not assets_depleted_year else min(len(years_data), assets_depleted_year + 2)
        
        timeline_html = """
        <table style="width:100%; border-collapse: collapse; margin-top: 1rem;">
            <thead style="background-color: #f0f2f6;">
                <tr>
                    <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Year</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Annual Care Cost</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Gap from Assets</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Remaining Assets</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Status</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, data in enumerate(years_data[:display_years]):
            year = data["year"]
            annual_cost = data["annual_cost"]
            annual_gap = data["annual_gap"]
            remaining = data["remaining_assets"]
            
            # Status indicator
            if remaining <= 0:
                status = "🔴 Depleted"
                row_color = "#ffebee"
            elif remaining < annual_gap * 2:
                status = "🟡 Critical"
                row_color = "#fff9e6"
            else:
                status = "🟢 Covered"
                row_color = "#e8f5e9" if i % 2 == 0 else "#ffffff"
            
            timeline_html += f"""
            <tr style="background-color: {row_color};">
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Year {year}</strong></td>
                <td style="padding: 10px; text-align: right; border: 1px solid #ddd;">${annual_cost:,.0f}</td>
                <td style="padding: 10px; text-align: right; border: 1px solid #ddd; color: #d32f2f;">${annual_gap:,.0f}</td>
                <td style="padding: 10px; text-align: right; border: 1px solid #ddd;"><strong>${remaining:,.0f}</strong></td>
                <td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{status}</td>
            </tr>
            """
        
        timeline_html += """
            </tbody>
        </table>
        """
        
        st.markdown(timeline_html, unsafe_allow_html=True)
        
        if len(years_data) > display_years:
            with st.expander(f"📋 View Full {len(years_data)}-Year Timeline"):
                full_timeline_html = """
                <table style="width:100%; border-collapse: collapse;">
                    <thead style="background-color: #f0f2f6;">
                        <tr>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Year</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Annual Care Cost</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Gap from Assets</th>
                            <th style="padding: 12px; text-align: right; border: 1px solid #ddd;">Remaining Assets</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for data in years_data:
                    full_timeline_html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">Year {data['year']}</td>
                        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">${data['annual_cost']:,.0f}</td>
                        <td style="padding: 8px; text-align: right; border: 1px solid #ddd; color: #d32f2f;">${data['annual_gap']:,.0f}</td>
                        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;">${data['remaining_assets']:,.0f}</td>
                    </tr>
                    """
                
                full_timeline_html += """
                    </tbody>
                </table>
                """
                st.markdown(full_timeline_html, unsafe_allow_html=True)
        
        # Add recommendations
        st.markdown("---")
        st.markdown("#### 💡 Planning Recommendations")
        
        if assets_depleted_year and assets_depleted_year <= 5:
            st.error("""
            **🚨 Immediate Action Needed**
            - Consider Medicaid planning and asset protection strategies
            - Explore additional insurance coverage options
            - Review care level alternatives that may reduce costs
            - Consult with a financial advisor and elder law attorney
            """)
        elif assets_depleted_year and assets_depleted_year <= 10:
            st.warning("""
            **⚠️ Plan Ahead**
            - Begin exploring long-term financing options
            - Consider annuity products to extend runway
            - Investigate VA benefits if eligible
            - Review insurance coverage adequacy
            """)
        else:
            st.info("""
            **✅ Strong Financial Position**
            - Continue monitoring costs and adjusting plans as needed
            - Consider setting aside additional reserves for unexpected costs
            - Keep insurance policies current and adequate
            - Review this plan annually as health needs change
            """)
    
    elif monthly_gap <= 0:
        st.success("""
        ### ✅ Fully Covered Care Costs
        
        Your monthly income and coverage **fully cover** your care costs with no asset depletion needed!
        Your assets will remain intact and may continue to grow.
        """)
        
        surplus = abs(monthly_gap) * 12
        st.metric("Annual Surplus", f"${surplus:,.0f}", delta=f"+${surplus:,.0f}")
    
    else:
        st.warning("""
        ### ⚠️ Insufficient Data
        
        Please complete all financial modules to calculate an accurate asset runway timeline.
        """)


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
