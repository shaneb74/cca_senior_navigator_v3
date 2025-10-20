"""
Assessment Engine - JSON-driven assessment rendering for Cost Planner v2.

This engine renders financial assessments from JSON configurations, similar to
the module engine but specialized for assessment-level state management.

Pattern: Follows core/modules/engine.py architecture
State: Stored in session_state under assessment-specific keys
Navigation: Section-based flow within assessments
"""

from __future__ import annotations

import time
from html import escape as H
from typing import Any

import streamlit as st

from core.events import log_event
from core.session_store import safe_rerun
from core.ui import render_navi_panel_v2
from core.mode_engine import (
    render_mode_toggle,
    get_visible_fields,
    render_aggregate_field,
    render_unallocated_field,
)


def run_assessment(
    assessment_key: str, assessment_config: dict[str, Any], product_key: str = "cost_planner_v2"
) -> dict[str, Any]:
    """
    Run a single financial assessment flow.

    Args:
        assessment_key: Unique key for this assessment (e.g., 'income', 'assets')
        assessment_config: JSON configuration with sections, fields, calculations
        product_key: Parent product key for state management

    Returns:
        Updated assessment state dict
    """
    # Initialize state key
    state_key = f"{product_key}_{assessment_key}"

    # Initialize assessment state
    st.session_state.setdefault(state_key, {})
    state = st.session_state[state_key]

    # Track current section (default to 0)
    section_index = int(st.session_state.get(f"{state_key}._section", 0))

    # Get sections from config
    sections = assessment_config.get("sections", [])
    if not sections:
        st.error(f"⚠️ Assessment '{assessment_key}' has no sections defined.")
        st.stop()

    # Clamp section index to valid range
    section_index = max(0, min(section_index, len(sections) - 1))
    st.session_state[f"{state_key}._section"] = section_index

    current_section = sections[section_index]

    # Check if we're viewing intro or results (no Navi on these)
    section_type = current_section.get("type")
    is_intro = section_type == "intro"
    is_results = section_type == "results"

    # ========================================================================
    # CENTERED CONTAINER (Hub-like aesthetic)
    # ========================================================================
    st.markdown('<div class="sn-app module-container">', unsafe_allow_html=True)

    # ========================================================================
    # NAVI GUIDANCE PANEL
    # ========================================================================
    if not is_intro and not is_results:
        _render_navi_guidance(
            assessment_config=assessment_config,
            current_section=current_section,
            section_index=section_index,
            total_sections=len(sections),
            state=state,
        )

    # ========================================================================
    # SECTION HEADER
    # ========================================================================
    _render_section_header(
        assessment_config=assessment_config,
        current_section=current_section,
        section_index=section_index,
        total_sections=len(sections),
    )

    # ========================================================================
    # MODE TOGGLE (if section supports Basic/Advanced modes)
    # ========================================================================
    current_mode = "advanced"  # Default mode
    if not is_intro and not is_results:
        mode_config = current_section.get("mode_config", {})
        if mode_config.get("supports_basic_advanced"):
            # Render mode toggle
            current_mode = render_mode_toggle(f"{assessment_key}_{current_section['id']}")

    # ========================================================================
    # FIELDS RENDERING
    # ========================================================================
    if not is_results:
        new_values = _render_fields(current_section, state, current_mode)
        if new_values:
            state.update(new_values)

            # Save to product tiles for persistence
            tiles = st.session_state.setdefault("tiles", {})
            product_tiles = tiles.setdefault(product_key, {})
            assessments_state = product_tiles.setdefault("assessments", {})
            assessments_state[assessment_key] = state.copy()

    # ========================================================================
    # INFO BOXES (from JSON)
    # ========================================================================
    info_boxes = current_section.get("info_boxes", [])
    if info_boxes and not is_results:
        _render_info_boxes(info_boxes)

    # ========================================================================
    # RESULTS VIEW
    # ========================================================================
    if is_results:
        _render_results_view(assessment_config, state, assessment_key)

        # Render navigation actions for results page
        _render_results_navigation(
            assessment_key=assessment_key,
            state_key=state_key,
            section_index=section_index,
            product_key=product_key,
        )

        st.markdown("</div>", unsafe_allow_html=True)
        return state

    # ========================================================================
    # NAVIGATION ACTIONS
    # ========================================================================
    _render_navigation_actions(
        assessment_key=assessment_key,
        assessment_config=assessment_config,
        state_key=state_key,
        section_index=section_index,
        total_sections=len(sections),
        current_section=current_section,
        state=state,
        product_key=product_key,
    )

    st.markdown("</div>", unsafe_allow_html=True)
    return state


