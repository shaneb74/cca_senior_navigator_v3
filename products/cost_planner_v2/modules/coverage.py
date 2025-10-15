"""
Cost Planner v2 - Coverage Module

Calculates coverage from various sources:
- Long-term care insurance
- VA benefits (Aid & Attendance)
- Medicare/Medicaid
- Other insurance

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any
from core.mcip import MCIP


def render():
    """Render coverage assessment module."""
    
    st.title("🏥 Coverage & Benefits Assessment")
    st.markdown("### Understanding your coverage sources")
    
    st.info("""
    This helps us calculate:
    - Available insurance coverage
    - Veteran benefits eligibility
    - Medicare/Medicaid contributions
    - Your out-of-pocket cost gap
    """)
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_coverage" not in st.session_state:
        st.session_state.cost_v2_coverage = {
            "has_ltc_insurance": False,
            "ltc_monthly_benefit": 0,
            "is_veteran": False,
            "va_monthly_benefit": 0,
            "has_medicare": False,
            "medicare_coverage": 0,
            "has_medicaid": False,
            "medicaid_coverage": 0,
            "other_coverage": 0
        }
    
    # Long-Term Care Insurance
    st.markdown("## 💼 Long-Term Care Insurance")
    
    has_ltc = st.checkbox(
        "Do you have long-term care insurance?",
        value=st.session_state.cost_v2_coverage.get("has_ltc_insurance", False),
        key="has_ltc"
    )
    
    ltc_benefit = 0
    if has_ltc:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Monthly Benefit Amount** ($)")
            ltc_benefit = st.number_input(
                "Monthly Benefit Amount ($)",
                min_value=0,
                max_value=20000,
                step=100,
                value=st.session_state.cost_v2_coverage.get("ltc_monthly_benefit", 0),
                help="How much does your policy pay per month?",
                key="ltc_benefit",
                label_visibility="collapsed"
            )
        
        with col2:
            st.metric("LTC Coverage", f"${ltc_benefit:,.0f}/mo")
        
        st.caption("💡 **Tip:** Check your policy documents for exact benefit amounts and any waiting periods")
    
    st.markdown("---")
    
    # Veteran Benefits
    st.markdown("## 🎖️ Veteran Benefits (Aid & Attendance)")
    
    is_veteran = st.checkbox(
        "Are you (or your spouse) a wartime veteran?",
        value=st.session_state.cost_v2_coverage.get("is_veteran", False),
        help="Veterans and surviving spouses may qualify for Aid & Attendance benefits",
        key="is_veteran"
    )
    
    va_benefit = 0
    if is_veteran:
        st.success("""
        ### ✅ You may be eligible for VA Aid & Attendance!
        
        **Current maximum monthly benefits (2025):**
        - Veteran alone: $2,379
        - Veteran with spouse: $2,829
        - Surviving spouse: $1,537
        
        **Requirements:**
        - Served during wartime
        - Need help with daily living activities
        - Meet income/asset limits
        """)
        
        va_status = st.selectbox(
            "Your Status",
            options=["Not sure", "Veteran alone", "Veteran with spouse", "Surviving spouse"],
            key="va_status"
        )
        
        # Set estimated benefit based on status
        va_amounts = {
            "Veteran alone": 2379,
            "Veteran with spouse": 2829,
            "Surviving spouse": 1537,
            "Not sure": 0
        }
        
        va_benefit = va_amounts.get(va_status, 0)
        
        if va_benefit > 0:
            st.metric("Estimated VA Benefit", f"${va_benefit:,.0f}/mo")
            st.caption("⚠️ Actual benefit depends on income, assets, and medical expenses. We recommend applying through a VA-accredited representative.")
    
    st.markdown("---")
    
    # Medicare
    st.markdown("## 🏥 Medicare")
    
    has_medicare = st.checkbox(
        "Are you enrolled in Medicare?",
        value=st.session_state.cost_v2_coverage.get("has_medicare", False),
        key="has_medicare"
    )
    
    medicare_coverage = 0
    if has_medicare:
        st.warning("""
        **Important:** Medicare has limited coverage for long-term care:
        - ✅ Covers skilled nursing care (up to 100 days)
        - ✅ Covers home health for medical needs
        - ❌ Does NOT cover custodial care (assistance with daily living)
        - ❌ Does NOT cover assisted living or memory care
        """)
        
        medicare_applies = st.selectbox(
            "Does Medicare cover any of your current care costs?",
            options=["No", "Yes - Skilled nursing (short-term)", "Yes - Home health (medical)"],
            key="medicare_type"
        )
        
        if medicare_applies != "No":
            st.markdown("**Estimated Monthly Medicare Contribution** ($)")
            medicare_coverage = st.number_input(
                "Estimated monthly Medicare contribution ($)",
                min_value=0,
                max_value=5000,
                step=100,
                value=st.session_state.cost_v2_coverage.get("medicare_coverage", 0),
                help="Estimate how much Medicare pays toward your care",
                key="medicare_amount",
                label_visibility="collapsed"
            )
    
    st.markdown("---")
    
    # Medicaid
    st.markdown("## 🏛️ Medicaid")
    
    has_medicaid = st.checkbox(
        "Are you enrolled in Medicaid or considering applying?",
        value=st.session_state.cost_v2_coverage.get("has_medicaid", False),
        key="has_medicaid"
    )
    
    medicaid_coverage = 0
    if has_medicaid:
        st.success("""
        **Medicaid can cover:**
        - ✅ Nursing home care
        - ✅ Home and community-based services
        - ✅ Assisted living (in some states)
        
        **Eligibility requirements:**
        - Income limits (varies by state)
        - Asset limits (typically $2,000 individual, $3,000 couple)
        - Medical necessity
        """)
        
        medicaid_status = st.selectbox(
            "Medicaid Status",
            options=["Planning to apply", "Application pending", "Currently enrolled"],
            key="medicaid_status"
        )
        
        if medicaid_status == "Currently enrolled":
            st.markdown("**Monthly Medicaid Coverage** ($)")
            medicaid_coverage = st.number_input(
                "Monthly Medicaid coverage ($)",
                min_value=0,
                max_value=10000,
                step=100,
                value=st.session_state.cost_v2_coverage.get("medicaid_coverage", 0),
                help="How much does Medicaid pay toward your care?",
                key="medicaid_amount",
                label_visibility="collapsed"
            )
    
    st.markdown("---")
    
    # Other Coverage
    st.markdown("## 💳 Other Coverage")
    
    st.markdown("**Other Insurance or Assistance** ($/month)")
    other_coverage = st.number_input(
        "Other insurance or assistance ($/month)",
        min_value=0,
        max_value=10000,
        step=100,
        value=st.session_state.cost_v2_coverage.get("other_coverage", 0),
        help="Private insurance, family assistance, etc.",
        key="other_coverage",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Coverage Summary
    st.markdown("## 📊 Total Coverage Summary")
    
    total_coverage = ltc_benefit + va_benefit + medicare_coverage + medicaid_coverage + other_coverage
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Insurance", f"${ltc_benefit:,.0f}")
    
    with col2:
        st.metric("VA + Medicare/Medicaid", f"${va_benefit + medicare_coverage + medicaid_coverage:,.0f}")
    
    with col3:
        st.metric("**Total Coverage**", f"**${total_coverage:,.0f}**")
    
    # Calculate gap (if monthly costs module completed)
    monthly_costs_data = st.session_state.cost_v2_modules.get("monthly_costs", {}).get("data")
    
    if monthly_costs_data:
        total_cost = monthly_costs_data.get("total_monthly_cost", 0)
        gap = total_cost - total_coverage
        
        st.markdown("### 💰 Coverage Gap Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Monthly Cost", f"${total_cost:,.0f}")
        
        with col2:
            st.metric("Coverage", f"${total_coverage:,.0f}")
        
        with col3:
            if gap > 0:
                st.metric("**Gap to Cover**", f"**${gap:,.0f}**", delta=f"-${gap:,.0f}", delta_color="inverse")
            else:
                st.metric("**Surplus**", f"**${abs(gap):,.0f}**", delta=f"+${abs(gap):,.0f}")
        
        if gap > 0:
            # Calculate runway from income/assets module
            income_data = st.session_state.cost_v2_modules.get("income_assets", {}).get("data")
            
            if income_data:
                monthly_income = income_data.get("total_monthly_income", 0)
                total_assets = income_data.get("total_assets", 0)
                
                if monthly_income >= gap:
                    st.success(f"✅ **Good news!** Your monthly income (${monthly_income:,.0f}) covers the gap.")
                else:
                    income_shortfall = gap - monthly_income
                    
                    if total_assets > 0:
                        months_runway = total_assets / income_shortfall
                        years_runway = months_runway / 12
                        
                        st.warning(f"""
                        ⚠️ **Monthly income falls short by ${income_shortfall:,.0f}**
                        
                        Using assets to cover the gap:
                        - **Financial runway:** {months_runway:.0f} months ({years_runway:.1f} years)
                        - Assets will be depleted around {_format_future_date(months_runway)}
                        """)
                    else:
                        st.error(f"❌ **Monthly shortfall:** ${income_shortfall:,.0f} with no reported assets to cover the gap.")
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🏠 Back to Hub", key="coverage_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    with col2:
        if st.button("← Back to Modules", key="coverage_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col3:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="coverage_save"):
            # Save data
            data = {
                "has_ltc_insurance": has_ltc,
                "ltc_monthly_benefit": ltc_benefit,
                "is_veteran": is_veteran,
                "va_monthly_benefit": va_benefit,
                "has_medicare": has_medicare,
                "medicare_coverage": medicare_coverage,
                "has_medicaid": has_medicaid,
                "medicaid_coverage": medicaid_coverage,
                "other_coverage": other_coverage,
                "total_coverage": total_coverage
            }
            
            # Update session state
            st.session_state.cost_v2_coverage = data
            
            # Mark module complete
            st.session_state.cost_v2_modules["coverage"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ Coverage assessment saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")


def _format_future_date(months: float) -> str:
    """Format future date based on months from now.
    
    Args:
        months: Number of months in the future
    
    Returns:
        Formatted date string
    """
    from datetime import datetime, timedelta
    import calendar
    
    future_date = datetime.now() + timedelta(days=30 * months)
    month_name = calendar.month_name[future_date.month]
    return f"{month_name} {future_date.year}"
