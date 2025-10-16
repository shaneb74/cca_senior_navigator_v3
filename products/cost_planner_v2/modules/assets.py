"""
Cost Planner v2 - Assets & Resources Module

Collects information about:
- Liquid assets (checking, savings, CDs, money market)
- Retirement accounts (IRA, 401k, etc.)
- Investments (stocks, bonds, mutual funds)
- Real estate (primary residence, investment property)
- Other assets (business, vehicles, collections)

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any


def render():
    """Render assets & resources assessment module."""
    
    st.title("🏦 Assets & Resources")
    st.markdown("### Available financial assets and resources")
    
    st.info("""
    This helps us determine:
    - Total assets available for care costs
    - Asset liquidity and accessibility
    - How long your assets can sustain care expenses
    """)
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_assets" not in st.session_state:
        st.session_state.cost_v2_assets = {
            "checking_savings": 0,
            "cds_money_market": 0,
            "ira_traditional": 0,
            "ira_roth": 0,
            "k401_403b": 0,
            "other_retirement": 0,
            "stocks_bonds": 0,
            "mutual_funds": 0,
            "primary_residence_value": 0,
            "primary_residence_mortgage": 0,
            "investment_property": 0,
            "business_value": 0,
            "other_assets_value": 0
        }
    
    # Liquid Assets Section
    st.markdown("## 💵 Liquid Assets")
    st.caption("Easily accessible cash and savings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        checking_savings = st.number_input(
            "Checking & Savings Accounts",
            min_value=0,
            max_value=10000000,
            step=1000,
            value=st.session_state.cost_v2_assets["checking_savings"],
            help="Total in bank accounts",
            key="checking_savings"
        )
    
    with col2:
        cds_money_market = st.number_input(
            "CDs & Money Market Accounts",
            min_value=0,
            max_value=10000000,
            step=1000,
            value=st.session_state.cost_v2_assets["cds_money_market"],
            help="Certificates of deposit and money market funds",
            key="cds_money_market"
        )
    
    total_liquid_assets = checking_savings + cds_money_market
    st.metric("**Total Liquid Assets**", f"${total_liquid_assets:,.0f}")
    
    st.markdown("---")
    
    # Retirement Accounts Section
    st.markdown("## 📊 Retirement Accounts")
    st.caption("401(k), IRA, and other retirement savings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ira_traditional = st.number_input(
            "Traditional IRA",
            min_value=0,
            max_value=10000000,
            step=5000,
            value=st.session_state.cost_v2_assets["ira_traditional"],
            help="Traditional IRA balance",
            key="ira_traditional"
        )
        
        ira_roth = st.number_input(
            "Roth IRA",
            min_value=0,
            max_value=10000000,
            step=5000,
            value=st.session_state.cost_v2_assets["ira_roth"],
            help="Roth IRA balance",
            key="ira_roth"
        )
    
    with col2:
        k401_403b = st.number_input(
            "401(k) / 403(b)",
            min_value=0,
            max_value=10000000,
            step=5000,
            value=st.session_state.cost_v2_assets["k401_403b"],
            help="Employer retirement plan balance",
            key="k401_403b"
        )
        
        other_retirement = st.number_input(
            "Other Retirement Accounts",
            min_value=0,
            max_value=10000000,
            step=5000,
            value=st.session_state.cost_v2_assets["other_retirement"],
            help="Other retirement savings (SEP IRA, pension plans)",
            key="other_retirement"
        )
    
    total_retirement_accounts = ira_traditional + ira_roth + k401_403b + other_retirement
    st.metric("**Total Retirement Accounts**", f"${total_retirement_accounts:,.0f}")
    
    st.markdown("---")
    
    # Investments Section
    st.markdown("## 📈 Investments")
    st.caption("Stocks, bonds, mutual funds, and other investments")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stocks_bonds = st.number_input(
            "Stocks & Bonds",
            min_value=0,
            max_value=50000000,
            step=10000,
            value=st.session_state.cost_v2_assets["stocks_bonds"],
            help="Individual stocks and bonds",
            key="stocks_bonds"
        )
    
    with col2:
        mutual_funds = st.number_input(
            "Mutual Funds & ETFs",
            min_value=0,
            max_value=50000000,
            step=10000,
            value=st.session_state.cost_v2_assets["mutual_funds"],
            help="Mutual funds and exchange-traded funds",
            key="mutual_funds"
        )
    
    total_investments = stocks_bonds + mutual_funds
    st.metric("**Total Investments**", f"${total_investments:,.0f}")
    
    st.markdown("---")
    
    # Real Estate Section
    st.markdown("## 🏠 Real Estate")
    st.caption("Property excluding or including primary residence")
    
    primary_residence_value = st.number_input(
        "Primary Residence Value",
        min_value=0,
        max_value=50000000,
        step=25000,
        value=st.session_state.cost_v2_assets["primary_residence_value"],
        help="Estimated market value of your home",
        key="primary_residence_value"
    )
    
    if primary_residence_value > 0:
        st.caption("ℹ️ May be protected under Medicaid rules")
    
    primary_residence_mortgage = st.number_input(
        "Remaining Mortgage Balance",
        min_value=0,
        max_value=10000000,
        step=10000,
        value=st.session_state.cost_v2_assets["primary_residence_mortgage"],
        help="Outstanding mortgage on primary residence",
        key="primary_residence_mortgage"
    )
    
    primary_equity = primary_residence_value - primary_residence_mortgage
    if primary_residence_value > 0:
        st.metric("**Home Equity**", f"${primary_equity:,.0f}")
    
    investment_property = st.number_input(
        "Investment Property Value",
        min_value=0,
        max_value=50000000,
        step=25000,
        value=st.session_state.cost_v2_assets["investment_property"],
        help="Rental properties, vacation homes, land",
        key="investment_property"
    )
    
    st.markdown("---")
    
    # Other Assets Section
    st.markdown("## 💎 Other Assets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        business_value = st.number_input(
            "Business Ownership Value",
            min_value=0,
            max_value=50000000,
            step=25000,
            value=st.session_state.cost_v2_assets["business_value"],
            help="Value of business interests",
            key="business_value"
        )
    
    with col2:
        other_assets_value = st.number_input(
            "Other Assets (vehicles, collections, etc.)",
            min_value=0,
            max_value=10000000,
            step=5000,
            value=st.session_state.cost_v2_assets["other_assets_value"],
            help="Vehicles, jewelry, collections, other valuables",
            key="other_assets_value"
        )
    
    st.markdown("---")
    
    # Calculate totals
    total_available_assets = (
        checking_savings + cds_money_market + 
        ira_traditional + ira_roth + k401_403b + other_retirement +
        stocks_bonds + mutual_funds + 
        investment_property + business_value + other_assets_value
    )
    
    # Summary
    st.markdown("## 📊 Asset Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Liquid Assets", f"${total_liquid_assets:,.0f}")
    
    with col2:
        st.metric("Retirement", f"${total_retirement_accounts:,.0f}")
    
    with col3:
        st.metric("Total Available", f"${total_available_assets:,.0f}")
    
    if total_available_assets > 0:
        st.info(f"""
        💡 **Asset Breakdown:**
        - Liquid: ${total_liquid_assets:,.0f} ({100*total_liquid_assets/total_available_assets:.1f}%)
        - Retirement: ${total_retirement_accounts:,.0f} ({100*total_retirement_accounts/total_available_assets:.1f}%)
        - Investments: ${total_investments:,.0f} ({100*total_investments/total_available_assets:.1f}%)
        - Other: ${investment_property + business_value + other_assets_value:,.0f}
        """)
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🏠 Back to Hub", key="assets_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    with col2:
        if st.button("← Back to Modules", key="assets_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col3:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="assets_save"):
            # Save data to module state
            data = {
                "checking_savings": checking_savings,
                "cds_money_market": cds_money_market,
                "total_liquid_assets": total_liquid_assets,
                "ira_traditional": ira_traditional,
                "ira_roth": ira_roth,
                "k401_403b": k401_403b,
                "other_retirement": other_retirement,
                "total_retirement_accounts": total_retirement_accounts,
                "stocks_bonds": stocks_bonds,
                "mutual_funds": mutual_funds,
                "total_investments": total_investments,
                "primary_residence_value": primary_residence_value,
                "primary_residence_mortgage": primary_residence_mortgage,
                "primary_equity": primary_equity,
                "investment_property": investment_property,
                "business_value": business_value,
                "other_assets_value": other_assets_value,
                "total_available_assets": total_available_assets
            }
            
            # Update session state
            st.session_state.cost_v2_assets = data
            
            # Mark module complete
            if "cost_v2_modules" not in st.session_state:
                st.session_state.cost_v2_modules = {}
            
            st.session_state.cost_v2_modules["assets"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ Assets & Resources saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")
