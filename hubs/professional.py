from __future__ import annotations

from typing import Dict, List

import streamlit as st

from core.base_hub import render_dashboard_body
from core.product_tile import ProductTileHub
from core.state import is_professional, switch_to_professional
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
    # Ensure professional mode is active (should be set by welcome.py before navigation)
    # If somehow accessed without professional mode, switch to it
    if not is_professional():
        switch_to_professional()
        st.rerun()
        return

    # MCIP panel data
    pending_actions = 7
    new_referrals = 3
    cases_needing_updates = 5
    last_login = "2025-10-12 14:30"

    # 6 Professional product tiles as specified
    raw_cards: List[Dict[str, any]] = [
        {
            "title": "Professional Dashboard",
            "subtitle": "Overview and priorities",
            "badges": [{"label": "7 new", "tone": "brand"}],
            "description": "At-a-glance priorities and recent activity across all your cases.",
            "meta": [
                f"{pending_actions} pending actions",
                f"{new_referrals} new referrals today",
            ],
            "actions": [
                {"label": "Open Dashboard", "route": "hub_professional"},
            ],
        },
        {
            "title": "Client List / Search",
            "subtitle": "Find and access client profiles",
            "badges": [],
            "description": "Find clients and open their profiles with full case history.",
            "meta": [
                "Search by name, ID, or case number",
                "Quick filters for active cases",
            ],
            "actions": [
                {"label": "Find a Client", "route": "hub_professional"},
            ],
        },
        {
            "title": "Case Management & Referrals",
            "subtitle": "Track cases and referrals",
            "badges": [{"label": f"{cases_needing_updates} due", "tone": "neutral"}],
            "description": "Create, track, and update cases or referrals with integrated notes.",
            "meta": [
                f"{cases_needing_updates} cases need updates",
                "Automated status tracking",
            ],
            "actions": [
                {"label": "Manage Cases", "route": "hub_professional"},
            ],
        },
        {
            "title": "Scheduling + Analytics",
            "subtitle": "Appointments and metrics",
            "badges": [{"label": "3 due today", "tone": "ai"}],
            "description": "Manage appointments and view engagement metrics across your caseload.",
            "meta": [
                "Calendar integration available",
                "Weekly performance reports",
            ],
            "actions": [
                {"label": "View Schedule", "route": "hub_professional"},
            ],
        },
        {
            "title": "Health Assessment Access",
            "subtitle": "View assessments and flags",
            "badges": [],
            "description": "Open assessment summaries and recidivism-risk flags for your clients.",
            "meta": [
                "Risk scores and alerts included",
                "Historical comparison views",
            ],
            "actions": [
                {"label": "View Assessments", "route": "hub_professional"},
            ],
        },
        {
            "title": "Advisor Mode Navi (CRM Query Engine)",
            "subtitle": "Professional CRM insights",
            "badges": [{"label": "Beta", "tone": "ai"}],
            "description": "Professional-grade CRM queries and quick insights powered by AI.",
            "meta": [
                "Natural language queries",
                "Export to reports or share links",
            ],
            "actions": [
                {"label": "Open CRM", "route": "hub_professional"},
            ],
        },
    ]

    cards = [_to_tile(card, (idx + 1) * 10) for idx, card in enumerate(raw_cards)]

    body_html = render_dashboard_body(
        title="Professional Hub",
        subtitle="Comprehensive tools for discharge planners, nurses, physicians, social workers, and geriatric care managers.",
        chips=[
            {"label": f"Pending: {pending_actions}"},
            {"label": f"New referrals: {new_referrals}", "variant": "muted"},
            {"label": f"Updates needed: {cases_needing_updates}"},
            {"label": f"Last login: {last_login}", "variant": "muted"},
        ],
        cards=cards,
    )

    render_page(body_html=body_html, active_route="hub_professional")
