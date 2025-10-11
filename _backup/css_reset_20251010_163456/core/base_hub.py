# core/base_hub.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


# -----------------------------
# CSS injector (theme -> hub_grid -> dashboard), once per session
# -----------------------------
def _inject_hub_css_once(show_probe: bool = False) -> List[str]:
    """
    Load hub CSS in this order (later overrides earlier):
      1) assets/css/theme.css
      2) assets/css/hub_grid.css
      3) assets/css/dashboard.css
    Returns a list of loaded sources (paths or "[inline fallback]").
    """
    key = "_sn_hub_css_loaded_v2"
    if isinstance(st.session_state.get(key), list):
        return st.session_state[key]

    here = Path(__file__).resolve().parent
    candidates = [
        # normal repo-root paths
        Path("assets/css/theme.css"),
        Path("assets/css/hub_grid.css"),
        Path("assets/css/dashboard.css"),
        # defensive fallbacks if CWD differs
        here.parents[1] / "assets" / "css" / "theme.css",
        here.parents[1] / "assets" / "css" / "hub_grid.css",
        here.parents[1] / "assets" / "css" / "dashboard.css",
    ]

    loaded: List[str] = []
    for css_path in candidates:
        try:
            if css_path.is_file():
                css = css_path.read_text(encoding="utf-8")
                # guard against stray </style> in file content
                if "</style>" in css.lower():
                    continue
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
                loaded.append(str(css_path))
        except Exception:
            continue

    if not loaded:
        # Minimal fallback so hubs still look like hubs
        fallback_css = """
/* Fallback hub grid + card (inlined) */
.sn-hub.dashboard-shell{min-height:auto;background:linear-gradient(180deg,rgba(230,238,255,.65) 0%,rgba(247,249,252,.95) 52%,#fff 100%)}
.sn-hub .dashboard-grid{display:grid;grid-template-columns:repeat(12,1fr);gap:1.5rem}
.sn-hub .dashboard-grid > [data-testid="stMarkdownContainer"],
.sn-hub .dashboard-grid > [data-testid="stMarkdown"],
.sn-hub .dashboard-grid > div[data-testid="stMarkdown"]{grid-column:span 6 !important}
@media (max-width:900px){
  .sn-hub .dashboard-grid > [data-testid="stMarkdownContainer"],
  .sn-hub .dashboard-grid > [data-testid="stMarkdown"],
  .sn-hub .dashboard-grid > div[data-testid="stMarkdown"]{grid-column:span 12 !important}
}
.sn-hub .dashboard-grid .ptile{grid-column:span 6}
.sn-hub .dashboard-grid .mtile{grid-column:span 12}
@media (max-width:900px){.sn-hub .dashboard-grid .ptile,.sn-hub .dashboard-grid .mtile{grid-column:span 12}}
.sn-hub .dashboard-card{background:#fff;border:1px solid #d8e0ea;border-radius:16px;padding:1.5rem;box-shadow:0 1px 1px rgba(0,0,0,.02),0 8px 18px rgba(0,0,0,.06)}
        """.strip()
        st.markdown(f"<style>{fallback_css}</style>", unsafe_allow_html=True)
        loaded.append("[inline fallback]")

    st.session_state[key] = loaded
    if show_probe:
        st.caption(f"Hub CSS loaded: {', '.join(loaded)}")
    return loaded


