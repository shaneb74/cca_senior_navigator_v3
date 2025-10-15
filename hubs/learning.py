from __future__ import annotations

from typing import Dict, List

import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.hub_guide import compute_hub_guide
from core.navi import render_navi_panel
from core.product_tile import ProductTileHub
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

__all__ = ["render"]


def _legacy_actions_to_routes(actions: List[Dict[str, str]]) -> Dict[str, str]:
    primary = actions[0] if actions else {}
    secondary = actions[1] if len(actions) > 1 else {}
    return {
        "primary_label": primary.get("label"),
        "primary_route": f"?go={primary.get('route')}" if primary.get("route") else None,
        "secondary_label": secondary.get("label") if secondary.get("route") else None,
        "secondary_route": f"?go={secondary.get('route')}" if secondary.get("route") else None,
    }


def _card_to_tile(card: Dict[str, any], order: int) -> ProductTileHub:
    actions = _legacy_actions_to_routes(card.get("actions", []))
    meta = [str(line) for line in card.get("meta", [])]
    footnote = card.get("footnote")
    if footnote:
        meta.append(str(footnote))

    return ProductTileHub(
        key=card.get("title", f"card-{order}").lower().replace(" ", "-") + f"-{order}",
        title=card.get("title", ""),
        desc=card.get("subtitle", ""),
        blurb=card.get("description", ""),
        badges=card.get("badges", []),
        meta_lines=meta,
        primary_label=actions.get("primary_label"),
        primary_route=actions.get("primary_route") or "#",
        secondary_label=actions.get("secondary_label"),
        secondary_route=actions.get("secondary_route"),
        order=order,
    )


def render(ctx=None) -> None:
    person_name = st.session_state.get("person_name", "").strip()
    learning_progress = st.session_state.get("learning_progress", 0)
    
    completed_resources = st.session_state.get("completed_resources", [])

    modules_viewed = len(completed_resources)

    raw_cards = [
        {
            "title": "Caregiver guides",
            "subtitle": "Step-by-step playbooks",
            "badges": [{"label": "Concierge", "tone": "brand"}],
            "description": "Understand levels of care, funding paths, and decision checklists.",
            "meta": [
                f"{modules_viewed} guide(s) completed",
                "Save favourites to share with family.",
            ],
            "actions": [
                {"label": "Browse guides", "route": "hub_learning"},
                {"label": "Most popular", "route": "hub_learning"},
            ],
            "footnote": "New guides drop every week.",
        },
        {
            "title": "Video library",
            "subtitle": "Sharp insights in under 5 minutes",
            "badges": [{"label": "On demand", "tone": "neutral"}],
            "description": "Walk through real scenarios, from dementia care to financing assisted living.",
            "meta": [
                "Captions + downloadable notes",
                "Created with our advisor network",
            ],
            "actions": [
                {"label": "Watch now", "route": "hub_learning"},
                {"label": "See categories", "route": "hub_learning"},
            ],
            "footnote": "Add videos to your playlist to revisit later.",
        },
        {
            "title": "FAQ center",
            "subtitle": "Ask and explore",
            "badges": [{"label": "AI agent", "tone": "ai"}],
            "description": "Tap into our knowledge base or ask the Senior Navigator AI anything.",
            "meta": [
                "42 topics ready today",
                "Tailored answers for your journey",
            ],
            "actions": [
                {"label": "Search FAQs", "route": "faqs"},
                {"label": "Contact support", "route": "pfma_stub"},
            ],
            "footnote": "AI summaries sync with your dashboard history.",
        },
        {
            "title": "Learning progress",
            "subtitle": f"{learning_progress}% complete",
            "badges": [{"label": "Personalized", "tone": "brand"}],
            "description": "Stay on track with recommended lessons and follow-up actions.",
            "meta": [
                f"Goal: {min(learning_progress + 20, 100)}% by next week",
            ],
            "actions": [
                {"label": "Continue path", "route": "hub_learning"},
                {"label": "Reset topics", "route": "hub_learning"},
            ],
            "footnote": None,
        },
    ]

    cards = [_card_to_tile(card, (idx + 1) * 10) for idx, card in enumerate(raw_cards)]

    # Use callback pattern to render Navi AFTER header
    def render_content():
        # Render Navi panel (after header, before hub content)
        render_navi_panel(location="hub", hub_key="learning")
        
        # Render hub body HTML WITHOUT title/subtitle/chips (Navi replaces them)
        body_html = render_dashboard_body(
            title=None,
            subtitle=None,
            chips=None,
            hub_guide_block=None,  # Navi replaces hub guide
            cards=cards,
            additional_services=get_additional_services("learning"),
        )
        st.markdown(body_html, unsafe_allow_html=True)

    # Render with simple header/footer
    render_header_simple(active_route="hub_learning")
    render_content()
    render_footer_simple()
