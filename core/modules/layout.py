from __future__ import annotations

from html import escape as _escape
from typing import Dict

import streamlit as st


def header(step_index: int, total: int, title: str, subtitle: str | None = None) -> None:
    # Calculate progress percentage
    progress_pct = ((step_index + 1) / total) * 100 if total > 0 else 0
    
    dots = "".join(
        [
            f"<span class='step-pill{' is-active' if i == step_index else ''}'></span>"
            for i in range(total)
        ]
    )
    subtitle_html = f"<div class='lead'>{_escape(subtitle)}</div>" if subtitle else ""
    
    # Add blue progress bar
    progress_bar_html = f"""
        <div class="mod-progress-rail">
          <div class="mod-progress-fill" style="width: {progress_pct:.1f}%"></div>
        </div>
    """
    
    st.markdown(
        f"""
        <div class="mod-head">
          {progress_bar_html}
          <div class="mod-steps">{dots}</div>
          <div class="mod-head-row">
            <a class="mod-back" href="javascript:history.back()">← Back</a>
            <h2 class="h2">{_escape(title)}</h2>
          </div>
          {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def actions(next_label: str = "Continue", skip_label: str | None = "Skip", show_save_exit: bool = True, is_intro: bool = False, show_back: bool = False, step_index: int = 0, config = None) -> tuple[bool, bool, bool, bool, bool]:
    """Render module action buttons with simplified, centered layout.
    
    Args:
        next_label: Label for primary action button
        skip_label: Label for skip button (None to hide) - DEPRECATED, not used
        show_save_exit: Whether to show Save & Continue Later text link
        is_intro: If True, hide Save & Continue Later (nothing to save yet)
        show_back: If True, show Back text link above Save & Continue Later
        step_index: Current step index (for back button navigation)
        config: Module config (for back button state management)
    
    Returns:
        (next_clicked, skip_clicked, save_exit_clicked, back_clicked, back_to_hub_clicked)
    """
    st.markdown('<div class="sn-app mod-actions">', unsafe_allow_html=True)
    
    # Primary action - centered Continue button (max 400px)
    next_clicked = st.button(
        next_label, 
        key="_mod_next", 
        type="primary", 
        use_container_width=True,
        help=None
    )
    
    # Back button - small text link, appears above Save & Continue Later
    back_clicked = False
    if show_back:
        st.markdown('<div class="mod-back-prev-wrapper">', unsafe_allow_html=True)
        back_clicked = st.button(
            "← Back to Previous Question",
            key="_mod_back_prev",
            type="secondary",
            use_container_width=False,
            help=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Save & Continue Later - small text link
    save_exit_clicked = False
    if show_save_exit and not is_intro:
        st.markdown('<div class="mod-save-exit-wrapper">', unsafe_allow_html=True)
        save_exit_clicked = st.button(
            "💾 Save & Continue Later",
            key="_mod_save_exit",
            type="secondary",
            use_container_width=False,
            help=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Back to hub - small text link at bottom
    st.markdown('<div class="mod-back-hub-wrapper">', unsafe_allow_html=True)
    back_to_hub_clicked = st.button(
        "← Back to Hub",
        key="_mod_back_hub",
        type="secondary",
        use_container_width=False,
        help=None
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Skip functionality removed - not needed in current design
    skip_clicked = False
    
    st.markdown('</div>', unsafe_allow_html=True)
    return next_clicked, skip_clicked, save_exit_clicked, back_clicked, back_to_hub_clicked


def bottom_summary(items: Dict[str, str]) -> None:
    if not items:
        return
    chips = "".join(
        f"<div class='sum-item'><div class='meta'>{_escape(k)}</div><div class='value'>{_escape(v)}</div></div>"
        for k, v in items.items()
    )
    st.markdown(
        f"<div class='mod-bottom'>{chips}</div>",
        unsafe_allow_html=True,
    )


__all__ = ["header", "actions", "bottom_summary"]
