from __future__ import annotations

from typing import Dict

import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import BaseHub
from core.hub_guide import compute_hub_guide
from core.product_tile import ProductTileHub


class ConciergeHub(BaseHub):
    def __init__(self) -> None:
        super().__init__(
            title="Concierge Care Hub",
            icon="🏠",
            description="Finish the essentials, then unlock curated next steps with your advisor.",
        )

    def build_dashboard(self) -> Dict:
        person_name = st.session_state.get("person_name", "John")
        appointment_time = st.session_state.get("appointment_time") or "No appointment scheduled yet"
        appointment_status = st.session_state.get("appointment_status", "Scheduled")

        gcp_state = st.session_state.get("gcp", {})
        gcp_progress = float(gcp_state.get("progress", 0) or 0)
        cost_state = st.session_state.get("cost", {})
        cost_progress = float(cost_state.get("progress", st.session_state.get("cost_planner_progress", 0)) or 0)

        def gcp_meta() -> list[str]:
            lines = ["≈12 minutes • Auto-saves"]
            if gcp_progress >= 100:
                lines.append("Recommendation ready to review")
            elif gcp_progress > 0:
                lines.append("Resume to finish your plan")
            else:
                lines.append("Not started yet")
            return lines

        def cost_meta() -> list[str]:
            lines = ["Syncs with Guided Care Plan", "Progress saved automatically"]
            if cost_progress >= 100:
                lines.append("Completed projection ready to review")
            elif cost_progress > 0:
                lines.append("Keep going to finish the projection")
            else:
                lines.append("Not started yet")
            return lines

        if gcp_progress >= 100:
            gcp_primary_label, gcp_primary_go = "See responses", "gcp_view"
            gcp_secondary_label, gcp_secondary_go = "Start over", "gcp_reset"
        elif gcp_progress > 0:
            gcp_primary_label, gcp_primary_go = "Resume", "gcp_resume"
            gcp_secondary_label, gcp_secondary_go = "See responses", "gcp_view"
        else:
            gcp_primary_label, gcp_primary_go = "Start", "gcp_start"
            gcp_secondary_label = gcp_secondary_go = None

        if cost_progress >= 100:
            cost_primary_label, cost_primary_go = "See responses", "cost_view"
            cost_secondary_label, cost_secondary_go = "Start over", "cost_open"
        elif cost_progress > 0:
            cost_primary_label, cost_primary_go = "Continue", "cost_continue"
            cost_secondary_label, cost_secondary_go = "See responses", "cost_view"
        else:
            cost_primary_label, cost_primary_go = "Start", "cost_open"
            cost_secondary_label = cost_secondary_go = None

        pfma_progress = 100 if appointment_status.lower() == "completed" else (40 if appointment_time != "No appointment scheduled yet" else 0)

        cards = [
            ProductTileHub(
                key="gcp",
                title="Guided Care Plan",
                desc="Understand the situation",
                blurb="Personalized assessment across daily life, health, and cognition.",
                badge_text="GUIDED PLAN",
                meta_lines=gcp_meta(),
                primary_label=gcp_primary_label,
                primary_go=gcp_primary_go,
                secondary_label=gcp_secondary_label,
                secondary_go=gcp_secondary_go,
                progress=gcp_progress,
                variant="brand",
                order=10,
            ),
            ProductTileHub(
                key="cost",
                title="Cost Planner",
                desc="Estimate monthly costs and runway",
                blurb="Project expenses, compare living options, and see how long current funds will last.",
                badge_text="FINANCIAL",
                meta_lines=cost_meta(),
                primary_label=cost_primary_label,
                primary_go=cost_primary_go,
                secondary_label=cost_secondary_label,
                secondary_go=cost_secondary_go,
                progress=cost_progress,
                variant="brand",
                order=20,
            ),
            ProductTileHub(
                key="pfma",
                title="Plan with My Advisor",
                desc="Schedule a 1:1 planning session",
                blurb="Get matched with the right advisor to coordinate care, benefits, and trusted partners.",
                badge_text="CONCIERGE TEAM",
                meta_lines=[f"Status: {appointment_status}", appointment_time],
                primary_label="Get connected",
                primary_go="pfma_start",
                secondary_label="Share updates",
                secondary_go="pfma_updates",
                progress=pfma_progress,
                variant="brand",
                order=30,
            ),
            ProductTileHub(
                key="faqs",
                title="FAQs & Answers",
                desc="Ask the Senior Navigator AI",
                blurb="Instant, tailored assistance whenever you need it.",
                badge_text="AI AGENT",
                meta_lines=["Available 24/7", "Summaries saved to your timeline"],
                primary_label="Open",
                primary_go="faqs_open",
                secondary_label="Recent topics",
                secondary_go="faqs_recent",
                progress=0,
                variant="teal",
                order=40,
            ),
        ]

        chips = [
            {"label": "Concierge journey"},
            {"label": f"For {person_name}", "variant": "muted"},
            {"label": "Advisor & AI blended"},
        ]

        return {
            "title": self.title,
            "subtitle": self.description,
            "chips": chips,
            "cards": cards,
            "additional_services": get_additional_services("concierge"),
            "hub_guide_block": compute_hub_guide("concierge"),
        }


def render() -> None:
    hub = ConciergeHub()
    hub.render()
