from __future__ import annotations

from typing import Dict

import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import BaseHub
from core.product_tile import ProductTileHub


class WaitingRoomHub(BaseHub):
    def __init__(self) -> None:
        super().__init__(
            title="Waiting Room Hub",
            icon="🕐",
            description="Track appointment status, complete pre-visit tasks, and stay ready for your advisor.",
        )

    def build_dashboard(self) -> Dict:
        person_name = st.session_state.get("person_name", "John")
        appointment_time = st.session_state.get("appointment_time", "Advisor call pending")
        appointment_status = st.session_state.get("appointment_status", "Scheduled")
        prep_completed = st.session_state.get("prep_completed", False)
        ride_confirmed = st.session_state.get("ride_confirmed", False)

        appointment_progress = 100 if appointment_status.lower() == "completed" else 60
        checklist_progress = 100 if prep_completed else 50
        waiting_progress = 40
        transport_progress = 100 if ride_confirmed else 20

        cards = [
            ProductTileHub(
                key="upcoming_appointment",
                title="Upcoming appointment",
                desc="Review details, add notes, and share updates with your advisor.",
                blurb="Track confirmations and reminders in one place.",
                badge_text="APPOINTMENT",
                meta_lines=[f"Status: {appointment_status}", appointment_time],
                primary_label="View details",
                primary_go="pfma_stub",
                secondary_label="Reschedule",
                secondary_go="pfma_stub",
                progress=appointment_progress,
                variant="brand",
                order=10,
            ),
            ProductTileHub(
                key="pre_visit_checklist",
                title="Pre-visit checklist",
                desc="Upload docs and confirm topics.",
                blurb="Bring recent medical updates, medications, and top questions.",
                badge_text="GUIDED",
                meta_lines=["Checklist saves automatically", "Share securely with advisors"],
                primary_label="Review tasks" if prep_completed else "Start checklist",
                primary_go="gcp_stub",
                secondary_label="Questions for advisor",
                secondary_go="pfma_stub",
                progress=checklist_progress,
                variant="brand",
                order=20,
            ),
            ProductTileHub(
                key="virtual_waiting",
                title="Virtual waiting room",
                desc="Ready when you are.",
                blurb="Launch five minutes before your appointment and test your connection.",
                badge_text="LIVE LINK",
                meta_lines=["Link opens in a new tab", "Tech check available anytime"],
                primary_label="Join call",
                primary_go="pfma_stub",
                secondary_label="View wait time",
                secondary_go="pfma_stub",
                progress=waiting_progress,
                variant="teal",
                order=30,
            ),
            ProductTileHub(
                key="transportation",
                title="Transportation",
                desc="Confirm ride plans.",
                blurb="Arrange rides for appointments, tours, or caregiving visits.",
                badge_text="TRUSTED PARTNERS",
                meta_lines=["Coordinate with Lyft Health, GoGoGrandparent, and more."],
                primary_label="Book ride",
                primary_go="hub_trusted",
                secondary_label="Share itinerary",
                secondary_go="pfma_stub",
                progress=transport_progress,
                variant="violet",
                order=40,
            ),
        ]

        guide_block = {
            "eyebrow": "You're on the list",
            "title": "Relax — we’ll notify you the moment your advisor joins.",
            "body": "Complete the pre-visit checklist so your advisor has the latest updates before the call.",
            "actions": [
                {"label": "Finish checklist", "route": "gcp_stub", "variant": "primary"},
                {"label": "Contact support", "route": "pfma_stub", "variant": "ghost"},
            ],
        }

        chips = [
            {"label": "Waiting room"},
            {"label": "Advisor session", "variant": "muted"},
            {"label": "Prepared & confident"},
        ]

        return {
            "chips": chips,
            "cards": cards,
            "additional_services": get_additional_services("waiting_room"),
            "hub_guide_block": guide_block,
        }


def render() -> None:
    hub = WaitingRoomHub()
    hub.render()
