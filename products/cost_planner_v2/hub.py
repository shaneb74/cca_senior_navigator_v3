"""
Cost Planner v2 Module Hub

Orchestrates financial modules with tier-based filtering.
Demonstrates how products can use different internal architectures
(module hub vs single module vs custom workflow) while following
the universal product interface.

Uses Navi as the single intelligence layer for guidance and progress.
"""

import streamlit as st
from typing import List, Dict, Optional
from core.mcip import MCIP, CareRecommendation
from core.navi import render_navi_panel


def render():
    """Render module hub with financial assessment modules."""
    
    # Get context from MCIP
    recommendation = MCIP.get_care_recommendation()
    triage = st.session_state.get("cost_v2_triage", {})
    
    if not recommendation:
        st.error("❌ No care recommendation found. Please complete Guided Care Plan first.")
        if st.button("← Back"):
            st.session_state.cost_v2_step = "gcp_gate"
            st.rerun()
        return
    
    # Render Navi panel for guidance
    render_navi_panel(
        location="product",
        product_key="cost_v2",
        module_config=None
    )
    
    st.title("💰 Financial Assessment")
    
    # Show context
    tier = recommendation.tier.replace("_", " ").title()
    st.info(f"📋 **Care Recommendation:** {tier}")
    
    if triage:
        status_display = "Planning Ahead" if triage.get("status") == "planning" else "Existing Customer"
        st.caption(f"🎯 **Status:** {status_display}")
    
    st.markdown("---")
    
    # Module progress tracking
    if "cost_v2_modules" not in st.session_state:
        st.session_state.cost_v2_modules = {
            "income_assets": {"status": "not_started", "progress": 0, "data": None},
            "monthly_costs": {"status": "not_started", "progress": 0, "data": None},
            "coverage": {"status": "not_started", "progress": 0, "data": None}
        }
    
    modules_state = st.session_state.cost_v2_modules
    
    # Calculate overall progress
    total_modules = len(modules_state)
    completed = sum(1 for m in modules_state.values() if m["status"] == "completed")
    overall_progress = int((completed / total_modules) * 100)
    
    # Show overall progress
    st.progress(overall_progress / 100, text=f"Overall Progress: {completed}/{total_modules} modules complete")
    
    st.markdown("---")
    
    # Module tiles
    st.markdown("### � Financial Assessment Modules")
    
    # Module 1: Income & Assets
    _render_module_tile(
        module_key="income_assets",
        title="💵 Income & Assets",
        description="Sources of income and available assets for care costs",
        icon="💵",
        estimated_time="3-5 min"
    )
    
    st.markdown("")
    
    # Module 2: Monthly Costs
    _render_module_tile(
        module_key="monthly_costs",
        title="💰 Monthly Costs",
        description="Detailed breakdown of care costs and additional services",
        icon="💰",
        estimated_time="4-6 min"
    )
    
    st.markdown("")
    
    # Module 3: Coverage
    _render_module_tile(
        module_key="coverage",
        title="🏥 Coverage & Benefits",
        description="Insurance, VA benefits, and other coverage sources",
        icon="🏥",
        estimated_time="5-7 min"
    )
    
    st.markdown("---")
    
    # Summary and next steps
    if completed == total_modules:
        st.success("### ✅ All Modules Complete!")
        st.markdown("You've completed the financial assessment. Review your summary below.")
        
        # Show summary
        _render_summary()
        
        st.markdown("---")
        
        # Publish to MCIP
        if not _already_published():
            if st.button("📊 Publish Financial Profile to MCIP", type="primary", key="publish_financial"):
                _publish_to_mcip()
                st.success("✅ Financial profile published!")
                st.rerun()
        else:
            # Already published - show next steps
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Continue to Expert Review →", type="primary", use_container_width=True):
                    st.session_state.cost_v2_step = "expert_review"
                    st.rerun()
            
            with col2:
                if st.button("🏠 Return to Hub", use_container_width=True):
                    from core.nav import route_to
                    route_to("hub_concierge")
    
    else:
        st.info(f"💡 Complete all {total_modules} modules to proceed to expert review.")


def _render_care_context(recommendation: CareRecommendation):
    """Show care recommendation context at top of hub.
    
    This creates the visual connection between GCP and Cost Planner.
    User sees that costs are based on their personalized recommendation.
    
    Args:
        recommendation: Care recommendation from MCIP
    """
    tier_label = recommendation.tier.replace("_", " ").title()
    confidence_pct = int(recommendation.confidence * 100)
    
    st.info(f"""
    **Based on your Guided Care Plan:**
    - 🎯 Recommended Care Level: **{tier_label}**
    - 📊 Confidence: {confidence_pct}%
    
    We'll calculate costs specific to **{tier_label}** care in your region.
    """)


