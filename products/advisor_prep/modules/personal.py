"""
Advisor Prep - Personal Information Section

Data inventory view showing captured personal information for advisor review.
"""

import streamlit as st

from core.events import log_event
from core.mcip import MCIP
from core.name_utils import section_header, personalize
from core.navi import render_navi_panel


def render():
    """Render Personal Information data inventory for advisor review."""
    _render_data_inventory()


def _render_data_inventory():
    """Display all capturable personal information fields."""
    
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

    # Section header
    st.markdown(f"### {section_header('Personal Information - Capturable Fields')}")
    st.markdown(personalize("*These are all the personal fields the app can capture for {NAME}.*"))

    # Get personal data from session to show current values
    personal_data = st.session_state.get("personal_assessment", {})
    advisor_prep_data = st.session_state.get("advisor_prep", {}).get("data", {}).get("personal", {})
    all_personal_data = {**personal_data, **advisor_prep_data}
    
    # Core personal information fields (from legacy form)
    _display_data_section("👤 Basic Demographics", [
        ("Person Name", st.session_state.get("person_name", "Not captured")),
        ("Planning For", st.session_state.get("planning_for_name", "Not captured")),
        ("Age Range", all_personal_data.get("age_range", "Not captured"), ["Under 65", "65-74", "75-84", "85-94", "95+"]),
    ])
    
    # Living situation fields
    _display_data_section("🏠 Living Situation", [
        ("Current Living Situation", all_personal_data.get("living_situation", "Not captured"), 
         ["Lives alone", "Lives with spouse/partner", "Lives with family", "Lives with caregiver", "Other"]),
        ("Primary Caregiver", all_personal_data.get("primary_caregiver", "Not captured"),
         ["Self-sufficient", "Spouse/Partner", "Adult child", "Other family member", "Professional caregiver", "Multiple caregivers"]),
    ])
    
    # Support network fields
    support_network = all_personal_data.get("support_network", [])
    support_display = ", ".join(support_network) if support_network else "Not captured"
    
    _display_data_section("👥 Support Network", [
        ("Support Types", support_display, ["Family nearby", "Friends in area", "Religious community", "Neighbors", "Professional services", "Limited support"]),
        ("Emergency Contact", all_personal_data.get("emergency_contact", "Not captured"), ["Free text field"]),
    ])
    
    # Show completion status
    if all_personal_data:
        st.success("✓ Some personal information captured")
        _mark_section_complete()
    else:
        st.info("No personal data captured yet.")

    # Render Navi panel for contextual guidance
    render_navi_panel()


def _display_data_section(title: str, data_items: list):
    """Display a section of capturable fields.
    
    Args:
        title: Section title
        data_items: List of (field_name, current_value, options) tuples
    """
    st.markdown(f"#### {title}")
    
    for item in data_items:
        if len(item) == 3:
            field_name, value, options = item
            if isinstance(options, list) and len(options) > 1:
                options_display = f"Options: {', '.join(options)}"
            else:
                options_display = "Type: " + str(options[0]) if options else "Free text"
        else:
            field_name, value = item
            options_display = "Available"
        
        if value and value != "Not captured":
            status = "✅ Captured"
            value_display = f"**{value}**"
        else:
            status = "❌ Not Captured"
            value_display = "*Available for capture*"
        
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1:
            st.write(f"**{field_name}**")
        with col2:
            st.write(status)
        with col3:
            if value and value != "Not captured":
                st.write(value_display)
            else:
                st.caption(options_display)
    
    st.markdown("---")


def _mark_section_complete():
    """Mark personal section as complete."""
    # Initialize advisor_prep structure if needed
    if "advisor_prep" not in st.session_state:
        st.session_state["advisor_prep"] = {
            "sections_complete": [],
            "data": {"personal": {}, "financial": {}, "housing": {}, "medical": {}},
        }
    
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "personal" not in sections_complete:
        sections_complete.append("personal")
        
        # Update MCIP contract with prep progress
        appt = MCIP.get_advisor_appointment()
        if appt:
            appt.prep_sections_complete = sections_complete
            appt.prep_progress = len(sections_complete) * 25
            MCIP.set_advisor_appointment(appt)

        # Log completion
        log_event("advisor_prep.personal_section_complete", {"method": "data_inventory"})


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