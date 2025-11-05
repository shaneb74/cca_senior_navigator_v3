"""
Medicaid Clarification & Assessment Page

This page helps disambiguate between Medicaid and Medicare, since many users
confuse these two programs. It provides educational content and routes users
to the appropriate flow based on their actual enrollment status.

Flow:
1. User indicated they're on "Medicaid or State Assistance" in triage
2. This page explains the difference between Medicaid and Medicare
3. User confirms which program(s) they're actually enrolled in
4. Route A: Medicaid confirmed → Simplified Medicaid assessment
5. Route B: Medicare only → Return to normal financial assessment (unset flag)
"""

import streamlit as st

from core.nav import route_to


def render():
    """Render Medicaid clarification and assessment page."""
    
    st.title("💙 Medicaid Program Clarification")
    
    st.markdown("---")
    
    # Educational content block
    st.info("""
    ### ⚠️ Important: Understanding Medicaid vs Medicare
    
    Many people confuse these two programs. Let's clarify the difference:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🏥 **MEDICARE**
        
        **Who qualifies:**
        - Seniors age 65+
        - Some younger people with disabilities
        
        **What it covers:**
        - ✅ Hospital visits
        - ✅ Doctor appointments
        - ✅ Some medical equipment
        - ❌ **Does NOT cover long-term care** (assisted living, memory care)
        
        **Cost:**
        - Monthly premiums (typically $100-200)
        - Based on your work history
        
        **Note:** Most seniors have Medicare. This is the standard health insurance program.
        """)
    
    with col2:
        st.markdown("""
        ### 💚 **MEDICAID**
        
        **Who qualifies:**
        - People with **limited income**
        - People with **limited assets**
        - Must meet strict financial requirements
        
        **What it covers:**
        - ✅ Hospital visits
        - ✅ Doctor appointments
        - ✅ **Long-term care** (nursing homes)
        - ✅ Some assisted living (varies by state)
        
        **Cost:**
        - Little to no cost
        - State/federal assistance program
        
        **Note:** Medicaid is a low-income assistance program with different planning needs.
        """)
    
    st.markdown("---")
    
    # Clarification question
    st.markdown("### 📋 Please Confirm Your Enrollment")
    st.markdown("Based on the above information, which program(s) are you enrolled in?")
    
    st.markdown("")  # Spacing
    
    # Initialize selection state
    if "medicaid_confirmation" not in st.session_state:
        st.session_state.medicaid_confirmation = None
    
    # Radio button options
    medicaid_status = st.radio(
        "Select your situation:",
        options=[
            "medicaid_only",
            "medicare_only", 
            "both",
            "neither"
        ],
        format_func=lambda x: {
            "medicaid_only": "✅ I am enrolled in MEDICAID (low-income state assistance)",
            "medicare_only": "🏥 I only have MEDICARE (standard senior health insurance)",
            "both": "✅ I am enrolled in BOTH Medicaid AND Medicare",
            "neither": "❓ I'm not sure / Not enrolled in either"
        }[x],
        index=None,
        key="medicaid_clarification_radio",
        help="Select the option that best describes your current enrollment"
    )
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back", key="medicaid_clarif_back", use_container_width=True):
            # Go back to triage to change answer
            st.session_state.cost_v2_step = "triage"
            st.rerun()
    
    with col2:
        # Enable continue only if selection made
        if medicaid_status:
            if st.button(
                "Continue →",
                type="primary",
                use_container_width=True,
                key="medicaid_clarif_continue"
            ):
                _handle_medicaid_confirmation(medicaid_status)
        else:
            st.button(
                "Continue →",
                type="primary",
                use_container_width=True,
                disabled=True,
                help="Please select an option above to continue",
                key="medicaid_clarif_continue_disabled"
            )
    
    with col3:
        if st.button("← Back to Lobby", key="medicaid_clarif_back_lobby", use_container_width=True):
            route_to("hub_lobby")


