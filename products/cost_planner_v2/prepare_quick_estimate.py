"""
Cost Planner v2 - Prepare for Quick Estimate Gate

Lightweight personalization gate that collects essential context before showing
the Quick Estimate comparison view. Asks location and home carry questions based
on the GCP recommendation, then passes data to comparison_view.

Architecture:
- Part of Step 1 (Intro) - precedes Quick Estimate
- Stores all data in session state (no MCIP writes yet)
- Returns True when ready to show Quick Estimate
"""

from typing import Any

import streamlit as st

from core.mcip import MCIP
from products.cost_planner_v2 import comparison_calcs
from products.cost_planner_v2.utils.regional_data import RegionalDataProvider

# ==============================================================================
# SESSION STATE KEYS
# ==============================================================================

SESSION_KEYS = {
    "zip": "prepare_qe_zip",
    "region_label": "prepare_qe_region_label",
    "regional_multiplier": "prepare_qe_regional_multiplier",
    "care_recommendation": "prepare_qe_care_recommendation",
    "keep_home": "prepare_qe_keep_home",
    "home_carry_base": "prepare_qe_home_carry_base",
    "show_comparison": "prepare_qe_show_comparison",
    "home_carry_source": "prepare_qe_home_carry_source",
    "is_complete": "prepare_qe_is_complete",
}


# ==============================================================================
# GCP CONTEXT HELPERS
# ==============================================================================

def _get_spouse_or_partner_present() -> bool:
    """Extract spouse/partner flag from GCP recommendation.
    
    Returns:
        True if living with spouse/partner, False otherwise
    """
    # Try to get from MCIP (primary source)
    gcp_rec = MCIP.get_care_recommendation()
    if gcp_rec and hasattr(gcp_rec, 'spouse_or_partner_present'):
        return gcp_rec.spouse_or_partner_present

    # Fallback: check session state directly (in case MCIP not yet initialized)
    gcp_data = st.session_state.get("gcp_care_recommendation", {})
    return gcp_data.get("spouse_or_partner_present", False)


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def render_prepare_gate(recommendation_context: Any | None = None) -> bool:
    """Render the preparation gate and return completion status.
    
    Args:
        recommendation_context: GCP recommendation object (optional)
        
    Returns:
        True if all required fields are complete and user clicked CTA
    """

    # Initialize session state
    _init_session_state(recommendation_context)

    # DEV LOGGING: Verify three-layer storage of spouse flag
    if st.session_state.get("debug_mode", False):
        st.markdown("---")
        st.markdown("### 🔍 Spouse/Partner Flag Verification")

        # Layer 1: Session State
        session_value = st.session_state.get("spouse_or_partner_present", None)

        # Layer 2: MCIP Global Context
        gcp_rec = MCIP.get_care_recommendation()
        mcip_value = getattr(gcp_rec, 'spouse_or_partner_present', None) if gcp_rec else None

        # Layer 3: Will be persisted (preview what will be saved)
        from core.session_store import extract_user_state
        user_data_preview = extract_user_state(st.session_state)
        persisted_value = user_data_preview.get("spouse_or_partner_present", None)

        st.json({
            "layer_1_session_state": session_value,
            "layer_2_mcip_context": mcip_value,
            "layer_3_will_persist": persisted_value,
            "all_layers_match": (session_value == mcip_value == persisted_value),
        })
        st.markdown("---")

    # Get current recommendation
    rec_tier = st.session_state.get(SESSION_KEYS["care_recommendation"])

    # Render gate UI
    st.markdown("### Let's personalize your estimate")
    st.markdown(
        """<div style="color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.95rem;">
        Answer a few quick questions so we can show you the most relevant costs.
        </div>""",
        unsafe_allow_html=True
    )

    # Question 1: ZIP code (everyone)
    _render_zip_question()

    # Question 2 & 3: Home carry and comparison (based on recommendation)
    if rec_tier:
        if rec_tier == "in_home_care":
            _render_inhome_questions()
        else:
            _render_facility_questions()


# ==============================================================================
# QUESTION RENDERERS
# ==============================================================================

