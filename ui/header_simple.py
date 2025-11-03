"""Simple header component - no layout.py, no session state manipulation."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import streamlit as st

from core.state import is_authenticated, get_user_name, logout_user
from core.ui import img_src
from core.url_helpers import add_uid_to_href, can_go_back, go_back, back_fallback, route_to


def render_back_button(title: str = "") -> None:
    """
    Render a consistent Back button with optional title.
    
    Uses navigation stack if available, otherwise returns to hub.
    
    Args:
        title: Optional title to display next to back button
    """
    cols = st.columns([1, 12])
    with cols[0]:
        if st.button("← Back", key="global_back_btn", use_container_width=True):
            if can_go_back():
                go_back()
            else:
                route_to(push=False, **back_fallback())
    with cols[1]:
        if title:
            st.subheader(title)


def render_header_simple(active_route: str | None = None) -> None:
    """
    Render a clean, single-line header with logo and navigation links.

    Uses plain <a href="?page=X"> links for instant navigation without reruns.
    No session state writes, no st.button() complexity.

    Args:
        active_route: Current page route (e.g., 'welcome', 'hub_concierge')
    """
    logo_url = img_src("assets/images/logos/cca_logo.png")

    # Load UI configuration for nav visibility
    ui_config_path = Path(__file__).parent.parent / "config" / "ui_config.json"
    nav_visibility = {}
    try:
        with open(ui_config_path, encoding="utf-8") as f:
            ui_config = json.load(f)
            nav_visibility = ui_config.get("header", {}).get("nav_items", {})
    except (FileNotFoundError, json.JSONDecodeError):
        # If config doesn't exist or is invalid, show all items by default
        pass

    # Define navigation items (use exact keys from nav.json)
    # Visibility controlled by config/ui_config.json
    all_nav_items = [
        {"label": "Welcome", "route": "welcome"},
        {"label": "Lobby", "route": "hub_lobby"},
        {"label": "Learning", "route": "hub_learning"},
        {"label": "Resources", "route": "hub_resources"},
        {"label": "Trusted Partners", "route": "hub_trusted"},
        {"label": "Professional", "route": "hub_professional"},
        {"label": "Tools", "route": "testing_tools"},  # Internal testing tools
        {"label": "About Us", "route": "about"},
    ]

    # Filter based on visibility config (default to visible if not specified)
    nav_items = [
        item for item in all_nav_items if nav_visibility.get(item["route"], {}).get("visible", True)
    ]

    # Build nav links HTML with UID preservation
    nav_links_html = []
    for item in nav_items:
        is_active = active_route == item["route"]
        active_class = " active" if is_active else ""
        aria_current = ' aria-current="page"' if is_active else ""
        
        # Add special class for Tools link
        special_class = " nav-link--tools" if item["route"] == "testing_tools" else ""

        href_with_uid = add_uid_to_href(f"?page={item['route']}")
        nav_links_html.append(
            f'<a href="{href_with_uid}" class="nav-link{active_class}{special_class}"{aria_current} target="_self">{item["label"]}</a>'
        )

    # Auth section - show login or user menu based on auth state
    if is_authenticated():
        user_name = get_user_name()
        # Use a unique key for the logout button
        nav_links_html.append(
            f'<span class="nav-user">👤 {user_name}</span>'
        )
    else:
        login_href = add_uid_to_href("?page=login")
        nav_links_html.append(f'<a href="{login_href}" class="nav-link nav-link--login" target="_self">Log In</a>')

    nav_html = "\n          ".join(nav_links_html)

    css = dedent(
        """
        <style>
        /* Reset Streamlit padding above header */
        .block-container {
          padding-top: 0 !important;
        }
        
        /* Header container */
        .sn-header {
          background: #ffffff;
          border-bottom: 1px solid #e6edf5;
          padding: 12px 24px;
          position: sticky;
          top: 0;
          z-index: 1000;
          margin: 0;
        }
        
        .sn-header__inner {
          max-width: 1240px;
          margin: 0 auto;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 32px;
        }
        
        /* Brand/logo section */
        .sn-header__brand {
          display: flex !important;
          align-items: center;
          gap: 0;
          text-decoration: none;
          color: var(--ink, #0f172a);
        }
        
        .sn-header__logo {
          height: 40px;
          width: auto;
          display: block;
        }
        
        .sn-header__brand-text {
          font-size: 1.25rem !important;
          font-weight: 700 !important;
          line-height: 1.2;
          color: #1e3a8a !important;
          letter-spacing: -0.01em;
          display: inline-block !important;
          visibility: visible !important;
        }
        
        /* Navigation links */
        .sn-header__nav {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }
        
        .nav-link {
          display: inline-flex;
          align-items: center;
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--ink-600, #475569);
          text-decoration: none;
          transition: all 0.15s ease;
          white-space: nowrap;
        }
        
        .nav-link:hover {
          background: rgba(37, 99, 235, 0.08);
          color: var(--brand-600, #2563eb);
        }
        
        .nav-link.active {
          background: rgba(37, 99, 235, 0.12);
          color: var(--brand-700, #1d4ed8);
          font-weight: 700;
        }
        
        .nav-link--login {
          margin-left: 8px;
          background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
          color: #ffffff !important;
          font-weight: 700;
          border: none;
        }
        
        .nav-link--login:hover {
          background: linear-gradient(90deg, #1d4ed8, #2563eb) !important;
          color: #ffffff !important;
        }
        
        /* Tools link (testing/internal) */
        .nav-link--tools {
          background: rgba(147, 51, 234, 0.08);
          color: #7c3aed;
          font-weight: 600;
        }
        
        .nav-link--tools:hover {
          background: rgba(147, 51, 234, 0.12);
          color: #6d28d9;
        }
        
        .nav-link--tools.active {
          background: rgba(147, 51, 234, 0.16);
          color: #6d28d9;
          font-weight: 700;
        }
        
        /* Authenticated user display */
        .nav-user {
          display: inline-flex;
          align-items: center;
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--ink, #0f172a);
          background: rgba(37, 99, 235, 0.08);
          white-space: nowrap;
          margin-left: 8px;
        }
        
        /* Mobile responsive */
        @media (max-width: 1024px) {
          .sn-header__inner {
            flex-direction: column;
            gap: 16px;
            align-items: flex-start;
          }
          
          .sn-header__nav {
            width: 100%;
            justify-content: flex-start;
          }
        }
        
        @media (max-width: 640px) {
          .sn-header {
            padding: 8px 16px;
          }
          
          .sn-header__brand-text {
            font-size: 1rem;
          }
          
          .nav-link {
            padding: 6px 12px;
            font-size: 0.875rem;
          }
        }
        </style>
        """
    )

    html = dedent(
        f"""
        <header class="sn-header">
          <div class="sn-header__inner">
            <a href="{add_uid_to_href("?page=welcome")}" class="sn-header__brand" target="_self" style="display: flex !important; align-items: center; gap: 12px;">
              <img src="{logo_url}" alt="CCA Logo" class="sn-header__logo" style="height: 48px !important; width: auto !important; display: block !important; visibility: visible !important; opacity: 1 !important;" />
              <span class="sn-header__brand-text" style="font-size: 1.25rem; font-weight: 700; color: #1e3a8a; display: inline-block;">Senior Navigator</span>
            </a>
            <nav class="sn-header__nav">
              {nav_html}
            </nav>
          </div>
        </header>
        """
    )

    # Render CSS first, then HTML separately (like hub pages do)
    # Add target="_self" to all links to force same-tab navigation
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)
    
    # Add logout button for authenticated users (placed in a small container)
    if is_authenticated():
        col1, col2, col3 = st.columns([10, 2, 1])
        with col2:
            if st.button("🚪 Logout", key="header_logout_btn", use_container_width=True):
                logout_user()
                st.rerun()


__all__ = ["render_header_simple", "render_back_button"]
