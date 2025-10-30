"""
Product outcome utilities for displaying product completion results.

Phase 3B: Product outcomes show at-a-glance status on Lobby tiles.
"""

import streamlit as st
from typing import Optional


def get_product_outcome(product_key: str) -> Optional[str]:
    """Return outcome summary for the given product.
    
    Reads from session state to display product completion results
    on Lobby Hub tiles. Examples:
    - "Recommended: Assisted Living"
    - "Estimated cost: $4,500/mo"
    - "Next meeting: Nov 3, 10:00am"
    
    Args:
        product_key: Product identifier (e.g., 'gcp', 'cost_planner', 'pfma')
    
    Returns:
        Outcome string if available, None otherwise
    """
    outcomes = st.session_state.get("product_outcomes", {})
    return outcomes.get(product_key, None)


def set_product_outcome(product_key: str, outcome: str) -> None:
    """Store a product outcome in session state.
    
    Args:
        product_key: Product identifier
        outcome: Outcome text to display
    """
    if "product_outcomes" not in st.session_state:
        st.session_state["product_outcomes"] = {}
    
    st.session_state["product_outcomes"][product_key] = outcome