def _render_zip_question():
    """Render ZIP code input for everyone."""

    st.markdown("#### Where will this care be provided?")
    st.caption("💡 Costs vary by region, so we use ZIP to localize rates.")
    
    # Initialize cost.inputs if missing
    if "cost.inputs" not in st.session_state:
        st.session_state["cost.inputs"] = {}
    
    # Get ZIP from cost.inputs (single source of truth)
    current_zip = st.session_state["cost.inputs"].get("zip", "")

    zip_code = st.text_input(
        "ZIP Code",
        max_chars=5,
        placeholder="90210",
        value=current_zip,
        key="prepare_qe_zip_input",
        label_visibility="collapsed"
    )

    # Update session state and resolve region
    if zip_code and len(zip_code) == 5:
        # Check if ZIP changed
        previous_zip = st.session_state["cost.inputs"].get("zip")
        zip_changed = (previous_zip != zip_code)
        
        # Atomic write to cost.inputs (single source of truth)
        st.session_state["cost.inputs"]["zip"] = zip_code
        st.session_state[SESSION_KEYS["zip"]] = zip_code  # Mirror to prepare gate key
        _resolve_region(zip_code)
        
        # Log ZIP persistence
        print(f"[ZIP_STATE] set zip={zip_code} persisted=True")

        # If ZIP changed and user hasn't manually edited home carry, update it with new ZIP lookup
        if zip_changed:
            home_carry_source = st.session_state.get(SESSION_KEYS["home_carry_source"])
            if home_carry_source != "user":  # Only update if not manually edited
                new_default = _get_default_home_carry(zip_code)
                # Update both widget keys (one will be active depending on care type)
                st.session_state["prepare_qe_home_carry_inhome"] = int(new_default)
                st.session_state["prepare_qe_home_carry_facility"] = int(new_default)
                st.session_state[SESSION_KEYS["home_carry_base"]] = float(new_default)
                st.session_state[SESSION_KEYS["home_carry_source"]] = "default"
                print(f"[ZIP_UPDATE] ZIP changed to {zip_code}, updated home_carry to ${new_default:,.0f}")

        # Show resolved region
        region_label = st.session_state.get(SESSION_KEYS["region_label"])
        if region_label:
            st.success(f"📍 Region: **{region_label}**")
    elif zip_code:
        st.session_state["cost.inputs"]["zip"] = None
        st.session_state[SESSION_KEYS["zip"]] = None
        st.warning("⚠️ Please enter a valid 5-digit ZIP code")

    st.markdown("")


def _render_inhome_questions():
    """Render questions for in-home care recommendation (staying at home)."""

    # RULE 1: For in-home, keep_home is locked to True (home costs are inherent)
    st.session_state[SESSION_KEYS["keep_home"]] = True

    # [CP_DEBUG] Log context on mount
    if st.session_state.get("debug_mode", False):
        import sys
        rec_tier = st.session_state.get(SESSION_KEYS["care_recommendation"], "in_home_care")
        has_partner = st.session_state.get("spouse_or_partner_present", False)
        print(
            f"[CP_DEBUG] CP Intro Mount: category={rec_tier}, has_partner={has_partner}, "
            f"keep_home=True, locked=True",
            file=sys.stderr
        )

    # Show explanatory note (no toggle control)
    st.info("🏠 **Home costs are included while care is provided at home.**")
    st.markdown("")

    # Home Carry Cost (always included for in-home)
    st.markdown("#### What are your monthly household costs?")
    st.caption(
        "💡 Typical monthly cost to keep the household running "
        "(mortgage/rent, utilities, insurance, groceries)."
    )

    # Get default with regional scaling if ZIP entered
    zip_code = st.session_state.get(SESSION_KEYS["zip"])
    default_home_carry = _get_default_home_carry(zip_code)

    home_carry = st.number_input(
        "Monthly Home Carry Cost",
        min_value=0,
        max_value=50000,
        value=int(default_home_carry),
        step=100,
        key="prepare_qe_home_carry_inhome",
        label_visibility="collapsed"
    )

    # Track if user edited the value
    if home_carry != default_home_carry:
        st.session_state[SESSION_KEYS["home_carry_source"]] = "user"
    else:
        st.session_state[SESSION_KEYS["home_carry_source"]] = "default"

    st.session_state[SESSION_KEYS["home_carry_base"]] = float(home_carry)

    st.markdown("")

    # Optional: Show Assisted Living comparison
    st.markdown("#### Would you also like to see an Assisted Living comparison side-by-side?")
    show_comparison = st.checkbox(
        "Show Assisted Living comparison",
        value=st.session_state.get(SESSION_KEYS["show_comparison"], False),
        key="prepare_qe_show_al_comparison"
    )
    st.session_state[SESSION_KEYS["show_comparison"]] = show_comparison

    st.markdown("")


