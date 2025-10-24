"""
Cost Planner v2 - Authentication Step

Simple authentication integration using core.state toggle system.
Sign-in is required to access Financial Assessment (no guest mode in MVP).
"""

import streamlit as st

from core.state import authenticate_user, is_authenticated


def render():
    """Render authentication step.

    For MVP, we use the existing toggle authentication system.
    Users must sign in to continue - no guest access.

    Workflow:
    1. Show fake auth page with pre-filled demo data
    2. Sign in required to proceed to Financial Assessment

    Future: Replace with real OAuth/email authentication.
    """

    # Not authenticated - show sign-in only (no guest mode in MVP)
    st.title("🔐 Sign In to Continue")

    # Clear explanation of requirement
    st.markdown("""
    Create an account or sign in to access the Financial Assessment.
    """)

    st.markdown("---")

    st.markdown("### 📧 Sign In")

    st.markdown("**For MVP Demo:**")

    name_input = st.text_input(
        "Your Name",
        value="Sarah",
        help="Enter your name for personalized experience",
        key="cost_v2_auth_name",
    )

    email_input = st.text_input(
        "Email Address",
        value="sarah@example.com",
        help="We'll send updates and cost estimates here",
        key="cost_v2_auth_email",
    )

    if st.button("🔐 Sign In", type="primary", use_container_width=True, key="cost_v2_signin"):
        # Toggle authentication on
        authenticate_user(name=name_input, email=email_input)
        st.success(f"✅ Welcome, {name_input}!")
        st.rerun()

    st.markdown("---")

    # Back button
    if st.button("← Back to Quick Estimate", key="auth_back"):
        st.session_state.cost_v2_step = "intro"
        st.rerun()
