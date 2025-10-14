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
    1. Continue as guest (proceed with limited features)
    2. Sign in (toggle auth on)
    
    Future: Replace with real OAuth/email authentication.
    """
    
    st.title("🔐 Sign In to Save Your Progress")
    
    # Check if already authenticated
    if is_authenticated():
        name = get_user_name()
        st.success(f"✅ Welcome back, {name}!")
        st.info("You're signed in and ready to create your detailed financial plan.")
        
        if st.button("Continue to Financial Assessment →", type="primary", use_container_width=True):
            # Move to GCP gate (next step)
            st.session_state.cost_v2_step = "gcp_gate"
            st.rerun()
        return
    
    # Not authenticated - show options
    st.info("""
    ### Why sign in?
    
    - 💾 **Save your progress** - Pick up where you left off
    - 📊 **Get personalized recommendations** - Based on your care plan
    - 🔒 **Keep your data secure** - All information is private
    - 📧 **Receive expert guidance** - Get advisor support
    - 📱 **Access anywhere** - View your plan on any device
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📧 Sign In")
        
        # Simple demo authentication (toggle-based)
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
        
        st.warning("""
        **Guest Mode Limitations:**
        
        - ⚠️ Progress won't be saved
        - ⚠️ Can't access full financial breakdown
        - ⚠️ No advisor review available
        - ⚠️ Results will be lost on page refresh
        """)
        
        st.markdown("You can sign in later to unlock all features.")
        
        if st.button("Continue as Guest", use_container_width=True, key="cost_v2_guest"):
            # Set guest flag and continue
            st.session_state.cost_v2_guest_mode = True
            st.session_state.cost_v2_step = "gcp_gate"
            st.info("ℹ️ Proceeding in guest mode. Sign in anytime to save your work.")
            st.rerun()
    
    st.markdown("---")
    
    # Back button
    if st.button("← Back to Quick Estimate", key="auth_back"):
        st.session_state.cost_v2_step = "intro"
        st.rerun()
    
    # Future auth methods placeholder
    with st.expander("🚀 Coming Soon: More Sign-In Options"):
        st.markdown("""
        We're adding more authentication methods:
        
        - 🔗 **Google Sign-In** - Use your Google account
        - 🔗 **Facebook Sign-In** - Use your Facebook account
        - 📱 **Phone/SMS** - Sign in with your mobile number
        - 🔐 **Magic Link** - Passwordless email authentication
        
        For now, use the simple email sign-in above.
        """)
