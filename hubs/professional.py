from __future__ import annotations

from typing import Dict, List

import streamlit as st

from core.base_hub import render_dashboard_body
from core.product_tile import ProductTileHub
from layout import render_page

__all__ = ["render"]


def _to_tile(card: Dict[str, any], order: int) -> ProductTileHub:
    actions = card.get("actions", [])
    primary = actions[0] if actions else {}
    secondary = actions[1] if len(actions) > 1 else {}

    meta = [str(line) for line in card.get("meta", [])]
    footnote = card.get("footnote")
    if footnote:
        meta.append(str(footnote))

    return ProductTileHub(
        key=card.get("title", f"tile-{order}").lower().replace(" ", "-") + f"-{order}",
        title=card.get("title", ""),
        desc=card.get("subtitle", ""),
        blurb=card.get("description", ""),
        badges=card.get("badges", []),
        meta_lines=meta,
        primary_label=primary.get("label"),
        primary_route=f"?go={primary.get('route')}" if primary.get("route") else "#",
        secondary_label=secondary.get("label") if secondary.get("route") else None,
        secondary_route=f"?go={secondary.get('route')}" if secondary.get("route") else None,
        order=order,
    )


def render(ctx=None) -> None:
    professional_role = st.session_state.get("professional_role", "Care Coordinator")
    active_cases = st.session_state.get("active_cases", 3)
    legal_requests = st.session_state.get("legal_requests", 0)
    analytics_ready = st.session_state.get("analytics_ready", False)

    raw_cards: List[Dict[str, any]] = [
        {
            "title": "Care coordination",
            "subtitle": f"Toolkit for {professional_role}",
            "badges": [{"label": "Team workspace", "tone": "brand"}],
            "description": "Centralize updates, request records, and share notes with families.",
            "meta": [
                f"{active_cases} active cases",
                "Secure messaging & templates included",
            ],
            "actions": [
                {"label": "View cases", "route": "hub_professional"},
                {"label": "Schedule consult", "route": "pfma_stub"},
            ],
            "footnote": "Collaborate with Concierge advisors in real time.",
        },
        {
            "title": "Legal services",
            "subtitle": "Power of attorney, guardianship, more",
            "badges": [{"label": "Partner network", "tone": "neutral"}],
            "description": "Connect families with vetted elder law attorneys and document prep specialists.",
            "meta": [f"{legal_requests} pending requests"],
            "actions": [
                {"label": "Find attorney", "route": "hub_trusted"},
                {"label": "Document prep", "route": "hub_trusted"},
            ],
            "footnote": "Set reminders for key filing deadlines.",
        },
        {
            "title": "Financial planning",
            "subtitle": "Funding paths and benefit reviews",
            "badges": [{"label": "Advisor", "tone": "brand"}],
            "description": "Coordinate with financial professionals to align budgets with care decisions.",
            "meta": [
                "Integrates with Cost Planner",
                "Share secure summaries with families",
            ],
            "actions": [
                {"label": "Book appointment", "route": "cost_planner_stub"},
                {"label": "Resource center", "route": "hub_learning"},
            ],
            "footnote": "Invite families to review projections together.",
        },
        {
            "title": "Analytics dashboard",
            "subtitle": "Outcomes & performance",
            "badges": [{"label": "Beta", "tone": "ai"}],
            "description": "Monitor case velocity, satisfaction scores, and referral sources.",
            "meta": ["Export to CSV or share interactive reports."],
            "actions": [
                {"label": "View analytics", "route": "hub_professional"},
                {"label": "Download latest", "route": "hub_professional"},
            ],
            "footnote": "Data refreshes every morning at 6 AM.",
        },
    ]

    cards = [_to_tile(card, (idx + 1) * 10) for idx, card in enumerate(raw_cards)]

    body_html = render_dashboard_body(
        title="Professional Hub",
        subtitle="Coordinate discharge planning, track cases, and share updates with families.",
        chips=[
            {"label": "Care delivery"},
            {"label": "Partner tools", "variant": "muted"},
            {"label": "Secure collaboration"},
        ],
        cards=cards,
    )

    render_page(body_html=body_html, active_route="hub_professional")
