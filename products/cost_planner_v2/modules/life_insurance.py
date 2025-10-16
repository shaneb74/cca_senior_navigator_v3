"""
Cost Planner v2 - Life Insurance Module

Collects information about:
- Life insurance policies
- Policy types and death benefits
- Cash value and surrender options
- Policy options for care costs (accelerated death benefit, LTC riders)

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any


def render():
    """Render life insurance assessment module."""
    
    st.title("🛡️ Life Insurance")
    st.markdown("### Life insurance policies and cash value")
    
    st.info("""
    This helps us understand:
    - Life insurance policies you have
    - Cash value that may be available for care costs
    - Policy options to help fund care (riders, settlements)
    """)
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_life_insurance" not in st.session_state:
        st.session_state.cost_v2_life_insurance = {
            "has_life_insurance": False,
            "policy_count": "1",
            "policy_type": "whole",
            "death_benefit": 0,
            "has_cash_value": False,
            "cash_value": 0,
            "monthly_premium": 0,
            "accelerated_death_benefit": False,
            "ltc_rider": False,
            "considering_life_settlement": False
        }
    
    # Policies Section
    st.markdown("## 📋 Life Insurance Policies")
    st.caption("Information about current life insurance coverage")
    
    has_life_insurance = st.checkbox(
        "Do you have life insurance?",
        value=st.session_state.cost_v2_life_insurance["has_life_insurance"],
        key="has_life_insurance"
    )
    
    policy_count = "1"
    policy_type = "whole"
    death_benefit = 0
    has_cash_value = False
    cash_value = 0
    monthly_premium = 0
    accelerated_death_benefit = False
    ltc_rider = False
    considering_life_settlement = False
    
    if has_life_insurance:
        policy_count = st.selectbox(
            "Number of Policies",
            options=["1", "2", "3"],
            format_func=lambda x: f"{x} {'policy' if x == '1' else 'policies'}" if x != "3" else "3+ policies",
            index=["1", "2", "3"].index(
                st.session_state.cost_v2_life_insurance["policy_count"]
            ),
            key="policy_count"
        )
        
        st.markdown("---")
        
        # Primary Policy Details
        st.markdown("## 📄 Primary Policy Details")
        
        policy_type = st.selectbox(
            "Policy Type",
            options=["term", "whole", "universal", "variable", "not_sure"],
            format_func=lambda x: {
                "term": "Term Life",
                "whole": "Whole Life",
                "universal": "Universal Life",
                "variable": "Variable Life",
                "not_sure": "Not sure"
            }[x],
            index=["term", "whole", "universal", "variable", "not_sure"].index(
                st.session_state.cost_v2_life_insurance["policy_type"]
            ),
            key="policy_type"
        )
        
        death_benefit = st.number_input(
            "Death Benefit (Face Value)",
            min_value=0,
            max_value=10000000,
            step=10000,
            value=st.session_state.cost_v2_life_insurance["death_benefit"],
            help="Total payout amount upon death",
            key="death_benefit"
        )
        
        if policy_type != "term":
            has_cash_value = st.checkbox(
                "Does this policy have cash value?",
                value=st.session_state.cost_v2_life_insurance["has_cash_value"],
                help="Whole, universal, and variable life policies build cash value",
                key="has_cash_value"
            )
            
            if has_cash_value:
                cash_value = st.number_input(
                    "Current Cash Value",
                    min_value=0,
                    max_value=5000000,
                    step=1000,
                    value=st.session_state.cost_v2_life_insurance["cash_value"],
                    help="Current cash surrender value",
                    key="cash_value"
                )
        
        monthly_premium = st.number_input(
            "Monthly Premium",
            min_value=0,
            max_value=5000,
            step=10,
            value=st.session_state.cost_v2_life_insurance["monthly_premium"],
            help="Current monthly premium payment",
            key="monthly_premium"
        )
        
        st.markdown("---")
        
        # Policy Options Section
        st.markdown("## 💡 Policy Options for Care Costs")
        
        accelerated_death_benefit = st.checkbox(
            "Does your policy have an Accelerated Death Benefit rider?",
            value=st.session_state.cost_v2_life_insurance["accelerated_death_benefit"],
            help="Allows access to death benefit while living if terminally or chronically ill",
            key="accelerated_death_benefit"
        )
        
        ltc_rider = st.checkbox(
            "Does your policy have a Long-Term Care rider?",
            value=st.session_state.cost_v2_life_insurance["ltc_rider"],
            help="Allows use of death benefit for long-term care expenses",
            key="ltc_rider"
        )
        
        considering_life_settlement = st.checkbox(
            "Would you consider a life settlement (selling policy)?",
            value=st.session_state.cost_v2_life_insurance["considering_life_settlement"],
            help="Selling policy to investor for more than cash value but less than death benefit",
            key="considering_life_settlement"
        )
        
        st.info("""
        💡 **Using Life Insurance for Care Costs:**
        
        - **Cash Value:** Can borrow against or surrender for immediate funds
        - **Accelerated Death Benefit:** Access 25-95% of death benefit if terminally ill
        - **LTC Rider:** Use death benefit to pay for long-term care
        - **Life Settlement:** Sell policy for lump sum (typically 10-25% of death benefit)
        
        ⚠️ **Important:** These options reduce or eliminate the death benefit for beneficiaries.
        """)
    
    st.markdown("---")
    
    # Summary
    if has_life_insurance:
        st.markdown("## 📊 Life Insurance Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Death Benefit", f"${death_benefit:,.0f}")
        
        with col2:
            if has_cash_value:
                st.metric("Cash Value", f"${cash_value:,.0f}")
            else:
                st.metric("Cash Value", "N/A")
        
        with col3:
            st.metric("Monthly Premium", f"${monthly_premium:,.0f}")
        
        # Policy options summary
        policy_options = []
        if accelerated_death_benefit:
            policy_options.append("Accelerated Death Benefit")
        if ltc_rider:
            policy_options.append("Long-Term Care Rider")
        
        if policy_options:
            st.success(f"✅ **Available Options:** {', '.join(policy_options)}")
        
        if considering_life_settlement and death_benefit > 0:
            estimated_settlement = death_benefit * 0.15  # Rough estimate: 15% of death benefit
            st.info(f"""
            💡 **Estimated Life Settlement Value:** ${estimated_settlement:,.0f}
            
            (Typically 10-25% of death benefit, varies by age and health)
            """)
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🏠 Back to Hub", key="life_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    with col2:
        if st.button("← Back to Modules", key="life_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col3:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="life_save"):
            # Save data to module state
            data = {
                "has_life_insurance": has_life_insurance,
                "policy_count": policy_count,
                "policy_type": policy_type,
                "death_benefit": death_benefit,
                "has_cash_value": has_cash_value,
                "cash_value": cash_value,
                "monthly_premium": monthly_premium,
                "accelerated_death_benefit": accelerated_death_benefit,
                "ltc_rider": ltc_rider,
                "considering_life_settlement": considering_life_settlement
            }
            
            # Update session state
            st.session_state.cost_v2_life_insurance = data
            
            # Mark module complete
            if "cost_v2_modules" not in st.session_state:
                st.session_state.cost_v2_modules = {}
            
            st.session_state.cost_v2_modules["life_insurance"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ Life Insurance saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")
