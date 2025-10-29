"""
Progress Manager - Tracks journey completion and calculates overall progress.

Part of Phase 5.2: Global Progress Tracker
Provides persistent progress tracking across all hubs and pages.
"""

import streamlit as st
import yaml
from pathlib import Path
from typing import Tuple, Set, Optional


# Path to progress configuration file
PROGRESS_FILE = Path(__file__).parent / "config" / "progress.yaml"


def load_progress_config() -> dict:
    """
    Load progress configuration from YAML file.
    
    Returns:
        Dictionary with pages, stages, and weights
        
    Raises:
        FileNotFoundError: If progress.yaml doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    if not PROGRESS_FILE.exists():
        raise FileNotFoundError(f"Progress config not found: {PROGRESS_FILE}")
    
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def mark_page_complete(page: str) -> Set[str]:
    """
    Mark a hub/page as visited and completed.
    
    Args:
        page: Name of the page/hub to mark as complete
        
    Returns:
        Updated set of completed pages
        
    Example:
        >>> mark_page_complete("Welcome")
        {'Welcome'}
        >>> mark_page_complete("Care Preferences")
        {'Welcome', 'Care Preferences'}
    """
    completed = st.session_state.get("_navi_completed_pages", set())
    # Create new set to trigger session_state update
    completed = completed.copy()
    completed.add(page)
    st.session_state["_navi_completed_pages"] = completed
    return completed


def calculate_progress() -> Tuple[int, Set[str]]:
    """
    Calculate overall journey completion percentage.
    
    Returns:
        Tuple of (percentage: int, completed_pages: Set[str])
        
    Example:
        >>> mark_page_complete("Welcome")
        >>> calculate_progress()
        (14, {'Welcome'})  # 1 of 7 pages = ~14%
    """
    cfg = load_progress_config()
    total = len(cfg.get("pages", []))
    completed = st.session_state.get("_navi_completed_pages", set())
    
    if total == 0:
        return 0, completed
    
    percent = int((len(completed) / total) * 100)
    return percent, completed


def calculate_weighted_progress() -> Tuple[int, Set[str]]:
    """
    Calculate weighted journey completion percentage.
    
    Uses weights from progress.yaml to give more importance to key pages.
    
    Returns:
        Tuple of (weighted_percentage: int, completed_pages: Set[str])
    """
    cfg = load_progress_config()
    weights = cfg.get("weights", {})
    completed = st.session_state.get("_navi_completed_pages", set())
    
    if not weights:
        # Fallback to simple calculation if no weights defined
        return calculate_progress()
    
    total_weight = sum(weights.values())
    completed_weight = sum(weights.get(page, 0) for page in completed)
    
    if total_weight == 0:
        return 0, completed
    
    percent = int((completed_weight / total_weight) * 100)
    return percent, completed


def get_next_unvisited() -> Optional[str]:
    """
    Return the next hub/page the user hasn't completed yet.
    
    Returns:
        Name of next unvisited page, or None if all completed
        
    Example:
        >>> mark_page_complete("Welcome")
        >>> get_next_unvisited()
        'Care Preferences'
    """
    cfg = load_progress_config()
    completed = st.session_state.get("_navi_completed_pages", set())
    
    for page in cfg.get("pages", []):
        if page not in completed:
            return page
    
    return None  # All pages completed


def get_pages_for_stage(stage: str) -> list:
    """
    Get list of pages associated with a journey stage.
    
    Args:
        stage: Journey stage name (e.g., "Awareness", "Assessment")
        
    Returns:
        List of page names for that stage
    """
    cfg = load_progress_config()
    stages = cfg.get("stages", {})
    return stages.get(stage, [])


def reset_progress() -> None:
    """
    Reset all progress tracking (for testing or new journey).
    
    Clears completed pages from session state.
    """
    if "_navi_completed_pages" in st.session_state:
        del st.session_state["_navi_completed_pages"]


def get_progress_stats() -> dict:
    """
    Get detailed progress statistics for analytics.
    
    Returns:
        Dictionary with completion metrics
    """
    cfg = load_progress_config()
    percent, completed = calculate_progress()
    weighted_percent, _ = calculate_weighted_progress()
    total_pages = len(cfg.get("pages", []))
    next_page = get_next_unvisited()
    
    return {
        "percent": percent,
        "weighted_percent": weighted_percent,
        "completed_count": len(completed),
        "total_count": total_pages,
        "completed_pages": list(completed),
        "next_unvisited": next_page,
    }
