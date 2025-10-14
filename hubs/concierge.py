# hubs/concierge.py
"""
Concierge Hub - Navi-Powered Polymorphic Display

This hub uses Navi as the single intelligence layer.
Navi orchestrates journey coordination, Additional Services, and Q&A.
"""
import streamlit as st

from core.mcip import MCIP
from core.navi import render_navi_panel, NaviOrchestrator
from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.product_tile import ProductTileHub
from layout import render_page

__all__ = ["render"]


def render(ctx=None) -> None:
    """Render the Concierge Hub with Navi orchestration."""
    
    # Initialize MCIP
    MCIP.initialize()
    
    # Render Navi panel (THE single intelligence layer)
    # Replaces: Hub Guide + MCIP journey status
    navi_ctx = render_navi_panel(location="hub", hub_key="concierge")
    
    # Extract data from Navi context
    next_action = navi_ctx.next_action
    person_name = navi_ctx.user_name or ""
    person = person_name if person_name else "you"
    
    # Show save confirmation if returning
    # Handle save messages from legacy products (backwards compatibility)
    save_msg = st.session_state.pop("_show_save_message", None)
    if save_msg:
        product_name = {
            "gcp": "Guided Care Plan",
            "cost": "Cost Planner",
            "pfma": "Plan with My Advisor"
        }.get(save_msg.get("product", ""), "questionnaire")
        
        prog = save_msg.get("progress", 0)
        step = save_msg.get("step", 0)
        total = save_msg.get("total", 0)
        
        if prog >= 100:
            st.success(f"✅ {product_name} complete! You can review your results anytime.")
        else:
            st.info(f"💾 Progress saved! You're {prog:.0f}% through the {product_name} (step {step} of {total}). Click Continue below to pick up where you left off.")
    
    # Build hub order from MCIP
    hub_order = {
        "hub_id": "concierge",
        "ordered_products": ["gcp_v4", "cost_v2", "pfma_v2"],
        "reason": _get_hub_reason(),
        "total": 3,
        "next_step": next_action.get("route", "gcp_v4").replace("?page=", ""),
    }
    hub_order["next_route"] = f"?page={hub_order['next_step']}"
    ordered_index = {pid: idx + 1 for idx, pid in enumerate(hub_order["ordered_products"])}
    
    # Build product tiles dynamically from MCIP
    cards = [
        _build_gcp_tile(hub_order, ordered_index, next_action),
        _build_cost_planner_tile(hub_order, ordered_index, next_action),
        _build_pfma_tile(hub_order, ordered_index, next_action),
        _build_faq_tile(),
    ]
    
    # Get additional services (filters based on GCP completion)
    additional = get_additional_services("concierge")
    
    # Build chips
    chips = [{"label": "Concierge journey"}]
    if person_name:
        chips.append({"label": f"For {person}", "variant": "muted"})
    chips.append({"label": "Advisor & AI blended"})
    
    # Render dashboard (Navi journey status already shown above)
    body_html = render_dashboard_body(
        title="Concierge Care Hub",
        subtitle="Finish the essentials, then unlock curated next steps with your advisor.",
        chips=chips,
        hub_guide_block=None,  # Deprecated - using render_mcip_journey_status() instead
        hub_order=hub_order,
        cards=cards,
        additional_services=additional,
    )
    
    render_page(body_html=body_html, active_route="hub_concierge")


def _get_hub_reason() -> str:
    """Get contextual reason for hub based on MCIP state."""
    care_rec = MCIP.get_care_recommendation()
    
    if care_rec and care_rec.tier:
        tier_map = {
            "independent": "Independent Living",
            "in_home": "In-Home Care",
            "assisted_living": "Assisted Living",
            "memory_care": "Memory Care"
        }
        tier_label = tier_map.get(care_rec.tier, care_rec.tier.replace("_", " ").title())
        return f"Based on your {tier_label} recommendation"
    
    return "Complete your care plan to personalize your journey"


def _build_gcp_tile(hub_order: dict, ordered_index: dict, next_action: dict) -> ProductTileHub:
    """Build GCP tile dynamically from MCIP."""
    summary = MCIP.get_product_summary("gcp_v4")
    
    if not summary:
        # Fallback if MCIP doesn't have data
        summary = {
            "status": "not_started",
            "summary_line": "Get your personalized care recommendation",
            "route": "gcp_v4"
        }
    
    # Determine states
    is_complete = (summary["status"] == "complete")
    is_in_progress = st.session_state.get("gcp", {}).get("progress", 0) > 0
    is_next = (next_action.get("route") == "gcp_v4")
    
    # Build description
    if is_complete:
        desc = None
        desc_html = f'<span class="tile-recommendation">{summary["summary_line"]}</span>'
        status_text = summary["summary_line"]
        progress = 100
    elif is_in_progress:
        prog = st.session_state.get("gcp", {}).get("progress", 0)
        desc = f"Resume questionnaire ({prog:.0f}% complete)"
        desc_html = None
        status_text = None
        progress = prog
    else:
        desc = "Discover the type of care that's right for you."
        desc_html = None
        status_text = None
        progress = 0
    
    return ProductTileHub(
        key="gcp_v4",
        title="Guided Care Plan",
        desc=desc,
        desc_html=desc_html,
        blurb="Answer a few short questions about your daily needs, health, and safety. We'll create a personal care plan to help you take the next step with confidence. Everything saves automatically, and it only takes about 2 minutes.",
        image_square="gcp.png",
        meta_lines=["≈2 min • Auto-saves"],
        primary_route=f"?page={summary['route']}",
        progress=progress,
        status_text=status_text,
        variant="brand",
        order=10,
        visible=True,
        locked=False,
        recommended_in_hub="concierge",
        recommended_total=hub_order["total"],
        recommended_order=ordered_index.get("gcp_v4", 1),
        recommended_reason="Start here to personalize everything.",
        is_next_step=is_next,
    )


