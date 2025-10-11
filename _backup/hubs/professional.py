from __future__ import annotations

from typing import Dict

import streamlit as st

from core.base_hub import BaseHub, status_label


class ProfessionalHub(BaseHub):
    def __init__(self) -> None:
        super().__init__(
            title="Professional Hub",
            icon="💼",
            description="Coordinate discharge planning, track cases, and share updates with families.",
        )

    def build_dashboard(self) -> Dict:
        professional_role = st.session_state.get("professional_role", "Care Coordinator")
        active_cases = st.session_state.get("active_cases", 3)
        legal_requests = st.session_state.get("legal_requests", 0)
        analytics_ready = st.session_state.get("analytics_ready", False)

        cards = [
            {
                "title": "Care coordination",
                "subtitle": f"Toolkit for {professional_role}",
                "status": "in_progress",
                "status_label": status_label("in_progress"),
                "badges": [{"label": "Team workspace", "variant": "brand"}],
                "description": "Centralize updates, request records, and share notes with families.",
                "meta": [f"{active_cases} active cases", "Secure messaging & templates included"],
                "actions": [
                    {"label": "View cases", "route": "hub_professional", "variant": "primary"},
                    {"label": "Schedule consult", "route": "pfma_stub", "variant": "ghost"},
                ],
                "footnote": "Collaborate with Concierge advisors in real time.",
            },
            {
                "title": "Legal services",
                "subtitle": "Power of attorney, guardianship, more",
                "status": "new" if legal_requests == 0 else "in_progress",
                "status_label": status_label("new" if legal_requests == 0 else "in_progress"),
                "badges": [{"label": "Partner network", "variant": "neutral"}],
                "description": "Connect families with vetted elder law attorneys and document prep specialists.",
                "meta": [f"{legal_requests} pending requests"],
                "actions": [
                    {"label": "Find attorney", "route": "hub_trusted", "variant": "primary"},
                    {"label": "Document prep", "route": "hub_trusted", "variant": "ghost"},
                ],
                "footnote": "Set reminders for key filing deadlines.",
            },
            {
                "title": "Financial planning",
                "subtitle": "Funding paths and benefit reviews",
                "status": "in_progress",
                "status_label": status_label("in_progress"),
                "badges": [{"label": "Advisor", "variant": "brand"}],
                "description": "Coordinate with financial professionals to align budgets with care decisions.",
                "meta": ["Integrates with Cost Planner", "Share secure summaries with families"],
                "actions": [
                    {"label": "Book appointment", "route": "cost_planner_stub", "variant": "primary"},
                    {"label": "Resource center", "route": "hub_learning", "variant": "ghost"},
                ],
                "footnote": "Invite families to review projections together.",
            },
            {
                "title": "Analytics dashboard",
                "subtitle": "Outcomes & performance",
                "status": "complete" if analytics_ready else "new",
                "status_label": status_label("complete" if analytics_ready else "new"),
                "badges": [{"label": "Beta", "variant": "ai"}],
                "description": "Monitor case velocity, satisfaction scores, and referral sources.",
                "meta": ["Export to CSV or share interactive reports."],
                "actions": [
                    {"label": "View analytics", "route": "hub_professional", "variant": "primary"},
                    {"label": "Download latest", "route": "hub_professional", "variant": "ghost"},
                ],
                "footnote": "Data refreshes every morning at 6 AM.",
            },
        ]

        callout = {
            "eyebrow": "For professionals",
            "title": "Bring families and partners into one shared workspace.",
            "body": "Use Concierge advisors as an extension of your team—sync notes, upload documents, and track handoffs effortlessly.",
            "actions": [
                {"label": "Invite a family", "route": "hub_concierge", "variant": "primary"},
                {"label": "Meet the advisor team", "route": "pfma_stub", "variant": "ghost"},
            ],
        }

        chips = [
            {"label": "Care delivery"},
            {"label": "Partner tools", "variant": "muted"},
            {"label": "Secure collaboration"},
        ]

        additional = {
            "title": "Partner resources",
            "description": "Extend your toolkit with vetted solutions.",
            "items": [
                {
                    "title": "Training center",
                    "body": "Micro-learning modules for frontline teams.",
                    "action": {"label": "Access courses", "route": "hub_learning"},
                },
                {
                    "title": "Network directory",
                    "body": "Find vetted providers by specialty and location.",
                    "action": {"label": "Browse network", "route": "hub_trusted"},
                },
                {
                    "title": "Marketing kit",
                    "body": "Ready-to-use templates to introduce families to Concierge.",
                    "action": {"label": "Download kit", "route": "hub_professional"},
                },
            ],
        }

        return {
            "chips": chips,
            "callout": callout,
            "cards": cards,
            "additional_services": additional,
        }


def render() -> None:
    hub = ProfessionalHub()
    hub.render()
