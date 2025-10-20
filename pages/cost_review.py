"""
Cost Planner Assessment Review Page

Read-only view of all Cost Planner responses and data.
Shows complete financial assessment with clean, organized display.

Access: Available after completing Cost Planner
Route: ?page=cost_review
"""

import streamlit as st
from core.mcip import MCIP
from core.ui import img_src


def render():
    """Render Cost Planner review page."""
    
    # Check if Cost Planner is complete (check both cost_v2 and legacy cost_planner)
    is_complete = MCIP.is_product_complete("cost_v2") or MCIP.is_product_complete("cost_planner")
    
    # Also check if we have financial profile data
    has_financial_data = MCIP.get_financial_profile() is not None
    
    if not is_complete and not has_financial_data:
        st.warning("⚠️ Complete the Cost Planner first to view your assessment review.")
        if st.button("← Back to Concierge", key="review_back_incomplete"):
            st.query_params["page"] = "hub_concierge"
            st.rerun()
        return
    
    # Get all Cost Planner data from session state
    quick_estimate = st.session_state.get("cost_v2_quick_estimate", {})
    qualifiers = st.session_state.get("cost_v2_qualifiers", {})
    
    # Get assessment data - check both new format (cost_planner_v2_*) and legacy format (cost_v2_modules)
    # New format (active assessments)
    income_data = st.session_state.get("cost_planner_v2_income", {})
    assets_data = st.session_state.get("cost_planner_v2_assets", {})
    va_benefits_data = st.session_state.get("cost_planner_v2_va_benefits", {})
    health_insurance_data = st.session_state.get("cost_planner_v2_health_insurance", {})
    life_insurance_data = st.session_state.get("cost_planner_v2_life_insurance", {})
    medicaid_data = st.session_state.get("cost_planner_v2_medicaid", {})
    
    # Legacy format (demo profiles) - fallback if new format is empty
    if not income_data or not assets_data:
        cost_v2_modules = st.session_state.get("cost_v2_modules", {})
        if not income_data and "income" in cost_v2_modules:
            income_data = cost_v2_modules["income"].get("data", {})
        if not assets_data and "assets" in cost_v2_modules:
            assets_data = cost_v2_modules["assets"].get("data", {})
        if not va_benefits_data and "va_benefits" in cost_v2_modules:
            va_benefits_data = cost_v2_modules["va_benefits"].get("data", {})
        if not health_insurance_data and "health_insurance" in cost_v2_modules:
            health_insurance_data = cost_v2_modules["health_insurance"].get("data", {})
        if not life_insurance_data and "life_insurance" in cost_v2_modules:
            life_insurance_data = cost_v2_modules["life_insurance"].get("data", {})
        if not medicaid_data and "medicaid" in cost_v2_modules:
            medicaid_data = cost_v2_modules["medicaid"].get("data", {})
    
    # Get expert review analysis
    product_summary = MCIP.get_product_summary("cost_v2")
    
    # Render Navi guidance banner
    _render_navi_guidance(product_summary)
    
    # Page header
    st.markdown('<div class="sn-app module-container">', unsafe_allow_html=True)
    st.markdown(
        '<div class="mod-head"><div class="mod-head-row">'
        '<h2 class="h2">💰 Cost Planner Review</h2>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    
    # Summary section
    _render_summary_section(product_summary)
    
    st.markdown("---")
    
    # Financial Timeline & Runway section
    financial_profile = MCIP.get_financial_profile()
    if financial_profile:
        _render_financial_timeline_section(financial_profile, income_data, assets_data)
        st.markdown("---")
    
    # Quick Estimate section
    if quick_estimate:
        _render_quick_estimate_section(quick_estimate)
        st.markdown("---")
    
    # Qualifiers section
    if qualifiers:
        _render_qualifiers_section(qualifiers)
        st.markdown("---")
    
    # Financial Assessments sections
    st.markdown("### 📊 Financial Assessment Details")
    st.markdown("")
    
    # Income
    if income_data:
        _render_income_section(income_data)
        st.markdown("")
    
    # Assets
    if assets_data:
        _render_assets_section(assets_data)
        st.markdown("")
    
    # VA Benefits
    if va_benefits_data:
        _render_va_benefits_section(va_benefits_data)
        st.markdown("")
    
    # Health Insurance
    if health_insurance_data:
        _render_health_insurance_section(health_insurance_data)
        st.markdown("")
    
    # Life Insurance
    if life_insurance_data:
        _render_life_insurance_section(life_insurance_data)
        st.markdown("")
    
    # Medicaid
    if medicaid_data:
        _render_medicaid_section(medicaid_data)
        st.markdown("")
    
    st.markdown("---")
    
    # Navigation buttons
    _render_navigation()
    
    st.markdown("</div>", unsafe_allow_html=True)


def _render_navi_guidance(product_summary):
    """Render Navi-style guidance banner."""
    summary_line = product_summary.get("summary_line", "Financial assessment complete") if product_summary else "Financial assessment complete"
    
    # Simple Navi-style banner (using string concatenation to avoid f-string issues)
    banner_html = (
        '<div style="background: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px 20px; margin-bottom: 24px;">'
        '    <div style="display: flex; align-items: start; gap: 12px;">'
        '        <span style="font-size: 24px;">💰</span>'
        '        <div style="flex: 1;">'
        '            <div style="font-weight: 700; color: #1e40af; font-size: 16px; margin-bottom: 4px;">Your Financial Assessment</div>'
        '            <div style="color: #1e3a8a; font-size: 14px; line-height: 1.5;">'
        '                ' + summary_line + '. This page shows all the information you provided in your Cost Planner assessment.'
        '            </div>'
        '        </div>'
        '    </div>'
        '</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)


def _render_summary_section(product_summary):
    """Render summary of expert review results."""
    st.markdown("### 📋 Financial Review Summary")
    
    if product_summary and product_summary.get("summary_line"):
        st.markdown(f"**Result:** {product_summary['summary_line']}")
    
    # Add any additional summary info from expert review
    if product_summary and product_summary.get("details"):
        details = product_summary["details"]
        if isinstance(details, dict):
            if "coverage_tier" in details:
                tier_display = {
                    "excellent": "Excellent Coverage ✅",
                    "good": "Good Coverage 👍",
                    "moderate": "Moderate Coverage ⚠️",
                    "limited": "Limited Coverage ⚠️",
                    "critical": "Critical Gap ❗"
                }
                tier_text = tier_display.get(details["coverage_tier"], details["coverage_tier"])
                st.markdown(f"**Coverage Status:** {tier_text}")
            
            if "coverage_percentage" in details:
                st.markdown(f"**Income Coverage:** {details['coverage_percentage']:.0f}% of estimated care costs")


def _render_financial_timeline_section(financial_profile, income_data, assets_data):
    """Render financial timeline and runway projection."""
    with st.expander("📅 **Financial Timeline & Runway Projection**", expanded=True):
        st.markdown("#### Financial Overview")
        
        # Monthly breakdown
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**💵 Monthly Income**")
            monthly_income = income_data.get("total_monthly_income", 0)
            st.markdown(f"${monthly_income:,.2f}")
        
        with col2:
            st.markdown("**💰 Monthly Care Cost**")
            monthly_cost = financial_profile.estimated_monthly_cost
            st.markdown(f"${monthly_cost:,.2f}")
        
        with col3:
            st.markdown("**📊 Monthly Gap**")
            gap = financial_profile.gap_amount
            if gap > 0:
                st.markdown(f'<span style="color: #dc2626;">-${gap:,.2f}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span style="color: #16a34a;">${abs(gap):,.2f} surplus</span>', unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("---")
        st.markdown("")
        
        # Coverage analysis
        st.markdown("#### Coverage Analysis")
        coverage_pct = financial_profile.coverage_percentage
        
        # Progress bar for coverage
        st.markdown(f"**Income covers {coverage_pct:.1f}% of monthly care costs**")
        st.progress(min(coverage_pct / 100, 1.0))
        
        st.markdown("")
        
        # Runway projection
        st.markdown("#### 🛤️ Financial Runway")
        
        runway_months = financial_profile.runway_months
        runway_years = runway_months / 12
        
        total_assets = assets_data.get("total_asset_value", 0) or assets_data.get("net_asset_value", 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Total Available Assets**")
            st.markdown(f"${total_assets:,.2f}")
        
        with col2:
            st.markdown("**Estimated Runway**")
            if runway_years >= 1:
                st.markdown(f"**{runway_months} months** ({runway_years:.1f} years)")
            else:
                st.markdown(f"**{runway_months} months**")
        
        st.markdown("")
        
        # Runway explanation
        if gap > 0:
            annual_gap = gap * 12
            st.info(
                f"💡 **Projection:** With a monthly gap of ${gap:,.2f}, your assets can cover care costs for approximately "
                f"**{runway_years:.1f} years** before additional funding sources are needed. "
                f"This assumes an annual shortfall of ${annual_gap:,.2f}."
            )
        else:
            st.success(
                f"✅ **Excellent Position:** Your monthly income fully covers your care costs with a surplus of ${abs(gap):,.2f}. "
                f"Your assets of ${total_assets:,.2f} remain protected and can be preserved for legacy or emergency needs."
            )
        
        st.markdown("")
        st.markdown("---")
        st.markdown("")
        
        # Future projection table
        st.markdown("#### 📈 Multi-Year Projection")
        
        if gap > 0:
            # Calculate cumulative asset depletion
            projections = []
            remaining_assets = total_assets
            
            for year in [1, 3, 5, 10, 15]:
                if year * 12 <= runway_months:
                    annual_spend = gap * 12
                    assets_after = remaining_assets - (annual_spend * year)
                    projections.append({
                        "Year": f"Year {year}",
                        "Assets Remaining": f"${max(0, assets_after):,.0f}",
                        "Annual Gap": f"${annual_spend:,.0f}"
                    })
            
            if projections:
                # Create simple table
                for proj in projections:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**{proj['Year']}**")
                    with col2:
                        st.markdown(proj['Assets Remaining'])
                    with col3:
                        st.markdown(f"_Gap: {proj['Annual Gap']}_")
        else:
            st.markdown("_With income covering all costs, assets remain stable over time._")


def _render_quick_estimate_section(quick_estimate):
    """Render quick estimate initial inputs."""
    with st.expander("🗺️ **Quick Estimate** (Initial Inputs)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            if "zip_code" in quick_estimate:
                st.markdown(f"**ZIP Code:** {quick_estimate['zip_code']}")
            if "care_level" in quick_estimate:
                st.markdown(f"**Care Level:** {quick_estimate['care_level']}")
        
        with col2:
            if "estimate" in quick_estimate:
                estimate = quick_estimate["estimate"]
                if isinstance(estimate, dict):
                    monthly_cost = estimate.get("monthly_adjusted", estimate.get("monthly_base", 0))
                    st.markdown(f"**Estimated Monthly Cost:** ${monthly_cost:,.0f}")


def _render_qualifiers_section(qualifiers):
    """Render qualifier responses."""
    with st.expander("📋 **Qualifiers** (Your Situation)", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            veteran_status = "Yes ✓" if qualifiers.get("is_veteran", False) else "No"
            st.markdown(f"**Veteran Status:** {veteran_status}")
        
        with col2:
            homeowner_status = "Yes ✓" if qualifiers.get("is_homeowner", False) else "No"
            st.markdown(f"**Home Owner:** {homeowner_status}")
        
        with col3:
            medicaid_status = "Yes ✓" if qualifiers.get("is_on_medicaid", False) else "No"
            st.markdown(f"**On Medicaid:** {medicaid_status}")


def _render_income_section(income_data):
    """Render income assessment data."""
    with st.expander("💵 **Income Assessment**", expanded=False):
        if not income_data:
            st.markdown("_No income data recorded._")
            return
        
        # Check if using array format (new) or flat format (legacy)
        sources = income_data.get("income_sources", [])
        
        if sources:
            # New format: income_sources array
            st.markdown("#### Monthly Income Sources")
            for idx, source in enumerate(sources, 1):
                source_type = source.get("type", "Unknown")
                amount = source.get("amount", 0)
                st.markdown(f"{idx}. **{source_type}:** ${amount:,.2f}/month")
        else:
            # Legacy format: flat fields
            st.markdown("#### Monthly Income Sources")
            
            income_items = []
            if income_data.get("ss_monthly", 0) > 0:
                income_items.append(("Social Security", income_data["ss_monthly"]))
            if income_data.get("pension_monthly", 0) > 0:
                income_items.append(("Pension", income_data["pension_monthly"]))
            if income_data.get("retirement_distributions_monthly", 0) > 0:
                income_items.append(("Retirement Distributions", income_data["retirement_distributions_monthly"]))
            if income_data.get("employment_income", 0) > 0:
                income_items.append(("Employment Income", income_data["employment_income"]))
            if income_data.get("annuity_monthly", 0) > 0:
                income_items.append(("Annuity", income_data["annuity_monthly"]))
            if income_data.get("dividends_interest_monthly", 0) > 0:
                income_items.append(("Dividends & Interest", income_data["dividends_interest_monthly"]))
            if income_data.get("rental_income_monthly", 0) > 0:
                income_items.append(("Rental Income", income_data["rental_income_monthly"]))
            if income_data.get("alimony_support_monthly", 0) > 0:
                income_items.append(("Alimony/Support", income_data["alimony_support_monthly"]))
            if income_data.get("ltc_insurance_monthly", 0) > 0:
                income_items.append(("LTC Insurance", income_data["ltc_insurance_monthly"]))
            if income_data.get("family_support_monthly", 0) > 0:
                income_items.append(("Family Support", income_data["family_support_monthly"]))
            if income_data.get("other_income", 0) > 0:
                income_items.append(("Other Income", income_data["other_income"]))
            
            for idx, (source_name, amount) in enumerate(income_items, 1):
                st.markdown(f"{idx}. **{source_name}:** ${amount:,.2f}/month")
            
            if not income_items:
                st.markdown("_No income sources recorded._")
        
        # Total Monthly Income
        if "total_monthly_income" in income_data:
            st.markdown("")
            st.markdown(f"**Total Monthly Income:** ${income_data['total_monthly_income']:,.2f}")


def _render_assets_section(assets_data):
    """Render assets assessment data."""
    with st.expander("🏦 **Assets & Resources**", expanded=False):
        if not assets_data:
            st.markdown("_No asset data recorded._")
            return
        
        # Check if using array format (new) or flat format (legacy)
        assets = assets_data.get("assets", [])
        
        if assets:
            # New format: assets array
            st.markdown("#### Assets")
            for idx, asset in enumerate(assets, 1):
                asset_type = asset.get("type", "Unknown")
                value = asset.get("value", 0)
                debt = asset.get("debt", 0)
                st.markdown(f"{idx}. **{asset_type}:** ${value:,.2f} (Debt: ${debt:,.2f})")
        else:
            # Legacy format: flat fields organized by category
            
            # Liquid Assets
            liquid_items = []
            if assets_data.get("checking_balance", 0) > 0:
                liquid_items.append(("Checking Account", assets_data["checking_balance"]))
            if assets_data.get("savings_cds_balance", 0) > 0:
                liquid_items.append(("Savings/CDs", assets_data["savings_cds_balance"]))
            if assets_data.get("cash_on_hand", 0) > 0:
                liquid_items.append(("Cash on Hand", assets_data["cash_on_hand"]))
            
            if liquid_items:
                st.markdown("#### 💵 Liquid Assets")
                for name, value in liquid_items:
                    st.markdown(f"- **{name}:** ${value:,.2f}")
                st.markdown("")
            
            # Investments
            investment_items = []
            if assets_data.get("brokerage_stocks_bonds", 0) > 0:
                investment_items.append(("Stocks & Bonds", assets_data["brokerage_stocks_bonds"]))
            if assets_data.get("brokerage_mf_etf", 0) > 0:
                investment_items.append(("Mutual Funds/ETFs", assets_data["brokerage_mf_etf"]))
            if assets_data.get("brokerage_other", 0) > 0:
                investment_items.append(("Other Brokerage", assets_data["brokerage_other"]))
            
            if investment_items:
                st.markdown("#### 📈 Investments")
                for name, value in investment_items:
                    st.markdown(f"- **{name}:** ${value:,.2f}")
                st.markdown("")
            
            # Retirement Accounts
            retirement_items = []
            if assets_data.get("retirement_traditional", 0) > 0:
                retirement_items.append(("Traditional IRA/401(k)", assets_data["retirement_traditional"]))
            if assets_data.get("retirement_roth", 0) > 0:
                retirement_items.append(("Roth IRA/401(k)", assets_data["retirement_roth"]))
            if assets_data.get("retirement_pension_value", 0) > 0:
                retirement_items.append(("Pension Value", assets_data["retirement_pension_value"]))
            
            if retirement_items:
                st.markdown("#### 🏦 Retirement Accounts")
                for name, value in retirement_items:
                    st.markdown(f"- **{name}:** ${value:,.2f}")
                st.markdown("")
            
            # Real Estate
            real_estate_items = []
            if assets_data.get("home_equity_estimate", 0) > 0:
                real_estate_items.append(("Home Equity", assets_data["home_equity_estimate"]))
            if assets_data.get("real_estate_other", 0) > 0:
                real_estate_items.append(("Other Real Estate", assets_data["real_estate_other"]))
            
            if real_estate_items:
                st.markdown("#### 🏠 Real Estate")
                for name, value in real_estate_items:
                    st.markdown(f"- **{name}:** ${value:,.2f}")
                st.markdown("")
            
            # Life Insurance
            if assets_data.get("life_insurance_cash_value", 0) > 0:
                st.markdown("#### 💼 Life Insurance")
                st.markdown(f"- **Cash Value:** ${assets_data['life_insurance_cash_value']:,.2f}")
                st.markdown("")
        
        # Totals
        st.markdown("---")
        if "total_asset_value" in assets_data:
            st.markdown(f"**Total Asset Value:** ${assets_data['total_asset_value']:,.2f}")
        if "total_asset_debt" in assets_data:
            st.markdown(f"**Total Debt:** ${assets_data['total_asset_debt']:,.2f}")
        if "net_asset_value" in assets_data:
            st.markdown(f"**Net Asset Value:** ${assets_data['net_asset_value']:,.2f}")
        elif "net_worth" in assets_data:
            st.markdown(f"**Net Worth:** ${assets_data['net_worth']:,.2f}")


def _render_va_benefits_section(va_benefits_data):
    """Render VA benefits data."""
    with st.expander("🎖️ **VA Benefits**", expanded=False):
        if not va_benefits_data:
            st.markdown("_No VA benefits data recorded._")
            return
        
        # Veteran Status
        is_veteran = va_benefits_data.get("is_veteran", False)
        st.markdown(f"**Veteran Status:** {'Yes ✓' if is_veteran else 'No'}")
        
        if is_veteran:
            # Disability Rating
            if "disability_rating" in va_benefits_data:
                rating = va_benefits_data["disability_rating"]
                st.markdown(f"**Disability Rating:** {rating}%")
            
            # Monthly Disability Benefit
            if "monthly_disability_benefit" in va_benefits_data:
                benefit = va_benefits_data["monthly_disability_benefit"]
                st.markdown(f"**Monthly Disability Benefit:** ${benefit:,.2f}")
            
            # Aid & Attendance
            if "aid_and_attendance_eligible" in va_benefits_data:
                eligible = va_benefits_data["aid_and_attendance_eligible"]
                st.markdown(f"**Aid & Attendance Eligible:** {'Yes ✓' if eligible else 'No'}")
            
            if "aid_and_attendance_benefit" in va_benefits_data:
                aa_benefit = va_benefits_data["aid_and_attendance_benefit"]
                if aa_benefit > 0:
                    st.markdown(f"**Aid & Attendance Benefit:** ${aa_benefit:,.2f}/month")


def _render_health_insurance_section(health_insurance_data):
    """Render health insurance data."""
    with st.expander("🏥 **Health Insurance**", expanded=False):
        if not health_insurance_data:
            st.markdown("_No health insurance data recorded._")
            return
        
        # Medicare
        has_medicare = health_insurance_data.get("has_medicare", False)
        st.markdown(f"**Has Medicare:** {'Yes ✓' if has_medicare else 'No'}")
        
        if has_medicare:
            parts = health_insurance_data.get("medicare_parts", [])
            if parts:
                st.markdown(f"**Medicare Parts:** {', '.join(parts)}")
        
        # Medicaid
        has_medicaid = health_insurance_data.get("has_medicaid", False)
        st.markdown(f"**Has Medicaid:** {'Yes ✓' if has_medicaid else 'No'}")
        
        # Private Insurance
        has_private = health_insurance_data.get("has_private_insurance", False)
        st.markdown(f"**Has Private Insurance:** {'Yes ✓' if has_private else 'No'}")
        
        if has_private:
            if "private_insurance_provider" in health_insurance_data:
                st.markdown(f"**Provider:** {health_insurance_data['private_insurance_provider']}")
            if "monthly_premium" in health_insurance_data:
                premium = health_insurance_data["monthly_premium"]
                st.markdown(f"**Monthly Premium:** ${premium:,.2f}")


def _render_life_insurance_section(life_insurance_data):
    """Render life insurance data."""
    with st.expander("💼 **Life Insurance & Annuities**", expanded=False):
        if not life_insurance_data:
            st.markdown("_No life insurance data recorded._")
            return
        
        # Life Insurance Policies
        policies = life_insurance_data.get("policies", [])
        if policies:
            st.markdown("#### Life Insurance Policies")
            for idx, policy in enumerate(policies, 1):
                policy_type = policy.get("type", "Unknown")
                cash_value = policy.get("cash_value", 0)
                death_benefit = policy.get("death_benefit", 0)
                st.markdown(f"{idx}. **{policy_type}**")
                st.markdown(f"   - Cash Value: ${cash_value:,.2f}")
                st.markdown(f"   - Death Benefit: ${death_benefit:,.2f}")
        
        # Annuities
        annuities = life_insurance_data.get("annuities", [])
        if annuities:
            st.markdown("")
            st.markdown("#### Annuities")
            for idx, annuity in enumerate(annuities, 1):
                annuity_type = annuity.get("type", "Unknown")
                value = annuity.get("value", 0)
                monthly_payout = annuity.get("monthly_payout", 0)
                st.markdown(f"{idx}. **{annuity_type}**")
                st.markdown(f"   - Value: ${value:,.2f}")
                if monthly_payout > 0:
                    st.markdown(f"   - Monthly Payout: ${monthly_payout:,.2f}")


def _render_medicaid_section(medicaid_data):
    """Render Medicaid planning data."""
    with st.expander("🏛️ **Medicaid Planning**", expanded=False):
        if not medicaid_data:
            st.markdown("_No Medicaid data recorded._")
            return
        
        # Current Medicaid Status
        currently_on_medicaid = medicaid_data.get("currently_on_medicaid", False)
        st.markdown(f"**Currently on Medicaid:** {'Yes ✓' if currently_on_medicaid else 'No'}")
        
        # Planning Interest
        interested_in_planning = medicaid_data.get("interested_in_planning", False)
        st.markdown(f"**Interested in Medicaid Planning:** {'Yes ✓' if interested_in_planning else 'No'}")
        
        # State
        if "state" in medicaid_data:
            st.markdown(f"**State:** {medicaid_data['state']}")
        
        # Additional notes
        if "notes" in medicaid_data and medicaid_data["notes"]:
            st.markdown("")
            st.markdown("**Notes:**")
            st.markdown(medicaid_data["notes"])


def _render_navigation():
    """Render navigation buttons."""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Concierge", key="review_back_to_hub", use_container_width=True):
            st.query_params["page"] = "hub_concierge"
            st.rerun()
    
    with col2:
        if st.button("📊 View Expert Review", key="review_expert", use_container_width=True, type="primary"):
            # Navigate to expert review step
            st.session_state.cost_v2_step = "expert_review"
            st.query_params["page"] = "cost_v2"
            st.rerun()
    
    with col3:
        if st.button("↻ Retake Assessment", key="review_restart", use_container_width=True):
            # Clear Cost Planner state for restart
            st.session_state.cost_v2_step = "intro"
            st.query_params["page"] = "cost_v2"
            st.rerun()
