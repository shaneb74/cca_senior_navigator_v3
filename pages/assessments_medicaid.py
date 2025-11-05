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


# Apply clean styling to override Streamlit defaults
def _apply_clean_styling():
    """Apply custom CSS to make the page look professional."""
    st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Clean info boxes */
    .stAlert {
        background-color: #f8fafc !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    
    /* Clean radio buttons */
    .stRadio > label {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #475569 !important;
    }
    
    .stRadio > div {
        gap: 12px !important;
    }
    
    .stRadio label {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
    }
    
    .stRadio label:hover {
        border-color: #3b82f6 !important;
        background: #f8fafc !important;
    }
    
    /* Clean checkboxes */
    .stCheckbox {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }
    
    /* Clean text inputs */
    .stTextInput input, .stTextArea textarea {
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Clean multiselect */
    .stMultiSelect {
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
    }
    
    /* Remove excessive spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Clean buttons */
    .stButton button {
        border-radius: 6px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
    }
    
    /* Hide emoji spam in section headers */
    h1, h2, h3 {
        color: #0f172a !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render():
    """Render Medicaid clarification and assessment page."""
    
    _apply_clean_styling()
    
    # Use Navi for education instead of info boxes
    from core.navi_module import render_module_navi_coach
    render_module_navi_coach(
        title_text="Understanding Medicaid vs Medicare",
        body_text="Many people confuse Medicaid and Medicare. Medicare is standard health insurance for seniors 65+ (most seniors have this). Medicaid is a low-income assistance program with strict asset limits. Medicare does NOT cover long-term care, but Medicaid does.",
        tip_text="If you only have Medicare (the standard senior program), you'll continue to our normal financial assessment. If you're on Medicaid (low-income assistance), we'll provide specialized resources."
    )
    
    # Clean title
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 40px auto;'>
        <h1 style='font-size: 32px; font-weight: 700; color: #0f172a; margin: 0 0 8px 0;'>
            Medicaid Program Clarification
        </h1>
        <p style='font-size: 15px; color: #64748b; margin: 0;'>
            Let's confirm which program you're enrolled in
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div style='padding: 20px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; height: 100%;'>
            <div style='font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 16px;'>
                MEDICARE
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Who qualifies:**")
        st.markdown("• Seniors age 65+  \n• Some younger people with disabilities")
        
        st.markdown("**What it covers:**")
        st.markdown("• Hospital visits  \n• Doctor appointments  \n• Some medical equipment  \n• **Does NOT cover long-term care**")
        
        st.markdown("**Cost:**")
        st.markdown("• Monthly premiums (typically $100-200)  \n• Based on your work history")
        
        st.markdown("""
        <div style='margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 6px; font-size: 13px; color: #475569;'>
            Most seniors have Medicare. This is the standard health insurance program.
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='padding: 20px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; height: 100%;'>
            <div style='font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 16px;'>
                MEDICAID
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Who qualifies:**")
        st.markdown("• People with limited income  \n• People with limited assets  \n• Must meet strict financial requirements")
        
        st.markdown("**What it covers:**")
        st.markdown("• Hospital visits  \n• Doctor appointments  \n• **Long-term care (nursing homes)**  \n• Some assisted living (varies by state)")
        
        st.markdown("**Cost:**")
        st.markdown("• Little to no cost  \n• State/federal assistance program")
        
        st.markdown("""
        <div style='margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 6px; font-size: 13px; color: #475569;'>
            Medicaid is a low-income assistance program with different planning needs.
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div><div style='height: 32px;'></div>", unsafe_allow_html=True)
    
    # Clarification question - no stupid icons
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 16px auto;'>
        <h2 style='font-size: 18px; font-weight: 600; color: #0f172a; margin: 0 0 8px 0;'>
            Confirm Your Enrollment
        </h2>
        <p style='font-size: 14px; color: #64748b; margin: 0;'>
            Based on the above information, which program(s) are you enrolled in?
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize selection state
    if "medicaid_confirmation" not in st.session_state:
        st.session_state.medicaid_confirmation = None
    
    # Radio button options with cleaner container
    st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
    
    medicaid_status = st.radio(
        "Select your situation:",
        options=[
            "medicaid_only",
            "medicare_only", 
            "both",
            "neither"
        ],
        format_func=lambda x: {
            "medicaid_only": "I am enrolled in MEDICAID (low-income state assistance)",
            "medicare_only": "I only have MEDICARE (standard senior health insurance)",
            "both": "I am enrolled in BOTH Medicaid AND Medicare",
            "neither": "I'm not sure / Not enrolled in either"
        }[x],
        index=None,
        key="medicaid_clarification_radio",
        label_visibility="collapsed"
    )
    
    st.markdown("</div><div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # Navigation buttons - clean styling
    st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button("← Back", key="medicaid_clarif_back", use_container_width=True):
            st.session_state.cost_v2_step = "triage"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div data-role="primary">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button("← Back to Lobby", key="medicaid_clarif_back_lobby", use_container_width=True):
            route_to("hub_lobby")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


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
    
    _apply_clean_styling()
    
    # Clean title
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 40px auto;'>
        <h1 style='font-size: 32px; font-weight: 700; color: #0f172a; margin: 0 0 8px 0;'>
            Medicaid Planning Assessment
        </h1>
        <p style='font-size: 15px; color: #64748b; margin: 0;'>
            Let's gather some basic information to help guide your planning
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navi panel with empathetic messaging
    from core.navi_module import render_module_navi_coach
    render_module_navi_coach(
        title_text="We understand you're working with limited resources",
        body_text="Medicaid has specific rules and limits. Let's gather some basic information to help guide your planning.",
        tip_text="Since you're on Medicaid, the financial planning process is different. We'll focus on maintaining eligibility while ensuring quality care."
    )
    
    # Info about Medicaid planning - clean styling
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 32px auto; padding: 20px; background: #f8fafc; border-left: 4px solid #3b82f6; border-radius: 8px;'>
        <p style='font-size: 15px; font-weight: 600; color: #1e293b; margin: 0 0 16px 0;'>
            About Medicaid & Long-Term Care
        </p>
        <p style='font-size: 14px; color: #475569; margin: 0 0 12px 0;'>
            Since you're enrolled in Medicaid, your care planning has some unique considerations:
        </p>
        <div style='font-size: 14px; color: #64748b; line-height: 1.7;'>
            • Asset Limits: Medicaid has strict asset limits (typically $2,000 for individuals)<br>
            • Income Limits: Monthly income must be below state thresholds<br>
            • Covered Services: Medicaid covers nursing home care and some home/community-based services<br>
            • State Variations: Rules vary by state
        </div>
        <p style='font-size: 13px; color: #64748b; margin: 16px 0 0 0; padding-top: 12px; border-top: 1px solid #e2e8f0;'>
            Our financial assessment will be simplified since your resources are already within Medicaid guidelines.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Basic information collection
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 32px auto;'>
        <h2 style='font-size: 20px; font-weight: 600; color: #0f172a; margin: 0 0 20px 0;'>
            Basic Information
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
    
    # State of residence (critical for Medicaid rules)
    state = st.text_input(
        "What state do you live in?",
        max_chars=2,
        placeholder="e.g., CA, NY, FL",
        help="Medicaid rules vary significantly by state",
        key="medicaid_assessment_state"
    )
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # Current care situation
    st.markdown("<p style='font-size: 14px; font-weight: 500; color: #475569; margin: 0 0 12px 0;'>Current Care Situation</p>", unsafe_allow_html=True)
    care_situation = st.radio(
        "Where are you currently receiving care?",
        options=[
            "home",
            "assisted_living",
            "nursing_home",
            "planning"
        ],
        format_func=lambda x: {
            "home": "Living at home with Medicaid services",
            "assisted_living": "In assisted living facility",
            "nursing_home": "In nursing home",
            "planning": "Planning for future care"
        }[x],
        key="medicaid_care_situation",
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
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
    
    # Resources and support needed
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 20px auto;'>
        <h2 style='font-size: 20px; font-weight: 600; color: #0f172a; margin: 0;'>
            How Can We Help?
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
    
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
        key="medicaid_additional_notes",
        height=100
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    
    # Navigation and next steps
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 32px auto; padding: 20px; background: #f8fafc; border-left: 4px solid #16a34a; border-radius: 8px;'>
        <p style='font-size: 15px; font-weight: 600; color: #1e293b; margin: 0 0 16px 0;'>
            Next Steps
        </p>
        <p style='font-size: 14px; color: #475569; margin: 0 0 12px 0;'>
            For Medicaid recipients, we recommend:
        </p>
        <div style='font-size: 14px; color: #64748b; line-height: 1.7;'>
            1. <strong>Medicaid Planning Attorney</strong> — Specialized legal help with eligibility and asset protection<br>
            2. <strong>State Medicaid Office</strong> — Official information about your state's specific rules<br>
            3. <strong>Care Coordination</strong> — Help finding Medicaid-accepting facilities
        </div>
        <p style='font-size: 13px; color: #64748b; margin: 16px 0 0 0; padding-top: 12px; border-top: 1px solid #e2e8f0; font-style: italic;'>
            Note: Our standard financial planning tools are designed for individuals with private resources. 
            For Medicaid recipients, specialized planning is needed.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button("← Back", key="medicaid_assess_back", use_container_width=True):
            st.session_state.cost_v2_step = "medicaid_clarification"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div data-role="primary">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button("← Back to Lobby", key="medicaid_assess_back_lobby", use_container_width=True):
            route_to("hub_lobby")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_medicaid_resources():
    """Render Medicaid-specific resources and next steps page."""
    
    _apply_clean_styling()
    
    # Clean title
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 40px auto;'>
        <h1 style='font-size: 32px; font-weight: 700; color: #0f172a; margin: 0 0 8px 0;'>
            Medicaid Resources & Next Steps
        </h1>
        <p style='font-size: 15px; color: #64748b; margin: 0;'>
            Here are the resources that can help with your Medicaid planning
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Success message - clean styling
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 32px auto; padding: 20px; background: #f0fdf4; border-left: 4px solid #16a34a; border-radius: 8px;'>
        <p style='font-size: 15px; font-weight: 600; color: #15803d; margin: 0;'>
            Thank you for providing this information.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get saved assessment data
    assessment = st.session_state.get("medicaid_assessment", {})
    user_state = assessment.get("state", "your state")
    
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto 32px auto;'>
        <h2 style='font-size: 24px; font-weight: 600; color: #0f172a; margin: 0;'>
            Recommended Resources
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Resource cards - clean styling without emoji spam
    st.markdown(f"""
    <div style='max-width: 900px; margin: 0 auto;'>
        <!-- State Medicaid Office -->
        <div style='padding: 24px; background: white; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 20px;'>
            <div style='font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 12px;'>
                {user_state.upper()} Medicaid Office
            </div>
            <p style='font-size: 14px; color: #475569; margin: 0 0 12px 0;'>
                Your state's Medicaid office is the best resource for:
            </p>
            <div style='font-size: 14px; color: #64748b; line-height: 1.7; margin-bottom: 16px;'>
                • Current income and asset limits<br>
                • Covered services and waiver programs<br>
                • Application assistance<br>
                • Appeals and questions
            </div>
            <a href='https://www.medicaid.gov/state-overviews/index.html' target='_blank' style='display: inline-block; padding: 8px 16px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 500;'>
                Find Your State Medicaid Office →
            </a>
        </div>
        
        <!-- Medicaid Planning Attorneys -->
        <div style='padding: 24px; background: white; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 20px;'>
            <div style='font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 12px;'>
                Medicaid Planning Attorneys
            </div>
            <p style='font-size: 14px; color: #475569; margin: 0 0 12px 0;'>
                Specialized attorneys can help with:
            </p>
            <div style='font-size: 14px; color: #64748b; line-height: 1.7; margin-bottom: 16px;'>
                • Asset protection strategies<br>
                • Spousal impoverishment protections<br>
                • Trust planning<br>
                • Application assistance<br>
                • Appeals
            </div>
            <a href='https://www.naela.org' target='_blank' style='display: inline-block; padding: 8px 16px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 500;'>
                Find an Elder Law Attorney →
            </a>
        </div>
        
        <!-- Care Coordination -->
        <div style='padding: 24px; background: white; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 20px;'>
            <div style='font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 12px;'>
                Care Coordination Resources
            </div>
            <p style='font-size: 14px; color: #475569; margin: 0 0 12px 0;'>
                These organizations help Medicaid recipients find care:
            </p>
            <div style='font-size: 14px; color: #64748b; line-height: 1.7; margin-bottom: 16px;'>
                • Area Agency on Aging: Local aging services and care coordination<br>
                • State SHIP Programs: Free health insurance counseling<br>
                • Long-Term Care Ombudsman: Advocacy for residents in care facilities
            </div>
            <a href='https://eldercare.acl.gov' target='_blank' style='display: inline-block; padding: 8px 16px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 500;'>
                Find Local Resources →
            </a>
        </div>
        
        <!-- How We Can Help -->
        <div style='padding: 24px; background: #f8fafc; border-left: 4px solid #3b82f6; border-radius: 8px; margin-bottom: 32px;'>
            <p style='font-size: 16px; font-weight: 600; color: #1e293b; margin: 0 0 12px 0;'>
                How Senior Navigator Can Still Help
            </p>
            <p style='font-size: 14px; color: #475569; margin: 0 0 12px 0;'>
                While our financial planning tools are designed for individuals with private resources, 
                we can still assist you with:
            </p>
            <div style='font-size: 14px; color: #64748b; line-height: 1.7;'>
                • Care Needs Assessment: Understanding the level of care needed<br>
                • Facility Research: Finding Medicaid-accepting facilities in your area<br>
                • General Education: Learning about care options and quality indicators<br>
                • Family Support: Resources for family caregivers
            </div>
            <p style='font-size: 13px; color: #64748b; margin: 12px 0 0 0; font-style: italic;'>
                You can always return to the main lobby to access these tools.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation - clean styling
    st.markdown("<div style='max-width: 900px; margin: 0 auto;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div data-role="primary">', unsafe_allow_html=True)
        if st.button(
            "Return to Main Lobby",
            type="primary",
            use_container_width=True,
            key="medicaid_resources_lobby"
        ):
            route_to("hub_lobby")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div data-role="secondary">', unsafe_allow_html=True)
        if st.button(
            "View My Responses",
            use_container_width=True,
            key="medicaid_resources_view"
        ):
            with st.expander("Your Medicaid Assessment", expanded=True):
                st.json(assessment)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
