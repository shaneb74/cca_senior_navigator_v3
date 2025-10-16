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
    
    # Render Navi panel for guidance
    render_navi_panel(
        location="product",
        product_key="cost_planner_v2"
    )
    
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
