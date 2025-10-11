from __future__ import annotations

import html
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

import streamlit as st

from core.hub_guide import render_hub_guide
from senior_navigator.ui.tiles import render_product_tile

_CSS_PATH = Path("assets/css/dashboard.css")
_SESSION_FLAG = "_dashboard_css_injected"


@lru_cache(maxsize=1)
def _load_css_text() -> str:
    if not _CSS_PATH.exists():
        return ""
    return _CSS_PATH.read_text(encoding="utf-8")


def inject_dashboard_css() -> None:
    """Attach shared dashboard styles to the Streamlit app."""
    if st.session_state.get(_SESSION_FLAG):
        return
    css = _load_css_text()
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.session_state[_SESSION_FLAG] = True


def render_dashboard(
    *,
    title: str = "",
    subtitle: Optional[str] = None,
    chips: Sequence[Mapping[str, str]] = (),
    callout: Optional[Mapping[str, object]] = None,
    cards: Sequence[object] = (),
    additional_services: Optional[object] = None,
    hub_guide_block: Optional[Mapping[str, object]] = None,
) -> None:
    """Render the shared hub dashboard."""
    inject_dashboard_css()

    chips = list(chips or [])
    cards = list(cards or [])

    # Normalize, filter by visibility, and sort by order then title
    _cards = []
    for c in cards:
        # support both component instances and dict configs
        vis = getattr(c, "visible", True) if hasattr(c, "visible") else c.get("visible", True)
        if not vis:
            continue
        order = getattr(c, "order", 100) if hasattr(c, "order") else c.get("order", 100)
        title = getattr(c, "title", "") if hasattr(c, "title") else c.get("title", "")
        _cards.append((order, str(title).casefold(), c))
    _cards.sort(key=lambda x: (x[0], x[1]))
    sorted_cards = [c for _, __, c in _cards]

    st.markdown('<div class="dashboard-shell">', unsafe_allow_html=True)

    has_head = any([title, subtitle, chips, hub_guide_block, callout])
    if has_head:
        st.markdown('<div class="dashboard-head">', unsafe_allow_html=True)
        if title:
            st.markdown(f'<h1 class="dashboard-title">{_escape(title)}</h1>', unsafe_allow_html=True)
        if subtitle:
            st.markdown(f'<p class="dashboard-subtitle">{_escape(subtitle)}</p>', unsafe_allow_html=True)
        if chips:
            st.markdown('<div class="dashboard-breadcrumbs">', unsafe_allow_html=True)
            for chip in chips:
                label = _escape(chip.get("label", ""))
                if not label:
                    continue
                muted = " is-muted" if chip.get("variant") == "muted" else ""
                st.markdown(f'<span class="dashboard-chip{muted}">{label}</span>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if hub_guide_block:
            render_hub_guide(hub_guide_block)
        elif callout:
            render_hub_guide(callout)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    for card in sorted_cards:
        if hasattr(card, "render") and callable(getattr(card, "render")):
            card.render()
            continue
        if isinstance(card, Mapping):
            if card.get("component") == "product_tile":
                config = card.get("config") or {}
                render_product_tile(dict(config))
            else:
                st.markdown(_render_card(card), unsafe_allow_html=True)
            continue
        st.markdown(str(card), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    addl_markup = _render_additional(additional_services)
    if addl_markup:
        st.markdown(addl_markup, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_additional(data: object) -> str:
    if not data:
        return ""

    if isinstance(data, Mapping):
        items = list(data.get("items") or [])
        if not items:
            return ""
        title = _escape(data.get("title", "Additional services"))
        description = _escape(data.get("description", "Curated partner solutions that complement your plan."))
    elif isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        items = [item for item in data if isinstance(item, Mapping)]
        if not items:
            return ""
        title = "Additional services"
        description = "Curated partner solutions that complement your plan."
    else:
        return ""

    bits = [
        '<section class="dashboard-additional">',
        '<div class="dashboard-additional__head">',
        f'<h3 class="dashboard-additional__title">{_escape(title)}</h3>',
    ]
    if description:
        bits.append(f'<p class="dashboard-muted">{_escape(description)}</p>')
    bits.append("</div>")
    bits.append('<div class="dashboard-additional__grid">')

    for item in items:
        tile = item if isinstance(item, Mapping) else {}
        title_text = _escape(tile.get("title", ""))
        subtitle = _escape(tile.get("subtitle") or tile.get("body") or "")
        go = tile.get("go") or tile.get("route") or tile.get("href") or tile.get("key") or "#"
        label = _escape(tile.get("cta", "Open"))
        href = tile.get("href") or f"?go={go}"

        card_bits = ['<article class="dashboard-additional__card">']
        if title_text:
            card_bits.append(f"<h4>{title_text}</h4>")
        if subtitle:
            card_bits.append(f'<p class="dashboard-muted">{subtitle}</p>')
        card_bits.append(f'<a class="dashboard-additional__cta" href="{_escape(href)}">{label}</a>')
        card_bits.append("</article>")
        bits.append("".join(card_bits))

    bits.append("</div></section>")
    return "".join(bits)


def _render_card(card: Mapping[str, object]) -> str:
    status = (card.get("status") or "new").lower()
    span = int(card.get("span", 4))
    classes = f"dashboard-card is-{status}"
    title = _escape(card.get("title", ""))
    subtitle = _escape(card.get("subtitle", ""))
    description = _escape(card.get("description", ""))
    status_label = _escape(card.get("status_label", status.replace("_", " ").title()))
    badges: Iterable[Mapping[str, str]] = card.get("badges", []) or []
    meta_items: Iterable[str] = card.get("meta", []) or []
    footnote = _escape(card.get("footnote", ""))
    actions: Sequence[Mapping[str, object]] = card.get("actions", []) or []

    html_parts = [
        f'<article class="{classes}" style="grid-column: span {span};">',
        '<div class="dashboard-card__head">',
        '<div class="dashboard-card__title-row">',
        f'<h3 class="dashboard-card__title">{title}</h3>',
    ]
    if status_label:
        html_parts.append(f'<span class="dashboard-status">{status_label}</span>')
    html_parts.append("</div>")
    if subtitle:
        html_parts.append(f'<p class="dashboard-card__subtitle">{subtitle}</p>')
    html_parts.append("</div>")

    badge_markup = []
    for badge in badges:
        label = _escape(badge.get("label", ""))
        if not label:
            continue
        variant = badge.get("variant", "brand")
        badge_markup.append(f'<span class="badge badge--{variant}">{label}</span>')
    if badge_markup:
        html_parts.append('<div class="dashboard-badges">' + "".join(badge_markup) + "</div>")

    if description:
        html_parts.append(f'<p class="dashboard-description">{description}</p>')

    if meta_items:
        html_parts.append('<div class="dashboard-card__meta">')
        for meta in meta_items:
            html_parts.append(f"<span>{_escape(meta)}</span>")
        html_parts.append("</div>")

    if actions:
        html_parts.append('<div class="dashboard-card__actions">')
        for action in actions:
            html_parts.append(_render_action(action))
        html_parts.append("</div>")

    if footnote:
        html_parts.append('<div class="dashboard-card__footer">')
        html_parts.append(f'<span class="dashboard-card__footnote">{footnote}</span>')
        html_parts.append("</div>")

    html_parts.append("</article>")
    return "".join(html_parts)


def _render_action(action: Mapping[str, object], *, primary_default: bool = True) -> str:
    label = _escape(action.get("label", "Open"))
    variant = action.get("variant")
    if not variant and primary_default:
        variant = "primary"
    variant = variant or "ghost"
    href = _action_href(action)
    return f'<a class="dashboard-cta dashboard-cta--{variant}" href="{_escape(href)}">{label}</a>'


def _action_href(action: Mapping[str, object]) -> str:
    href = action.get("href")
    if href:
        return str(href)
    go = action.get("go")
    if go:
        return f"?go={go}"
    route = action.get("route")
    if route:
        return f"?page={route}"
    return "#"


def _escape(value: object) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


__all__ = ["inject_dashboard_css", "render_dashboard"]
