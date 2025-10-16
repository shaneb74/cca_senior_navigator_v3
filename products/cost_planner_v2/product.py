"""
Cost Planner v2 Product Router

Workflow:
1. Intro/Quick Estimate (unauthenticated)
2. Auth Gate (sign in or continue as guest)
3. Triage (existing customer vs planning)
4. Financial Modules (income, costs, coverage)
5. Expert Advisor Review
6. Exit

Note: GCP (Guided Care Plan) is recommended but NOT required.
Users can complete Cost Planner with general estimates.
"""

import streamlit as st
from core.mcip import MCIP
from core.navi import render_navi_panel
from core.state import get_user_name
from layout import static_url
from ui.product_shell import product_shell_start, product_shell_end


def render():
    """Render Cost Planner v2 workflow.
    
    Step routing:
    - Step 1: Intro (unauthenticated quick estimate)
    - Step 2: Auth (sign in or guest mode)
    - Step 3: Triage (existing vs planning)
    - Step 4: Modules (financial assessment)
    - Step 5: Expert Review
    - Step 6: Exit
    
    Note: GCP gate removed from workflow. GCP is recommended
    but accessed separately via navigation, not forced in flow.
    """
    
    # Check for restart intent (when complete and re-entering at intro)
    _handle_restart_if_needed()
    
    # CRITICAL: Ensure cost_planner is unlocked when accessed
    # This handles the case where a user navigates directly to Cost Planner
    # without completing GCP first
    MCIP.initialize()
    unlocked_products = MCIP.get_unlocked_products()
    if "cost_planner" not in unlocked_products and "cost_v2" not in unlocked_products:
        # Auto-unlock cost planner since user is accessing it
        journey = st.session_state["mcip"]["journey"]
        if "cost_planner" not in journey["unlocked_products"]:
            journey["unlocked_products"].append("cost_planner")
        if "cost_v2" not in journey["unlocked_products"]:
            journey["unlocked_products"].append("cost_v2")
        # Save the updated journey state
        MCIP._save_contracts_for_persistence()
        print(f"[COST_PLANNER] Auto-unlocked cost_planner and cost_v2")
        print(f"[COST_PLANNER] Updated unlocked_products: {journey['unlocked_products']}")
    
    product_shell_start()
    
    # Render Navi panel with dynamic guidance based on step and GCP status
    _render_navi_with_context(current_step)
    
    # Initialize step state
    if "cost_v2_step" not in st.session_state:
        st.session_state.cost_v2_step = "intro"
    
    current_step = st.session_state.cost_v2_step
    
    # Route to appropriate step
    if current_step == "intro":
        _render_intro_step()
    elif current_step == "auth":
        _render_auth_step()
    elif current_step == "triage":
        _render_triage_step()
    elif current_step == "modules":
        _render_modules_step()
    elif current_step == "module_active":
        _render_active_module()
    elif current_step == "expert_review":
        _render_expert_review_step()
    elif current_step == "exit":
        _render_exit_step()
    else:
        # Fallback to intro
        st.session_state.cost_v2_step = "intro"
        st.rerun()
    
    product_shell_end()


