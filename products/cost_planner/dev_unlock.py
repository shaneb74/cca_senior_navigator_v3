"""
Development utility to temporarily unlock Cost Planner for testing.

This script enables the cost_planner_enabled flag in session state,
allowing the Cost Planner tile to appear in the Concierge hub.

Usage:
    This should be imported and called in app.py during development,
    or manually invoked in a notebook/REPL session.
"""

import streamlit as st


def enable_cost_planner_for_testing() -> None:
    """
    Enable Cost Planner tile in Concierge hub for development/testing.
    
    Sets the 'cost_planner_enabled' flag to True in the handoff data,
    which makes the Cost Planner tile visible per additional_services.py logic.
    """
    # Ensure handoff structure exists
    if "handoff" not in st.session_state:
        st.session_state["handoff"] = {}
    
    # Set the flag that enables Cost Planner tile visibility
    # This mimics what MCIP/Hub Guide would do when approving the product
    if "gcp" not in st.session_state["handoff"]:
        st.session_state["handoff"]["gcp"] = {}
    
    if "flags" not in st.session_state["handoff"]["gcp"]:
        st.session_state["handoff"]["gcp"]["flags"] = {}
    
    st.session_state["handoff"]["gcp"]["flags"]["cost_planner_enabled"] = True


def disable_cost_planner() -> None:
    """Disable Cost Planner tile (revert to production behavior)."""
    if "handoff" in st.session_state:
        gcp_data = st.session_state["handoff"].get("gcp", {})
        flags = gcp_data.get("flags", {})
        if "cost_planner_enabled" in flags:
            del flags["cost_planner_enabled"]


def is_cost_planner_enabled() -> bool:
    """Check if Cost Planner is currently enabled."""
    handoff = st.session_state.get("handoff", {})
    gcp_data = handoff.get("gcp", {})
    flags = gcp_data.get("flags", {})
    return flags.get("cost_planner_enabled", False)


def show_dev_controls() -> None:
    """Show sidebar controls for enabling/disabling Cost Planner during dev."""
    with st.sidebar:
        st.divider()
        st.caption("🛠️ **Development Controls**")
        
        enabled = is_cost_planner_enabled()
        
        if enabled:
            st.success("✅ Cost Planner: **Enabled**")
            if st.button("🔒 Lock Cost Planner", use_container_width=True):
                disable_cost_planner()
                st.rerun()
        else:
            st.warning("🔒 Cost Planner: **Locked**")
            if st.button("🔓 Unlock Cost Planner", use_container_width=True):
                enable_cost_planner_for_testing()
                st.rerun()