def _render_facility_questions():
    """Render questions for facility care recommendation (AL/MC/MC-HA)."""

    # Get context from GCP
    spouse_or_partner_present = st.session_state.get("spouse_or_partner_present", False)
    rec_tier = st.session_state.get(SESSION_KEYS["care_recommendation"], "assisted_living")
    compare_inhome = st.session_state.get("cost.compare_inhome", False)

    # [CP_DEBUG] Log context on mount
    if st.session_state.get("debug_mode", False):
        import sys
        print(f"[CP_DEBUG] CP Intro Mount: category={rec_tier}, has_partner={spouse_or_partner_present}, compare_inhome={compare_inhome}", file=sys.stderr)

    # RULE 2 & 3: Default keep_home based on has_partner, but editable
    # Check if user has already set a value (don't override on revisit)
    if SESSION_KEYS["keep_home"] not in st.session_state:
        # First visit: set default based on has_partner
        default_keep_home = spouse_or_partner_present
        st.session_state[SESSION_KEYS["keep_home"]] = default_keep_home

    # Keep Home question with context-aware copy
    if spouse_or_partner_present:
        # RULE 2: With partner, default Yes, partner-specific copy
        st.markdown("#### A spouse or partner may remain at home. Include home expenses in the plan?")
        st.caption(
            "💡 When one person moves to a care facility but a spouse/partner stays home, "
            "the household expenses continue. We've defaulted this to **Yes**."
        )
    else:
        # RULE 3: No partner, default No, softer copy
        st.markdown("#### Will the home continue to be maintained after the move?")
        st.caption(
            "💡 If the home will be sold or no longer maintained, select **No**. "
            "Only include home expenses if someone continues living there."
        )

    keep_home_options = ["No", "Yes"]
    current_keep_home = st.session_state.get(SESSION_KEYS["keep_home"], spouse_or_partner_present)
    keep_home_choice = st.radio(
        "Keep Household",
        options=keep_home_options,
        index=1 if current_keep_home else 0,
        horizontal=True,
        key="prepare_qe_keep_home_radio",
        label_visibility="collapsed"
    )

    keep_home = (keep_home_choice == "Yes")
    st.session_state[SESSION_KEYS["keep_home"]] = keep_home

    # [CP_DEBUG] Log applied values
    if st.session_state.get("debug_mode", False):
        import sys
        locked = False  # Facility questions are always editable
        print(
            f"[CP_DEBUG] CP Intro Applied: keep_home={keep_home}, "
            f"locked={locked}, default_was={spouse_or_partner_present}",
            file=sys.stderr
        )

    st.markdown("")

    # Home Carry input (only if keep_home=Yes)
    if keep_home:
        st.markdown("##### Monthly Home Carry Cost")
        st.caption(
            "💡 Typical monthly cost to keep the household running. "
            "Adjust if needed."
        )

        # Get default with regional scaling if ZIP entered
        zip_code = st.session_state.get(SESSION_KEYS["zip"])
        default_home_carry = _get_default_home_carry(zip_code)

        home_carry = st.number_input(
            "Home Carry Cost",
            min_value=0,
            max_value=50000,
            value=int(default_home_carry),
            step=100,
            key="prepare_qe_home_carry_facility",
            label_visibility="collapsed"
        )

        # Track if user edited the value
        if home_carry != default_home_carry:
            st.session_state[SESSION_KEYS["home_carry_source"]] = "user"
        else:
            st.session_state[SESSION_KEYS["home_carry_source"]] = "default"

        st.session_state[SESSION_KEYS["home_carry_base"]] = float(home_carry)
        st.markdown("")
    else:
        # Clear home carry if not keeping home
        st.session_state[SESSION_KEYS["home_carry_base"]] = None
        st.session_state[SESSION_KEYS["home_carry_source"]] = None

    # ====================================================================
    # CONSOLIDATED CTAs (DYNAMIC LABELS)
    # ====================================================================
    st.markdown("")
    st.markdown("---")
    
    # Get tier display name
    tier_display_map = {
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care",
        "in_home": "In-Home Care",
        "in_home_care": "In-Home Care",
        "in_home_plus": "In-Home Care"
    }
    tier_display = tier_display_map.get(rec_tier, rec_tier.replace("_", " ").title())
    
    # Dynamic compare label based on tier
    if rec_tier in ["assisted_living", "memory_care", "memory_care_high_acuity"]:
        compare_label = f"⚖️ Compare {tier_display} vs In-Home Care"
    else:
        compare_label = "⚖️ Compare In-Home vs Community Options"
    
    continue_label = f"→ Continue with {tier_display}"
    
    # Get ZIP status for validation
    zip_code = st.session_state.get("cost.inputs", {}).get("zip") or st.session_state.get(SESSION_KEYS["zip"])
    has_zip = bool(zip_code and len(str(zip_code)) == 5)
    
    # Primary CTA: Compare (always enabled - doesn't need ZIP to toggle view)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(compare_label, key="compare_cta", use_container_width=True, type="primary"):
            # Set view mode to compare (single source of truth)
            st.session_state["cost.view_mode"] = "compare"
            # Clear single-path tier to ensure comparison renders
            if "cost.single_path_tier" in st.session_state:
                del st.session_state["cost.single_path_tier"]
            # Sync ZIP and other data (even if ZIP missing, sync what we have)
            _sync_to_comparison_view()
            # Log action
            print(f"[COST_CTA] action=compare tier={rec_tier} zip_present={has_zip} view_mode=compare")
            st.rerun()
    
    with col2:
        # Secondary CTA: Continue with recommended tier (requires ZIP)
        continue_disabled = not has_zip
        if st.button(continue_label, key="continue_cta", use_container_width=True, disabled=continue_disabled):
            if has_zip:
                # Set view mode to single (single source of truth)
                st.session_state["cost.view_mode"] = "single"
                st.session_state[SESSION_KEYS["is_complete"]] = True
                st.session_state["cost.single_path_tier"] = rec_tier  # Explicit tier for single view
                _sync_to_comparison_view()
                
                # Enhanced logging with all flags being set
                print(f"[COST_CTA] action=continue tier={rec_tier} zip_present=True "
                      f"set_view_mode=single set_single_path_tier={rec_tier} "
                      f"set_is_complete=True proceeded=True")
                st.rerun()
            else:
                # Log blocked action
                print(f"[COST_CTA] action=continue tier={rec_tier} zip_present=False proceeded=False")
    
    # Show ZIP warning if Continue button is disabled
    if not has_zip:
        st.caption("💡 ZIP code is required to show your estimate.")
    
    st.markdown("")
    
    # Return completion status
    return st.session_state.get(SESSION_KEYS["is_complete"], False)