def _render_navi_with_context(current_step: str):
    """Render Navi panel with context-aware guidance.
    
    Provides specific, helpful guidance based on:
    - Current step in Cost Planner workflow
    - Whether user has completed GCP
    - GCP recommendation if available
    """
    
    # Get GCP recommendation if available
    gcp_rec = MCIP.get_care_recommendation()
    has_gcp = gcp_rec and gcp_rec.tier
    
    # Care tier display names
    tier_display_map = {
        "no_care_needed": "No Care Recommended",
        "in_home_care": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)"
    }
    
    # Build context-aware message based on step
    if current_step == "intro":
        if has_gcp:
            recommended_care = tier_display_map.get(gcp_rec.tier, gcp_rec.tier)
            title = "Let's explore care costs"
            reason = f"""Based on your Guided Care Plan, I recommend **{recommended_care}**.
            
You can calculate costs for this recommendation below, or explore other care scenarios to compare options.

**Why this matters:** Understanding costs early helps you plan ahead and identify funding sources."""
            encouragement = {
                "icon": "💡",
                "status": "info",
                "message": "Feel free to calculate multiple scenarios. Your GCP recommendation will stay visible so you can always refer back to it."
            }
        else:
            title = "Let's get a quick cost estimate"
            reason = """Enter your ZIP code and select a care type to see ballpark costs in your area.
            
**Pro tip:** If you complete the Guided Care Plan first, I can give you a personalized recommendation and more accurate cost estimates based on specific care needs."""
            encouragement = {
                "icon": "📊",
                "status": "info",
                "message": "These are general estimates. For a detailed financial plan with funding sources and strategies, continue to the Full Assessment after calculating."
            }
        
        render_navi_panel(
            location="product",
            product_key="cost_planner_v2",
            title=title,
            reason=reason,
            encouragement=encouragement
        )
    
    else:
        # For other steps, use default Navi guidance
        render_navi_panel(
            location="product",
            product_key="cost_planner_v2"
        )


def _render_intro_step():
    """Step 1: Intro with quick estimate (unauthenticated)."""
    from products.cost_planner_v2 import intro
    intro.render()


def _render_auth_step():
    """Step 2: Authentication gate."""
    from products.cost_planner_v2 import auth
    auth.render()


def _render_triage_step():
    """Step 3: Status triage (existing vs planning)."""
    from products.cost_planner_v2 import triage
    triage.render()


def _render_modules_step():
    """Step 4: Financial modules hub."""
    from products.cost_planner_v2 import hub
    hub.render()


def _render_active_module():
    """Render currently active financial module."""
    module_key = st.session_state.get("cost_v2_current_module")
    
    if not module_key:
        # No module selected - go back to hub
        st.session_state.cost_v2_step = "modules"
        st.rerun()
        return
    
    # Import the specific module renderer based on key
    try:
        if module_key == "income":
            from products.cost_planner_v2.modules import income
            income.render()
        elif module_key == "assets":
            from products.cost_planner_v2.modules import assets
            assets.render()
        elif module_key == "va_benefits":
            from products.cost_planner_v2.modules import va_benefits
            va_benefits.render()
        elif module_key == "health_insurance":
            from products.cost_planner_v2.modules import health_insurance
            health_insurance.render()
        elif module_key == "life_insurance":
            from products.cost_planner_v2.modules import life_insurance
            life_insurance.render()
        elif module_key == "medicaid_navigation":
            from products.cost_planner_v2.modules import medicaid_navigation
            medicaid_navigation.render()
        else:
            st.error(f"Unknown module: {module_key}")
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    except Exception as e:
        st.error(f"Error loading module '{module_key}': {e}")
        st.session_state.cost_v2_step = "modules"
        st.rerun()


def _render_expert_review_step():
    """Step 5: Expert Advisor Review."""
    from products.cost_planner_v2 import expert_review
    expert_review.render()


def _render_exit_step():
    """Step 6: Exit with summary and next actions."""
    from products.cost_planner_v2 import exit
    exit.render()


def _render_exit_step():
    """Step 7: Exit with summary and next actions."""
    from products.cost_planner_v2 import exit
    exit.render()


