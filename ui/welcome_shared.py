from __future__ import annotations

import html
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

import streamlit as st

from core.nav import route_to
from core.ui import img_src as resolve_img

_CSS_PATH = Path("assets/css/welcome.css")
_CSS_FLAG = "_welcome_css_loaded"

_PILLS: Dict[str, Dict[str, Optional[str]]] = {
    "someone": {"label": "For someone", "page": "pages/someone_else.py", "fallback": "for_someone"},
    "self": {"label": "For me", "page": "pages/self.py", "fallback": "for_me_contextual"},
    "pro": {"label": "Professional", "page": "pages/professionals.py", "fallback": None},
}


@lru_cache(maxsize=1)
def _load_css() -> str:
    if not _CSS_PATH.exists():
        return ""
    return _CSS_PATH.read_text(encoding="utf-8")


def inject_welcome_css() -> None:
    if st.session_state.get(_CSS_FLAG):
        return
    css = _load_css()
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.session_state[_CSS_FLAG] = True


def _go_to(page_path: Optional[str], fallback_route: Optional[str]) -> None:
    switch_fn = getattr(st, "switch_page", None)
    if page_path and callable(switch_fn):
        try:
            switch_fn(page_path)
            return
        except Exception:
            pass
    if fallback_route:
        try:
            route_to(fallback_route)
        except Exception:
            pass


def render_welcome_card(
    *,
    active: str,
    title: str,
    placeholder: str,
    note: str,
    image_path: str,
    submit_route: Optional[str] = "hub_concierge",
) -> None:
    inject_welcome_css()

    safe_active = active if active in _PILLS else "someone"
    photo_data = resolve_img(image_path)
    alt_text = {
        "someone": "Family support hero image",
        "self": "Self planning hero image",
        "pro": "Professional coordination hero image",
    }.get(safe_active, "Welcome illustration")

    st.markdown('<div class="wl-shell"><div class="wl-hero">', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.05, 0.95], gap="large")

    with left_col:
        st.markdown('<div class="wl-frame"><div class="wl-card">', unsafe_allow_html=True)

        pill_container = st.container()
        with pill_container:
            st.markdown('<div class="wl-pills">', unsafe_allow_html=True)
            pill_cols = st.columns(len(_PILLS))
            for (key, config), col in zip(_PILLS.items(), pill_cols):
                with col:
                    disabled = key == safe_active
                    if st.button(
                        config["label"],
                        key=f"wl-pill-{key}",
                        disabled=disabled,
                        type="secondary",
                        use_container_width=True,
                    ):
                        _go_to(config.get("page"), config.get("fallback"))
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f'<h1 class="wl-title">{html.escape(title)}</h1>', unsafe_allow_html=True)

        form = st.form(f"welcome-form-{safe_active}", clear_on_submit=False)
        with form:
            form_row = st.container()
            form_row.markdown('<div class="wl-input-row">', unsafe_allow_html=True)
            input_col, button_col = form_row.columns([3, 2], gap="small")
            with input_col:
                name_value = st.text_input(
                    placeholder,
                    key=f"welcome-name-{safe_active}",
                    label_visibility="collapsed",
                    placeholder=placeholder,
                )
            with button_col:
                submitted = st.form_submit_button("Continue", type="primary")
            form_row.markdown("</div>", unsafe_allow_html=True)

        if submitted and name_value.strip():
            st.session_state["person_name"] = name_value.strip()
            if submit_route:
                _go_to(None, submit_route)

        st.markdown(
            f'<div class="wl-note"><p class="wl-note__text">{html.escape(note)}</p></div>',
            unsafe_allow_html=True,
        )

        st.markdown("</div></div>", unsafe_allow_html=True)

    with right_col:
        if photo_data:
            st.markdown(
                f'<div class="wl-right"><div class="wl-photo"><img src="{photo_data}" alt="{html.escape(alt_text)}"/></div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("</div></div>", unsafe_allow_html=True)


__all__ = ["inject_welcome_css", "render_welcome_card"]