# ==============================================================================
# HELPERS
# ==============================================================================

def _init_session_state(recommendation_context: Any | None):
    """Initialize session state with defaults."""

    # Get GCP recommendation if available
    if recommendation_context is None:
        gcp_rec = MCIP.get_care_recommendation()
        if gcp_rec and hasattr(gcp_rec, 'tier'):
            recommendation_context = gcp_rec.tier
        else:
            recommendation_context = "assisted_living"  # Default fallback

    # Initialize all keys if not present
    if SESSION_KEYS["care_recommendation"] not in st.session_state:
        st.session_state[SESSION_KEYS["care_recommendation"]] = recommendation_context

    if SESSION_KEYS["is_complete"] not in st.session_state:
        st.session_state[SESSION_KEYS["is_complete"]] = False

    # NOTE: show_comparison is deprecated in favor of cost.view_mode
    # Keep for backward compatibility but don't reset if already set
    if SESSION_KEYS["show_comparison"] not in st.session_state:
        # Default: False (single-path) - let user choose via CTAs
        st.session_state[SESSION_KEYS["show_comparison"]] = False

    # LAYER 1: Session state - Store spouse/partner flag
    if "spouse_or_partner_present" not in st.session_state:
        spouse_flag = _get_spouse_or_partner_present()
        st.session_state["spouse_or_partner_present"] = spouse_flag

        # LAYER 2: User data persistence - will auto-save via USER_PERSIST_KEYS
        # (No additional code needed - session_store.py handles it)

        # LAYER 3: MCIP global context - already published via CareRecommendation
        # (No additional code needed - MCIP.publish_care_recommendation handles it)


