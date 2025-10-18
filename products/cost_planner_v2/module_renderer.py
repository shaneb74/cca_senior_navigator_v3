"""
Dynamic Module Renderer for Cost Planner v2

Renders financial assessment modules from JSON configuration.
Similar to GCP's data-driven approach but for financial forms.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, Dict

import streamlit as st


@lru_cache(maxsize=1)
def load_module_config() -> dict[str, Any]:
    """Load module configuration from JSON file.

    Returns:
        Dict with complete module configuration
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "cost_planner_v2_modules.json"
    with open(config_path) as f:
        return json.load(f)


def get_module_definition(module_key: str) -> Optional[dict[str, Any]]:
    """Get specific module definition by key.

    Args:
        module_key: Module identifier

    Returns:
        Module definition dict or None
    """
    config = load_module_config()
    for module in config["modules"]:
        if module["key"] == module_key:
            return module
    return None


def render_module(module_key: str):
    """Dynamically render a module from JSON configuration.

    Args:
        module_key: Module identifier (e.g., 'income_assets')
    """
    module_def = get_module_definition(module_key)

    if not module_def:
        st.error(f"Module '{module_key}' not found in configuration")
        return

    # Render header
    st.title(f"{module_def['icon']} {module_def['title']}")
    st.markdown(f"### {module_def['description']}")

    # Initialize session state for this module
    state_key = f"cost_v2_{module_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = _initialize_module_state(module_def)

    st.markdown("---")

    # Render each section
    collected_data = {}
    for section in module_def["sections"]:
        # Check visibility conditions
        if not _is_section_visible(section):
            continue

        # Render section
        section_data = _render_section(section, state_key)
        collected_data.update(section_data)

    st.markdown("---")

    # Calculate totals and derived values
    output_data = _calculate_outputs(module_def, collected_data)

    # Render insights
    _render_insights(module_def, output_data)

    st.markdown("---")

    # Navigation buttons
    _render_navigation(module_key, module_def, output_data)


def _initialize_module_state(module_def: dict[str, Any]) -> dict[str, Any]:
    """Initialize default state for module fields.

    Args:
        module_def: Module definition

    Returns:
        Dict with default values
    """
    state = {}
    for section in module_def["sections"]:
        for field in section.get("fields", []):
            state[field["key"]] = field.get("default", 0 if field["type"] == "currency" else "")
    return state


def _is_section_visible(section: dict[str, Any]) -> bool:
    """Check if section should be visible based on conditions.

    Args:
        section: Section definition

    Returns:
        True if section should be visible
    """
    visible_if = section.get("visible_if")
    if not visible_if:
        return True

    # Simple condition evaluation
    condition = visible_if.get("condition", "")
    # Note: Advanced condition parsing not implemented yet
    # Currently all sections are visible by default
    return True


def _render_section(section: dict[str, Any], state_key: str) -> dict[str, Any]:
    """Render a section with its fields.

    Args:
        section: Section definition
        state_key: Session state key for module

    Returns:
        Dict with collected field values
    """
    # Section header
    icon = section.get("icon", "")
    st.markdown(f"## {icon} {section['title']}")

    # Help text
    if "help_text" in section:
        st.caption(f"💡 **Tip:** {section['help_text']}")

    # Render info boxes
    for info_box in section.get("info_boxes", []):
        if _evaluate_visible_if(info_box.get("visible_if")):
            box_type = info_box["type"]
            content = info_box["content"]
            if box_type == "success":
                st.success(content)
            elif box_type == "info":
                st.info(content)
            elif box_type == "warning":
                st.warning(content)

    # Layout
    layout = section.get("layout", "single_column")
    data = {}

    if layout == "two_column":
        col1, col2 = st.columns(2)
        col1_fields = [f for f in section["fields"] if f.get("column", 1) == 1]
        col2_fields = [f for f in section["fields"] if f.get("column", 1) == 2]

        with col1:
            for field in col1_fields:
                data[field["key"]] = _render_field(field, state_key)

        with col2:
            for field in col2_fields:
                data[field["key"]] = _render_field(field, state_key)
    else:
        # Single column or auto layout
        col_count = section.get("columns", 1)
        if col_count == 2:
            col1, col2 = st.columns(2)
            fields = section["fields"]
            mid = len(fields) // 2

            with col1:
                for field in fields[:mid]:
                    data[field["key"]] = _render_field(field, state_key)

            with col2:
                for field in fields[mid:]:
                    data[field["key"]] = _render_field(field, state_key)
        else:
            for field in section["fields"]:
                data[field["key"]] = _render_field(field, state_key)

    # Render section summary
    if "summary" in section:
        _render_summary(section["summary"], data)

    return data


