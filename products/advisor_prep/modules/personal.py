"""
Advisor Prep - Personal Information Section

LLM-powered comprehensive personal assessment for advisor review.
Replaces form-based approach with detailed narrative analysis.
"""

import streamlit as st

from core.events import log_event
from core.flags import get_flag_value
from core.mcip import MCIP
from core.name_utils import section_header, personalize
from core.navi import render_navi_panel

# Try to import the new LLM advisor summary system
try:
    from ai.advisor_summary_engine import AdvisorSummaryEngine
    LLM_SUMMARY_AVAILABLE = True
except ImportError:
    LLM_SUMMARY_AVAILABLE = False


def render():
    """Render Personal Information prep section with LLM-generated comprehensive assessment."""

    # Get feature flag
    feature_flag = get_flag_value("FEATURE_ADVISOR_SUMMARY_LLM", "off")
    
    # Check if LLM enhancement is active and available
    if feature_flag in ["adjust"] and LLM_SUMMARY_AVAILABLE:
        _render_llm_assessment()
    else:
        _render_legacy_form()


def _render_llm_assessment():
    """Render LLM-generated comprehensive personal assessment."""
    
    # Progress tracking
    container = st.container()
    with container:
        st.success("✓ About Person section complete - comprehensive assessment available for advisor review")
    
    # Navigation buttons at top
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Financial Overview", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "financial"
            st.rerun()
    with col2:
        if st.button("Medical & Care →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "medical"
            st.rerun()
    with col3:
        if st.button("Housing Preferences →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "housing"
            st.rerun()

    # Personalized section header
    st.markdown(f"### {section_header('Personal Information Assessment')}")
    st.markdown(personalize("*This assessment shows what we know about {NAME_POS} personal demographics, social support, and decision-making context.*"))

    try:
        if LLM_SUMMARY_AVAILABLE:
            engine = AdvisorSummaryEngine()
            context = engine.build_advisor_context_from_session()
            assessment = engine.generate_drawer_narrative("about_person", context)
            
            if assessment and assessment.strip():
                st.markdown(f"#### {section_header('Personal Information Summary')}")
                st.markdown(assessment)
            else:
                st.warning("Assessment generation temporarily unavailable. Please check back in a moment.")
                _render_legacy_form()
        else:
            st.warning("LLM assessment system not available. Showing basic form.")
            _render_legacy_form()
            
    except Exception as e:
        st.error(f"Error generating assessment: {str(e)}")
        _render_legacy_form()

    # Render Navi panel for contextual guidance
    render_navi_panel()

    # Log completion
    log_event("advisor_prep", "personal_section_complete", {"method": "llm_assessment"})


def _render_legacy_form():
    """Render legacy form-based personal section."""
    
    # Personalized section header
    st.markdown(f"### {section_header('Personal Information')}")
    st.markdown(personalize("*Please provide information about {NAME_POS} personal background and support network.*"))
    
    # Basic personal form
    with st.form("personal_form"):
        age_range = st.selectbox(
            personalize("Age Range for {NAME}"),
            ["Under 65", "65-74", "75-84", "85-94", "95+"]
        )
        
        living_situation = st.selectbox(
            personalize("Current Living Situation for {NAME}"),
            ["Lives alone", "Lives with spouse/partner", "Lives with family", "Lives with caregiver", "Other"]
        )
        
        primary_caregiver = st.selectbox(
            personalize("Primary Caregiver for {NAME}"),
            ["Self-sufficient", "Spouse/Partner", "Adult child", "Other family member", "Professional caregiver", "Multiple caregivers"]
        )
        
        support_network = st.multiselect(
            personalize("Support Network for {NAME}"),
            ["Family nearby", "Friends in area", "Religious community", "Neighbors", "Professional services", "Limited support"]
        )
        
        emergency_contact = st.text_input(
            personalize("Emergency Contact for {NAME}"),
            help=personalize("Name and relationship of emergency contact for {NAME}")
        )
        
        submitted = st.form_submit_button("Save Personal Information", type="primary")
        
        if submitted:
            # Store personal information
            personal_data = {
                "age_range": age_range,
                "living_situation": living_situation,
                "primary_caregiver": primary_caregiver,
                "support_network": support_network,
                "emergency_contact": emergency_contact
            }
            
            st.session_state["personal_assessment"] = personal_data
            st.success("✓ Personal information saved!")
            
            # Mark section as complete
            MCIP.set_completion_status("advisor_prep", "personal", True)
            
            # Log event
            log_event("advisor_prep", "personal_form_submitted", personal_data)

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Financial Overview", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "financial"
            st.rerun()
    with col2:
        if st.button("Medical & Care →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "medical"
            st.rerun()