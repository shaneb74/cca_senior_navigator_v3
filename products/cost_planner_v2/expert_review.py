"""
Expert Financial Review for Cost Planner v2

Clean, professional display of financial analysis with recommendations.
Communication through Navi panel, minimal UI clutter.
"""

from html import escape as H
import streamlit as st

from core.ui import render_navi_panel_v2
from core.mcip import MCIP
from products.cost_planner_v2.financial_profile import get_financial_profile, publish_to_mcip
from products.cost_planner_v2.expert_formulas import calculate_expert_review


def render():
    """
    Render expert financial review page.
    
    Shows financial analysis with clean, professional design.
    Navi handles all communication, UI stays minimal.
    """
    
    # Get financial profile
    profile = get_financial_profile()
    
    # Check if required assessments complete
    if not profile.required_assessments_complete:
        _render_incomplete_state()
        return
    
    # Get GCP recommendation for cost estimation
    care_recommendation = MCIP.get_care_recommendation()
    
    # Get ZIP code from intro
    zip_code = st.session_state.get("cost_v2_zip")
    
    # Calculate expert review
    analysis = calculate_expert_review(
        profile=profile,
        care_recommendation=care_recommendation,
        zip_code=zip_code
    )
    
    # Publish profile to MCIP
    publish_to_mcip(profile)
    
    # Render Navi guidance
    _render_navi_guidance(analysis, profile)
    
    # Main content container
    st.markdown('<div class="sn-app module-container">', unsafe_allow_html=True)
    
    # Page header
    st.markdown('<div class="mod-head"><div class="mod-head-row"><h2 class="h2">💰 Financial Review</h2></div></div>', unsafe_allow_html=True)
    
    # Coverage summary (clean, minimal)
    _render_coverage_summary(analysis)
    
    st.markdown('<div style="margin: 32px 0;"></div>', unsafe_allow_html=True)
    
    # Financial details (simple list)
    _render_financial_details(analysis, profile)
    
    st.markdown('<div style="margin: 32px 0;"></div>', unsafe_allow_html=True)
    
    # Action items (clean list)
    _render_action_items(analysis)
    
    st.markdown('<div style="margin: 48px 0;"></div>', unsafe_allow_html=True)
    
    # Navigation
    _render_navigation()
    
    st.markdown('</div>', unsafe_allow_html=True)



def _render_incomplete_state():
    """Show state when required assessments not complete."""
    
    # Navi communication
    render_navi_panel_v2(
        title="Complete Required Assessments",
        reason="Please complete Income and Assets assessments to see your financial review.",
        encouragement={
            'icon': '📋',
            'text': 'These two assessments are essential for accurate cost analysis.',
            'status': 'active'
        },
        context_chips=[],
        primary_action={'label': '', 'route': ''},
        variant="module"
    )
    
    # Minimal content
    st.markdown('<div class="sn-app module-container">', unsafe_allow_html=True)
    st.markdown('<div class="mod-head"><div class="mod-head-row"><h2 class="h2">💰 Financial Review</h2></div></div>', unsafe_allow_html=True)
    
    st.info("Complete Income and Assets assessments to unlock your personalized financial review.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Assessments", use_container_width=True, type="primary"):
            st.session_state.cost_v2_step = "assessments"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_navi_guidance(analysis, profile):
    """Render Navi panel with contextual guidance based on analysis."""
    
    # Determine message based on coverage tier
    if analysis.coverage_tier == "excellent":
        title = "Excellent Financial Position"
        reason = "Your income and benefits fully cover your estimated care costs. You're well-prepared financially."
        encouragement = {
            'icon': '✅',
            'text': 'Review the recommendations below to optimize your financial strategy.',
            'status': 'complete'
        }
    
    elif analysis.coverage_tier == "good":
        title = "Strong Financial Foundation"
        reason = f"Your income covers {analysis.coverage_percentage:.0f}% of estimated care costs. You have a solid foundation with manageable gaps."
        encouragement = {
            'icon': '👍',
            'text': 'Review the action items below to address the small remaining gap.',
            'status': 'active'
        }
    
    elif analysis.coverage_tier == "moderate":
        title = "Strategic Planning Recommended"
        reason = f"Your income covers {analysis.coverage_percentage:.0f}% of estimated costs. A strategic plan will help bridge the gap."
        encouragement = {
            'icon': '📊',
            'text': 'Focus on the action items below to develop your financial strategy.',
            'status': 'active'
        }
    
    elif analysis.coverage_tier == "concerning":
        title = "Action Needed Soon"
        reason = f"Your income covers {analysis.coverage_percentage:.0f}% of estimated costs. Planning is important to secure sustainable care."
        encouragement = {
            'icon': '⚠️',
            'text': 'Prioritize the action items below—time is important.',
            'status': 'warning'
        }
    
    else:  # critical
        title = "Immediate Planning Essential"
        reason = f"Your income covers {analysis.coverage_percentage:.0f}% of estimated costs. Immediate action is needed to secure care."
        encouragement = {
            'icon': '🚨',
            'text': 'Follow the action items below urgently—help is available.',
            'status': 'warning'
        }
    
    # Context chips
    context_chips = []
    if analysis.runway_months is not None:
        if analysis.runway_months >= 36:
            runway_label = f"{int(analysis.runway_months)} months coverage"
        elif analysis.runway_months >= 12:
            runway_label = f"{int(analysis.runway_months)} months runway"
        else:
            runway_label = f"{int(analysis.runway_months)} months remaining"
        
        context_chips.append({
            'label': runway_label,
            'sublabel': None
        })
    
    render_navi_panel_v2(
        title=title,
        reason=reason,
        encouragement=encouragement,
        context_chips=context_chips,
        primary_action={'label': '', 'route': ''},
        variant="module"
    )



