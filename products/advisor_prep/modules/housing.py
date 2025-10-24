"""
Advisor Prep - Housing Preferences Section

Data inventory view showing captured housing preferences for advisor review.
"""

import streamlit as st

from core.events import log_event
from core.mcip import MCIP
from core.name_utils import section_header, personalize
from core.navi import render_navi_panel


def render():
    """Render Housing Preferences data inventory for advisor review."""
    _render_data_inventory()


def _render_data_inventory():
    """Display captured housing preferences in inventory format."""
    
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

    # Section header
    st.markdown(f"### {section_header('Housing Preferences Data Inventory')}")
    st.markdown(personalize("*Review what we know about {NAME_POS} housing preferences and transition plans.*"))

    # Get housing data from session
    housing_data = st.session_state.get("housing_assessment", {})
    advisor_prep_data = st.session_state.get("advisor_prep", {}).get("data", {}).get("housing", {})
    gcp_data = st.session_state.get("gcp_care_recommendation", {})
    
    # Combine data sources
    all_housing_data = {**housing_data, **advisor_prep_data}
    
    # Current housing situation
    _display_data_section("🏠 Current Housing", [
        ("Current Housing Type", all_housing_data.get("current_housing", "Not captured")),
        ("Living Situation", st.session_state.get("living_situation", "Not captured")),
    ])
    
    # Care preferences from GCP
    care_recommendation = gcp_data.get("recommendation", "Not captured") if gcp_data else "Not captured"
    
    _display_data_section("🔧 Care Setting Preferences", [
        ("Recommended Care Level", care_recommendation),
        ("Preferred Care Setting", all_housing_data.get("care_preference", "Not captured")),
    ])
    
    # Location and timing
    _display_data_section("📍 Location & Timeline", [
        ("Preferred Location", all_housing_data.get("location_preference", "Not captured")),
        ("Move Timeline", all_housing_data.get("move_timeline", "Not captured")),
    ])
    
    # Housing priorities
    priorities = all_housing_data.get("housing_priorities", [])
    if priorities:
        priorities_display = ", ".join(priorities)
    else:
        priorities_display = "Not captured"
    
    _display_data_section("⭐ Priorities", [
        ("Housing Priorities", priorities_display),
    ])
    
    # Show completion status
    if all_housing_data or gcp_data:
        st.success("✓ Housing preferences captured")
        _mark_section_complete()
    else:
        st.info("No housing data captured yet.")

    # Render Navi panel for contextual guidance
    render_navi_panel()


def _display_data_section(title: str, data_items: list):
    """Display a section of data inventory.
    
    Args:
        title: Section title
        data_items: List of (field_name, value) tuples
    """
    st.markdown(f"#### {title}")
    
    for field_name, value in data_items:
        if value and value != "Not captured" and value != []:
            status = "✅ Captured"
            value_display = f"**{value}**"
        else:
            status = "❌ Not Captured"
            value_display = "*No data*"
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.write(field_name)
        with col2:
            st.write(status)
        with col3:
            st.write(value_display)
    
    st.markdown("---")


def _mark_section_complete():
    """Mark housing section as complete."""
    # Initialize advisor_prep structure if needed
    if "advisor_prep" not in st.session_state:
        st.session_state["advisor_prep"] = {
            "sections_complete": [],
            "data": {"personal": {}, "financial": {}, "housing": {}, "medical": {}},
        }
    
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "housing" not in sections_complete:
        sections_complete.append("housing")
        
        # Update MCIP contract with prep progress
        appt = MCIP.get_advisor_appointment()
        if appt:
            appt.prep_sections_complete = sections_complete
            appt.prep_progress = len(sections_complete) * 25
            MCIP.set_advisor_appointment(appt)

        # Log completion
        log_event("advisor_prep", "housing_section_complete", {"method": "data_inventory"})


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
