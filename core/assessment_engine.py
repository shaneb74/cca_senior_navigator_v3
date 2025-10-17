"""
Assessment Engine - JSON-driven assessment rendering for Cost Planner v2.

This engine renders financial assessments from JSON configurations, similar to
the module engine but specialized for assessment-level state management.

Pattern: Follows core/modules/engine.py architecture
State: Stored in session_state under assessment-specific keys
Navigation: Section-based flow within assessments
"""

from __future__ import annotations

import json
import time
from html import escape as H
from typing import Any, Dict, List, Optional

import streamlit as st

from core.events import log_event
from core.session_store import safe_rerun
from core.ui import render_navi_panel_v2


def run_assessment(
    assessment_key: str,
    assessment_config: Dict[str, Any],
    product_key: str = "cost_planner_v2"
) -> Dict[str, Any]:
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
    is_intro = (section_type == "intro")
    is_results = (section_type == "results")
    
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
            state=state
        )
    
    # ========================================================================
    # SECTION HEADER
    # ========================================================================
    _render_section_header(
        assessment_config=assessment_config,
        current_section=current_section,
        section_index=section_index,
        total_sections=len(sections)
    )
    
    # ========================================================================
    # FIELDS RENDERING
    # ========================================================================
    if not is_results:
        new_values = _render_fields(current_section, state)
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
            product_key=product_key
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
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
        product_key=product_key
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    return state


def _render_navi_guidance(
    assessment_config: Dict[str, Any],
    current_section: Dict[str, Any],
    section_index: int,
    total_sections: int,
    state: Dict[str, Any]
) -> None:
    """Render Navi panel with contextual guidance."""
    
    # Get assessment metadata
    title = assessment_config.get("title", "Financial Assessment")
    
    # Calculate progress
    progress_sections = [s for s in assessment_config.get("sections", []) 
                         if s.get("type") != "intro" and s.get("type") != "results"]
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
        context_chips.append({
            'label': f"Step {current_progress + 1} of {total_progress}",
            'sublabel': None
        })
    
    render_navi_panel_v2(
        title=navi_title,
        reason=navi_reason,
        encouragement={
            'icon': '💡',
            'text': 'Take your time. You can save and come back anytime.',
            'status': 'active'
        },
        context_chips=context_chips,
        primary_action={'label': '', 'route': ''},
        variant="module"
    )


def _render_section_header(
    assessment_config: Dict[str, Any],
    current_section: Dict[str, Any],
    section_index: int,
    total_sections: int
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
        unsafe_allow_html=True
    )


