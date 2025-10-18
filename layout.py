from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from textwrap import dedent
from typing import Any

import streamlit as st

from core.ui import safe_img_src

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static" / "images"

SOCIAL = {
    "instagram": "https://www.instagram.com/conciergecareadvisors/",
    "facebook": "https://www.facebook.com/ConciergeCareAdvisors/",
    "x": "https://x.com/ConciergeCareWA",
    "youtube": "https://www.youtube.com/channel/UCOboMytz50ccLE32xga3Tig",
    "linkedin": "https://www.linkedin.com/company/concierge-care-advisors",
}


def static_url(filename: str) -> str:
    """
    Accepts any of:
      - "gcp.png"
      - "images/gcp.png"
      - "static/images/gcp.png"
    and returns a repo-relative URL via img_src.
    """
    from core.ui import img_src  # lazy import to avoid circular deps

    safe = filename.lstrip("/").replace("\\", "/")
    if safe.startswith("static/images/"):
        safe = safe[len("static/images/") :]
    elif safe.startswith("images/"):
        safe = safe[len("images/") :]

    path = (STATIC_DIR / safe).resolve()
    try:
        path.relative_to(STATIC_DIR)
    except ValueError:
        raise FileNotFoundError(f"Missing static asset: {filename} (expected at {path})")
    if not path.exists():
        raise FileNotFoundError(f"Missing static asset: {filename} (expected at {path})")

    rel_path = path.relative_to(BASE_DIR)
    return img_src(str(rel_path).replace("\\", "/"))


def _current_page() -> str:
    qp = st.query_params
    if "page" in qp:
        value = qp["page"]
        if isinstance(value, list) and value:
            return str(value[0])
        return str(value)
    return "welcome"


def _nav_link(label: str, key: str, current: str | None = None) -> str:
    active = " is-active" if current == key else ""
    return f'<a href="?page={key}" class="nav-link{active}">{label}</a>'


RESPONSIVE_CSS = dedent(
    """
    <style>
    @media (max-width: 900px){
      .header__inner .global-nav { display: none; }
      .header__inner .nav-toggle { display: inline-block; }
      body.nav-open .header__inner .global-nav {
        display: flex; position: absolute; top: 56px; right: 0; left: 0;
        background: #fff; border-top: 1px solid #e6edf5; padding: 12px 16px; gap: 10px; flex-wrap: wrap;
        box-shadow: 0 6px 18px rgba(15,23,42,.08);
      }
      body.nav-open .header__inner .global-nav .nav-link,
      body.nav-open .header__inner .global-nav .btn { width: 100%; justify-content: center; }
    }
    </style>
    """
).strip()


def _build_header(active_route: str | None = None) -> str:
    from core.state import get_user_name, is_authenticated

    logo_url = safe_img_src("cca_logo.png")
    brand_html = ""
    if logo_url:
        brand_html = f'<img src="{logo_url}" alt="Concierge Care Advisors" class="brand-logo" />'
    current = active_route or _current_page()

    # Build navigation links
    nav_links = [
        _nav_link("Welcome", "welcome", current),
        _nav_link("Concierge", "hub_concierge", current),
        _nav_link("Waiting Room", "hub_waiting", current),
        _nav_link("Learning", "hub_learning", current),
        _nav_link("Trusted Partners", "hub_trusted", current),
        _nav_link("Professional", "hub_professional", current),
    ]

    links = "".join(nav_links)

    # Auth button - toggles between login and logout
    if is_authenticated():
        user_name = get_user_name()
        display_name = user_name if user_name else "User"
        auth_button = (
            f'<div class="header-auth">'
            f'<span class="header-auth__greeting">👋 {display_name}</span>'
            f'<a href="?page=logout" class="btn btn--secondary header-auth__logout">Log out</a>'
            f"</div>"
        )
    else:
        auth_button = '<a href="?page=login" class="btn btn--secondary" style="height:32px;padding:0 12px">Log in</a>'

    return dedent(
        f"""
        <header class="header sn-global-header" id="sn-global-header">
        <div class="container header__inner">
        <div class="brand">
        <button class="nav-toggle" aria-label="Toggle navigation" onclick="document.body.classList.toggle('nav-open')">☰</button>
        {brand_html}
        <span class="brand-text">Senior Navigator</span>
        </div>
        <nav class="nav cluster global-nav">
        {links}
        {auth_button}
        </nav>
        </div>
        </header>
        """
    ).strip()


FOOTER_HTML = dedent(
    f"""
    <footer class="footer">
    <div class="container footer__inner">
    <div class="muted">© 2025 Concierge Care Senior Navigator™</div>
    <div class="cluster footer-links">
    <a href="?page=terms" class="nav-link">Terms &amp; Conditions</a>
    <a href="?page=privacy" class="nav-link">Privacy Policy</a>
    <a href="?page=about" class="nav-link">About</a>
    <a href="{SOCIAL["instagram"]}" class="nav-link" target="_blank" rel="noopener">Instagram</a>
    <a href="{SOCIAL["facebook"]}" class="nav-link" target="_blank" rel="noopener">Facebook</a>
    <a href="{SOCIAL["x"]}" class="nav-link" target="_blank" rel="noopener">X</a>
    <a href="{SOCIAL["youtube"]}" class="nav-link" target="_blank" rel="noopener">YouTube</a>
    <a href="{SOCIAL["linkedin"]}" class="nav-link" target="_blank" rel="noopener">LinkedIn</a>
    </div>
    </div>
    </footer>
    """
).strip()


