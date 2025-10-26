import importlib
import json
from collections.abc import Callable

import streamlit as st
from core.url_helpers import route_to as url_route_to, current_route as url_current_route

# Registry records
PRODUCTS = {
    "gcp": {"hub": "concierge", "title": "Guided Care Plan", "route": "/product/gcp"},
    "gcp_v4": {"hub": "concierge", "title": "Guided Care Plan", "route": "/product/gcp_v4"},
    "cost_planner": {
        "hub": "concierge",
        "title": "Cost Planner",
        "route": "/products/cost_planner",
    },
    "cost_v2": {
        "hub": "concierge",
        "title": "Cost Planner",
        "route": "/products/cost_planner_v2",
    },
    "pfma": {
        "hub": "concierge",
        "title": "Plan with My Advisor",
        "route": "/products/pfma",
    },
    "pfma_v2": {
        "hub": "concierge",
        "title": "Plan with My Advisor",
        "route": "/products/pfma_v2",
    },
}


def _import_callable(path: str) -> Callable:
    mod, fn = path.split(":")
    return getattr(importlib.import_module(mod), fn)


def load_nav(ctx: dict) -> dict[str, dict]:
    with open("config/nav.json", encoding="utf-8") as f:
        cfg = json.load(f)

    role = ctx["auth"].get("role", "guest")
    is_auth = ctx["auth"].get("is_authenticated", False)
    flags = {k for k, v in ctx.get("flags", {}).items() if v}

    pages: dict[str, dict] = {}
    for group in cfg["groups"]:
        for item in group["items"]:
            if item.get("requires_auth") and not is_auth:
                continue
            if item.get("hide_when_auth") and is_auth:
                continue
            if "roles" in item and role not in item["roles"]:
                continue
            if "flags" in item and not set(item["flags"]).issubset(flags):
                continue
            pages[item["key"]] = {
                "label": item["label"],
                "render": _import_callable(item["module"]),
                "group": group["label"],
                "hidden": item.get("hidden", False),
            }
    return pages


def route_to(key: str, **context) -> None:
    """Navigate to a page by updating query params and triggering rerun.

    Preserves UID in query params to maintain session across navigation.
    Uses URL-driven routing with history support.
    
    Optional context params are stored in session_state["_nav_context"] for
    the target page to consume (e.g., seed tags, query prefill).

    Args:
        key: Page key from nav.json (e.g., "hub_concierge")
        **context: Optional context data (seed, from_faq, tags, etc.)
    """
    # Store context for target page
    if context:
        st.session_state["_nav_context"] = {"route": key, **context}
    
    # Preserve UID when routing
    uid = st.query_params.get("uid")
    route_params = {"page": key}
    if uid:
        route_params["uid"] = uid
    
    # Use URL-driven routing with history support
    url_route_to(**route_params)


def current_route(default: str, pages: dict[str, dict]) -> str:
    """Get current route from query params.

    Args:
        default: Default page key if none set
        pages: Available pages dict

    Returns:
        Current page key or default
    """
    # Normalize query params for navigation (works with href links from tiles)
    aliases = {
        "faqs": "faq",
        "faq": "faq",
        "faqs_and_answers": "faq",
        "ai_advisor": "faq",
        "advisor": "faq",
    }

    raw_page = st.query_params.get("page")
    candidate = raw_page or default

    if isinstance(candidate, str):
        normalized = candidate.lower().strip()
    else:
        normalized = default

    page = aliases.get(normalized, normalized)

    if page not in pages:
        page = default

    st.session_state["current_route"] = page
    return page
