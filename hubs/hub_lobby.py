# hubs/hub_lobby.py
"""
Lobby Hub - Unified Dashboard Entry Point

Phase 4A: Consolidated Waiting Room and Lobby into single adaptive hub.
Manages the entire user journey lifecycle: Discovery → Planning → Post-Planning.

Phase 5E: Dynamic Personalization integration.
Personalized navigation, tone, and visible modules based on user tier, cognition, and phase.

Architecture:
--------------
- Dynamic product tile rendering via ProductTileHub objects
- MCIP-based journey phase detection and product gating
- Organized tile categories: Discovery, Planning, Engagement, Additional Services, Completed
- NAVI-integrated FAQ (no longer a tile)
- Phase 5E: Schema-driven personalization via core.personalizer

Phase History:
--------------
Phase 3A: NAVI integration, MCIP gating, Additional Services
Phase 3B: Personalized NAVI, product outcomes, FAQ always unlocked
Phase 4A: Waiting Room consolidation, completed journeys, FAQ→NAVI integration
Phase 5D: Journey alignment, navigation fixes, 4-section structure
Phase 5E: Dynamic personalization engine integration
"""

import os
import streamlit as st
from core.product_tile import ProductTileHub
from core.base_hub import render_dashboard_body
from core.ui import render_navi_panel_v2
from core.mcip import MCIP
from core.additional_services import get_additional_services
from core.product_outcomes import get_product_outcome
from core.journeys import get_journey_phase
from core.personalizer import get_user_context, get_visible_modules
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

__all__ = ["render"]


# ==============================================================================
# HELPER FUNCTIONS FROM WAITING ROOM
# ==============================================================================

def _dev_unlock_tiles() -> bool:
    """Check if dev unlock mode is enabled for tile gating.
    
    Returns:
        True if DEV_UNLOCK_TILES env var or session state flag is set
    """
    if st.session_state.get("_DEV_UNLOCK_TILES") is True:
        return True
    if os.getenv("DEV_UNLOCK_TILES", "0") in ("1", "true", "True", "YES", "yes"):
        return True
    return False


def _is_gcp_complete() -> bool:
    """Check if Guided Care Plan is complete.
    
    Returns:
        True if GCP summary_ready flag is set (canonical or legacy)
    """
    ss = st.session_state
    g = ss.get("gcp", {})
    # Canonical: set at Daily Living → Continue
    if g.get("summary_ready"):
        return True
    # Legacy/alias support
    if ss.get("summary_ready") or ss.get("_summary_ready"):
        return True
    # Fallback: legacy outcomes imply a computed recommendation
    if ss.get("gcp.final_tier") or ss.get("gcp_care_recommendation", {}).get("_outcomes", {}).get("tier"):
        return True
    return False


def _is_cost_planner_complete() -> bool:
    """Check if Cost Planner is complete.
    
    Returns:
        True if cost completed flag or totals exist in state
    """
    ss = st.session_state
    cost = ss.get("cost", {})
    # Preferred explicit flag (we set this in step 3)
    if cost.get("completed"):
        return True
    # Practical fallbacks that reflect "the user has results"
    if ss.get("_qe_totals"):      # quick estimate totals cache
        return True
    if cost.get("last_totals"):   # any persisted totals snapshot
        return True
    return False


def _get_trivia_badges():
    """Get list of earned trivia badges for tile display.

    Reads from persisted product_tiles_v2 structure.

    Returns:
        List of badge strings to show on tile
    """
    tiles = st.session_state.get("product_tiles_v2", {})
    progress = tiles.get("senior_trivia_hub", {})
    badges_earned = progress.get("badges_earned", {})

    if not badges_earned:
        return ["new"]  # Show 'new' badge if no games played yet

    # Extract badge names (without stars)
    badge_list = []
    for module_key, badge_info in badges_earned.items():
        badge_name = badge_info.get("name", "")
        # Clean up badge name (remove star emojis)
        clean_name = (
            badge_name.replace(" ⭐⭐⭐⭐", "")
            .replace(" ⭐⭐⭐", "")
            .replace(" ⭐⭐", "")
            .replace(" ⭐", "")
        )
        if clean_name:
            badge_list.append(clean_name)

    # Limit to 3 badges on tile (most recent)
    return badge_list[:3] if badge_list else ["new"]


def _get_trivia_progress():
    """Calculate trivia progress as percentage of quizzes completed.

    Returns:
        Progress percentage (0-100)
    """
    tiles = st.session_state.get("product_tiles_v2", {})
    progress = tiles.get("senior_trivia_hub", {})
    badges_earned = progress.get("badges_earned", {})

    # Total available quizzes
    total_quizzes = 5  # truths_myths, music_trivia, medicare_quiz, healthy_habits, community_challenge

    if not badges_earned:
        return 0

    completed_count = len(badges_earned)
    return int((completed_count / total_quizzes) * 100)