# -----------------------------
# Primary hub renderer (namespaced shell)
# -----------------------------
def render_dashboard(
    *,
    title: str = "",
    subtitle: Optional[str] = None,
    chips: Optional[List[Dict[str, str]]] = None,
    hub_guide_block: Optional[Dict[str, Any]] = None,
    cards: Optional[List[Any]] = None,
    additional_services: Optional[List[Dict[str, Any]]] = None,
    **_ignored,  # ignore legacy extras safely
) -> None:
    st.set_page_config(layout="wide")
    loaded = _inject_hub_css_once(show_probe=True)

    # Visible probe bar so we know injection happened:
    # green = file CSS loaded, yellow = inline fallback only.
    probe_color = (
        "#00e676" if any(src != "[inline fallback]" for src in loaded) else "#ffdd57"
    )
    st.markdown(
        f'<div style="height:3px;background:{probe_color};margin:-0.5rem 0 0.75rem;border-radius:2px"></div>',
        unsafe_allow_html=True,
    )

    # Small local tweaks that shouldn't live in global CSS
    st.markdown(
        """
        <style>
          div.block-container { padding-top: 1.2rem; }
          .sn-hub .dashboard-head { padding: 0; margin: 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    chips = chips or []
    cards = cards or []

    # Shell
    st.markdown('<div class="sn-hub dashboard-shell">', unsafe_allow_html=True)

    # Header
    if any([title, subtitle, chips, hub_guide_block]):
        st.markdown('<div class="dashboard-head">', unsafe_allow_html=True)

        if title:
            st.markdown(
                f'<h1 class="dashboard-title">{title}</h1>', unsafe_allow_html=True
            )
        if subtitle:
            st.markdown(
                f'<p class="dashboard-subtitle">{subtitle}</p>', unsafe_allow_html=True
            )
        if chips:
            st.markdown('<div class="dashboard-breadcrumbs">', unsafe_allow_html=True)
            for chip in chips:
                cls = "dashboard-chip" + (
                    " is-muted" if chip.get("variant") == "muted" else ""
                )
                st.markdown(
                    f'<span class="{cls}">{chip.get("label","")}</span>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        if hub_guide_block:
            from core.hub_guide import render_hub_guide

            render_hub_guide(hub_guide_block)

        st.markdown("</div>", unsafe_allow_html=True)

    # Cards grid (ordered)
    sorted_cards: List[Tuple[int, str, Any]] = []
    for c in cards:
        vis = (
            getattr(c, "visible", True)
            if hasattr(c, "visible")
            else c.get("visible", True)
        )
        if not vis:
            continue
        order = (
            getattr(c, "order", 100)
            if hasattr(c, "order")
            else int(c.get("order", 100))
        )
        t = getattr(c, "title", "") if hasattr(c, "title") else c.get("title", "")
        sorted_cards.append((int(order), str(t).casefold(), c))
    sorted_cards.sort(key=lambda x: (x[0], x[1]))

    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    for _, __, card in sorted_cards:
        if hasattr(card, "render"):
            card.render()
        elif isinstance(card, dict) and card.get("html"):
            st.markdown(str(card["html"]), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Additional services (optional)
    if additional_services:
        st.markdown('<section class="dashboard-additional">', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-additional__head">', unsafe_allow_html=True)
        st.markdown(
            '<h3 class="dashboard-additional__title">Additional services</h3>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="dashboard-muted">Curated partner solutions that complement your plan.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="dashboard-additional__grid">', unsafe_allow_html=True)
        for s in additional_services:
            st.markdown(
                '<div class="dashboard-additional__card">', unsafe_allow_html=True
            )
            st.markdown(f'<h4>{s["title"]}</h4>', unsafe_allow_html=True)
            if s.get("subtitle"):
                st.markdown(f"<p>{s['subtitle']}</p>", unsafe_allow_html=True)
            st.markdown(
                f'<a class="dashboard-additional__cta" href="?go={s.get("go", "")}">{s.get("cta", "Open")}</a>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</section>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<style>.sn-hub .dashboard-card{outline:2px solid red!important}</style>",
        unsafe_allow_html=True,
    )


# -----------------------------
# Back-compat helpers
# -----------------------------
def status_label(progress: float | int | None, locked: bool = False) -> str:
    """Legacy helper that returns a simple status string."""
    if locked:
        return "Locked"
    if progress is None:
        return ""
    try:
        p = float(progress)
    except Exception:
        p = 0.0
    if p >= 100:
        return "Complete"
    if p > 0:
        return "In progress"
    return "New"


class BaseHub:
    """
    Legacy wrapper so old hubs that did:

        from core.base_hub import BaseHub
        hub = BaseHub()
        hub.render(title=..., cards=[...])

    still work. Internally delegates to render_dashboard.
    """

    def __init__(self, **default_kwargs):
        self._default_kwargs = dict(default_kwargs or {})

    def render(self, **kwargs) -> None:
        merged = {**self._default_kwargs, **kwargs}

        # Accept only the keys render_dashboard cares about.
        allowed = {
            "title",
            "subtitle",
            "chips",
            "hub_guide_block",
            "cards",
            "additional_services",
        }
        safe = {k: v for k, v in merged.items() if k in allowed}

        # Common legacy aliases
        if "guide" in merged and "hub_guide_block" not in safe:
            safe["hub_guide_block"] = merged["guide"]
        if "additional" in merged and "additional_services" not in safe:
            safe["additional_services"] = merged["additional"]

        render_dashboard(**safe)


__all__ = ["render_dashboard", "BaseHub", "status_label", "_inject_hub_css_once"]
