"""
Advisor Prep - Financial Section

LLM-powered comprehensive financial assessment for advisor review.
Replaces form-based approach with detailed narrative analysis.
"""

import json
from pathlib import Path

import streamlit as st

from core.events import log_event
from core.flags import get_flag_value
from core.mcip import MCIP
from core.name_utils import section_header, personalize
from core.navi import render_navi_panel
from products.advisor_prep.prefill import get_financial_prefill

# Try to import the new LLM advisor summary system
try:
    from ai.advisor_summary_engine import AdvisorSummaryEngine
    LLM_SUMMARY_AVAILABLE = True
except ImportError:
    LLM_SUMMARY_AVAILABLE = False


def render():
    """Render Financial prep section with LLM-generated comprehensive assessment."""

    # Load config for metadata
    config = _load_config()

    # Render Navi panel for contextual guidance
    render_navi_panel(location="product", product_key="advisor_prep", module_config=config)

    # Personalized section header
    st.markdown(f"## {config['icon']} {section_header(config['title'])}")
    st.markdown(f"*{personalize(config['description'])}*")

    # Check if LLM enhancement is enabled
    llm_mode = get_flag_value("FEATURE_ADVISOR_SUMMARY_LLM", "off") if LLM_SUMMARY_AVAILABLE else "off"

    if llm_mode in ["adjust"] and LLM_SUMMARY_AVAILABLE:
        # Render LLM-powered comprehensive financial assessment
        _render_llm_financial_assessment()
    else:
        # Fallback to original form-based approach
        _render_legacy_financial_form(config)

import json
from pathlib import Path

import streamlit as st

from core.events import log_event
from core.flags import get_flag_value
from core.mcip import MCIP
from core.navi import render_navi_panel
from products.advisor_prep.prefill import get_financial_prefill

# Try to import the new LLM advisor summary system
try:
    from ai.advisor_summary_engine import AdvisorSummaryEngine
    LLM_SUMMARY_AVAILABLE = True
except ImportError:
    LLM_SUMMARY_AVAILABLE = False


def render():
    """Render Financial prep section with LLM-generated comprehensive assessment."""

    # Load config for metadata
    config = _load_config()

    # Render Navi
    render_navi_panel(location="product", product_key="advisor_prep", module_config=None)

    st.markdown(f"## {config['icon']} {config['title']}")
    st.markdown(f"*{config['description']}*")

    # Check if LLM enhancement is enabled
    llm_mode = get_flag_value("FEATURE_ADVISOR_SUMMARY_LLM", "off") if LLM_SUMMARY_AVAILABLE else "off"

    if llm_mode in ["assist", "adjust"] and LLM_SUMMARY_AVAILABLE:
        # Render LLM-powered comprehensive financial assessment
        _render_llm_financial_assessment()
    else:
        # Fallback to original form-based approach
        _render_legacy_financial_form()

    # Navigation footer
    st.markdown("---")
    _render_navigation()


def _render_llm_financial_assessment():
    """Render LLM-generated comprehensive financial assessment."""
    
    # Personalized section header
    st.markdown(f"### {section_header('Comprehensive Financial Assessment')}")
    st.markdown(personalize("*This assessment shows what we know about {NAME_POS} financial situation and care funding options.*"))

    try:
        # Generate comprehensive financial assessment
        engine = AdvisorSummaryEngine()
        drawers = engine.generate_all_drawers()
        
        financial_assessment = drawers.get('financial_overview')
        
        if financial_assessment:
            st.markdown("### 💰 Complete Financial Analysis")
            
            # Display the comprehensive financial assessment
            with st.container():
                st.markdown(
                    """
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #007acc;">
                    """ + financial_assessment.replace('\n', '<br>') + """
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            # Mark section as complete with LLM assessment
            _mark_section_complete_with_llm()
            
            st.success("✅ **Comprehensive financial assessment generated for advisor review**")
            
            # Show additional context available
            st.markdown("### 📊 Assessment Coverage")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **✅ Information Captured:**
                - Income sources and stability
                - Asset portfolio analysis  
                - Care funding projections
                - Benefits optimization opportunities
                """)
            
            with col2:
                st.markdown("""
                **📋 For Advisor Follow-up:**
                - Estate planning updates
                - Investment allocation review
                - Tax planning strategies
                - Medicaid planning considerations
                """)
                
        else:
            st.warning("Unable to generate financial assessment. Using standard form.")
            _render_legacy_financial_form()
            
    except Exception as e:
        st.error(f"LLM assessment generation failed: {e}")
        st.info("Falling back to standard financial form.")
        _render_legacy_financial_form()