def _handle_medicaid_confirmation(status: str):
    """Handle user's confirmation of Medicaid enrollment.
    
    Routes to appropriate flow based on actual enrollment:
    - Medicaid (only or with Medicare) → Simplified Medicaid assessment
    - Medicare only → Normal financial assessment (unset Medicaid flag)
    - Neither/Unsure → Return to triage for clarification
    
    Args:
        status: One of "medicaid_only", "medicare_only", "both", "neither"
    """
    
    if status in ["medicaid_only", "both"]:
        # User confirmed they ARE on Medicaid
        # Keep the Medicaid flag set, route to simplified assessment
        st.session_state.flags["medicaid_planning_interest"] = True
        st.session_state.flags["confirmed_medicaid_user"] = True
        
        # Update qualifiers
        st.session_state.cost_v2_qualifiers["is_on_medicaid"] = True
        if "profile" in st.session_state:
            st.session_state.profile["qualifiers"]["is_on_medicaid"] = True
        
        # Route to simplified Medicaid assessment
        st.session_state.cost_v2_step = "medicaid_assessment"
        st.rerun()
        
    elif status == "medicare_only":
        # User only has Medicare (common confusion)
        # UNSET Medicaid flag, route to normal financial assessment
        st.session_state.flags["medicaid_planning_interest"] = False
        st.session_state.flags["confirmed_medicaid_user"] = False
        
        # Update qualifiers
        st.session_state.cost_v2_qualifiers["is_on_medicaid"] = False
        if "profile" in st.session_state:
            st.session_state.profile["qualifiers"]["is_on_medicaid"] = False
        
        # Note: They likely have Medicare, which is normal for seniors
        st.session_state.flags["has_medicare"] = True
        
        # Route to normal financial assessment hub
        st.session_state.cost_v2_step = "assessments"
        st.rerun()
        
    else:  # neither or unsure
        # User is unsure - send back to triage
        st.warning("Please return to the previous question to clarify your enrollment status.")
        st.session_state.cost_v2_step = "triage"
        st.rerun()


