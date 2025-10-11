# core/hub_guide.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import streamlit as st

GuideAction = Dict[str, str]
GuideBlock = Dict[str, Any]


def _ctx() -> Dict[str, Any]:
    ss = st.session_state
    return {
        "role": ss.get("role", "consumer"),
        "person_name": ss.get("person_name", "John"),
        "gcp": ss.get("gcp", {}),
        "cost": ss.get("cost", {}),
        "flags": ss.get("flags", {}),
        "first_visit": bool(ss.get("first_visit", True)),
    }


def _progress(bucket: Dict[str, Any]) -> float:
    try:
        return float(bucket.get("progress", 0))
    except Exception:
        return 0.0


def compute_hub_guide(hub: str = "concierge") -> Optional[GuideBlock]:
    """
    Returns a dict with eyebrow/title/body/actions or None.
    Actions = [{label, route, variant}] where variant = primary|ghost|neutral
    """
    c = _ctx()
    name = c["person_name"]
    gcp_p = _progress(c["gcp"])
    cost_p = _progress(c["cost"])

    # Concierge examples; extend per hub if needed
    if hub == "concierge":
        # First visit: push to start plan
        if c["first_visit"] and gcp_p == 0 and cost_p == 0:
            return {
                "eyebrow": "Advisor insight",
                "title": f"Let’s kick off {name}’s plan.",
                "body": "Start the Guided Care Plan to get a recommendation, then estimate costs with the Cost Planner.",
                "actions": [
                    {
                        "label": "Start Guided Care Plan",
                        "route": "gcp_start",
                        "variant": "primary",
                    },
                    {
                        "label": "Open Cost Planner",
                        "route": "cost_open",
                        "variant": "ghost",
                    },
                ],
                "variant": "brand",
            }

        # GCP in progress, cost not started
        if 0 < gcp_p < 100 and cost_p == 0:
            return {
                "eyebrow": "Keep going",
                "title": "Finish your assessment, then estimate budget.",
                "body": "Complete the remaining questions to unlock accurate cost scenarios.",
                "actions": [
                    {
                        "label": "Resume Guided Care Plan",
                        "route": "gcp_resume",
                        "variant": "primary",
                    },
                    {"label": "See responses", "route": "gcp_view", "variant": "ghost"},
                ],
                "variant": "brand",
            }

        # GCP done, cost not started
        if gcp_p >= 100 and cost_p == 0:
            return {
                "eyebrow": "Nice work",
                "title": f"Recommendation ready. Next: costs for {name}.",
                "body": "Use the Cost Planner to project expenses and runway based on your choices.",
                "actions": [
                    {
                        "label": "Start Cost Planner",
                        "route": "cost_open",
                        "variant": "primary",
                    },
                    {
                        "label": "Review recommendation",
                        "route": "gcp_view",
                        "variant": "ghost",
                    },
                ],
                "variant": "success",
            }

        # Cost in progress
        if cost_p > 0 and cost_p < 100:
            return {
                "eyebrow": "Almost there",
                "title": "Finish your cost inputs to see monthly runway.",
                "body": "Add income, assets, and housing to complete your projection.",
                "actions": [
                    {
                        "label": "Resume Cost Planner",
                        "route": "cost_open",
                        "variant": "primary",
                    },
                    {
                        "label": "See partial results",
                        "route": "cost_view",
                        "variant": "ghost",
                    },
                ],
                "variant": "brand",
            }

        # Everything complete: point to advisor
        if gcp_p >= 100 and cost_p >= 100:
            return {
                "eyebrow": "Next step",
                "title": "Bring advisor-ready numbers to your call.",
                "body": "Share updates and book time with your advisor to finalize the plan.",
                "actions": [
                    {
                        "label": "Get connected",
                        "route": "pfma_start",
                        "variant": "primary",
                    },
                    {
                        "label": "Share updates",
                        "route": "pfma_updates",
                        "variant": "ghost",
                    },
                ],
                "variant": "teal",
            }

    return None


def render_hub_guide(block: GuideBlock) -> None:
    if not block:
        return
    import streamlit as st

    eyebrow = block.get("eyebrow", "")
    title = block.get("title", "")
    body = block.get("body", "")
    actions: List[GuideAction] = block.get("actions") or []

    html_parts = ['<div class="hub-guide">', '<section class="dashboard-callout">']
    if eyebrow:
        html_parts.append(f'<div class="dashboard-callout-eyebrow">{eyebrow}</div>')
    if title:
        html_parts.append(f'<h2 class="dashboard-callout-title">{title}</h2>')
    if body:
        html_parts.append(f'<p class="dashboard-callout-text">{body}</p>')
    if actions:
        html_parts.append('<div class="dashboard-card__actions">')
        for a in actions:
            variant = a.get("variant", "primary")
            cls = (
                "dashboard-cta dashboard-cta--primary"
                if variant == "primary"
                else (
                    "dashboard-cta dashboard-cta--ghost"
                    if variant == "ghost"
                    else "dashboard-cta dashboard-cta--neutral"
                )
            )
            html_parts.append(
                f'<a class="{cls}" href="?go={a.get("route","#")}">{a.get("label","Open")}</a>'
            )
        html_parts.append("</div>")
    html_parts.append("</section>")
    html_parts.append("</div>")

    st.markdown("".join(html_parts), unsafe_allow_html=True)
