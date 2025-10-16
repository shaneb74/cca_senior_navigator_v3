"""Exit Step - Cost Planner v2 (Redesigned)

Final celebration and next steps page.
Clean, calm completion with clear actionable next steps.

Design Philosophy:
- Celebrate completion in a calm, confident way
- Summarize accomplishments clearly
- Offer actionable next steps
- Visually cohesive with Expert Advisor Review
"""

from typing import Dict
import streamlit as st
from core.ui import render_navi_panel_v2


def render():
    """Render exit step with clean card-based completion layout.
    
    Layout:
    1. Navi Panel (celebratory, encouraging)
    2. Accomplishments Card (checklist of completed items)
    3. Plan Highlights Card (key metrics summary)
    4. What's Next Grid (3 actionable paths)
    5. Footer Navigation
    """
    
    _render_navi_completion()
    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
    
    st.markdown("## 🎯 Your Financial Plan is Complete")
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    
    _render_accomplishments_card()
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    
    _render_plan_highlights_card()
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    
    _render_whats_next_section()
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    
    _render_footer_navigation()


def _render_navi_completion():
    """Render Navi panel with celebratory, encouraging tone."""
    
    render_navi_panel_v2(
        title="Your Financial Plan is Complete!",
        reason="You've completed your financial plan — great work! You can download a copy, share it with your family, or meet with an advisor to review it together. Everything you've entered is saved and ready for next steps.",
        encouragement={
            "icon": "💡",
            "message": "The more details you add over time, the clearer your plan becomes — and I'll keep helping you update it whenever you need.",
            "status": "complete"
        },
        context_chips=[
            {"label": "All modules completed"},
            {"label": "Ready to download or share"}
        ],
        primary_action=None  # No action in Navi here
    )


