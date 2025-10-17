# hubs/waiting_room.py
import html
import streamlit as st
from typing import Optional

from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.hub_guide import compute_hub_guide
from core.mcip import MCIP
from core.navi import render_navi_panel
from core.product_tile import ProductTileHub
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

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
        clean_name = badge_name.replace(" ⭐⭐⭐⭐", "").replace(" ⭐⭐⭐", "").replace(" ⭐⭐", "").replace(" ⭐", "")
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


def _build_advisor_prep_tile() -> Optional[ProductTileHub]:
    """Build Advisor Prep tile if PFMA booking exists.
    
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
    
    return ProductTileHub(
        key="advisor_prep",
        title="Advisor Prep",
        desc=desc,
        blurb=appt_context,
        badge_text="OPTIONAL",
        image_square="advisor_prep.png",  # Note: image file needs to be added
        meta_lines=["4 sections • 5-10 min total"],
        badges=badges,
        primary_label=primary_label,
        primary_route="?page=advisor_prep",
        primary_go="advisor_prep",
        secondary_label=None,
        secondary_go=None,
        progress=progress,
        status_text="✓ Complete" if progress == 100 else None,
        variant="purple",
        order=6,  # After Trivia (5), before Appointment (10)
        locked=False,
        recommended_in_hub="waiting_room",
        recommended_total=3,
        recommended_order=1  # Recommend first after booking
    )


def render(ctx=None) -> None:
    person_name = st.session_state.get("person_name", "").strip()
    # Use person's name if available, otherwise use neutral "you"
    person = person_name if person_name else "you"

    # Pull state safely with fallbacks
    appt = st.session_state.get("appointment", {}) or {}
    appointment_summary = appt.get("summary", "No appointment scheduled")
    appointment_countdown = appt.get("countdown", "No date")
    edu_progress = float((st.session_state.get("learning", {}) or {}).get("progress", 0))
    gamification_progress = float(
        (st.session_state.get("gamification", {}) or {}).get("progress", 0)
    )

    # Dynamically add Senior Trivia tile with earned badges (FIRST TILE - order=5)
    trivia_badges = _get_trivia_badges()
    trivia_progress = _get_trivia_progress()
    
    # Build advisor prep tile (conditional on PFMA booking)
    advisor_prep_tile = _build_advisor_prep_tile()
    
    cards = [
        ProductTileHub(
            key="senior_trivia",
            title="Senior Trivia & Brain Games",
            desc="Test your knowledge with fun, educational trivia",
            blurb="Play solo or with family! Topics include senior living myths, music nostalgia, Medicare, healthy habits, and family fun.",
            primary_label="Play Trivia",
            primary_go="senior_trivia",
            secondary_label=None,
            secondary_go=None,
            progress=trivia_progress,  # Progress based on completed quizzes
            badges=trivia_badges,  # Dynamic badges from earned achievements
            variant="teal",
            order=5,  # First tile
        ),
        # Conditionally add Advisor Prep tile (order=6)
        advisor_prep_tile,
        ProductTileHub(
            key="appointment",
            title="Your Upcoming Appointment",
            desc=f"Starts in {appointment_countdown} • {appointment_summary}",
            blurb="Review details, prepare questions, and confirm your concierge consult.",
            primary_label="View details",
            primary_go="appointment_details",
            secondary_label="Reschedule",
            secondary_go="appointment_reschedule",
            progress=None,  # no pill; explicit status below
            status_text="Scheduled",
            badges=["countdown"],
            variant="warn",
            order=10,
        ),
        ProductTileHub(
            key="partners_spotlight",
            title="Featured Partners",
            desc="Tailored recommendations for home care, tech, and more",
            blurb="Browse verified providers spotlighted for your plan.",
            primary_label="Browse partners",
            primary_go="partners_spotlight_carousel",
            progress=None,
            badges=["verified"],
            variant="brand",
            order=20,
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

    guide = compute_hub_guide("waiting_room")
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
