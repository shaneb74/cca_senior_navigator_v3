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
from core.navi import render_navi_panel
from core.mcip import MCIP
from core.additional_services import get_additional_services
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

__all__ = ["render"]


def _get_product_state(product_key: str) -> str:
    """Determine product state based on MCIP status.
    
    Args:
        product_key: Product identifier (e.g., 'gcp_v4', 'cost_v2')
    
    Returns:
        State string: 'locked', 'available', or 'completed'
    """
    # Normalize product keys (handle aliases)
    key_map = {
        'gcp_v4': 'gcp',
        'gcp': 'gcp',
        'cost_v2': 'cost_planner',
        'cost_planner': 'cost_planner',
        'cost_intro': 'cost_planner',
        'pfma_v3': 'pfma',
        'pfma': 'pfma',
        'faq': 'faq',
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
    
    Args:
        tile: Original ProductTileHub object
        state: State to apply ('locked', 'available', 'completed')
    
    Returns:
        Modified tile with state-specific properties
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
    """Render the Lobby Hub with NAVI guidance, MCIP gating, and Additional Services.
    
    Phase 3A Features:
    - NAVI panel at top for journey guidance
    - MCIP-based product availability gating
    - Product state indicators (locked/available/completed)
    - Additional Services section at bottom
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
    # NAVI GUIDANCE PANEL (Phase 3A)
    # ========================================
    # Render NAVI at the top to guide user through journey
    render_navi_panel(
        location="hub",
        hub_key="lobby",
        product_key=None,
        module_config=None
    )
    
    # Add spacing after NAVI panel
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # ========================================
    # PAGE TITLE & SUBTITLE
    # ========================================
    st.title("Senior Navigator Dashboard")
    st.markdown("Choose a tool to get started with your care planning journey.")
    
    # ========================================
    # PRODUCT TILES WITH MCIP GATING (Phase 3A)
    # ========================================
    # Get product tiles with state applied
    cards = _build_product_tiles()
    
    # Render dashboard body with dynamic tiles
    body_html = render_dashboard_body(
        title=None,  # Already rendered above
        subtitle=None,
        chips=None,
        hub_guide_block=None,
        hub_order=None,
        cards=cards,
        additional_services=None,  # Will render separately below
    )
    
    st.markdown(body_html, unsafe_allow_html=True)
    
    # ========================================
    # ADDITIONAL SERVICES SECTION (Phase 3A)
    # ========================================
    # Port from Concierge hub - render at bottom
    additional_services = get_additional_services("lobby")
    
    if additional_services:
        st.markdown("---")  # Visual separator
        st.markdown("### Explore More Services")
        st.markdown(
            "Additional resources to support your care planning journey.",
            help="These services can help with specific aspects of care coordination."
        )
        
        # Render additional services in dashboard grid
        st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
        
        for service in additional_services:
            # Build service card HTML
            title = service.get('title', 'Service')
            desc = service.get('desc', '')
            route = service.get('route', '#')
            icon = service.get('icon', '🔧')
            
            card_html = f"""
            <div class="dashboard-card">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <h3 style="margin-bottom: 0.5rem;">{title}</h3>
                <p class="subtext" style="margin-bottom: 1rem;">{desc}</p>
                <a href="?page={route}" class="btn-pill" style="text-decoration: none; display: inline-block;">
                    Open
                </a>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================
    # FOOTER
    # ========================================
    render_footer_simple()
