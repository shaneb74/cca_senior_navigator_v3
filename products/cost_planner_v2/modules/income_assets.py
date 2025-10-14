"""
Cost Planner v2 - Income & Assets Module

Collects information about:
- Monthly income sources (Social Security, pensions, etc.)
- Liquid assets (savings, investments)
- Total assets (including property, retirement accounts)

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any


def render():
    """Render income & assets assessment module."""
    
    st.title("💵 Income & Assets Assessment")
    st.markdown("### Understanding your financial resources")
    
    st.info("""
    This helps us determine:
    - How much monthly income is available for care costs
    - Available assets to fund care
    - Financial runway (how long assets will last)
    """)
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_income_assets" not in st.session_state:
        st.session_state.cost_v2_income_assets = {
            "monthly_income_ss": 0,
            "monthly_income_pension": 0,
            "monthly_income_other": 0,
            "liquid_assets": 0,
            "property_value": 0,
            "retirement_accounts": 0,
            "other_assets": 0
        }
    
    # Monthly Income Section
    st.markdown("## 💰 Monthly Income Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ss_income = st.number_input(
            "Social Security Benefits ($/month)",
            min_value=0,
            max_value=10000,
            step=100,
            value=st.session_state.cost_v2_income_assets["monthly_income_ss"],
            help="Monthly Social Security income",
            key="income_ss"
        )
    
    with col2:
        pension_income = st.number_input(
            "Pension Income ($/month)",
            min_value=0,
            max_value=20000,
            step=100,
            value=st.session_state.cost_v2_income_assets["monthly_income_pension"],
            help="Monthly pension or annuity income",
            key="income_pension"
        )
    
    other_income = st.number_input(
        "Other Income ($/month)",
        min_value=0,
        max_value=50000,
        step=100,
        value=st.session_state.cost_v2_income_assets["monthly_income_other"],
        help="Investment income, rental income, part-time work, etc.",
        key="income_other"
    )
    
    total_monthly_income = ss_income + pension_income + other_income
    
    st.metric("**Total Monthly Income**", f"${total_monthly_income:,.0f}")
    
    st.markdown("---")
    
    # Assets Section
    st.markdown("## 🏦 Available Assets")
    
    st.caption("💡 **Tip:** Include only assets available for care costs (excluding primary residence if staying)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        liquid_assets = st.number_input(
            "Liquid Assets (checking, savings, CDs)",
            min_value=0,
            max_value=10000000,
            step=1000,
            value=st.session_state.cost_v2_income_assets["liquid_assets"],
            help="Easily accessible cash and savings",
            key="liquid_assets"
        )
        
        property_value = st.number_input(
            "Property Value (excluding primary residence)",
            min_value=0,
            max_value=50000000,
            step=10000,
            value=st.session_state.cost_v2_income_assets["property_value"],
            help="Investment properties, vacation homes, land",
            key="property_value"
        )
    
    with col2:
        retirement_accounts = st.number_input(
            "Retirement Accounts (401k, IRA, etc.)",
            min_value=0,
            max_value=10000000,
            step=1000,
            value=st.session_state.cost_v2_income_assets["retirement_accounts"],
            help="Value of retirement accounts available for withdrawal",
            key="retirement_accounts"
        )
        
        other_assets = st.number_input(
            "Other Assets (investments, bonds, etc.)",
            min_value=0,
            max_value=10000000,
            step=1000,
            value=st.session_state.cost_v2_income_assets["other_assets"],
            help="Stocks, bonds, mutual funds, other investments",
            key="other_assets"
        )
    
    total_assets = liquid_assets + property_value + retirement_accounts + other_assets
    
    st.metric("**Total Available Assets**", f"${total_assets:,.0f}")
    
    st.markdown("---")
    
    # Summary
    st.markdown("## 📊 Financial Resource Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Monthly Income", f"${total_monthly_income:,.0f}")
    
    with col2:
        st.metric("Liquid Assets", f"${liquid_assets:,.0f}")
    
    with col3:
        st.metric("Total Assets", f"${total_assets:,.0f}")
    
    # Quick projection
    if total_monthly_income > 0 and total_assets > 0:
        st.info(f"""
        💡 **Quick Insight:** With ${total_monthly_income:,.0f}/month income and ${total_assets:,.0f} 
        in assets, you have substantial resources to work with. We'll calculate exactly how long these 
        will last in the next steps.
        """)
    
    st.markdown("---")
    
    # Navigation
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("← Back to Hub", key="income_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col2:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="income_save"):
            # Save data to module state
            data = {
                "monthly_income_ss": ss_income,
                "monthly_income_pension": pension_income,
                "monthly_income_other": other_income,
                "total_monthly_income": total_monthly_income,
                "liquid_assets": liquid_assets,
                "property_value": property_value,
                "retirement_accounts": retirement_accounts,
                "other_assets": other_assets,
                "total_assets": total_assets
            }
            
            # Update session state
            st.session_state.cost_v2_income_assets = data
            
            # Mark module complete
            st.session_state.cost_v2_modules["income_assets"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ Income & Assets saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")