def _render_legacy_financial_form():
    """Render original form-based financial section as fallback."""
    
    # Get prefill data from Cost Planner / Financial Profile
    prefill_data = get_financial_prefill()

    # Show prefill context if we have prefilled data
    if any(
        [
            prefill_data["monthly_income"],
            prefill_data["total_assets"],
            prefill_data["insurance_coverage"],
            prefill_data["primary_concern"],
        ]
    ):
        st.info(
            "💡 **We've brought over what we already know** from your financial assessments. Please review and update anything that's outdated."
        )

    st.markdown("---")

    # Get current data
    current_data = st.session_state["advisor_prep"]["data"]["financial"]
    config = _load_config()

    # Render fields from JSON config
    form_data = {}

    for field in config["fields"]:
        field_key = field["key"]
        field_label = field["label"]
        field_type = field["type"]
        field_required = field.get("required", False)
        field_help = field.get("help", "")

        # Get prefill value (prioritize saved data, then prefill, then empty)
        if current_data.get(field_key) is not None:
            default_value = current_data.get(field_key)
        else:
            default_value = _get_prefill_value_from_data(field_key, prefill_data)

        # Render appropriate input widget with prefill
        if field_type == "number":
            # Show hint if value was prefilled
            hint = None
            if default_value and not current_data.get(field_key):
                hint = field.get("prefill_hint", "Prefilled from your financial assessments")

            combined_help = f"{field_help}\n\n*{hint}*" if hint else field_help

            value = st.number_input(
                field_label,
                value=float(default_value) if default_value else 0.0,
                min_value=0.0,
                step=100.0,
                help=combined_help,
                format="%.0f",
            )
        elif field_type == "multiselect":
            options = field.get("options", [])
            default = default_value if isinstance(default_value, list) else []

            # Show hint if value was prefilled
            hint = None
            if default and not current_data.get(field_key):
                hint = field.get("prefill_hint", "Prefilled from your profile")

            combined_help = f"{field_help}\n\n*{hint}*" if hint else field_help

            value = st.multiselect(
                field_label, options=options, default=default, help=combined_help
            )
        elif field_type == "select":
            options = field.get("options", [])
            index = 0
            if default_value and default_value in options:
                index = options.index(default_value)

            # Show derivation hint if this is a derived field
            hint = None
            if default_value and field_key == "primary_concern":
                hint = prefill_data.get("primary_concern_reason")

            combined_help = f"{field_help}\n\n*{hint}*" if hint else field_help

            value = st.selectbox(field_label, options=options, index=index, help=combined_help)
        else:
            value = default_value

        form_data[field_key] = value

    # Save button for legacy form
    col_save1, col_save2, col_save3 = st.columns([1, 2, 1])

    with col_save2:
        if st.button("💾 Save Financial Information", type="primary", use_container_width=True):
            _save_section(form_data)

    with col_save3:
        # Show completion status
        sections_complete = st.session_state["advisor_prep"]["sections_complete"]
        if "financial" in sections_complete:
            st.success("✓ Saved")


def _render_navigation():
    """Render navigation controls."""
    col_nav1, col_nav2 = st.columns(2)

    with col_nav1:
        if st.button("← Back to Menu", type="secondary", use_container_width=True):
            st.session_state.pop("advisor_prep_current_section", None)
            st.rerun()

    with col_nav2:
        # Show completion status
        sections_complete = st.session_state["advisor_prep"]["sections_complete"]
        if "financial" in sections_complete:
            st.success("✓ Assessment Complete")


def _mark_section_complete_with_llm():
    """Mark financial section as complete with LLM assessment."""
    # Mark section complete
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "financial" not in sections_complete:
        sections_complete.append("financial")

    # Save LLM-generated status
    if "advisor_prep" not in st.session_state:
        st.session_state["advisor_prep"] = {
            "sections_complete": [],
            "data": {"personal": {}, "financial": {}, "housing": {}, "medical": {}},
        }
    
    st.session_state["advisor_prep"]["data"]["financial"] = {
        "assessment_type": "llm_generated",
        "generated_at": str(st.session_state.get("current_time", "unknown")),
        "comprehensive_report": True
    }

    # Award duck badge (local import to avoid circular dependency)
    try:
        from products.advisor_prep.utils import award_duck_badge
        award_duck_badge("financial")
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
            "section": "financial",
            "assessment_type": "llm_comprehensive",
            "has_llm_report": True,
        },
    )


def _load_config() -> dict:
    """Load financial section JSON config."""
    config_path = Path(__file__).parent.parent / "config" / "financial.json"
    with open(config_path) as f:
        return json.load(f)


def _get_prefill_value_from_data(field_key: str, prefill_data: dict):
    """Map field keys to prefill data.

    Args:
        field_key: Field key from config
        prefill_data: Prefill data from get_financial_prefill()

    Returns:
        Prefill value or None
    """
    mapping = {
        "monthly_income": prefill_data.get("monthly_income"),
        "total_assets": prefill_data.get("total_assets"),
        "insurance_coverage": prefill_data.get("insurance_coverage"),
        "primary_concern": prefill_data.get("primary_concern"),
    }

    return mapping.get(field_key)


def _save_section(form_data: dict):
    """Save financial section data.

    Args:
        form_data: Form field values
    """
    # Save to session state
    st.session_state["advisor_prep"]["data"]["financial"] = form_data

    # Mark section complete
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "financial" not in sections_complete:
        sections_complete.append("financial")

    # Award duck badge (local import to avoid circular dependency)
    try:
        from products.advisor_prep.utils import award_duck_badge

        award_duck_badge("financial")
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
            "section": "financial",
            "has_income": bool(form_data.get("monthly_income")),
            "has_assets": bool(form_data.get("total_assets")),
            "insurance_types": len(form_data.get("insurance_coverage", [])),
        },
    )

    st.success("✓ Financial information saved!")

    # Return to menu after short delay
    import time

    time.sleep(1)
    st.session_state.pop("advisor_prep_current_section", None)
    st.rerun()
