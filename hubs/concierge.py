# hubs/concierge.py
"""
Concierge Hub - Navi-Powered Polymorphic Display

This hub uses Navi as the single intelligence layer.
Navi orchestrates journey coordination, Additional Services, and Q&A.
"""
import html
from typing import Optional

import streamlit as st

from core.mcip import MCIP
from core.navi import NaviOrchestrator, render_navi_panel
from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.product_tile import ProductTileHub
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

__all__ = ["render"]


def render(ctx=None) -> None:
    """Render the Concierge Hub with Navi orchestration."""
    
    # Initialize MCIP
    MCIP.initialize()
    
    # Show save confirmation if returning
    # Handle save messages from legacy products (backwards compatibility)
    save_msg = st.session_state.pop("_show_save_message", None)
    if save_msg:
        product_name = {
            "gcp": "Guided Care Plan",
            "gcp_v4": "Guided Care Plan",
            "cost": "Cost Planner",
            "cost_v2": "Cost Planner",
            "pfma": "Plan with My Advisor",
            "pfma_v2": "Plan with My Advisor"
        }.get(save_msg.get("product", ""), "questionnaire")
        
        prog = save_msg.get("progress", 0)
        step = save_msg.get("step", 0)
        total = save_msg.get("total", 0)
        
        if prog >= 100:
            st.success(f"✅ {product_name} complete! You can review your results anytime.")
        else:
            st.info(f"💾 Progress saved! You're {prog:.0f}% through the {product_name} (step {step} of {total}). Click Continue below to pick up where you left off.")
    
    # Get MCIP data for tiles
    progress = MCIP.get_journey_progress()
    next_action = MCIP.get_recommended_next_action()
    
    person_name = st.session_state.get("person_name", "").strip()
    person = person_name if person_name else "you"
    
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
    
    alert_html = _build_saved_progress_alert(save_msg)

    # Use callback pattern to render Navi AFTER header but BEFORE body
    def render_content():
        # Render Navi panel (after header, before hub content)
        render_navi_panel(location="hub", hub_key="concierge")
        
        # Render hub body HTML WITHOUT title/subtitle/chips (Navi replaces them)
        body_html = render_dashboard_body(
            title=None,  # Skip title - Navi provides context
            subtitle=None,  # Skip subtitle - Navi provides context
            chips=None,  # Skip chips - Navi provides status
            hub_guide_block=None,
            hub_order=hub_order,
            cards=cards,
            additional_services=additional,  # Include in HTML for proper layout
        )
        
        full_html = (alert_html or "") + body_html
        st.markdown(full_html, unsafe_allow_html=True)
    
    # Render with simple header/footer (no layout.py)
    render_header_simple(active_route="hub_concierge")
    render_content()
    render_footer_simple()


def _get_hub_reason() -> str:
    """Get contextual reason for hub based on MCIP state."""
    care_rec = MCIP.get_care_recommendation()
    
    if care_rec and care_rec.tier:
        # CRITICAL: These are the ONLY 5 allowed tier display names
        tier_map = {
            "no_care_needed": "No Care Needed",
            "in_home": "In-Home Care",
            "assisted_living": "Assisted Living",
            "memory_care": "Memory Care",
            "memory_care_high_acuity": "Memory Care (High Acuity)"
        }
        tier_label = tier_map.get(care_rec.tier, care_rec.tier.replace("_", " ").title())
        return f"Based on your {tier_label} recommendation"
    
    return "Complete your care plan to personalize your journey"


def _get_product_progress(product_key: str) -> float:
    """Get latest progress percentage for a product from session state."""
    candidates = []
    tiles = st.session_state.get("tiles", {})
    if isinstance(tiles, dict):
        candidates.append(tiles.get(product_key, {}))
    candidates.append(st.session_state.get(product_key, {}))

    if product_key == "gcp_v4":
        candidates.extend([
            st.session_state.get("gcp", {}),
            st.session_state.get("gcp_care_recommendation", {}),
        ])
    elif product_key == "cost_v2":
        candidates.append(st.session_state.get("cost", {}))
    elif product_key == "pfma_v2":
        candidates.append(st.session_state.get("pfma", {}))

    for source in candidates:
        if isinstance(source, dict) and "progress" in source:
            try:
                return float(source.get("progress", 0))
            except Exception:
                continue
    return 0.0


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
    prog = _get_product_progress("gcp_v4")
    is_complete = (summary["status"] == "complete")
    is_in_progress = not is_complete and prog > 0
    is_next = (next_action.get("route") == "gcp_v4")
    
    # DEV MODE: Check for flag validation issues
    dev_warning = None
    if st.session_state.get("dev_mode", False):
        from core.validators import validate_module_flags
        module_path = "products/gcp_v4/modules/care_recommendation/module.json"
        is_valid, flags_used, invalid_flags = validate_module_flags(module_path, "GCP Care Recommendation")
        if not is_valid:
            dev_warning = f"⚠️ DEV: Module uses {len(invalid_flags)} undefined flag(s): {', '.join(invalid_flags[:3])}"
    
    # Build description
    if dev_warning:
        # Show dev warning prominently
        desc = None
        desc_html = f'<span class="text-warning">{dev_warning}</span>'
        status_text = None
        progress = prog if is_in_progress else 0
    elif is_complete:
        desc = None
        desc_html = f'<span class="tile-recommendation">{summary["summary_line"]}</span>'
        status_text = summary["summary_line"]
        progress = 100
    elif is_in_progress:
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
    cost_prog = _get_product_progress("cost_v2")
    is_complete = (summary["status"] == "complete")
    is_locked = (summary["status"] == "locked")
    is_in_progress = not is_complete and not is_locked and cost_prog > 0
    is_next = (next_action.get("route") == "cost_v2")
    
    # Build description and progress
    if is_complete:
        desc = summary["summary_line"]
        progress = 100
        status_text = "✓ Complete"
    elif is_in_progress:
        desc = f"Resume planner ({cost_prog:.0f}% complete)"
        progress = cost_prog
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


