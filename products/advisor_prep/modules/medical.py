"""
Advisor Prep - Medical & Care Section

LLM-powered comprehensive medical and care assessment for advisor review.
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
    """Render Medical & Care Needs prep section with LLM-generated comprehensive assessment."""

    # Get feature flag
    feature_flag = get_flag_value("FEATURE_ADVISOR_SUMMARY_LLM", "off")
    
    # Check if LLM enhancement is active and available
    if feature_flag in ["adjust"] and LLM_SUMMARY_AVAILABLE:
        _render_llm_assessment()
    else:
        _render_legacy_form()


def _render_llm_assessment():
    """Render LLM-generated comprehensive medical and care assessment."""
    
    # Progress tracking
    container = st.container()
    with container:
        st.success("✓ Medical & Care section complete - comprehensive assessment available for advisor review")
    
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

    # Personalized section header
    st.markdown(f"### {section_header('Medical & Care Needs Assessment')}")
    st.markdown(personalize("*This assessment shows what we know about {NAME_POS} medical conditions, care needs, and functional status.*"))

    try:
        if LLM_SUMMARY_AVAILABLE:
            engine = AdvisorSummaryEngine()
            context = engine.build_advisor_context_from_session()
            assessment = engine.generate_drawer_narrative("medical_care", context)
            
            if assessment and assessment.strip():
                st.markdown(f"#### {section_header('Medical & Care Summary')}")
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
    log_event("advisor_prep", "medical_section_complete", {"method": "llm_assessment"})


def _render_legacy_form():
    """Render legacy form-based medical section."""
    
    # Personalized section header
    st.markdown(f"### {section_header('Medical & Care Information')}")
    st.markdown(personalize("*Please provide information about {NAME_POS} medical conditions and care needs.*"))
    
    # Basic medical form
    with st.form("medical_form"):
        primary_conditions = st.text_area(
            personalize("Primary Medical Conditions for {NAME}"),
            help=personalize("List {NAME_POS} main health conditions")
        )
        
        current_medications = st.text_area(
            personalize("Current Medications for {NAME}"),
            help=personalize("List {NAME_POS} current medications")
        )
        
        care_level = st.selectbox(
            personalize("Current Care Level for {NAME}"),
            ["Independent", "Some assistance needed", "Significant assistance needed", "Full care required"]
        )
        
        mobility_status = st.selectbox(
            personalize("Mobility Status for {NAME}"),
            ["Fully mobile", "Uses walking aid", "Uses wheelchair", "Bedbound"]
        )
        
        cognitive_status = st.selectbox(
            personalize("Cognitive Status for {NAME}"),
            ["No concerns", "Mild memory issues", "Moderate cognitive decline", "Significant cognitive impairment"]
        )
        
        submitted = st.form_submit_button("Save Medical Information", type="primary")
        
        if submitted:
            # Store medical information
            medical_data = {
                "primary_conditions": primary_conditions,
                "current_medications": current_medications,
                "care_level": care_level,
                "mobility_status": mobility_status,
                "cognitive_status": cognitive_status
            }
            
            st.session_state["medical_assessment"] = medical_data
            st.success("✓ Medical information saved!")
            
            # Mark section as complete
            MCIP.set_completion_status("advisor_prep", "medical", True)
            
            # Log event
            log_event("advisor_prep", "medical_form_submitted", medical_data)

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← About Person", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "personal"
            st.rerun()
    with col2:
        if st.button("Housing Preferences →", use_container_width=True):
            st.session_state["advisor_prep_current_section"] = "housing"
            st.rerun()

import json
from pathlib import Path

import streamlit as st

import core.flag_manager as flag_manager
from core.events import log_event
from core.flags import get_flag_value
from core.mcip import MCIP
from core.navi import render_navi_panel
from products.advisor_prep.prefill import get_care_needs_prefill

# Try to import the new LLM advisor summary system
try:
    from ai.advisor_summary_engine import AdvisorSummaryEngine
    LLM_SUMMARY_AVAILABLE = True
except ImportError:
    LLM_SUMMARY_AVAILABLE = False


def render():
    """Render Medical & Care Needs prep section with LLM-generated comprehensive assessment."""

    # Load config for metadata
    config = _load_config()

    # Render Navi
    render_navi_panel(location="product", product_key="advisor_prep", module_config=None)

    st.markdown(f"## {config['icon']} {config['title']}")
    st.markdown(f"*{config['description']}*")

    # Check if LLM enhancement is enabled
    llm_mode = get_flag_value("FEATURE_ADVISOR_SUMMARY_LLM", "off") if LLM_SUMMARY_AVAILABLE else "off"

    if llm_mode in ["assist", "adjust"] and LLM_SUMMARY_AVAILABLE:
        # Render LLM-powered comprehensive medical assessment
        _render_llm_medical_assessment()
    else:
        # Fallback to original form-based approach
        _render_legacy_medical_form()

    # Navigation footer
    st.markdown("---")
    _render_navigation()


def _render_llm_medical_assessment():
    """Render LLM-generated comprehensive medical assessment."""
    
    st.markdown("### Comprehensive Medical & Care Needs Assessment")
    st.markdown("*This assessment shows health conditions, care requirements, and coordination needs.*")
    
    try:
        # Generate assessment using session state data
        engine = AdvisorSummaryEngine()
        context = engine.build_advisor_context_from_session()
        
        if context:
            assessment = engine.generate_drawer_narrative("medical_care", context)
            
            if assessment:
                # Display the assessment in a styled container
                st.markdown("#### Medical & Care Summary")
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #dc3545;">
                {assessment.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
                
                # Mark section as complete automatically with LLM assessment
                _mark_medical_complete()
                
                st.success("✅ Medical assessment complete using available session data")
            else:
                st.warning("Unable to generate assessment. Using fallback form.")
                _render_legacy_medical_form()
        else:
            st.info("Insufficient data for comprehensive assessment. Please complete other sections first.")
            _render_legacy_medical_form()
            
    except Exception as e:
        st.error(f"Assessment generation failed: {e}")
        st.warning("Using fallback form interface.")
        _render_legacy_medical_form()


def _render_legacy_medical_form():
    """Render original form-based medical interface."""
    
    # Load config
    config = _load_config()
    
    # Get care needs prefill
    prefill_data = get_care_needs_prefill()
    
    st.markdown("---")
    render_navi_panel(location="product", product_key="advisor_prep", module_config=None)

    st.markdown(f"## {config['icon']} {config['title']}")
    st.markdown(f"*{config['description']}*")

    # Show prefill context if available
    if prefill_data and prefill_data.get("chronic_conditions"):
        st.info(
            "💡 We've brought over some information from your Guided Care Plan and Cost Planner. Feel free to edit anything that's changed."
        )

    st.markdown("---")

    # Load Conditions Registry
    conditions = _load_conditions_registry()

    # Get current state from Flag Manager
    # get_active() returns List[str] of flag IDs
    # get_chronic_conditions() returns List[Dict] of condition records
    current_flags = flag_manager.get_active()
    chronic_condition_records = flag_manager.get_chronic_conditions()
    current_conditions = [rec["code"] for rec in chronic_condition_records]

    # Section 1: Chronic Conditions (Conditions Registry)
    st.markdown("### Chronic Health Conditions")
    st.caption(
        "Select any ongoing health conditions. This information helps your advisor recommend appropriate care options and resources."
    )

    # Get saved data from session or prefill
    saved_data = st.session_state["advisor_prep"]["data"]["medical"]
    current_conditions = saved_data.get("chronic_conditions") or prefill_data.get(
        "chronic_conditions", []
    )

    # Multi-select for conditions
    selected_conditions = st.multiselect(
        "Select Chronic Conditions",
        options=[c["code"] for c in conditions],
        format_func=lambda code: _format_condition(code, conditions),
        default=current_conditions,
        help="These conditions will be shared with your advisor",
    )

    # Section 2: Care Flags (Flag Toggles)
    st.markdown("---")
    st.markdown("### Additional Care Needs")
    st.caption("Select any additional care needs that apply to your situation.")

    # Get care flags from config
    care_flags_config = next(f for f in config["fields"] if f["key"] == "care_flags")
    care_flags = care_flags_config["flags"]

    # Get care needs prefill (8 toggles with enabled state and reasons)
    care_needs = prefill_data.get("care_needs", {})

    selected_flags = []

    # Create grid layout for flags (2 columns)
    cols = st.columns(2)

    for idx, flag in enumerate(care_flags):
        with cols[idx % 2]:
            flag_key = flag["key"]

            # Get saved value or prefill value
            saved_flags = saved_data.get("care_flags", [])
            if saved_flags:
                # Use saved value
                is_active = flag_key in saved_flags
                help_text = flag.get("help", "")
            else:
                # Use prefill value with provenance
                care_need = care_needs.get(flag_key, {})
                is_active = care_need.get("enabled", False)
                reason = care_need.get("reason", "")
                help_text = f"💡 {reason}" if reason else flag.get("help", "")

            # Render checkbox
            checkbox_value = st.checkbox(
                f"{flag['icon']} {flag['label']}",
                value=is_active,
                key=f"flag_{flag_key}",
                help=help_text,
            )

            if checkbox_value:
                selected_flags.append(flag_key)

    # Section 3: Additional Medical Notes
    st.markdown("---")
    st.markdown("### Additional Medical Information")

    current_notes = st.session_state["advisor_prep"]["data"]["medical"].get("medical_notes", "")

    medical_notes = st.text_area(
        "Additional Notes (Optional)",
        value=current_notes,
        placeholder="Any other health information your advisor should know (recent hospitalizations, upcoming surgeries, special equipment needs, etc.)",
        max_chars=500,
        help="Optional: Share any additional medical context",
    )

    # Save button
    st.markdown("---")

    col_save1, col_save2, col_save3 = st.columns([1, 2, 1])

    with col_save1:
        if st.button("← Back to Menu", type="secondary", use_container_width=True):
            st.session_state.pop("advisor_prep_current_section", None)
            st.rerun()

    with col_save2:
        if st.button("💾 Save Medical Information", type="primary", use_container_width=True):
            _save_medical_section(selected_conditions, selected_flags, medical_notes)

    with col_save3:
        # Show completion status
        sections_complete = st.session_state["advisor_prep"]["sections_complete"]
        if "medical" in sections_complete:
            st.success("✓ Saved")


def _render_navigation():
    """Render navigation buttons."""
    
    col_save1, col_save2, col_save3 = st.columns([1, 2, 1])

    with col_save1:
        if st.button("← Back to Menu", type="secondary", use_container_width=True):
            st.session_state.pop("advisor_prep_current_section", None)
            st.rerun()

    with col_save3:
        # Show completion status
        sections_complete = st.session_state["advisor_prep"]["sections_complete"]
        if "medical" in sections_complete:
            st.success("✓ Saved")


def _mark_medical_complete():
    """Mark medical section as complete without form data."""
    
    # Mark section complete
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "medical" not in sections_complete:
        sections_complete.append("medical")

    # Award duck badge (local import to avoid circular dependency)
    try:
        from products.advisor_prep.utils import award_duck_badge
        award_duck_badge("medical")
    except ImportError:
        pass  # Duck badges not available

    # Update MCIP contract with prep progress
    appt = MCIP.get_advisor_appointment()
    if appt:
        appt.prep_sections_complete = sections_complete
        appt.prep_progress = len(sections_complete) * 25
        MCIP.set_advisor_appointment(appt)

    # Update MCIP Waiting Room status based on progress
    if len(sections_complete) == 0:
        MCIP.update_advisor_prep_status("not_started")
    elif len(sections_complete) < 4:
        MCIP.update_advisor_prep_status("in_progress")
    else:
        MCIP.update_advisor_prep_status("complete")

    # Log event
    log_event(
        "advisor_prep.section.completed",
        {"section": "medical", "assessment_type": "llm_generated"},
    )


def _load_config() -> dict:
    """Load medical section JSON config."""
    config_path = Path(__file__).parent.parent / "config" / "medical.json"
    with open(config_path) as f:
        return json.load(f)


def _load_conditions_registry() -> list:
    """Load Conditions Registry JSON.

    Returns:
        List of condition dicts from registry
    """
    # Path is relative to workspace root
    registry_path = (
        Path(__file__).parent.parent.parent.parent / "config" / "conditions" / "conditions.json"
    )
    with open(registry_path) as f:
        data = json.load(f)
        return data.get("conditions", [])


def _format_condition(code: str, conditions: list) -> str:
    """Format condition for display in multiselect.

    Args:
        code: Condition code
        conditions: List of condition dicts from registry

    Returns:
        Formatted label
    """
    condition = next((c for c in conditions if c["code"] == code), None)
    if condition:
        return f"{condition['label']} ({condition['category']})"
    return code


def _save_medical_section(selected_conditions: list, selected_flags: list, medical_notes: str):
    """Save medical section data via Flag Manager.

    Args:
        selected_conditions: List of chronic condition codes
        selected_flags: List of care flag keys
        medical_notes: Additional medical notes
    """
    # Update chronic conditions via Flag Manager
    # This automatically applies auto-flag rules (≥1 → chronic_present, ≥2 → chronic_conditions)
    flag_manager.update_chronic_conditions(selected_conditions, source="advisor_prep.medical")

    # Update care flags
    # Get current active flags (returns List[str])
    current_flags = set(flag_manager.get_active())

    # Determine which flags to activate/deactivate
    selected_flags_set = set(selected_flags)
    flags_to_activate = selected_flags_set - current_flags
    flags_to_deactivate = current_flags - selected_flags_set

    # Only deactivate care flags (not system flags like chronic_present, chronic_conditions)
    care_flag_keys = [
        "memory_support",
        "mobility_limited",
        "behavioral_concerns",
        "medication_management",
        "diabetic_care",
        "wound_care",
        "oxygen_therapy",
        "hospice_palliative",
    ]
    flags_to_deactivate = flags_to_deactivate.intersection(care_flag_keys)

    # Apply changes
    for flag_key in flags_to_activate:
        flag_manager.activate(flag_key, source="advisor_prep.medical")

    for flag_key in flags_to_deactivate:
        flag_manager.deactivate(flag_key, source="advisor_prep.medical")

    # Save medical notes to session state
    st.session_state["advisor_prep"]["data"]["medical"] = {
        "chronic_conditions": selected_conditions,
        "care_flags": selected_flags,
        "medical_notes": medical_notes,
    }

    # Mark section complete
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "medical" not in sections_complete:
        sections_complete.append("medical")

    # Award duck badge (local import to avoid circular dependency)
    try:
        from products.advisor_prep.utils import award_duck_badge

        award_duck_badge("medical")
    except ImportError:
        pass  # Duck badges not available

    # Update MCIP contract with prep progress
    appt = MCIP.get_advisor_appointment()
    if appt:
        appt.prep_sections_complete = sections_complete
        appt.prep_progress = len(sections_complete) * 25
        MCIP.set_advisor_appointment(appt)

    # Update MCIP Waiting Room status based on progress
    if len(sections_complete) == 0:
        MCIP.update_advisor_prep_status("not_started")
    elif len(sections_complete) < 4:
        MCIP.update_advisor_prep_status("in_progress")
    else:
        MCIP.update_advisor_prep_status("complete")

    # Log event
    log_event(
        "advisor_prep.section.completed",
        {
            "section": "medical",
            "conditions_count": len(selected_conditions),
            "flags_count": len(selected_flags),
            "has_notes": bool(medical_notes),
        },
    )

    st.success("✓ Medical information saved!")

    # Return to menu after short delay
    import time

    time.sleep(1)
    st.session_state.pop("advisor_prep_current_section", None)
    st.rerun()
