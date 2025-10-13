"""Mock authentication for Cost Planner.

This provides a temporary authentication system for development and testing.
Replace with real authentication integration when ready.
"""

import streamlit as st
from typing import Dict, Any


def is_authenticated() -> bool:
    """Check if user is authenticated.
    
    Returns:
        True if user has authenticated, False otherwise
    """
    return st.session_state.get("auth", {}).get("is_authenticated", False)


def require_auth() -> bool:
    """Gate content behind authentication.
    
    Shows authentication prompt if user is not logged in.
    Blocks content rendering until authenticated.
    
    Returns:
        True if authenticated (content should render)
        False if blocked (content should NOT render)
    """
    if is_authenticated():
        return True
    
    # Show auth requirement message
    st.warning("🔒 **Authentication Required**")
    st.markdown("""
    This section requires you to log in to:
    - Save your progress
    - Access personalized financial calculations
    - Securely store sensitive financial data
    
    ---
    
    **For Development:** Click below to simulate authentication.
    """)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🔓 Mock Login", type="primary", use_container_width=True):
            st.session_state.setdefault("auth", {})["is_authenticated"] = True
            st.rerun()
    
    with col2:
        st.caption("*Real authentication will be integrated in production*")
    
    return False


def requires_auth(module_key: str) -> bool:
    """Check if a specific module requires authentication.
    
    Args:
        module_key: Module identifier (e.g., "income_sources", "base")
    
    Returns:
        True if user can access module (either public or authenticated)
        False if access denied (shows auth gate)
    """
    # Define public modules that don't require authentication
    PUBLIC_MODULES = ["base", "recommendation_cost_detail"]
    
    if module_key in PUBLIC_MODULES:
        return True  # Public module, no auth needed
    
    # All other modules require authentication
    return require_auth()


def mock_login_button() -> None:
    """Show mock login/logout controls in sidebar (dev mode only).
    
    This provides easy testing of authenticated vs guest flows.
    Remove or hide in production.
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔧 Dev Tools")
        
        if is_authenticated():
            st.success("✓ Authenticated")
            st.caption("*Logged in as: dev@example.com*")
            if st.button("🔓 Mock Logout", use_container_width=True):
                st.session_state["auth"]["is_authenticated"] = False
                st.rerun()
        else:
            st.info("Not authenticated")
            if st.button("🔒 Mock Login", use_container_width=True):
                st.session_state.setdefault("auth", {})["is_authenticated"] = True
                st.rerun()
        
        st.caption("*Mock authentication for development*")


def get_user_info() -> Dict[str, Any]:
    """Get current user information (mock implementation).
    
    Returns:
        Dict with user info (email, name, etc.)
        Empty dict if not authenticated
    """
    if not is_authenticated():
        return {}
    
    # Mock user data - replace with real user data from auth provider
    return {
        "email": "dev@example.com",
        "name": "Development User",
        "user_id": "mock_user_123",
        "authenticated_at": "2025-10-12T10:00:00Z",
    }
