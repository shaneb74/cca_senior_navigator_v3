"""
Advisor Prep - Housing Preferences Section

LLM-powered comprehensive housing preferences assessment for advisor review.
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
    """Render Housing Preferences prep section with LLM-generated comprehensive assessment."""

    # Get feature flag
    feature_flag = get_flag_value("FEATURE_ADVISOR_SUMMARY_LLM", "off")
    
    # Check if LLM enhancement is active and available
    if feature_flag in ["adjust"] and LLM_SUMMARY_AVAILABLE:
        _render_llm_assessment()
    else:
        _render_legacy_form()


def _render_llm_assessment():
    """Render LLM-generated comprehensive housing preferences assessment."""
    
    # Progress tracking
    container = st.container()
    with container:
        st.success("✓ Housing Preferences section complete - comprehensive assessment available for advisor review")
    
    # Navigation buttons at top
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Medical & Care", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "medical"
            st.rerun()
    with col2:
        if st.button("About Person →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "personal"
            st.rerun()
    with col3:
        if st.button("Financial Overview →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "financial"
            st.rerun()

    # Personalized section header
    st.markdown(f"### {section_header('Housing Preferences Assessment')}")
    st.markdown(personalize("*This assessment shows {NAME_POS} housing preferences, transition readiness, and care setting options.*"))

    try:
        if LLM_SUMMARY_AVAILABLE:
            engine = AdvisorSummaryEngine()
            context = engine.build_advisor_context_from_session()
            assessment = engine.generate_drawer_narrative("housing_preferences", context)
            
            if assessment and assessment.strip():
                st.markdown(f"#### {section_header('Housing & Transition Summary')}")
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
    log_event("advisor_prep", "housing_section_complete", {"method": "llm_assessment"})


def _render_legacy_form():
    """Render legacy form-based housing section."""
    
    # Personalized section header
    st.markdown(f"### {section_header('Housing Preferences')}")
    st.markdown(personalize("*Please provide information about {NAME_POS} housing preferences and care needs.*"))
    
    # Basic housing form
    with st.form("housing_form"):
        current_housing = st.selectbox(
            personalize("Current Housing Type for {NAME}"),
            ["Single-family home", "Apartment/Condo", "Senior housing", "Assisted living", "Memory care", "Other"]
        )
        
        care_preference = st.selectbox(
            personalize("Preferred Care Setting for {NAME}"),
            ["Age in place at home", "Senior housing community", "Assisted living", "Memory care", "Nursing home", "Not sure yet"]
        )
        
        location_preference = st.text_input(
            personalize("Preferred Location for {NAME}"),
            help=personalize("City, state, or 'near family' for {NAME_POS} preferred location")
        )
        
        move_timeline = st.selectbox(
            personalize("Timeline for {NAME_POS} Move"),
            ["Immediately", "Within 3 months", "Within 6 months", "Within 1 year", "More than 1 year", "Not planning to move"]
        )
        
        housing_priorities = st.multiselect(
            personalize("Housing Priorities for {NAME}"),
            ["Cost", "Location", "Quality of care", "Social activities", "Medical services", "Pet-friendly", "Family proximity", "Safety/security"]
        )
        
        submitted = st.form_submit_button("Save Housing Preferences", type="primary")
        
        if submitted:
            # Store housing information
            housing_data = {
                "current_housing": current_housing,
                "care_preference": care_preference,
                "location_preference": location_preference,
                "move_timeline": move_timeline,
                "housing_priorities": housing_priorities
            }
            
            st.session_state["housing_assessment"] = housing_data
            st.success("✓ Housing preferences saved!")
            
            # Mark section as complete
            MCIP.set_completion_status("advisor_prep", "housing", True)
            
            # Log event
            log_event("advisor_prep", "housing_form_submitted", housing_data)

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Medical & Care", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "medical"
            st.rerun()
    with col2:
        if st.button("Financial Overview →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "financial"
            st.rerun()