def _render_navi_guidance(
    assessment_config: dict[str, Any],
    current_section: dict[str, Any],
    section_index: int,
    total_sections: int,
    state: dict[str, Any],
) -> None:
    """Render Navi panel with contextual guidance."""

    # Get assessment metadata
    title = assessment_config.get("title", "Financial Assessment")

    # Calculate progress
    progress_sections = [
        s
        for s in assessment_config.get("sections", [])
        if s.get("type") != "intro" and s.get("type") != "results"
    ]
    current_progress = min(section_index, len(progress_sections))
    total_progress = len(progress_sections)

    # Build Navi message
    if section_index == 0:
        # Intro section
        navi_title = f"Let's work on {title}"
        navi_reason = current_section.get("help_text", "I'll guide you through each section.")
    else:
        # Regular section
        section_title = current_section.get("title", "This Section")
        navi_title = f"Section: {section_title}"
        navi_reason = current_section.get("help_text", "Fill in the fields below.")

    # Progress context chip
    context_chips = []
    if total_progress > 0:
        context_chips.append(
            {"label": f"Step {current_progress + 1} of {total_progress}", "sublabel": None}
        )

    render_navi_panel_v2(
        title=navi_title,
        reason=navi_reason,
        encouragement={
            "icon": "💡",
            "text": "Take your time. You can save and come back anytime.",
            "status": "active",
        },
        context_chips=context_chips,
        primary_action={"label": "", "route": ""},
        variant="module",
    )


