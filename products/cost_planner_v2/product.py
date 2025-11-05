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
from ui.product_shell import product_shell_end, product_shell_start


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

    # DEBUG: Log GCP state on Cost Planner mount
    print("[CP_MOUNT] Cost Planner v2 Loading")
    gcp_state = st.session_state.get("gcp", {})
    if gcp_state:
        print(f"[CP_GCP_STATE] published_tier={gcp_state.get('published_tier')} allowed_tiers={gcp_state.get('allowed_tiers')}")
    else:
        print("[CP_GCP_STATE] No GCP state found - user may not have completed GCP yet")

    # Check MCIP contract as fallback
    from core.mcip import MCIP
    mcip_rec = MCIP.get_care_recommendation()
    if mcip_rec:
        print(f"[CP_MCIP] tier={mcip_rec.tier} allowed={getattr(mcip_rec, 'allowed_tiers', None)}")

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

    product_shell_start()

    # HOUSEHOLD FLOW: Detect dual-person mode for cost planning
    try:
        from core.household import get_careplan_for
        primary_id = st.session_state.get("person.primary_id")
        partner_id = st.session_state.get("person.partner_id")

        cp_primary = get_careplan_for(st, primary_id) if primary_id else None
        cp_partner = get_careplan_for(st, partner_id) if partner_id else None

        # Set dual mode flag if both CarePlans exist
        dual_mode = bool(cp_primary and cp_partner)
        st.session_state["cost.dual_mode"] = dual_mode

        if dual_mode:
            print(f"[COST_PLANNER] Dual mode enabled: primary={cp_primary.uid} partner={cp_partner.uid}")
    except Exception:
        st.session_state["cost.dual_mode"] = False

    # Initialize step state - check if user has progressed past intro
    if "cost_v2_step" not in st.session_state:
        # Check query params for explicit step override (from tile buttons)
        step_from_query = st.query_params.get("step")
        if step_from_query in ["intro", "auth", "triage", "assessments", "modules", "expert_review", "exit"]:
            st.session_state.cost_v2_step = step_from_query
        # Check if user has completed intro by checking for assessment state
        elif "cost_v2_income" in st.session_state or "cost_v2_assets" in st.session_state:
            # User has been to Financial Assessment - resume there
            st.session_state.cost_v2_step = "assessments"
        elif "cost_v2_qualifiers" in st.session_state:
            # User has completed qualifiers - resume at assessments
            st.session_state.cost_v2_step = "assessments"
        else:
            # First time - start at intro
            st.session_state.cost_v2_step = "intro"
    else:
        # If step is already in session_state, check if query param wants to override
        step_from_query = st.query_params.get("step")
        if step_from_query in ["intro", "auth", "triage", "assessments", "modules", "expert_review", "exit"]:
            # Allow query param to override current step (for tile buttons)
            if st.session_state.cost_v2_step != step_from_query:
                st.session_state.cost_v2_step = step_from_query

    current_step = st.session_state.cost_v2_step


    # Navi rendering disabled - now handled by compact panels at page level
    # Each Cost Planner page renders its own compact Navi at the top
    # _render_navi_with_context(current_step)

    # Route to appropriate step
    if current_step == "intro":
        _render_intro_step()
    elif current_step == "auth":
        _render_auth_step()
    elif current_step == "triage":
        _render_triage_step()
    elif current_step == "medicaid_clarification":
        _render_medicaid_clarification_step()
    elif current_step == "medicaid_assessment":
        _render_medicaid_assessment_step()
    elif current_step == "medicaid_resources":
        _render_medicaid_resources_step()
    elif current_step in ["modules", "assessments"]:
        # Support both old "modules" and new "assessments" step names for backward compatibility
        _render_assessments_step()
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
    """DEPRECATED - Hero Navi panels removed from Cost Planner.
    
    This function is no longer used. All Cost Planner pages now use
    compact Navi panels at the page level via render_module_navi_coach().
    
    Old implementation created hero-style Navi panels that duplicated
    content and cluttered the UI. Now each page owns its compact panel.
    """
    pass  # Function deprecated, call site already commented out


def _render_intro_step():
    """Step 1: Intro with quick estimate (unauthenticated)."""
    from products.cost_planner_v2 import intro

    intro.render()


