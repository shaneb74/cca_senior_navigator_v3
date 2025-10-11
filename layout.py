from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import streamlit as st

from core.ui import img_src

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
    """Resolve a static image relative to the repo root and return a data URI."""
    path = (STATIC_DIR / filename).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Missing static asset: {filename} (expected at {path})")
    rel_path = path.relative_to(BASE_DIR)
    return img_src(str(rel_path).replace("\\", "/"))


def render_header() -> None:
    logo_url = static_url("logos/cca_logo.png")
    st.markdown(
        dedent(
            f"""
            <header class="welcome-header">
              <div class="container welcome-header__inner">
                <a href="?page=welcome" class="welcome-brand">
                  <img class="welcome-brand__logo" src="{logo_url}" alt="Concierge Care Senior Navigator logo" />
                  <span class="welcome-brand__text">
                    <span>Concierge Care</span>
                    <span>Senior Navigator</span>
                  </span>
                </a>
                <div class="welcome-auth">
                  <a href="?page=login" class="welcome-auth__link">Log in or sign up</a>
                </div>
              </div>
            </header>
            """
        ),
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        dedent(
            f"""
            <footer class="welcome-footer">
              <div class="container">
                <div class="welcome-footer-bottom ordered-footer">
                  <span>© 2025 Concierge Care Senior Navigator™</span>
                  <a class="legal" href="?page=terms">Terms &amp; Conditions</a>
                  <a class="legal" href="?page=privacy">Privacy Policy</a>
                  <a class="social" href="{SOCIAL['instagram']}" target="_blank" rel="noopener">Instagram</a>
                  <a class="social" href="{SOCIAL['facebook']}" target="_blank" rel="noopener">Facebook</a>
                  <a class="social" href="{SOCIAL['x']}" target="_blank" rel="noopener">X</a>
                  <a class="social" href="{SOCIAL['youtube']}" target="_blank" rel="noopener">YouTube</a>
                  <a class="social" href="{SOCIAL['linkedin']}" target="_blank" rel="noopener">LinkedIn</a>
                </div>
              </div>
            </footer>
            """
        ),
        unsafe_allow_html=True,
    )


def render_page(
    content_fn, *args, show_header: bool = True, show_footer: bool = True, **kwargs
) -> None:
    """Render a page with optional header and footer chrome."""
    if show_header:
        render_header()
    content_fn(*args, **kwargs)
    if show_footer:
        render_footer()


__all__ = ["render_header", "render_footer", "render_page", "static_url", "SOCIAL"]
