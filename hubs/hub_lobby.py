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
from components.empty_state import render_empty_state

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


def _build_active_journeys(user_ctx: dict) -> list:
    """Filter user journeys to only active (not completed) ones.
    
    Phase Post-CSS: Separates active and completed journeys for proper rendering.
    
    Args:
        user_ctx: User context dictionary
    
    Returns:
        List of active journey data dictionaries
    """
    return [
        j for j in user_ctx.get("journeys", {}).values()
        if not j.get("completed")
    ]


def _build_completed_journeys(user_ctx: dict) -> list:
    """Filter user journeys to only completed ones.
    
    Phase Post-CSS: Separates active and completed journeys for proper rendering.
    
    Args:
        user_ctx: User context dictionary
    
    Returns:
        List of completed journey data dictionaries
    """
    return [
        j for j in user_ctx.get("journeys", {}).values()
        if j.get("completed")
    ]


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
    Phase Journey Fix: Delegate normalization to MCIP for single source of truth.
    
    Args:
        product_key: Product identifier (e.g., 'gcp_v4', 'cost_v2')
    
    Returns:
        State string: 'locked', 'available', or 'completed'
    """
    # Delegate normalization to MCIP (single source of truth)
    # MCIP handles all key aliases: gcp_v4→gcp, cost_v2→cost_planner, etc.
    normalized_key = MCIP._normalize_product_key(product_key)
    
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
    Phase 5K: Adds "Completed" badge to completed tiles.
    
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
        # Phase 5G: Show completion indicator (text-only, no emoji)
        tile.primary_label = "Completed"
        tile.variant = "success"  # Use success variant if available
        
        # Phase 5K: Add "Completed" badge
        if not tile.badges:
            tile.badges = ["Completed"]
        elif "Completed" not in tile.badges:
            tile.badges.append("Completed")
        
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
    
    Phase 4A Revision: Discovery tiles focus on first-touch onboarding.
    Phase 5A: Added Discovery Learning first-touch onboarding tile.
    Phase 5F: Moved GCP to Planning phase for proper journey flow.
    Phase 5K: Filter out completed journeys (they appear in Completed section).
    
    Returns:
        List of discovery tiles with MCIP state applied
    """
    # Check if discovery_learning is completed
    if MCIP.is_product_complete("discovery_learning"):
        # Don't show in active tiles - it will appear in Completed Journeys section
        return []
    
    tiles = [
        ProductTileHub(
            key="discovery_learning",
            title="Start Your Discovery Journey",
            desc="Welcome! Let NAVI introduce you to the care planning process.",
            blurb="First-time here? Learn what to expect and how we'll guide you step-by-step.",
            image_square=None,  # Phase 5E: No PNG, CSS icon
            primary_route="?page=discovery_learning",
            primary_label="Start Here",
            variant="brand",
            order=5,
            visible=True,
            phase="discovery",  # Phase 5A: journey phase tag
            locked=False,  # Phase 5K: Always unlocked
        ),
    ]
    
    # Apply MCIP state to each tile (but discovery should always be available)
    tiles_with_state = []
    for tile in tiles:
        state = _get_product_state(tile.key)
        # Override locked state for discovery - always available
        if state == "locked":
            state = "available"
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
    Phase 5F: Moved GCP here from Discovery - proper planning journey flow.
    Phase 5K: Filter out completed tiles (they appear in Completed section).
    FAQ removed (integrated into NAVI).
    
    Returns:
        List of planning tiles with MCIP state applied
    """
    tiles = [
        ProductTileHub(
            key="gcp_v4",
            title="Guided Care Plan",
            desc="Explore and compare care options.",
            blurb="Answer a few short questions about your daily needs, health, and safety.",
            image_square=None,  # Phase 5E: No PNG, CSS icon
            primary_route="?page=gcp_v4",
            primary_label="Start",
            variant="brand",
            order=10,
            visible=True,
            phase="planning",  # Phase 5F: Corrected to planning phase
        ),
        ProductTileHub(
            key="learn_recommendation",
            title="Learn About My Recommendation",
            desc="Understand your care option before planning costs.",
            blurb="Educational step to learn what your recommendation means and how to prepare.",
            image_square=None,  # Phase 5E: No PNG, CSS icon
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
            image_square=None,  # Phase 5E: No PNG, CSS icon
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
            image_square=None,  # Phase 5E: No PNG, CSS icon
            primary_route="?page=pfma_v3",
            primary_label="Open",
            variant="brand",
            order=30,
            visible=True,
            phase="planning",  # Phase 5A: journey phase tag
        ),
        # Phase 5L: Removed additional_services tile - now rendered as dynamic service cards section
    ]
    
    # Phase Journey Fix: Don't filter out completed planning tiles individually
    # They stay visible until ALL planning journey is complete (GCP + Cost Planner + PFMA)
    planning_complete = _is_planning_journey_complete()
    
    if planning_complete:
        # All planning done - filter them all out (they appear in Completed section)
        tiles = []
    else:
        # Planning still in progress - keep all tiles (even if individually complete)
        tiles_with_state = []
        for tile in tiles:
            state = _get_product_state(tile.key)
            tile_with_state = _apply_tile_state(tile, state)
            tiles_with_state.append(tile_with_state)
        return tiles_with_state
    
    return tiles


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

def _is_planning_journey_complete() -> bool:
    """Check if Planning Journey is complete.
    
    Planning Journey requires:
    - GCP (Guided Care Plan) - required
    - Cost Planner - required
    - PFMA (My Advisor) - required
    - Learn Recommendation - optional (included if done)
    
    Returns:
        True if all required products are complete, False otherwise
    """
    required_products = ["gcp", "cost_planner", "pfma"]
    return all(MCIP.is_product_complete(key) for key in required_products)


def _build_completed_tiles() -> list[ProductTileHub]:
    """Build tiles for completed journeys.
    
    Phase 4A: New section for closed-out products.
    Phase 5D: Updated to use "My Advisor" name.
    Phase 5K: Added discovery_learning to completed journeys.
    Phase Journey Fix: Planning products move together when all core products done.
    
    Returns:
        List of completed product tiles
    """
    completed = []
    
    # Discovery Learning moves individually when complete
    if MCIP.is_product_complete("discovery_learning"):
        completed.append(ProductTileHub(
            key="discovery_learning",
            title="Discovery Journey",
            desc="Your introduction to care planning",
            primary_label="View Summary",
            primary_route="?page=discovery_learning",
            variant="success",
            order=900,
            visible=True,
            badges=["Completed"],
            phase="analysis",
        ))
    
    # Planning Journey products move together when all required are done
    planning_complete = _is_planning_journey_complete()
    
    if planning_complete:
        # Core planning products (always show when planning complete)
        planning_products = [
            ("gcp", "Guided Care Plan", "Your personalized care recommendation"),
            ("cost_planner", "Cost Planner", "Your financial plan and projections"),
            ("pfma", "My Advisor", "Your advisor consultation"),
        ]
        
        # Add Learn Recommendation if user completed it (optional)
        if MCIP.is_product_complete("learn_recommendation"):
            planning_products.insert(1, (
                "learn_recommendation",
                "Learn About My Recommendation",
                "Understanding your care option"
            ))
        
        for key, title, desc in planning_products:
            tile = ProductTileHub(
                key=key,
                title=title,
                desc=desc,
                primary_label="View Summary",
                primary_route=f"?page={key}",
                variant="success",
                order=900,
                visible=True,
                badges=["Completed"],
                phase="analysis",
            )
            # Add outcome if available
            outcome = get_product_outcome(key)
            if outcome:
                tile.desc = outcome
            completed.append(tile)
    
    return completed


def render_additional_services(user_ctx: dict) -> None:
    """
    Dynamically display additional services using existing core/additional_services.py logic.
    
    Phase 5L: Restores flag-driven partner services from Concierge Hub.
    Uses get_additional_services("concierge") which includes:
    - Universal services: Learning Center, Care Coordination Network
    - Flag-triggered partners: Omcare, SeniorLife.AI (show "Navi Recommended" badge)
    - Conditional services based on GCP flags and MCIP data
    
    Args:
        user_ctx: User context dict (not used - get_additional_services() reads from MCIP directly)
    """
    # Phase Post-CSS: Add ID for tour targeting
    st.markdown('<div id="additional-services">', unsafe_allow_html=True)
    st.markdown("### Additional Services")
    st.caption("Partner-powered programs and tools personalized by Navi.")

    services = get_additional_services("concierge")
    if not services:
        st.info("No additional services available right now.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Build cards HTML
    cards_html = []
    for svc in services:
        personalization = svc.get("personalization")
        badge = (
            '<span class="service-badge">Navi Recommended</span>'
            if personalization == "personalized"
            else ""
        )
        
        cards_html.append(
            f'<div class="service-card">'
            f'{badge}'
            f'<h4 class="service-title">{svc["title"]}</h4>'
            f'<p class="service-desc">{svc["subtitle"]}</p>'
            f'<a href="?page={svc["go"]}" class="service-cta">{svc["cta"]}</a>'
            f'</div>'
        )
    
    # Render complete grid
    full_html = f'<div class="service-grid-container">{"".join(cards_html)}</div>'
    st.markdown(full_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_completed_journeys_section(completed_tiles: list[ProductTileHub]) -> None:
    """Render the completed journeys section with proper grid alignment.
    
    Phase 5K: Uses grid layout matching main product tiles for consistency.
    
    Args:
        completed_tiles: List of completed ProductTileHub objects
    """
    # Phase Post-CSS: Add ID for tour targeting
    st.markdown('<div id="completed-journeys" class="completed-journey-section">', unsafe_allow_html=True)
    st.markdown(
        '<div class="completed-journey-header">My Completed Journeys</div>',
        unsafe_allow_html=True
    )
    
    if not completed_tiles:
        # Show empty state when no completed journeys
        st.markdown(
            render_empty_state(
                title="No Completed Journeys Yet",
                message="When you finish a journey, it will appear here for easy review.",
                icon="✅"
            ),
            unsafe_allow_html=True
        )
    else:
        # Render tiles in grid layout matching main dashboard
        st.markdown('<div class="completed-grid">', unsafe_allow_html=True)
        for tile in completed_tiles:
            tile_html = tile.render_html()
            if tile_html:
                st.markdown(tile_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# LOBBY ONBOARDING TOUR (Phase Post-CSS)
# ==============================================================================

def _render_lobby_tour() -> None:
    """Render contextual one-time lobby onboarding tour with replay option.
    
    Phase Post-CSS: Adds guided tour highlighting key lobby sections.
    Uses Streamlit native components for maximum compatibility.
    Tour runs once per user session, with manual replay via help icon.
    """
    # Global enable/disable flag
    ENABLE_LOBBY_TOUR = False  # Disabled for now
    
    if not ENABLE_LOBBY_TOUR:
        return
    
    # Initialize tour state
    if "lobby_tour_done" not in st.session_state:
        st.session_state["lobby_tour_done"] = False
    
    if "lobby_tour_step" not in st.session_state:
        st.session_state["lobby_tour_step"] = 0
    
    if "lobby_tour_active" not in st.session_state:
        st.session_state["lobby_tour_active"] = False
    
    # Check for replay trigger from query params
    if st.query_params.get("replay_tour") == "1":
        st.session_state["lobby_tour_done"] = False
        st.session_state["lobby_tour_active"] = True
        st.session_state["lobby_tour_step"] = 0
        st.query_params.clear()
    
    # Auto-start tour for first-time users
    if not st.session_state["lobby_tour_done"] and not st.session_state["lobby_tour_active"]:
        st.session_state["lobby_tour_active"] = True
    
    # Tour steps definition
    tour_steps = [
        {
            "title": "🧭 Welcome to Your Lobby",
            "message": "Let's take a quick tour to show you around. You'll learn where everything is and how to navigate your care journey.",
        },
        {
            "title": "👋 Meet Navi - Your AI Guide",
            "message": "Look for the Navi panel at the top of your Lobby. Navi provides personalized guidance, tracks your progress, and suggests next steps based on where you are in your journey.",
        },
        {
            "title": "🧭 Your Active Journeys",
            "message": "Below Navi, you'll find all active products and tools. Start with the Discovery Journey if you're new, or continue your Guided Care Plan and Cost Planner when you're ready.",
        },
        {
            "title": "💡 Additional Services",
            "message": "Scroll down to see partner services and AI-recommended resources tailored to your specific care needs and situation.",
        },
        {
            "title": "✅ Completed Journeys",
            "message": "At the bottom, completed journeys are archived. You can always come back to review your care recommendation, cost plan, or other completed assessments.",
        },
        {
            "title": "🎉 You're All Set!",
            "message": "That's everything! If you ever need this tour again, click the ❓ help icon in the top-right corner. Ready to begin?",
        }
    ]
    
    # Render replay button (always visible after first tour)
    if st.session_state["lobby_tour_done"]:
        st.markdown(
            """
            <a href="?page=hub_lobby&replay_tour=1" 
               class="tour-replay-button" 
               title="Replay lobby tour"
               style="
                   position: fixed;
                   top: 80px;
                   right: 24px;
                   z-index: 9999;
                   background: var(--surface-neutral, #fff);
                   cursor: pointer;
                   color: var(--brand-primary, #5b4cf0);
                   font-size: 20px;
                   padding: 10px 12px;
                   border-radius: 50%;
                   text-decoration: none;
                   transition: all 0.2s ease;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                   border: 2px solid var(--brand-primary, #5b4cf0);
               "
               onmouseover="this.style.background='var(--brand-primary, #5b4cf0)'; this.style.color='white';"
               onmouseout="this.style.background='var(--surface-neutral, #fff)'; this.style.color='var(--brand-primary, #5b4cf0)';">
                ❓
            </a>
            """,
            unsafe_allow_html=True
        )
        return
    
    # Render active tour using st.dialog
    if st.session_state["lobby_tour_active"]:
        current_step = st.session_state["lobby_tour_step"]
        
        if current_step < len(tour_steps):
            step = tour_steps[current_step]
            
            # Use st.dialog for modal
            @st.dialog(step['title'], width="large")
            def show_tour_step():
                # Message content
                st.markdown(step['message'])
                
                # Add helpful note for scroll sections
                if current_step >= 3:  # Additional Services and Completed Journeys
                    st.info("💡 This section is below. Scroll down after the tour to see it.", icon="ℹ️")
                
                # Progress indicator
                st.divider()
                st.caption(f"Step {current_step + 1} of {len(tour_steps)}")
                
                # Buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if current_step > 0:
                        if st.button("← Back", key=f"tour_back_{current_step}", use_container_width=True):
                            st.session_state["lobby_tour_step"] -= 1
                            st.rerun()
                    else:
                        st.markdown("")  # Empty space for alignment
                
                with col2:
                    if st.button("Skip Tour", key=f"tour_skip_{current_step}", use_container_width=True):
                        st.session_state["lobby_tour_active"] = False
                        st.session_state["lobby_tour_done"] = True
                        st.session_state["lobby_tour_step"] = 0
                        st.rerun()
                
                with col3:
                    if current_step < len(tour_steps) - 1:
                        if st.button("Next →", key=f"tour_next_{current_step}", type="primary", use_container_width=True):
                            st.session_state["lobby_tour_step"] += 1
                            st.rerun()
                    else:
                        if st.button("Start Exploring!", key=f"tour_done_{current_step}", type="primary", use_container_width=True):
                            st.session_state["lobby_tour_active"] = False
                            st.session_state["lobby_tour_done"] = True
                            st.session_state["lobby_tour_step"] = 0
                            st.rerun()
            
            show_tour_step()
        else:
            # Tour completed
            st.session_state["lobby_tour_active"] = False
            st.session_state["lobby_tour_done"] = True
            st.session_state["lobby_tour_step"] = 0


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
    
    # Phase 5M: Journey progress bar moved inside NAVI card (core/navi_hub.py)
    # Removed temporary top header progress display
    # from core.journeys import get_phase_completion
    # journey_stage = st.session_state.get("journey_stage", "discovery")
    # completion = get_phase_completion(journey_stage)
    # st.caption(f"**{journey_stage.replace('_', ' ').title()} Phase Progress**")
    # st.progress(completion)
    # st.markdown("<br/>", unsafe_allow_html=True)
    
    # Phase Post-CSS: Add ID for tour targeting
    st.markdown('<div id="navi-panel">', unsafe_allow_html=True)
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
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
    
    # Phase 5E: Filter tiles by visible modules from personalization
    # Phase 5L: Removed additional_services exception (now rendered as separate dynamic section)
    if visible_modules:
        discovery_tiles = [
            t for t in discovery_tiles 
            if t.key in visible_modules or t.key.startswith("discovery_")
        ]
        planning_tiles = [
            t for t in planning_tiles 
            if t.key in visible_modules or t.key.startswith("discovery_")
        ]
        engagement_tiles = [
            t for t in engagement_tiles 
            if t.key in visible_modules or t.key.startswith("discovery_")
        ]
    
    # Sort each section by order
    discovery_tiles.sort(key=lambda t: t.order)
    planning_tiles.sort(key=lambda t: t.order)
    engagement_tiles.sort(key=lambda t: t.order)
    
    # ========================================
    # COMPLETED JOURNEYS SECTION (Phase 5G)
    # ========================================
    completed_tiles = _build_completed_tiles()
    
    # ========================================
    # RENDER ACTIVE JOURNEYS WITH SECTION HEADERS
    # ========================================
    # Phase Post-CSS: Add ID for tour targeting
    st.markdown('<div id="product-tiles">', unsafe_allow_html=True)
    
    # Discovery Journey Section
    if discovery_tiles:
        st.markdown(
            '<div class="journey-section-header"><span class="journey-section-title">Discovery</span></div>',
            unsafe_allow_html=True
        )
        discovery_html = render_dashboard_body(
            title="",
            subtitle=None,
            chips=None,
            hub_guide_block=None,
            hub_order=None,
            cards=discovery_tiles,
            additional_services=[],
        )
        st.markdown(discovery_html, unsafe_allow_html=True)
    
    # Planning Tools Section
    if planning_tiles:
        st.markdown(
            '<div class="journey-section-header"><span class="journey-section-title">Planning Tools</span></div>',
            unsafe_allow_html=True
        )
        planning_html = render_dashboard_body(
            title="",
            subtitle=None,
            chips=None,
            hub_guide_block=None,
            hub_order=None,
            cards=planning_tiles,
            additional_services=[],
        )
        st.markdown(planning_html, unsafe_allow_html=True)
    
    # Engagement Section (Post-Planning Journey)
    # Only show after Planning Journey is complete
    planning_complete = _is_planning_journey_complete()
    
    if planning_complete and engagement_tiles:
        st.markdown(
            '<div class="journey-section-header"><span class="journey-section-title">Engagement</span></div>',
            unsafe_allow_html=True
        )
        engagement_html = render_dashboard_body(
            title="",
            subtitle=None,
            chips=None,
            hub_guide_block=None,
            hub_order=None,
            cards=engagement_tiles,
            additional_services=[],
        )
        st.markdown(engagement_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========================================
    # INFORMATIONAL TEXT (Phase 5G)
    # ========================================
    # Show only when completed journeys exist
    if completed_tiles:
        st.markdown(
            '<p class="section-note">Your completed journeys are shown below.</p>',
            unsafe_allow_html=True
        )
    
    # ========================================
    # ADDITIONAL SERVICES SECTION (Phase 5L - Dynamic Context-Driven Cards)
    # ========================================
    # Phase 5L: Replace old product-tile implementation with dynamic service cards
    # Driven by care flags, not product tiles
    render_additional_services(user_ctx)
    
    # ========================================
    # MY COMPLETED JOURNEYS (Phase 5K - Always Visible with Empty State)
    # ========================================
    # Use helper function for proper grid rendering
    _render_completed_journeys_section(completed_tiles)
    
    # ========================================
    # FOOTER
    # ========================================
    render_footer_simple()
    
    # ========================================
    # LOBBY ONBOARDING TOUR (Phase Post-CSS)
    # ========================================
    _render_lobby_tour()
