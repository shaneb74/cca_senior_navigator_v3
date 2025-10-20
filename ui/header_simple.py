"""Simple header component - no layout.py, no session state manipulation."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import streamlit as st

from core.ui import img_src
from core.url_helpers import add_uid_to_href


def render_header_simple(active_route: str | None = None) -> None:
    """
    Render a clean, single-line header with logo and navigation links.

    Uses plain <a href="?page=X"> links for instant navigation without reruns.
    No session state writes, no st.button() complexity.

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

    # Build nav links HTML - use onclick for session-safe navigation
    nav_links_html = []
    for item in nav_items:
        is_active = active_route == item["route"]
        active_class = " active" if is_active else ""
        aria_current = ' aria-current="page"' if is_active else ""

        # Use data attribute and onclick instead of href for session-safe navigation
        nav_links_html.append(
            f'<a href="#" class="nav-link{active_class}"{aria_current} data-route="{item["route"]}" onclick="return false;">{item["label"]}</a>'
        )

    # Login link (always shown for now)
    nav_links_html.append(f'<a href="#" class="nav-link nav-link--login" data-route="login" onclick="return false;">Log In</a>')

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
            <a href="#" class="sn-header__brand" data-route="welcome" onclick="return false;" style="display: flex !important; align-items: center; gap: 12px;">
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
    
    # Add JavaScript to handle navigation by updating URL query params
    # This triggers Streamlit's query params change detection
    nav_script = """
    <script>
    (function() {
      function wireUpNavigation() {
        // Get all nav links
        const navLinks = document.querySelectorAll('.nav-link, .sn-header__brand');
        
        navLinks.forEach(link => {
          link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const route = this.getAttribute('data-route');
            if (!route) return;
            
            // Update URL query params directly (triggers Streamlit rerun)
            const url = new URL(window.location.href);
            url.searchParams.set('page', route);
            
            // Use history.replaceState to avoid pushState rate limiting
            window.history.replaceState({}, '', url);
            
            // Trigger Streamlit to detect the query param change
            window.parent.postMessage({
              type: 'streamlit:setQueryParams',
              queryParams: { page: route }
            }, '*');
            
            return false;
          });
        });
      }
      
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', wireUpNavigation);
      } else {
        wireUpNavigation();
      }
    })();
    </script>
    """
    
    st.markdown(nav_script, unsafe_allow_html=True)


__all__ = ["render_header_simple"]
