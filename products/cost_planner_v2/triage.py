"""
Cost Planner v2 - Triage Step

Determines user's current status:
- Existing customer (already in facility/receiving care)
- Planning ahead (no current placement)

This affects which modules are shown and cost calculation approach.
"""

import streamlit as st
from core.mcip import MCIP


def render():
    """Render triage step to determine user status."""
    
    st.title("🎯 Your Current Situation")
    st.markdown("### Help us understand where you are in your care journey")
    
    # Get GCP recommendation for context
    recommendation = MCIP.get_care_recommendation()
    
    if recommendation:
        tier = recommendation.tier.replace("_", " ").title()
        st.info(f"💡 **Your Care Assessment:** {tier} recommended")
    
    st.markdown("---")
    
    # Initialize triage state
    if "cost_v2_triage" not in st.session_state:
        st.session_state.cost_v2_triage = None
    
    # Status selection
    st.markdown("#### What best describes your current situation?")
    
    status = st.radio(
        "Select one:",
        options=[
            "planning",
            "existing"
        ],
        format_func=lambda x: {
            "planning": "📋 Planning Ahead - Not currently receiving care",
            "existing": "🏥 Existing Customer - Already in facility or receiving care"
        }[x],
        help="This helps us tailor the financial assessment to your situation",
        key="cost_v2_triage_status"
    )
    
    # Show description based on selection
    if status == "planning":
        st.success("""
        ### 📋 Planning Ahead
        
        Great! We'll help you:
        - ✅ Estimate future care costs
        - ✅ Calculate financial runway
        - ✅ Identify funding sources
        - ✅ Compare facility options
        - ✅ Plan for future transitions
        
        **You'll complete:**
        1. Income & Assets assessment
        2. Monthly costs projection
        3. Coverage analysis (insurance, VA, etc.)
        4. Gap analysis and recommendations
        """)
    
    elif status == "existing":
        st.info("""
        ### 🏥 Existing Customer
        
        We'll help you:
        - ✅ Review current costs
        - ✅ Optimize payment sources
        - ✅ Identify additional benefits
        - ✅ Project future expenses
        - ✅ Plan for cost increases
        
        **You'll complete:**
        1. Current facility/care costs
        2. Payment sources review
        3. Additional benefits eligibility
        4. Future cost projection
        """)
    
    st.markdown("---")
    
    # Additional context questions
    with st.expander("📝 Optional: Tell us more (helps with accuracy)"):
        
        if status == "planning":
            location = st.text_input(
                "Preferred Location (City, State)",
                placeholder="e.g., San Diego, CA",
                help="We'll use this for regional cost adjustments",
                key="cost_v2_location"
            )
            
            timeline = st.selectbox(
                "Expected Timeline",
                options=[
                    "Immediate (0-3 months)",
                    "Near-term (3-6 months)",
                    "Mid-term (6-12 months)",
                    "Long-term (1+ years)"
                ],
                help="When do you expect to need care?",
                key="cost_v2_timeline"
            )
        
        elif status == "existing":
            facility_name = st.text_input(
                "Facility/Provider Name",
                placeholder="e.g., Sunrise Senior Living",
                help="Optional - helps us verify current costs",
                key="cost_v2_facility"
            )
            
            monthly_cost = st.number_input(
                "Current Monthly Cost ($)",
                min_value=0,
                max_value=50000,
                step=100,
                help="Approximate current monthly cost",
                key="cost_v2_current_cost"
            )
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("← Back", key="triage_back"):
            st.session_state.cost_v2_step = "gcp_gate"
            st.rerun()
    
    with col2:
        if st.button("Continue to Financial Assessment →", type="primary", use_container_width=True, key="triage_continue"):
            # Save triage data
            st.session_state.cost_v2_triage = {
                "status": status,
                "location": st.session_state.get("cost_v2_location", ""),
                "timeline": st.session_state.get("cost_v2_timeline", ""),
                "facility_name": st.session_state.get("cost_v2_facility", ""),
                "monthly_cost": st.session_state.get("cost_v2_current_cost", 0)
            }
            
            # Proceed to modules
            st.session_state.cost_v2_step = "modules"
            st.rerun()
    
    # Help text
    st.caption("💡 **Tip:** Your responses help us provide more accurate cost estimates and recommendations.")
