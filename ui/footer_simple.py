"""Simple footer component - minimal copyright and version."""

from __future__ import annotations

from textwrap import dedent

import streamlit as st


def render_footer_simple(version: str = "3.2.1") -> None:
    """
    Render a minimal footer with copyright and version.

    No excessive padding, just a clean single line.

    Args:
        version: App version string (default: "3.2.1")
    """
    css = dedent(
        """
        <style>
        /* Reset Streamlit padding below footer */
        .block-container {
          padding-bottom: 0 !important;
        }
        
        /* Footer container */
        .sn-footer {
          background: #ffffff;
          border-top: 1px solid #e6edf5;
          padding: 16px 24px;
          margin-top: 80px;
        }
        
        .sn-footer__inner {
          max-width: 1240px;
          margin: 0 auto;
          text-align: center;
        }
        
        .sn-footer__text {
          font-size: 0.875rem;
          font-weight: 400;
          color: #64748b;
          margin: 0;
        }
        
        .sn-footer__text a {
          color: #64748b;
          text-decoration: none;
          font-weight: 500;
        }
        
        .sn-footer__text a:hover {
          color: #475569;
        }
        
        /* Mobile responsive */
        @media (max-width: 640px) {
          .sn-footer {
            padding: 12px 16px;
          }
          
          .sn-footer__text {
            font-size: 0.8125rem;
          }
        }
        </style>
        """
    )

    html = dedent(
        f"""
        <footer class="sn-footer">
          <div class="sn-footer__inner">
            <p class="sn-footer__text">
              © 2025 Concierge Care Advisors, Inc. | Senior Navigator™ | Patent Pending  •  v{version}
            </p>
          </div>
        </footer>
        """
    )

    st.markdown(css + html, unsafe_allow_html=True)


__all__ = ["render_footer_simple"]
