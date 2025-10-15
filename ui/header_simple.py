"""Simple header component - no layout.py, no session state manipulation."""
from __future__ import annotations

from textwrap import dedent
from typing import Optional

import streamlit as st

from core.ui import img_src


def render_header_simple(active_route: Optional[str] = None) -> None:
    """
    Render a clean, single-line header with logo and navigation links.
    
    Uses plain <a href="?page=X"> links for instant navigation without reruns.
    No session state writes, no st.button() complexity.
    
    Args:
        active_route: Current page route (e.g., 'welcome', 'hub_concierge')
    """
    logo_url = img_src("static/images/logos/cca_logo.png")
    
    # Define navigation items (use exact keys from nav.json)
    nav_items = [
        {"label": "Welcome", "route": "welcome"},
        {"label": "Concierge", "route": "hub_concierge"},
        {"label": "Waiting Room", "route": "hub_waiting"},
        {"label": "Learning", "route": "hub_learning"},
        {"label": "Trusted Partners", "route": "hub_trusted"},
        {"label": "Professional", "route": "hub_professional"},
        {"label": "About Us", "route": "about"},
    ]
    
    # Build nav links HTML
    nav_links_html = []
    for item in nav_items:
        is_active = active_route == item["route"]
        active_class = " active" if is_active else ""
        aria_current = ' aria-current="page"' if is_active else ""
        
        nav_links_html.append(
            f'<a href="?page={item["route"]}" class="nav-link{active_class}"{aria_current}>{item["label"]}</a>'
        )
    
    # Login link (always shown for now)
    nav_links_html.append('<a href="?page=login" class="nav-link nav-link--login">Log In</a>')
    
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
            <a href="?page=welcome" class="sn-header__brand" style="display: flex !important; align-items: center; gap: 12px;">
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
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)


__all__ = ["render_header_simple"]