_RESPONSIVE_SENTINEL = "_sn_header_css_injected"
_FRAME_SENTINEL = "_global_frame_rendered"
_HEADER_SENTINEL = "_sn_global_header_rendered"


def _ensure_global_css() -> None:
    """Attempt to inject global CSS without breaking if the injector is unavailable."""
    try:
        from app import inject_css  # type: ignore
    except Exception:
        return
    try:
        inject_css()
    except Exception:
        pass


def render_page(
    content: Callable[..., Any] | str | None = None,
    *args: Any,
    body_html: str | None = None,
    show_header: bool = True,
    show_footer: bool = True,
    title: str = "",
    active_route: str | None = None,
    sidebar_html: str | None = None,
    body_only: bool = False,
    **kwargs: Any,
) -> None:
    # Always ensure global CSS is injected for consistent styling
    _ensure_global_css()

    if body_only:
        if body_html is not None:
            st.markdown(body_html, unsafe_allow_html=True)
        if callable(content):
            content(*args, **kwargs)
        elif isinstance(content, str):
            st.markdown(content, unsafe_allow_html=True)
        return

    if st.session_state.get(_FRAME_SENTINEL):
        if body_html is not None:
            st.markdown(body_html, unsafe_allow_html=True)
        if callable(content):
            content(*args, **kwargs)
        elif isinstance(content, str):
            st.markdown(content, unsafe_allow_html=True)
        return

    st.session_state[_FRAME_SENTINEL] = True

    if not st.session_state.get(_RESPONSIVE_SENTINEL):
        st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)
        st.session_state[_RESPONSIVE_SENTINEL] = True

    if show_header:
        render_header(active_route=active_route)

    if title:
        st.markdown(
            f"<div class='container'><h1 class='hero-title' style='margin:.5rem 0 0'>{title}</h1></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<main class='container stack'>", unsafe_allow_html=True)
    if body_html is not None:
        st.markdown(body_html, unsafe_allow_html=True)
    elif callable(content):
        content(*args, **kwargs)
    elif content is not None:
        st.markdown(str(content), unsafe_allow_html=True)
    st.markdown("</main>", unsafe_allow_html=True)

    if sidebar_html:
        st.sidebar.markdown(sidebar_html, unsafe_allow_html=True)

    if show_footer:
        render_footer()


def render_header(active_route: str | None = None) -> None:
    _ensure_global_css()
    if not st.session_state.get(_RESPONSIVE_SENTINEL):
        st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)
        st.session_state[_RESPONSIVE_SENTINEL] = True
    if st.session_state.get(_HEADER_SENTINEL):
        return
    st.session_state[_HEADER_SENTINEL] = True
    st.markdown(_build_header(active_route=active_route), unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)


def render_shell_start(
    title: str = "",
    *,
    active_route: str | None = None,
    show_header: bool = True,
) -> None:
    """Open the global layout shell without relying on render_page."""
    try:
        from core.base_hub import _inject_hub_css_once  # type: ignore
    except Exception:
        _inject_hub_css_once = None
    else:
        try:
            _inject_hub_css_once()  # type: ignore[misc]
        except Exception:
            pass
    _ensure_global_css()
    if not st.session_state.get(_RESPONSIVE_SENTINEL):
        st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)
        st.session_state[_RESPONSIVE_SENTINEL] = True
    if show_header:
        render_header(active_route=active_route)
    if title:
        st.markdown(
            f"<div class='container'><h1 class='hero-title' style='margin:.5rem 0 0'>{title}</h1></div>",
            unsafe_allow_html=True,
        )
    st.markdown("<main class='container stack'>", unsafe_allow_html=True)
    st.session_state[_FRAME_SENTINEL] = True


def render_shell_end(*, show_footer: bool = True) -> None:
    """Close the global layout shell opened via render_shell_start."""
    st.markdown("</main>", unsafe_allow_html=True)
    if show_footer:
        render_footer()


def reset_global_frame() -> None:
    st.session_state.pop(_FRAME_SENTINEL, None)
    st.session_state.pop(_RESPONSIVE_SENTINEL, None)
    st.session_state.pop(_HEADER_SENTINEL, None)
    # Also reset hub CSS flag so it gets re-injected on next hub render
    st.session_state.pop("_sn_hub_css_loaded_v4", None)


__all__ = [
    "render_page",
    "render_shell_start",
    "render_shell_end",
    "render_header",
    "render_footer",
    "static_url",
    "reset_global_frame",
]
