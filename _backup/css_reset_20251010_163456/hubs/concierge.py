# hubs/concierge.py
import streamlit as st
from core.base_hub import render_dashboard, _inject_hub_css_once
from core.hub_guide import compute_hub_guide
from core.additional_services import get_additional_services
from core.product_tile import ProductTileHub


__all__ = ["render"]

_inject_hub_css_once()


def render(ctx=None) -> None:
    person = st.session_state.get("person_name", "John")
    gcp_prog = float(st.session_state.get("gcp", {}).get("progress", 0))
    cost_prog = float(st.session_state.get("cost", {}).get("progress", 0))

    cards = [
        ProductTileHub(
            key="gcp",
            title="Guided Care Plan",
            desc="Understand the situation",
            blurb="Personalized assessment across daily life, health, and cognition.",
            meta_lines=["≈12 minutes • Auto-saves"],
            primary_label="Start",
            primary_go="gcp_start",
            secondary_label="See responses",
            secondary_go="gcp_view",
            progress=gcp_prog,
            variant="brand",
            order=10,
            visible=True,
            locked=False,
        ),
        ProductTileHub(
            key="cost",
            title="Cost Planner",
            desc="Estimate monthly costs and runway",
            blurb="Project expenses, compare living options, and see how long current funds will last.",
            meta_lines=["Syncs with Guided Care Plan", "Progress saved automatically"],
            primary_label="Start",
            primary_go="cost_open",
            secondary_label="See responses",
            secondary_go="cost_view",
            progress=cost_prog,
            variant="brand",
            order=20,
            visible=True,
            locked=False,
        ),
        ProductTileHub(
            key="pfma",
            title="Plan with My Advisor",
            desc="Schedule a 1:1 planning session",
            blurb="Get matched with the right advisor to coordinate care, benefits, and trusted partners.",
            badge_text="CONCIERGE TEAM",
            primary_label="Get connected",
            primary_go="pfma_start",
            secondary_label="Share updates",
            secondary_go="pfma_updates",
            progress=0,
            variant="brand",
            order=30,
        ),
        ProductTileHub(
            key="faqs",
            title="FAQs & Answers",
            desc="Ask the Senior Navigator AI",
            blurb="Instant, tailored assistance.",
            badge_text="AI AGENT",
            primary_label="Open",
            primary_go="faqs_open",
            progress=0,
            variant="teal",
            order=40,
        ),
    ]

    guide = compute_hub_guide("concierge")
    additional = get_additional_services("concierge")

    render_dashboard(
        title="Concierge Care Hub",
        subtitle="Finish the essentials, then unlock curated next steps with your advisor.",
        chips=[
            {"label": "Concierge journey"},
            {"label": f"For {person}", "variant": "muted"},
            {"label": "Advisor & AI blended"},
        ],
        hub_guide_block=guide,
        cards=cards,
        additional_services=additional,
    )
