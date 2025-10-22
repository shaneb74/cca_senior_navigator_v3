"""
Advisor Prep - Housing Section

JSON-driven generic form renderer for housing preferences.
"""

import json
from pathlib import Path

import streamlit as st

from core.events import log_event
from core.mcip import MCIP
from core.navi import render_navi_panel


def render():
    """Render Housing prep section."""

    # Load config
    config = _load_config()

    # Render Navi (pass None for module_config since this isn't a stepped module)
    render_navi_panel(location="product", product_key="advisor_prep", module_config=None)

    st.markdown(f"## {config['icon']} {config['title']}")
    st.markdown(f"*{config['description']}*")
    st.markdown("---")

    # Get current data
    current_data = st.session_state["advisor_prep"]["data"]["housing"]

    # Render fields from JSON config
    form_data = {}

    for field in config["fields"]:
        field_key = field["key"]
        field_label = field["label"]
        field_type = field["type"]
        field_required = field.get("required", False)
        field_help = field.get("help", "")

        # Get prefill value
        default_value = current_data.get(field_key) or _get_prefill_value(field)

        # Render appropriate input widget
        if field_type == "text":
            value = st.text_input(
                field_label,
                value=default_value or "",
                placeholder=field.get("placeholder", ""),
                help=field_help,
            )
        elif field_type == "select":
            options = field.get("options", [])
            index = 0
            if default_value and default_value in options:
                index = options.index(default_value)

            value = st.selectbox(field_label, options=options, index=index, help=field_help)
        elif field_type == "multiselect":
            options = field.get("options", [])
            default = default_value if isinstance(default_value, list) else []

            value = st.multiselect(field_label, options=options, default=default, help=field_help)
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
        if st.button("💾 Save Housing Preferences", type="primary", use_container_width=True):
            _save_section(form_data)

    with col_save3:
        # Show completion status
        sections_complete = st.session_state["advisor_prep"]["sections_complete"]
        if "housing" in sections_complete:
            st.success("✓ Saved")


def _load_config() -> dict:
    """Load housing section JSON config."""
    config_path = Path(__file__).parent.parent / "config" / "housing.json"
    with open(config_path) as f:
        return json.load(f)


def _get_prefill_value(field: dict):
    """Get prefill value from session state based on prefill_from path.

    Args:
        field: Field config dict

    Returns:
        Prefill value or None
    """
    prefill_path = field.get("prefill_from")
    if not prefill_path:
        return None

    # Parse path (e.g., "gcp.results.recommendation")
    parts = prefill_path.split(".")

    # Prefill is currently handled by get_housing_prefill() function
    # This fallback returns None for any fields not covered by that function
    return None


def _save_section(form_data: dict):
    """Save housing section data.

    Args:
        form_data: Form field values
    """
    # Save to session state
    st.session_state["advisor_prep"]["data"]["housing"] = form_data

    # Mark section complete
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    if "housing" not in sections_complete:
        sections_complete.append("housing")

    # Award duck badge (local import to avoid circular dependency)
    try:
        from products.advisor_prep.utils import award_duck_badge

        award_duck_badge("housing")
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
            "section": "housing",
            "has_preference": bool(form_data.get("care_preference")),
            "has_location": bool(form_data.get("location_preference")),
            "timeline": form_data.get("move_timeline"),
            "priorities_count": len(form_data.get("housing_priorities", [])),
        },
    )

    st.success("✓ Housing preferences saved!")

    # Return to menu after short delay
    import time

    time.sleep(1)
    st.session_state.pop("advisor_prep_current_section", None)
    st.rerun()
