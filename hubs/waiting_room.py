# hubs/waiting_room.py
import html
import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.hub_guide import compute_hub_guide
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
            progress=None,
            badges=trivia_badges,  # Dynamic badges from earned achievements
            variant="teal",
            order=5,  # First tile
        ),
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
