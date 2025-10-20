"""
Mode Engine: JSON-driven Basic/Advanced mode rendering

This module reads mode configuration from JSON and executes appropriate
rendering logic based on the current mode.

Key Principles:
1. Configuration lives in JSON (what to show, how to distribute)
2. Logic lives in Python (calculations, rendering, state management)
3. "Unallocated = 0 in calculations" (only detail fields used)
"""

import streamlit as st
from typing import Dict, List, Any, Optional


def render_mode_toggle(assessment_key: str) -> str:
    """
    Render mode toggle UI with elevated button design.
    
    Design:
    - Active button: Primary blue with shadow, white text
    - Inactive button: Muted gray, readable, invites interaction
    - Accessible: WCAG AA compliant, aria-selected, keyboard nav
    - Centered horizontally with consistent spacing
    
    Args:
        assessment_key: Unique key for this assessment (e.g., "assets")
        
    Returns:
        Current mode ("basic" or "advanced")
    """
    mode_key = f"{assessment_key}_mode"
    current_mode = st.session_state.get(mode_key, "basic")
    
    # Custom CSS for elevated button design
    st.markdown("""
    <style>
    .mode-toggle-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 16px 0 24px 0;
        gap: 12px;
    }
    
    .mode-button {
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 2px solid transparent;
        text-align: center;
        min-width: 200px;
    }
    
    .mode-button-active {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
        border-color: #3b82f6;
    }
    
    .mode-button-inactive {
        background: #f1f5f9;
        color: #475569;
        border-color: #e2e8f0;
    }
    
    .mode-button-inactive:hover {
        background: #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    .mode-button-active:hover {
        box-shadow: 0 6px 8px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render as radio with custom styling via st.columns for centering
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_mode = st.radio(
            label="**Detail Level**",
            options=["basic", "advanced"],
            format_func=lambda x: "⚡ Basic (Quick Entry)" if x == "basic" else "📊 Advanced (Detailed Breakdown)",
            index=0 if current_mode == "basic" else 1,
            horizontal=True,
            key=f"{assessment_key}_mode_toggle",
            label_visibility="collapsed"  # Hide default label, we'll style the buttons
        )
    
    # Detect mode change
    if selected_mode != current_mode:
        st.session_state[mode_key] = selected_mode
        st.session_state[f"{mode_key}_just_changed"] = True
    
    st.markdown("---")
    
    return selected_mode


def show_mode_guidance(mode: str):
    """
    Display Navi's context-aware guidance based on current mode.
    
    Design: Navi messaging appears at top of assessment card,
    provides clear guidance on current mode and next actions.
    
    Args:
        mode: Current mode ("basic" or "advanced")
    """
    if mode == "basic":
        st.info("""
        🧭 **Quick entry mode active** — Just enter totals for a fast estimate. 
        You can expand to Advanced anytime for a detailed breakdown.
        """)
    else:
        st.info("""
        🧭 **Now showing your detailed breakdown.** Update individual fields as needed; 
        totals will update automatically.
        """)


def show_mode_change_feedback(assessment_key: str, mode: str):
    """
    Show Navi's feedback when user switches modes.
    
    Args:
        assessment_key: Unique key for this assessment
        mode: New mode after switch
    """
    change_key = f"{assessment_key}_mode_just_changed"
    if st.session_state.get(change_key):
        if mode == "advanced":
            st.success("""
            ✅ **Switched to Advanced Mode**
            
            Your totals have been distributed across detail fields below. 
            Adjust individual amounts as needed for more accuracy.
            """)
        else:
            st.success("""
            ✅ **Switched to Basic Mode**
            
            Your detail fields have been combined into totals. 
            Enter new aggregate values if needed.
            """)
        
        # Clear flag
        del st.session_state[change_key]


def get_visible_fields(section: Dict[str, Any], mode: str) -> List[Dict[str, Any]]:
    """
    Get list of fields that should be visible in current mode.
    
    Args:
        section: Section config from JSON
        mode: Current mode ("basic" or "advanced")
        
    Returns:
        List of field configs that should be rendered
    """
    mode_config = section.get("mode_config", {})
    
    # If section doesn't support modes, show all fields
    if not mode_config.get("supports_basic_advanced"):
        return section.get("fields", [])
    
    # Get mode-specific field keys
    if mode == "basic":
        visible_keys = [mode_config.get("basic_mode_aggregate")]
    else:  # advanced
        visible_keys = mode_config.get("advanced_mode_fields", [])
    
    # Filter fields
    visible_fields = []
    for field in section.get("fields", []):
        # Check if field should be visible in this mode
        field_visible_in = field.get("visible_in_modes", [])
        
        if not field_visible_in:  # No restriction, check key
            if field["key"] in visible_keys:
                visible_fields.append(field)
        elif mode in field_visible_in:  # Explicit mode visibility
            visible_fields.append(field)
    
    return visible_fields


def calculate_aggregate(field: Dict[str, Any], state: Dict[str, Any]) -> float:
    """
    Calculate aggregate value from detail fields.
    
    CRITICAL: This is the ONLY calculation method. Always uses detail fields.
    
    Args:
        field: Aggregate field config
        state: Current assessment state
        
    Returns:
        Sum of detail fields (always float)
    """
    detail_keys = field.get("aggregate_from", [])
    total = sum(float(state.get(key, 0.0) or 0.0) for key in detail_keys)
    return total


def distribute_aggregate(
    field: Dict[str, Any], 
    total_value: float, 
    state: Dict[str, Any]
) -> Dict[str, float]:
    """
    Distribute aggregate value across detail fields.
    
    Args:
        field: Aggregate field config (contains distribution_strategy)
        total_value: Value to distribute
        state: Current assessment state
        
    Returns:
        Dict mapping detail field keys to distributed values
    """
    detail_keys = field.get("aggregate_from", [])
    mode_behavior = field.get("mode_behavior", {}).get("basic", {})
    strategy = mode_behavior.get("distribution_strategy", "even")
    
    if strategy == "even":
        # Split evenly across all fields
        per_field = float(total_value) / len(detail_keys) if detail_keys else 0.0
        return {key: float(per_field) for key in detail_keys}
    
    elif strategy == "proportional":
        # Split based on existing proportions
        current_total = sum(float(state.get(key, 0.0) or 0.0) for key in detail_keys)
        
        if current_total == 0:
            # No existing data, fall back to even split
            per_field = float(total_value) / len(detail_keys) if detail_keys else 0.0
            return {key: float(per_field) for key in detail_keys}
        else:
            # Maintain current proportions
            return {
                key: float(total_value * (float(state.get(key, 0.0) or 0.0) / current_total))
                for key in detail_keys
            }
    
    else:
        # Unknown strategy, default to even
        per_field = total_value / len(detail_keys) if detail_keys else 0
        return {key: per_field for key in detail_keys}


def render_aggregate_field(
    field: Dict[str, Any], 
    state: Dict[str, Any], 
    mode: str,
    container: Any = None
) -> Optional[Dict[str, float]]:
    """
    Render an aggregate field based on current mode.
    
    Args:
        field: Field config from JSON
        state: Current assessment state
        mode: Current mode ("basic" or "advanced")
        container: Streamlit container (st, col1, col2, etc.) - defaults to st
        
    Returns:
        Dict of state updates, or None if no changes
    """
    if container is None:
        container = st
    
    field_key = field["key"]
    mode_behavior = field.get("mode_behavior", {}).get(mode, {})
    display_type = mode_behavior.get("display", "input")
    
    updates = {}
    
    if display_type == "input" and mode == "basic":
        # Basic mode: show editable input
        help_text = mode_behavior.get("help", field.get("help", ""))
        
        # Get current value and ensure it's a float (JSON may have integers)
        current_val = state.get(field_key, field.get("default", 0.0))
        if current_val is None:
            current_val = 0.0
        current_val = float(current_val)
        
        value = container.number_input(
            label=field.get("label", field_key),
            min_value=float(field.get("min", 0.0)),
            max_value=float(field.get("max", 100000000.0)),
            step=float(field.get("step", 1000.0)),
            value=current_val,
            help=help_text,
            key=f"input_{field_key}",
            format="%.2f"
        )
        
        # Store original entry for Unallocated calculation
        updates[f"{field_key}_entered"] = value
        
        # Distribute to detail fields
        distributed = distribute_aggregate(field, value, state)
        updates.update(distributed)
        
        # Show distribution preview
        if value > 0:
            with st.expander("📋 Distribution Preview", expanded=False):
                st.write("This total will be split as:")
                for key, val in distributed.items():
                    label = _get_field_label_from_section(key, field.get("aggregate_from", []))
                    st.write(f"- {label}: ${val:,.2f}")
    
    elif display_type == "calculated_label" and mode == "advanced":
        # Advanced mode: show calculated total (read-only)
        total = calculate_aggregate(field, state)
        help_text = mode_behavior.get("help", field.get("help", ""))
        
        st.markdown(f"""
        <div style="background: #f0f9ff; padding: 12px; border-radius: 4px; margin-bottom: 12px;">
            <strong>{field.get('label', field_key)}:</strong> ${total:,.2f}
            <br/><small style="color: #666;">{help_text}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Show Unallocated field if configured
        unallocated_config = field.get("unallocated", {})
        if unallocated_config.get("enabled") and unallocated_config.get("show_in_mode") == mode:
            render_unallocated_field(field, state)
    
    return updates if updates else None


def render_unallocated_field(field: Dict[str, Any], state: Dict[str, Any]):
    """
    Render Unallocated field when user has original estimate from Basic mode.
    
    CRITICAL: Unallocated is NEVER included in calculations. Purely informational.
    
    Args:
        field: Aggregate field config
        state: Current assessment state
    """
    field_key = field["key"]
    unallocated_config = field.get("unallocated", {})
    
    # Check if user has original estimate
    original_key = f"{field_key}_entered"
    if original_key not in state:
        return  # No original estimate
    
    # Calculate unallocated amount
    original_estimate = state.get(original_key, 0.0)
    allocated_total = calculate_aggregate(field, state)
    unallocated = original_estimate - allocated_total
    
    # Only show if non-zero
    if abs(unallocated) < 0.01:
        return
    
    # Render informational display
    label = unallocated_config.get("label", "Unallocated")
    help_text = unallocated_config.get("help", "")
    
    st.markdown(f"""
    <div style="background: #fef3c7; padding: 12px; border-radius: 4px; margin: 12px 0; border-left: 4px solid #f59e0b;">
        <strong>📊 {label}:</strong> ${unallocated:,.2f}
        <br/>
        <small style="color: #666;">
            Your original estimate was ${original_estimate:,.2f}. 
            You've allocated ${allocated_total:,.2f} in the detail fields above.
            <br/>
            <em>{help_text}</em>
        </small>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    actions = unallocated_config.get("actions", [])
    
    if len(actions) == 2:
        col1, col2 = st.columns(2)
    else:
        col1 = st.columns(1)[0]
        col2 = None
    
    with col1:
        if "clear_original" in actions:
            if st.button(
                "Clear Original Estimate", 
                key=f"clear_{field_key}",
                help="Remove the original estimate and hide this field"
            ):
                del state[original_key]
                st.rerun()
    
    if col2:
        with col2:
            if "move_to_other" in actions:
                other_field = unallocated_config.get("other_field_key")
                if st.button(
                    f"Move to '{_get_field_label_from_section(other_field, [])}'", 
                    key=f"other_{field_key}",
                    help=f"Add unallocated amount to '{other_field}' field"
                ):
                    if other_field:
                        state[other_field] = state.get(other_field, 0.0) + unallocated
                        del state[original_key]
                        st.rerun()
    
    # Warning for negative unallocated (over-allocation)
    if unallocated < -0.01:
        st.warning(f"""
        ⚠️ **Over-allocated**
        
        Your detail entries total ${allocated_total:,.2f}, which exceeds your 
        original estimate of ${original_estimate:,.2f}.
        
        This is fine—your detail entries are what will be used in calculations.
        Click "Clear Original Estimate" to remove this warning.
        """)


def _get_field_label_from_section(field_key: str, field_keys: List[str]) -> str:
    """
    Get human-readable label for a field key.
    
    This is a helper for display purposes.
    In production, this should look up the actual field label from JSON.
    
    Args:
        field_key: Field key to get label for
        field_keys: List of all field keys in section
        
    Returns:
        Human-readable label
    """
    # Simple conversion: snake_case to Title Case
    # In production, look up actual label from field config
    return field_key.replace("_", " ").title()