def _build_cost_planner_tile(hub_order: dict, ordered_index: dict, next_action: dict) -> ProductTileHub:
    """Build Cost Planner tile dynamically from MCIP."""
    summary = MCIP.get_product_summary("cost_v2")
    
    if not summary:
        summary = {
            "status": "locked",
            "summary_line": "Complete Guided Care Plan first",
            "route": None
        }
    
    # Determine states
    is_complete = (summary["status"] == "complete")
    is_locked = (summary["status"] == "locked")
    is_in_progress = st.session_state.get("cost", {}).get("progress", 0) > 0
    is_next = (next_action.get("route") == "cost_v2")
    
    # Build description and progress
    if is_complete:
        desc = summary["summary_line"]
        progress = 100
        status_text = "✓ Complete"
    elif is_in_progress:
        prog = st.session_state.get("cost", {}).get("progress", 0)
        desc = f"Resume planner ({prog:.0f}% complete)"
        progress = prog
        status_text = None
    elif is_locked:
        desc = summary["summary_line"]
        progress = 0
        status_text = None
    else:
        desc = summary["summary_line"]
        progress = 0
        status_text = None
    
    return ProductTileHub(
        key="cost_v2",
        title="Cost Planner",
        desc=desc,
        blurb="Project expenses, compare living options, and see how long current funds will last.",
        image_square="cp.png",
        meta_lines=["≈10–15 min • Save anytime"],
        primary_route=f"?page={summary['route']}" if summary['route'] else None,
        primary_go="cost_v2",
        secondary_label="See responses" if is_in_progress else None,
        secondary_go="cost_view" if is_in_progress else None,
        progress=progress,
        status_text=status_text,
        variant="brand",
        order=20,
        visible=True,
        locked=is_locked,
        unlock_requires=["gcp:complete"],
        lock_msg="Finish your Guided Care Plan to continue.",
        recommended_in_hub="concierge",
        recommended_total=hub_order["total"],
        recommended_order=ordered_index.get("cost_v2", 2),
        recommended_reason=_get_hub_reason(),
        is_next_step=is_next,
    )


def _build_pfma_tile(hub_order: dict, ordered_index: dict, next_action: dict) -> ProductTileHub:
    """Build PFMA tile dynamically from MCIP."""
    summary = MCIP.get_product_summary("pfma_v2")
    
    if not summary:
        summary = {
            "status": "locked",
            "summary_line": "Complete Cost Planner first",
            "route": None
        }
    
    # Determine states
    is_complete = (summary["status"] == "complete")
    is_locked = (summary["status"] == "locked")
    is_in_progress = st.session_state.get("pfma", {}).get("progress", 0) > 0
    is_next = (next_action.get("route") == "pfma_v2")
    
    # Build description and progress
    if is_complete:
        desc = summary["summary_line"]
        progress = 100
        status_text = "✓ Complete"
        meta_lines = ["✅ 🦆🦆🦆🦆 All Ducks in a Row!"]
        badges = [{"label": "🦆🦆🦆🦆 Earned", "tone": "success"}]
    elif is_in_progress:
        prog = st.session_state.get("pfma", {}).get("progress", 0)
        desc = f"Resume appointment booking ({prog:.0f}% complete)"
        progress = prog
        status_text = None
        meta_lines = ["≈5–8 min • Ducks in a Row"]
        badges = []
    elif is_locked:
        desc = summary["summary_line"]
        progress = 0
        status_text = None
        meta_lines = ["≈5–8 min • Ducks in a Row"]
        badges = []
    else:
        desc = summary["summary_line"]
        progress = 0
        status_text = None
        meta_lines = ["≈5–8 min • Ducks in a Row"]
        badges = []
    
    return ProductTileHub(
        key="pfma_v2",
        title="Plan with My Advisor",
        desc=desc,
        blurb="Get matched with the right advisor to coordinate care, benefits, and trusted partners.",
        badge_text="CONCIERGE TEAM",
        image_square="pfma.png",
        meta_lines=meta_lines,
        badges=badges,
        primary_route=f"?page={summary['route']}" if summary['route'] else None,
        primary_go="pfma_v2",
        secondary_label="Share updates",
        secondary_go="pfma_updates",
        progress=progress,
        status_text=status_text,
        variant="brand",
        order=30,
        locked=is_locked,
        unlock_requires=["cost:complete"],
        lock_msg="Complete your Cost Planner to book your appointment.",
        recommended_in_hub="concierge",
        recommended_total=hub_order["total"],
        recommended_order=ordered_index.get("pfma_v2", 3),
        recommended_reason=_get_hub_reason(),
        is_next_step=is_next,
    )


def _build_faq_tile() -> ProductTileHub:
    """Build FAQ tile (always available, never locked)."""
    return ProductTileHub(
        key="faqs",
        title="FAQs & Answers",
        desc="Answers in plain language, available whenever you are.",
        blurb=(
            "Search our advisor-reviewed knowledge base or ask Senior Navigator AI for tailored guidance, "
            "resources, and next steps you can share with family."
        ),
        badge_text="AI AGENT",
        image_square="faq.png",
        meta_lines=[
            "Advisor curated responses",
            "Available 24/7",
        ],
        primary_label="Open",
        primary_route="?page=faqs",
        progress=0,
        variant="teal",
        order=40,
        is_next_step=False,
    )

