"""
Cost Planner v2 - Income Sources Module

Collects information about:
- Social Security benefits
- Pension and annuity income
- Employment income
- Investment income
- Other income sources

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any


def render():
    """Render income sources assessment module."""
    
    st.title("💰 Income Sources")
    st.markdown("### Monthly income from all sources")
    
    st.info("""
    This helps us understand:
    - Your total monthly income available
    - Primary income sources
    - Sustainable income for care costs
    """)
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_income" not in st.session_state:
        st.session_state.cost_v2_income = {
            "ss_monthly": 0,
            "pension_monthly": 0,
            "employment_status": "not_employed",
            "employment_monthly": 0,
            "investment_monthly": 0,
            "other_monthly": 0
        }
    
    # Social Security Section
    st.markdown("## 🏛️ Social Security Benefits")
    st.caption("Monthly Social Security retirement or disability benefits")
    
    ss_monthly = st.number_input(
        "Social Security Monthly Benefit",
        min_value=0,
        max_value=5000,
        step=10,
        value=st.session_state.cost_v2_income["ss_monthly"],
        help="Enter the monthly Social Security benefit amount",
        key="ss_monthly"
    )
    
    st.markdown("---")
    
    # Pension Section
    st.markdown("## 📊 Pension & Annuity Income")
    st.caption("Retirement pension and annuity payments")
    
    pension_monthly = st.number_input(
        "Monthly Pension Amount",
        min_value=0,
        max_value=20000,
        step=100,
        value=st.session_state.cost_v2_income["pension_monthly"],
        help="Monthly pension or annuity income",
        key="pension_monthly"
    )
    
    st.markdown("---")
    
    # Employment Section
    st.markdown("## 💼 Employment Income")
    st.caption("Income from current employment or self-employment")
    
    employment_status = st.selectbox(
        "Employment Status",
        options=["not_employed", "part_time", "full_time", "self_employed"],
        format_func=lambda x: {
            "not_employed": "Not employed",
            "part_time": "Part-time employment",
            "full_time": "Full-time employment",
            "self_employed": "Self-employed"
        }[x],
        index=["not_employed", "part_time", "full_time", "self_employed"].index(
            st.session_state.cost_v2_income["employment_status"]
        ),
        key="employment_status"
    )
    
    employment_monthly = 0
    if employment_status != "not_employed":
        employment_monthly = st.number_input(
            "Monthly Employment Income (after tax)",
            min_value=0,
            max_value=50000,
            step=100,
            value=st.session_state.cost_v2_income["employment_monthly"],
            help="Net monthly income from employment",
            key="employment_monthly"
        )
    
    st.markdown("---")
    
    # Investment Income Section
    st.markdown("## 📈 Investment Income")
    st.caption("Dividends, interest, and rental income")
    
    investment_monthly = st.number_input(
        "Monthly Investment Income (dividends, interest, rental)",
        min_value=0,
        max_value=50000,
        step=100,
        value=st.session_state.cost_v2_income["investment_monthly"],
        help="Investment dividends, interest, rental property income",
        key="investment_monthly"
    )
    
    st.markdown("---")
    
    # Other Income Section
    st.markdown("## 💵 Other Income Sources")
    
    other_monthly = st.number_input(
        "Other Monthly Income (family support, trust, etc.)",
        min_value=0,
        max_value=50000,
        step=100,
        value=st.session_state.cost_v2_income["other_monthly"],
        help="Family support, trust distributions, other income",
        key="other_monthly"
    )
    
    st.markdown("---")
    
    # Calculate total
    total_monthly_income = (
        ss_monthly + pension_monthly + employment_monthly + 
        investment_monthly + other_monthly
    )
    
    # Summary
    st.markdown("## 📊 Total Monthly Income")
    st.metric("**Total Income**", f"${total_monthly_income:,.0f}/month")
    
    if total_monthly_income > 0:
        st.info(f"""
        💡 **Income Breakdown:**
        - Social Security: ${ss_monthly:,.0f}
        - Pension: ${pension_monthly:,.0f}
        - Employment: ${employment_monthly:,.0f}
        - Investment: ${investment_monthly:,.0f}
        - Other: ${other_monthly:,.0f}
        """)
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🏠 Back to Hub", key="income_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    with col2:
        if st.button("← Back to Modules", key="income_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col3:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="income_save"):
            # Save data to module state
            data = {
                "ss_monthly": ss_monthly,
                "pension_monthly": pension_monthly,
                "employment_status": employment_status,
                "employment_monthly": employment_monthly,
                "investment_monthly": investment_monthly,
                "other_monthly": other_monthly,
                "total_monthly_income": total_monthly_income
            }
            
            # Update session state
            st.session_state.cost_v2_income = data
            
            # Mark module complete
            if "cost_v2_modules" not in st.session_state:
                st.session_state.cost_v2_modules = {}
            
            st.session_state.cost_v2_modules["income"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ Income Sources saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")
