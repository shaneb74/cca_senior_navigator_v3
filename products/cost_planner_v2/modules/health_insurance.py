"""
Cost Planner v2 - Health Insurance Module

Collects information about:
- Medicare coverage (Parts A, B, C, D, supplements)
- Medicaid enrollment
- Long-Term Care insurance
- Private health insurance

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any


def render():
    """Render health insurance assessment module."""
    
    st.title("🏥 Health Insurance")
    st.markdown("### Medicare, Medicaid, and other health coverage")
    
    st.info("""
    This helps us understand:
    - Your current health insurance coverage
    - What costs may be covered by insurance
    - Long-term care insurance benefits available
    """)
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_health_insurance" not in st.session_state:
        st.session_state.cost_v2_health_insurance = {
            "has_medicare": False,
            "medicare_parts": [],
            "medicare_advantage": False,
            "medicare_supplement": False,
            "medicare_monthly_premium": 0,
            "has_medicaid": False,
            "medicaid_status": "enrolled",
            "medicaid_covers_ltc": False,
            "medicaid_monthly_coverage": 0,
            "has_ltc_insurance": False,
            "ltc_provider": "",
            "ltc_daily_benefit": 0,
            "ltc_elimination_period": "90",
            "ltc_benefit_period": "3",
            "ltc_monthly_premium": 0,
            "has_private_insurance": False,
            "private_insurance_type": "employer",
            "private_insurance_monthly_premium": 0
        }
    
    # Medicare Section
    st.markdown("## 🏥 Medicare Coverage")
    st.caption("Federal health insurance for seniors 65+")
    
    has_medicare = st.checkbox(
        "Are you enrolled in Medicare?",
        value=st.session_state.cost_v2_health_insurance["has_medicare"],
        key="has_medicare"
    )
    
    medicare_parts = []
    medicare_advantage = False
    medicare_supplement = False
    medicare_monthly_premium = 0
    
    if has_medicare:
        medicare_parts = st.multiselect(
            "Medicare Parts",
            options=["part_a", "part_b", "part_d"],
            default=st.session_state.cost_v2_health_insurance.get("medicare_parts", []),
            format_func=lambda x: {
                "part_a": "Part A (Hospital Insurance)",
                "part_b": "Part B (Medical Insurance)",
                "part_d": "Part D (Prescription Drug)"
            }[x],
            key="medicare_parts"
        )
        
        medicare_advantage = st.checkbox(
            "Do you have Medicare Advantage (Part C)?",
            value=st.session_state.cost_v2_health_insurance["medicare_advantage"],
            key="medicare_advantage"
        )
        
        medicare_supplement = st.checkbox(
            "Do you have a Medigap (Supplement) plan?",
            value=st.session_state.cost_v2_health_insurance["medicare_supplement"],
            key="medicare_supplement"
        )
        
        medicare_monthly_premium = st.number_input(
            "Total Monthly Medicare Premiums (Parts B, D, Advantage, or Supplement)",
            min_value=0,
            max_value=1000,
            step=10,
            value=st.session_state.cost_v2_health_insurance["medicare_monthly_premium"],
            help="Total monthly premium you pay for all Medicare coverage",
            key="medicare_monthly_premium"
        )
        
        st.info("ℹ️ **Important:** Medicare does **not** typically cover long-term care costs in assisted living or memory care facilities. It may cover short-term skilled nursing care following hospitalization.")
    
    st.markdown("---")
    
    # Medicaid Section
    st.markdown("## 🏛️ Medicaid Coverage")
    st.caption("State/federal health program for those with limited income")
    
    has_medicaid = st.checkbox(
        "Are you enrolled in Medicaid?",
        value=st.session_state.cost_v2_health_insurance["has_medicaid"],
        key="has_medicaid"
    )
    
    medicaid_status = "enrolled"
    medicaid_covers_ltc = False
    medicaid_monthly_coverage = 0
    
    if has_medicaid:
        medicaid_status = st.selectbox(
            "Medicaid Status",
            options=["enrolled", "pending", "planning", "not_eligible"],
            format_func=lambda x: {
                "enrolled": "Currently enrolled",
                "pending": "Application pending",
                "planning": "Planning to apply",
                "not_eligible": "Not eligible"
            }[x],
            index=["enrolled", "pending", "planning", "not_eligible"].index(
                st.session_state.cost_v2_health_insurance["medicaid_status"]
            ),
            key="medicaid_status"
        )
        
        if medicaid_status == "enrolled":
            medicaid_covers_ltc = st.checkbox(
                "Does Medicaid cover your long-term care?",
                value=st.session_state.cost_v2_health_insurance["medicaid_covers_ltc"],
                key="medicaid_covers_ltc"
            )
            
            if medicaid_covers_ltc:
                medicaid_monthly_coverage = st.number_input(
                    "Monthly Medicaid Coverage Amount",
                    min_value=0,
                    max_value=10000,
                    step=100,
                    value=st.session_state.cost_v2_health_insurance["medicaid_monthly_coverage"],
                    help="Estimated monthly value of Medicaid coverage",
                    key="medicaid_monthly_coverage"
                )
    else:
        st.success("""
        💡 **Medicaid Planning:** If you're not currently on Medicaid but may need it in the future, 
        we can connect you with specialists who help with Medicaid planning and asset protection strategies.
        """)
    
    st.markdown("---")
    
    # LTC Insurance Section
    st.markdown("## 💼 Long-Term Care Insurance")
    st.caption("Private insurance that covers long-term care costs")
    
    has_ltc_insurance = st.checkbox(
        "Do you have long-term care insurance?",
        value=st.session_state.cost_v2_health_insurance["has_ltc_insurance"],
        key="has_ltc_insurance"
    )
    
    ltc_provider = ""
    ltc_daily_benefit = 0
    ltc_monthly_benefit = 0
    ltc_elimination_period = "90"
    ltc_benefit_period = "3"
    ltc_monthly_premium = 0
    
    if has_ltc_insurance:
        ltc_provider = st.text_input(
            "Insurance Company",
            value=st.session_state.cost_v2_health_insurance["ltc_provider"],
            placeholder="e.g., Genworth, Mutual of Omaha",
            key="ltc_provider"
        )
        
        ltc_daily_benefit = st.number_input(
            "Daily Benefit Amount",
            min_value=0,
            max_value=1000,
            step=10,
            value=st.session_state.cost_v2_health_insurance["ltc_daily_benefit"],
            help="Daily benefit amount from your policy",
            key="ltc_daily_benefit"
        )
        
        ltc_monthly_benefit = ltc_daily_benefit * 30
        st.metric("**Monthly Benefit**", f"${ltc_monthly_benefit:,.0f}")
        
        ltc_elimination_period = st.selectbox(
            "Elimination Period (Waiting Period)",
            options=["0", "30", "60", "90", "100", "180"],
            format_func=lambda x: {
                "0": "No waiting period",
                "30": "30 days",
                "60": "60 days",
                "90": "90 days",
                "100": "100 days",
                "180": "180 days"
            }[x],
            index=["0", "30", "60", "90", "100", "180"].index(
                st.session_state.cost_v2_health_insurance["ltc_elimination_period"]
            ),
            help="Number of days you must pay out-of-pocket before benefits begin",
            key="ltc_elimination_period"
        )
        
        ltc_benefit_period = st.selectbox(
            "Benefit Period",
            options=["2", "3", "4", "5", "lifetime"],
            format_func=lambda x: f"{x} years" if x != "lifetime" else "Lifetime",
            index=["2", "3", "4", "5", "lifetime"].index(
                st.session_state.cost_v2_health_insurance["ltc_benefit_period"]
            ),
            help="How long benefits will be paid",
            key="ltc_benefit_period"
        )
        
        ltc_monthly_premium = st.number_input(
            "Monthly Premium",
            min_value=0,
            max_value=2000,
            step=10,
            value=st.session_state.cost_v2_health_insurance["ltc_monthly_premium"],
            help="Monthly premium you pay for LTC insurance",
            key="ltc_monthly_premium"
        )
    
    st.markdown("---")
    
    # Private Insurance Section
    st.markdown("## 💳 Private Health Insurance")
    st.caption("Employer or private health insurance")
    
    has_private_insurance = st.checkbox(
        "Do you have private health insurance (non-Medicare)?",
        value=st.session_state.cost_v2_health_insurance["has_private_insurance"],
        key="has_private_insurance"
    )
    
    private_insurance_type = "employer"
    private_insurance_monthly_premium = 0
    
    if has_private_insurance:
        private_insurance_type = st.selectbox(
            "Insurance Type",
            options=["employer", "marketplace", "private"],
            format_func=lambda x: {
                "employer": "Employer/Retiree coverage",
                "marketplace": "ACA Marketplace plan",
                "private": "Private individual plan"
            }[x],
            index=["employer", "marketplace", "private"].index(
                st.session_state.cost_v2_health_insurance["private_insurance_type"]
            ),
            key="private_insurance_type"
        )
        
        private_insurance_monthly_premium = st.number_input(
            "Monthly Premium",
            min_value=0,
            max_value=3000,
            step=50,
            value=st.session_state.cost_v2_health_insurance["private_insurance_monthly_premium"],
            help="Monthly premium for private health insurance",
            key="private_insurance_monthly_premium"
        )
    
    st.markdown("---")
    
    # Calculate totals
    total_monthly_premiums = (
        medicare_monthly_premium + ltc_monthly_premium + private_insurance_monthly_premium
    )
    total_monthly_coverage = medicaid_monthly_coverage + ltc_monthly_benefit
    total_net_benefit = total_monthly_coverage - total_monthly_premiums
    
    # Summary
    st.markdown("## 📊 Insurance Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Monthly Coverage", f"${total_monthly_coverage:,.0f}")
    
    with col2:
        st.metric("Monthly Premiums", f"${total_monthly_premiums:,.0f}")
    
    with col3:
        st.metric("Net Monthly Benefit", f"${total_net_benefit:,.0f}")
    
    if total_monthly_coverage > 0 or total_monthly_premiums > 0:
        st.info(f"""
        💡 **Insurance Breakdown:**
        - Medicaid LTC Coverage: ${medicaid_monthly_coverage:,.0f}
        - LTC Insurance Benefit: ${ltc_monthly_benefit:,.0f}
        - Total Premiums: ${total_monthly_premiums:,.0f}
        - **Net Benefit: ${total_net_benefit:,.0f}**
        """)
    
    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🏠 Back to Hub", key="health_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    with col2:
        if st.button("← Back to Modules", key="health_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    with col3:
        if st.button("Save & Continue →", type="primary", use_container_width=True, key="health_save"):
            # Save data to module state
            data = {
                "has_medicare": has_medicare,
                "medicare_parts": medicare_parts,
                "medicare_advantage": medicare_advantage,
                "medicare_supplement": medicare_supplement,
                "medicare_monthly_premium": medicare_monthly_premium,
                "has_medicaid": has_medicaid,
                "medicaid_status": medicaid_status,
                "medicaid_covers_ltc": medicaid_covers_ltc,
                "medicaid_monthly_coverage": medicaid_monthly_coverage,
                "has_ltc_insurance": has_ltc_insurance,
                "ltc_provider": ltc_provider,
                "ltc_daily_benefit": ltc_daily_benefit,
                "ltc_monthly_benefit": ltc_monthly_benefit,
                "ltc_elimination_period": ltc_elimination_period,
                "ltc_benefit_period": ltc_benefit_period,
                "ltc_monthly_premium": ltc_monthly_premium,
                "has_private_insurance": has_private_insurance,
                "private_insurance_type": private_insurance_type,
                "private_insurance_monthly_premium": private_insurance_monthly_premium,
                "total_monthly_insurance_net": total_net_benefit
            }
            
            # Update session state
            st.session_state.cost_v2_health_insurance = data
            
            # Mark module complete
            if "cost_v2_modules" not in st.session_state:
                st.session_state.cost_v2_modules = {}
            
            st.session_state.cost_v2_modules["health_insurance"] = {
                "status": "completed",
                "progress": 100,
                "data": data
            }
            
            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success("✅ Health Insurance saved!")
            st.rerun()
    
    st.caption("💾 Your progress is automatically saved")