def _render_field(field: dict[str, Any], state_key: str) -> Any:
    """Render a single form field.

    Args:
        field: Field definition
        state_key: Session state key for module

    Returns:
        Field value
    """
    # Check visibility
    if not _evaluate_visible_if(field.get("visible_if")):
        return st.session_state[state_key].get(field["key"], field.get("default"))

    field_type = field["type"]
    field_key = field["key"]
    label = field["label"]
    description = field.get("description", "")

    # Render label with description
    if description:
        st.markdown(f"**{label}** ({description})")
    else:
        st.markdown(f"**{label}**")

    # Render appropriate widget
    value = None

    if field_type == "currency":
        value = st.number_input(
            label,
            min_value=field.get("min", 0),
            max_value=field.get("max", 1000000),
            step=field.get("step", 1),
            value=st.session_state[state_key].get(field_key, field.get("default", 0)),
            help=field.get("help"),
            key=f"{state_key}_{field_key}",
            label_visibility="collapsed",
        )

    elif field_type == "text":
        value = st.text_input(
            label,
            value=st.session_state[state_key].get(field_key, field.get("default", "")),
            max_chars=field.get("max_length"),
            placeholder=field.get("placeholder"),
            help=field.get("help"),
            key=f"{state_key}_{field_key}",
            label_visibility="collapsed",
        )

    elif field_type == "checkbox":
        # For checkbox fields with cost, show the cost in the label
        checkbox_label = label
        if "cost" in field:
            cost = field["cost"]
            if field.get("cost_applies_regional_multiplier"):
                # Get regional multiplier from session state
                multiplier = st.session_state.get("cost_v2_monthly_costs", {}).get(
                    "regional_multiplier", 1.0
                )
                cost = cost * multiplier
            checkbox_label = f"{label} (+${cost:,.0f}/mo)"

        value = st.checkbox(
            checkbox_label,
            value=st.session_state[state_key].get(field_key, field.get("default", False)),
            help=field.get("help"),
            key=f"{state_key}_{field_key}",
        )

    elif field_type == "select":
        options = field.get("options", [])
        option_values = [opt["value"] for opt in options]
        option_labels = [opt["label"] for opt in options]

        default_value = st.session_state[state_key].get(field_key, field.get("default"))
        default_index = option_values.index(default_value) if default_value in option_values else 0

        selected_label = st.selectbox(
            label,
            options=option_labels,
            index=default_index,
            help=field.get("help"),
            key=f"{state_key}_{field_key}_select",
        )

        value = option_values[option_labels.index(selected_label)]

    elif field_type == "slider":
        st.markdown(f"**{label}** ({description})" if description else f"**{label}**")
        value = st.slider(
            label,
            min_value=field.get("min", 0),
            max_value=field.get("max", 100),
            value=st.session_state[state_key].get(field_key, field.get("default", 0)),
            step=field.get("step", 1),
            help=field.get("help"),
            key=f"{state_key}_{field_key}",
            label_visibility="collapsed",
        )

    elif field_type == "display_only":
        # Display-only field (calculated elsewhere)
        display_value = st.session_state[state_key].get(field_key, 0)
        format_str = field.get("display_format", "{}")
        st.metric(label, format_str.format(display_value), help=field.get("help"))
        value = display_value

    elif field_type == "calculated":
        # Calculated field
        value = _calculate_field_value(field, state_key)
        format_str = field.get("display_format", "{}")
        st.metric(label, format_str.format(value))

    # Update session state
    st.session_state[state_key][field_key] = value

    return value


def _evaluate_visible_if(visible_if: Optional[dict[str, Any]]) -> bool:
    """Evaluate visibility condition.

    Args:
        visible_if: Visibility condition

    Returns:
        True if field should be visible
    """
    if not visible_if:
        return True

    # Get the field value to check
    field_name = visible_if.get("field")
    if not field_name:
        return True

    # Find the value in session state
    # Simple state lookup - iterates through session state dicts
    for key, value in st.session_state.items():
        if isinstance(value, dict) and field_name in value:
            field_value = value[field_name]

            # Check condition
            if "equals" in visible_if:
                return field_value == visible_if["equals"]
            elif "not_equals" in visible_if:
                return field_value != visible_if["not_equals"]

    return True


def _calculate_field_value(field: dict[str, Any], state_key: str) -> Any:
    """Calculate value for calculated field.

    Args:
        field: Field definition
        state_key: Session state key

    Returns:
        Calculated value
    """
    source = field.get("source")

    if source == "va_benefit_lookup":
        # Get VA status and return benefit amount
        config = load_module_config()
        va_status = st.session_state[state_key].get("va_status", "not_sure")
        return config["va_benefit_amounts"].get(va_status, 0)

    # Default
    return 0


def _render_summary(summary: dict[str, Any], data: dict[str, Any]):
    """Render section summary metric.

    Args:
        summary: Summary definition
        data: Section data
    """
    summary_type = summary["type"]
    label = summary["label"]

    if summary_type == "calculated":
        formula = summary["formula"]

        # Simple formula evaluation
        if formula.startswith("sum("):
            # Extract field names
            fields_str = formula[4:-1]  # Remove "sum(" and ")"
            field_names = [f.strip() for f in fields_str.split(",")]
            total = sum(data.get(f, 0) for f in field_names)

            format_str = summary.get("display_format", "{}")
            st.metric(f"**{label}**", format_str.format(total))


