"""
Advisor Prep - Financial Section

JSON-driven generic form renderer for financial information.
Includes prefill logic from Cost Planner and Financial Profile.
"""

import json
import streamlit as st
from pathlib import Path
from products.advisor_prep.utils import award_duck_badge

from core.mcip import MCIP
from core.events import log_event
from core.navi import render_navi_panel
from products.advisor_prep.prefill import get_financial_prefill


def render():
    """Render Financial prep section."""
    
    # Load config
    config = _load_config()
    
    # Get prefill data from Cost Planner / Financial Profile
    prefill_data = get_financial_prefill()
    
    # Render Navi (pass None for module_config since this isn't a stepped module)
    render_navi_panel(
        location="product",
        product_key="advisor_prep",
        module_config=None
    )
    
    st.markdown(f"## {config['icon']} {config['title']}")
    st.markdown(f"*{config['description']}*")
    
    # Show prefill context if we have prefilled data
    if any([prefill_data["monthly_income"], prefill_data["total_assets"], 
            prefill_data["insurance_coverage"], prefill_data["primary_concern"]]):
        st.info("💡 **We've brought over what we already know** from your financial assessments. Please review and update anything that's outdated.")
    
    st.markdown("---")
    
    # Get current data
    current_data = st.session_state["advisor_prep"]["data"]["financial"]
    
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
                format="%.0f"
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
                field_label,
                options=options,
                default=default,
                help=combined_help
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
            
            value = st.selectbox(
                field_label,
                options=options,
                index=index,
                help=combined_help
            )
        else:
            value = default_value
        
        form_data[field_key] = value
    
    # Save button
    st.markdown("---")
    
    col_save1, col_save2, col_save3 = st.columns([1, 2, 1])
    
    with col_save1:
        if st.button("← Back to Menu", type="secondary", use_container_width=True):
            st.session_state.pop("advisor_prep_current_section", None)
            st.rerun()
    
    with col_save2:
        if st.button("💾 Save Financial Information", type="primary", use_container_width=True):
            _save_section(form_data)
    
    with col_save3:
        # Show completion status
        sections_complete = st.session_state["advisor_prep"]["sections_complete"]
        if "financial" in sections_complete:
            st.success("✓ Saved")


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
        "primary_concern": prefill_data.get("primary_concern")
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
    
    # Award duck badge
    award_duck_badge("financial")
    
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
    log_event("advisor_prep.section.completed", {
        "section": "financial",
        "has_income": bool(form_data.get("monthly_income")),
        "has_assets": bool(form_data.get("total_assets")),
        "insurance_types": len(form_data.get("insurance_coverage", []))
    })
    
    st.success("✓ Financial information saved!")
    
    # Return to menu after short delay
    import time
    time.sleep(1)
    st.session_state.pop("advisor_prep_current_section", None)
    st.rerun()
