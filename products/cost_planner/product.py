"""Cost Planner product entry point and router.

This module handles routing between the base module (landing/dashboard)
and individual calculation sub-modules (income, assets, costs, etc.).
"""

from typing import Optional
import streamlit as st
import importlib

from core.modules.engine import run_module
from core.nav import route_to
from products.cost_planner import auth
from products.cost_planner.base_module_config import get_base_config
from products.cost_planner.cost_estimate_v2 import (
    get_recommended_care_type,
    get_gcp_recommendation,
    get_gcp_recommendation_display,
    calculate_cost_estimate,
    render_cost_breakdown,
)
from ui.product_shell import product_shell_start, product_shell_end


def render(module: Optional[str] = None) -> None:
    """Render Cost Planner product.
    
    Routes to either the base module (landing/dashboard) or a specific
    calculation sub-module based on URL parameters.
    
    Args:
        module: Optional module key to render directly
                If None, checks query params for 'cost_module'
    """
    product_shell_start()
    
    # Show mock authentication controls in sidebar (dev mode)
    auth.mock_login_button()
    
    # Check if GCP has been completed - required for Cost Planner
    # Use same check as hub tile: progress >= 100
    # NOTE: On first render after navigation, session state may be empty {}.
    # Check if GCP state exists at all - if it's {}, state hasn't loaded yet, so wait.
    gcp_state = st.session_state.get("gcp", {})
    
    # If GCP state is completely empty, it means we're still loading - don't block yet
    if not gcp_state:
        # State not loaded yet - proceed without gate check, will check on next render
        pass
    else:
        # State is loaded, check progress
        gcp_progress = float(gcp_state.get("progress", 0))
        
        if gcp_progress < 100:
            # GCP not completed - show requirement message
            st.warning("⚠️ **Guided Care Plan Required**")
            st.markdown(
                """
                The Cost Planner depends on your personalized care recommendation from the 
                Guided Care Plan assessment.
                
                **Please complete the Guided Care Plan first** to:
                - Get your personalized care recommendation
                - See accurate cost estimates for your situation
                - Access the full Cost Planner features
                """
            )
            
            if st.button("← Go to Guided Care Plan", type="primary"):
                st.query_params.clear()
                st.query_params["page"] = "gcp"
                st.rerun()
            
            render_shell_end()
            return
    
    # Determine which module to render
    target_module = st.query_params.get("cost_module", module)
    
    if not target_module or target_module == "base":
        # Render base/home module (router/dashboard)
        _render_base_module()
    elif target_module == "expert_review":
        # Render Expert Review page
        _render_expert_review()
    elif target_module == "financial_timeline":
        # Render Financial Timeline page
        _render_financial_timeline()
    else:
        # Render specific calculation module
        _render_sub_module(target_module)
    
    render_shell_end()


def _render_base_module() -> None:
    """Render base/home module (landing page + module dashboard).
    
    The base module is public (no authentication required) and serves as:
    - Product introduction/welcome
    - Quick Estimate (care type selection + cost comparison)
    - Authentication gate before Full Assessment
    - Profile flags collection (veteran, homeowner, medicaid)
    - Module selection dashboard
    """
    config = get_base_config()
    
    # Get current step index to determine which step we're on
    state_key = config.state_key
    step_index = int(st.session_state.get(f"{state_key}._step", 0))
    
    # DEBUG: Show current step info
    st.sidebar.write(f"🔍 Debug: step_index={step_index}")
    if step_index < len(config.steps):
        st.sidebar.write(f"🔍 Debug: step.id={config.steps[step_index].id}")
    
    # DEBUG: Reset button if on wrong step
    if step_index >= len(config.steps):
        st.sidebar.error(f"⚠️ Step index {step_index} exceeds config steps ({len(config.steps)})")
        if st.sidebar.button("🔄 Reset to Intro"):
            st.session_state[f"{state_key}._step"] = 0
            st.rerun()
    
    # Check if we're on a step that needs custom rendering (bypass standard module engine)
    if step_index < len(config.steps):
        step = config.steps[step_index]
        
        if step.id == "quick_estimate":
            st.sidebar.success("✅ Using CUSTOM rendering for quick_estimate")
            # Custom rendering for quick estimate with dynamic button behavior
            _render_quick_estimate_custom(config, step, step_index)
            return
        elif step.id == "auth_gate":
            st.sidebar.success("✅ Using CUSTOM rendering for auth_gate")
            # Custom rendering for auth gate
            _render_auth_gate_custom(config, step, step_index)
            return
        elif step.id == "profile_flags":
            st.sidebar.success("✅ Using CUSTOM rendering for profile_flags")
            # Custom rendering for profile flags to avoid the phantom page
            _render_profile_flags_custom(config, step, step_index)
            return
        elif step.id == "module_dashboard":
            st.sidebar.success("✅ Using CUSTOM rendering for module_dashboard")
            # Custom rendering for module dashboard
            _render_module_dashboard_custom(config, step, step_index)
            return
        elif step.id == "intro":
            st.sidebar.success("✅ Using STANDARD rendering for intro")
            # Intro step uses standard module engine (just shows text + continue button)
            context = run_module(config)
            return
        else:
            st.sidebar.warning(f"⚠️ Unknown step: {step.id}")
    
    # If we got here, something is very wrong - show error
    st.error(f"❌ No rendering path found for step_index={step_index}")
    st.write(f"Config has {len(config.steps)} steps")
    if step_index < len(config.steps):
        st.write(f"Step ID: {config.steps[step_index].id}")
    st.stop()


