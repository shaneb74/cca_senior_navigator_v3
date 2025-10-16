"""
Cost Planner v2 - Assets & Resources Module

Collects information about:
- Primary assets (checking, savings, investments)
- Property & real estate (primary residence, other real estate)
- Other resources (vehicles, valuables, other assets)
- Home sale interest flag (activates Home Sale module)

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any
from core.ui import render_navi_panel_v2


def render():
    """Render assets & resources assessment module."""
    
    st.title("🏦 Assets & Resources")
    
    # Navi guidance banner
    render_navi_panel_v2(
        title="Let's look at your assets and resources",
        reason="This helps me understand what savings, property, or other funds might help pay for care. Enter what you're comfortable sharing — I'll handle the math.",
        encouragement={
            "icon": "💡",
            "status": "getting_started",
            "text": "Inputs stay visible. Open a Quick Guide anytime for examples or definitions."
        },
        context_chips=[],
        primary_action={'label': 'Continue', 'action': None},
        variant="module"
    )
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_assets" not in st.session_state:
        st.session_state.cost_v2_assets = {
            "checking_savings": 0,
            "investment_accounts": 0,
            "primary_residence_value": 0,
            "home_sale_interest": False,
            "other_real_estate": 0,
            "other_resources": 0
        }
    
    # Two-column grid layout
    col1, col2 = st.columns(2, gap="large")
    
    # LEFT COLUMN: Primary Assets
    with col1:
        st.markdown('<div class="asset-card">', unsafe_allow_html=True)
        st.markdown("#### 🏦 Primary Assets")
        
        # Checking & Savings
        st.markdown("**Checking & Savings**")
        st.markdown('<span class="asset-caption">Total balance in all checking and savings accounts</span>', unsafe_allow_html=True)
        
        checking_savings = st.number_input(
            "Total Balance",
            min_value=0,
            max_value=10000000,
            step=1000,
            value=st.session_state.cost_v2_assets["checking_savings"],
            help="Total in all bank accounts",
            key="checking_savings",
            label_visibility="visible"
        )
        
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            - **Include:** All active checking, savings, and money market accounts
            - **Average:** $100,000–$250,000 for seniors (varies widely)
            - **Tip:** Liquid assets are important for immediate care costs
            - **Medicaid:** Up to $2,000 allowed for individual (2024)
            """)
        
        st.markdown("---")
        
        # Investment Accounts
        st.markdown("**Investment Accounts**")
        st.markdown('<span class="asset-caption">401(k), IRA, brokerage, stocks, bonds, mutual funds</span>', unsafe_allow_html=True)
        
        investment_accounts = st.number_input(
            "Estimated Total Value",
            min_value=0,
            max_value=50000000,
            step=5000,
            value=st.session_state.cost_v2_assets["investment_accounts"],
            help="Combined value of all investment accounts",
            key="investment_accounts",
            label_visibility="visible"
        )
        
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            - **401(k)/IRA:** Retirement accounts (estimates OK)
            - **Brokerage:** Stocks, bonds, mutual funds, ETFs
            - **Penalties:** Early withdrawal before 59½ may incur fees
            - **Tax impact:** Withdrawals are taxable income
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # RIGHT COLUMN: Property & Real Estate
    with col2:
        st.markdown('<div class="asset-card">', unsafe_allow_html=True)
        st.markdown("#### 🏠 Property & Real Estate")
        
        # Primary Residence
        st.markdown("**Primary Residence**")
        st.markdown('<span class="asset-caption">Your current home</span>', unsafe_allow_html=True)
        
        primary_residence_value = st.number_input(
            "Estimated Home Value",
            min_value=0,
            max_value=50000000,
            step=25000,
            value=st.session_state.cost_v2_assets["primary_residence_value"],
            help="Estimated market value of your home",
            key="primary_residence_value",
            label_visibility="visible"
        )
        
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            - **Market estimate:** Recent comparable sales in your area
            - **Appraisal:** Professional valuation if selling or refinancing
            - **Medicaid protection:** Primary home often exempt (up to certain equity limits)
            - **Value:** Median U.S. home value ~$420,000 (2024)
            """)
        
        st.markdown("---")
        
        # Home Sale Interest Checkbox
        st.markdown('<div class="home-sale-checkbox-wrapper">', unsafe_allow_html=True)
        st.markdown(
            '<label for="home_sale_interest" style="font-size: 16px; font-weight: 500; color: #1F2937; line-height: 1.6; display: block; margin-bottom: 4px; cursor: pointer;">I\'d like to evaluate selling this home or explore home equity options</label>',
            unsafe_allow_html=True
        )
        home_sale_interest = st.checkbox(
            "Home sale interest checkbox",
            value=st.session_state.cost_v2_assets.get("home_sale_interest", False),
            key="home_sale_interest",
            label_visibility="collapsed",
            help="Check this to activate the Home Sale module for guidance on selling, reverse mortgages, or HELOCs"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if home_sale_interest:
            st.info("💡 I'll guide you through sale, reverse mortgage, or HELOC options in the next step.")
        
        st.markdown("---")
        
        # Other Real Estate
        st.markdown("**Other Real Estate**")
        st.markdown('<span class="asset-caption">Rental properties, vacation homes, land, etc.</span>', unsafe_allow_html=True)
        
        other_real_estate = st.number_input(
            "Estimated Value",
            min_value=0,
            max_value=50000000,
            step=25000,
            value=st.session_state.cost_v2_assets["other_real_estate"],
            help="Investment properties, vacation homes, land",
            key="other_real_estate",
            label_visibility="visible"
        )
        
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            - **Rental income:** Consider both property value and monthly income
            - **Vacation homes:** May need to be sold or rented for care costs
            - **Land:** Undeveloped property can be liquidated if needed
            - **Tax implications:** Capital gains on sale of investment property
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # BOTTOM ROW: Other Resources (full width)
    st.markdown('<div class="asset-card">', unsafe_allow_html=True)
    st.markdown("#### 💎 Other Resources")
    
    st.markdown("**Vehicles / Valuables / Other Assets**")
    st.markdown('<span class="asset-caption">Vehicles, jewelry, collectibles, business interests, etc.</span>', unsafe_allow_html=True)
    
    other_resources = st.number_input(
        "Estimated Total Value",
        min_value=0,
        max_value=10000000,
        step=5000,
        value=st.session_state.cost_v2_assets["other_resources"],
        help="Vehicles, jewelry, collections, business value, other valuables",
        key="other_resources",
        label_visibility="visible"
    )
    
    with st.expander("💡 Quick Guide"):
        st.markdown("""
        - **Vehicles:** Current market value (not purchase price)
        - **Jewelry/collectibles:** Appraised value for significant items
        - **Business interests:** Ownership stake in private businesses
        - **Liquidation:** Consider which assets could realistically be sold for care costs
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get values from session state
    checking_savings = st.session_state.get("checking_savings", 0)
    investment_accounts = st.session_state.get("investment_accounts", 0)
    primary_residence_value = st.session_state.get("primary_residence_value", 0)
    home_sale_interest = st.session_state.get("home_sale_interest", False)
    other_real_estate = st.session_state.get("other_real_estate", 0)
    other_resources = st.session_state.get("other_resources", 0)
    
    # Calculate total
    total_asset_value = (
        checking_savings + investment_accounts + 
        primary_residence_value + other_real_estate + other_resources
    )
    
    # Summary
    st.markdown("### � Total Asset Value")
    st.metric("**Total Assets**", f"${total_asset_value:,.0f}")
    
    if total_asset_value > 0:
        col1, col2 = st.columns(2)
        with col1:
            if checking_savings > 0:
                st.caption(f"💰 Checking & Savings: ${checking_savings:,.0f}")
            if investment_accounts > 0:
                st.caption(f"📊 Investment Accounts: ${investment_accounts:,.0f}")
        with col2:
            if primary_residence_value > 0:
                st.caption(f"🏠 Primary Residence: ${primary_residence_value:,.0f}")
            if other_real_estate > 0:
                st.caption(f"🏘️ Other Real Estate: ${other_real_estate:,.0f}")
            if other_resources > 0:
                st.caption(f"💎 Other Resources: ${other_resources:,.0f}")
    
    st.markdown("---")
    
    # Fixed Footer Navigation
    footer_container = st.container()
    with footer_container:
        st.markdown('<div class="fixed-footer-nav">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if st.button("← Back to Modules", key="assets_back"):
                st.session_state.cost_v2_step = "modules"
                st.rerun()
        
        with col2:
            if st.button("💾 Save & Continue →", type="primary", use_container_width=True, key="assets_save"):
                # Save data to module state
                data = {
                    "checking_savings": checking_savings,
                    "investment_accounts": investment_accounts,
                    "primary_residence_value": primary_residence_value,
                    "home_sale_interest": home_sale_interest,
                    "other_real_estate": other_real_estate,
                    "other_resources": other_resources,
                    "total_asset_value": total_asset_value
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
                
                # If home sale interest is checked, activate the home_sale module in the hub
                if home_sale_interest:
                    # Set a flag that the hub can check to show the Home Sale module tile
                    st.session_state.cost_v2_home_sale_enabled = True
                else:
                    # Remove the flag if unchecked
                    st.session_state.cost_v2_home_sale_enabled = False
                
                # Return to hub
                st.session_state.cost_v2_step = "modules"
                st.success("✅ Assets & Resources saved!")
                st.rerun()
        
        st.caption("💾 Your progress is automatically saved")
        st.markdown('</div>', unsafe_allow_html=True)
