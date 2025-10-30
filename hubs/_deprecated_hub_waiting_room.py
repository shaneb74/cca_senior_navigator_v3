# hubs/waiting_room.py


import os
import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.mcip import MCIP
from core.navi import render_navi_panel
from core.product_tile import ProductTileHub
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple

__all__ = ["render"]


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
    total_quizzes = (
        5  # truths_myths, music_trivia, medicare_quiz, healthy_habits, community_challenge
    )

    if not badges_earned:
        return 0

    completed_count = len(badges_earned)
    return int((completed_count / total_quizzes) * 100)


def _build_advisor_prep_tile(is_next_recommended: bool) -> ProductTileHub | None:
    """Build Advisor Prep tile if PFMA booking exists.
    
    Args:
        is_next_recommended: True if this is the MCIP-recommended next action
    
    Returns:
        ProductTileHub or None if not available
    """
    prep_summary = MCIP.get_advisor_prep_summary()

    if not prep_summary.get("available"):
        return None  # Don't show tile until appointment booked

    sections_complete = prep_summary.get("sections_complete", [])
    progress = prep_summary.get("progress", 0)
    next_section = prep_summary.get("next_section")
    appt_context = prep_summary.get("appointment_context", "")

    # Build description
    if progress == 100:
        desc = "✓ All prep sections complete — you're ready!"
        primary_label = "Review Prep"
    elif progress > 0:
        desc = f"{len(sections_complete)} of 4 sections complete"
        primary_label = "Continue Prep"
    else:
        desc = "Help your advisor prepare for your consultation"
        primary_label = "Start Prep"

    # Build badges
    badges = []
    if progress == 100:
        badges = [{"label": "Ready", "tone": "success"}]
    elif progress > 0:
        badges = [{"label": f"{len(sections_complete)}/4", "tone": "info"}]

    # Variant: gradient brand if recommended, purple otherwise
    variant = "brand" if is_next_recommended else "purple"

    return ProductTileHub(
        key="advisor_prep",
        title="Advisor Prep",
        desc=desc,
        blurb=appt_context or "Prepare for your upcoming consultation with your advisor",
        badge_text="OPTIONAL",
        image_square="advisor_prep.png",
        meta_lines=["4 sections • 5-10 min total"],
        badges=badges,
        primary_label=primary_label,
        primary_route="?page=advisor_prep",
        primary_go="advisor_prep",
        secondary_label=None,
        secondary_go=None,
        progress=progress,
        status_text="✓ Complete" if progress == 100 else None,
        variant=variant,  # Gradient if recommended
        order=1,  # FIRST in Waiting Room (MCIP-driven)
        locked=False,
        recommended_in_hub="waiting_room",
        recommended_total=5,  # Total activities in Waiting Room
        recommended_order=1,  # First recommendation
        is_next_step=is_next_recommended,  # Enables gradient styling
    )


def _build_trivia_tile(is_next_recommended: bool) -> ProductTileHub:
    """Build Senior Trivia tile.
    
    Args:
        is_next_recommended: True if this is the MCIP-recommended next action
    
    Returns:
        ProductTileHub
    """
    trivia_badges = _get_trivia_badges()
    trivia_progress = _get_trivia_progress()

    # Variant: gradient brand if recommended, teal otherwise
    variant = "brand" if is_next_recommended else "teal"

    return ProductTileHub(
        key="senior_trivia",
        title="Senior Trivia & Brain Games",
        desc="Test your knowledge with fun, educational trivia",
        blurb="Play solo or with family! Topics include senior living myths, music nostalgia, Medicare, healthy habits, and family fun.",
        primary_label="Play Trivia",
        primary_go="senior_trivia",
        secondary_label=None,
        secondary_go=None,
        progress=trivia_progress,
        badges=trivia_badges,
        variant=variant,  # Gradient if recommended
        order=2,  # SECOND in Waiting Room (MCIP-driven)
        recommended_in_hub="waiting_room",
        recommended_total=5,
        recommended_order=2,
        is_next_step=is_next_recommended,
    )


def _build_featured_partners_tile(is_next_recommended: bool) -> ProductTileHub:
    """Build Featured Partners tile.
    
    Args:
        is_next_recommended: True if this is the MCIP-recommended next action
    
    Returns:
        ProductTileHub
    """
    # Variant: gradient brand if recommended, default brand otherwise
    variant = "brand" if is_next_recommended else "brand"

    return ProductTileHub(
        key="partners_spotlight",
        title="Featured Partners",
        desc="Tailored recommendations for home care, tech, and more",
        blurb="Browse verified providers spotlighted for your plan.",
        primary_label="Browse Partners",
        primary_go="partners_spotlight_carousel",
        progress=None,
        badges=["verified"],
        variant=variant,
        order=3,  # THIRD in Waiting Room (MCIP-driven)
        recommended_in_hub="waiting_room",
        recommended_total=5,
        recommended_order=3,
        is_next_step=is_next_recommended,
    )


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