def _render_quick_estimate_header() -> None:
    """Render GCP recommendation summary before the quick estimate form."""
    # Get GCP recommendation (required - user must complete GCP first)
    gcp_rec = get_gcp_recommendation()
    gcp_rec_display = get_gcp_recommendation_display()
    
    # Display recommendation summary prominently
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 32%, #111827 100%); 
                    padding: 24px; border-radius: 12px; color: white; margin-bottom: 24px;">
            <h3 style="color: white; margin: 0 0 12px 0;">Your Care Recommendation</h3>
            <p style="font-size: 1.3em; font-weight: 600; margin: 0;">
                {gcp_rec if gcp_rec else "Complete Guided Care Plan First"}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Note about comparing options and regional pricing
    st.caption(
        "💡 You can select a different care type below to compare options. "
        "We'll provide regional pricing after you complete authentication."
    )


def _render_quick_estimate_custom(config, step, step_index: int) -> None:
    """Custom rendering for quick estimate step with dynamic button behavior."""
    state_key = config.state_key
    st.session_state.setdefault(state_key, {})
    state = st.session_state[state_key]
    
    # Initialize estimate shown flag
    estimate_shown_key = f"{state_key}._estimate_shown"
    if estimate_shown_key not in st.session_state:
        st.session_state[estimate_shown_key] = False
    
    # Simple header
    st.markdown(f"### {step.title}")
    if step.subtitle:
        st.caption(step.subtitle)
    
    # Show GCP recommendation summary
    _render_quick_estimate_header()
    
    # ZIP Code input (needed for regional cost multipliers)
    st.markdown("### Enter your ZIP code")
    zip_code = st.text_input(
        "ZIP Code",
        value=state.get("profile", {}).get("zip_code", ""),
        max_chars=5,
        help="We'll use this to provide regional cost estimates",
        key=f"{state_key}_quick_zip",
        label_visibility="collapsed",
        placeholder="Enter 5-digit ZIP code"
    )
    
    # Save ZIP to profile
    if zip_code:
        if "profile" not in state:
            state["profile"] = {}
        state["profile"]["zip_code"] = zip_code
    
    st.markdown("")  # Spacing
    
    # Render care type selection field
    st.markdown("### Select care type to estimate")
    
    # Get GCP recommended care type for pre-selection
    recommended_care_type = get_recommended_care_type()
    current_selection = state.get("answers", {}).get("selected_care_type", recommended_care_type)
    
    # Care type options
    care_options = {
        "no_care": "No Care Needed - Living independently ($0/month)",
        "in_home_care": "In-Home Care - Part-time assistance ($5,200/month avg)",
        "assisted_living": "Assisted Living - 24/7 support community ($5,500/month avg)",
        "memory_care": "Memory Care - Specialized cognitive care ($7,200/month avg)",
        "memory_care_high_acuity": "Memory Care (High Acuity) - Intensive care ($9,000/month avg)"
    }
    
    selected_care_type = st.radio(
        "Care Type",
        options=list(care_options.keys()),
        format_func=lambda x: care_options[x],
        index=list(care_options.keys()).index(current_selection) if current_selection in care_options else 0,
        key=f"{state_key}_care_type_radio",
        label_visibility="collapsed"
    )
    
    # Save selection to state
    if "answers" not in state:
        state["answers"] = {}
    state["answers"]["selected_care_type"] = selected_care_type
    
    # Show cost estimate if "See My Estimate" was clicked
    if st.session_state.get(estimate_shown_key, False):
        st.divider()
        st.markdown("### Your Cost Estimate")
        
        try:
            # Use ZIP code if provided, otherwise None for national average
            user_zip = state.get("profile", {}).get("zip_code")
            estimate = calculate_cost_estimate(selected_care_type, zip_code=user_zip)
            render_cost_breakdown(estimate, show_details=True)
            
            if user_zip:
                st.info(
                    f"📍 **Regional Estimate:** Costs adjusted for ZIP code {user_zip}. "
                    "Change your ZIP code above to see estimates for other regions."
                )
            else:
                st.info(
                    "📍 **National Average:** This estimate uses national average costs. "
                    "Enter your ZIP code above to see regional pricing."
                )
        except Exception as e:
            st.error(f"Error calculating estimate: {e}")
        
        st.caption("💡 **Tip:** You can change the care type above to compare different options before continuing.")
    
    # Action buttons with dynamic label
    st.divider()
    st.markdown('<div class="sn-app mod-actions">', unsafe_allow_html=True)
    
    if not st.session_state.get(estimate_shown_key, False):
        # Show "See My Estimate" button
        if st.button("See My Estimate", key="_quick_est_show", type="primary", use_container_width=True):
            st.session_state[estimate_shown_key] = True
            st.rerun()
    else:
        # Show "Continue to Full Assessment" button
        if st.button("Continue to Full Assessment", key="_quick_est_continue", type="primary", use_container_width=True):
            # Check if authenticated - if not, go to auth gate
            # If yes, go directly to profile flags
            is_auth = auth.is_authenticated()
            target_step = 3 if is_auth else 2
            
            # DEBUG: Log what's happening
            st.sidebar.write(f"🔍 Button clicked! Auth={is_auth}, target_step={target_step}")
            
            # Set the step
            st.session_state[f"{state_key}._step"] = target_step
            
            # DEBUG: Verify it was set
            actual_step = st.session_state.get(f"{state_key}._step", "NOT SET")
            st.sidebar.write(f"🔍 Step set to: {actual_step}")
            
            st.rerun()
    
    # Save & Continue Later button
    st.markdown('<div style="margin-top: 0.75rem;">', unsafe_allow_html=True)
    if st.button("💾 Save & Continue Later", key="_quick_est_save", type="secondary", use_container_width=True):
        # Save current step to tiles
        tiles = st.session_state.setdefault("tiles", {})
        tile_state = tiles.setdefault(config.product, {})
        tile_state["last_step"] = step_index
        st.success("✅ Progress saved! You can return anytime.")
        st.stop()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_quick_estimate_footer_DEPRECATED(context: dict) -> None:
    """DEPRECATED - DO NOT USE. Quick estimate now uses custom rendering only.
    
    This function was part of the old approach where run_module() rendered
    quick_estimate with standard form fields. Now we use _render_quick_estimate_custom()
    which provides the purple GCP recommendation box and dynamic button behavior.
    
    Kept for reference only - should never be called.
    """
    st.error("❌ DEPRECATED FUNCTION CALLED: _render_quick_estimate_footer_DEPRECATED")
    st.write("This rendering path should not be used. Quick estimate must use custom rendering.")
    return  # Early exit - don't render anything
    # Get user's selection
    answers = context.get("answers", {})
    selected_care_type = answers.get("selected_care_type")
    
    if not selected_care_type:
        return  # No selection yet, nothing to show
    
    # Check if estimate has been shown
    state_key = context.get("config", {}).state_key if hasattr(context.get("config", {}), "state_key") else "cost.base"
    estimate_shown_key = f"{state_key}._estimate_shown"
    
    # Intercept button clicks to show estimate first
    # Check if the Continue button was clicked but estimate not shown yet
    next_clicked_key = f"{state_key}._next_clicked"
    if next_clicked_key in st.session_state and st.session_state[next_clicked_key]:
        if not st.session_state.get(estimate_shown_key, False):
            # First click - show estimate and update flag
            st.session_state[estimate_shown_key] = True
            # Clear the next click flag to prevent progression
            st.session_state[next_clicked_key] = False
            # Force rerun to update button label
            st.rerun()
    
    # Show cost breakdown if estimate has been shown OR user clicked "See My Estimate"
    if st.session_state.get(estimate_shown_key, False):
        st.divider()
        st.markdown("### Your Cost Estimate")
        
        try:
            estimate = calculate_cost_estimate(selected_care_type, zip_code=None)
            render_cost_breakdown(estimate, show_details=True)
            
            # Show what's included in national average
            st.info(
                "📍 **National Average:** This estimate uses national average costs. "
                "After you complete authentication, we'll apply regional pricing based on your ZIP code."
            )
        except Exception as e:
            st.error(f"Error calculating estimate: {e}")
        
        # Show comparison hint
        st.caption("� **Tip:** You can change the care type above to compare different options before continuing.")