def _generate_sample_financial_data(recommendation: CareRecommendation) -> Dict:
    """Generate sample financial data based on care tier.
    
    This demonstrates tier-based cost calculation.
    In full implementation, this comes from module outputs.
    
    Args:
        recommendation: Care recommendation from MCIP
    
    Returns:
        Dict with financial data
    """
    
    # Sample costs by tier (monthly)
    tier_base_costs = {
        "independent": 0.0,        # Living at home independently
        "in_home": 3500.0,         # In-home care services
        "assisted_living": 4500.0, # Assisted living facility
        "memory_care": 6500.0      # Memory care facility
    }
    
    base_cost = tier_base_costs.get(recommendation.tier, 3500.0)
    
    # Sample additional services (varies by tier)
    additional_services = {
        "independent": 200.0,      # Home modifications, meal delivery
        "in_home": 850.0,          # Therapy, medical transport
        "assisted_living": 650.0,  # Activities, therapy
        "memory_care": 950.0       # Specialized therapies, security
    }
    
    additional = additional_services.get(recommendation.tier, 500.0)
    
    # Sample veteran benefits (if flags indicate)
    veteran_benefit = 1850.0 if _has_veteran_flag(recommendation) else 0.0
    
    # Calculate totals
    total_monthly = base_cost + additional
    annual_cost = total_monthly * 12
    three_year = annual_cost * 3 * 1.03  # 3% inflation
    five_year = annual_cost * 5 * 1.05   # 5% inflation
    
    # Funding sources
    funding_sources = {
        "personal_savings": 2000.0,
        "family_contribution": 1000.0,
        "veteran_benefits": veteran_benefit,
        "insurance": 0.0,
        "medicare": 0.0,
        "medicaid": 0.0
    }
    
    total_funding = sum(funding_sources.values())
    funding_gap = total_monthly - total_funding
    
    return {
        "base_care_cost": base_cost,
        "additional_services": additional,
        "total_monthly_cost": total_monthly,
        "annual_cost": annual_cost,
        "three_year_projection": three_year,
        "five_year_projection": five_year,
        "funding_sources": funding_sources,
        "funding_gap": funding_gap,
        "care_tier": recommendation.tier,
        "region": "northeast",  # Sample - would come from module
        "facility_type": "standard"  # Sample - would come from module
    }


def _has_veteran_flag(recommendation: CareRecommendation) -> bool:
    """Check if recommendation has veteran-related flags.
    
    Args:
        recommendation: Care recommendation from MCIP
    
    Returns:
        True if veteran flags present
    """
    # In full implementation, check flags
    # For now, return False
    return False


def _render_financial_preview(financial_data: Dict, recommendation: CareRecommendation):
    """Show preview of financial summary.
    
    Args:
        financial_data: Financial calculations
        recommendation: Care recommendation from MCIP
    """
    st.markdown("### 💰 Cost Estimate Preview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Base Care Cost",
            f"${financial_data['base_care_cost']:,.0f}/mo"
        )
    
    with col2:
        st.metric(
            "Additional Services",
            f"${financial_data['additional_services']:,.0f}/mo"
        )
    
    with col3:
        st.metric(
            "Total Monthly Cost",
            f"${financial_data['total_monthly_cost']:,.0f}/mo",
            delta=f"Based on {recommendation.tier.replace('_', ' ').title()}"
        )
    
    # Funding breakdown
    st.markdown("### 💳 Funding Sources")
    
    total_funding = sum(financial_data['funding_sources'].values())
    gap = financial_data['funding_gap']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        for source, amount in financial_data['funding_sources'].items():
            if amount > 0:
                st.markdown(f"- **{source.replace('_', ' ').title()}**: ${amount:,.0f}/mo")
    
    with col2:
        if gap > 0:
            st.error(f"**Funding Gap:**\n${gap:,.0f}/mo")
        elif gap < 0:
            st.success(f"**Surplus:**\n${abs(gap):,.0f}/mo")
        else:
            st.info("**Fully Funded**")


