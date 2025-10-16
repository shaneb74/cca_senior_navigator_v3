"""
Cost Planner v2 Module Hub

Orchestrates financial modules with tier-based filtering.
Demonstrates how products can use different internal architectures
(module hub vs single module vs custom workflow) while following
the universal product interface.

Uses Navi as the single intelligence layer for guidance and progress.
"""

import streamlit as st
import json
import os
from typing import List, Dict, Optional
from core.mcip import MCIP, CareRecommendation


def _load_module_config() -> Dict:
    """Load module configuration from JSON."""
    config_path = os.path.join("config", "cost_planner_v2_modules.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        st.error(f"❌ Configuration file not found: {config_path}")
        return {"modules": []}
    except json.JSONDecodeError as e:
        st.error(f"❌ Error parsing configuration file: {e}")
        return {"modules": []}


def render():
    """Render module hub with financial assessment modules."""
    
    # Load module configuration
    config = _load_module_config()
    modules_config = config.get("modules", [])
    
    if not modules_config:
        st.error("❌ No modules configured. Please check the configuration file.")
        return
    
    # Get context from MCIP
    recommendation = MCIP.get_care_recommendation()
    triage = st.session_state.get("cost_v2_triage", {})
    
    # Optional: Show info if no GCP recommendation (use general estimates)
    if not recommendation:
        st.info("ℹ️ You're using general cost estimates. Complete the Guided Care Plan for personalized recommendations.")
    
    # Navi panel is rendered by product.py - don't duplicate it here
    
    st.title("💰 Financial Assessment")
    
    # Show context
    if recommendation:
        tier = recommendation.tier.replace("_", " ").title()
        st.success(f"✅ **Care Recommendation:** {tier}")
    else:
        st.warning("⚠️ **Using General Estimates** - No personalized care assessment")
    
    if triage:
        status_display = "Planning Ahead" if triage.get("status") == "planning" else "Existing Customer"
        st.caption(f"🎯 **Status:** {status_display}")
    
    st.markdown("---")
    
    # Module progress tracking - initialize from config
    if "cost_v2_modules" not in st.session_state:
        st.session_state.cost_v2_modules = {}
        for module in modules_config:
            module_key = module.get("key")
            st.session_state.cost_v2_modules[module_key] = {
                "status": "not_started",
                "progress": 0,
                "data": None
            }
    
    modules_state = st.session_state.cost_v2_modules
    
    # Calculate overall progress
    total_modules = len(modules_state)
    completed = sum(1 for m in modules_state.values() if m["status"] == "completed")
    overall_progress = int((completed / total_modules) * 100) if total_modules > 0 else 0
    
    # Show overall progress
    st.progress(overall_progress / 100, text=f"Overall Progress: {completed}/{total_modules} modules complete")
    
    st.markdown("---")
    
    # Module tiles
    st.markdown("### 💼 Financial Assessment Modules")
    
    # Render modules dynamically from config
    for module in sorted(modules_config, key=lambda m: m.get("sort_order", 0)):
        _render_module_tile(
            module_key=module.get("key"),
            title=f"{module.get('icon', '�')} {module.get('title', 'Module')}",
            description=module.get("description", ""),
            icon=module.get("icon", "�"),
            estimated_time=module.get("estimated_time", "3-5 min"),
            required=module.get("required", False)
        )
        st.markdown("")
    
    st.markdown("---")
    
    # Summary and next steps
    required_modules = [m.get("key") for m in modules_config if m.get("required", False)]
    required_completed = sum(1 for key in required_modules if modules_state.get(key, {}).get("status") == "completed")
    
    if completed == total_modules:
        st.success("### ✅ All Modules Complete!")
        st.markdown("You've completed the financial assessment. Review your summary below.")
        
        # Show summary
        _render_summary()
        
        st.markdown("---")
        
        # Navigation buttons - automatically publish when continuing
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Continue to Expert Review →", type="primary", use_container_width=True):
                # Automatically publish to MCIP before proceeding
                if not _already_published():
                    _publish_to_mcip()
                st.session_state.cost_v2_step = "expert_review"
                st.rerun()
        
        with col2:
            if st.button("🏠 Return to Concierge", use_container_width=True):
                from core.nav import route_to
                route_to("hub_concierge")
    
    elif required_completed == len(required_modules) and len(required_modules) > 0:
        st.success(f"### ✅ Required Modules Complete ({required_completed}/{len(required_modules)})")
        st.info(f"💡 Optional: Complete {total_modules - completed} more module(s) for a comprehensive assessment, or proceed with current data.")
        
        # Show summary
        _render_summary()
        
        st.markdown("---")
        
        # Navigation buttons - automatically publish when continuing
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Continue to Expert Review →", type="primary", use_container_width=True):
                # Automatically publish to MCIP before proceeding
                if not _already_published():
                    _publish_to_mcip()
                st.session_state.cost_v2_step = "expert_review"
                st.rerun()
        
        with col2:
            if st.button("🏠 Return to Concierge", use_container_width=True):
                from core.nav import route_to
                route_to("hub_concierge")
    
    else:
        st.info(f"💡 Complete {len(required_modules) - required_completed} more required module(s) to proceed. ({required_completed}/{len(required_modules)} required complete)")



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
    estimated_time: str,
    required: bool = False
):
    """Render a single module tile.
    
    Args:
        module_key: Module identifier
        title: Module title
        description: Module description
        icon: Emoji icon
        estimated_time: Estimated completion time
        required: Whether module is required for progression
    """
    modules_state = st.session_state.cost_v2_modules
    module = modules_state.get(module_key, {"status": "not_started", "progress": 0, "data": None})
    
    status = module["status"]
    progress = module["progress"]
    
    # Container
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"<div style='font-size: 48px; text-align: center;'>{icon}</div>", unsafe_allow_html=True)
        
        with col2:
            # Add required badge if applicable
            title_text = f"**{title}**"
            if required:
                title_text += " 🔴"
            st.markdown(title_text)
            st.caption(description)
            time_text = f"⏱️ {estimated_time}"
            if required:
                time_text += " • **Required**"
            st.caption(time_text)
        
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
                    if key.startswith("total_") or key.startswith("monthly_") or key.endswith("_cost") or key.endswith("_assets") or key.endswith("_coverage") or key.endswith("_income") or key.endswith("_benefit") or key.endswith("_premium"):
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
    """Render comprehensive summary of all completed modules."""
    from core.mcip import MCIP
    
    modules_state = st.session_state.cost_v2_modules
    
    st.markdown("### 📊 Financial Assessment Summary")
    st.markdown("---")
    
    # Get care recommendation for context
    care_rec = MCIP.get_care_recommendation()
    if care_rec:
        st.info(f"**Care Level:** {care_rec.tier.replace('_', ' ').title()}")
    
    # =========================================================================
    # INCOME SECTION
    # =========================================================================
    if modules_state.get("income", {}).get("data"):
        st.markdown("#### 💰 Monthly Income")
        data = modules_state["income"]["data"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Social Security", 
                f"${data.get('ss_monthly', 0):,.0f}",
                help="Monthly Social Security benefits"
            )
        with col2:
            st.metric(
                "Pension", 
                f"${data.get('pension_monthly', 0):,.0f}",
                help="Monthly pension/annuity income"
            )
        with col3:
            st.metric(
                "Other Income", 
                f"${data.get('employment_monthly', 0) + data.get('investment_monthly', 0) + data.get('other_monthly', 0):,.0f}",
                help="Employment, investment, and other income"
            )
        
        total_income = sum([
            data.get('ss_monthly', 0),
            data.get('pension_monthly', 0),
            data.get('employment_monthly', 0),
            data.get('investment_monthly', 0),
            data.get('other_monthly', 0)
        ])
        
        st.success(f"**Total Monthly Income:** ${total_income:,.0f}")
        st.markdown("---")
    
    # =========================================================================
    # ASSETS SECTION
    # =========================================================================
    if modules_state.get("assets", {}).get("data"):
        st.markdown("#### 🏦 Available Assets")
        data = modules_state["assets"]["data"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            liquid = data.get('checking_savings', 0) + data.get('cds_money_market', 0)
            st.metric(
                "Liquid Assets", 
                f"${liquid:,.0f}",
                help="Cash, checking, savings, CDs"
            )
            
            retirement = sum([
                data.get('ira_traditional', 0),
                data.get('ira_roth', 0),
                data.get('k401_403b', 0),
                data.get('other_retirement', 0)
            ])
            st.metric(
                "Retirement Accounts", 
                f"${retirement:,.0f}",
                help="401k, IRA, and other retirement savings"
            )
        
        with col2:
            investments = data.get('stocks_bonds', 0) + data.get('mutual_funds', 0)
            st.metric(
                "Investments", 
                f"${investments:,.0f}",
                help="Stocks, bonds, mutual funds"
            )
            
            real_estate = data.get('investment_property', 0)
            st.metric(
                "Real Estate", 
                f"${real_estate:,.0f}",
                help="Investment property value"
            )
        
        total_assets = liquid + retirement + investments + real_estate
        st.success(f"**Total Available Assets:** ${total_assets:,.0f}")
        st.markdown("---")
    
    # =========================================================================
    # VA BENEFITS SECTION
    # =========================================================================
    if modules_state.get("va_benefits", {}).get("data"):
        data = modules_state["va_benefits"]["data"]
        if data.get('is_veteran'):
            st.markdown("#### 🎖️ VA Benefits")
            
            col1, col2 = st.columns(2)
            
            with col1:
                va_disability = data.get('va_disability_monthly', 0)
                if va_disability > 0:
                    st.metric(
                        "VA Disability", 
                        f"${va_disability:,.0f}",
                        help="Monthly VA Disability Compensation"
                    )
            
            with col2:
                aid_attendance = data.get('aid_attendance_monthly', 0)
                if aid_attendance > 0:
                    st.metric(
                        "Aid & Attendance", 
                        f"${aid_attendance:,.0f}",
                        help="Monthly Aid & Attendance Benefit"
                    )
            
            total_va = va_disability + aid_attendance
            if total_va > 0:
                st.success(f"**Total VA Benefits:** ${total_va:,.0f}/month")
            else:
                st.info("✅ Veteran status confirmed - May be eligible for VA benefits")
            
            st.markdown("---")
    
    # =========================================================================
    # INSURANCE COVERAGE SECTION
    # =========================================================================
    if modules_state.get("health_insurance", {}).get("data"):
        st.markdown("#### 🏥 Insurance Coverage")
        data = modules_state["health_insurance"]["data"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if data.get('has_medicare'):
                st.success("✅ **Medicare**")
            else:
                st.warning("⚠️ **No Medicare**")
        
        with col2:
            if data.get('has_medicaid'):
                st.success("✅ **Medicaid**")
                if data.get('medicaid_covers_ltc'):
                    st.caption("Covers long-term care")
            else:
                st.info("ℹ️ **No Medicaid**")
        
        with col3:
            if data.get('has_ltc_insurance'):
                ltc_daily = data.get('ltc_daily_benefit', 0)
                ltc_monthly = ltc_daily * 30
                st.success(f"✅ **LTC Insurance**")
                st.metric("Monthly Benefit", f"${ltc_monthly:,.0f}")
            else:
                st.info("ℹ️ **No LTC Insurance**")
        
        st.markdown("---")
    
    # =========================================================================
    # LIFE INSURANCE SECTION
    # =========================================================================
    if modules_state.get("life_insurance", {}).get("data"):
        data = modules_state["life_insurance"]["data"]
        if data.get('has_life_insurance'):
            st.markdown("#### 🛡️ Life Insurance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                death_benefit = data.get('death_benefit', 0)
                st.metric(
                    "Death Benefit", 
                    f"${death_benefit:,.0f}",
                    help="Face value of policy"
                )
            
            with col2:
                if data.get('has_cash_value'):
                    cash_value = data.get('cash_value', 0)
                    st.metric(
                        "Available Cash Value", 
                        f"${cash_value:,.0f}",
                        help="Can be borrowed or surrendered"
                    )
            
            # Show policy options
            if data.get('accelerated_death_benefit') or data.get('ltc_rider'):
                options = []
                if data.get('accelerated_death_benefit'):
                    options.append("Accelerated Death Benefit")
                if data.get('ltc_rider'):
                    options.append("LTC Rider")
                st.info(f"**Available Riders:** {', '.join(options)}")
            
            st.markdown("---")
    
    # =========================================================================
    # MEDICAID PLANNING SECTION
    # =========================================================================
    if modules_state.get("medicaid_navigation", {}).get("data"):
        data = modules_state["medicaid_navigation"]["data"]
        interest = data.get('medicaid_interest', 'not_interested')
        
        if interest != 'not_interested':
            st.markdown("#### 🧭 Medicaid Planning")
            
            col1, col2 = st.columns(2)
            
            with col1:
                interest_labels = {
                    'learning': 'Learning about Medicaid',
                    'may_need_soon': 'May need within 1-2 years',
                    'need_now': 'Need to apply soon',
                    'already_enrolled': 'Already enrolled'
                }
                st.info(f"**Status:** {interest_labels.get(interest, interest)}")
            
            with col2:
                if data.get('preliminary_eligible'):
                    st.success("✅ **Preliminarily Eligible**")
                else:
                    st.warning("⚠️ **Planning May Be Needed**")
            
            st.markdown("---")
    
    # =========================================================================
    # FINANCIAL TIMELINE
    # =========================================================================
    financial_data = st.session_state.get("financial_assessment_complete")
    if financial_data:
        st.markdown("#### 📅 Financial Care Timeline")
        st.markdown("*How long your resources will cover care costs*")
        
        timeline = financial_data.get('timeline', {})
        costs = financial_data.get('costs', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            monthly_cost = costs.get('estimated_monthly', 0)
            st.metric(
                "Estimated Monthly Cost",
                f"${monthly_cost:,.0f}",
                help=f"Based on {costs.get('care_tier', 'unknown')} care level"
            )
        
        with col2:
            coverage_pct = timeline.get('coverage_percentage', 0)
            st.metric(
                "Coverage %",
                f"{coverage_pct}%",
                help="% of costs covered by income + benefits"
            )
        
        with col3:
            monthly_gap = timeline.get('monthly_gap', 0)
            if monthly_gap > 0:
                st.metric(
                    "Monthly Gap",
                    f"${monthly_gap:,.0f}",
                    delta=f"-${monthly_gap:,.0f}",
                    delta_color="inverse",
                    help="Amount to cover from assets each month"
                )
            else:
                st.metric(
                    "Monthly Surplus",
                    f"${abs(monthly_gap):,.0f}",
                    delta=f"+${abs(monthly_gap):,.0f}",
                    help="Fully covered by income + benefits"
                )
        
        with col4:
            runway = timeline.get('runway_months', 0)
            if runway >= 999:
                st.metric(
                    "Care Timeline",
                    "Unlimited",
                    help="Fully covered by income + benefits"
                )
            elif runway > 0:
                years = runway // 12
                months = runway % 12
                if years > 0:
                    timeline_str = f"{years}y {months}m"
                else:
                    timeline_str = f"{months} months"
                st.metric(
                    "Asset Runway",
                    timeline_str,
                    help="How long liquid assets will last at current gap"
                )
            else:
                st.metric(
                    "Asset Runway",
                    "⚠️ Immediate",
                    help="Insufficient liquid assets to cover gap"
                )
        
        # Timeline visualization
        if 0 < runway < 999:
            st.markdown("##### Timeline Projection")
            years_total = runway / 12
            if years_total <= 5:
                progress = (years_total / 5) * 100
                st.progress(progress / 100)
                st.caption(f"Asset runway: {years_total:.1f} years of care coverage")
            else:
                st.success(f"✅ Assets can cover care costs for {years_total:.1f} years")
        elif runway >= 999:
            st.success("✅ **Income and benefits fully cover monthly care costs!**")
        else:
            st.warning("⚠️ **Immediate financial planning recommended** - Consider Medicaid or other funding sources")


def _format_runway_message(runway_years: int, runway_months: int, monthly_gap: float) -> str:
    """Format a user-friendly runway message for display on Cost Planner tile and Navi.
    
    Args:
        runway_years: Number of years assets will last
        runway_months: Number of months assets will last
        monthly_gap: Monthly gap amount (positive means drawing from assets)
    
    Returns:
        Formatted message string
    """
    if monthly_gap <= 0:
        # Fully covered - no asset drawdown needed
        return "Your income and benefits fully cover your care costs with no asset drawdown needed."
    
    elif runway_years == 0:
        # Assets insufficient
        return "Your current assets are insufficient to cover care costs. Immediate financial planning recommended."
    
    elif runway_years >= 30:
        # Assets last 30+ years
        return "Based on your cost of care and your assets, you can pay for this care plan for 30+ years."
    
    elif runway_years == 1:
        # Less than 2 years
        remaining_months = runway_months % 12
        if remaining_months > 0:
            return f"Based on your cost of care and your assets, you can pay for this care plan for 1 year and {remaining_months} months."
        else:
            return "Based on your cost of care and your assets, you can pay for this care plan for 1 year."
    
    else:
        # Multiple years
        remaining_months = runway_months % 12
        if remaining_months > 0:
            return f"Based on your cost of care and your assets, you can pay for this care plan for {runway_years} years and {remaining_months} months."
        else:
            return f"Based on your cost of care and your assets, you can pay for this care plan for {runway_years} years."


def _publish_to_mcip():
    """Aggregate module data and publish to MCIP with proper cost calculation."""
    from datetime import datetime
    from core.mcip import FinancialProfile, MCIP
    from products.cost_planner_v2.utils.cost_calculator import CostCalculator
    
    modules_state = st.session_state.cost_v2_modules
    
    # =========================================================================
    # 1. AGGREGATE INCOME FROM ALL SOURCES
    # =========================================================================
    income_data = modules_state.get("income", {}).get("data", {})
    monthly_income_sources = {
        'social_security': income_data.get('ss_monthly', 0),  # Field from income.py
        'pension': income_data.get('pension_monthly', 0),
        'employment': income_data.get('employment_monthly', 0),
        'investment': income_data.get('investment_monthly', 0),
        'other': income_data.get('other_monthly', 0)
    }
    total_monthly_income = sum(monthly_income_sources.values())
    
    # =========================================================================
    # 2. AGGREGATE ASSETS FROM ALL SOURCES
    # =========================================================================
    assets_data = modules_state.get("assets", {}).get("data", {})
    
    # Calculate liquid assets (checking + savings + CDs/money market)
    liquid_assets = assets_data.get('checking_savings', 0) + assets_data.get('cds_money_market', 0)
    
    # Calculate retirement accounts
    retirement_total = sum([
        assets_data.get('ira_traditional', 0),
        assets_data.get('ira_roth', 0),
        assets_data.get('k401_403b', 0),
        assets_data.get('other_retirement', 0)
    ])
    
    # Calculate investments
    investments_total = assets_data.get('stocks_bonds', 0) + assets_data.get('mutual_funds', 0)
    
    # Real estate (just investment property, not primary residence for Medicaid purposes)
    real_estate = assets_data.get('investment_property', 0)
    
    asset_categories = {
        'liquid': liquid_assets,
        'retirement': retirement_total,
        'investments': investments_total,
        'real_estate': real_estate,
        'business': assets_data.get('business_value', 0),
        'other': assets_data.get('other_assets_value', 0)
    }
    total_assets = sum(asset_categories.values())
    
    # =========================================================================
    # 3. AGGREGATE COVERAGE FROM BENEFITS & INSURANCE
    # =========================================================================
    
    # VA Benefits
    va_data = modules_state.get("va_benefits", {}).get("data", {})
    va_monthly_benefit = 0
    
    # Sum VA disability and Aid & Attendance benefits (only if module completed)
    if va_data and va_data.get('is_veteran'):
        va_monthly_benefit = sum([
            va_data.get('va_disability_monthly', 0),
            va_data.get('aid_attendance_monthly', 0)
        ])
    
    # Health Insurance (LTC)
    insurance_data = modules_state.get("health_insurance", {}).get("data", {})
    ltc_monthly_coverage = 0
    has_medicare = False
    
    # Only process if insurance data exists
    if insurance_data:
        if insurance_data.get('has_ltc_insurance'):
            ltc_daily_benefit = insurance_data.get('ltc_daily_benefit', 0)
            ltc_max_days = insurance_data.get('ltc_max_benefit_days', 0)
            ltc_monthly_coverage = ltc_daily_benefit * 30  # Convert daily to monthly
        
        # Medicare coverage (typically doesn't cover long-term care, but note it)
        has_medicare = insurance_data.get('has_medicare', False)
    
    # Total monthly coverage from benefits/insurance
    total_monthly_coverage = va_monthly_benefit + ltc_monthly_coverage
    
    # =========================================================================
    # 4. CALCULATE ESTIMATED MONTHLY COST BASED ON CARE RECOMMENDATION
    # =========================================================================
    
    # Get care recommendation from GCP
    care_recommendation = MCIP.get_care_recommendation()
    
    if care_recommendation and care_recommendation.tier:
        # Use actual care tier and regional data to calculate costs
        user_zip = assets_data.get('primary_residence_zip')  # If collected
        user_state = assets_data.get('primary_residence_state')  # If collected
        
        # Calculate cost estimate using the CostCalculator
        try:
            cost_estimate = CostCalculator.calculate_comprehensive_estimate(
                care_tier=care_recommendation.tier,
                zip_code=user_zip,
                state=user_state
            )
            estimated_monthly_cost = cost_estimate.monthly_adjusted
        except Exception:
            # Fallback to default national averages if calculation fails
            tier_defaults = {
                'independent': 2500,
                'in_home': 4500,
                'assisted_living': 5000,
                'memory_care': 7000,
                'memory_care_high_acuity': 9000
            }
            estimated_monthly_cost = tier_defaults.get(care_recommendation.tier, 5000)
    else:
        # No care recommendation - use national average for assisted living
        estimated_monthly_cost = 5000
    
    # =========================================================================
    # 5. CALCULATE FINANCIAL RUNWAY (HOW LONG ASSETS WILL LAST WITH INFLATION)
    # =========================================================================
    
    # Calculate monthly gap (cost - income - coverage)
    monthly_gap = estimated_monthly_cost - total_monthly_income - total_monthly_coverage
    
    # Calculate runway in months with 3% annual inflation (matches expert_review.py)
    runway_months = 0
    runway_years = 0
    
    if monthly_gap > 0 and liquid_assets > 0:
        # Calculate year-by-year with 3% inflation until assets depleted or 30 years
        inflation_rate = 0.03
        remaining_assets = liquid_assets
        
        for year in range(1, 31):  # Cap at 30 years
            # Calculate inflated monthly gap for this year
            inflation_multiplier = (1 + inflation_rate) ** year
            inflated_monthly_gap = monthly_gap * inflation_multiplier
            annual_gap = inflated_monthly_gap * 12
            
            # Calculate remaining assets after this year
            remaining_assets -= annual_gap
            
            if remaining_assets <= 0:
                # Assets depleted during this year
                runway_years = year
                runway_months = year * 12
                break
        
        if runway_years == 0:
            # Assets last beyond 30 years
            runway_years = 30
            runway_months = 360
    
    elif monthly_gap <= 0:
        # Fully covered by income + benefits
        runway_years = 30  # Max out at 30 years
        runway_months = 360
    else:
        # No liquid assets to cover gap
        runway_years = 0
        runway_months = 0
    
    # Calculate coverage percentage
    monthly_resources = total_monthly_income + total_monthly_coverage
    coverage_percentage = int((monthly_resources / estimated_monthly_cost * 100)) if estimated_monthly_cost > 0 else 0
    
    # =========================================================================
    # 6. BUILD AND PUBLISH FINANCIAL PROFILE CONTRACT
    # =========================================================================
    
    financial_profile = FinancialProfile(
        estimated_monthly_cost=round(estimated_monthly_cost, 2),
        coverage_percentage=min(coverage_percentage, 100),  # Cap at 100%
        gap_amount=round(monthly_gap, 2),
        runway_months=runway_months,
        confidence=0.95,  # Very high confidence from detailed Financial Assessment modules
        generated_at=datetime.utcnow().isoformat() + "Z",
        status="complete"
    )
    
    # Publish to MCIP for use by other products
    MCIP.publish_financial_profile(financial_profile)
    
    # Store detailed breakdown in session state for Cost Planner access
    st.session_state["financial_assessment_complete"] = {
        "income": {
            "sources": monthly_income_sources,
            "total_monthly": total_monthly_income
        },
        "assets": {
            "categories": asset_categories,
            "total": total_assets,
            "liquid": liquid_assets
        },
        "coverage": {
            "va_benefit": va_monthly_benefit,
            "ltc_coverage": ltc_monthly_coverage,
            "has_medicare": has_medicare,
            "total_monthly": total_monthly_coverage
        },
        "costs": {
            "estimated_monthly": estimated_monthly_cost,
            "care_tier": care_recommendation.tier if care_recommendation else "unknown"
        },
        "timeline": {
            "monthly_gap": monthly_gap,
            "runway_months": runway_months,
            "runway_years": runway_years,
            "coverage_percentage": coverage_percentage,
            "summary_message": _format_runway_message(runway_years, runway_months, monthly_gap)
        },
        "generated_at": datetime.utcnow().isoformat()
    }
    
    # Mark product complete
    MCIP.mark_product_complete("cost_v2")
    
    # Mark as published
    st.session_state["cost_planner_v2_published"] = True