def _render_accomplishments_card():
    """Render accomplishments checklist card."""
    
    st.markdown('<div class="completion-card">', unsafe_allow_html=True)
    st.markdown("### ✔️ Summary of What You've Accomplished")
    
    accomplishments = [
        "Authenticated and secured your account",
        "Completed your Guided Care Plan",
        "Assessed income and available assets",
        "Calculated care costs and coverage",
        "Reviewed your financial runway",
        "Had expert review of your financial plan"
    ]
    
    for item in accomplishments:
        st.markdown(f'<div class="accomplishment-item">• {item}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_plan_highlights_card():
    """Render plan highlights summary card."""
    
    st.markdown('<div class="completion-card">', unsafe_allow_html=True)
    st.markdown("### 💡 Plan Highlights")
    
    # Get care recommendation
    from core.mcip import MCIP
    recommendation = MCIP.get_care_recommendation()
    
    # Get financial metrics
    metrics = _calculate_completion_metrics()
    
    # Display highlights
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        if recommendation:
            tier_label = recommendation.tier.replace("_", " ").title()
            confidence_pct = int(recommendation.confidence * 100)
            st.markdown(f"**Recommended Care Plan:** {tier_label}")
            st.markdown(f"**Confidence Level:** {confidence_pct}%")
        else:
            st.markdown("**Recommended Care Plan:** Not set")
            st.markdown("**Confidence Level:** —")
    
    with col2:
        st.markdown(f"**Monthly Care Cost:** ${metrics['monthly_cost']:,.0f}")
        if metrics['monthly_gap'] >= 0:
            st.markdown(f"**Monthly Surplus:** +${metrics['monthly_gap']:,.0f}")
        else:
            st.markdown(f"**Monthly Gap:** ${abs(metrics['monthly_gap']):,.0f}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def _calculate_completion_metrics() -> Dict:
    """Calculate financial metrics for completion summary.
    
    Returns dict with:
    - monthly_cost
    - monthly_coverage
    - monthly_gap (positive = surplus, negative = shortfall)
    - total_assets
    """
    
    modules = st.session_state.get("cost_v2_modules", {})
    
    # Get module data
    income_data = modules.get("income", {}).get("data", {})
    assets_data = modules.get("assets", {}).get("data", {})
    va_data = modules.get("va_benefits", {}).get("data", {})
    insurance_data = modules.get("health_insurance", {}).get("data", {})
    life_insurance_data = modules.get("life_insurance", {}).get("data", {})
    
    # Calculate total monthly income
    total_monthly_income = (
        income_data.get("ss_monthly", 0) +
        income_data.get("pension_monthly", 0) +
        income_data.get("employment_monthly", 0) +
        income_data.get("investment_monthly", 0) +
        income_data.get("other_monthly", 0) +
        (va_data.get("va_disability_monthly", 0) if va_data else 0) +
        (va_data.get("aid_attendance_monthly", 0) if va_data else 0)
    )
    
    # Calculate total assets
    total_assets = (
        assets_data.get("checking_savings", 0) +
        assets_data.get("investment_accounts", 0) +
        assets_data.get("primary_residence_value", 0) +
        assets_data.get("other_real_estate", 0) +
        assets_data.get("other_resources", 0)
    )
    
    # Get monthly care cost from MCIP
    from core.mcip import MCIP
    estimated_monthly_cost = 0
    recommendation = MCIP.get_care_recommendation()
    
    financial_profile = MCIP.get_financial_profile()
    if financial_profile and hasattr(financial_profile, 'estimated_monthly_cost'):
        estimated_monthly_cost = financial_profile.estimated_monthly_cost
    elif recommendation:
        tier_defaults = {
            'independent': 2500,
            'in_home': 4500,
            'assisted_living': 5000,
            'memory_care': 7000,
            'memory_care_high_acuity': 9000
        }
        estimated_monthly_cost = tier_defaults.get(recommendation.tier, 5000)
    
    # Calculate total coverage
    total_coverage = (
        (insurance_data.get("ltc_daily_benefit", 0) * 30 if insurance_data and insurance_data.get("has_ltc_insurance") else 0) +
        (life_insurance_data.get("monthly_benefit", 0) if life_insurance_data else 0)
    )
    
    # Calculate gap
    monthly_coverage = total_monthly_income + total_coverage
    monthly_gap = monthly_coverage - estimated_monthly_cost
    
    return {
        "monthly_cost": estimated_monthly_cost,
        "monthly_coverage": monthly_coverage,
        "monthly_gap": monthly_gap,
        "total_assets": total_assets
    }


def _render_whats_next_section():
    """Render What's Next section with 3-column grid."""
    
    st.markdown("## 🚀 What's Next")
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    
    # 3-column grid
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown('<div class="next-step-card">', unsafe_allow_html=True)
        st.markdown("### 📅 Meet with an Advisor")
        st.markdown("Review your plan with a certified senior care advisor")
        if st.button("Schedule Meeting", use_container_width=True, type="primary", key="schedule_advisor_btn"):
            from core.nav import route_to
            st.session_state.cost_planner_v2_complete = True
            route_to("pfma_v2")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="next-step-card">', unsafe_allow_html=True)
        st.markdown("### 📄 Download Your Plan")
        st.markdown("Get a PDF copy of your comprehensive financial plan")
        if st.button("Download PDF", use_container_width=True, key="download_pdf_btn"):
            st.info("📄 PDF generation coming soon!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="next-step-card">', unsafe_allow_html=True)
        st.markdown("### 🏠 Return to Hub")
        st.markdown("Explore other tools and resources in your dashboard")
        if st.button("Go to Hub", use_container_width=True, key="goto_hub_btn"):
            from core.nav import route_to
            st.session_state.cost_planner_v2_complete = True
            route_to("hub_concierge")
        st.markdown('</div>', unsafe_allow_html=True)


def _render_footer_navigation():
    """Render footer navigation with additional options."""
    
    st.markdown("---")
    
    # Footer with auto-save message
    st.caption("✅ Your progress is automatically saved")
    
    # Three-column layout for buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Start Over", use_container_width=True, key="start_over_btn"):
            # Show confirmation
            st.session_state.cost_v2_show_restart_confirm = True
            st.rerun()
    
    with col2:
        if st.button("💾 Save Changes", use_container_width=True, key="save_changes_btn"):
            st.success("✅ All changes are automatically saved!")
    
    with col3:
        if st.button("🏠 Back to Hub", use_container_width=True, key="back_hub_btn"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    # Restart confirmation modal (if triggered)
    if st.session_state.get("cost_v2_show_restart_confirm", False):
        st.markdown("---")
        st.warning("⚠️ **Are you sure you want to start over?** This will clear all your financial assessment data.")
        
        col_confirm1, col_confirm2 = st.columns(2)
        with col_confirm1:
            if st.button("Yes, Clear All Data", type="primary", use_container_width=True, key="confirm_restart"):
                _clear_all_data()
                st.session_state.cost_v2_show_restart_confirm = False
                st.success("✅ Data cleared! Restarting...")
                st.rerun()
        
        with col_confirm2:
            if st.button("Cancel", use_container_width=True, key="cancel_restart"):
                st.session_state.cost_v2_show_restart_confirm = False
                st.rerun()


def _clear_all_data():
    """Clear all Cost Planner v2 session data."""
    keys_to_clear = [
        "cost_v2_step",
        "cost_v2_guest_mode",
        "cost_v2_triage",
        "cost_v2_current_module",
        "cost_v2_modules",
        "cost_v2_income",
        "cost_v2_assets",
        "cost_v2_va_benefits",
        "cost_v2_health_insurance",
        "cost_v2_life_insurance",
        "cost_v2_medicaid_navigation",
        "cost_v2_advisor_notes",
        "cost_v2_schedule_advisor",
        "cost_v2_show_restart_confirm",
        "cost_planner_v2_published",
        "cost_planner_v2_complete"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset to intro step
    st.session_state.cost_v2_step = "intro"
