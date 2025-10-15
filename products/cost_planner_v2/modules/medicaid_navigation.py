"""
Cost Planner v2 - Medicaid Navigation Module

Collects information about:
- Medicaid interest level and timeline
- Asset and income assessment for eligibility
- Planning timeline and lookback concerns
- Need for Medicaid planning specialists

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any


def render():
    """Render Medicaid navigation assessment module."""
    
    st.title("🧭 Medicaid Navigation")
    st.markdown("### Medicaid planning and eligibility assessment")
    
    st.info("""
    This helps us:
    - Assess potential Medicaid eligibility
    - Identify planning timeline and strategies
    - Connect you with Medicaid planning specialists
    - Understand lookback period concerns
    """)
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_medicaid_navigation" not in st.session_state:
        st.session_state.cost_v2_medicaid_navigation = {
            "medicaid_interest": "learning",
            "medicaid_state": "",
            "marital_status": "single",
            "countable_assets": 0,
            "monthly_income": 0,
            "when_need_care": "not_sure",
            "lookback_concern": False,
            "recent_transfers_amount": 0,
            "needs_medicaid_attorney": False,
            "needs_application_help": False,
            "protect_spouse": False
        }
    
    # Current Status Section
    st.markdown("## 📋 Current Medicaid Status")
    
    medicaid_interest = st.selectbox(
        "Medicaid Interest Level",
        options=["not_interested", "learning", "may_need_soon", "need_now", "already_enrolled"],
        format_func=lambda x: {
            "not_interested": "Not interested",
            "learning": "Just learning about it",
            "may_need_soon": "May need within 1-2 years",
            "need_now": "Need to apply soon",
            "already_enrolled": "Already enrolled"
        }[x],
        index=["not_interested", "learning", "may_need_soon", "need_now", "already_enrolled"].index(
            st.session_state.cost_v2_medicaid_navigation["medicaid_interest"]
        ),
        key="medicaid_interest"
    )
    
    medicaid_state = ""
    marital_status = "single"
    countable_assets = 0
    monthly_income = 0
    when_need_care = "not_sure"
    lookback_concern = False
    recent_transfers_amount = 0
    needs_medicaid_attorney = False
    needs_application_help = False
    protect_spouse = False
    preliminary_eligible = False
    
    if medicaid_interest != "not_interested":
        medicaid_state = st.text_input(
            "State of Residence (e.g., CA, NY, FL)",
            value=st.session_state.cost_v2_medicaid_navigation["medicaid_state"],
            max_chars=2,
            help="Medicaid rules vary by state",
            key="medicaid_state"
        )
        
        st.markdown("---")
        
        # Asset Assessment Section
        st.markdown("## 💰 Asset & Income Assessment")
        st.caption("Preliminary Medicaid eligibility screening")
        
        marital_status = st.selectbox(
            "Marital Status",
            options=["single", "married", "widowed", "divorced"],
            format_func=lambda x: x.capitalize(),
            index=["single", "married", "widowed", "divorced"].index(
                st.session_state.cost_v2_medicaid_navigation["marital_status"]
            ),
            help="Affects asset and income limits",
            key="marital_status"
        )
        
        countable_assets = st.number_input(
            "Estimated Countable Assets (excluding home, car, prepaid funeral)",
            min_value=0,
            max_value=10000000,
            step=5000,
            value=st.session_state.cost_v2_medicaid_navigation["countable_assets"],
            help="Assets that count toward Medicaid limits (typically $2,000 for individual, $3,000 for couple)",
            key="countable_assets"
        )
        
        monthly_income = st.number_input(
            "Total Monthly Income",
            min_value=0,
            max_value=50000,
            step=100,
            value=st.session_state.cost_v2_medicaid_navigation["monthly_income"],
            help="Total monthly income from all sources",
            key="monthly_income"
        )
        
        # Preliminary eligibility calculation
        # Simplified: Individual asset limit $2,000, income limit ~$2,829
        asset_limit = 3000 if marital_status == "married" else 2000
        income_limit = 2829  # Approximate 2025 limit
        
        preliminary_eligible = (countable_assets <= asset_limit) and (monthly_income <= income_limit)
        
        if preliminary_eligible:
            st.success("""
            ✅ **You may be eligible for Medicaid** based on preliminary screening. 
            Assets and income appear to be within typical limits.
            """)
        else:
            st.warning(f"""
            ⚠️ **You may be over Medicaid asset/income limits** based on preliminary screening. 
            
            **However, Medicaid planning strategies may help you qualify:**
            
            - Spend-down strategies
            - Asset transfers (with proper timing)
            - Income trusts
            - Spousal protections
            
            💡 We can connect you with Medicaid planning specialists.
            
            **Your preliminary assessment:**
            - Countable assets: ${countable_assets:,.0f} (Limit: ${asset_limit:,.0f})
            - Monthly income: ${monthly_income:,.0f} (Limit: ${income_limit:,.0f})
            """)
        
        st.markdown("---")
        
        # Planning Timeline Section
        st.markdown("## 📅 Planning Timeline")
        
        when_need_care = st.selectbox(
            "When do you anticipate needing Medicaid coverage?",
            options=["immediate", "within_6_months", "6_12_months", "1_2_years", "2_plus_years", "not_sure"],
            format_func=lambda x: {
                "immediate": "Immediately",
                "within_6_months": "Within 6 months",
                "6_12_months": "6-12 months",
                "1_2_years": "1-2 years",
                "2_plus_years": "2+ years",
                "not_sure": "Not sure"
            }[x],
            index=["immediate", "within_6_months", "6_12_months", "1_2_years", "2_plus_years", "not_sure"].index(
                st.session_state.cost_v2_medicaid_navigation["when_need_care"]
            ),
            key="when_need_care"
        )
        
        lookback_concern = st.checkbox(
            "Have you transferred assets in the past 5 years?",
            value=st.session_state.cost_v2_medicaid_navigation["lookback_concern"],
            help="Medicaid has a 5-year lookback period for asset transfers",
            key="lookback_concern"
        )
        
        if lookback_concern:
            recent_transfers_amount = st.number_input(
                "Approximate Value of Transfers",
                min_value=0,
                max_value=10000000,
                step=10000,
                value=st.session_state.cost_v2_medicaid_navigation["recent_transfers_amount"],
                help="Total value of gifts or asset transfers in past 5 years",
                key="recent_transfers_amount"
            )
            
            st.warning("""
            ⚠️ **5-Year Lookback Period:**
            
            Medicaid reviews all asset transfers made within 5 years of application. 
            Transfers may result in a penalty period where you're ineligible for coverage.
            
            **However, certain transfers are exempt:**
            - Transfers to spouse
            - Transfers to disabled child
            - Home transfers to caregiver child
            
            💡 A Medicaid planning specialist can review your transfers and calculate any penalty period.
            """)
        
        st.markdown("---")
        
        # Next Steps Section
        st.markdown("## 🎯 Next Steps & Support")
        
        needs_medicaid_attorney = st.checkbox(
            "Would you like to connect with a Medicaid planning attorney?",
            value=st.session_state.cost_v2_medicaid_navigation["needs_medicaid_attorney"],
            help="Specialists in asset protection and Medicaid qualification",
            key="needs_medicaid_attorney"
        )
        
        needs_application_help = st.checkbox(
            "Do you need help with the Medicaid application?",
            value=st.session_state.cost_v2_medicaid_navigation["needs_application_help"],
            help="Application assistance and document preparation",
            key="needs_application_help"
        )
        
        if marital_status == "married":
            protect_spouse = st.checkbox(
                "Need to protect spouse's financial security?",
                value=st.session_state.cost_v2_medicaid_navigation["protect_spouse"],
                help="Spousal impoverishment protections",
                key="protect_spouse"
            )
    
    st.markdown("---")
    
    # Summary
    if medicaid_interest != "not_interested":
        st.markdown("## 📊 Medicaid Navigation Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Interest Level", {
                "not_interested": "Not interested",
                "learning": "Learning",
                "may_need_soon": "May need soon",
                "need_now": "Need now",
                "already_enrolled": "Enrolled"
            }[medicaid_interest])
        
        with col2:
            st.metric("Timeline", {
                "immediate": "Immediate",
                "within_6_months": "< 6 months",
                "6_12_months": "6-12 months",
                "1_2_years": "1-2 years",
                "2_plus_years": "2+ years",
                "not_sure": "Not sure"
            }[when_need_care])
        
        if preliminary_eligible:
            st.success("✅ **Preliminary Assessment:** May be eligible")
        else:
            st.info("💡 **Preliminary Assessment:** May need planning strategies")
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🏠 Back to Hub", key="medicaid_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    with col2:
        if st.button("← Back to Modules", key="medicaid_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col3:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="medicaid_save"):
            # Save data to module state
            data = {
                "medicaid_interest": medicaid_interest,
                "medicaid_state": medicaid_state,
                "marital_status": marital_status,
                "countable_assets": countable_assets,
                "monthly_income": monthly_income,
                "preliminary_eligible": preliminary_eligible,
                "when_need_care": when_need_care,
                "lookback_concern": lookback_concern,
                "recent_transfers_amount": recent_transfers_amount,
                "needs_medicaid_attorney": needs_medicaid_attorney,
                "needs_application_help": needs_application_help,
                "protect_spouse": protect_spouse
            }
            
            # Update session state
            st.session_state.cost_v2_medicaid_navigation = data
            
            # Mark module complete
            if "cost_v2_modules" not in st.session_state:
                st.session_state.cost_v2_modules = {}
            
            st.session_state.cost_v2_modules["medicaid_navigation"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ Medicaid Navigation saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")
