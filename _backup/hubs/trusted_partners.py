from __future__ import annotations

from typing import Dict

import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import BaseHub, status_label


class TrustedPartnersHub(BaseHub):
    def __init__(self) -> None:
        super().__init__(
            title="Trusted Partners Hub",
            icon="🤝",
            description="Verified care providers, senior living communities, and specialty services curated for your family.",
        )

    def build_dashboard(self) -> Dict:
        person_name = st.session_state.get("person_name", "John")
        location = st.session_state.get("location", "your area")
        verified_partners = st.session_state.get("verified_partners", 23)
        tours_booked = st.session_state.get("tours_booked", 0)

        cards = [
            {
                "title": "Home care agencies",
                "subtitle": f"Trusted professionals near {location}",
                "status": "in_progress",
                "status_label": status_label("in_progress"),
                "badges": [{"label": "Concierge curated", "variant": "brand"}],
                "description": "Compare hourly support, live-in aides, and respite options with transparent pricing.",
                "meta": [
                    f"{verified_partners} verified partners",
                    "Background checked & insured",
                ],
                "actions": [
                    {
                        "label": "View agencies",
                        "route": "hub_trusted",
                        "variant": "primary",
                    },
                    {
                        "label": "Compare services",
                        "route": "hub_trusted",
                        "variant": "ghost",
                    },
                ],
                "footnote": "Save favourites to share with your advisor.",
            },
            {
                "title": "Senior communities",
                "subtitle": "Independent, assisted, memory care",
                "status": "in_progress" if tours_booked else "new",
                "status_label": status_label("in_progress" if tours_booked else "new"),
                "badges": [{"label": "Onsite & virtual", "variant": "neutral"}],
                "description": "See availability, starting rates, and upcoming events at recommended communities.",
                "meta": [
                    f"{tours_booked} tour(s) booked",
                    "Personalized shortlist based on your plan",
                ],
                "actions": [
                    {
                        "label": "Explore options",
                        "route": "hub_trusted",
                        "variant": "primary",
                    },
                    {
                        "label": "Schedule tour",
                        "route": "pfma_stub",
                        "variant": "ghost",
                    },
                ],
                "footnote": "Advisors confirm with communities within 24 hours.",
            },
            {
                "title": "Financial advisors",
                "subtitle": "Specialists in senior finance",
                "status": "new",
                "status_label": status_label("new"),
                "badges": [{"label": "Partners", "variant": "brand"}],
                "description": "Collaborate with vetted professionals on pensions, VA benefits, and long-term care insurance.",
                "meta": ["Coordinate with your Cost Planner outputs."],
                "actions": [
                    {
                        "label": "Find advisor",
                        "route": "pfma_stub",
                        "variant": "primary",
                    },
                    {
                        "label": "Resource center",
                        "route": "hub_learning",
                        "variant": "ghost",
                    },
                ],
                "footnote": "We pre-screen for licensure and experience.",
            },
            {
                "title": "Partner network",
                "subtitle": "Trusted services for daily living",
                "status": "complete" if verified_partners > 0 else "new",
                "status_label": status_label(
                    "complete" if verified_partners > 0 else "new"
                ),
                "badges": [{"label": "Growing library", "variant": "ai"}],
                "description": "Coordinate transportation, meal delivery, home safety upgrades, and more.",
                "meta": ["Tap to filter by category or urgency."],
                "actions": [
                    {
                        "label": "Browse network",
                        "route": "hub_trusted",
                        "variant": "primary",
                    },
                    {
                        "label": "Share with family",
                        "route": "hub_concierge",
                        "variant": "ghost",
                    },
                ],
                "footnote": "Partners sign the Concierge Care standards pledge.",
            },
        ]

        callout = {
            "eyebrow": "Handpicked for you",
            "title": f"Discover vetted partners ready to support {person_name}.",
            "body": "Your advisor works alongside this network—tell us what you need and we'll coordinate the intros.",
            "actions": [
                {
                    "label": "Request recommendations",
                    "route": "pfma_stub",
                    "variant": "primary",
                },
                {
                    "label": "See saved partners",
                    "route": "hub_trusted",
                    "variant": "ghost",
                },
            ],
        }

        chips = [
            {"label": "Partner marketplace"},
            {"label": "Verified & transparent", "variant": "muted"},
            {"label": "Advisor supported"},
        ]

        additional_services = get_additional_services("trusted_partners")

        return {
            "chips": chips,
            "callout": callout,
            "cards": cards,
            "additional_services": additional_services,
        }


def render() -> None:
    hub = TrustedPartnersHub()
    hub.render()
