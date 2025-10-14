"""Exit Step - Cost Planner v2

Final summary and handoff to next product (PFMA or Hub).

This is the final step of the Cost Planner v2 workflow.
"""

import streamlit as st
from typing import Dict


def render():
    """Render exit step with final summary and next actions.
    
    Shows:
    - Completion message
    - Summary of financial plan
    - Next recommended actions
    - Navigation options (PFMA, Hub, Download PDF)
    """
    
    st.markdown("# ✅ Your Financial Plan is Complete!")
    
    # Check if advisor meeting requested
    schedule_advisor = st.session_state.get("cost_v2_schedule_advisor", False)
    
    if schedule_advisor:
        _render_advisor_handoff()
    else:
        _render_standard_completion()
    
    st.markdown("---")
    
    _render_summary_highlights()
    
    st.markdown("---")
    
    _render_next_actions()


def _render_advisor_handoff():
    """Render advisor scheduling handoff message."""
    
    st.success("### 📅 Ready to Schedule Your Advisor Meeting")
    
    st.markdown("""
    Your complete financial plan is ready for review with one of our certified elder care advisors.
    
    **What to expect in your meeting:**
    - Review of your complete financial assessment
    - Discussion of funding strategies and options
    - Guidance on insurance and benefits optimization
    - Long-term care planning recommendations
    - Answers to all your questions
    
    **Meeting duration:** 45-60 minutes  
    **Format:** Video call or phone  
    **Cost:** Complimentary for Senior Navigator members
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("📅 Schedule Advisor Meeting Now", type="primary", use_container_width=True):
            # Route to PFMA (Plan with My Advisor)
            from core.nav import route_to
            st.session_state.cost_planner_v2_complete = True
            route_to("pfma")
    
    with col2:
        if st.button("Maybe Later", use_container_width=True):
            st.session_state.cost_v2_schedule_advisor = False
            st.rerun()


def _render_standard_completion():
    """Render standard completion message."""
    
    st.success("### 🎉 Congratulations!")
    
    st.markdown("""
    You've completed your comprehensive financial assessment for senior care.
    
    **What you've accomplished:**
    - ✅ Authenticated and secured your account
    - ✅ Completed your Guided Care Plan
    - ✅ Assessed your income and available assets
    - ✅ Calculated detailed monthly care costs
    - ✅ Reviewed coverage from all sources
    - ✅ Identified your financial gap and runway
    - ✅ Had expert review of your complete plan
    
    Your financial plan is saved and ready to share with family or advisors.
    """)


def _render_summary_highlights():
    """Render key highlights from financial plan."""
    
    st.markdown("### 📊 Your Financial Plan Highlights")
    
    # Get module data
    modules = st.session_state.get("cost_v2_modules", {})
    income_data = modules.get("income_assets", {}).get("data", {})
    costs_data = modules.get("monthly_costs", {}).get("data", {})
    coverage_data = modules.get("coverage", {}).get("data", {})
    
    if not all([income_data, costs_data, coverage_data]):
        st.warning("⚠️ Financial data incomplete. Please return to modules to complete your assessment.")
        return
    
    # Calculate key metrics
    total_monthly_income = income_data.get("total_monthly_income", 0)
    total_assets = income_data.get("total_assets", 0)
    total_monthly_cost = costs_data.get("total_monthly_cost", 0)
    total_coverage = coverage_data.get("total_coverage", 0)
    
    monthly_gap = total_monthly_cost - total_coverage - total_monthly_income
    
    # Display in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Monthly Cost",
            value=f"${total_monthly_cost:,.0f}",
            help="Total monthly care costs"
        )
    
    with col2:
        st.metric(
            label="Coverage + Income",
            value=f"${total_coverage + total_monthly_income:,.0f}",
            help="Monthly income and benefits"
        )
    
    with col3:
        if monthly_gap > 0:
            st.metric(
                label="Monthly Gap",
                value=f"${monthly_gap:,.0f}",
                delta=f"-${monthly_gap:,.0f}",
                delta_color="inverse"
            )
        else:
            st.metric(
                label="Monthly Surplus",
                value=f"${abs(monthly_gap):,.0f}",
                delta=f"+${abs(monthly_gap):,.0f}"
            )
    
    with col4:
        st.metric(
            label="Total Assets",
            value=f"${total_assets:,.0f}",
            help="Available assets"
        )
    
    # Financial runway
    if monthly_gap > 0 and total_assets > 0:
        runway_months = int(total_assets / monthly_gap)
        runway_years = runway_months / 12
        
        st.markdown("")
        
        if runway_years < 2:
            st.error(f"⚠️ **Financial Runway:** {runway_years:.1f} years - Consider discussing funding options with an advisor")
        elif runway_years < 5:
            st.warning(f"⚠️ **Financial Runway:** {runway_years:.1f} years - Review asset liquidation timeline")
        else:
            st.success(f"✅ **Financial Runway:** {runway_years:.1f} years")
    elif monthly_gap <= 0:
        st.success("✅ **Fully Funded:** Your income and benefits cover all monthly costs!")
    
    # Advisor notes (if any)
    advisor_notes = st.session_state.get("cost_v2_advisor_notes", "")
    if advisor_notes:
        st.markdown("---")
        st.markdown("### 📝 Your Notes")
        st.info(advisor_notes)


def _render_next_actions():
    """Render next action buttons."""
    
    st.markdown("### 🎯 What's Next?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📅 Meet with Advisor")
        st.markdown("Review your plan with a certified elder care advisor")
        if st.button("Schedule Meeting", key="schedule_pfma", use_container_width=True, type="primary"):
            from core.nav import route_to
            st.session_state.cost_planner_v2_complete = True
            route_to("pfma")
    
    with col2:
        st.markdown("#### 📄 Download Plan")
        st.markdown("Get a PDF copy of your complete financial plan")
        if st.button("Download PDF", key="download_pdf", use_container_width=True):
            st.info("📄 PDF generation coming soon!")
            # TODO: Implement PDF generation
    
    with col3:
        st.markdown("#### 🏠 Return to Hub")
        st.markdown("Explore other tools and resources")
        if st.button("Go to Hub", key="goto_hub", use_container_width=True):
            from core.nav import route_to
            st.session_state.cost_planner_v2_complete = True
            route_to("hub_concierge")
    
    st.markdown("---")
    
    # Additional options
    with st.expander("📧 Share Your Plan"):
        st.markdown("**Email your financial plan to family members or advisors**")
        
        email = st.text_input("Email address:", placeholder="example@email.com")
        message = st.text_area("Optional message:", placeholder="Here's my senior care financial plan...")
        
        if st.button("Send Email", key="send_email"):
            if email:
                st.info(f"📧 Email functionality coming soon! Would send to: {email}")
                # TODO: Implement email functionality
            else:
                st.error("Please enter an email address")
    
    with st.expander("🔄 Start Over"):
        st.warning("**Warning:** This will clear all your financial assessment data and start fresh.")
        if st.button("Clear All Data & Restart", key="restart_cost_planner"):
            _clear_all_data()
            st.success("✅ Data cleared! Redirecting to intro...")
            st.rerun()


def _clear_all_data():
    """Clear all Cost Planner v2 session data."""
    keys_to_clear = [
        "cost_v2_step",
        "cost_v2_guest_mode",
        "cost_v2_triage",
        "cost_v2_current_module",
        "cost_v2_modules",
        "cost_v2_income_assets",
        "cost_v2_monthly_costs",
        "cost_v2_coverage",
        "cost_v2_advisor_notes",
        "cost_v2_schedule_advisor",
        "cost_planner_v2_published",
        "cost_planner_v2_complete"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset to intro step
    st.session_state.cost_v2_step = "intro"
