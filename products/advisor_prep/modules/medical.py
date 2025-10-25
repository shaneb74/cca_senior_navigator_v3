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
    """Display all capturable medical and care information fields."""
    
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
    st.markdown(f"### {section_header('Medical & Care - Capturable Fields')}")
    st.markdown(personalize("*These are all the medical fields the app can capture for {NAME}.*"))

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
    
    # Load conditions registry for display
    conditions = _load_conditions_registry()
    
    # Show all 15 available chronic conditions
    condition_options = []
    for condition in conditions:
        condition_options.append(f"{condition['label']} ({condition['category']})")
    
    # Display current chronic conditions vs available
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
    
    _display_data_section("🏥 Chronic Health Conditions", [
        ("Available Conditions", conditions_display, condition_options),
        ("Conditions Count", f"{len(chronic_conditions)} conditions" if chronic_conditions else "0 conditions", 
         ["Up to 15 conditions available"]),
    ])
    
    # Show all 8 available care flags
    care_flag_labels = {
        "memory_support": "🧠 Memory Support",
        "mobility_limited": "🦽 Mobility Assistance", 
        "behavioral_concerns": "🤝 Behavioral Support",
        "medication_management": "💊 Medication Management",
        "diabetic_care": "🩸 Diabetic Care",
        "wound_care": "🩹 Wound Care",
        "oxygen_therapy": "🫁 Oxygen Therapy",
        "hospice_palliative": "🕊️ Hospice/Palliative Care"
    }
    
    if active_care_flags:
        care_needs_display = ", ".join([care_flag_labels.get(flag, flag) for flag in active_care_flags])
    else:
        care_needs_display = "Not captured"
    
    available_care_flags = list(care_flag_labels.values())
    
    _display_data_section("🩺 Care Needs & Flags", [
        ("Available Care Flags", care_needs_display, available_care_flags),
        ("Care Needs Count", f"{len(active_care_flags)} care needs" if active_care_flags else "0 care needs", 
         ["Up to 8 care flags available"]),
    ])
    
    # Display additional notes field
    medical_notes = medical_session_data.get("medical_notes") or advisor_prep_data.get("medical_notes", "")
    
    _display_data_section("📝 Additional Information", [
        ("Medical Notes", medical_notes if medical_notes else "Not captured", 
         ["Free text field (max 500 characters)"]),
    ])
    
    # Show completion status
    if chronic_conditions or active_care_flags or medical_notes:
        st.success("✓ Some medical information captured")
        _mark_section_complete()
    else:
        st.info("No medical data captured yet.")

    # Show what's available summary
    st.markdown("---")
    st.markdown("#### 📋 Medical Data Capacity")
    st.info(f"""
    **Available for capture:**
    - **Chronic Conditions:** 15 conditions across 6 categories (cardiovascular, respiratory, neurological, etc.)
    - **Care Flags:** 8 specialized care needs with auto-flagging
    - **Medical Notes:** Free text field for additional context
    - **Auto-flagging:** System automatically sets flags based on condition counts
    """)

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
                if len(options) > 5:
                    options_display = f"{len(options)} options available"
                else:
                    options_display = f"Options: {', '.join(options)}"
            else:
                options_display = "Type: " + str(options[0]) if options else "Free text"
        else:
            field_name, value = item
            options_display = "Available"
        
        if value and value != "Not captured" and value != [] and "0 conditions" not in str(value) and "0 care needs" not in str(value):
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
            if value and value != "Not captured" and value != [] and "0 conditions" not in str(value) and "0 care needs" not in str(value):
                st.write(value_display)
            else:
                st.caption(options_display)
    
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
        log_event("advisor_prep.medical_section_complete", {"method": "data_inventory"})


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