def _render_auth_gate_custom(config, step, step_index: int) -> None:
    """Custom rendering for auth gate step.
    
    Shows authentication requirement and mock login buttons.
    Completely bypasses standard form rendering.
    """
    state_key = config.state_key
    
    # Simple header without complex HTML
    st.markdown(f"### {step.title}")
    if step.subtitle:
        st.markdown(step.subtitle)
    
    # Check if user is already authenticated
    if auth.is_authenticated():
        st.success("✅ You're signed in! Click Continue below to proceed.")
        
        # Continue button
        if st.button("Continue", key="_auth_continue", type="primary", use_container_width=True):
            st.session_state[f"{state_key}._step"] = 3  # Go to profile_flags
            st.rerun()
        return
    
    # Show authentication requirement
    st.warning("🔒 **Authentication Required**")
    st.markdown(
        """
        To access the Full Financial Assessment, please sign in or create a free account.
        
        **Why we require an account:**
        - Securely save your financial information
        - Access detailed benefit eligibility tools
        - Resume your assessment anytime from any device
        - Receive personalized recommendations
        """
    )
    
    # Mock login buttons for development
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Sign In (Dev)", use_container_width=True, type="primary"):
            st.session_state.setdefault("auth", {})["is_authenticated"] = True
            st.rerun()
    with col2:
        if st.button("📝 Create Account (Dev)", use_container_width=True):
            st.session_state.setdefault("auth", {})["is_authenticated"] = True
            st.rerun()
    
    st.caption("*In development: authentication is simulated for testing*")


