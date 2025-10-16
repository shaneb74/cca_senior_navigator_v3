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
    
    # Initialize qualifier state
    if "cost_v2_qualifiers" not in st.session_state:
        st.session_state.cost_v2_qualifiers = {
            "is_veteran": False,
            "is_homeowner": False,
            "is_on_medicaid": False
        }
    
    st.markdown("#### Please answer these three questions:")
    
    # Question 1: Veteran status
    is_veteran = st.checkbox(
        "✅ Are you (or your loved one) a **Veteran**?",
        value=st.session_state.cost_v2_qualifiers.get("is_veteran", False),
        help="This helps us show VA benefits and resources",
        key="cost_v2_is_veteran"
    )
    
    # Question 2: Home ownership
    is_homeowner = st.checkbox(
        "✅ Do you (or your loved one) own a **home**?",
        value=st.session_state.cost_v2_qualifiers.get("is_homeowner", False),
        help="This helps us assess available assets and funding options",
        key="cost_v2_is_homeowner"
    )
    
    # Question 3: Medicaid status
    is_on_medicaid = st.checkbox(
        "✅ Are you (or your loved one) currently on **Medicaid**? (not Medicare)",
        value=st.session_state.cost_v2_qualifiers.get("is_on_medicaid", False),
        help="This helps us provide specific coverage guidance",
        key="cost_v2_is_on_medicaid"
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
            # Save qualifier data
            st.session_state.cost_v2_qualifiers = {
                "is_veteran": is_veteran,
                "is_homeowner": is_homeowner,
                "is_on_medicaid": is_on_medicaid
            }
            
            # Proceed to modules
            st.session_state.cost_v2_step = "modules"
            st.rerun()