def _render_fields(section: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render form fields for current section.
    
    Supports field types:
    - currency: st.number_input with $ formatting
    - select: st.selectbox
    - checkbox: st.checkbox
    - multiselect: st.multiselect
    - text: st.text_input
    - date: st.date_input
    
    Handles:
    - visible_if conditions
    - default values
    - min/max constraints
    - help text
    """
    new_values: Dict[str, Any] = {}
    fields = section.get("fields", [])
    
    # Check if section uses two-column layout
    layout = section.get("layout", "simple")
    
    if layout == "two_column":
        col1, col2 = st.columns(2)
        columns = {1: col1, 2: col2}
    else:
        columns = None
    
    for field in fields:
        # Check visibility
        if not _is_field_visible(field, state):
            continue
        
        # Get field properties
        key = field.get("key")
        label = field.get("label", key)
        field_type = field.get("type", "text")
        required = field.get("required", False)
        help_text = field.get("help")
        default = field.get("default")
        
        # Get current value or default
        current_value = state.get(key, default)
        
        # Render appropriate widget
        if field_type == "currency":
            min_val = field.get("min", 0)
            max_val = field.get("max", 10000000)
            step = field.get("step", 100)
            
            # Determine which column to render in
            if columns:
                column_num = field.get("column", 1)
                container = columns.get(column_num, columns[1])
            else:
                container = st
            
            value = container.number_input(
                label=f"{label} {'*' if required else ''}",
                min_value=min_val,
                max_value=max_val,
                value=current_value if current_value is not None else min_val,
                step=step,
                format="%d",
                help=help_text,
                key=f"field_{key}"
            )
            new_values[key] = value
            
        elif field_type == "select":
            options = field.get("options", [])
            option_labels = [opt.get("label", opt.get("value")) for opt in options]
            option_values = [opt.get("value", opt.get("label")) for opt in options]
            
            # Find current index
            try:
                current_index = option_values.index(current_value) if current_value else 0
            except ValueError:
                current_index = 0
            
            # Determine which column to render in
            if columns:
                column_num = field.get("column", 1)
                container = columns.get(column_num, columns[1])
            else:
                container = st
            
            selected_label = container.selectbox(
                label=f"{label} {'*' if required else ''}",
                options=option_labels,
                index=current_index,
                help=help_text,
                key=f"field_{key}"
            )
            
            # Map back to value
            selected_index = option_labels.index(selected_label)
            value = option_values[selected_index]
            new_values[key] = value
            
        elif field_type == "checkbox":
            # Determine which column to render in
            if columns:
                column_num = field.get("column", 1)
                container = columns.get(column_num, columns[1])
            else:
                container = st
            
            value = container.checkbox(
                label=label,
                value=bool(current_value),
                help=help_text,
                key=f"field_{key}"
            )
            new_values[key] = value
            
        elif field_type == "multiselect":
            options = field.get("options", [])
            option_labels = [opt.get("label", opt.get("value")) for opt in options]
            
            # Determine which column to render in
            if columns:
                column_num = field.get("column", 1)
                container = columns.get(column_num, columns[1])
            else:
                container = st
            
            value = container.multiselect(
                label=f"{label} {'*' if required else ''}",
                options=option_labels,
                default=current_value if isinstance(current_value, list) else [],
                help=help_text,
                key=f"field_{key}"
            )
            new_values[key] = value
            
        elif field_type == "date":
            # Determine which column to render in
            if columns:
                column_num = field.get("column", 1)
                container = columns.get(column_num, columns[1])
            else:
                container = st
            
            value = container.date_input(
                label=f"{label} {'*' if required else ''}",
                value=current_value,
                help=help_text,
                key=f"field_{key}"
            )
            new_values[key] = value
            
        else:  # text
            # Determine which column to render in
            if columns:
                column_num = field.get("column", 1)
                container = columns.get(column_num, columns[1])
            else:
                container = st
            
            value = container.text_input(
                label=f"{label} {'*' if required else ''}",
                value=str(current_value) if current_value else "",
                help=help_text,
                key=f"field_{key}"
            )
            new_values[key] = value
    
    return new_values


def _is_field_visible(field: Dict[str, Any], state: Dict[str, Any]) -> bool:
    """Check if field should be visible based on visible_if condition."""
    visible_if = field.get("visible_if")
    if not visible_if:
        return True
    
    # Check field condition
    check_field = visible_if.get("field")
    if not check_field:
        return True
    
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


def _render_info_boxes(info_boxes: List[Dict[str, Any]]) -> None:
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
    assessment_config: Dict[str, Any],
    state: Dict[str, Any],
    assessment_key: str
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


def _evaluate_formula(formula: str, state: Dict[str, Any]) -> float:
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
    assessment_config: Dict[str, Any],
    state_key: str,
    section_index: int,
    total_sections: int,
    current_section: Dict[str, Any],
    state: Dict[str, Any],
    product_key: str
) -> None:
    """Render navigation buttons (Back, Continue, Save & Exit)."""
    
    is_first = (section_index == 0)
    is_last = (section_index == total_sections - 1)
    
    # Check required fields
    required_fields = [f for f in current_section.get("fields", []) 
                       if f.get("required") and _is_field_visible(f, state)]
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
            if st.button("← Back", key=f"back_{assessment_key}", type="secondary", use_container_width=True):
                prev_section = max(0, section_index - 1)
                st.session_state[f"{state_key}._section"] = prev_section
                safe_rerun()
    
    with col2:
        # Continue button
        continue_label = "View Results" if is_last else "Continue →"
        if st.button(continue_label, key=f"continue_{assessment_key}", type="primary", use_container_width=True):
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
                    log_event("assessment.completed", {
                        "product": product_key,
                        "assessment": assessment_key
                    })
                
                safe_rerun()
    
    with col3:
        # Back to Hub button
        if st.button("← Back to Hub", key=f"hub_{assessment_key}", type="secondary", use_container_width=True):
            # Clear current assessment and return to assessment hub
            st.session_state.pop(f"{product_key}_current_assessment", None)
            st.session_state[f"{product_key}_step"] = "assessments"
            safe_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def _render_results_navigation(
    assessment_key: str,
    state_key: str,
    section_index: int,
    product_key: str
) -> None:
    """Render navigation buttons for results page."""
    
    st.markdown('<div class="sn-app mod-actions">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Review Answers button - go back to first question section
        if st.button("← Review Answers", key=f"review_{assessment_key}", type="secondary", use_container_width=True):
            # Find first non-intro section
            st.session_state[f"{state_key}._section"] = 1  # Skip intro (0), go to first questions (1)
            safe_rerun()
    
    with col2:
        # Back to Hub button
        if st.button("← Back to Hub", key=f"hub_results_{assessment_key}", type="primary", use_container_width=True):
            # Clear current assessment and return to assessment hub
            st.session_state.pop(f"{product_key}_current_assessment", None)
            st.session_state[f"{product_key}_step"] = "assessments"
            safe_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


__all__ = ["run_assessment"]
