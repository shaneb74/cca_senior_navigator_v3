from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

import streamlit as st

from core.base_hub import render_dashboard_body
from core.hub_guide import compute_hub_guide, partners_intel_from_state
from core.navi import render_navi_panel
from core.product_tile import ProductTileHub, tile_requirements_satisfied
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

DATA_DIR = Path(__file__).resolve().parents[1] / "config"
PARTNERS_FILE = DATA_DIR / "partners.json"
CATEGORIES_FILE = DATA_DIR / "partner_categories.json"
FILTER_KEY = "_partners_filters"


def _load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _get_filters(default_state: str, categories: Mapping[str, Dict[str, Any]]) -> Dict[str, str]:
    stored = st.session_state.get(FILTER_KEY, {})
    default_filters = {
        "q": stored.get("q", ""),
        "cat": stored.get("cat", "all"),
        "state": stored.get("state", default_state or "any"),
    }

    with st.sidebar:
        st.subheader("Filter partners")
        search_value = st.text_input(
            "Search", value=default_filters["q"], placeholder="Search partners…"
        )
        cat_options = ["all"] + list(categories.keys())
        category_value = st.selectbox(
            "Category",
            options=cat_options,
            index=(
                cat_options.index(default_filters["cat"])
                if default_filters["cat"] in cat_options
                else 0
            ),
            format_func=lambda c: "All categories" if c == "all" else categories[c]["label"],
        )
        coverage_options = ["any"]
        if default_state:
            coverage_options.append(default_state)
        state_value = st.selectbox(
            "Coverage",
            options=coverage_options,
            index=(
                coverage_options.index(default_filters["state"])
                if default_filters["state"] in coverage_options
                else 0
            ),
            format_func=lambda s: "Any coverage" if s == "any" else f"Near me ({s})",
        )

    filters = {"q": search_value, "cat": category_value, "state": state_value}
    st.session_state[FILTER_KEY] = filters
    return filters


def _matches_filters(partner: Dict[str, Any], filters: Dict[str, str]) -> bool:
    query = filters["q"].strip().lower()
    if query:
        haystack = " ".join(
            str(partner.get(field, "")) for field in ("name", "headline", "blurb")
        ).lower()
        if query not in haystack:
            return False

    category_filter = filters["cat"]
    if category_filter != "all" and partner.get("category") != category_filter:
        return False

    state_filter = filters["state"]
    if state_filter != "any":
        partner_states = partner.get("states") or []
        if "US" not in partner_states and state_filter not in partner_states:
            return False

    return True


def _partner_to_tile(
    partner: Dict[str, Any], state: Mapping[str, Any], order: int
) -> ProductTileHub:
    unlocked = tile_requirements_satisfied(partner.get("unlock_requires"), state)
    lock_msg = partner.get("lock_msg") or ""
    rating = partner.get("rating")

    meta_lines: List[str] = []
    if isinstance(rating, (int, float)):
        meta_lines.append(f"Rating {rating:.1f}")

    primary = partner.get("primary_cta") or {}
    secondary = partner.get("secondary_cta") or {}

    return ProductTileHub(
        key=partner.get("id", partner.get("name", "partner")),
        title=partner.get("name", ""),
        desc=partner.get("headline", ""),
        blurb=partner.get("blurb", ""),
        image_square=partner.get("image_square"),
        badges=partner.get("tags", []),
        meta_lines=meta_lines,
        progress=None,
        locked=not unlocked,
        lock_msg=(lock_msg if not unlocked else None),
        unlock_requires=partner.get("unlock_requires") or [],
        primary_route=primary.get("route", "#"),
        primary_label=primary.get("label", "Connect"),
        secondary_route=secondary.get("route") if secondary else None,
        secondary_label=(
            secondary.get("label", "Learn more") if secondary and secondary.get("route") else None
        ),
        variant="partner",
        order=order,
        visible=True,
    )


def page_partners() -> None:
    partners: List[Dict[str, Any]] = _load_json(PARTNERS_FILE)
    categories_data: List[Dict[str, Any]] = _load_json(CATEGORIES_FILE)
    categories = {entry["id"]: entry for entry in categories_data}

    profile_state = (
        st.session_state.get("profile", {}).get("state")
        or st.session_state.get("location_state")
        or "WA"
    )
    filters = _get_filters(str(profile_state), categories)

    filtered_partners = [p for p in partners if _matches_filters(p, filters)]

    guide_html = compute_hub_guide(
        "partners",
        hub_order=None,
        extra_panel=partners_intel_from_state(st.session_state),
    )

    tiles = [
        _partner_to_tile(partner, st.session_state, (idx + 1) * 10)
        for idx, partner in enumerate(filtered_partners)
    ]

    cards_html = None
    if not tiles:
        cards_html = '<div class="dashboard-grid"><div class="dashboard-empty">No partners match your filters yet.</div></div>'

    # Use callback pattern to render Navi AFTER header
    def render_content():
        # Render Navi panel (after header, before hub content)
        render_navi_panel(location="hub", hub_key="partners")
        
        # Render hub body HTML WITHOUT title/chips (Navi replaces them)
        body_html = render_dashboard_body(
            title=None,
            chips=None,
            hub_guide_block=None,  # Navi replaces hub guide
            cards=tiles if tiles else None,
            cards_html=cards_html,
        )
        st.markdown(body_html, unsafe_allow_html=True)

    # Render with simple header/footer
    render_header_simple(active_route="hub_trusted")
    render_content()
    render_footer_simple()


render = page_partners


__all__ = ["page_partners", "render"]
