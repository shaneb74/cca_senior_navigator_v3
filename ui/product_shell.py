"""Simple product shell - no layout.py complexity."""

from __future__ import annotations

import streamlit as st


def product_shell_start() -> None:
    """
    Start product shell - minimal container, no header.
    Products/modules should render their own headers if needed.
    """
    # Just add a minimal CSS reset for product pages
    css = """
    <style>
    /* Remove excessive Streamlit padding for products */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Product-specific container */
    .product-content {
        max-width: 1240px;
        margin: 0 auto;
        padding: 0 24px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def product_shell_end() -> None:
    """End product shell - nothing to do."""
    pass


def product_shell_bg() -> None:
    """Legacy compatibility - does nothing."""
    pass


__all__ = ["product_shell_start", "product_shell_end", "product_shell_bg"]