def _resolve_region(zip_code: str):
    """Resolve region label and multiplier from ZIP code."""

    regional = RegionalDataProvider.get_multiplier(zip_code=zip_code)

    st.session_state[SESSION_KEYS["region_label"]] = regional.region_name
    st.session_state[SESSION_KEYS["regional_multiplier"]] = regional.multiplier


def _get_default_home_carry(zip_code: str | None) -> float:
    """Get default home carry cost with ZIP-based CSV lookup.
    
    Priority:
    1. ZIP-based CSV lookup (exact match or ZIP3 bucket)
    2. Fallback to regional scaling if CSV lookup fails
    3. National baseline if no ZIP provided
    """
    from products.cost_planner_v2.utils.home_costs import lookup_zip

    if not zip_code:
        return comparison_calcs.HOME_CARRY_BASE

    # Try CSV lookup first
    lookup_result = lookup_zip(zip_code, kind="owner")
    if lookup_result:
        amount = lookup_result["amount"]
        src = lookup_result["source"]
        conf = int(lookup_result["confidence"] * 100)
        
        # Log once per session
        if not st.session_state.get("_home_cost_logged"):
            print(f"[HOME_CARRY_DEFAULT] zip={zip_code} amount=${amount:,.0f} source={src} conf={conf}%")
            st.session_state["_home_cost_logged"] = True
        
        return amount

    # Fallback to old regional scaling
    print(f"[HOME_CARRY_DEFAULT] zip={zip_code} CSV lookup failed, using regional scaling fallback")
    return comparison_calcs.get_home_carry_effective(zip_code, user_override=None)


def _validate_inputs() -> bool:
    """Validate all required inputs are complete.
    
    Returns:
        True if valid, False otherwise
    """

    # ZIP is always required
    zip_code = st.session_state.get(SESSION_KEYS["zip"])
    if not zip_code or len(zip_code) != 5:
        return False

    # For facility with keep_home=True, need home_carry_base
    keep_home = st.session_state.get(SESSION_KEYS["keep_home"])
    rec_tier = st.session_state.get(SESSION_KEYS["care_recommendation"])

    if rec_tier != "in_home_care" and keep_home:
        home_carry = st.session_state.get(SESSION_KEYS["home_carry_base"])
        if home_carry is None:
            return False

    # For in-home, home_carry_base is always required
    if rec_tier == "in_home_care":
        home_carry = st.session_state.get(SESSION_KEYS["home_carry_base"])
        if home_carry is None:
            return False

    return True


def _sync_to_comparison_view():
    """Sync prepare gate data to comparison_view session keys.
    
    This bridges the prepare gate to the comparison view component.
    """

    # ZIP code (use cost.inputs as source of truth, fallback to prepare gate key)
    zip_code = st.session_state.get("cost.inputs", {}).get("zip") or st.session_state.get(SESSION_KEYS["zip"])
    if zip_code:
        st.session_state["cost_v2_quick_zip"] = zip_code

    # Home carry cost
    home_carry = st.session_state.get(SESSION_KEYS["home_carry_base"])
    if home_carry is not None:
        st.session_state["comparison_home_carry_cost"] = home_carry

    # Keep home flag
    keep_home = st.session_state.get(SESSION_KEYS["keep_home"])
    if keep_home is not None:
        st.session_state["comparison_keep_home"] = keep_home

    # Show comparison flag
    # Note: comparison_view doesn't currently read this, but we store it for future use
    st.session_state["comparison_show_both"] = st.session_state.get(
        SESSION_KEYS["show_comparison"], True
    )


# ==============================================================================
# RESET UTILITY
# ==============================================================================

def reset_prepare_gate():
    """Clear all prepare gate session state.
    
    Use this when user navigates away or starts over.
    """

    for key in SESSION_KEYS.values():
        if key in st.session_state:
            del st.session_state[key]