def _render_auth_step():
    """Step 2: Authentication gate."""
    from products.cost_planner_v2 import auth

    auth.render()


def _render_triage_step():
    """Step 3: Quick qualifier questions (Veteran, Homeowner, Medicaid)."""
    from products.cost_planner_v2 import triage

    triage.render()


def _render_medicaid_clarification_step():
    """Step 3a: Medicaid vs Medicare clarification."""
    from pages.assessments_medicaid import render
    
    render()


def _render_medicaid_assessment_step():
    """Step 3b: Simplified Medicaid assessment."""
    from pages.assessments_medicaid import render_medicaid_assessment
    
    render_medicaid_assessment()


def _render_medicaid_resources_step():
    """Step 3c: Medicaid resources and next steps."""
    from pages.assessments_medicaid import render_medicaid_resources
    
    render_medicaid_resources()


def _render_assessments_step():
    """Step 4: Financial Assessment hub (now using JSON-driven assessments)."""
    from products.cost_planner_v2.assessments import render_assessment_hub

    render_assessment_hub(product_key="cost_planner_v2")


def _render_assessment_page_step(assessment_key: str):
    """Render a single assessment page (Phase 5: page-based flow)."""
    from products.cost_planner_v2.assessments import render_assessment_page

    render_assessment_page(assessment_key=assessment_key, product_key="cost_planner_v2")


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
        if st.button(
            "➡️ Continue to Financial Assessment",
            type="primary",
            use_container_width=True,
            key="gate_continue",
        ):
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
    
    Uses a flag to prevent clearing state on every render - only on first load.
    """
    # Check if we've already handled restart in this session
    if st.session_state.get("_cost_v2_restart_handled", False):
        return  # Already restarted, don't clear state again

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

    # Set flag FIRST to prevent re-clearing on next render
    st.session_state._cost_v2_restart_handled = True

    # 1. Clear cost planner step state
    if "cost_v2_step" in st.session_state:
        st.session_state.cost_v2_step = "intro"

    # 2. Clear financial module states AND quick estimate
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
        "cost_v2_quick_estimate",  # Clear quick estimate to force fresh calculation
        "cost_v2_triage",
        "cost_v2_qualifiers",
        # Clear quick estimate form widget keys
        "cost_v2_quick_zip",
        "cost_v2_quick_care_type",
        "calc_estimate_btn",
        "continue_full_assessment",  # Clear continue button state
        "recalculate",  # Clear recalculate button state
        "intro_back_hub",  # Clear back button state
        # Clear assessment state
        "cost_planner_v2_current_assessment",
        # Clear persisted assessment data
        "cost_planner_v2_income",
        "cost_planner_v2_assets",
        "cost_planner_v2_va_benefits",
        "cost_planner_v2_health_insurance",
        "cost_planner_v2_life_insurance",
        "cost_planner_v2_medicaid_navigation",
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
        if hasattr(MCIP, "_data") and "product_summaries" in MCIP._data:
            if "cost_v2" in MCIP._data["product_summaries"]:
                del MCIP._data["product_summaries"]["cost_v2"]
            if "cost_planner" in MCIP._data["product_summaries"]:
                del MCIP._data["product_summaries"]["cost_planner"]
        # Mark Cost Planner as not complete in journey
        if hasattr(MCIP, "_data") and "journey_progress" in MCIP._data:
            if "cost_planner" in MCIP._data["journey_progress"]:
                MCIP._data["journey_progress"]["cost_planner"] = 0
            if "cost_v2" in MCIP._data["journey_progress"]:
                MCIP._data["journey_progress"]["cost_v2"] = 0
    except Exception:
        pass  # If MCIP clear fails, state is already cleared above

    # 5. Persist the cleared state to disk
    # This ensures the cleared keys are saved to the user file
    # so they don't get reloaded on next page navigation
    try:
        from core.session_store import extract_user_state, get_or_create_user_id, save_user

        uid = get_or_create_user_id(st.session_state)
        user_data = extract_user_state(st.session_state)
        save_user(uid, user_data)
    except Exception:
        pass  # Silently handle persistence errors

    # Note: GCP state and recommendation preserved automatically
