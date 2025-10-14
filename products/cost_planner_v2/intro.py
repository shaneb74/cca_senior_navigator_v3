"""
Cost Planner v2 - Intro Page

Quick estimate calculator (unauthenticated).
Allows anonymous users to get a ballpark cost estimate before creating an account.

Workflow:
1. Welcome message
2. Quick estimate form (care type + location)
3. Show estimate
4. Gate: "Sign in to get detailed breakdown"
5. Auth → Triage
"""

import streamlit as st
from typing import Optional
from products.cost_planner_v2.utils import CostCalculator


def render():
    """Render intro page with quick estimate."""
    
    st.title("💰 Cost Planner")
    st.markdown("### Get a Quick Cost Estimate")
    
    st.info("""
    **See what senior care costs in your area** — in less than 30 seconds.
    
    This quick calculator gives you ballpark costs based on:
    - ✅ Type of care needed
    - ✅ Your location (regional cost differences)
    
    💡 **Sign in later** to get a detailed financial plan with personalized recommendations.
    """)
    
    st.markdown("---")
    
    # Initialize session state for quick estimate
    if "cost_v2_quick_estimate" not in st.session_state:
        st.session_state.cost_v2_quick_estimate = None
    
    # Quick estimate form
    _render_quick_estimate_form()
    
    # Show results if calculated
    if st.session_state.cost_v2_quick_estimate:
        st.markdown("---")
        _render_quick_estimate_results()


def _render_quick_estimate_form():
    """Render quick estimate input form."""
    
    st.markdown("#### 📝 Tell us about your needs:")
    
    # Care type selection
    # CRITICAL: These are the ONLY 5 allowed care types
    care_type = st.selectbox(
        "What type of care are you exploring?",
        options=[
            "No Care Needed",
            "In-Home Care",
            "Assisted Living",
            "Memory Care",
            "Memory Care (High Acuity)"
        ],
        help="Choose the care option that best matches your current needs",
        key="cost_v2_quick_care_type"
    )
    
    # Map display name to internal key
    care_type_map = {
        "No Care Needed": "no_care_needed",
        "In-Home Care": "in_home_care",
        "Assisted Living": "assisted_living",
        "Memory Care": "memory_care",
        "Memory Care (High Acuity)": "memory_care_high_acuity"
    }
    care_tier = care_type_map[care_type]
    
    # Location input
    col1, col2 = st.columns(2)
    
    with col1:
        zip_code = st.text_input(
            "ZIP Code (optional)",
            max_chars=5,
            placeholder="90210",
            help="Enter your ZIP code for regional cost adjustment",
            key="cost_v2_quick_zip"
        )
    
    with col2:
        state = st.text_input(
            "State (optional)",
            max_chars=2,
            placeholder="CA",
            help="2-letter state code (e.g., CA, NY, FL)",
            key="cost_v2_quick_state"
        ).upper()
    
    # Calculate button
    if st.button("🔍 Calculate Quick Estimate", type="primary", use_container_width=True):
        _calculate_quick_estimate(care_tier, zip_code or None, state or None)


def _calculate_quick_estimate(care_tier: str, zip_code: Optional[str], state: Optional[str]):
    """Calculate and store quick estimate."""
    
    # Validate inputs
    if zip_code and len(zip_code) < 5:
        st.error("Please enter a valid 5-digit ZIP code, or leave it blank.")
        return
    
    if state and len(state) != 2:
        st.error("Please enter a 2-letter state code (e.g., CA, NY, FL), or leave it blank.")
        return
    
    # Calculate estimate
    try:
        estimate = CostCalculator.calculate_quick_estimate(
            care_tier=care_tier,
            zip_code=zip_code,
            state=state
        )
        
        st.session_state.cost_v2_quick_estimate = {
            "estimate": estimate,
            "care_tier": care_tier,
            "zip_code": zip_code,
            "state": state
        }
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error calculating estimate: {str(e)}")


def _render_quick_estimate_results():
    """Render quick estimate results."""
    
    data = st.session_state.cost_v2_quick_estimate
    estimate = data["estimate"]
    
    st.success("### ✅ Your Quick Estimate")
    
    # Show care type and location
    care_type_display = estimate.care_tier.replace("_", " ").title()
    location_display = estimate.region_name
    
    st.markdown(f"""
    **Care Type:** {care_type_display}  
    **Location:** {location_display}
    """)
    
    if estimate.multiplier != 1.0:
        multiplier_pct = int((estimate.multiplier - 1.0) * 100)
        if multiplier_pct > 0:
            st.caption(f"ℹ️ Costs in {estimate.region_name} are about {multiplier_pct}% above the national average.")
        else:
            st.caption(f"ℹ️ Costs in {estimate.region_name} are about {abs(multiplier_pct)}% below the national average.")
    
    st.markdown("---")
    
    # Show cost estimates
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Monthly Cost",
            value=f"${estimate.monthly_adjusted:,.0f}",
            help="Estimated monthly cost for base care"
        )
    
    with col2:
        st.metric(
            label="Annual Cost",
            value=f"${estimate.annual:,.0f}",
            help="Estimated annual cost (monthly × 12)"
        )
    
    with col3:
        st.metric(
            label="3-Year Projection",
            value=f"${estimate.three_year:,.0f}",
            help="Estimated 3-year cost (annual × 3)"
        )
    
    # Important notes
    st.info("""
    **💡 This is a quick estimate only.** Actual costs vary based on:
    - Specific facility or care provider
    - Level of care needed (ADLs, medication management, etc.)
    - Additional services (therapy, transportation, activities)
    - Insurance and benefits (Medicare, VA, long-term care insurance)
    """)
    
    st.markdown("---")
    
    # Call to action: Sign in for detailed plan
    st.markdown("### 🎯 Want a Detailed Financial Plan?")
    
    st.markdown("""
    **Sign in to unlock:**
    - ✅ Personalized care assessment (Guided Care Plan)
    - ✅ Detailed cost breakdown with all services
    - ✅ Funding sources and gap analysis
    - ✅ Expert financial review
    - ✅ Facility comparison tool
    - ✅ Medicare and VA benefits calculator
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔐 Sign In / Create Account", type="primary", use_container_width=True, key="quick_estimate_auth"):
            # Go to auth step
            st.session_state.cost_v2_step = "auth"
            st.rerun()
    
    with col2:
        if st.button("🏠 Return to Hub", use_container_width=True, key="quick_estimate_hub"):
            from core.nav import route_to
            route_to("hub_concierge")


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
