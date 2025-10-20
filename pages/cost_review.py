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
            st.query_params["page"] = "concierge"
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
        
        # Monthly Income Sources
        st.markdown("#### Monthly Income Sources")
        
        sources = income_data.get("income_sources", [])
        if sources:
            for idx, source in enumerate(sources, 1):
                source_type = source.get("type", "Unknown")
                amount = source.get("amount", 0)
                st.markdown(f"{idx}. **{source_type}:** ${amount:,.2f}/month")
        
        # Total Monthly Income
        if "total_monthly_income" in income_data:
            st.markdown("")
            st.markdown(f"**Total Monthly Income:** ${income_data['total_monthly_income']:,.2f}")


def _render_assets_section(assets_data):
    """Render assets assessment data."""
    with st.expander("🏦 **Assets Assessment**", expanded=False):
        if not assets_data:
            st.markdown("_No asset data recorded._")
            return
        
        # Assets
        st.markdown("#### Assets")
        assets = assets_data.get("assets", [])
        if assets:
            for idx, asset in enumerate(assets, 1):
                asset_type = asset.get("type", "Unknown")
                value = asset.get("value", 0)
                debt = asset.get("debt", 0)
                st.markdown(f"{idx}. **{asset_type}:** ${value:,.2f} (Debt: ${debt:,.2f})")
        
        # Totals
        if "total_asset_value" in assets_data:
            st.markdown("")
            st.markdown(f"**Total Asset Value:** ${assets_data['total_asset_value']:,.2f}")
        if "total_asset_debt" in assets_data:
            st.markdown(f"**Total Debt:** ${assets_data['total_asset_debt']:,.2f}")
        if "net_worth" in assets_data:
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
            st.query_params["page"] = "concierge"
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