def _render_coverage_summary(analysis):
    """Render clean coverage summary - no banners, just facts."""
    
    # Coverage percentage (large, clean display)
    coverage_display = f"{min(analysis.coverage_percentage, 999):.0f}%" if analysis.coverage_percentage < 1000 else "999%+"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 24px 0;">
        <div style="font-size: 48px; font-weight: 700; color: var(--text-primary);">
            {coverage_display}
        </div>
        <div style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;">
            Income Coverage of Estimated Care Costs
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Monthly breakdown (simple 3-column)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 16px; background: var(--surface-primary); border-radius: 8px;">
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Estimated Cost</div>
            <div style="font-size: 20px; font-weight: 600; color: var(--text-primary);">
                ${analysis.estimated_monthly_cost:,.0f}<span style="font-size: 14px; font-weight: 400;">/mo</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 16px; background: var(--surface-primary); border-radius: 8px;">
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Total Income</div>
            <div style="font-size: 20px; font-weight: 600; color: var(--text-primary);">
                ${analysis.total_monthly_income + analysis.total_monthly_benefits:,.0f}<span style="font-size: 14px; font-weight: 400;">/mo</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        gap_label = "Surplus" if analysis.monthly_gap < 0 else "Gap"
        gap_color = "var(--success-fg)" if analysis.monthly_gap < 0 else "var(--error-fg)"
        st.markdown(f"""
        <div style="text-align: center; padding: 16px; background: var(--surface-primary); border-radius: 8px;">
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">{gap_label}</div>
            <div style="font-size: 20px; font-weight: 600; color: {gap_color};">
                ${abs(analysis.monthly_gap):,.0f}<span style="font-size: 14px; font-weight: 400;">/mo</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_financial_details(analysis, profile):
    """Render financial details as clean, simple list."""
    
    st.markdown("### Financial Details")
    
    # Income breakdown
    if analysis.total_monthly_income > 0:
        st.markdown(f"**Monthly Income:** ${analysis.total_monthly_income:,.0f}")
        
        # Show breakdown if helpful
        details = []
        if profile.ss_monthly > 0:
            details.append(f"Social Security ${profile.ss_monthly:,.0f}")
        if profile.pension_monthly > 0:
            details.append(f"Pension ${profile.pension_monthly:,.0f}")
        if profile.employment_monthly > 0:
            details.append(f"Employment ${profile.employment_monthly:,.0f}")
        if profile.other_income_monthly > 0:
            details.append(f"Other ${profile.other_income_monthly:,.0f}")
        
        if details:
            st.markdown(f"<div style='color: var(--text-secondary); font-size: 14px; margin-left: 16px;'>{', '.join(details)}</div>", unsafe_allow_html=True)
    
    # Benefits
    if analysis.total_monthly_benefits > 0:
        st.markdown(f"**Monthly Benefits:** ${analysis.total_monthly_benefits:,.0f}")
    
    # Assets
    if analysis.total_liquid_assets > 0:
        st.markdown(f"**Liquid Assets:** ${analysis.total_liquid_assets:,.0f}")
        
        # Runway if applicable
        if analysis.runway_months is not None and analysis.runway_months > 0:
            years = int(analysis.runway_months / 12)
            months = int(analysis.runway_months % 12)
            
            if years > 0:
                runway_text = f"{years} year{'s' if years != 1 else ''}"
                if months > 0:
                    runway_text += f", {months} month{'s' if months != 1 else ''}"
            else:
                runway_text = f"{months} month{'s' if months != 1 else ''}"
            
            st.markdown(f"<div style='color: var(--text-secondary); font-size: 14px; margin-left: 16px;'>Coverage runway: {runway_text}</div>", unsafe_allow_html=True)


def _render_action_items(analysis):
    """Render action items as clean, simple list."""
    
    st.markdown("### Recommended Actions")
    
    # Primary recommendation
    st.markdown(f"**{analysis.primary_recommendation}**")
    
    st.markdown('<div style="margin: 16px 0;"></div>', unsafe_allow_html=True)
    
    # Action items
    if analysis.action_items:
        for i, action in enumerate(analysis.action_items, 1):
            st.markdown(f"{i}. {action}")
    
    # Resources (if any)
    if analysis.resources:
        st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
        st.markdown("**Helpful Resources:**")
        for resource in analysis.resources:
            st.markdown(f"• {resource}")


def _render_navigation():
    """Render simple navigation buttons."""
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Assessments", use_container_width=True):
            st.session_state.cost_v2_step = "assessments"
            st.rerun()
    
    with col3:
        if st.button("Exit Cost Planner →", use_container_width=True):
            st.session_state.cost_v2_step = "exit"
            st.rerun()