def render_medicaid_assessment():
    """Render simplified Medicaid-specific assessment.
    
    For users who confirmed they're on Medicaid, this provides:
    - Empathetic messaging about limited resources
    - Simplified data collection (Medicaid limits are standard)
    - Focus on Medicaid eligibility and state-specific rules
    - Modified advisor CTAs (different planning needs)
    """
    
    st.title("💚 Medicaid Planning Assessment")
    
    # Navi panel with empathetic messaging
    from core.navi_module import render_module_navi_coach
    render_module_navi_coach(
        title_text="We understand you're working with limited resources",
        body_text="Medicaid has specific rules and limits. Let's gather some basic information to help guide your planning.",
        tip_text="Since you're on Medicaid, the financial planning process is different. We'll focus on maintaining eligibility while ensuring quality care."
    )
    
    st.markdown("---")
    
    # Info about Medicaid planning
    st.info("""
    ### 📋 About Medicaid & Long-Term Care
    
    Since you're enrolled in Medicaid, your care planning has some unique considerations:
    
    - **Asset Limits:** Medicaid has strict asset limits (typically $2,000 for individuals)
    - **Income Limits:** Monthly income must be below state thresholds
    - **Covered Services:** Medicaid covers nursing home care and some home/community-based services
    - **State Variations:** Rules vary by state
    
    Our financial assessment will be simplified since your resources are already within Medicaid guidelines.
    """)
    
    st.markdown("---")
    
    # Basic information collection
    st.markdown("### 💬 Basic Information")
    
    # State of residence (critical for Medicaid rules)
    state = st.text_input(
        "What state do you live in?",
        max_chars=2,
        placeholder="e.g., CA, NY, FL",
        help="Medicaid rules vary significantly by state",
        key="medicaid_assessment_state"
    )
    
    # Current care situation
    st.markdown("**Current Care Situation:**")
    care_situation = st.radio(
        "Where are you currently receiving care?",
        options=[
            "home",
            "assisted_living",
            "nursing_home",
            "planning"
        ],
        format_func=lambda x: {
            "home": "🏡 Living at home with Medicaid services",
            "assisted_living": "🏘️ In assisted living facility",
            "nursing_home": "🏥 In nursing home",
            "planning": "📋 Planning for future care"
        }[x],
        key="medicaid_care_situation"
    )
    
    # Medicaid waiver program
    has_waiver = st.checkbox(
        "Are you enrolled in a Medicaid waiver program? (HCBS, EDCD, etc.)",
        help="Medicaid waivers allow home and community-based services as an alternative to nursing homes",
        key="medicaid_has_waiver"
    )
    
    if has_waiver:
        waiver_type = st.text_input(
            "Which waiver program?",
            placeholder="e.g., HCBS, EDCD, Community Care",
            key="medicaid_waiver_type"
        )
    
    st.markdown("---")
    
    # Resources and support needed
    st.markdown("### 🤝 How Can We Help?")
    
    help_needed = st.multiselect(
        "What support are you looking for? (Select all that apply)",
        options=[
            "Understanding Medicaid rules in my state",
            "Finding Medicaid-accepting facilities",
            "Maintaining Medicaid eligibility",
            "Navigating waiver programs",
            "Understanding covered services",
            "Planning for spouse (spousal impoverishment protections)",
            "Other questions about Medicaid and care"
        ],
        key="medicaid_help_needed"
    )
    
    # Additional notes
    additional_notes = st.text_area(
        "Any additional information or questions?",
        placeholder="Share any concerns or specific questions about Medicaid and your care planning...",
        key="medicaid_additional_notes"
    )
    
    st.markdown("---")
    
    # Navigation and next steps
    st.markdown("### 🎯 Next Steps")
    
    st.info("""
    **For Medicaid recipients, we recommend:**
    
    1. **Medicaid Planning Attorney** - Specialized legal help with eligibility and asset protection
    2. **State Medicaid Office** - Official information about your state's specific rules
    3. **Care Coordination** - Help finding Medicaid-accepting facilities
    
    *Note: Our standard financial planning tools are designed for individuals with private resources. 
    For Medicaid recipients, specialized planning is needed.*
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back", key="medicaid_assess_back", use_container_width=True):
            st.session_state.cost_v2_step = "medicaid_clarification"
            st.rerun()
    
    with col2:
        if st.button(
            "Submit & Get Resources →",
            type="primary",
            use_container_width=True,
            key="medicaid_assess_submit"
        ):
            # Save Medicaid assessment data
            st.session_state.medicaid_assessment = {
                "state": state,
                "care_situation": care_situation,
                "has_waiver": has_waiver,
                "waiver_type": waiver_type if has_waiver else None,
                "help_needed": help_needed,
                "additional_notes": additional_notes
            }
            
            # Mark Cost Planner as complete (with Medicaid flag)
            from core.mcip import MCIP
            MCIP.mark_product_complete("cost_planner")
            
            # Route to Medicaid-specific resources/exit page
            st.session_state.cost_v2_step = "medicaid_resources"
            st.rerun()
    
    with col3:
        if st.button("← Back to Lobby", key="medicaid_assess_back_lobby", use_container_width=True):
            route_to("hub_lobby")


def render_medicaid_resources():
    """Render Medicaid-specific resources and next steps page."""
    
    st.title("💚 Medicaid Resources & Next Steps")
    
    st.success("✅ **Thank you for providing this information!**")
    
    st.markdown("---")
    
    # Get saved assessment data
    assessment = st.session_state.get("medicaid_assessment", {})
    user_state = assessment.get("state", "your state")
    
    st.markdown("### 📚 Recommended Resources")
    
    # State-specific Medicaid office
    st.markdown(f"""
    #### 🏛️ {user_state.upper()} Medicaid Office
    
    Your state's Medicaid office is the best resource for:
    - Current income and asset limits
    - Covered services and waiver programs
    - Application assistance
    - Appeals and questions
    
    **Find your state Medicaid office:** [Medicaid.gov State Directory](https://www.medicaid.gov/state-overviews/index.html)
    """)
    
    st.markdown("---")
    
    # Medicaid planning attorneys
    st.markdown("""
    #### ⚖️ Medicaid Planning Attorneys
    
    Specialized attorneys can help with:
    - Asset protection strategies
    - Spousal impoverishment protections
    - Trust planning
    - Application assistance
    - Appeals
    
    **Find a Medicaid planning attorney:** [National Academy of Elder Law Attorneys](https://www.naela.org)
    """)
    
    st.markdown("---")
    
    # Care coordination resources
    st.markdown("""
    #### 🤝 Care Coordination Resources
    
    These organizations help Medicaid recipients find care:
    - **Area Agency on Aging:** Local aging services and care coordination
    - **State SHIP Programs:** Free health insurance counseling
    - **Long-Term Care Ombudsman:** Advocacy for residents in care facilities
    
    **Find local resources:** Call 211 or visit [Eldercare Locator](https://eldercare.acl.gov)
    """)
    
    st.markdown("---")
    
    # What we can still help with
    st.info("""
    ### 💙 How Senior Navigator Can Still Help
    
    While our financial planning tools are designed for individuals with private resources, 
    we can still assist you with:
    
    - **Care Needs Assessment** - Understanding the level of care needed
    - **Facility Research** - Finding Medicaid-accepting facilities in your area
    - **General Education** - Learning about care options and quality indicators
    - **Family Support** - Resources for family caregivers
    
    You can always return to the main lobby to access these tools.
    """)
    
    st.markdown("---")
    
    # Navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "🏠 Return to Main Lobby",
            type="primary",
            use_container_width=True,
            key="medicaid_resources_lobby"
        ):
            route_to("hub_lobby")
    
    with col2:
        if st.button(
            "📋 View My Responses",
            use_container_width=True,
            key="medicaid_resources_view"
        ):
            with st.expander("Your Medicaid Assessment", expanded=True):
                st.json(assessment)
