from __future__ import annotations

from html import escape as _escape
from typing import Dict

import streamlit as st


def header(step_index: int, total: int, title: str, subtitle: str | None = None) -> None:
    dots = "".join(
        [
            f"<span class='step-pill{' is-active' if i == step_index else ''}'></span>"
            for i in range(total)
        ]
    )
    subtitle_html = f"<div class='lead'>{_escape(subtitle)}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="mod-head">
          <div class="mod-steps">{dots}</div>
          <div class="mod-head-row">
            <a class="mod-back" href="javascript:history.back()">← Back</a>
            <h2 class="h2">{_escape(title)}</h2>
          </div>
          {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def actions(next_label: str = "Continue", skip_label: str | None = "Skip") -> tuple[bool, bool]:
    cols = st.columns(2) if skip_label else [st.container()]
    with cols[0]:
        next_clicked = st.button(next_label, type="primary", key="_mod_next")
    skip_clicked = False
    if skip_label:
        with cols[1]:
            skip_clicked = st.button(skip_label, key="_mod_skip")
    return next_clicked, skip_clicked


def bottom_summary(items: Dict[str, str]) -> None:
    if not items:
        return
    chips = "".join(
        f"<div class='sum-item'><div class='meta'>{_escape(k)}</div><div class='value'>{_escape(v)}</div></div>"
        for k, v in items.items()
    )
    st.markdown(
        f"<div class='mod-bottom'>{chips}</div>",
        unsafe_allow_html=True,
    )


__all__ = ["header", "actions", "bottom_summary"]