def _build_clinical_review_tile() -> ProductTileHub:
    """Build Concierge Clinical Review tile.
    
    Returns:
        ProductTileHub (visible but locked until GCP & CP complete)
    """
    _gcp_done = _is_gcp_complete()
    _cp_done = _is_cost_planner_complete()
    
    _ccr_locked = not (_gcp_done and _cp_done)
    if _dev_unlock_tiles():
        _ccr_locked = False
    
    # TEMP: gate decision log (remove when stable)
    print(f"[CCR_GATE] dev={_dev_unlock_tiles()} gcp={_gcp_done} cp={_cp_done} locked={_ccr_locked}")

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
        order=4,
        locked=_ccr_locked,
        lock_msg="Unlocks after Guided Care Plan and Cost Planner. Providers use both your care and financial info to give precise guidance." if _ccr_locked else None,
    )


def _determine_next_recommendation() -> str:
    """Determine next recommended activity using MCIP logic.
    
    Priority order:
    1. Advisor Prep (if appointment booked and not complete)
    2. Senior Trivia (if no badges earned)
    3. Featured Partners (default)
    
    Returns:
        Key of recommended tile ("advisor_prep", "senior_trivia", "partners_spotlight")
    """
    # Check waiting room state from MCIP
    waiting_room_state = MCIP.get_waiting_room_state()
    current_focus = waiting_room_state.get("current_focus", "advisor_prep")

    # Get advisor prep summary
    prep_summary = MCIP.get_advisor_prep_summary()
    advisor_prep_available = prep_summary.get("available", False)
    advisor_prep_progress = prep_summary.get("progress", 0)

    # Priority 1: Advisor Prep if available and not complete
    if advisor_prep_available and advisor_prep_progress < 100:
        return "advisor_prep"

    # Priority 2: Senior Trivia if no progress
    trivia_progress = _get_trivia_progress()
    if trivia_progress == 0:
        return "senior_trivia"

    # Priority 3: Featured Partners (default)
    return "partners_spotlight"


def render(ctx=None) -> None:
    """Render Waiting Room Hub with MCIP-driven tile ordering and styling."""

    # Initialize MCIP
    MCIP.initialize()

    # Determine next recommended activity
    next_recommendation = _determine_next_recommendation()

    # Pull state safely with fallbacks for remaining tiles
    edu_progress = float((st.session_state.get("learning", {}) or {}).get("progress", 0))

    # Build MCIP-driven tiles (orders 1-3)
    advisor_prep_tile = _build_advisor_prep_tile(
        is_next_recommended=(next_recommendation == "advisor_prep")
    )
    trivia_tile = _build_trivia_tile(
        is_next_recommended=(next_recommendation == "senior_trivia")
    )
    partners_tile = _build_featured_partners_tile(
        is_next_recommended=(next_recommendation == "partners_spotlight")
    )
    clinical_review_tile = _build_clinical_review_tile()

    # Assemble tiles in MCIP-driven order
    cards = [
        advisor_prep_tile,  # Order 1 (if available)
        trivia_tile,         # Order 2
        partners_tile,       # Order 3
        clinical_review_tile,  # Order 4 (visible-always; locked until GCP & CP complete)
        # Remaining tiles (legacy order values)
        ProductTileHub(
            key="educational_feed",
            title="Recommended Learning",
            desc="Videos, guides, and tips for your journey",
            blurb="Pick up where you left off or discover new resources.",
            primary_label="Explore feed",
            primary_go="educational_feed",
            secondary_label="Continue watching",
            secondary_go="resume_edu_content",
            progress=edu_progress,
            badges=["personalized"],
            variant="teal",
            order=30,
        ),
    ]

    # Filter out None tiles (Advisor Prep may be None if appointment not booked)
    cards = [c for c in cards if c is not None]

    # Sort by order (MCIP-driven)
    cards.sort(key=lambda c: c.order)

    additional = get_additional_services("waiting_room")

    # Use callback pattern to render Navi AFTER header
    def render_content():
        # Render Navi panel (after header, before hub content)
        render_navi_panel(location="hub", hub_key="waiting_room")

        # Render hub body HTML WITHOUT title/subtitle/chips (Navi replaces them)
        body_html = render_dashboard_body(
            title=None,
            subtitle=None,
            chips=None,
            hub_guide_block=None,  # Navi replaces hub guide
            cards=cards,
            additional_services=additional,  # Include in HTML for proper layout
        )
        st.markdown(body_html, unsafe_allow_html=True)

    # Render with simple header/footer
    render_header_simple(active_route="hub_waiting")
    render_content()
    render_footer_simple()
