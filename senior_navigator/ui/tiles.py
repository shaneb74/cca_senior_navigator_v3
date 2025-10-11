from __future__ import annotations

import html
from typing import Dict, Iterable

import streamlit as st


def _escape(value: object) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def _render_meta_lines(meta: Iterable[object]) -> str:
    if isinstance(meta, (str, bytes)):
        meta = [meta]
    lines = []
    for item in meta:
        text = _escape(item)
        if text:
            lines.append(f'<div class="ptile__meta">• {text}</div>')
    return "".join(lines)


def render_product_tile(config: Dict[str, object]) -> None:
    """
    Render a large product tile using shared tokens.
    Unknown keys in config are ignored.
    """
    title = _escape(config.get("title"))
    status_text = _escape(config.get("status_text"))
    desc = _escape(config.get("desc"))
    blurb = _escape(config.get("blurb"))
    meta_items = config.get("meta") or []

    primary_label = _escape(config.get("primary_label"))
    primary_go = _escape(config.get("primary_go"))
    secondary_label = _escape(config.get("secondary_label"))
    secondary_go = _escape(config.get("secondary_go"))

    parts = ['<div class="ptile">']
    parts.append(
        f'<div class="ptile__head"><h3 class="ptile__title">{title}</h3>'
        f'<span class="ptile__status">{status_text}</span></div>'
    )
    if desc:
        parts.append(f'<p class="ptile__desc">{desc}</p>')
    if blurb:
        parts.append(f'<p class="ptile__meta">{blurb}</p>')
    parts.append(_render_meta_lines(meta_items))

    actions = []
    if primary_label and primary_go:
        actions.append(f'<a class="ptile__btn" href="?go={primary_go}">{primary_label}</a>')
    if secondary_label and secondary_go:
        actions.append(
            f'<a class="ptile__btn ghost" href="?go={secondary_go}">{secondary_label}</a>'
        )

    if actions:
        parts.append('<div class="ptile__actions">' + "".join(actions) + "</div>")

    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_module_tile(config: Dict[str, object]) -> None:
    """
    Render a compact module tile for product sub-modules.
    Config keys outside the expected set are ignored.
    """
    title = _escape(config.get("title"))
    badge_text = _escape(config.get("badge_text"))
    summary_label = _escape(config.get("summary_label"))
    summary_value = _escape(config.get("summary_value"))
    primary_label = _escape(config.get("primary_label"))
    primary_go = _escape(config.get("primary_go"))
    secondary_label = _escape(config.get("secondary_label"))
    secondary_go = _escape(config.get("secondary_go"))
    status_text = _escape(config.get("status_text"))

    parts = ['<div class="mtile">']
    parts.append('<div class="mtile__row">')
    parts.append(f'<h4 class="mtile__title">{title}</h4>')
    if badge_text:
        parts.append(f'<span class="mtile__badge">{badge_text}</span>')
    parts.append("</div>")

    parts.append(
        '<div class="mtile__summary">'
        '<span aria-hidden="true" style="width:24px;height:24px;border:2px solid #111827;border-radius:6px;display:inline-block"></span>'
        f'<div><div class="label">{summary_label}</div><div class="value">{summary_value}</div></div>'
        "</div>"
    )

    action_bits = []
    if primary_label and primary_go:
        action_bits.append(f'<a class="mtile__link" href="?go={primary_go}">{primary_label}</a>')
    if secondary_label and secondary_go:
        action_bits.append(
            f'<a class="mtile__link" href="?go={secondary_go}">{secondary_label}</a>'
        )
    if status_text:
        action_bits.append(f'<span class="mtile__status">{status_text}</span>')

    if action_bits:
        parts.append('<div class="mtile__actions">' + "".join(action_bits) + "</div>")

    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


__all__ = ["render_product_tile", "render_module_tile"]
