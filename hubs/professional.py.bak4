from __future__ import annotations

from html import escape as html_escape

import streamlit as st

from core.base_hub import render_dashboard_body
from core.navi import render_navi_panel
from core.product_tile import ProductTileHub
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple

__all__ = ["render"]


def _to_tile(card: dict[str, any], order: int) -> ProductTileHub:
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
        primary_route=f"?page={primary.get('route')}" if primary.get("route") else "#",
        secondary_label=secondary.get("label") if secondary.get("route") else None,
        secondary_route=f"?page={secondary.get('route')}" if secondary.get("route") else None,
        order=order,
    )


def _build_mcip_panel(
    *,
    pending_actions: int,
    new_referrals: int,
    cases_needing_updates: int,
    last_login: str,
) -> str:
    metrics = [
        ("Pending", f"{pending_actions}", False),
        ("New referrals", f"{new_referrals}", True),
        ("Updates needed", f"{cases_needing_updates}", False),
    ]
    chips_html = []
    for label, value, muted in metrics:
        classes = "dashboard-chip"
        if muted:
            classes += " is-muted"
        chips_html.append(
            f'<span class="{classes}">{html_escape(label)}: {html_escape(value)}</span>'
        )

    chips_block = "".join(chips_html)
    last_login_text = html_escape(last_login)

    return (
        '<section class="hub-guide hub-guide--order">'
        '<div class="mcip-msg">Caseload snapshot</div>'
        f'<div class="hub-guide__actions">{chips_block}</div>'
        f'<div class="mcip-sub">Last login: {last_login_text}</div>'
        '<div class="mcip-extra">Metrics refresh as referrals and case notes update. Open the dashboard tile to triage priorities.</div>'
        "</section>"
    )


def render(ctx=None) -> None:
    # ============================================================
    # AUTHENTICATION DISABLED FOR DEVELOPMENT TESTING
    # ============================================================
    # Role-based gating temporarily removed to verify navigation and rendering
    # Professional Hub is now accessible without role checks
    # The following code is intentionally commented out:
    #
    # if not is_professional():
    #     switch_to_professional()
    #     st.rerun()
    #     return
    #
    # Once navigation and rendering are confirmed stable, role-based
    # authentication will be re-enabled.
    # ============================================================

    # MCIP panel data
    pending_actions = 7
    new_referrals = 3
    cases_needing_updates = 5
    last_login = "2025-10-12 14:30"

    # 6 Professional product tiles as specified
    raw_cards: list[dict[str, any]] = [
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
            "title": "Recidivism Assessment / Solutions",
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

    mcip_panel = _build_mcip_panel(
        pending_actions=pending_actions,
        new_referrals=new_referrals,
        cases_needing_updates=cases_needing_updates,
        last_login=last_login,
    )

    # Use callback pattern to render Navi AFTER header
    def render_content():
        # Render Navi panel (after header, before hub content)
        render_navi_panel(location="hub", hub_key="professional")

        # Render hub body HTML WITHOUT title/subtitle (Navi replaces them)
        body_html = render_dashboard_body(
            title=None,
            subtitle=None,
            hub_guide_block=None,  # Navi replaces MCIP panel
            cards=cards,
        )
        st.markdown(body_html, unsafe_allow_html=True)

    # Render with simple header/footer
    render_header_simple(active_route="hub_professional")
    render_content()
    render_footer_simple()
