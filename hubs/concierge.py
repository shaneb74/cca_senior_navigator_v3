# hubs/concierge.py
import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.hub_guide import compute_hub_guide
from core.product_tile import ProductTileHub
from layout import render_page

__all__ = ["render"]


def render(ctx=None) -> None:
    person = st.session_state.get("person_name", "John")
    gcp_prog = float(st.session_state.get("gcp", {}).get("progress", 0))
    cost_prog = float(st.session_state.get("cost", {}).get("progress", 0))
    pfma_prog = float(st.session_state.get("pfma", {}).get("progress", 0))

    next_step = "gcp"
    if gcp_prog >= 100 and cost_prog < 100:
        next_step = "cost"
    elif cost_prog >= 100 and pfma_prog < 100:
        next_step = "pfma"

    care_tier = st.session_state.get("gcp", {}).get("care_tier")
    reason = (
        f"Based on your {str(care_tier).replace('_', ' ').title()} recommendation"
        if care_tier
        else None
    )

    hub_order = {
        "hub_id": "concierge",
        "ordered_products": ["gcp", "cost", "pfma"],
        "reason": reason,
        "total": 3,
        "next_step": next_step,
    }
    hub_order["next_route"] = f"/product/{next_step}"
    ordered_index = {pid: idx + 1 for idx, pid in enumerate(hub_order["ordered_products"])}

    cards = [
        ProductTileHub(
            key="gcp",
            title="Guided Care Plan",
            desc="Answer a few questions to get a care recommendation.",
            blurb="Personalized assessment across daily life, health, and cognition.",
            image_square="gcp.png",
            meta_lines=["≈12 min • Auto-saves"],
            primary_route="?page=gcp",
            primary_go="gcp_start",
            secondary_label="See responses",
            secondary_go="gcp_view",
            progress=gcp_prog,
            variant="brand",
            order=10,
            visible=True,
            locked=False,
            recommended_in_hub="concierge",
            recommended_total=hub_order["total"],
            recommended_order=ordered_index["gcp"],
            recommended_reason="Start here to personalize everything.",
        ),
        ProductTileHub(
            key="cost",
            title="Cost Planner",
            desc="Estimate monthly costs and runway",
            blurb="Project expenses, compare living options, and see how long current funds will last.",
            image_square="cp.png",
            meta_lines=["≈10–15 min • Save anytime"],
            primary_route="/product/cost",
            primary_go="cost_open",
            secondary_label="See responses",
            secondary_go="cost_view",
            progress=cost_prog,
            variant="brand",
            order=20,
            visible=True,
            locked=not (gcp_prog >= 100),
            unlock_requires=["gcp:complete"],
            lock_msg="Finish your Guided Care Plan to continue.",
            recommended_in_hub="concierge",
            recommended_total=hub_order["total"],
            recommended_order=ordered_index["cost"],
            recommended_reason=reason,
        ),
        ProductTileHub(
            key="pfma",
            title="Plan with My Advisor",
            desc="Schedule a 1:1 planning session",
            blurb="Get matched with the right advisor to coordinate care, benefits, and trusted partners.",
            badge_text="CONCIERGE TEAM",
            image_square="pfma.png",
            meta_lines=["≈5–8 min • Ducks in a Row"],
            primary_route="/product/pfma",
            primary_go="pfma_start",
            secondary_label="Share updates",
            secondary_go="pfma_updates",
            progress=pfma_prog,
            variant="brand",
            order=30,
            locked=not (cost_prog >= 50),
            unlock_requires=["cost:>=50"],
            lock_msg="Estimate at least half your costs, then book.",
            recommended_in_hub="concierge",
            recommended_total=hub_order["total"],
            recommended_order=ordered_index["pfma"],
            recommended_reason=reason,
        ),
        ProductTileHub(
            key="faqs",
            title="FAQs & Answers",
            desc="Ask the Senior Navigator AI",
            blurb="Instant, tailored assistance.",
            badge_text="AI AGENT",
            image_square="faq.png",
            primary_label="Open",
            primary_go="faqs_open",
            progress=0,
            variant="teal",
            order=40,
        ),
    ]

    guide = compute_hub_guide("concierge", hub_order=hub_order)
    additional = get_additional_services("concierge")

    body_html = render_dashboard_body(
        title="Concierge Care Hub",
        subtitle="Finish the essentials, then unlock curated next steps with your advisor.",
        chips=[
            {"label": "Concierge journey"},
            {"label": f"For {person}", "variant": "muted"},
            {"label": "Advisor & AI blended"},
        ],
        hub_guide_block=guide,
        hub_order=hub_order,
        cards=cards,
        additional_services=additional,
    )

    render_page(body_html=body_html, active_route="hub_concierge")
