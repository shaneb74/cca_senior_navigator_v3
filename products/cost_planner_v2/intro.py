"""
Cost Planner v2 - Intro Page (Quick Estimate)

Unauthenticated quick estimate calculator.
Allows anonymous users to get a ballpark cost estimate before creating an account.

Spec:
- ZIP only (no State field)
- 5 care types only: No Care Recommended, In-Home Care, Assisted Living, Memory Care, Memory Care (High Acuity)
- Seed with GCP recommendation when available
- Line-item breakdown: base cost, regional %, condition add-ons, total
- Reassurance copy + CTA to Full Assessment

Workflow:
1. Welcome message
2. Quick estimate form (care type + ZIP)
3. Show line-item breakdown
4. Reassurance copy
5. CTA → Full Assessment (authentication)
"""

import streamlit as st

from core.mcip import MCIP
from products.cost_planner_v2 import comparison_view, prepare_quick_estimate


def render():
    """Render intro page with prepare gate, then comparison view.
    
    Flow:
    1. Show prepare gate (personalization questions)
    2. When complete, show comparison view (Quick Estimate)
    """

    # Mark CP intro scope for header helper
    st.session_state["cp_intro"] = True

    # HOUSEHOLD FLOW: Load household and CarePlans (single-writer pattern)
    try:
        from core.household import ensure_household_state, get_careplan_for
        
        # Only prefill if cost.inputs not already initialized
        if "cost.inputs" not in st.session_state:
            hh = ensure_household_state(st)
            
            # Get person IDs
            primary_id = st.session_state.get("person.primary_id")
            partner_id = st.session_state.get("person.partner_id")
            
            # Load CarePlans
            cp_primary = get_careplan_for(st, primary_id) if primary_id else None
            cp_partner = get_careplan_for(st, partner_id) if partner_id else None
            
            # Prefill cost inputs from household data (single write on first entry)
            inputs = {
                "zip": hh.zip,
                "keep_home": hh.keep_home_default if hh.keep_home_default is not None else False,
                "owner_tenant": hh.home_owner_type or "unknown",
            }
            
            # Use hours from primary CarePlan if available
            if cp_primary:
                inputs["hours"] = cp_primary.hours_user or cp_primary.hours_suggested
            
            st.session_state["cost.inputs"] = inputs
            print(f"[COST_PLANNER] Prefilled: zip={hh.zip} has_partner={hh.has_partner}")
        
        # Log ZIP state on load
        current_zip = st.session_state.get("cost.inputs", {}).get("zip")
        if current_zip:
            print(f"[ZIP_STATE] loaded zip={current_zip} from cost.inputs")
            
        # Initialize cost.view_mode ONCE (never reset during reruns)
        # Single source of truth: "compare" or "single"
        if "cost.view_mode" not in st.session_state:
            # Default to single-path view on first load
            st.session_state["cost.view_mode"] = "single"
            print(f"[VIEW_MODE] initialized to single")
            
        # Mirror to cost.compare_inhome for backward compatibility
        st.session_state["cost.compare_inhome"] = (st.session_state["cost.view_mode"] == "compare")
            
    except Exception:
        # Fallback to non-household flow
        # Initialize cost.inputs if missing
        if "cost.inputs" not in st.session_state:
            st.session_state["cost.inputs"] = {}
        # Initialize cost.view_mode ONCE (never reset during reruns)
        if "cost.view_mode" not in st.session_state:
            st.session_state["cost.view_mode"] = "single"
            print(f"[VIEW_MODE] initialized to single (fallback)")
        # Mirror to cost.compare_inhome for backward compatibility
        st.session_state["cost.compare_inhome"] = (st.session_state["cost.view_mode"] == "compare")

    # Open centered container for calm, consistent layout (desktop only)
    st.markdown("<div class='sn-container'>", unsafe_allow_html=True)

    # Check for GCP handoff
    from_gcp = st.session_state.get("flow.from_gcp", False)
    handoff_blurb = None
    
    # Get GCP recommendation for context
    gcp_rec = MCIP.get_care_recommendation()
    rec_tier = None
    if gcp_rec and hasattr(gcp_rec, 'tier'):
        rec_tier = gcp_rec.tier

    # GCP HANDOFF LOGIC: Generate contextual blurb and set dual_mode
    if from_gcp:
        try:
            from core.household import ensure_household_state, get_careplan_for
            from ai.navi_engine import (
                detect_dual_mode_from_careplans,
                get_primary_tier_from_careplans,
                generate_handoff_blurb
            )
            
            # Collect available care plans
            careplans = []
            hh = ensure_household_state(st)
            
            # Get person IDs
            primary_id = st.session_state.get("person.primary_id")
            partner_id = st.session_state.get("person.partner_id")
            
            # Load CarePlans
            if primary_id:
                cp_primary = get_careplan_for(st, primary_id)
                if cp_primary:
                    careplans.append(cp_primary)
                    
            if partner_id:
                cp_partner = get_careplan_for(st, partner_id)
                if cp_partner:
                    careplans.append(cp_partner)
            
            # Set dual_mode based on multiple care plans
            dual_mode = detect_dual_mode_from_careplans(careplans)
            if dual_mode and "cost.dual_mode" not in st.session_state:
                st.session_state["cost.dual_mode"] = True
                print(f"[GCP_HANDOFF] Enabled dual_mode: {len(careplans)} care plans detected")
            
            # Get primary and partner tiers for context
            primary_tier = get_primary_tier_from_careplans(careplans) or rec_tier
            partner_tier = None
            if len(careplans) >= 2:
                # Get partner tier from the other care plan
                for cp in careplans:
                    cp_tier = getattr(cp, 'final_tier', None) or getattr(cp, 'tier', None)
                    if cp_tier and cp_tier != primary_tier:
                        from ai.navi_engine import normalize_tier
                        partner_tier = normalize_tier(cp_tier)
                        break
            
            # Get flags for context
            flags = []
            if gcp_rec and hasattr(gcp_rec, 'flags'):
                flags = gcp_rec.flags
            
            # Calculate care intensity from GCP data
            care_intensity = "medium"  # default
            if gcp_rec and hasattr(gcp_rec, 'tier_score'):
                if gcp_rec.tier_score >= 0.8:
                    care_intensity = "high"
                elif gcp_rec.tier_score <= 0.4:
                    care_intensity = "low"
            
            # Determine if in-home comparison is suggested
            compare_inhome_suggested = (
                primary_tier in ("assisted_living", "memory_care", "memory_care_high_acuity") or
                dual_mode or 
                st.session_state.get("cost.compare_inhome", False)
            )
            
            # Threshold detection (placeholder - would come from cost analysis)
            threshold_crossed = False  # TODO: Implement based on regional cost data
            
            # Generate enhanced handoff blurb with full context
            if primary_tier:
                handoff_blurb = generate_handoff_blurb(
                    primary_tier=primary_tier,
                    dual_mode=dual_mode,
                    flags=flags,
                    partner_tier=partner_tier,
                    threshold_crossed=threshold_crossed,
                    care_intensity=care_intensity,
                    compare_inhome_suggested=compare_inhome_suggested
                )
                print(f"[GCP_HANDOFF] Generated enhanced blurb: tier={primary_tier}, dual_mode={dual_mode}, partner_tier={partner_tier}, intensity={care_intensity}")
        except Exception as e:
            print(f"[GCP_HANDOFF] Error generating context: {e}")
            # Fallback to standard flow
            pass

    # Build Navi header content
    header_title = "Let's look at costs"
    tier_display = None
    if rec_tier:
        tier_display = rec_tier.replace("_", " ").title()
    
    # Use handoff blurb if available, otherwise use standard messaging
    if handoff_blurb:
        header_reason = handoff_blurb
    else:
        header_reason = (
            f"I've pre-selected {tier_display} from your Guided Care Plan. You can explore other scenarios too."
            if tier_display
            else "We'll start with your Guided Care Plan. You can explore other scenarios too."
        )

    # Use the unified header helper (scoped to CP intro)
    try:
        from products.gcp_v4.ui_helpers import render_navi_header_message
        # Feed title/subtitle through session to the helper
        st.session_state["gcp_step_title"] = header_title
        st.session_state["gcp_step_subtitle"] = header_reason
        render_navi_header_message()
    except Exception:
        pass

    # Show prepare gate first
    is_ready = prepare_quick_estimate.render_prepare_gate(
        recommendation_context=rec_tier
    )

    # Show comparison view when gate is complete OR user has toggled to compare mode OR single mode is set
    view_mode = st.session_state.get("cost.view_mode", "single")
    single_path_tier = st.session_state.get("cost.single_path_tier")
    
    # Log intro state
    zip_from_inputs = st.session_state.get("cost.inputs", {}).get("zip")
    zip_from_v2 = st.session_state.get("cost_v2_quick_zip")
    print(f"[CP_INTRO] is_ready={is_ready} view_mode={view_mode} single_path_tier={single_path_tier} zip_inputs={zip_from_inputs} zip_v2={zip_from_v2}")
    
    # Show estimate view when:
    # 1. Gate is complete (is_ready=True), OR
    # 2. User explicitly chose compare mode, OR
    # 3. User explicitly chose single mode via Continue CTA (single_path_tier is set)
    show_estimate_view = is_ready or view_mode == "compare" or single_path_tier is not None
    
    if show_estimate_view:
        st.markdown("---")
        # Use cost.inputs as source of truth, fallback to cost_v2_quick_zip
        zip_code = zip_from_inputs or zip_from_v2
        
        # Log render decision
        print(f"[COST_RENDER] view_mode={view_mode} zip_present={bool(zip_code)} show_estimate={show_estimate_view}")
        
        # Always render comparison view - ZIP gating happens inside for compute only
        # Layout is controlled by view_mode, not ZIP presence
        comparison_view.render_comparison_view(zip_code=zip_code)

    # Close container and reset single-render guard and CP intro flag at end of render
    st.markdown("</div>", unsafe_allow_html=True)
    if st.session_state.get("_gcp_cp_header_rendered"):
        st.session_state["_gcp_cp_header_rendered"] = False
    if st.session_state.get("_gcp_cp_header_key"):
        del st.session_state["_gcp_cp_header_key"]
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
