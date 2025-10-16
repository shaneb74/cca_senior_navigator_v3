"""
Cost Planner v2 - Authentication Step

Simple authentication integration using core.state toggle system.
Users can continue as guest or sign in for full functionality.
"""

import streamlit as st
from core.state import is_authenticated, authenticate_user, get_user_name


def render():
    """Render authentication step.
    
    For MVP, we use the existing toggle authentication system.
    Users can:
    1. Auto-skip if already authenticated (seamless experience)
    2. Sign in (toggle auth on)
    3. Continue as guest (limited features)
    
    Future: Replace with real OAuth/email authentication.
    """
    
    # AUTO-ADVANCE: If already authenticated, skip this step
    if is_authenticated():
        # User is logged in - go directly to next step
        st.session_state.cost_v2_step = "triage"
        st.rerun()
        return
    
    # Not authenticated - show streamlined sign-in options
    st.title("🔐 Sign In to Save Your Progress")
    
    # Simplified, cleaner benefits (no yellow box)
    st.markdown("""
    Create an account or sign in to save your progress and get personalized recommendations.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📧 Sign In")
        
        st.markdown("**For MVP Demo:**")
        
        name_input = st.text_input(
            "Your Name",
            value="Sarah",
            help="Enter your name for personalized experience",
            key="cost_v2_auth_name"
        )
        
        email_input = st.text_input(
            "Email Address",
            value="sarah@example.com",
            help="We'll send updates and cost estimates here",
            key="cost_v2_auth_email"
        )
        
        if st.button("🔐 Sign In", type="primary", use_container_width=True, key="cost_v2_signin"):
            # Toggle authentication on
            authenticate_user(name=name_input, email=email_input)
            st.success(f"✅ Welcome, {name_input}!")
            st.rerun()
    
    with col2:
        st.markdown("### 🌐 Continue as Guest")
        
        st.markdown("""
        **Note:** Progress won't be saved in guest mode. You can sign in later.
        """)
        
        if st.button("Continue as Guest", use_container_width=True, key="cost_v2_guest"):
            # Set guest flag and continue
            st.session_state.cost_v2_guest_mode = True
            st.session_state.cost_v2_step = "triage"
            st.rerun()
    
    st.markdown("---")
    
    # Back button
    if st.button("← Back to Quick Estimate", key="auth_back"):
        st.session_state.cost_v2_step = "intro"
        st.rerun()