def _render_section_header(
    assessment_config: dict[str, Any],
    current_section: dict[str, Any],
    section_index: int,
    total_sections: int,
) -> None:
    """Render section header with title and optional subtitle."""

    section_title = current_section.get("title", "Section")
    section_icon = current_section.get("icon", "")

    # Add icon to title if present
    if section_icon:
        section_title = f"{section_icon} {section_title}"

    st.markdown(
        f"""
        <div class="mod-head">
          <div class="mod-head-row">
            <h2 class="h2">{H(section_title)}</h2>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _should_show_field(field: dict[str, Any], state: dict[str, Any], new_values: dict[str, Any] = None) -> bool:
    """
    Check if field should be visible based on visibility conditions.
    
    Args:
        field: Field configuration dict
        state: Current assessment state
        new_values: Optional dict of newly rendered field values (converted from labels to values)
    
    Returns:
        True if field should be rendered, False otherwise
    """
    # Check visibility condition
    return _is_field_visible(field, state, new_values)


def _render_fields(section: dict[str, Any], state: dict[str, Any], mode: str = "advanced") -> dict[str, Any]:
    """
    Render form fields for current section.

    Supports field types:
    - currency: st.number_input with $ formatting
    - select: st.selectbox
    - checkbox: st.checkbox
    - multiselect: st.multiselect
    - text: st.text_input
    - textarea: st.text_area
    - date: st.date_input
    - aggregate_input: Mode-aware aggregate field (Basic: input, Advanced: calculated label)

    Handles:
    - visible_if conditions
    - default values
    - min/max constraints
    - help text
    - mode-based visibility (Basic/Advanced)
    
    Args:
        section: Section configuration dict
        state: Current assessment state
        mode: Current mode ("basic" or "advanced")
    """
    new_values: dict[str, Any] = {}
    
    # Get mode-filtered fields if section supports modes
    mode_config = section.get("mode_config", {})
    if mode_config.get("supports_basic_advanced"):
        fields = get_visible_fields(section, mode)
    else:
        fields = section.get("fields", [])

    # Check if section uses two-column layout
    layout = section.get("layout", "simple")

    if layout == "two_column":
        col1, col2 = st.columns(2)
        columns = {1: col1, 2: col2}
    else:
        columns = None

    for field in fields:
        # Check visibility conditions
        # Pass new_values so visibility checks can see converted label→value mappings
        if not _should_show_field(field, state, new_values):
            # Field is hidden but preserve its value in state
            key = field.get("key")
            if key and key not in state:
                # Initialize with default if not already in state
                default = field.get("default")
                if default is not None:
                    state[key] = default
            continue

        # Get field properties
        key = field.get("key")
        label = field.get("label", key)
        field_type = field.get("type", "text")
        required = field.get("required", False)
        help_text = field.get("help")
        default = field.get("default")

        # Get current value from state dict (from persistence) or default
        current_value = state.get(key, default)
        
        # Generate unique widget key
        widget_key = f"field_{key}"

        # RENDER CUSTOM HTML LABEL (visible regardless of CSS)
        label_html = f"""
        <div style="margin-bottom: 4px;">
            <label style="
                display: block;
                font-size: 14px;
                font-weight: 500;
                color: #1e293b;
                line-height: 1.4;
            ">
                {label}{'<span style="color: #dc2626;"> *</span>' if required else ""}
            </label>
        </div>
        """

        # Determine container for rendering
        if columns:
            column_num = field.get("column", 1)
            container = columns.get(column_num, columns[1])
        else:
            container = st

        # Show custom label
        container.markdown(label_html, unsafe_allow_html=True)

        # Render appropriate widget based on field type
        if field_type == "aggregate_input":
            # NEW: Mode-aware aggregate field (uses mode_engine)
            updates = render_aggregate_field(field, state, mode, container)
            if updates:
                new_values.update(updates)
        
        elif field_type == "currency":
            min_val = field.get("min", 0)
            max_val = field.get("max", 10000000)
            step = field.get("step", 100)
            readonly = field.get("readonly", False)
            
            # Ensure all numeric values are the same type (float for currency to support cents)
            min_val = float(min_val)
            max_val = float(max_val)
            step = float(step)
            
            # Handle current value - convert to float if present, otherwise use min_val
            if current_value is not None:
                current_value = float(current_value)
            else:
                current_value = min_val

            # Define on_change callback to trigger immediate rerun for aggregate updates
            def _on_currency_change():
                """Callback to ensure UI updates immediately when currency field changes."""
                # Force a rerun so aggregate totals update immediately
                pass  # The act of having an on_change callback triggers the rerun
            
            value = container.number_input(
                label=label,  # Still need this for accessibility
                label_visibility="collapsed",  # Hide Streamlit's label
                min_value=min_val,
                max_value=max_val,
                value=current_value,
                step=step,
                format="%.2f",  # Support cents (e.g., $1,908.95)
                help=help_text,
                key=widget_key,  # Use widget_key variable
                disabled=readonly,  # Make read-only if specified
                on_change=_on_currency_change,  # Trigger rerun for immediate aggregate updates
            )
            new_values[key] = value

        elif field_type == "select":
            options = field.get("options", [])
            option_labels = [opt.get("label", opt.get("value")) for opt in options]
            option_values = [opt.get("value", opt.get("label")) for opt in options]

            # Find current index based on current_value (which might be a value or label)
            current_index = 0
            if current_value is not None:
                # Try to find in values first (most common case)
                try:
                    current_index = option_values.index(current_value)
                except ValueError:
                    # Maybe it's a label instead?
                    try:
                        current_index = option_labels.index(current_value)
                    except ValueError:
                        # Default to first option
                        current_index = 0

            # Define on_change callback to trigger immediate rerun
            def _on_select_change():
                """Callback to ensure UI updates immediately when select field changes."""
                pass  # The act of having an on_change callback triggers the rerun

            selected_label = container.selectbox(
                label=label,  # Still need this for accessibility
                label_visibility="collapsed",  # Hide Streamlit's label
                options=option_labels,
                index=current_index,
                help=help_text,
                key=widget_key,  # Use widget_key instead of f"field_{key}"
                on_change=_on_select_change,  # Trigger rerun for immediate updates
            )

            # Map back to value - the selectbox returns the label
            try:
                selected_index = option_labels.index(selected_label)
                value = option_values[selected_index]
            except (ValueError, IndexError):
                # Fallback: use first option's value
                value = option_values[0] if option_values else None
            
            new_values[key] = value

        elif field_type == "checkbox":
            value = container.checkbox(
                label=label,  # Checkbox labels should remain visible
                value=bool(current_value),
                help=help_text,
                key=widget_key,  # Use widget_key variable
            )
            new_values[key] = value

        elif field_type == "multiselect":
            options = field.get("options", [])
            option_labels = [opt.get("label", opt.get("value")) for opt in options]

            value = container.multiselect(
                label=label,
                label_visibility="collapsed",
                options=option_labels,
                default=current_value if isinstance(current_value, list) else [],
                help=help_text,
                key=widget_key,  # Use widget_key variable
            )
            new_values[key] = value

        elif field_type == "textarea":
            value = container.text_area(
                label=label,
                label_visibility="collapsed",
                value=str(current_value) if current_value else "",
                help=help_text,
                key=widget_key,  # Use widget_key variable
            )
            new_values[key] = value

        elif field_type == "date":
            value = container.date_input(
                label=label,
                label_visibility="collapsed",
                value=current_value,
                help=help_text,
                key=widget_key,  # Use widget_key variable
            )
            new_values[key] = value

        elif field_type == "display_currency":
            # Display-only currency label (no input, just shows formatted value)
            # Value comes from state (e.g., auto-calculated VA disability amount)
            display_value = float(current_value) if current_value is not None else 0.0
            formatted_value = f"${display_value:,.2f}"
            
            # Render as a styled display box
            container.markdown(
                f"""
                <div style="
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-size: 24px;
                    font-weight: 600;
                    color: #0f172a;
                    text-align: left;
                    margin-bottom: 8px;
                ">
                    {formatted_value}
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # Don't include in new_values since it's display-only
            # (value already in state from auto-calculation)

        elif field_type == "display_currency_aggregate":
            # Display-only calculated total (sum of sub-fields)
            # Always shows as a styled label, never editable
            
            sub_fields = field.get("aggregate_from", [])
            
            # Calculate aggregate from sub-fields
            # CRITICAL: Read from st.session_state first for real-time updates
            aggregate_total = 0.0
            for sub_field_key in sub_fields:
                sub_widget_key = f"field_{sub_field_key}"
                sub_value = st.session_state.get(sub_widget_key)
                if sub_value is None:
                    sub_value = state.get(sub_field_key, 0.0)
                
                # Convert to float safely
                if isinstance(sub_value, (int, float)):
                    aggregate_total += float(sub_value)
                elif isinstance(sub_value, str) and sub_value.strip():
                    try:
                        aggregate_total += float(sub_value.replace(',', '').replace('$', ''))
                    except ValueError:
                        pass  # Skip non-numeric values
            
            formatted_value = f"${aggregate_total:,.2f}"
            
            # Render as a styled aggregate display
            container.markdown(
                f"""
                <div style="
                    background: #f0f9ff;
                    border: 2px solid #3b82f6;
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-size: 18px;
                    font-weight: 700;
                    color: #1e40af;
                    text-align: right;
                    margin-bottom: 8px;
                ">
                    <span style="font-size: 12px; font-weight: 500; color: #60a5fa; text-transform: uppercase; letter-spacing: 0.05em; margin-right: 8px;">Total:</span>
                    {formatted_value}
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # Store the calculated aggregate in state
            state[key] = aggregate_total

        else:  # text
            value = container.text_input(
                label=label,
                label_visibility="collapsed",
                value=str(current_value) if current_value else "",
                help=help_text,
                key=widget_key,  # Use widget_key variable
            )
            new_values[key] = value

    return new_values


def _is_field_visible(field: dict[str, Any], state: dict[str, Any], new_values: dict[str, Any] = None) -> bool:
    """
    Check if field should be visible based on visible_if condition.
    
    Args:
        field: Field configuration dict
        state: Current assessment state
        new_values: Optional dict of newly rendered field values (label→value conversions)
    
    Returns:
        True if field passes visibility check, False otherwise
    """
    visible_if = field.get("visible_if")
    if not visible_if:
        return True

    # Check field condition
    check_field = visible_if.get("field")
    if not check_field:
        return True

    # CRITICAL FIX: Check in this priority order:
    # 1. new_values (has converted label→value for current render)
    # 2. state dict (has persisted values from previous renders)
    # This ensures conditional fields appear immediately when parent field changes
    if new_values and check_field in new_values:
        current_value = new_values[check_field]
    else:
        current_value = state.get(check_field)

    # Check equals condition
    if "equals" in visible_if:
        return current_value == visible_if["equals"]

    # Check not_equals condition
    if "not_equals" in visible_if:
        return current_value != visible_if["not_equals"]

    # Check in condition
    if "in" in visible_if:
        return current_value in visible_if["in"]

    return True


def _render_info_boxes(info_boxes: list[dict[str, Any]]) -> None:
    """Render info boxes from JSON config."""
    for box in info_boxes:
        box_type = box.get("type", "info")
        message = box.get("message", "")

        if box_type == "success":
            st.success(message)
        elif box_type == "warning":
            st.warning(message)
        elif box_type == "error":
            st.error(message)
        else:
            st.info(message)


def _render_results_view(
    assessment_config: dict[str, Any], state: dict[str, Any], assessment_key: str
) -> None:
    """Render results summary for completed assessment."""

    # Get summary config
    summary_config = assessment_config.get("summary", {})

    if summary_config:
        summary_label = summary_config.get("label", "Summary")
        summary_type = summary_config.get("type", "calculated")

        if summary_type == "calculated":
            # Evaluate calculation
            formula = summary_config.get("formula", "")
            result = _evaluate_formula(formula, state)

            display_format = summary_config.get("display_format", "${:,.0f}")

            st.success(f"✅ {summary_label}: {display_format.format(result)}")

    # Show all collected data
    st.markdown("### Your Responses")

    for section in assessment_config.get("sections", []):
        if section.get("type") in ["intro", "results"]:
            continue

        section_title = section.get("title", "Section")
        st.markdown(f"**{section_title}**")

        for field in section.get("fields", []):
            key = field.get("key")
            label = field.get("label", key)
            value = state.get(key)

            if value is not None:
                # Format value based on type
                field_type = field.get("type", "text")
                if field_type == "currency":
                    st.write(f"- {label}: ${value:,.0f}")
                elif field_type == "select":
                    # Map value to label
                    options = field.get("options", [])
                    for opt in options:
                        if opt.get("value") == value:
                            st.write(f"- {label}: {opt.get('label', value)}")
                            break
                    else:
                        st.write(f"- {label}: {value}")
                else:
                    st.write(f"- {label}: {value}")


def _evaluate_formula(formula: str, state: dict[str, Any]) -> float:
    """
    Evaluate a calculation formula.

    Supports:
    - sum(field1, field2, ...)
    - field1 + field2
    - field1 * field2
    - etc.
    """
    # Handle sum() function
    if formula.startswith("sum("):
        # Extract field names
        fields_str = formula[4:-1]  # Remove "sum(" and ")"
        field_names = [f.strip() for f in fields_str.split(",")]

        total = 0.0
        for field_name in field_names:
            value = state.get(field_name, 0)
            if value is None:
                value = 0
            total += float(value)

        return total

    # For simple expressions, evaluate with state context
    # WARNING: This uses eval - only safe because formulas come from JSON config
    try:
        return eval(formula, {"__builtins__": {}}, state)
    except:
        return 0.0


def _render_navigation_actions(
    assessment_key: str,
    assessment_config: dict[str, Any],
    state_key: str,
    section_index: int,
    total_sections: int,
    current_section: dict[str, Any],
    state: dict[str, Any],
    product_key: str,
) -> None:
    """Render navigation buttons (Back, Continue, Save & Exit)."""

    is_first = section_index == 0
    is_last = section_index == total_sections - 1

    # Check required fields
    required_fields = [
        f
        for f in current_section.get("fields", [])
        if f.get("required") and _is_field_visible(f, state)
    ]
    missing_fields = []
    for field in required_fields:
        key = field.get("key")
        value = state.get(key)
        if value is None or value == "" or value == []:
            missing_fields.append(field.get("label", key))

    st.markdown('<div class="sn-app mod-actions">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Back button (except on first section)
        if not is_first:
            if st.button(
                "← Back", key=f"back_{assessment_key}", type="secondary", use_container_width=True
            ):
                prev_section = max(0, section_index - 1)
                st.session_state[f"{state_key}._section"] = prev_section
                safe_rerun()

    with col2:
        # Continue button
        continue_label = "View Results" if is_last else "Continue →"
        if st.button(
            continue_label,
            key=f"continue_{assessment_key}",
            type="primary",
            use_container_width=True,
        ):
            if missing_fields:
                st.warning(f"Please complete required fields: {', '.join(missing_fields)}")
            else:
                next_section = min(section_index + 1, total_sections - 1)
                st.session_state[f"{state_key}._section"] = next_section

                # Mark assessment as complete if moving to results
                if next_section == total_sections - 1:
                    state["status"] = "done"
                    state["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

                    # Log completion event
                    log_event(
                        "assessment.completed",
                        {"product": product_key, "assessment": assessment_key},
                    )

                safe_rerun()

    with col3:
        # Back to Hub button
        if st.button(
            "← Back to Hub", key=f"hub_{assessment_key}", type="secondary", use_container_width=True
        ):
            # Clear current assessment and return to assessment hub
            st.session_state.pop(f"{product_key}_current_assessment", None)
            st.session_state[f"{product_key}_step"] = "assessments"
            safe_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_results_navigation(
    assessment_key: str, state_key: str, section_index: int, product_key: str
) -> None:
    """Render navigation buttons for results page."""

    st.markdown('<div class="sn-app mod-actions">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        # Review Answers button - go back to first question section
        if st.button(
            "← Review Answers",
            key=f"review_{assessment_key}",
            type="secondary",
            use_container_width=True,
        ):
            # Find first non-intro section
            st.session_state[f"{state_key}._section"] = (
                1  # Skip intro (0), go to first questions (1)
            )
            safe_rerun()

    with col2:
        # Back to Hub button
        if st.button(
            "← Back to Hub",
            key=f"hub_results_{assessment_key}",
            type="primary",
            use_container_width=True,
        ):
            # Clear current assessment and return to assessment hub
            st.session_state.pop(f"{product_key}_current_assessment", None)
            st.session_state[f"{product_key}_step"] = "assessments"
            safe_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["run_assessment"]
