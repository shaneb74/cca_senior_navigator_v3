"""
Cost Planner v2 - Intro Page (Mini-Form)

Clean entry point with minimal form:
- ZIP code input (automatic update with debounce)
- Monthly home carry input
- One CTA to Quick Estimate

No tabs, no cards, no maintain-home question here.
"""

import time

import streamlit as st

from core.navi import render_navi_panel
from products.cost_planner_v2.ui_helpers import go_to_quick_estimate
from products.cost_planner_v2.utils.home_costs import lookup_zip
from products.cost_planner_v2.utils.regional_data import RegionalDataProvider


def render():
    """Render intro page with clean mini-form."""

    print("[PAGE_MOUNT] cost_intro")

    # Mark CP intro scope for header helper
    st.session_state["cp_intro"] = True

    # Initialize cost namespace FIRST (before any rendering)
    cost = st.session_state.setdefault("cost", {})
    inputs = cost.setdefault("inputs", {})
    meta = cost.setdefault("meta", {})  # Container for submission guards and flags

    # Legacy safety: prevent downstream key errors
    inputs.setdefault("maintain_home", True)  # UI toggle lives in facility cards later

    print(f"[INTRO] Render start: zip={inputs.get('zip')} home_carry={inputs.get('home_carry')}")

    # HOUSEHOLD FLOW: Load household and CarePlans (single-writer pattern)
    try:
        from core.household import ensure_household_state, get_careplan_for

        # Only prefill if cost.inputs not already initialized
        if not inputs:  # Check if inputs dict is empty
            hh = ensure_household_state(st)

            # Get person IDs
            primary_id = st.session_state.get("person.primary_id")
            partner_id = st.session_state.get("person.partner_id")

            # Load CarePlans
            cp_primary = get_careplan_for(st, primary_id) if primary_id else None
            cp_partner = get_careplan_for(st, partner_id) if partner_id else None

            # Prefill cost inputs from household data (single write on first entry)
            inputs["zip"] = hh.zip
            inputs["keep_home"] = hh.keep_home_default if hh.keep_home_default is not None else False
            inputs["owner_tenant"] = hh.home_owner_type or "unknown"

            # Use hours from primary CarePlan if available
            if cp_primary:
                inputs["hours"] = cp_primary.hours_user or cp_primary.hours_suggested

            print(f"[COST_PLANNER] Prefilled: zip={hh.zip} has_partner={hh.has_partner}")

        # Log ZIP state on load
        current_zip = inputs.get("zip")
        if current_zip:
            print(f"[ZIP_STATE] loaded zip={current_zip} from cost.inputs")

    except Exception as e:
        print(f"[COST_PLANNER] Household load error: {e}")
        # Fallback already handled by setdefault above

    # Open centered container
    st.markdown("<div class='sn-container'>", unsafe_allow_html=True)

    # Render Navi (pinned, unconditional - always at top)
    render_navi_panel(location="product", product_key="cost_planner")

    # Render mini-form
    st.markdown("### Let's personalize your estimate")
    st.markdown(
        """<div style="color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.95rem;">
        Answer two quick questions so we can show you the most relevant costs.
        </div>""",
        unsafe_allow_html=True
    )

    # Question 1: ZIP code (automatic update with debounce)
    st.markdown("#### Where will this care be provided?")
    st.caption("💡 Costs vary by region, so we use ZIP to localize rates.")

    # Direct ZIP input (no form)
    zip_value = st.text_input(
        "ZIP Code",
        value=inputs.get("zip", "") or "",
        placeholder="Enter ZIP",
        max_chars=5,
        key="intro_zip_input",
        label_visibility="collapsed"
    )

    # Debounce: update only if value changed & enough time passed
    typed_zip = (zip_value or "").strip()
    now = time.time()
    last_update = meta.get("zip_last_update", 0)

    if typed_zip and len(typed_zip) == 5 and typed_zip != inputs.get("zip") and (now - last_update) > 1.0:
        inputs["zip"] = typed_zip
        st.session_state["cost_v2_quick_zip"] = typed_zip
        meta["zip_last_update"] = now

        # Only estimate home carry if user hasn't manually set it
        if not inputs.get("home_carry_user_set", False):
            est = lookup_zip(typed_zip, kind="owner")
            if est and est.get("amount") is not None:
                inputs["home_carry"] = float(est["amount"])

        print(f"[INTRO_ZIP] auto-update zip={typed_zip} home_carry={inputs.get('home_carry')}")

        # Blur focus so it doesn't trap
        st.markdown(
            "<script>window.parent.document.activeElement?.blur();</script>",
            unsafe_allow_html=True
        )
        st.rerun()

    # Display current ZIP and region (if valid)
    if inputs.get("zip") and len(str(inputs.get("zip"))) == 5:
        # Resolve region
        regional = RegionalDataProvider.get_multiplier(zip_code=inputs.get("zip"))
        region_label = regional.region_name

        # Show inline region (no green banner)
        st.markdown(
            f'📍 <span class="region-label"><b>Region:</b> {region_label}</span>',
            unsafe_allow_html=True
        )

        print(f"[ZIP_STATE] displaying zip={inputs.get('zip')} region={region_label}")

    # Preference-aware hint (small polish)
    gcp_data = st.session_state.get("gcp", {})
    move_pref = gcp_data.get("move_preference")
    if move_pref == "stay_home":
        st.markdown(
            '<div class="cp-hint">We\'ll include your monthly home costs since you plan to stay home.</div>',
            unsafe_allow_html=True
        )
    elif move_pref in ("open", "uncertain"):
        st.markdown(
            '<div class="cp-hint">You can compare staying home or moving; ZIP will localize costs.</div>',
            unsafe_allow_html=True
        )

    st.markdown("")

    # Question 2: Monthly Home Carry
    st.markdown("#### What are your monthly household costs?")
    st.caption(
        "💡 Typical monthly cost to keep the household running "
        "(mortgage/rent, utilities, insurance, groceries)."
    )

    # Read-before-write: Only initialize if missing, never overwrite on rerun
    if inputs.get("home_carry") is None:
        stored_zip = inputs.get("zip")
        if stored_zip and len(str(stored_zip)) == 5:
            est = lookup_zip(stored_zip, kind="owner")
            if est and est.get("amount") is not None:
                inputs["home_carry"] = float(est["amount"])
                print(f"[INTRO_HOME_CARRY] Initialized from ZIP: {inputs['home_carry']}")
            else:
                inputs["home_carry"] = 0.0
        else:
            inputs["home_carry"] = 0.0

    # Get current value from session state
    home_carry_value = float(inputs.get("home_carry") or 0.0)

    # Salt widget key with ZIP so it mounts fresh when ZIP changes
    # This prevents client-side stale value from overwriting server value
    carry_key = f"intro_home_carry__{inputs.get('zip', '')}"

    # Render number input using session value (no magic defaults)
    new_home_carry = st.number_input(
        "Monthly Home Carry Cost",
        value=home_carry_value,
        min_value=0.0,
        max_value=50000.0,
        step=50.0,
        format="%.0f",
        key=carry_key,
        label_visibility="collapsed"
    )

    # Track user changes
    if new_home_carry != home_carry_value:
        inputs["home_carry_user_set"] = True
        inputs["home_carry"] = float(new_home_carry)
        st.session_state.comparison_home_carry_cost = float(new_home_carry)
        print(f"[INTRO_HOME_CARRY] user_set={inputs['home_carry']}")
    else:
        # Sync to legacy key
        st.session_state.comparison_home_carry_cost = home_carry_value

    st.markdown("")

    # CTA: Compare My Cost Options (full width)
    has_zip = bool(inputs.get("zip") and len(str(inputs.get("zip"))) == 5)

    if st.button("Compare My Cost Options", key="intro_compare_cta", use_container_width=True, type="primary"):
        if has_zip:
            print(f"[INTRO] Navigate to quick_estimate: zip={inputs.get('zip')}")
            go_to_quick_estimate()
        else:
            st.error("⚠️ Please enter a valid ZIP code first")

    # Show ZIP warning if missing
    if not has_zip:
        st.caption("💡 ZIP code is required to show your estimate.")

    # Close container and reset CP intro flag
    st.markdown("</div>", unsafe_allow_html=True)
    st.session_state["cp_intro"] = False


def _render_auth_gate():
    """Render authentication gate.

    Users must authenticate to access detailed financial planning.
    This is the mandatory workflow step after quick estimate.
    """

    st.title("🔐 Sign In Required")

    st.info("""
    ### Create Your Free Account
    
    To access the detailed Cost Planner, you'll need to sign in or create a free account.
    
    **Why sign in?**
    - 💾 Save your progress automatically
    - 📊 Access personalized recommendations
    - 🔒 Keep your financial data secure
    - 📧 Get expert guidance and updates
    """)

    # Placeholder for auth buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📧 Sign In with Email", type="primary", use_container_width=True):
            st.info("🚧 Email authentication coming soon")

    with col2:
        if st.button("🔗 Sign In with Google", use_container_width=True):
            st.info("🚧 Google OAuth coming soon")

    st.markdown("---")

    if st.button("← Back to Quick Estimate", key="auth_back"):
        st.session_state.cost_v2_step = "intro"
        st.rerun()
