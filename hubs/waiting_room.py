# hubs/waiting_room.py

from typing import Optional
import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.hub_guide import compute_hub_guide
from core.mcip import MCIP
from core.navi import render_navi_panel
from core.product_tile import ProductTileHub
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple

__all__ = ["render"]


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


def _build_advisor_prep_tile(is_next_recommended: bool) -> Optional[ProductTileHub]:
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
    appt = st.session_state.get("appointment", {}) or {}
    appointment_summary = appt.get("summary", "No appointment scheduled")
    appointment_countdown = appt.get("countdown", "No date")
    edu_progress = float((st.session_state.get("learning", {}) or {}).get("progress", 0))
    gamification_progress = float(
        (st.session_state.get("gamification", {}) or {}).get("progress", 0)
    )
    
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
    
    # Assemble tiles in MCIP-driven order
    cards = [
        advisor_prep_tile,  # Order 1 (if available)
        trivia_tile,         # Order 2
        partners_tile,       # Order 3
        # Remaining tiles (legacy order values)
        ProductTileHub(
            key="appointment",
            title="Your Upcoming Appointment",
            desc=f"Starts in {appointment_countdown} • {appointment_summary}",
            blurb="Review details, prepare questions, and confirm your concierge consult.",
            primary_label="View details",
            primary_go="appointment_details",
            secondary_label="Reschedule",
            secondary_go="appointment_reschedule",
            progress=None,
            status_text="Scheduled",
            badges=["countdown"],
            variant="warn",
            order=10,
        ),
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
        ProductTileHub(
            key="entertainment",
            title="While You Wait",
            desc="Fun trivia and quick games",
            blurb="Earn badges and stay relaxed before your consult.",
            primary_label="Start playing",
            primary_go="entertainment_deck",
            progress=gamification_progress,
            badges=["badges"],
            variant="violet",
            order=40,
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
