"""
Cost Planner v2 - Quick Qualifier

Three simple questions to personalize which financial modules are shown:
- Veteran status (for VA Benefits module)
- Home ownership (for Assets module)
- Medicaid enrollment (for specific coverage guidance)
"""

import streamlit as st


def render():
    """Render quick qualifier questions to personalize modules."""
    
    st.title("📋 Quick Questions")
    st.markdown("### Help us personalize your Financial Assessment")
    
    st.markdown("---")
    
    # Initialize qualifier state (from profile if available, otherwise defaults)
    if "cost_v2_qualifiers" not in st.session_state:
        # Check if we have saved qualifiers in user profile
        profile_qualifiers = st.session_state.get('profile', {}).get('qualifiers', {})
        st.session_state.cost_v2_qualifiers = {
            "is_on_medicaid": profile_qualifiers.get("is_on_medicaid", False),
            "is_veteran": profile_qualifiers.get("is_veteran", False),
            "is_homeowner": profile_qualifiers.get("is_homeowner", False)
        }
    
    st.markdown("#### Please answer these three questions:")
    
    st.markdown("")  # Add spacing
    
    # Question 1: Medicaid or State Assistance
    st.markdown("**1. Are you (or your loved one) currently on Medicaid or State Assistance programs?**")
    is_on_medicaid = st.checkbox(
        "Yes, currently on Medicaid or State Assistance",
        value=st.session_state.cost_v2_qualifiers.get("is_on_medicaid", False),
        help="This helps us provide specific coverage guidance and identify additional resources",
        key="cost_v2_is_on_medicaid",
        label_visibility="visible"
    )
    
    st.markdown("")  # Add spacing
    
    # Question 2: Veteran status
    st.markdown("**2. Are you (or your loved one) a Veteran?**")
    is_veteran = st.checkbox(
        "Yes, a Veteran",
        value=st.session_state.cost_v2_qualifiers.get("is_veteran", False),
        help="This helps us show VA benefits and resources",
        key="cost_v2_is_veteran",
        label_visibility="visible"
    )
    
    st.markdown("")  # Add spacing
    
    # Question 3: Home ownership
    st.markdown("**3. Are you (or your loved one) a home owner?**")
    is_homeowner = st.checkbox(
        "Yes, a home owner",
        value=st.session_state.cost_v2_qualifiers.get("is_homeowner", False),
        help="This helps us assess available assets and funding options",
        key="cost_v2_is_homeowner",
        label_visibility="visible"
    )
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("← Back", key="qualifier_back"):
            st.session_state.cost_v2_step = "auth"
            st.rerun()
    
    with col2:
        if st.button("Continue to Financial Assessment →", type="primary", use_container_width=True, key="qualifier_continue"):
            # Save qualifier data to session state
            st.session_state.cost_v2_qualifiers = {
                "is_on_medicaid": is_on_medicaid,
                "is_veteran": is_veteran,
                "is_homeowner": is_homeowner
            }
            
            # Save to user profile for persistence
            if 'profile' not in st.session_state:
                st.session_state.profile = {}
            
            st.session_state.profile['qualifiers'] = {
                "is_on_medicaid": is_on_medicaid,
                "is_veteran": is_veteran,
                "is_homeowner": is_homeowner
            }
            
            # Proceed to modules
            st.session_state.cost_v2_step = "modules"
            st.rerun()
