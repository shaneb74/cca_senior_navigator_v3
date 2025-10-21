"""
Expert Financial Review for Cost Planner v2

Clean, professional display of financial analysis with recommendations.
Communication through Navi panel, minimal UI clutter.
"""

import streamlit as st

from core.mcip import MCIP
from core.ui import render_navi_panel_v2
from products.cost_planner_v2.expert_formulas import calculate_expert_review
from products.cost_planner_v2.financial_profile import get_financial_profile, publish_to_mcip
from products.cost_planner_v2.utils.cost_calculator import CostEstimate


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

    # Check if we have an estimate from the intro page
    intro_estimate = st.session_state.get("cost_v2_quick_estimate")
    estimated_monthly_cost = None
    if intro_estimate and "estimate" in intro_estimate:
        estimate_data = intro_estimate["estimate"]
        # Handle both dict (persisted) and CostEstimate object (legacy)
        if isinstance(estimate_data, dict):
            estimated_monthly_cost = estimate_data["monthly_adjusted"]
        else:
            estimated_monthly_cost = estimate_data.monthly_adjusted

    # Calculate expert review
    analysis = calculate_expert_review(
        profile=profile,
        care_recommendation=care_recommendation,
        zip_code=zip_code,
        estimated_monthly_cost=estimated_monthly_cost,
    )

    # Publish summary to MCIP
    publish_to_mcip(analysis, profile)

    # NEW FLOW: Render sections in logical decision order
    # 1. Navi guidance with coverage duration headline
    _render_navi_guidance(analysis, profile)

    # Main content container
    st.markdown('<div class="sn-app module-container">', unsafe_allow_html=True)

    # Page header
    st.markdown(
        '<div class="mod-head"><div class="mod-head-row"><h2 class="h2">💰 Financial Review</h2></div></div>',
        unsafe_allow_html=True,
    )

    # 2. Income vs Cost Snapshot (simplified card with progress bar)
    _render_income_cost_snapshot(analysis)

    st.markdown('<div style="margin: 32px 0;"></div>', unsafe_allow_html=True)

    # 3. Available Resources (expandable cards per category)
    if analysis.asset_categories:
        _render_available_resources_cards(analysis, profile)
        st.markdown('<div style="margin: 32px 0;"></div>', unsafe_allow_html=True)

    # 4. Coverage Impact Visualization (dynamic, updates with selections)
    if analysis.asset_categories:
        _render_coverage_impact_visualization(analysis, profile)
        st.markdown('<div style="margin: 32px 0;"></div>', unsafe_allow_html=True)

    # 5. Recommended Actions & Resources
    _render_recommended_actions(analysis)

    st.markdown('<div style="margin: 48px 0;"></div>', unsafe_allow_html=True)

    # Navigation
    _render_navigation()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_incomplete_state():
    """Show state when required assessments not complete."""

    # Navi communication
    render_navi_panel_v2(
        title="Complete Required Assessments",
        reason="Please complete Income and Assets assessments to see your financial review.",
        encouragement={
            "icon": "📋",
            "text": "These two assessments are essential for accurate cost analysis.",
            "status": "active",
        },
        context_chips=[],
        primary_action={"label": "", "route": ""},
        variant="module",
    )

    # Minimal content
    st.markdown('<div class="sn-app module-container">', unsafe_allow_html=True)
    st.markdown(
        '<div class="mod-head"><div class="mod-head-row"><h2 class="h2">💰 Financial Review</h2></div></div>',
        unsafe_allow_html=True,
    )

    st.info("Complete Income and Assets assessments to unlock your personalized financial review.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Assessments", use_container_width=True, type="primary"):
            st.session_state.cost_v2_step = "assessments"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_navi_guidance(analysis, profile):
    """
    Render Navi panel with contextual guidance based on analysis.
    
    NEW: Lead with coverage duration as primary metric, income coverage as submetric.
    """

    # Calculate coverage duration in human-friendly format
    if analysis.runway_months is not None and analysis.runway_months > 0:
        years = int(analysis.runway_months / 12)
        months = int(analysis.runway_months % 12)
        if years > 0:
            coverage_duration = f"{years} year{'s' if years != 1 else ''}"
            if months > 0:
                coverage_duration += f", {months} month{'s' if months != 1 else ''}"
        else:
            coverage_duration = f"{int(analysis.runway_months)} month{'s' if analysis.runway_months != 1 else ''}"
    elif analysis.monthly_gap <= 0:
        coverage_duration = "Indefinite"
    else:
        coverage_duration = "Immediate action needed"

    # Determine message based on coverage tier
    if analysis.coverage_tier == "excellent":
        title = "Excellent Financial Position"
        reason = f"🔹 **Coverage Duration:** {coverage_duration}  \n{analysis.coverage_percentage:.0f}% of monthly costs covered by income.\n\nYour income and benefits cover your estimated care costs. Let's review your options to extend your care plan."
        encouragement = {
            "icon": "✅",
            "text": "You're in great shape! Explore how your resources can strengthen your plan.",
            "status": "complete",
        }

    elif analysis.coverage_tier == "good":
        title = "Strong Financial Foundation"
        reason = f"🔹 **Coverage Duration:** {coverage_duration}  \n{analysis.coverage_percentage:.0f}% of monthly costs covered by income.\n\nYou have a solid foundation with a manageable gap. Let's explore your resources."
        encouragement = {
            "icon": "👍",
            "text": "You're close! Here's how we can close the gap and secure your care plan.",
            "status": "active",
        }

    elif analysis.coverage_tier == "moderate":
        title = "Strategic Planning Recommended"
        reason = f"🔹 **Coverage Duration:** {coverage_duration}  \n{analysis.coverage_percentage:.0f}% of monthly costs covered by income.\n\nA strategic plan will help you bridge the gap and fund your care."
        encouragement = {
            "icon": "📊",
            "text": "Let's develop a funding strategy using your available resources.",
            "status": "active",
        }

    elif analysis.coverage_tier == "concerning":
        title = "Action Needed Soon"
        reason = f"🔹 **Coverage Duration:** {coverage_duration}  \n{analysis.coverage_percentage:.0f}% of monthly costs covered by income.\n\nPlanning is important to secure sustainable care. We'll help you explore all options."
        encouragement = {
            "icon": "⚠️",
            "text": "Let's prioritize actions to address the gap—time is important.",
            "status": "warning",
        }

    else:  # critical
        title = "Immediate Planning Essential"
        reason = f"🔹 **Coverage Duration:** {coverage_duration}  \n{analysis.coverage_percentage:.0f}% of monthly costs covered by income.\n\nImmediate action is needed. We'll guide you through available resources and assistance programs."
        encouragement = {
            "icon": "🚨",
            "text": "Help is available—let's find solutions urgently.",
            "status": "warning",
        }

    # Context chips - removed (info now in reason text)
    context_chips = []

    render_navi_panel_v2(
        title=title,
        reason=reason,
        encouragement=encouragement,
        context_chips=context_chips,
        primary_action={"label": "", "route": ""},
        variant="module",
    )