def _render_profile_flags_custom(config, step, step_index: int):
    """Custom rendering for profile_flags step - just show the form fields."""
    st.markdown(f"### {step.title}")
    if step.subtitle:
        st.caption(step.subtitle)
    
    # Get state
    state_key = config.state_key
    state = st.session_state.get(state_key, {})
    profile = state.get("profile", {})
    
    st.markdown("**Please answer a few quick questions to customize your assessment:**")
    
    st.markdown("")
    
    # Veteran Status
    st.markdown("**Are you or your spouse a military veteran?**")
    is_veteran = st.radio(
        "veteran_label",
        options=[True, False],
        format_func=lambda x: "Yes" if x else "No",
        index=0 if profile.get("is_veteran", False) else 1,
        key=f"{state_key}_profile_veteran",
        label_visibility="collapsed"
    )
    
    st.markdown("")
    
    # Home Owner
    st.markdown("**Do you own your home?**")
    is_home_owner = st.radio(
        "home_label",
        options=[True, False],
        format_func=lambda x: "Yes" if x else "No",
        index=0 if profile.get("is_home_owner", False) else 1,
        key=f"{state_key}_profile_homeowner",
        label_visibility="collapsed"
    )
    
    st.markdown("")
    
    # Medicaid
    st.markdown("**Are you currently on Medicaid or interested in Medicaid planning?**")
    has_medicaid = st.radio(
        "medicaid_label",
        options=[True, False],
        format_func=lambda x: "Yes" if x else "No",
        index=0 if profile.get("has_medicaid", False) else 1,
        key=f"{state_key}_profile_medicaid",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Continue button - add unique key to avoid conflicts
    if st.button("Continue to Assessment Modules", key=f"{state_key}_profile_continue", type="primary", use_container_width=True):
        # Save to profile (ZIP code already saved from quick estimate)
        new_profile = {
            **profile,  # Keep existing profile data (including zip_code)
            "is_veteran": is_veteran,
            "is_home_owner": is_home_owner,
            "has_medicaid": has_medicaid
        }
        
        # Update state
        if state_key not in st.session_state:
            st.session_state[state_key] = {}
        st.session_state[state_key]["profile"] = new_profile
        
        # Debug logging
        st.sidebar.success(f"✅ Profile saved: {new_profile}")
        st.sidebar.info(f"🔄 Advancing from step {step_index} to {step_index + 1}")
        
        # Advance to next step
        st.session_state[f"{state_key}._step"] = step_index + 1
        st.rerun()


def _render_module_dashboard_custom(config, step, step_index: int):
    """Custom rendering for module_dashboard step - shows the 6 modules."""
    st.markdown(f"### {step.title}")
    if step.subtitle:
        st.caption(step.subtitle)
    
    # Get state
    state_key = config.state_key
    state = st.session_state.get(state_key, {})
    profile = state.get("profile", {})
    care_type = state.get("care_type")  # From quick estimate
    
    st.markdown("---")
    
    # Define all 6 modules with visibility rules
    modules = [
        {
            "id": "income",
            "title": "💰 Income",
            "description": "Social Security, pensions, and other income sources",
            "visible": True,  # Always visible
            "required": True
        },
        {
            "id": "assets",
            "title": "🏦 Assets",
            "description": "Savings, investments, and other financial assets",
            "visible": True,  # Always visible
            "required": True
        },
        {
            "id": "insurance",
            "title": "🏥 Insurance",
            "description": "Medicare, supplemental insurance, and long-term care policies",
            "visible": True,  # Always visible
            "required": True
        },
        {
            "id": "va_benefits",
            "title": "🎖️ VA Benefits",
            "description": "Veterans benefits and Aid & Attendance eligibility",
            "visible": profile.get("is_veteran", False),
            "required": False
        },
        {
            "id": "housing",
            "title": "🏡 Housing",
            "description": "Home equity and housing-related considerations",
            "visible": profile.get("is_home_owner", False) and care_type != "In-Home Care",
            "required": False
        },
        {
            "id": "medicaid",
            "title": "🏛️ Medicaid Planning",
            "description": "Medicaid eligibility and spend-down strategies",
            "visible": profile.get("has_medicaid", False),
            "required": False
        }
    ]
    
    # Filter to visible modules
    visible_modules = [m for m in modules if m["visible"]]
    
    st.markdown("### 📊 Financial Assessment Modules")
    st.caption(f"Complete {len([m for m in visible_modules if m['required']])} required modules to generate your personalized cost estimate.")
    
    # Render module tiles in 2 columns
    for i in range(0, len(visible_modules), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(visible_modules):
                module = visible_modules[i + j]
                with col:
                    # Module tile container
                    with st.container():
                        st.markdown(f"**{module['title']}**")
                        st.caption(module['description'])
                        
                        # Status badge (placeholder for now)
                        status = "Not Started"  # TODO: Get from state
                        if status == "Complete":
                            st.success("✓ Complete")
                        elif status == "In Progress":
                            st.info("⋯ In Progress")
                        else:
                            st.text("○ Not Started")
                        
                        # Action button
                        if st.button(
                            "Start Module" if status == "Not Started" else "Continue Module",
                            key=f"module_{module['id']}",
                            use_container_width=True,
                            type="secondary"
                        ):
                            st.info(f"🚧 Module '{module['title']}' coming soon!")
                    
                    st.markdown("")  # Spacing
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Hub", key="back_to_hub_modules", use_container_width=True):
            route_to("hub_concierge")
    with col2:
        if st.button("Continue to Expert Review →", key="continue_to_expert_review", use_container_width=True, type="primary"):
            # Navigate to Expert Review page
            st.query_params["cost_module"] = "expert_review"
            st.rerun()


def _render_auth_gate_content(context: dict) -> None:
    """Render authentication gate screen.
    
    Blocks progress until user is authenticated.
    Provides login/signup interface.
    """
    st.divider()
    
    # Check if user is already authenticated
    if auth.is_authenticated():
        st.success("✅ You're signed in! Click Continue to proceed.")
        return
    
    # Show authentication requirement
    st.warning("🔒 **Authentication Required**")
    st.markdown(
        """
        To access the Full Financial Assessment, please sign in or create a free account.
        
        **Why we require an account:**
        - Securely save your financial information
        - Access detailed benefit eligibility tools
        - Resume your assessment anytime from any device
        - Receive personalized recommendations
        """
    )
    
    # Mock login for development
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Sign In (Dev)", use_container_width=True, type="primary"):
            auth.mock_login()
            st.rerun()
    with col2:
        if st.button("📝 Create Account (Dev)", use_container_width=True):
            auth.mock_login()
            st.rerun()
    
    st.caption("*In development: authentication is simulated for testing*")


def _render_module_dashboard_content(context: dict) -> None:
    """Render the module dashboard with interactive tiles.
    
    Shows available calculation modules based on user's profile flags.
    Each module displays status and allows navigation.
    """
    st.divider()
    
    # Get profile flags from answers
    answers = context.get("answers", {})
    veteran_status = answers.get("veteran_status", False)
    home_owner = answers.get("home_owner", False)
    medicaid_status = answers.get("medicaid_status", False)
    zip_code = answers.get("zip_code")
    
    # Get GCP recommendation to determine Home Decision eligibility
    gcp_rec = get_gcp_recommendation()
    is_in_home_care = gcp_rec == "In-Home Care"
    
    # Show regional pricing context if zip provided
    if zip_code:
        from products.cost_planner.cost_estimate_v2 import resolve_regional_multiplier
        multiplier, match_type = resolve_regional_multiplier(zip_code)
        regional_pct = (multiplier - 1.0) * 100
        sign = "+" if regional_pct > 0 else ""
        
        st.info(
            f"📍 **Regional Pricing for ZIP {zip_code}:** {sign}{regional_pct:.0f}% adjustment ({match_type})\n\n"
            "All cost estimates in the modules below reflect regional pricing for your area."
        )
    
    st.markdown("### Your Financial Planning Modules")
    st.caption("Complete each module to build your comprehensive financial picture. Work in any order and return anytime.")
    
    # Define all available modules with metadata
    modules = [
        {
            "key": "housing",
            "title": "Housing & Home Equity",
            "description": "Evaluate your home equity, mortgage status, and housing options for funding care.",
            "icon": "🏡",
            "enabled": home_owner and not is_in_home_care,
            "condition": "Home ownership required • Not for In-Home Care" if not (home_owner and not is_in_home_care) else "Available",
            "status_key": "cost.housing._completed"
        },
        {
            "key": "income",
            "title": "Income Sources",
            "description": "Track income from Social Security, pensions, investments, and other sources.",
            "icon": "💰",
            "enabled": True,
            "condition": None,
            "status_key": "cost.income._completed"
        },
        {
            "key": "assets",
            "title": "Assets & Savings",
            "description": "Document savings accounts, investments, retirement funds, and other assets.",
            "icon": "💎",
            "enabled": True,
            "condition": None,
            "status_key": "cost.assets._completed"
        },
        {
            "key": "va_benefits",
            "title": "VA Benefits",
            "description": "Explore Aid & Attendance and other veteran benefits you may qualify for.",
            "icon": "🎖️",
            "enabled": veteran_status,
            "condition": "Veteran status required" if not veteran_status else "Available",
            "status_key": "cost.va_benefits._completed"
        },
        {
            "key": "insurance",
            "title": "Health Insurance & Benefits",
            "description": "Review long-term care insurance, Medicare, and other coverage options.",
            "icon": "🏥",
            "enabled": True,
            "condition": None,
            "status_key": "cost.insurance._completed"
        },
        {
            "key": "medicaid",
            "title": "Medicaid Navigator",
            "description": "Understand Medicaid eligibility, spend-down requirements, and application process.",
            "icon": "🏛️",
            "enabled": medicaid_status,
            "condition": "Medicaid enrollment required" if not medicaid_status else "Currently enrolled",
            "status_key": "cost.medicaid._completed"
        }
    ]
    
    # Render module tiles
    for module in modules:
        # Check module status
        is_completed = st.session_state.get(module["status_key"], False)
        is_in_progress = st.session_state.get(f"{module['status_key']}_started", False)
        
        # Determine status badge
        if is_completed:
            status_badge = "✅ Complete"
            status_color = "#10b981"
        elif is_in_progress:
            status_badge = "🔄 In Progress"
            status_color = "#f59e0b"
        else:
            status_badge = "○ Not Started"
            status_color = "#6b7280"
        
        # Build tile HTML
        enabled_class = "" if module["enabled"] else "disabled"
        
        # Show condition text with appropriate styling
        if module["condition"]:
            if module["enabled"]:
                condition_html = f"<div style='color: #10b981; font-size: 0.85em; margin-top: 4px;'>✓ {module['condition']}</div>"
            else:
                condition_html = f"<div style='color: #ef4444; font-size: 0.85em; margin-top: 4px;'>✗ {module['condition']}</div>"
        else:
            condition_html = ""
        
        tile_html = f"""
        <div style="
            border: 2px solid {'#e5e7eb' if module['enabled'] else '#f3f4f6'}; 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 16px;
            background: {'white' if module['enabled'] else '#f9fafb'};
            opacity: {'1' if module['enabled'] else '0.6'};
            transition: all 0.2s;
        ">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 2em;">{module['icon']}</span>
                    <div>
                        <h4 style="margin: 0; color: #111827;">{module['title']}</h4>
                        {condition_html}
                    </div>
                </div>
                <div style="
                    padding: 4px 12px; 
                    border-radius: 20px; 
                    background: {status_color}20;
                    color: {status_color};
                    font-size: 0.85em;
                    font-weight: 600;
                    white-space: nowrap;
                ">
                    {status_badge}
                </div>
            </div>
            <p style="margin: 0; color: #6b7280; font-size: 0.95em;">
                {module['description']}
            </p>
        </div>
        """
        
        st.markdown(tile_html, unsafe_allow_html=True)
        
        # Action button
        if module["enabled"]:
            button_label = "Continue" if is_in_progress else ("Review" if is_completed else "Start Module")
            if st.button(button_label, key=f"module_{module['key']}", use_container_width=True, type="primary" if not is_completed else "secondary"):
                # Navigate to module
                st.query_params["cost_module"] = module["key"]
                st.rerun()
        else:
            st.button("Not Available", key=f"module_{module['key']}_disabled", use_container_width=True, disabled=True)
        
        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    
    # Finish & Review section
    st.divider()
    st.markdown("### Ready to Review?")
    st.caption("Once you've completed the modules you need, review your complete financial picture.")
    
    # Count completed modules
    completed_count = sum(1 for m in modules if st.session_state.get(m["status_key"], False))
    total_enabled = sum(1 for m in modules if m["enabled"])
    
    st.progress(completed_count / total_enabled if total_enabled > 0 else 0)
    st.caption(f"{completed_count} of {total_enabled} modules completed")
    
    # Save progress to Cost Planner product state
    if "cost_planner" not in st.session_state:
        st.session_state["cost_planner"] = {}
    
    # Calculate overall progress (modules completed / total enabled)
    progress_pct = int((completed_count / total_enabled * 75) if total_enabled > 0 else 0)  # Max 75% from modules
    st.session_state["cost_planner"]["progress"] = progress_pct
    st.session_state["cost_planner"]["modules_completed"] = completed_count
    st.session_state["cost_planner"]["modules_total"] = total_enabled
    
    st.divider()
    
    # Navigation buttons at bottom
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 Return to Hub", key="return_to_hub_dashboard", use_container_width=True):
            route_to("hub_concierge")
    with col2:
        if st.button("💾 Save & Exit", key="save_exit_dashboard", use_container_width=True):
            st.success("✅ Progress saved!")
            route_to("hub_concierge")
    with col3:
        # Allow continuing to Expert Review regardless of completion
        if st.button("Continue to Expert Review →", key="continue_expert_review", type="primary", use_container_width=True):
            # Navigate to expert review within modular system
            st.query_params["cost_module"] = "expert_review"
            st.rerun()


def _render_expert_review() -> None:
    """Render Expert Review page - shows module completion and allows proceeding to timeline."""
    st.markdown("### 📋 Expert Review")
    st.caption("Review your completed modules and continue to your financial timeline.")
    
    st.divider()
    
    # Get all modules from session state
    modules = [
        {"key": "income", "title": "💰 Income"},
        {"key": "assets", "title": "🏦 Assets"},
        {"key": "insurance", "title": "🏥 Insurance"},
        {"key": "va_benefits", "title": "🎖️ VA Benefits"},
        {"key": "housing", "title": "🏡 Housing"},
        {"key": "medicaid", "title": "🏛️ Medicaid Planning"}
    ]
    
    # Count completion
    completed = []
    pending = []
    for module in modules:
        status_key = f"cost.{module['key']}._completed"
        if st.session_state.get(status_key, False):
            completed.append(module['title'])
        else:
            pending.append(module['title'])
    
    # Show stats
    st.success(f"### ✅ {len(completed)} modules completed")
    if pending:
        st.info(f"⏳ **{len(pending)} modules pending** (optional)")
    
    # Show completed modules
    if completed:
        st.markdown("#### ✅ Completed Modules")
        for title in completed:
            st.markdown(f"- {title}")
    
    # Show pending modules (non-required)
    if pending:
        st.markdown("#### ⏳ Pending Modules (Optional)")
        st.caption("You can continue without completing these, or go back to finish them.")
        for title in pending:
            st.markdown(f"- {title}")
    
    st.divider()
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 Return to Hub", key="return_hub_review", use_container_width=True):
            route_to("hub_concierge")
    with col2:
        if st.button("← Back to Modules", key="back_modules_review", use_container_width=True):
            st.query_params["cost_module"] = "base"
            st.rerun()
    with col3:
        if st.button("Continue to Financial Timeline →", key="continue_timeline_review", type="primary", use_container_width=True):
            # Mark Cost Planner as 100% complete
            if "cost_planner" not in st.session_state:
                st.session_state["cost_planner"] = {}
            st.session_state["cost_planner"]["progress"] = 100
            st.query_params["cost_module"] = "financial_timeline"
            st.rerun()


def _render_financial_timeline() -> None:
    """Render Financial Timeline - shows runway analysis and PFMA entry point."""
    st.markdown("### 💰 Financial Timeline")
    st.caption("Based on your care plan and financial resources, how long will your assets last?")
    
    st.divider()
    
    # Get data from session state
    state = st.session_state.get("cost_planner_base", {})
    
    # Get GCP recommendation for care type
    gcp_rec = get_gcp_recommendation()
    care_type_display = gcp_rec or "In-Home Care"
    
    # Calculate estimates (placeholder - would need real data from modules)
    monthly_income = st.session_state.get("cost.income.total_monthly", 3000)
    monthly_expenses = st.session_state.get("cost.expenses.total_monthly", 2500)
    monthly_care_cost = 4000  # From care recommendation
    total_assets = st.session_state.get("cost.assets.total", 150000)
    va_benefits = st.session_state.get("cost.va_benefits.monthly", 0)
    
    # Calculate monthly net
    total_monthly_income = monthly_income + va_benefits
    total_monthly_expenses = monthly_expenses + monthly_care_cost
    monthly_net = total_monthly_income - total_monthly_expenses
    
    # Calculate runway
    if monthly_net >= 0:
        runway_text = "indefinitely"
        runway_color = "green"
    else:
        monthly_burn = abs(monthly_net)
        if monthly_burn > 0 and total_assets > 0:
            runway_months = int(total_assets / monthly_burn)
            runway_years = round(runway_months / 12, 1)
            # Format text
            if runway_years >= 1:
                years_int = int(runway_years)
                months_remainder = int((runway_years - years_int) * 12)
                if months_remainder > 0:
                    runway_text = f"{years_int} year{'s' if years_int != 1 else ''} and {months_remainder} month{'s' if months_remainder != 1 else ''}"
                else:
                    runway_text = f"{years_int} year{'s' if years_int != 1 else ''}"
            else:
                runway_text = f"{runway_months} month{'s' if runway_months != 1 else ''}"
            
            # Determine color
            if runway_years >= 10:
                runway_color = "green"
            elif runway_years >= 5:
                runway_color = "blue"
            elif runway_years >= 2:
                runway_color = "orange"
            else:
                runway_color = "red"
        else:
            runway_text = "an uncertain duration"
            runway_color = "gray"
    
    # Main runway statement
    if runway_color == "green":
        st.success(f"""
        ### ✅ Strong Financial Position
        
        **Based on your care plan and financial resources, you can pay for your care plan for {runway_text}.**
        """)
    elif runway_color == "blue":
        st.info(f"""
        ### 🟡 Moderate Financial Runway
        
        **Based on your care plan and financial resources, you can pay for your care plan for {runway_text}.**
        """)
    elif runway_color == "orange":
        st.warning(f"""
        ### 🟠 Limited Financial Runway
        
        **Based on your care plan and financial resources, you can pay for your care plan for {runway_text}.**
        """)
    elif runway_color == "red":
        st.error(f"""
        ### 🔴 Urgent Planning Needed
        
        **Based on your care plan and financial resources, you can pay for your care plan for {runway_text}.**
        """)
    else:
        st.info(f"""
        ### 📊 Financial Assessment
        
        **Based on your care plan and financial resources, you can pay for your care plan for {runway_text}.**
        """)
    
    st.divider()
    
    # Financial overview
    st.markdown("### 📊 Monthly Financial Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Monthly Income", f"${total_monthly_income:,.0f}")
        if monthly_income > 0:
            st.caption(f"Base Income: ${monthly_income:,.0f}")
        if va_benefits > 0:
            st.caption(f"VA Benefits: ${va_benefits:,.0f}")
    with col2:
        st.metric("Monthly Expenses", f"${total_monthly_expenses:,.0f}")
        st.caption(f"Living Expenses: ${monthly_expenses:,.0f}")
        st.caption(f"Care Costs: ${monthly_care_cost:,.0f}")
    
    # Monthly gap
    st.divider()
    if monthly_net >= 0:
        st.success(f"### Monthly Surplus: ${monthly_net:,.0f}")
    else:
        st.warning(f"### Monthly Shortfall: ${abs(monthly_net):,.0f}")
    
    # Assets
    st.metric("Total Assets", f"${total_assets:,.0f}")
    
    st.divider()
    
    # Next steps
    st.markdown("### 🎯 Next Steps")
    st.markdown("""
    You've completed your financial assessment! Here's what you can do now:
    
    1. **Talk to an Advisor** — Schedule a personalized session to refine your care plan
    2. **Explore Funding Options** — Learn about Medicaid, VA benefits, and other programs
    3. **Return to Hub** — Access all your care planning tools and resources
    """)
    
    st.divider()
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 Return to Hub", key="return_hub_timeline", use_container_width=True):
            route_to("hub_concierge")
    with col2:
        if st.button("← Back to Expert Review", key="back_review_timeline", use_container_width=True):
            st.query_params["cost_module"] = "expert_review"
            st.rerun()
    with col3:
        if st.button("🦆 Talk to an Advisor →", key="pfma_timeline", type="primary", use_container_width=True):
            route_to("pfma")


def _render_sub_module(module_key: str) -> None:
    """Render a specific calculation sub-module.
    
    Args:
        module_key: Module identifier (e.g., "housing", "income", "assets", "va_benefits")
    """
    # Add "Back to Module Index" button at top
    if st.button("← Back to Module Index", key="_back_to_index"):
        st.query_params.clear()
        st.query_params["page"] = "cost"
        st.rerun()
    
    st.divider()
    
    # Check authentication before rendering protected modules
    if not auth.requires_auth(module_key):
        return  # Auth gate blocked rendering
    
    # Import module configuration dynamically
    try:
        module_path = f"products.cost_planner.modules.{module_key}.module_config"
        config_module = importlib.import_module(module_path)
        config = config_module.get_config()
    except ImportError as e:
        st.warning(f"⚠️ Module '{module_key}' is not yet implemented")
        st.caption(f"Looking for: `{module_path}`")
        st.info(
            f"""
            **Coming in Phase 2**
            
            The **{module_key.replace('_', ' ').title()}** module is planned but not yet built.
            
            Return to the Module Index to explore other available modules.
            """
        )
        return
    except Exception as e:
        st.error(f"❌ Error loading module '{module_key}'")
        st.exception(e)
        return
    
    # Run the module using the standard engine
    module_state = run_module(config)
    
    # Mark module as started
    st.session_state[f"{config.state_key}._completed_started"] = True
    
    # Check if module is complete and update status
    # (Modules mark themselves complete in their outcomes)


def register() -> dict:
    """Register Cost Planner product with the application.
    
    Returns:
        Dict with routes and tile configuration
    """
    return {
        "routes": {
            "cost": render,
        },
        "tile": {
            "key": "cost_planner",
            "title": "Cost Planner",
            "meta": ["≈15 min", "Requires login"],
            "progress_key": "cost.progress",
            "unlock_condition": lambda _ss: True,  # Always available
        },
    }