def _render_gcp_gate():
    """Show recommendation to complete GCP for personalized estimates.
    
    Updated behavior: GCP is recommended but NOT required.
    Users can proceed to Financial Modules with general estimates.
    """
    
    st.title("💰 Financial Planning")
    
    st.success("### 💡 Get Personalized Estimates (Recommended)")
    
    st.markdown("""
    For the most accurate cost estimates, we recommend completing the **Guided Care Plan** first.
    
    The Guided Care Plan takes just 2 minutes and will:
    - ✅ Assess daily living needs
    - ✅ Evaluate safety and cognitive factors  
    - ✅ Recommend the right care level
    - ✅ Unlock personalized cost estimates
    
    ---
    
    **You can continue without it**, but your estimates will be based on general averages 
    rather than your specific care needs.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("➡️ Continue to Financial Modules", type="primary", use_container_width=True, key="gate_continue"):
            st.session_state.cost_v2_step = "triage"
            st.rerun()
    
    with col2:
        if st.button("� Start Guided Care Plan", use_container_width=True, key="gate_start_gcp"):
            from core.nav import route_to
            route_to("gcp_v4")
    
    # Optional: Show what user will get after completing GCP
    with st.expander("📊 Benefits of completing the Guided Care Plan first"):
        st.markdown("""
        With a personalized care recommendation, you'll get:
        
        1. **Base Care Costs** - Monthly costs for YOUR recommended care level
        2. **Care Hours Calculator** - Cost of hourly care tailored to your needs
        3. **Additional Services** - Therapy, transportation, activities matched to your situation
        4. **Veteran Benefits** - Calculate VA Aid & Attendance eligibility with accurate care level
        5. **Insurance & Medicare** - Apply coverage to your specific costs
        6. **Facility Selection** - Compare facilities appropriate for your care level
        
        You'll receive:
        - 💰 **Personalized monthly cost breakdown**
        - 📊 **3-year and 5-year projections based on your care trajectory**
        - 💳 **Accurate funding gap analysis**
        - 📍 **Regional cost comparisons for your care level**
        
        **Without GCP:** You'll see general cost ranges that may not match your actual needs.
        """)


def _handle_restart_if_needed() -> None:
    """Handle restart when user clicks 'Restart' button on completed Cost Planner.
    
    Clears Cost Planner state to start fresh, but preserves GCP recommendation.
    Only triggers when Cost Planner is complete and user is at intro step.
    """
    # Check if Cost Planner is complete
    try:
        from core.mcip import MCIP
        if not MCIP.is_product_complete("cost_planner"):
            return  # Not complete, no restart needed
    except Exception:
        return  # Error checking MCIP, skip restart
    
    # Check if we're at intro (restart scenario)
    current_step = st.session_state.get("cost_v2_step", "intro")
    if current_step != "intro":
        return  # Not at intro, don't auto-restart
    
    # RESTART: Clear Cost Planner state but preserve GCP
    # 1. Clear cost planner step state
    if "cost_v2_step" in st.session_state:
        st.session_state.cost_v2_step = "intro"
    
    # 2. Clear financial module states
    module_keys = [
        "cost_v2_current_module",
        "cost_v2_guest_mode",
        "cost_v2_income",
        "cost_v2_assets", 
        "cost_v2_va_benefits",
        "cost_v2_health_insurance",
        "cost_v2_life_insurance",
        "cost_v2_medicaid",
        "cost_v2_modules_complete",
        "cost_v2_expert_review",
    ]
    for key in module_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # 3. Clear tile state
    tiles = st.session_state.get("tiles", {})
    if "cost_v2" in tiles:
        tiles["cost_v2"] = {}
    if "cost_planner" in tiles:
        tiles["cost_planner"] = {}
    
    # 4. Reset MCIP Cost Planner completion (but preserve GCP!)
    try:
        from core.mcip import MCIP
        # Clear Cost Planner summary so it shows as not complete
        if hasattr(MCIP, '_data') and 'product_summaries' in MCIP._data:
            if 'cost_v2' in MCIP._data['product_summaries']:
                del MCIP._data['product_summaries']['cost_v2']
            if 'cost_planner' in MCIP._data['product_summaries']:
                del MCIP._data['product_summaries']['cost_planner']
        # Mark Cost Planner as not complete in journey
        if hasattr(MCIP, '_data') and 'journey_progress' in MCIP._data:
            if 'cost_planner' in MCIP._data['journey_progress']:
                MCIP._data['journey_progress']['cost_planner'] = 0
            if 'cost_v2' in MCIP._data['journey_progress']:
                MCIP._data['journey_progress']['cost_v2'] = 0
    except Exception:
        pass  # If MCIP clear fails, state is already cleared above
    
    # Note: GCP state and recommendation preserved automatically