def _render_income_cost_snapshot(analysis):
    """
    Render Income vs Cost Snapshot with progress bar.
    
    Simplified card showing: cost, income, shortfall, and visual progress bar.
    """
    
    st.markdown("### 💰 Financial Snapshot")
    
    # Create clean card with background
    st.markdown('<div style="background: var(--surface-primary); border-radius: 12px; padding: 24px; border: 1px solid var(--border-primary);">', unsafe_allow_html=True)
    
    # Three-column layout for main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; font-weight: 500;">Estimated Monthly Care Cost</div>
                <div style="font-size: 28px; font-weight: 700; color: var(--text-primary);">${analysis.estimated_monthly_cost:,.0f}</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">/month</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; font-weight: 500;">Monthly Income</div>
                <div style="font-size: 28px; font-weight: 700; color: var(--text-primary);">${analysis.total_monthly_income + analysis.total_monthly_benefits:,.0f}</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">/month</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col3:
        shortfall_label = "Surplus" if analysis.monthly_gap < 0 else "Monthly Shortfall"
        shortfall_color = "var(--success-fg)" if analysis.monthly_gap < 0 else "var(--error-fg)"
        st.markdown(
            f"""
            <div style="text-align: center;">
                <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; font-weight: 500;">{shortfall_label}</div>
                <div style="font-size: 28px; font-weight: 700; color: {shortfall_color};">${abs(analysis.monthly_gap):,.0f}</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">/month</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Progress bar showing coverage from income
    st.markdown('<div style="margin-top: 24px;">', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; font-weight: 500;">Coverage From Income</div>',
        unsafe_allow_html=True,
    )
    
    coverage_pct = min(analysis.coverage_percentage, 100)  # Cap at 100% for display
    progress_color = "var(--success-fg)" if coverage_pct >= 80 else "var(--warning-fg)" if coverage_pct >= 50 else "var(--error-fg)"
    
    st.markdown(
        f"""
        <div style="width: 100%; background: var(--surface-secondary); border-radius: 8px; height: 32px; position: relative; overflow: hidden;">
            <div style="width: {coverage_pct}%; background: {progress_color}; height: 100%; border-radius: 8px; transition: width 0.3s ease;"></div>
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 14px; font-weight: 600; color: var(--text-primary);">
                {analysis.coverage_percentage:.0f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown('</div></div>', unsafe_allow_html=True)


def _render_coverage_summary(analysis):
    """Render clean coverage summary - no banners, just facts."""

    # Coverage percentage (large, clean display)
    coverage_display = (
        f"{min(analysis.coverage_percentage, 999):.0f}%"
        if analysis.coverage_percentage < 1000
        else "999%+"
    )

    st.markdown(
        f"""
    <div style="text-align: center; padding: 24px 0;">
        <div style="font-size: 48px; font-weight: 700; color: var(--text-primary);">
            {coverage_display}
        </div>
        <div style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;">
            Income Coverage of Estimated Care Costs
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Monthly breakdown (simple 4-column - added Runway!)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div style="text-align: center; padding: 16px; background: var(--surface-primary); border-radius: 8px;">
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Estimated Cost</div>
            <div style="font-size: 20px; font-weight: 600; color: var(--text-primary);">
                ${analysis.estimated_monthly_cost:,.0f}<span style="font-size: 14px; font-weight: 400;">/mo</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div style="text-align: center; padding: 16px; background: var(--surface-primary); border-radius: 8px;">
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Total Income</div>
            <div style="font-size: 20px; font-weight: 600; color: var(--text-primary);">
                ${analysis.total_monthly_income + analysis.total_monthly_benefits:,.0f}<span style="font-size: 14px; font-weight: 400;">/mo</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        gap_label = "Surplus" if analysis.monthly_gap < 0 else "Gap"
        gap_color = "var(--success-fg)" if analysis.monthly_gap < 0 else "var(--error-fg)"
        st.markdown(
            f"""
        <div style="text-align: center; padding: 16px; background: var(--surface-primary); border-radius: 8px;">
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">{gap_label}</div>
            <div style="font-size: 20px; font-weight: 600; color: {gap_color};">
                ${abs(analysis.monthly_gap):,.0f}<span style="font-size: 14px; font-weight: 400;">/mo</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        # Runway display - CRITICAL METRIC!
        if analysis.runway_months is not None and analysis.runway_months > 0:
            years = int(analysis.runway_months / 12)
            months = int(analysis.runway_months % 12)

            # Format display
            if years > 0:
                runway_value = f"{years}.{months // 3}" if months >= 3 else str(years)
                runway_unit = "yrs" if years > 1 else "yr"
            else:
                runway_value = str(int(analysis.runway_months))
                runway_unit = "mos"

            # Color based on runway length
            if analysis.runway_months >= 36:
                runway_color = "var(--success-fg)"
            elif analysis.runway_months >= 12:
                runway_color = "var(--warning-fg)"
            else:
                runway_color = "var(--error-fg)"

            st.markdown(
                f"""
            <div style="text-align: center; padding: 16px; background: var(--surface-primary); border-radius: 8px;">
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Coverage Runway</div>
                <div style="font-size: 20px; font-weight: 600; color: {runway_color};">
                    {runway_value}<span style="font-size: 14px; font-weight: 400;"> {runway_unit}</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            # No gap or infinite coverage
            runway_label = "Indefinite" if analysis.monthly_gap <= 0 else "Immediate"
            runway_color = "var(--success-fg)" if analysis.monthly_gap <= 0 else "var(--error-fg)"

            st.markdown(
                f"""
            <div style="text-align: center; padding: 16px; background: var(--surface-primary); border-radius: 8px;">
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Coverage Runway</div>
                <div style="font-size: 20px; font-weight: 600; color: {runway_color};">
                    {runway_label}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


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
            st.markdown(
                f"<div style='color: var(--text-secondary); font-size: 14px; margin-left: 16px;'>{', '.join(details)}</div>",
                unsafe_allow_html=True,
            )

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

            st.markdown(
                f"<div style='color: var(--text-secondary); font-size: 14px; margin-left: 16px;'>Coverage runway: {runway_text}</div>",
                unsafe_allow_html=True,
            )


def _render_available_resources_cards(analysis, profile):
    """
    Render available resources as expandable cards - one per category.
    
    NEW APPROACH: Each asset category is an expander with:
    - Balance summary in header
    - Availability status (Ready now, Taxed as income, etc.)
    - Checkbox to include in care funding plan
    - Helpful tooltip explaining the asset type
    """
    
    st.markdown("### 🏦 Available Resources to Cover Care Costs")
    
    # Only show if there are assets
    if not analysis.asset_categories:
        st.info("Complete additional financial assessments to see available resources.")
        return
    
    # Initialize selection state if not exists
    if "expert_review_selected_assets" not in st.session_state:
        # Default: Select liquid assets only
        st.session_state.expert_review_selected_assets = {
            name: category.is_liquid
            for name, category in analysis.asset_categories.items()
        }
    
    # Guidance text based on context
    if analysis.monthly_gap > 0:
        st.markdown(
            f"<div style='color: var(--text-secondary); font-size: 14px; margin-bottom: 20px;'>"
            f"Select which resources you'd like to include in your care funding plan. "
            f"We'll show how they extend your years of coverage."
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='color: var(--text-secondary); font-size: 14px; margin-bottom: 20px;'>"
            f"Your income fully covers estimated care costs. These assets are available as reserves if needed."
            f"</div>",
            unsafe_allow_html=True,
        )
    
    # Track if any selection changed
    selection_changed = False
    
    # Render each asset category as expandable card
    for cat_name in analysis.recommended_funding_order:
        if cat_name not in analysis.asset_categories:
            continue
            
        category = analysis.asset_categories[cat_name]
        
        # Build expander label with balance and status
        status_icon = "✅" if category.recommended else "⚠️"
        expander_label = f"{category.display_name} — ${category.current_balance:,.0f}"
        
        with st.expander(expander_label, expanded=False):
            # Two columns: info | checkbox
            info_col, checkbox_col = st.columns([4, 1])
            
            with info_col:
                # Current balance
                st.markdown(f"**Current Balance:** ${category.current_balance:,.0f}")
                
                # Available amount if different
                if category.accessible_value != category.current_balance:
                    diff_pct = (category.accessible_value / category.current_balance) * 100
                    st.markdown(f"**Available Now:** ${category.accessible_value:,.0f} ({diff_pct:.0f}% accessible)")
                else:
                    st.markdown(f"**Available Now:** ${category.accessible_value:,.0f}")
                
                # Availability status
                timeframe_map = {
                    "immediate": "✅ Ready to Use",
                    "1-3_months": "⏱️ Available in 1-3 Months",
                    "3-6_months": "📅 Available in 3-6 Months",
                    "6-12_months": "📆 Available in 6-12 Months",
                }
                timeframe_text = timeframe_map.get(category.liquidation_timeframe, category.liquidation_timeframe)
                st.markdown(f"**Status:** {timeframe_text}")
                
                # Tax implications if applicable
                if category.tax_implications != "none":
                    tax_labels = {
                        "ordinary_income": "⚙️ **Note:** Taxed as ordinary income when withdrawn",
                        "capital_gains": "📊 **Note:** Subject to capital gains tax",
                        "penalty": "⚠️ **Note:** Early withdrawal penalty may apply",
                    }
                    tax_text = tax_labels.get(category.tax_implications, category.tax_implications)
                    st.markdown(tax_text)
                
                # Recommendation note
                if cat_name in analysis.funding_notes:
                    note = analysis.funding_notes[cat_name]
                    st.info(f"💡 {note}")
                
                # Additional notes
                if category.notes:
                    st.markdown(f"<div style='font-size: 13px; color: var(--text-secondary); margin-top: 8px;'>{category.notes}</div>", unsafe_allow_html=True)
            
            with checkbox_col:
                # Checkbox for selection
                current_selection = st.session_state.expert_review_selected_assets.get(cat_name, False)
                new_selection = st.checkbox(
                    "Include in Care Funding Plan",
                    value=current_selection,
                    key=f"asset_select_{cat_name}",
                    disabled=not category.recommended,  # Disable if not recommended
                )
                
                if new_selection != current_selection:
                    st.session_state.expert_review_selected_assets[cat_name] = new_selection
                    selection_changed = True
    
    # Calculate extended coverage with selected assets
    from products.cost_planner_v2.expert_formulas import calculate_extended_runway
    
    selected_assets = st.session_state.expert_review_selected_assets
    extended_runway = calculate_extended_runway(
        analysis.monthly_gap if analysis.monthly_gap > 0 else 0,
        selected_assets,
        analysis.asset_categories,
    )
    
    # Show coverage analysis
    st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
    st.markdown("#### 📊 Coverage Analysis with Selected Assets")
    
    # Calculate total selected value
    total_selected = sum(
        analysis.asset_categories[name].accessible_value
        for name, selected in selected_assets.items()
        if selected and name in analysis.asset_categories
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Selected Assets",
            value=f"${total_selected:,.0f}",
        )
    
    with col2:
        if analysis.monthly_gap > 0 and total_selected > 0:
            # Show how gap is covered
            gap_covered_pct = min((total_selected / (analysis.monthly_gap * 12)) * 100, 999)
            st.metric(
                label="First Year Gap Coverage",
                value=f"{gap_covered_pct:.0f}%",
            )
        else:
            st.metric(
                label="Monthly Gap",
                value="$0" if analysis.monthly_gap <= 0 else f"${analysis.monthly_gap:,.0f}",
            )
    
    with col3:
        if extended_runway is not None and extended_runway > 0:
            years = int(extended_runway / 12)
            months = int(extended_runway % 12)
            
            if years > 0:
                runway_display = f"{years}y {months}m" if months > 0 else f"{years} years"
            else:
                runway_display = f"{int(extended_runway)} months"
            
            # Color based on length
            if extended_runway >= 36:
                delta_color = "normal"
            elif extended_runway >= 12:
                delta_color = "inverse"
            else:
                delta_color = "off"
            
            st.metric(
                label="Extended Coverage Runway",
                value=runway_display,
                delta="With selected assets",
                delta_color=delta_color,
            )
        elif analysis.monthly_gap <= 0:
            st.metric(
                label="Coverage Runway",
                value="Indefinite",
                delta="Income covers costs",
                delta_color="normal",
            )
        else:
            st.metric(
                label="Extended Runway",
                value="Select assets",
                delta="to calculate",
            )
    
    # Rerun if selection changed (to update calculations)
    if selection_changed:
        st.rerun()


def _render_coverage_impact_visualization(analysis, profile):
    """
    Render Coverage Impact Visualization showing how selected assets extend care funding.
    
    Shows:
    - Total Selected Assets
    - Extended Coverage Duration
    - Coverage Improvement
    - Visual timeline representation
    """
    
    from products.cost_planner_v2.expert_formulas import calculate_extended_runway
    
    st.markdown("### 📊 Coverage Analysis (Dynamic)")
    
    # Get current selections
    selected_assets = st.session_state.get("expert_review_selected_assets", {})
    
    # Calculate extended runway
    extended_runway = calculate_extended_runway(
        analysis.monthly_gap if analysis.monthly_gap > 0 else 0,
        selected_assets,
        analysis.asset_categories,
    )
    
    # Calculate total selected value
    total_selected = sum(
        analysis.asset_categories[name].accessible_value
        for name, selected in selected_assets.items()
        if selected and name in analysis.asset_categories
    )
    
    # Create card background
    st.markdown('<div style="background: var(--surface-primary); border-radius: 12px; padding: 24px; border: 1px solid var(--border-primary);">', unsafe_allow_html=True)
    
    # Three-column metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Selected Assets",
            value=f"${total_selected:,.0f}",
        )
    
    with col2:
        if analysis.monthly_gap > 0 and total_selected > 0:
            # Show how gap is covered
            gap_covered_pct = min((total_selected / (analysis.monthly_gap * 12)) * 100, 999)
            st.metric(
                label="First Year Gap Coverage",
                value=f"{gap_covered_pct:.0f}%",
            )
        else:
            st.metric(
                label="Monthly Shortfall",
                value="$0" if analysis.monthly_gap <= 0 else f"${abs(analysis.monthly_gap):,.0f}",
            )
    
    with col3:
        if extended_runway is not None and extended_runway > 0:
            years = int(extended_runway / 12)
            months = int(extended_runway % 12)
            
            if years > 0:
                runway_display = f"{years} years"
                if months > 0:
                    runway_display += f", {months} months"
            else:
                runway_display = f"{int(extended_runway)} months"
            
            # Calculate improvement over base runway
            if analysis.runway_months and analysis.runway_months > 0:
                improvement_months = extended_runway - analysis.runway_months
                improvement_years = improvement_months / 12
                delta_text = f"+{improvement_years:.1f} years"
            else:
                delta_text = "With selected assets"
            
            st.metric(
                label="New Coverage Duration",
                value=runway_display,
                delta=delta_text,
                delta_color="normal",
            )
        elif analysis.monthly_gap <= 0:
            st.metric(
                label="Coverage Duration",
                value="Indefinite",
                delta="Income covers costs",
                delta_color="normal",
            )
        else:
            st.metric(
                label="Extended Duration",
                value="Select assets above",
                delta="to calculate",
            )
    
    # Visual timeline bar (simplified for now - can enhance with actual timeline viz)
    if extended_runway and extended_runway > 0:
        st.markdown('<div style="margin-top: 24px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px;">Coverage Timeline</div>', unsafe_allow_html=True)
        
        # Show income coverage portion vs asset coverage portion
        if analysis.runway_months and analysis.runway_months > 0:
            income_portion = (analysis.runway_months / extended_runway) * 100
            asset_portion = ((extended_runway - analysis.runway_months) / extended_runway) * 100
        else:
            income_portion = 0
            asset_portion = 100
        
        st.markdown(
            f"""
            <div style="width: 100%; height: 40px; display: flex; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-primary);">
                <div style="width: {income_portion}%; background: var(--primary-bg); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: white;">
                    Income ({analysis.runway_months:.0f}mo)
                </div>
                <div style="width: {asset_portion}%; background: var(--success-bg); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: white;">
                    + Assets ({extended_runway - (analysis.runway_months or 0):.0f}mo)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_recommended_actions(analysis):
    """
    Render Recommended Actions & Helpful Resources section.
    
    Clear, numbered list of 3-5 key actions with supporting resources below.
    """

    st.markdown("### 🪄 Recommended Actions")
    
    # Primary recommendation in a highlighted box
    st.markdown('<div style="background: var(--surface-primary); border-left: 4px solid var(--primary-bg); padding: 16px; border-radius: 8px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown(f"**{analysis.primary_recommendation}**")
    st.markdown('</div>', unsafe_allow_html=True)

    # Action items as numbered list
    if analysis.action_items:
        for i, action in enumerate(analysis.action_items, 1):
            st.markdown(f"**{i}.** {action}")

    # Resources section (if any)
    if analysis.resources:
        st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
        st.markdown("### 📚 Helpful Resources")
        
        # Display as clean bullet list
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
