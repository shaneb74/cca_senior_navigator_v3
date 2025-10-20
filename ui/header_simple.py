"""Simple header component with session-safe navigation."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import streamlit as st

from core.ui import img_src


def render_header_simple(active_route: str | None = None) -> None:
    """
    Render a clean, single-line header with logo and navigation links.

    Uses Streamlit buttons with session-safe navigation (st.query_params + st.rerun)
    to prevent session state from being cleared during navigation.

    Args:
        active_route: Current page route (e.g., 'welcome', 'hub_concierge')
    """
    logo_url = img_src("static/images/logos/cca_logo.png")

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
        {"label": "Concierge", "route": "hub_concierge"},
        {"label": "Waiting Room", "route": "hub_waiting"},
        {"label": "Learning", "route": "hub_learning"},
        {"label": "Resources", "route": "hub_resources"},
        {"label": "Trusted Partners", "route": "hub_trusted"},
        {"label": "Professional", "route": "hub_professional"},
        {"label": "About Us", "route": "about"},
    ]

    # Filter based on visibility config (default to visible if not specified)
    nav_items = [
        item for item in all_nav_items if nav_visibility.get(item["route"], {}).get("visible", True)
    ]

    # Render header with Streamlit columns for session-safe navigation
    # CSS for header styling
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
        
        /* Button styling for session-safe navigation */
        .stButton > button {
          border: none;
          background: transparent;
          padding: 8px 16px;
          border-radius: 8px;
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--ink-600, #475569);
          transition: all 0.15s ease;
          white-space: nowrap;
        }
        
        .stButton > button:hover {
          background: rgba(37, 99, 235, 0.08) !important;
          color: var(--brand-600, #2563eb) !important;
          border: none !important;
        }
        
        /* Active button style */
        div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] {
          background: rgba(37, 99, 235, 0.12);
          color: var(--brand-700, #1d4ed8);
          font-weight: 700;
        }
        </style>
        """
    )

    # Render CSS
    st.markdown(css, unsafe_allow_html=True)
    
    # Render header HTML (logo and brand)
    header_html = dedent(
        f"""
        <header class="sn-header">
          <div class="sn-header__inner">
            <div class="sn-header__brand" style="display: flex !important; align-items: center; gap: 12px; margin-bottom: 8px;">
              <img src="{logo_url}" alt="CCA Logo" class="sn-header__logo" style="height: 48px !important; width: auto !important; display: block !important; visibility: visible !important; opacity: 1 !important;" />
              <span class="sn-header__brand-text" style="font-size: 1.25rem; font-weight: 700; color: #1e3a8a; display: inline-block;">Senior Navigator</span>
            </div>
          </div>
        </header>
        """
    )
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Render navigation buttons using columns for horizontal layout
    # Calculate number of columns needed (nav items + login button)
    total_buttons = len(nav_items) + 1  # +1 for login
    
    # Create columns for navigation buttons
    cols = st.columns([1] * total_buttons)
    
    # Render navigation buttons
    for idx, item in enumerate(nav_items):
        with cols[idx]:
            button_type = "secondary" if active_route == item["route"] else "primary"
            if st.button(
                item["label"],
                key=f"nav_{item['route']}",
                type=button_type,
                use_container_width=True,
            ):
                # Session-safe navigation
                st.query_params["page"] = item["route"]
                st.rerun()
    
    # Login button in last column
    with cols[-1]:
        if st.button("Log In", key="nav_login", type="primary", use_container_width=True):
            st.query_params["page"] = "login"
            st.rerun()


__all__ = ["render_header_simple"]
