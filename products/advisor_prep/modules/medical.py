"""
Advisor Prep - Medical & Care Section

Data inventory view showing captured medical conditions and care needs for advisor review.
"""

import json
from pathlib import Path

import streamlit as st

import core.flag_manager as flag_manager
from core.events import log_event
from core.mcip import MCIP
from core.name_utils import section_header, personalize
from core.navi import render_navi_panel
from products.advisor_prep.prefill import get_care_needs_prefill


def render():
    """Render Medical & Care Needs data inventory for advisor review."""
    _render_data_inventory()


def _render_data_inventory():
    """Display captured medical and care information in inventory format."""
    
    # Navigation buttons at top
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← About Person", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "personal"
            st.rerun()
    with col2:
        if st.button("Housing Preferences →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "housing"
            st.rerun()
    with col3:
        if st.button("Financial Overview →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "financial"
            st.rerun()

    # Section header
    st.markdown(f"### {section_header('Medical & Care Data Inventory')}")
    st.markdown(personalize("*Review what we know about {NAME_POS} medical conditions and care needs.*"))

    # Get medical data from various sources
    medical_session_data = st.session_state.get("medical_assessment", {})
    advisor_prep_data = st.session_state.get("advisor_prep", {}).get("data", {}).get("medical", {})
    
    # Get current chronic conditions from flag manager
    chronic_condition_records = flag_manager.get_chronic_conditions()
    chronic_conditions = [rec["code"] for rec in chronic_condition_records]
    
    # Get active care flags
    current_flags = flag_manager.get_active()
    care_flag_keys = [
        "memory_support", "mobility_limited", "behavioral_concerns", 
        "medication_management", "diabetic_care", "wound_care", 
        "oxygen_therapy", "hospice_palliative"
    ]
    active_care_flags = [flag for flag in current_flags if flag in care_flag_keys]
    
    # Load conditions registry for display names
    conditions = _load_conditions_registry()
    
    # Display chronic conditions
    if chronic_conditions:
        condition_names = []
        for code in chronic_conditions:
            condition = next((c for c in conditions if c["code"] == code), None)
            if condition:
                condition_names.append(f"{condition['label']} ({condition['category']})")
            else:
                condition_names.append(code)
        conditions_display = ", ".join(condition_names)
    else:
        conditions_display = "Not captured"
    
    _display_data_section("🏥 Medical Conditions", [
        ("Chronic Conditions", conditions_display),
        ("Conditions Count", f"{len(chronic_conditions)} conditions" if chronic_conditions else "No conditions"),
    ])
    
    # Display care needs/flags
    if active_care_flags:
        # Map flag keys to readable names
        flag_names = {
            "memory_support": "Memory Support Needed",
            "mobility_limited": "Mobility Limitations", 
            "behavioral_concerns": "Behavioral Concerns",
            "medication_management": "Medication Management",
            "diabetic_care": "Diabetic Care",
            "wound_care": "Wound Care",
            "oxygen_therapy": "Oxygen Therapy",
            "hospice_palliative": "Hospice/Palliative Care"
        }
        care_needs_display = ", ".join([flag_names.get(flag, flag) for flag in active_care_flags])
    else:
        care_needs_display = "Not captured"
    
    _display_data_section("🩺 Care Needs", [
        ("Active Care Flags", care_needs_display),
        ("Care Needs Count", f"{len(active_care_flags)} care needs" if active_care_flags else "No special care needs"),
    ])
    
    # Display additional notes
    medical_notes = medical_session_data.get("medical_notes") or advisor_prep_data.get("medical_notes", "")
    
    _display_data_section("📝 Additional Information", [
        ("Medical Notes", medical_notes if medical_notes else "Not captured"),
    ])
    
    # Show completion status
    if chronic_conditions or active_care_flags or medical_notes:
        st.success("✓ Medical information captured")
        _mark_section_complete()
    else:
        st.info("No medical data captured yet.")

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
    """Mark medical section as complete."""
    # Initialize advisor_prep structure if needed
    if "advisor_prep" not in st.session_state:
        st.session_state["advisor_prep"] = {
            "sections_complete": [],
            "data": {"personal": {}, "financial": {}, "housing": {}, "medical": {}},
        }
    
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "medical" not in sections_complete:
        sections_complete.append("medical")
        
        # Update MCIP contract with prep progress
        appt = MCIP.get_advisor_appointment()
        if appt:
            appt.prep_sections_complete = sections_complete
            appt.prep_progress = len(sections_complete) * 25
            MCIP.set_advisor_appointment(appt)

        # Log completion
        log_event("advisor_prep", "medical_section_complete", {"method": "data_inventory"})


def _load_conditions_registry() -> list:
    """Load Conditions Registry JSON.

    Returns:
        List of condition dicts from registry
    """
    # Path is relative to workspace root
    registry_path = (
        Path(__file__).parent.parent.parent.parent / "config" / "conditions" / "conditions.json"
    )
    try:
        with open(registry_path) as f:
            data = json.load(f)
            return data.get("conditions", [])
    except FileNotFoundError:
        return []
