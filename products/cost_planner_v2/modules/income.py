"""
Cost Planner v2 - Income Sources Module

Collects information about:
- Social Security benefits
- Pension income (includes annuities)
- Employment income
- Other income sources

Note: Investment income moved to Assets & Resources module.

Returns standard contract for aggregation.
"""

import streamlit as st
from typing import Dict, Any
from core.ui import render_navi_panel_v2


def render():
    """Render income sources assessment module."""
    
    st.title("💰 Income Sources")
    
    # Navi guidance banner (replaces blue info box)
    render_navi_panel_v2(
        title="Let's review your income together",
        reason="We'll look at your Social Security, pension, and any other income you have coming in each month. Once we've got that, I'll help you figure out what's available for care costs.",
        encouragement={
            "icon": "💡",
            "status": "getting_started",
            "text": "You can expand each section for examples and guidance as you go — I'll keep track of everything for you."
        },
        context_chips=[],
        primary_action={'label': 'Continue', 'action': None},
        variant="module"
    )
    
    st.markdown("---")
    
    # Initialize module state
    if "cost_v2_income" not in st.session_state:
        st.session_state.cost_v2_income = {
            "ss_monthly": 0,
            "pension_monthly": 0,
            "employment_status": "not_employed",
            "employment_monthly": 0,
            "other_monthly": 0
        }
    
    # PRIMARY INCOME GROUP
    st.markdown("### 📦 Primary Income")
    
    # Row 1: Social Security + Pension (using columns)
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<div class="income-card">', unsafe_allow_html=True)
        st.markdown("#### 🏛️ Social Security Benefits")
        st.markdown('<span class="income-caption">Monthly Social Security retirement or disability benefits</span>', unsafe_allow_html=True)
    
        ss_monthly = st.number_input(
            "Monthly Amount",
            min_value=0,
            max_value=5000,
            step=10,
            value=st.session_state.cost_v2_income["ss_monthly"],
            help="Enter the monthly Social Security benefit amount",
            key="ss_monthly"
        )
        
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            - **When to claim:** Age 62 (reduced) vs. 66-67 (full) vs. 70 (max benefit, up to 30% more)
            - **Spousal benefits:** Up to 50% of spouse's benefit if higher than your own
            - **Average 2024:** $1,907/month (retirement), $1,537/month (disability)
            - **Taxable:** 50-85% may be taxable depending on other income
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="income-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Pension & Annuity Income")
        st.markdown('<span class="income-caption">Retirement pension and annuity payments (combined)</span>', unsafe_allow_html=True)
    
        pension_monthly = st.number_input(
            "Monthly Amount",
            min_value=0,
            max_value=20000,
            step=100,
            value=st.session_state.cost_v2_income["pension_monthly"],
            help="Monthly pension or annuity income (combined total)",
            key="pension_monthly"
        )
        
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            - **Lump sum vs. monthly:** Weigh guaranteed income vs. flexibility
            - **Survivor benefits:** Choose the right option to protect your spouse's income
            - **Tax planning:** Pension income is typically fully taxable
            - **Value:** Lifetime guaranteed income is valuable for care planning
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 2: Employment + Other Income (using columns)
    col3, col4 = st.columns(2, gap="large")
    
    with col3:
        st.markdown('<div class="income-card">', unsafe_allow_html=True)
        st.markdown("#### 💼 Employment Income")
        st.markdown('<span class="income-caption">Income from current employment or self-employment</span>', unsafe_allow_html=True)
        
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
                "Monthly Income (after tax)",
                min_value=0,
                max_value=50000,
                step=100,
                value=st.session_state.cost_v2_income["employment_monthly"],
                help="Net monthly income from employment",
                key="employment_monthly"
            )
        
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            - **Social Security impact:** Earnings above $22,320 (2024) may reduce SS benefits if claiming before full retirement age
            - **Part-time work:** Provides income plus social engagement
            - **Healthcare:** Employment may provide insurance before Medicare (age 65)
            - **Flexibility:** Consulting or freelance work offers schedule control
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="income-card">', unsafe_allow_html=True)
        st.markdown("#### 💵 Other Income Sources")
        st.markdown('<span class="income-caption">Family support, trust distributions, VA benefits, etc.</span>', unsafe_allow_html=True)
        
        other_monthly = st.number_input(
            "Monthly Amount",
            min_value=0,
            max_value=50000,
            step=100,
            value=st.session_state.cost_v2_income["other_monthly"],
            help="Family support, trust distributions, VA benefits, other income",
            key="other_monthly"
        )
        
        with st.expander("💡 Quick Guide"):
            st.markdown("""
            - **Family support:** Regular financial help from adult children or family
            - **Trust distributions:** Income from irrevocable or special needs trusts
            - **VA benefits:** Veterans Aid & Attendance can provide $2,431/month (2024)
            - **Reverse mortgage:** Home equity conversion for monthly payments (age 62+)
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get values from session state (they're stored there via the key= parameter)
    ss_monthly = st.session_state.get("ss_monthly", 0)
    pension_monthly = st.session_state.get("pension_monthly", 0)
    employment_status = st.session_state.get("employment_status", "not_employed")
    employment_monthly = st.session_state.get("employment_monthly", 0)
    other_monthly = st.session_state.get("other_monthly", 0)
    
    # Calculate total
    total_monthly_income = (
        ss_monthly + pension_monthly + employment_monthly + other_monthly
    )
    
    # Summary
    st.markdown("### 💰 Total Monthly Income")
    st.metric("**Total Income**", f"${total_monthly_income:,.0f}/month")
    
    if total_monthly_income > 0:
        col1, col2 = st.columns(2)
        with col1:
            if ss_monthly > 0:
                st.caption(f"💰 Social Security: ${ss_monthly:,.0f}")
            if pension_monthly > 0:
                st.caption(f"📊 Pension: ${pension_monthly:,.0f}")
        with col2:
            if employment_monthly > 0:
                st.caption(f"💼 Employment: ${employment_monthly:,.0f}")
            if other_monthly > 0:
                st.caption(f"💵 Other: ${other_monthly:,.0f}")
    
    st.markdown("---")
    
    # Fixed Footer Navigation
    footer_container = st.container()
    with footer_container:
        st.markdown('<div class="fixed-footer-nav">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if st.button("← Back to Modules", key="income_back"):
                st.session_state.cost_v2_step = "modules"
                st.rerun()
        
        with col2:
            if st.button("💾 Save & Continue →", type="primary", use_container_width=True, key="income_save"):
                # Save data to module state
                data = {
                    "ss_monthly": ss_monthly,
                    "pension_monthly": pension_monthly,
                    "employment_status": employment_status,
                    "employment_monthly": employment_monthly,
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
        st.markdown('</div>', unsafe_allow_html=True)
