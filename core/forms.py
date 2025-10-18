from __future__ import annotations

from html import escape as _escape
from typing import List, Optional, Tuple

import streamlit as st


def progress_rail(current_step: float, total_steps: int) -> None:
    """Render a segmented progress rail with discrete bars for each step.
    
    Args:
        current_step: Current progress (can be fractional, e.g., 1.5 for 50% through step 2)
        total_steps: Total number of steps (creates this many segments)
    """
    if total_steps <= 0:
        return
    
    segments = []
    for i in range(total_steps):
        # Calculate fill percentage for this segment (0-100%)
        if current_step >= i + 1:
            # Fully filled
            fill_pct = 100
        elif current_step > i:
            # Partially filled
            fill_pct = int((current_step - i) * 100)
        else:
            # Not filled
            fill_pct = 0
        
        # Create segment with fill
        segment_class = "mod-rail-segment"
        if fill_pct >= 100:
            segment_class += " is-complete"
        elif fill_pct > 0:
            segment_class += " is-active"
        
        segments.append(
            f'<div class="{segment_class}">'
            f'<div class="mod-rail-segment__fill" style="width:{fill_pct}%"></div>'
            f'</div>'
        )
    
    html = f'<div class="mod-rail-container">{"".join(segments)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def progress_steps(current: int, total: int) -> None:
    """Render discrete steps representing section progress."""
    total = max(1, int(total or 1))
    current = max(0, min(int(current or 0), total - 1))
    items = []
    for idx in range(total):
        classes = ["ps-step"]
        if idx < current:
            classes.append("is-done")
        elif idx == current:
            classes.append("is-current")
        items.append(f'<li class="{" ".join(classes)}"></li>')
    html = '<ul class="ps">{}</ul>'.format("".join(items))
    st.markdown(html, unsafe_allow_html=True)


def chip_group(
    key: str,
    options: List[Tuple[str, str]],
    *,
    label: Optional[str] = None,
    help_text: Optional[str] = None,
) -> str:
    """Render a single-select chip group using styled radio buttons (looks like pills)."""
    # Build label list and value mapping
    labels = [lbl for lbl, val in options]
    label_to_value = {lbl: val for lbl, val in options}
    
    # Get current value and find its label
    current_value = st.session_state.get(key)
    current_label = None
    for lbl, val in options:
        if val == current_value:
            current_label = lbl
            break
    if current_label is None and labels:
        current_label = labels[0]

    # Calculate index - ensure it's always valid to prevent Streamlit from adding blank option
    if current_label and current_label in labels:
        default_index = labels.index(current_label)
    else:
        default_index = 0  # Default to first option if no match
    
    radio_key = f"{key}__radio"
    
    # Add wrapper with HTML/CSS for pill styling
    # Using a unique data attribute so CSS can target it
    st.markdown(
        f'<div class="mod-radio-pills" data-widget="radio-pills" data-key="{key}">',
        unsafe_allow_html=True
    )
    
    if label:
        st.markdown(f'<div class="mod-label">{_escape(label)}</div>', unsafe_allow_html=True)
    if help_text:
        st.markdown(f'<div class="mod-help">{_escape(help_text)}</div>', unsafe_allow_html=True)
    
    # Use native st.radio with horizontal layout - ALWAYS provide valid index
    choice_label = st.radio(
        label=label or "",
        options=labels,
        index=default_index,  # Explicit valid index prevents blank option
        horizontal=True,
        label_visibility="collapsed",
        key=radio_key,
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Update session state with the value (not label)
    selected_value = label_to_value.get(choice_label, choice_label)
    st.session_state[key] = selected_value

    return st.session_state.get(key)


def actions_row(
    *,
    primary: Tuple[str, str],
    secondary: Optional[Tuple[str, str]] = None,
) -> None:
    """Render a row of action buttons that route via core.nav.route_to."""
    from core.nav import route_to  # lazy import to avoid circular dependency

    st.markdown('<div class="sn-app mod-actions">', unsafe_allow_html=True)
    p_label, p_route = primary
    if st.button(p_label, key=f"actions__{p_label}__primary"):
        route_to(p_route)

    if secondary:
        s_label, s_route = secondary
        if st.button(s_label, key=f"actions__{s_label}__secondary"):
            route_to(s_route)

    st.markdown("</div>", unsafe_allow_html=True)