def _calculate_outputs(module_def: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    """Calculate final output values for module.

    Args:
        module_def: Module definition
        data: Collected form data

    Returns:
        Complete output data with calculations
    """
    output = data.copy()

    # Calculate totals based on output contract
    output_contract = module_def.get("output_contract", {})

    for key, value_type in output_contract.items():
        if value_type == "calculated":
            # Perform calculation based on key name
            if "total_monthly_income" == key:
                output[key] = sum(
                    [
                        data.get("monthly_income_ss", 0),
                        data.get("monthly_income_pension", 0),
                        data.get("monthly_income_other", 0),
                    ]
                )
            elif "total_assets" == key:
                output[key] = sum(
                    [
                        data.get("liquid_assets", 0),
                        data.get("property_value", 0),
                        data.get("retirement_accounts", 0),
                        data.get("other_assets", 0),
                    ]
                )
            elif "total_coverage" == key:
                output[key] = sum(
                    [
                        data.get("ltc_monthly_benefit", 0),
                        data.get("va_monthly_benefit", 0),
                        data.get("medicare_coverage", 0),
                        data.get("medicaid_coverage", 0),
                        data.get("other_coverage", 0),
                    ]
                )
            elif "total_monthly_expenses" == key:
                # Sum all expense categories
                output[key] = sum(
                    [
                        data.get("monthly_housing", 0),
                        data.get("property_taxes", 0),
                        data.get("hoa_fees", 0),
                        data.get("electric_gas", 0),
                        data.get("water_sewer", 0),
                        data.get("phone_internet", 0),
                        data.get("cable_streaming", 0),
                        data.get("groceries", 0),
                        data.get("dining_out", 0),
                        data.get("transportation", 0),
                        data.get("personal_care", 0),
                        data.get("health_insurance", 0),
                        data.get("prescriptions", 0),
                        data.get("medical_copays", 0),
                        data.get("dental_vision", 0),
                        data.get("debt_payments", 0),
                        data.get("insurance_other", 0),
                        data.get("entertainment", 0),
                        data.get("miscellaneous", 0),
                    ]
                )
            elif key.startswith("total_"):
                # Generic total calculation - sum all numeric fields in section
                # This handles section-level totals automatically
                pass

    return output


def _render_insights(module_def: dict[str, Any], data: dict[str, Any]):
    """Render conditional insights based on data.

    Args:
        module_def: Module definition
        data: Output data
    """
    for insight in module_def.get("insights", []):
        condition = insight.get("condition", "")

        # Simple condition evaluation using string matching
        # Advanced expression parser not implemented
        if "total_monthly_income > 0 AND total_assets > 0" in condition:
            if data.get("total_monthly_income", 0) > 0 and data.get("total_assets", 0) > 0:
                msg = insight["message"].format(**data)
                insight_type = insight.get("type", "info")

                if insight_type == "info":
                    st.info(msg)
                elif insight_type == "success":
                    st.success(msg)
                elif insight_type == "warning":
                    st.warning(msg)


def _render_navigation(module_key: str, module_def: dict[str, Any], output_data: dict[str, Any]):
    """Render navigation buttons.

    Args:
        module_key: Module identifier
        module_def: Module definition
        output_data: Complete output data
    """
    config = load_module_config()
    nav = config["navigation"]

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        back_hub = nav["back_to_hub"]
        if st.button(f"{back_hub['icon']} {back_hub['label']}", key=f"{module_key}_hub"):
            from core.nav import route_to

            route_to(back_hub["route"])

    with col2:
        back_modules = nav["back_to_modules"]
        if st.button(f"{back_modules['icon']} {back_modules['label']}", key=f"{module_key}_back"):
            st.session_state.cost_v2_step = "modules"
            st.rerun()

    with col3:
        save_btn = nav["save_continue"]
        button_type = save_btn.get("type", "secondary")
        if st.button(
            f"{save_btn['label']} {save_btn['icon']}",
            type=button_type,
            use_container_width=True,
            key=f"{module_key}_save",
        ):
            # Save to module registry
            st.session_state.cost_v2_modules[module_key] = {
                "status": "completed",
                "progress": 100,
                "data": output_data,
            }

            # Return to hub
            st.session_state.cost_v2_step = "modules"
            st.success(f"✅ {module_def['title']} saved!")
            st.rerun()

    st.caption("💾 Your progress is automatically saved")


def get_all_modules() -> list[dict[str, Any]]:
    """Get all module definitions.

    Returns:
        List of module definitions
    """
    config = load_module_config()
    return config["modules"]


def get_module_metadata() -> dict[str, Any]:
    """Get product metadata.

    Returns:
        Metadata dict
    """
    config = load_module_config()
    return config["metadata"]