def _publish_to_mcip(financial_data: Dict, recommendation: CareRecommendation):
    """Aggregate financial data and publish to MCIP.
    
    This demonstrates the universal publishing pattern.
    
    Args:
        financial_data: Aggregated financial calculations
        recommendation: Care recommendation from MCIP (for context)
    """
    
    from datetime import datetime
    from core.mcip import FinancialProfile
    
    # Build FinancialProfile contract
    financial_profile = FinancialProfile(
        # Monthly costs
        base_care_cost=financial_data["base_care_cost"],
        additional_services=financial_data["additional_services"],
        total_monthly_cost=financial_data["total_monthly_cost"],
        
        # Projections
        annual_cost=financial_data["annual_cost"],
        three_year_projection=financial_data["three_year_projection"],
        five_year_projection=financial_data["five_year_projection"],
        
        # Funding
        funding_sources=financial_data["funding_sources"],
        funding_gap=financial_data["funding_gap"],
        
        # Context
        care_tier=financial_data["care_tier"],
        region=financial_data["region"],
        facility_type=financial_data["facility_type"],
        
        # Provenance
        generated_at=datetime.utcnow().isoformat() + "Z",
        version="2.0.0",
        input_snapshot_id=_generate_snapshot_id(),
        
        # Status
        status="complete",
        last_updated=datetime.utcnow().isoformat() + "Z",
        needs_refresh=False
    )
    
    # Publish to MCIP (single source of truth)
    MCIP.publish_financial_profile(financial_profile)
    
    # Mark product complete in journey
    MCIP.mark_product_complete("cost_planner")
    
    # Mark as published in session
    st.session_state["cost_planner_v2_published"] = True


def _generate_snapshot_id() -> str:
    """Generate unique snapshot ID for provenance.
    
    Returns:
        Snapshot ID string
    """
    from datetime import datetime
    user_id = st.session_state.get("user_id", "anon")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"cost_v2_{user_id}_{timestamp}"


def _already_published() -> bool:
    """Check if financial profile already published.
    
    Returns:
        True if already published
    """
    return st.session_state.get("cost_planner_v2_published", False)


