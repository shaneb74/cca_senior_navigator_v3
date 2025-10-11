from __future__ import annotations

from typing import Dict

import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import BaseHub, status_label


class LearningHub(BaseHub):
    def __init__(self) -> None:
        super().__init__(
            title="Learning & Resources Hub",
            icon="📚",
            description="Stay informed with curated guides, short lessons, and AI-powered answers.",
        )

    def build_dashboard(self) -> Dict:
        person_name = st.session_state.get("person_name", "John")
        learning_progress = st.session_state.get("learning_progress", 0)
        completed_resources = st.session_state.get("completed_resources", [])

        progress_status = (
            "complete"
            if learning_progress >= 100
            else "in_progress" if learning_progress else "new"
        )
        modules_viewed = len(completed_resources)

        cards = [
            {
                "title": "Caregiver guides",
                "subtitle": "Step-by-step playbooks",
                "status": "in_progress" if modules_viewed else "new",
                "status_label": status_label(
                    "in_progress" if modules_viewed else "new"
                ),
                "badges": [{"label": "Concierge", "variant": "brand"}],
                "description": "Understand levels of care, funding paths, and decision checklists.",
                "meta": [
                    f"{modules_viewed} guide(s) completed",
                    "Save favourites to share with family.",
                ],
                "actions": [
                    {
                        "label": "Browse guides",
                        "route": "hub_learning",
                        "variant": "primary",
                    },
                    {
                        "label": "Most popular",
                        "route": "hub_learning",
                        "variant": "ghost",
                    },
                ],
                "footnote": "New guides drop every week.",
            },
            {
                "title": "Video library",
                "subtitle": "Sharp insights in under 5 minutes",
                "status": "new",
                "status_label": status_label("new"),
                "badges": [{"label": "On demand", "variant": "neutral"}],
                "description": "Walk through real scenarios, from dementia care to financing assisted living.",
                "meta": [
                    "Captions + downloadable notes",
                    "Created with our advisor network",
                ],
                "actions": [
                    {
                        "label": "Watch now",
                        "route": "hub_learning",
                        "variant": "primary",
                    },
                    {
                        "label": "See categories",
                        "route": "hub_learning",
                        "variant": "ghost",
                    },
                ],
                "footnote": "Add videos to your playlist to revisit later.",
            },
            {
                "title": "FAQ center",
                "subtitle": "Ask and explore",
                "status": "in_progress",
                "status_label": status_label("in_progress"),
                "badges": [{"label": "AI agent", "variant": "ai"}],
                "description": "Tap into our knowledge base or ask the Senior Navigator AI anything.",
                "meta": ["42 topics ready today", "Tailored answers for your journey"],
                "actions": [
                    {"label": "Search FAQs", "route": "faqs", "variant": "primary"},
                    {
                        "label": "Contact support",
                        "route": "pfma_stub",
                        "variant": "ghost",
                    },
                ],
                "footnote": "AI summaries sync with your dashboard history.",
            },
            {
                "title": "Learning progress",
                "subtitle": f"{learning_progress}% complete",
                "status": progress_status,
                "status_label": status_label(progress_status),
                "badges": [{"label": "Personalized", "variant": "brand"}],
                "description": "Stay on track with recommended lessons and follow-up actions.",
                "meta": [f"Goal: {min(learning_progress + 20, 100)}% by next week"],
                "actions": [
                    {
                        "label": "Continue path",
                        "route": "hub_learning",
                        "variant": "primary",
                    },
                    {
                        "label": "Reset topics",
                        "route": "hub_learning",
                        "variant": "ghost",
                    },
                ],
                "footnote": "We’ll nudge you when new lessons match your plan.",
            },
        ]

        callout = {
            "eyebrow": "Recommended for you",
            "title": f"Keep {person_name}'s circle aligned with quick, shareable lessons.",
            "body": "Save favourites to create a family digest, or invite your advisor to drop in notes.",
            "actions": [
                {
                    "label": "Share with family",
                    "route": "hub_concierge",
                    "variant": "primary",
                },
                {
                    "label": "See saved lessons",
                    "route": "hub_learning",
                    "variant": "ghost",
                },
            ],
        }

        chips = [
            {"label": "Learning journey"},
            {"label": "Self-paced resources", "variant": "muted"},
            {"label": "Advisor curated"},
        ]

        additional_services = get_additional_services("learning")

        return {
            "chips": chips,
            "callout": callout,
            "cards": cards,
            "additional_services": additional_services,
        }


def render() -> None:
    hub = LearningHub()
    hub.render()