def _get_product_state(product_key: str) -> str:
    """Determine product state based on MCIP status.
    
    Phase 4A: FAQ removed from tiles (integrated into NAVI).
    
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


# ==============================================================================
# TILE BUILDERS - DISCOVERY JOURNEY
# ==============================================================================

def _build_discovery_tiles() -> list[ProductTileHub]:
    """Build Discovery Journey tiles (first-time user experience).
    
    Phase 4A Revision: Discovery tiles are GCP-focused.
    Phase 5A: Added Discovery Learning first-touch onboarding tile.
    
    Returns:
        List of discovery tiles with MCIP state applied
    """
    tiles = [
        ProductTileHub(
            key="discovery_learning",
            title="Start Your Discovery Journey",
            desc="Welcome! Let NAVI introduce you to the care planning process.",
            blurb="First-time here? Learn what to expect and how we'll guide you step-by-step.",
            image_square="gcp.png",  # TODO: Get dedicated image
            primary_route="?page=discovery_learning",
            primary_label="Start Here",
            variant="brand",
            order=5,  # Before GCP (10)
            visible=True,
            phase="discovery",  # Phase 5A: journey phase tag
        ),
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
            phase="discovery",  # Phase 5A: journey phase tag
        ),
    ]
    
    # Apply MCIP state to each tile
    tiles_with_state = []
    for tile in tiles:
        state = _get_product_state(tile.key)
        tile_with_state = _apply_tile_state(tile, state)
        tiles_with_state.append(tile_with_state)
    
    return tiles_with_state


# ==============================================================================
# TILE BUILDERS - PLANNING TOOLS
# ==============================================================================

def _build_planning_tiles() -> list[ProductTileHub]:
    """Build Planning Tools tiles (unlocked after GCP).
    
    Phase 4A Revision: Planning tiles include Cost Planner and Plan With Advisor.
    Phase 4B: Added Learn About My Recommendation between GCP and Cost Planner.
    Phase 5A: Added journey phase tags to all planning tiles.
    FAQ removed (integrated into NAVI).
    
    Returns:
        List of planning tiles with MCIP state applied
    """
    tiles = [
        ProductTileHub(
            key="learn_recommendation",
            title="Learn About My Recommendation",
            desc="Understand your care option before planning costs.",
            blurb="Educational step to learn what your recommendation means and how to prepare.",
            image_square="gcp.png",  # TODO: Get dedicated image
            primary_route="?page=learn_recommendation",
            primary_label="Learn More",
            variant="brand",
            order=15,  # Between GCP (10) and Cost Planner (20)
            visible=True,
            phase="planning",  # Phase 5A: journey phase tag
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
            phase="planning",  # Phase 5A: journey phase tag
        ),
        ProductTileHub(
            key="pfma_v3",
            title="My Advisor",
            desc="Schedule and prepare for your next advisor meeting.",
            blurb="Get matched with the right advisor to coordinate care, benefits, and trusted partners.",
            image_square="pfma.png",
            primary_route="?page=pfma_v3",
            primary_label="Open",
            variant="brand",
            order=30,
            visible=True,
            phase="planning",  # Phase 5A: journey phase tag
        ),
    ]
    
    # Apply MCIP state to each tile
    tiles_with_state = []
    for tile in tiles:
        state = _get_product_state(tile.key)
        tile_with_state = _apply_tile_state(tile, state)
        tiles_with_state.append(tile_with_state)
    
    return tiles_with_state


# ==============================================================================
# TILE BUILDERS - ENGAGEMENT PRODUCTS
# ==============================================================================

# Phase 5D: Advisor Prep retired entirely (no longer shown)
# def _build_advisor_prep_tile() -> ProductTileHub | None:
#     """Build Advisor Prep tile if PFMA booking exists."""
#     # Function commented out - Advisor Prep is retired in Phase 5D
#     pass


def _build_trivia_tile() -> ProductTileHub:
    """Build Senior Trivia tile.
    
    Phase 4A Revision: Core engagement product (not additional service).
    Phase 5A: Added journey phase tag.
    
    Returns:
        ProductTileHub
    """
    trivia_badges = _get_trivia_badges()
    trivia_progress = _get_trivia_progress()

    return ProductTileHub(
        key="senior_trivia",
        title="Senior Trivia & Brain Games",
        desc="Test your knowledge with fun, educational trivia",
        blurb="Play solo or with family! Topics include senior living myths, music nostalgia, Medicare, healthy habits, and family fun.",
        primary_label="Play Trivia",
        primary_go="senior_trivia",
        progress=trivia_progress,
        badges=trivia_badges,
        variant="teal",
        order=110,
        phase="post_planning",  # Phase 5A: journey phase tag
    )


def _build_clinical_review_tile() -> ProductTileHub:
    """Build Concierge Clinical Review tile.
    
    Phase 4A Revision: Core engagement product (not additional service).
    Phase 5A: Added journey phase tag.
    
    Returns:
        ProductTileHub (visible but locked until GCP & CP complete)
    """
    _gcp_done = _is_gcp_complete()
    _cp_done = _is_cost_planner_complete()
    
    _ccr_locked = not (_gcp_done and _cp_done)
    if _dev_unlock_tiles():
        _ccr_locked = False

    return ProductTileHub(
        key="concierge_clinical_review",
        title="Concierge Clinical Review",
        desc="Review your plan with your doctor or a clinical specialist",
        blurb="Providers use both your care and financial info to give precise guidance.",
        primary_label="Start Clinical Review" if not _ccr_locked else "Complete Required Steps",
        primary_route="?page=ccr_overview" if not _ccr_locked else "?page=gcp_v4",
        primary_go="ccr_overview" if not _ccr_locked else "gcp_v4",
        badges=["new"] if not _ccr_locked else None,
        variant="purple",
        order=120,
        locked=_ccr_locked,
        lock_msg="Unlocks after Guided Care Plan and Cost Planner. Providers use both your care and financial info to give precise guidance." if _ccr_locked else None,
        phase="post_planning",  # Phase 5A: journey phase tag
    )


def _build_engagement_tiles() -> list[ProductTileHub]:
    """Build Engagement Product tiles.
    
    Phase 4A Revision: Trivia and CCR are core products (not additional services).
    Phase 5D: Removed Advisor Prep (retired entirely).
    
    Returns:
        List of engagement tiles (Trivia, CCR)
    """
    tiles = []
    
    # Trivia (always available)
    tiles.append(_build_trivia_tile())
    
    # Clinical Review (visible but may be locked)
    tiles.append(_build_clinical_review_tile())
    
    return tiles


# ==============================================================================
# TILE BUILDERS - COMPLETED JOURNEYS
# ==============================================================================

def _build_completed_tiles() -> list[ProductTileHub]:
    """Build tiles for completed journeys.
    
    Phase 4A: New section for closed-out products.
    Phase 5D: Updated to use "My Advisor" name.
    
    Returns:
        List of completed product tiles
    """
    completed = []
    
    # Check each major product for completion
    all_products = [
        ("gcp_v4", "Guided Care Plan", "Your personalized care recommendation"),
        ("cost_v2", "Cost Planner", "Your financial plan and projections"),
        ("pfma_v3", "My Advisor", "Your advisor consultation"),
    ]
    
    for key, title, desc in all_products:
        if _get_product_state(key) == "completed":
            tile = ProductTileHub(
                key=key,
                title=title,
                desc=desc,
                primary_label="View Summary",
                primary_route=f"?page={key}",
                variant="success",
                order=900,  # Low priority (at bottom)
                visible=True,
            )
            # Add outcome if available
            outcome = get_product_outcome(key)
            if outcome:
                tile.desc = outcome
            completed.append(tile)
    
    return completed


# ==============================================================================
# MAIN RENDER FUNCTION
# ==============================================================================

def render(ctx=None) -> None:
    """Render the Lobby Hub - Unified adaptive hub for all journey phases.
    
    Phase 4A Features:
    - Consolidated Waiting Room functionality
    - Organized tile categories: Discovery → Planning → Engagement → Completed
    - FAQ integrated into NAVI (no longer a tile)
    - Completed Journeys section (collapsible)
    - Additional Services for partner upsells only
    
    Phase 5D Features:
    - Retired Advisor Prep entirely (no replacement)
    - Renamed "Plan With My Advisor" → "My Advisor"
    - 4-section structure: NAVI Header → Active Journey → Additional Services → My Completed Journey
    - Completed Journey section appears BELOW Additional Services
    - All navigation routes to hub_lobby (not hub_concierge)
    
    Architecture:
    - Hubs → Product Tiles → Modules → Assets
    - NAVI provides journey context and FAQ access
    - MCIP-based product gating throughout
    """
    
    # Initialize MCIP to ensure journey state is ready
    MCIP.initialize()
    
    # Phase 5E: Get personalization context
    user_ctx = get_user_context()
    visible_modules = get_visible_modules()
    
    # Load dashboard CSS
    st.markdown(
        f"<style>{open('core/styles/dashboard.css').read()}</style>",
        unsafe_allow_html=True
    )
    
    # Render header
    render_header_simple(active_route="hub_lobby")
    
    # ========================================
    # NAVI GUIDANCE PANEL (Phase 3B - Personalized, Phase 5E - Dynamic)
    # ========================================
    # Build personalized NAVI data
    person_name = st.session_state.get("person_name", "").strip()
    
    # Phase 5E: Use personalized header message
    navi_header_message = user_ctx.get("navi_header_message", "Continue your personalized journey.")
    
    # Phase 5E: Use personalized header message
    navi_header_message = user_ctx.get("navi_header_message", "Continue your personalized journey.")
    header_text = user_ctx.get("header_text", "")
    
    # Determine title and reason based on MCIP state and personalization
    care_rec = MCIP.get_care_recommendation()
    if care_rec and care_rec.tier:
        title = f"Hi, {person_name}!" if person_name else navi_header_message
        tier_display = care_rec.tier.replace("_", " ").title()
        reason = header_text or f"Your personalized care plan recommends: {tier_display}"
    else:
        title = "Let's get started."
        reason = header_text or "Answer a few questions to build your personalized care plan."
    
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
        primary_action = {"label": "Explore Resources", "route": "hub_lobby"}
    
    # Secondary action - FAQ integrated into NAVI (Phase 4A)
    secondary_action = {"label": "Ask NAVI", "route": "faq"}
    
    # Phase 5A.1: Apply phase-aware context before rendering NAVI
    from apps.navi_core.context_manager import apply_phase_context
    apply_phase_context()
    
    # Phase 5A.1: Journey progress bar (temporary UI for testing)
    from core.journeys import get_phase_completion
    journey_stage = st.session_state.get("journey_stage", "discovery")
    completion = get_phase_completion(journey_stage)
    st.caption(f"**{journey_stage.replace('_', ' ').title()} Phase Progress**")
    st.progress(completion)
    st.markdown("<br/>", unsafe_allow_html=True)
    
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
    
    # Phase 5A.1: Optional debug caption for testing tone context
    if os.getenv("SN_DEBUG_PHASE_TONE", "0") == "1":
        st.caption(
            f"🧪 Phase: {st.session_state.get('journey_stage', 'N/A')} | "
            f"Tone: {st.session_state.get('navi_tone', 'N/A')}"
        )
    
    # Add spacing after NAVI panel
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # ========================================
    # PRODUCT TILES - ORGANIZED BY CATEGORY (Phase 4A, Phase 5E - Filtered)
    # ========================================
    
    # --- Discovery Journey ---
    discovery_tiles = _build_discovery_tiles()
    
    # --- Planning Tools ---
    planning_tiles = _build_planning_tiles()
    
    # --- Engagement Products ---
    engagement_tiles = _build_engagement_tiles()
    
    # Combine active tiles
    active_tiles = discovery_tiles + planning_tiles + engagement_tiles
    
    # Phase 5E: Filter tiles by visible modules from personalization
    if visible_modules:
        active_tiles = [t for t in active_tiles if t.key in visible_modules or t.key.startswith("discovery_")]
    
    # Sort by order
    active_tiles.sort(key=lambda t: t.order)
    
    # ========================================
    # ADDITIONAL SERVICES (Phase 4A Revision)
    # ========================================
    # Only partner upsells and NAVI-driven recommendations
    additional_services = get_additional_services("lobby")
    
    # ========================================
    # COMPLETED JOURNEYS SECTION (Phase 4A)
    # ========================================
    completed_tiles = _build_completed_tiles()
    
    # Render main hub body with active tiles and additional services
    body_html = render_dashboard_body(
        title="",  # NAVI provides context
        subtitle=None,
        chips=None,
        hub_guide_block=None,
        hub_order=None,
        cards=active_tiles,
        additional_services=additional_services,
    )
    
    st.markdown(body_html, unsafe_allow_html=True)
    
    # ========================================
    # ⭐ MY COMPLETED JOURNEY (Phase 5D)
    # ========================================
    # Appears BELOW Additional Services as separate section
    if completed_tiles:
        st.markdown('<div class="completed-journey-section">', unsafe_allow_html=True)
        st.markdown(
            '<div class="completed-journey-header">⭐ My Completed Journey</div>',
            unsafe_allow_html=True
        )
        
        # Render completed tiles with dimmed styling
        cols = st.columns(min(len(completed_tiles), 3))
        for idx, tile in enumerate(completed_tiles):
            col = cols[idx % len(cols)]
            with col:
                st.markdown('<div class="dashboard-card completed-card">', unsafe_allow_html=True)
                st.markdown('<div class="completed-overlay">✓</div>', unsafe_allow_html=True)
                st.markdown(f"### {tile.title}")
                st.markdown(f"{tile.desc}")
                st.markdown(
                    '<span class="completed-badge">✓ Completed</span>',
                    unsafe_allow_html=True
                )
                if st.button("Review Again", key=f"review_{tile.key}", use_container_width=True):
                    st.query_params["page"] = tile.key
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================
    # FOOTER
    # ========================================
    render_footer_simple()
