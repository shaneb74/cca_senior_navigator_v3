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

    # Open centered container for calm, consistent layout (desktop only)
    st.markdown("<div class='sn-container'>", unsafe_allow_html=True)

    # Get GCP recommendation for context
    gcp_rec = MCIP.get_care_recommendation()
    rec_tier = None
    if gcp_rec and hasattr(gcp_rec, 'tier'):
        rec_tier = gcp_rec.tier

    # Build Navi header content
    header_title = "Let’s look at costs"
    tier_display = None
    if rec_tier:
        tier_display = rec_tier.replace("_", " ").title()
    header_reason = (
        f"I’ve pre-selected {tier_display} from your Guided Care Plan. You can explore other scenarios too."
        if tier_display
        else "We’ll start with your Guided Care Plan. You can explore other scenarios too."
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

    # Show comparison view when gate is complete
    if is_ready:
        st.markdown("---")
        zip_code = st.session_state.get("cost_v2_quick_zip")

        if zip_code:
            comparison_view.render_comparison_view(zip_code=zip_code)
        else:
            st.error("⚠️ ZIP code is required to show estimate.")

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
