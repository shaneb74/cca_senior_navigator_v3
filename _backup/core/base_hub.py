from __future__ import annotations

from typing import Any, Dict

import streamlit as st
from ui.dashboard import render_dashboard


class BaseHub:
    """Base class for hub pages that render the shared dashboard."""

    def __init__(self, title: str, icon: str, description: str) -> None:
        self.title = title
        self.icon = icon
        self.description = description

    def build_dashboard(self) -> Dict[str, Any]:
        """Return kwargs for `ui.dashboard.render_dashboard`."""
        raise NotImplementedError("Hub subclasses must implement build_dashboard()")

    def render(self) -> None:
        st.set_page_config(page_title=self.title, layout="wide")
        st.markdown(
            """
            <style>
              div.block-container { padding-top: 1.2rem; }
              .dashboard-head { padding-top: 0; padding-bottom: 0; margin: 0; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        dashboard_kwargs = self.build_dashboard()

        defaults: Dict[str, Any] = {
            "title": dashboard_kwargs.get("title", self.title),
            "subtitle": dashboard_kwargs.get("subtitle", self.description),
        }
        merged: Dict[str, Any] = {**defaults, **dashboard_kwargs}
        merged.setdefault("cards", [])
        if not merged.get("subtitle"):
            merged.pop("subtitle", None)
        if not merged.get("callout"):
            merged.pop("callout", None)
        if not merged.get("chips"):
            merged.pop("chips", None)

        render_dashboard(**merged)


def status_label(status: str) -> str:
    lookup = {
        "new": "Not started",
        "in_progress": "In progress",
        "complete": "Complete",
    }
    return lookup.get(status, status.replace("_", " ").title())


__all__ = ["BaseHub", "status_label"]
