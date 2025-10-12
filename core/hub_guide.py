from __future__ import annotations

from html import escape as html_escape
from typing import Any, Dict, Optional

import streamlit as st

COMPACT_THRESH = 0.8  # when both core flows hit 80%+, shrink the guide


def _is_compact_by_progress() -> bool:
    gcp = float(st.session_state.get("gcp", {}).get("progress", 0.0) or 0.0)
    cost = float(st.session_state.get("cost", {}).get("progress", 0.0) or 0.0)
    return gcp >= COMPACT_THRESH and cost >= COMPACT_THRESH


def partners_intel_from_state(state: Dict[str, Any]) -> str:
    gcp = state.get("gcp", {}) or {}
    care = str(gcp.get("care_tier") or "").lower()
    flags = gcp.get("flags") or {}
    lines: list[str] = []

    if care in {"in_home", "independent", "stay_home"}:
        lines.append(
            "Start with Home Care, Home Safety, and Technology partners for at-home support."
        )
    if care in {"assisted_living", "memory_care", "memory_care_high_acuity"}:
        lines.append("Planning a move? Explore Legal & Financial and Medical Equipment partners.")
    if flags.get("meds_management_needed"):
        lines.append(
            "Medication management flagged. Consider Omcare for remote dispensing and adherence."
        )
    if flags.get("fall_risk"):
        lines.append("Fall risk identified. Safety and mobility partners may help reduce risk.")

    if not lines:
        return "Browse partners by category or search for a need."
    return "<br/>".join(html_escape(line) for line in lines)


def compute_hub_guide(
    hub_key: str,
    hub_order: Optional[Dict[str, Any]] = None,
    *,
    extra_panel: Optional[str] = None,
    force_compact: Optional[bool] = None,
) -> str:
    content: list[str] = []
    if hub_order:
        ordered = list(hub_order.get("ordered_products") or [])
        next_step = hub_order.get("next_step")
        total = hub_order.get("total")
        reason = hub_order.get("reason")
        next_route = hub_order.get("next_route")

        if reason:
            content.append(f'<div class="mcip-msg">{html_escape(str(reason))}</div>')

        if next_step and next_step in ordered:
            idx = ordered.index(next_step) + 1
            step_txt = f"Next step: {idx}"
            if total:
                step_txt += f" of {total}"
            content.append(f'<div class="mcip-sub">{html_escape(step_txt)}</div>')
            route = next_route or f"/product/{next_step}"
            content.append(f'<a class="btn btn--primary" href="{html_escape(route)}">Continue</a>')

    if extra_panel:
        content.append(f'<div class="mcip-extra">{extra_panel}</div>')

    if content:
        return '<section class="hub-guide hub-guide--order">' + "\n".join(content) + "</section>"

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


__all__ = [
    "compute_hub_guide",
    "_is_compact_by_progress",
    "COMPACT_THRESH",
    "partners_intel_from_state",
]
