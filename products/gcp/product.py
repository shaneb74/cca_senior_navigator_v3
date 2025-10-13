from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from core.modules.engine import run_module
from products.gcp.module_config import get_config
from layout import render_shell_end, render_shell_start


def render() -> None:
    """Render the Guided Care Plan product using the new module engine."""
    config = get_config()
    
    # Don't show page-level title - module intro has its own title
    render_shell_start("", active_route="gcp")
    
    # Run the module with the new engine
    module_state = run_module(config)
    
    render_shell_end()


def register() -> Dict[str, Any]:
    return {
        "routes": {"product/gcp": render},
        "tile": {
            "key": "gcp",
            "title": "Guided Care Plan",
            "meta": ["≈2 min • Auto-saves"],
            "progress_key": "gcp.progress",
            "unlock_condition": lambda _ss: True,
        },
    }
