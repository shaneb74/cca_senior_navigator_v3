from __future__ import annotations

from html import escape as html_escape
from typing import Optional

import streamlit as st

COMPACT_THRESH = 0.8  # when both core flows hit 80%+, shrink the guide


def _is_compact_by_progress() -> bool:
    gcp = float(st.session_state.get("gcp", {}).get("progress", 0.0) or 0.0)
    cost = float(st.session_state.get("cost", {}).get("progress", 0.0) or 0.0)
    return gcp >= COMPACT_THRESH and cost >= COMPACT_THRESH


def compute_hub_guide(hub_key: str, *, force_compact: Optional[bool] = None) -> str:
    person = html_escape(str(st.session_state.get("person_name", "John")))

    if force_compact is None:
        compact = _is_compact_by_progress()
    else:
        compact = bool(force_compact)

    classes = "hub-guide" + (" is-compact" if compact else "")

    if compact:
        title = f"{person}'s plan is underway"
        text = "Keep sharing updates and reviewing your plan. You can reopen the tools anytime."
        ctas = """
          <a href="?go=pfma_updates" class="btn btn--secondary">Share updates</a>
          <a href="?go=gcp_view" class="btn btn--secondary">Review plan</a>
        """
    else:
        title = f"Let's kick off {person}'s plan."
        text = "Start the Guided Care Plan to get a recommendation, then estimate costs with the Cost Planner."
        ctas = """
          <a href="?go=gcp_start" class="btn btn--primary">Start Guided Care Plan</a>
          <a href="?go=cost_open" class="btn btn--secondary">Open Cost Planner</a>
        """

    html = f"""
    <section class="{classes}">
      <div class="hub-guide__eyebrow">ADVISOR INSIGHT</div>
      <h2 class="hub-guide__title">{title}</h2>
      <p class="hub-guide__text">{text}</p>
      <div class="hub-guide__actions">{ctas}</div>
    </section>
    """

    return html.strip()


__all__ = ["compute_hub_guide", "_is_compact_by_progress", "COMPACT_THRESH"]
