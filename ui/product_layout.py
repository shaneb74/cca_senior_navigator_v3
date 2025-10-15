"""Simple product layout - no headers, minimal wrapper."""
from __future__ import annotations

import streamlit as st


def render_product_start() -> None:
    """
    Start a product/module layout with NO header/footer.
    Just a clean container for content.
    """
    # Simply start rendering - no header, no complex wrappers
    # Products will render their own content directly
    pass


def render_product_end() -> None:
    """
    End a product/module layout with NO footer.
    """
    # Nothing to close - products rendered directly
    pass


__all__ = ["render_product_start", "render_product_end"]
