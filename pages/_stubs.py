from typing import List, Optional, Tuple

import streamlit as st

from core.nav import route_to


def _page(title: str, desc: str, ctas: Optional[List[Tuple[str, str]]] = None):
    st.header(title)
    st.write(desc)
    if ctas:
        for label, target in ctas:
            if st.button(label, key=f"cta-{title}-{target}"):
                route_to(target)


def render_welcome():
    _page(
        "Welcome",
        "Entry for seniors and caregivers.",
        [
            ("Contextual Welcome", "welcome_contextual"),
            ("Professionals", "professionals"),
            ("Login", "login"),
        ],
    )


def render_welcome_contextual():
    _page(
        "Contextual Welcome",
        "Variant based on inbound source/referral.",
        [("Back to Welcome", "welcome")],
    )


def render_pro_welcome():
    _page(
        "Professional Welcome",
        "Entry for discharge planners and partners.",
        [("Pro Contextual", "pro_welcome_contextual")],
    )


def render_pro_welcome_contextual():
    _page(
        "Pro Contextual Welcome",
        "Contextualized pro entry.",
        [("Professionals", "professionals")],
    )


def render_professionals():
    _page(
        "Professionals",
        "Hub for professional tools and referral intake.",
        [("Trusted Partners", "trusted_partners")],
    )


def render_login():
    _page(
        "Login",
        "Auth form placeholder.",
        [("My Account", "my_account")],
    )


def render_ai_advisor():
    _page("AI Advisor (Navi)", "Conversation surface placeholder.")


def render_documents():
    _page("Documents", "Uploads and document listing. Auth required.")


def render_exports():
    _page("Exports", "PDF/CSV bundle generator. Auth required.")


def render_waiting_room():
    _page(
        "Waiting Room",
        "Post-booking dashboard with tasks.",
        [("AI Advisor", "ai_advisor")],
    )


def render_trusted_partners():
    _page("Trusted Partners", "Partner directory and disclosures.")


def render_my_account():
    _page(
        "My Account",
        "Profile, preferences, and consent history.",
        [("Privacy Policy", "privacy"), ("Terms of Use", "terms")],
    )


def render_terms():
    _page("Terms of Use", "Versioned legal surface.")


def render_privacy():
    _page("Privacy Policy", "Versioned privacy surface.")


def render_about():
    _page("About Us", "Company, mission, and contact.")
