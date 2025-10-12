# hubs/waiting_room.py
import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import _inject_hub_css_once, render_dashboard
from core.hub_guide import compute_hub_guide
from core.product_tile import ProductTileHub

__all__ = ["render"]

_inject_hub_css_once()


def render(ctx=None) -> None:
    person = st.session_state.get("person_name", "John")

    # Pull state safely with fallbacks
    appt = st.session_state.get("appointment", {}) or {}
    appointment_summary = appt.get("summary", "No appointment scheduled")
    appointment_countdown = appt.get("countdown", "No date")
    edu_progress = float(
        (st.session_state.get("learning", {}) or {}).get("progress", 0)
    )
    gamification_progress = float(
        (st.session_state.get("gamification", {}) or {}).get("progress", 0)
    )

    cards = [
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

    render_dashboard(
        title="Waiting Room",
        subtitle="Your plan is active. Keep it fresh and share updates with your advisor.",
        chips=[{"label": "In service"}, {"label": f"For {person}", "variant": "muted"}],
        hub_guide_block=guide,
        cards=cards,
        additional_services=additional,
    )
