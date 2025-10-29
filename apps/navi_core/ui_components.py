"""
UI Components - Global NAVI visual elements.

Part of Phase 5.2: Global Progress Tracker
Provides reusable UI widgets that appear across all hubs and pages.
"""

import streamlit as st
from typing import Optional
from apps.navi_core.progress_manager import (
    calculate_progress,
    calculate_weighted_progress,
    get_next_unvisited,
    load_progress_config
)


def navi_progress_widget(use_weighted: bool = True, show_next_step: bool = True) -> None:
    """
    Display global progress bar with visual badges for completed sections.
    
    This is a universal component that can be imported and displayed on any page.
    It automatically reads progress from session state and updates in real-time.
    
    Args:
        use_weighted: If True, use weighted progress calculation. Default True.
        show_next_step: If True, show suggested next step. Default True.
        
    Example:
        >>> from apps.navi_core.ui_components import navi_progress_widget
        >>> navi_progress_widget()
    """
    # Calculate progress
    if use_weighted:
        percent, completed = calculate_weighted_progress()
    else:
        percent, completed = calculate_progress()
    
    cfg = load_progress_config()
    total_pages = len(cfg.get("pages", []))
    
    # Header with progress percentage
    st.markdown("### 🧭 Your Journey Progress")
    
    # Progress bar
    st.progress(percent / 100 if percent <= 100 else 1.0)
    st.caption(f"**{len(completed)}** of **{total_pages}** sections completed (**{percent}%**)")
    
    # Check for milestone
    milestone = _get_milestone(percent, cfg)
    if milestone:
        st.success(f"🎉 {milestone['message']}")
    
    # Visual badges for all pages
    _render_page_badges(completed, cfg)
    
    # Next step suggestion
    if show_next_step:
        next_page = get_next_unvisited()
        if next_page:
            st.info(f"💡 **Next Step:** {next_page}")
        elif percent >= 100:
            st.success("🏆 **Journey Complete!** All sections finished.")


def navi_compact_progress(show_percentage: bool = True) -> None:
    """
    Display a compact progress indicator (for sidebars or headers).
    
    Args:
        show_percentage: If True, show percentage number. Default True.
    """
    percent, completed = calculate_weighted_progress()
    
    if show_percentage:
        st.metric(label="Journey Progress", value=f"{percent}%", delta=None)
    
    st.progress(percent / 100 if percent <= 100 else 1.0)


def navi_milestone_badge(percent: int) -> Optional[str]:
    """
    Get milestone badge for a given completion percentage.
    
    Args:
        percent: Completion percentage (0-100)
        
    Returns:
        Badge string or None if no milestone reached
    """
    cfg = load_progress_config()
    milestones = cfg.get("milestones", {})
    
    # Find highest milestone achieved
    # Note: YAML parser loads keys as integers
    achieved = [m for m in milestones.keys() if m <= percent]
    if achieved:
        highest = max(achieved)
        return milestones[highest].get("badge")
    
    return None


def _get_milestone(percent: int, cfg: dict) -> Optional[dict]:
    """
    Check if user has reached a new milestone.
    
    Args:
        percent: Current completion percentage
        cfg: Progress configuration dictionary
        
    Returns:
        Milestone dict or None
    """
    milestones = cfg.get("milestones", {})
    
    # Find exact milestone match
    # Note: YAML parser loads keys as integers
    if percent in milestones:
        return milestones[percent]
    
    return None


def _render_page_badges(completed: set, cfg: dict) -> None:
    """
    Render visual badges showing completion status for all pages.
    
    Args:
        completed: Set of completed page names
        cfg: Progress configuration dictionary
    """
    pages = cfg.get("pages", [])
    
    if not pages:
        return
    
    # Create columns for each page
    num_pages = len(pages)
    cols = st.columns(num_pages)
    
    for i, page in enumerate(pages):
        with cols[i]:
            if page in completed:
                st.markdown("✅")
            else:
                st.markdown("⬜️")
            
            # Shortened labels for compact display
            label = _shorten_page_name(page)
            st.markdown(f"<small>{label}</small>", unsafe_allow_html=True)


def _shorten_page_name(page: str) -> str:
    """
    Shorten page names for compact badge display.
    
    Args:
        page: Full page name
        
    Returns:
        Shortened version for display
    """
    shortenings = {
        "Welcome": "Welcome",
        "For Someone Else": "Setup",
        "Care Preferences": "Care Pref",
        "Cost Calculator": "Costs",
        "Guided Care Plan (GCP)": "GCP",
        "Financial Assessment": "Finance",
        "Move Preferences": "Location",
        "Concierge Hub": "Concierge",
        "Follow-Up": "Follow-Up",
    }
    
    return shortenings.get(page, page[:10])  # Max 10 chars


def navi_progress_summary() -> dict:
    """
    Get complete progress summary for display or analytics.
    
    Returns:
        Dictionary with all progress metrics
    """
    from apps.navi_core.progress_manager import get_progress_stats
    return get_progress_stats()
