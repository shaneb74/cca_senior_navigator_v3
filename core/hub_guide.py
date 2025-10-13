from __future__ import annotations

from html import escape as html_escape
from typing import Any, Dict, Optional

import streamlit as st

def _all_products_done(required: list[str]) -> bool:
    ss = st.session_state
    try:
        for pid in required or []:
            if int(ss.get(pid, {}).get("progress", 0)) < 100:
                return False
        return bool(required)
    except Exception:
        return False


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
    mode: str = "auto",
    extra_panel: Optional[str] = None,
) -> str:
    required_products = list(hub_order.get("ordered_products") or []) if hub_order else []
    if mode == "full":
        compact = False
    else:
        compact = (mode == "compact") or (
            mode == "auto" and required_products and _all_products_done(required_products)
        )

    if compact and (hub_order or extra_panel):
        content: list[str] = []
        if hub_order:
            next_step = hub_order.get("next_step")
            total = hub_order.get("total")
            reason = hub_order.get("reason")
            next_route = hub_order.get("next_route")

            if reason:
                content.append(f'<div class="mcip-msg">{html_escape(str(reason))}</div>')

            if next_step and next_step in required_products:
                idx = required_products.index(next_step) + 1
                step_txt = f"Next step: {idx}"
                if total:
                    step_txt += f" of {total}"
                content.append(f'<div class="mcip-sub">{html_escape(step_txt)}</div>')
                route = next_route or f"/product/{next_step}"
                content.append(f'<a class="btn btn--primary" href="{html_escape(route)}">Continue</a>')

        if extra_panel:
            content.append(f'<div class="mcip-extra">{extra_panel}</div>')

        css_class = "hub-guide hub-guide--order"
        css_class += " hub-guide--compact is-compact"

        if content:
            return f'<section class="{css_class}">' + "\n".join(content) + "</section>"

    content: list[str] = []
    person_name = st.session_state.get("person_name", "").strip()
    
    # Use person's name if available, otherwise use neutral "your"
    person_possessive = html_escape(f"{person_name}'s") if person_name else "your"

    if compact:
        classes = "hub-guide hub-guide--compact is-compact"
    else:
        classes = "hub-guide hub-guide--full"

    if compact:
        title = f"{person_possessive} plan is underway"
        text = "Keep sharing updates and reviewing your plan. You can reopen the tools anytime."
        ctas = """
          <a href="?go=pfma_updates" class="btn btn--secondary">Share updates</a>
          <a href="?page=gcp" class="btn btn--secondary">Review plan</a>
        """
    else:
        if hub_order:
            next_step = hub_order.get("next_step")
            total = hub_order.get("total")
            ordered = list(hub_order.get("ordered_products") or [])
            if next_step and next_step in ordered:
                idx = ordered.index(next_step) + 1
                step_txt = f"You're on step {idx}"
                if total:
                    step_txt += f" of {total}"
                
                # Only show Continue button if there's actual progress to resume
                # (GCP has started - progress > 0)
                gcp_prog = float(st.session_state.get("tiles", {}).get("gcp", {}).get("progress", 0))
                if gcp_prog > 0 and gcp_prog < 100:
                    # In progress - show Continue
                    text = step_txt + ". Continue below to keep momentum."
                    primary_route = hub_order.get("next_route") or f"/product/{next_step}"
                    ctas = f"""
                      <a href="{html_escape(primary_route)}" class="btn btn--primary">Continue</a>
                    """
                elif gcp_prog >= 100:
                    # GCP complete - show Continue to next step (Cost Planner)
                    text = "Great progress! Continue to the Cost Planner to estimate expenses."
                    primary_route = hub_order.get("next_route") or f"/product/{next_step}"
                    ctas = f"""
                      <a href="{html_escape(primary_route)}" class="btn btn--primary">Continue</a>
                      <a href="?go=cost_open" class="btn btn--secondary">Open Cost Planner</a>
                    """
                else:
                    # First visit - no progress yet
                    text = "Start the Guided Care Plan to get a recommendation, then estimate costs with the Cost Planner."
                    ctas = """
                      <a href="?page=gcp" class="btn btn--primary">Start Guided Care Plan</a>
                    """
            else:
                text = "Start the Guided Care Plan to get a recommendation, then estimate costs with the Cost Planner."
                ctas = """
                  <a href="?page=gcp" class="btn btn--primary">Start Guided Care Plan</a>
                """
            title = f"Let's kick off {person_possessive} plan."
        else:
            title = f"Let's kick off {person_possessive} plan."
            text = "Start the Guided Care Plan to get a recommendation, then estimate costs with the Cost Planner."
            ctas = """
              <a href="?page=gcp" class="btn btn--primary">Start Guided Care Plan</a>
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
    "_all_products_done",
    "partners_intel_from_state",
]
