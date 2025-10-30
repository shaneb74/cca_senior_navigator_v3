# hubs/hub_lobby.py
"""
Lobby Hub - Visual Dashboard Entry Point

Modernized dashboard design matching Senior Navigator design system.
Provides entry point to core products: GCP, Cost Planner, PFMA, and FAQ.

Architecture Note (Phase 2B):
--------------
This hub uses dynamic product tile rendering via ProductTileHub objects.
Products are registered in config/nav.json and loaded via the module engine.

The Senior Navigator architecture already supports:
  - Dynamic module discovery (core/modules/engine.py::run_module)
  - JSON-driven module configs (products/*/modules/*/config.py)
  - Dynamic product tiles (ProductTileHub with routes)

No hard-coded imports or manual module registration required.
"""

import streamlit as st
from core.product_tile import ProductTileHub
from core.base_hub import render_dashboard_body
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

__all__ = ["render"]


def _build_product_tiles() -> list[ProductTileHub]:
    """Build product tiles for Lobby hub."""
    tiles = [
        ProductTileHub(
            key="gcp_v4",
            title="Guided Care Plan",
            desc="Explore and compare care options.",
            blurb="Answer a few short questions about your daily needs, health, and safety.",
            image_square="gcp.png",
            primary_route="?page=gcp_v4",
            primary_label="Start",
            variant="brand",
            order=10,
            visible=True,
        ),
        ProductTileHub(
            key="cost_v2",
            title="Cost Planner",
            desc="Estimate and plan financial coverage.",
            blurb="Project expenses, compare living options, and see how long current funds will last.",
            image_square="cp.png",
            primary_route="?page=cost_intro",
            primary_label="Start",
            variant="brand",
            order=20,
            visible=True,
        ),
        ProductTileHub(
            key="pfma_v3",
            title="Plan With My Advisor",
            desc="Schedule and prepare for your next advisor meeting.",
            blurb="Get matched with the right advisor to coordinate care, benefits, and trusted partners.",
            image_square="pfma.png",
            primary_route="?page=pfma_v3",
            primary_label="Open",
            variant="brand",
            order=30,
            visible=True,
        ),
        ProductTileHub(
            key="faq",
            title="FAQs & Answers",
            desc="Instant help from NAVI AI.",
            blurb="Search our advisor-reviewed knowledge base or ask Senior Navigator AI for tailored guidance.",
            image_square="faq.png",
            primary_route="?page=faq",
            primary_label="Open",
            variant="teal",
            order=40,
            visible=True,
        ),
    ]
    return tiles


def render(ctx=None) -> None:
    """Render the Lobby Hub with modernized dashboard styling."""
    
    # Load dashboard CSS
    st.markdown(
        f"<style>{open('core/styles/dashboard.css').read()}</style>",
        unsafe_allow_html=True
    )
    
    # Render header
    render_header_simple(active_route="hub_lobby")
    
    # Page title
    st.title("Senior Navigator Dashboard")
    st.markdown("Choose a tool to get started with your care planning journey.")
    
    # Get product tiles
    cards = _build_product_tiles()
    
    # Render dashboard body with dynamic tiles
    body_html = render_dashboard_body(
        title=None,  # Already rendered above
        subtitle=None,
        chips=None,
        hub_guide_block=None,
        hub_order=None,
        cards=cards,
        additional_services=None,
    )
    
    st.markdown(body_html, unsafe_allow_html=True)
    
    # Render footer
    render_footer_simple()