def _render_completion_screen():
    """Show completion screen after publishing to MCIP."""
    
    financial = MCIP.get_financial_profile()
    
    if not financial:
        st.error("❌ Unable to load financial profile")
        return
    
    st.success("✅ **Your Financial Plan is Complete!**")
    
    st.markdown("---")
    
    st.markdown("### 📊 Financial Summary")
    
    # Monthly breakdown
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.metric("Base Care Cost", f"${financial.base_care_cost:,.0f}/mo")
        st.metric("Additional Services", f"${financial.additional_services:,.0f}/mo")
        st.metric("**Total Monthly Cost**", f"**${financial.total_monthly_cost:,.0f}/mo**")
    
    with col2:
        total_funding = sum(financial.funding_sources.values())
        st.metric("Funding Available", f"${total_funding:,.0f}/mo")
        
        if financial.funding_gap > 0:
            st.metric("Funding Gap", f"${financial.funding_gap:,.0f}/mo", 
                     delta=f"-${financial.funding_gap:,.0f}", delta_color="inverse")
        else:
            st.metric("Surplus", f"${abs(financial.funding_gap):,.0f}/mo",
                     delta=f"+${abs(financial.funding_gap):,.0f}")
    
    st.markdown("---")
    
    # Long-term projections
    st.markdown("### 📈 Long-Term Projections")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Year 1", f"${financial.annual_cost:,.0f}")
    
    with col2:
        st.metric("3 Years", f"${financial.three_year_projection:,.0f}")
    
    with col3:
        st.metric("5 Years", f"${financial.five_year_projection:,.0f}")
    
    st.caption("*Projections include estimated 3-5% annual inflation*")
    
    st.markdown("---")
    
    # Next steps
    st.markdown("### 🚀 What's Next?")
    
    st.markdown("""
    Now that you have your care recommendation and financial plan, you can:
    
    1. **📞 Schedule an Advisor Call** - Discuss your plan with a senior care expert
    2. **🏠 Browse Facilities** - Find specific facilities in your area
    3. **📚 Learn More** - Explore care options and resources
    4. **💾 Save Your Plan** - Download or email your personalized plan
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📞 Schedule Advisor Call", type="primary", use_container_width=True, key="next_pfma"):
            from core.nav import route_to
            route_to("pfma")
    
    with col2:
        if st.button("🏠 Return to Hub", use_container_width=True, key="next_hub"):
            from core.nav import route_to
            route_to("hub_concierge")
    
    # Debug mode
    if st.session_state.get("debug_mode"):
        with st.expander("🔧 Debug: MCIP State"):
            st.json({
                "care_tier": financial.care_tier,
                "total_monthly": financial.total_monthly_cost,
                "funding_gap": financial.funding_gap,
                "version": financial.version,
                "generated_at": financial.generated_at,
                "product_complete": MCIP.is_product_complete("cost_planner")
            })


def _render_module_tile(
    module_key: str,
    title: str,
    description: str,
    icon: str,
    estimated_time: str
):
    """Render a single module tile.
    
    Args:
        module_key: Module identifier
        title: Module title
        description: Module description
        icon: Emoji icon
        estimated_time: Estimated completion time
    """
    modules_state = st.session_state.cost_v2_modules
    module = modules_state[module_key]
    
    status = module["status"]
    progress = module["progress"]
    
    # Container
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"<div style='font-size: 48px; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{title}**")
            st.caption(description)
            st.caption(f"⏱️ {estimated_time}")
        
        with col3:
            if status == "completed":
                if st.button("✏️ Edit", key=f"{module_key}_edit", use_container_width=True):
                    _start_module(module_key)
            else:
                if st.button("▶️ Start", key=f"{module_key}_start", type="primary" if status == "not_started" else "secondary", use_container_width=True):
                    _start_module(module_key)
        
        # Show progress bar if in progress
        if status == "in_progress" or status == "completed":
            st.progress(progress / 100)
        
        # Show summary if completed
        if status == "completed" and module["data"]:
            with st.expander("📋 View Summary"):
                data = module["data"]
                for key, value in data.items():
                    if key.startswith("total_") or key.startswith("monthly_") or key.endswith("_cost") or key.endswith("_assets") or key.endswith("_coverage"):
                        if isinstance(value, (int, float)):
                            st.metric(key.replace("_", " ").title(), f"${value:,.0f}")


def _start_module(module_key: str):
    """Start a financial assessment module.
    
    Args:
        module_key: Module identifier
    """
    # Set current module
    st.session_state.cost_v2_current_module = module_key
    
    # Mark as in progress
    st.session_state.cost_v2_modules[module_key]["status"] = "in_progress"
    
    # Navigate to module
    st.session_state.cost_v2_step = "module_active"
    st.rerun()


def _render_summary():
    """Render summary of all completed modules."""
    modules_state = st.session_state.cost_v2_modules
    
    st.markdown("### 📊 Financial Summary")
    
    # Income & Assets
    if modules_state["income_assets"]["data"]:
        data = modules_state["income_assets"]["data"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Monthly Income", f"${data.get('total_monthly_income', 0):,.0f}")
        with col2:
            st.metric("Liquid Assets", f"${data.get('liquid_assets', 0):,.0f}")
        with col3:
            st.metric("Total Assets", f"${data.get('total_assets', 0):,.0f}")
    
    # Monthly Costs
    if modules_state["monthly_costs"]["data"]:
        data = modules_state["monthly_costs"]["data"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Base Care Cost", f"${data.get('base_care_cost', 0):,.0f}")
        with col2:
            st.metric("Additional Services", f"${data.get('additional_services_cost', 0):,.0f}")
        with col3:
            st.metric("Total Monthly Cost", f"${data.get('total_monthly_cost', 0):,.0f}")
    
    # Coverage
    if modules_state["coverage"]["data"]:
        data = modules_state["coverage"]["data"]
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Coverage", f"${data.get('total_coverage', 0):,.0f}")
        with col2:
            # Calculate gap
            monthly_cost = modules_state["monthly_costs"]["data"].get("total_monthly_cost", 0)
            coverage = data.get("total_coverage", 0)
            gap = monthly_cost - coverage
            
            if gap > 0:
                st.metric("Monthly Gap", f"${gap:,.0f}", 
                         delta=f"-${gap:,.0f}",
                         delta_color="inverse")
            else:
                st.metric("Monthly Surplus", f"${abs(gap):,.0f}", 
                         delta=f"+${abs(gap):,.0f}")


def _publish_to_mcip():
    """Aggregate module data and publish to MCIP."""
    modules_state = st.session_state.cost_v2_modules
    
    # Get all module data
    income_data = modules_state["income_assets"]["data"]
    costs_data = modules_state["monthly_costs"]["data"]
    coverage_data = modules_state["coverage"]["data"]
    
    # Calculate summary values
    total_monthly_cost = costs_data.get("total_monthly_cost", 0)
    total_coverage = coverage_data.get("total_coverage", 0)
    monthly_income = income_data.get("total_monthly_income", 0)
    total_assets = income_data.get("total_assets", 0)
    
    funding_gap = total_monthly_cost - total_coverage - monthly_income
    
    # Calculate runway
    if funding_gap > 0 and total_assets > 0:
        runway_months = int(total_assets / funding_gap)
    else:
        runway_months = 999  # Essentially unlimited
    
    # Build FinancialProfile contract
    from datetime import datetime
    from core.mcip import FinancialProfile
    
    financial_profile = FinancialProfile(
        estimated_monthly_cost=total_monthly_cost,
        coverage_percentage=int((total_coverage / total_monthly_cost * 100)) if total_monthly_cost > 0 else 0,
        gap_amount=funding_gap,
        runway_months=runway_months,
        confidence=0.85,  # High confidence from detailed modules
        generated_at=datetime.utcnow().isoformat() + "Z",
        status="complete"
    )
    
    # Publish to MCIP
    MCIP.publish_financial_profile(financial_profile)
    
    # Mark product complete
    MCIP.mark_product_complete("cost_v2")
    
    # Mark as published
    st.session_state["cost_planner_v2_published"] = True
