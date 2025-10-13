# hubs/concierge.py
import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.hub_guide import compute_hub_guide
from core.product_tile import ProductTileHub, html_escape
from layout import render_page

__all__ = ["render"]


def render(ctx=None) -> None:
    person_name = st.session_state.get("person_name", "").strip()
    # Use person's name if available, otherwise use neutral "you"
    person = person_name if person_name else "you"
    
    # Check for save message from module
    save_msg = st.session_state.pop("_show_save_message", None)
    if save_msg:
        product_name = {
            "gcp": "Guided Care Plan",
            "cost": "Cost Planner",
            "pfma": "Plan with My Advisor"
        }.get(save_msg.get("product", ""), "questionnaire")
        
        progress = save_msg.get("progress", 0)
        step = save_msg.get("step", 0)
        total = save_msg.get("total", 0)
        
        if progress >= 100:
            st.success(f"✅ {product_name} complete! You can review your results anytime.")
        else:
            st.info(f"💾 Progress saved! You're {progress:.0f}% through the {product_name} (step {step} of {total}). Click Continue below to pick up where you left off.")
    
    gcp_prog = float(st.session_state.get("gcp", {}).get("progress", 0))
    cost_prog = float(st.session_state.get("cost", {}).get("progress", 0))
    pfma_prog = float(st.session_state.get("pfma", {}).get("progress", 0))

    next_step = "gcp"
    if gcp_prog >= 100 and cost_prog < 100:
        next_step = "cost"
    elif cost_prog >= 100 and pfma_prog < 100:
        next_step = "pfma"

    # Read recommendation from handoff (written by module engine)
    handoff = st.session_state.get("handoff", {}).get("gcp", {})
    recommendation = handoff.get("recommendation")
    recommendation_display = str(recommendation).replace('_', ' ').title() if recommendation else None
    
    # Build reason for MCIP
    reason = (
        f"Based on your {recommendation_display} recommendation"
        if recommendation
        else None
    )
    
    # Build GCP status text with recommendation
    gcp_status_text = None
    if gcp_prog >= 100 and recommendation_display:
        gcp_status_text = f"✓ {recommendation_display}"
    
    # Build GCP tile description based on completion
    gcp_desc = "Discover the type of care that's right for you."
    gcp_desc_html = None  # For raw HTML when showing prominent recommendation
    gcp_recommended_reason = "Start here to personalize everything."
    
    if gcp_prog >= 100 and recommendation_display:
        # Display recommendation prominently with custom CSS class
        gcp_desc = None  # Clear standard desc
        gcp_desc_html = f'<span class="tile-recommendation">Recommendation: {html_escape(recommendation_display)}</span>'
    elif gcp_prog > 0:
        # In progress - show resume prompt
        gcp_desc = f"Resume questionnaire ({gcp_prog:.0f}% complete)"
        gcp_recommended_reason = "Pick up where you left off"

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
            desc=gcp_desc,
            desc_html=gcp_desc_html,  # For prominent recommendation display
            blurb="Answer a few short questions about your daily needs, health, and safety. We'll create a personal care plan to help you take the next step with confidence. Everything saves automatically, and it only takes about 2 minutes.",
            image_square="gcp.png",
            meta_lines=["≈2 min • Auto-saves"],
            primary_route="?page=gcp",
            progress=gcp_prog,
            status_text=gcp_status_text,
            variant="brand",
            order=10,
            visible=True,
            locked=False,
            recommended_in_hub="concierge",
            recommended_total=hub_order["total"],
            recommended_order=ordered_index["gcp"],
            recommended_reason=gcp_recommended_reason,
            is_next_step=(next_step == "gcp"),  # MCIP gradient control
        ),
        ProductTileHub(
            key="cost",
            title="Cost Planner",
            desc="Estimate monthly costs and runway",
            blurb="Project expenses, compare living options, and see how long current funds will last.",
            image_square="cp.png",
            meta_lines=["≈10–15 min • Save anytime"],
            primary_route="?page=cost",
            primary_go="cost",
            secondary_label="See responses" if cost_prog > 0 else None,  # Only show after started
            secondary_go="cost_view" if cost_prog > 0 else None,
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
            is_next_step=(next_step == "cost"),  # MCIP gradient control
        ),
        ProductTileHub(
            key="pfma",
            title="Plan with My Advisor",
            desc="Schedule a 1:1 planning session",
            blurb="Get matched with the right advisor to coordinate care, benefits, and trusted partners.",
            badge_text="CONCIERGE TEAM",
            image_square="pfma.png",
            meta_lines=(
                ["✅ 🦆🦆🦆🦆 All Ducks in a Row!"] if pfma_prog >= 100
                else ["≈5–8 min • Ducks in a Row"]
            ),
            badges=(
                [{"label": "🦆🦆🦆🦆 Earned", "tone": "success"}] if pfma_prog >= 100
                else []
            ),
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
            is_next_step=(next_step == "pfma"),  # MCIP gradient control
        ),
        ProductTileHub(
            key="faqs",
            title="FAQs & Answers",
            desc="Ask the Senior Navigator AI",
            blurb="Instant, tailored assistance.",
            badge_text="AI AGENT",
            image_square="faq.png",
            primary_label="Open",
            primary_route="?page=faqs",
            progress=0,
            variant="teal",
            order=40,
            is_next_step=False,  # FAQ never gets MCIP gradient
        ),
    ]

    guide = compute_hub_guide("concierge", hub_order=hub_order, mode="auto")
    additional = get_additional_services("concierge")
    
    # Build chips - only include "For {person}" chip if name exists
    chips = [{"label": "Concierge journey"}]
    if person_name:  # Only show "For X" if name is set
        chips.append({"label": f"For {person}", "variant": "muted"})
    chips.append({"label": "Advisor & AI blended"})

    body_html = render_dashboard_body(
        title="Concierge Care Hub",
        subtitle="Finish the essentials, then unlock curated next steps with your advisor.",
        chips=chips,
        hub_guide_block=guide,
        hub_order=hub_order,
        cards=cards,
        additional_services=additional,
    )

    render_page(body_html=body_html, active_route="hub_concierge")
