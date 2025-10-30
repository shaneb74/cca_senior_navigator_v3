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

Phase 3A Enhancements:
--------------
  - NAVI guidance and progress tracking at top
  - MCIP-based product gating (unlocked products only)
  - Product state management (locked/available/completed)
  - Additional Services section from Concierge hub
"""

import streamlit as st
from core.product_tile import ProductTileHub
from core.base_hub import render_dashboard_body
from core.ui import render_navi_panel_v2
from core.mcip import MCIP
from core.additional_services import get_additional_services
from core.product_outcomes import get_product_outcome
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

__all__ = ["render"]


def _get_product_state(product_key: str) -> str:
    """Determine product state based on MCIP status.
    
    Phase 3B: FAQ/AI Advisor is always available.
    
    Args:
        product_key: Product identifier (e.g., 'gcp_v4', 'cost_v2')
    
    Returns:
        State string: 'locked', 'available', or 'completed'
    """
    # FAQ/AI Advisor is always unlocked (Phase 3B)
    if product_key in ('faq', 'ai_advisor'):
        return "available"
    
    # Normalize product keys (handle aliases)
    key_map = {
        'gcp_v4': 'gcp',
        'gcp': 'gcp',
        'cost_v2': 'cost_planner',
        'cost_planner': 'cost_planner',
        'cost_intro': 'cost_planner',
        'pfma_v3': 'pfma',
        'pfma': 'pfma',
    }
    
    normalized_key = key_map.get(product_key, product_key)
    
    # Check if product is completed
    if MCIP.is_product_complete(normalized_key):
        return "completed"
    
    # Check if product is unlocked (available)
    if MCIP.is_product_unlocked(normalized_key):
        return "available"
    
    # Otherwise it's locked
    return "locked"


def _apply_tile_state(tile: ProductTileHub, state: str) -> ProductTileHub:
    """Apply visual state to a product tile.
    
    Phase 3B: Also adds product outcomes to completed tiles.
    
    Args:
        tile: Original ProductTileHub object
        state: State to apply ('locked', 'available', 'completed')
    
    Returns:
        Modified tile with state-specific properties and outcomes
    """
    if state == "locked":
        # Grey out tile and disable interaction
        tile.visible = True  # Show the tile
        tile.primary_label = "🔒 Locked"
        tile.desc = "Complete previous steps to unlock"
        
    elif state == "completed":
        # Show completion indicator
        tile.primary_label = "✓ Completed"
        tile.variant = "success"  # Use success variant if available
        
        # Add outcome display for completed products (Phase 3B)
        outcome = get_product_outcome(tile.key)
        if outcome:
            # Show outcome as prominent subtitle
            tile.desc = outcome
    
    # 'available' state keeps original tile properties
    return tile


def _build_product_tiles() -> list[ProductTileHub]:
    """Build product tiles for Lobby hub with MCIP-based state management.
    
    Returns:
        List of ProductTileHub objects with states applied
    """
    # Define all available tiles
    all_tiles = [
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
    
    # Apply state to each tile based on MCIP status
    tiles_with_state = []
    for tile in all_tiles:
        state = _get_product_state(tile.key)
        tile_with_state = _apply_tile_state(tile, state)
        tiles_with_state.append(tile_with_state)
    
    return tiles_with_state


def render(ctx=None) -> None:
    """Render the Lobby Hub - Central control center for Senior Navigator.
    
    Phase 3A Features:
    - NAVI panel at top for journey guidance
    - MCIP-based product availability gating
    - Product state indicators (locked/available/completed)
    - Additional Services section at bottom
    
    Phase 3B Enhancements:
    - Personalized NAVI with render_navi_panel_v2()
    - Removed redundant "Dashboard" title (NAVI provides context)
    - Product outcomes display on completed tiles
    - FAQ/AI Advisor always unlocked
    - Lobby is now the default hub (replaces Concierge)
    """
    
    # Initialize MCIP to ensure journey state is ready
    MCIP.initialize()
    
    # Load dashboard CSS
    st.markdown(
        f"<style>{open('core/styles/dashboard.css').read()}</style>",
        unsafe_allow_html=True
    )
    
    # Render header
    render_header_simple(active_route="hub_lobby")
    
    # ========================================
    # NAVI GUIDANCE PANEL (Phase 3B - Personalized)
    # ========================================
    # Build personalized NAVI data
    person_name = st.session_state.get("person_name", "").strip()
    person = person_name if person_name else "you"
    
    # Determine title and reason based on MCIP state
    care_rec = MCIP.get_care_recommendation()
    if care_rec and care_rec.tier:
        title = f"Hi, {person_name}!" if person_name else "Welcome back!"
        tier_display = care_rec.tier.replace("_", " ").title()
        reason = f"Your personalized care plan recommends: {tier_display}"
    else:
        title = "Let's get started."
        reason = "Answer a few questions to build your personalized care plan."
    
    encouragement = {
        "icon": "🧭",
        "text": "I'll guide you through each step with context and next actions.",
        "status": "getting_started",
    }
    
    # Context chips (empty for now, can be populated with progress)
    context_chips = []
    
    # Primary action - determine based on what's not completed
    if not MCIP.is_product_complete("gcp"):
        primary_action = {"label": "Start Care Plan", "route": "gcp_v4"}
    elif not MCIP.is_product_complete("cost_planner"):
        primary_action = {"label": "Calculate Care Costs", "route": "cost_intro"}
    else:
        primary_action = {"label": "Ask NAVI", "route": "faq"}
    
    # Secondary action - FAQ is always available
    secondary_action = {"label": "Get Help from NAVI", "route": "faq"}
    
    # Render personalized NAVI panel V2
    render_navi_panel_v2(
        title=title,
        reason=reason,
        encouragement=encouragement,
        context_chips=context_chips,
        primary_action=primary_action,
        secondary_action=secondary_action,
        progress=None,
        alert_html="",
        variant="hub",
    )
    
    # Add spacing after NAVI panel
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # ========================================
    # PAGE TITLE & SUBTITLE (Phase 3B: Removed - NAVI provides context)
    # ========================================
    # st.title("Senior Navigator Dashboard")
    # st.markdown("Choose a tool to get started with your care planning journey.")
    
    # ========================================
    # PRODUCT TILES WITH MCIP GATING (Phase 3A)
    # ========================================
    # Get product tiles with state applied
    cards = _build_product_tiles()
    
    # ========================================
    # ADDITIONAL SERVICES SECTION (Phase 3A)
    # ========================================
    # Get additional services from Concierge hub configuration
    additional_services = get_additional_services("concierge")
    
    # Render dashboard body with dynamic tiles and additional services
    body_html = render_dashboard_body(
        title=None,  # Already rendered above
        subtitle=None,
        chips=None,
        hub_guide_block=None,
        hub_order=None,
        cards=cards,
        additional_services=additional_services,  # Let render_dashboard_body handle rendering
    )
    
    st.markdown(body_html, unsafe_allow_html=True)
    
    # ========================================
    # FOOTER
    # ========================================
    render_footer_simple()
