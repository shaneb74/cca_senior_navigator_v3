"""
URL Helpers for Navigation & Session Preservation

Provides URL-driven routing with browser back/forward support and session preservation.
All navigation should use route_to() to ensure URL updates and history works correctly.
"""

from __future__ import annotations
from typing import Dict, Any
import streamlit as st

# Canonical query param keys for routing
QP_KEYS = ("page", "product", "module", "step", "uid")


def get_route_from_qp() -> Dict[str, str]:
    """Extract route information from current query parameters.
    
    Returns:
        Dictionary with route keys (page, product, module, step, uid)
    """
    # Get query params (works with Streamlit's query_params API)
    qp = dict(st.query_params)
    
    # Normalize single values (Streamlit query_params returns strings)
    route = {}
    for k in QP_KEYS:
        if k in qp:
            val = qp[k]
            # Handle list values (legacy compatibility)
            if isinstance(val, list):
                val = val[0] if val else None
            if val:
                route[k] = val
    
    return route


def set_route_qp(**parts: str) -> None:
    """Update query parameters with route information.
    
    Merges with current route, drops empty/None values.
    
    Args:
        **parts: Route components (page, product, module, step, uid)
    """
    # Get current route
    cur = get_route_from_qp()
    
    # Merge updates
    cur.update({k: v for k, v in parts.items() if v})
    
    # Remove keys if value is empty/None
    for k, v in list(cur.items()):
        if v in (None, "", "None"):
            cur.pop(k, None)
    
    # Update query params
    st.query_params.clear()
    for k, v in cur.items():
        st.query_params[k] = v


def current_route() -> Dict[str, str]:
    """Get current route from query params with session fallback.
    
    Returns:
        Current route dictionary
    """
    # Prefer query params as source of truth
    qp = get_route_from_qp()
    if qp:
        return qp
    
    # Fallback to session snapshot
    return st.session_state.get("current_route", {})


def route_to(push: bool = True, **parts: str) -> None:
    """Navigate to a new route with history tracking.
    
    Updates URL query parameters and triggers a rerun. Maintains a navigation
    stack for in-app Back button functionality.
    
    Args:
        push: Whether to push current route to history stack (default: True)
        **parts: Route components (page, product, module, step, uid)
    
    Example:
        route_to(page="product", product="cost_planner_v2")
        route_to(page="module", product="cost_planner_v2", module="intro")
    """
    # Initialize navigation stack
    st.session_state.setdefault("_nav_stack", [])
    
    # Get previous route before updating
    prev = current_route()
    
    # Update query params with new route
    set_route_qp(**parts)
    
    # Push to history stack if this is a new navigation
    new_route = current_route()
    if push and prev != new_route and prev:
        st.session_state["_nav_stack"].append(prev)
    
    # Trigger rerun to apply navigation
    st.rerun()


def can_go_back() -> bool:
    """Check if there's navigation history to go back to.
    
    Returns:
        True if navigation stack has entries
    """
    return bool(st.session_state.get("_nav_stack"))


def back_fallback() -> Dict[str, str]:
    """Get sensible fallback route when navigation stack is empty.
    
    Phase 3B: Changed default from hub_concierge to hub_lobby
    
    Returns:
        Default route (Lobby hub)
    """
    return {"page": "hub_lobby"}


def go_back() -> None:
    """Navigate to previous route in history stack.
    
    Pops from navigation stack and updates URL. If stack is empty,
    navigates to fallback route.
    """
    stack = st.session_state.get("_nav_stack", [])
    if stack:
        dest = stack.pop()
        set_route_qp(**dest)
        st.rerun()
    else:
        route_to(push=False, **back_fallback())


def add_uid_to_href(href: str) -> str:
    """Add current UID to href to preserve session across navigation.

    Args:
        href: Original href string (e.g., "?page=faq" or "?page=hub&foo=bar")

    Returns:
        href with uid appended (e.g., "?page=faq&uid=anon_xxxxx")
    """
    if not href or href == "#" or href.startswith("http"):
        return href

    # Get current UID from session_state
    uid = None
    if "anonymous_uid" in st.session_state:
        uid = st.session_state["anonymous_uid"]
    elif "auth" in st.session_state and st.session_state["auth"].get("user_id"):
        uid = st.session_state["auth"]["user_id"]

    if not uid:
        return href

    # Add uid to query string
    separator = "&" if "?" in href else "?"
    return f"{href}{separator}uid={uid}"