def _build_navi_guide_block(ctx) -> str:
    """Compose Navi insight block with gamified encouragement."""
    next_action = NaviOrchestrator.get_next_action(ctx) or {}
    summary = NaviOrchestrator.get_context_summary(ctx)
    reason = next_action.get("reason", "")
    action_label = next_action.get("action", "Continue your journey")
    action_route = next_action.get("route", "gcp_v4") or "gcp_v4"
    if not action_route.startswith("?page="):
        action_route = f"?page={action_route}"

    status = next_action.get("status", "")
    
    # Gamified encouragement messages based on progress
    encouragement_messages = {
        "getting_started": {
            "emoji": "🚀",
            "message": "Let's get started! Every journey begins with a single step.",
            "eyebrow": "Getting started"
        },
        "in_progress": {
            "emoji": "💪",
            "message": "You're making great progress! Keep up the momentum.",
            "eyebrow": "In progress"
        },
        "nearly_there": {
            "emoji": "🎯",
            "message": "Almost there! Just one more step to complete your journey.",
            "eyebrow": "Nearly there"
        },
        "complete": {
            "emoji": "🎉",
            "message": "Amazing work! You've completed all the essentials. Your advisor is ready to help you take the next steps.",
            "eyebrow": "Journey complete"
        }
    }
    
    encouragement = encouragement_messages.get(status, encouragement_messages["getting_started"])
    eyebrow = f"🤖 Navi Insight · {encouragement['eyebrow']}"

    boost_items = NaviOrchestrator.get_context_boost(ctx) or []
    boost_html = ""
    if boost_items:
        items = "".join(f"<li>{html.escape(item)}</li>" for item in boost_items)
        boost_html = (
            '<ul style="margin:0.75rem 0 0;padding-left:1.2rem;color:var(--ink-600);'
            'font-size:0.95rem;line-height:1.55;">' + items + "</ul>"
        )

    # Add encouragement banner between summary and reason
    encouragement_html = (
        '<div style="margin:12px 0;padding:14px 18px;background:linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);'
        'border:1px solid #bfdbfe;border-radius:12px;display:flex;align-items:center;gap:12px;">'
        f'<span style="font-size:1.75rem;line-height:1;">{encouragement["emoji"]}</span>'
        f'<span style="color:var(--ink-600);font-size:0.95rem;font-weight:500;line-height:1.5;">{html.escape(encouragement["message"])}</span>'
        '</div>'
    )

    completed_products = ctx.progress.get("completed_products", []) if ctx.progress else []
    
    # Don't show quick questions until PFMA is complete (keeping users focused)
    suggested = []
    questions_html = ""

    actions_html = (
        f'<a class="btn btn--primary" href="{action_route}" target="_self">{html.escape(action_label)}</a>'
        '<a class="btn btn--secondary" href="?page=faqs" target="_self">Ask Navi →</a>'
    )

    reason_html = html.escape(reason) if reason else ""

    return (
        '<section class="hub-guide hub-guide--full">'
        f'<div class="hub-guide__eyebrow">{eyebrow}</div>'
        f'<h2 class="hub-guide__title">{html.escape(summary)}</h2>'
        + encouragement_html
        + (f'<p class="hub-guide__text">{reason_html}</p>' if reason_html else "")
        + boost_html
        + f'<div class="hub-guide__actions">{actions_html}</div>'
        + questions_html
        + '</section>'
    )


def _build_saved_progress_alert(save_msg: Optional[dict]) -> str:
    if not save_msg:
        return ""
    product_name = {
        "gcp": "Guided Care Plan",
        "gcp_v4": "Guided Care Plan",
        "cost": "Cost Planner",
        "cost_v2": "Cost Planner",
        "pfma": "Plan with My Advisor",
        "pfma_v2": "Plan with My Advisor"
    }.get(save_msg.get("product", ""), "questionnaire")

    prog = save_msg.get("progress", 0)
    if prog >= 100:
        message = f"✅ {product_name} complete! You can review your results anytime."
        style = {
            "bg": "#ecfdf5",
            "border": "#bbf7d0",
            "color": "#047857"
        }
    else:
        step = save_msg.get("step", 0)
        total = save_msg.get("total", 0)
        message = (
            "💾 Progress saved! You're "
            f"{prog:.0f}% through the {product_name} (step {step} of {total}). "
            "Click Continue below to pick up where you left off."
        )
        style = {
            "bg": "#eff6ff",
            "border": "#bfdbfe",
            "color": "#1d4ed8"
        }

    return (
        '<div style="margin-bottom:20px;padding:16px 20px;border-radius:14px;'
        f'background:{style["bg"]};border:1px solid {style["border"]};color:{style["color"]};"'
        f'>{html.escape(message)}</div>'
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
    pfma_prog = _get_product_progress("pfma_v2")
    is_complete = (summary["status"] == "complete")
    is_locked = (summary["status"] == "locked")
    is_in_progress = not is_complete and not is_locked and pfma_prog > 0
    is_next = (next_action.get("route") == "pfma_v2")
    
    # Build description and progress
    if is_complete:
        desc = summary["summary_line"]
        progress = 100
        status_text = "✓ Complete"
        meta_lines = ["✅ 🦆🦆🦆🦆 All Ducks in a Row!"]
        badges = [{"label": "🦆🦆🦆🦆 Earned", "tone": "success"}]
    elif is_in_progress:
        desc = f"Resume appointment booking ({pfma_prog:.0f}% complete)"
        progress = pfma_prog
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


