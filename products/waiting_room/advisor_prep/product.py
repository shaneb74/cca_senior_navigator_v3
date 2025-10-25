"""
Advisor Prep - Optional preparation sections for advisor consultations

Module-based product with 4 JSON-driven sections:
- Personal: Demographics and living situation
- Financial: Income, assets, and insurance
- Housing: Care preferences and location
- Medical: Chronic conditions and care flags (Flag Manager integration)

Architecture:
- Entry point: product.render() checks prerequisites and routes to modules
- Module router: Displays section menu and routes to selected section
- Modules: personal.py, financial.py, housing.py, medical.py
- JSON configs: Define fields, types, prefill sources
- Progress tracking: n/4 sections complete, updates MCIP
"""

import json
from pathlib import Path

import streamlit as st

from core.events import log_event
from core.mcip import MCIP
from core.nav import route_to
from core.navi import render_navi_panel


def render():
    """Main entry point for Advisor Prep product."""

    # Step 1: Check prerequisites (requires PFMA booking)
    if not _check_prerequisites():
        render_navi_panel(location="product", product_key="advisor_prep", module_config=None)
        _render_gate()
        return

    # Step 2: Initialize state
    _initialize_state()

    # Step 3: Check if section selected
    current_section = st.session_state.get("advisor_prep_current_section")

    if current_section:
        # Render specific section module
        _render_section(current_section)
    else:
        # Render section menu
        render_navi_panel(location="product", product_key="advisor_prep", module_config=None)
        _render_section_menu()


# =============================================================================
# PREREQUISITE CHECKING
# =============================================================================


def _check_prerequisites() -> bool:
    """Check if PFMA appointment is booked.

    Returns:
        True if prerequisites met, False otherwise
    """
    appt = MCIP.get_advisor_appointment()
    return appt is not None and appt.scheduled


def _render_gate():
    """Show friendly gate requiring PFMA booking first."""
    st.markdown("## 🎯 Prepare for Your Appointment")

    st.info(
        "**Ready to prepare for your consultation?**\n\n"
        "Please book your advisor appointment first. Once scheduled, "
        "you can return here to complete optional prep sections."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("← Return to Waiting Room", type="secondary", use_container_width=True):
            route_to("hub_waiting")

    with col2:
        if st.button("Book Appointment →", type="primary", use_container_width=True):
            route_to("pfma_v3")


# =============================================================================
# STATE INITIALIZATION
# =============================================================================


def _initialize_state():
    """Initialize Advisor Prep state if not exists."""
    if "advisor_prep" not in st.session_state:
        st.session_state["advisor_prep"] = {
            "sections_complete": [],
            "data": {"personal": {}, "financial": {}, "housing": {}, "medical": {}},
        }
        log_event("advisor_prep.started", {})


# =============================================================================
# SECTION MENU
# =============================================================================


def _render_section_menu():
    """Render section selection menu."""
    st.markdown("## 🎯 Prepare for Your Appointment")

    # Get appointment context
    prep_summary = MCIP.get_advisor_prep_summary()
    st.info(f"**{prep_summary['appointment_context']}**")

    st.markdown(
        "Complete these optional sections to help your advisor provide personalized guidance. "
        "All information is confidential and helps us maximize the value of your consultation."
    )

    # Progress indicator
    sections_complete = st.session_state["advisor_prep"]["sections_complete"]
    progress = len(sections_complete) * 25

    st.progress(progress / 100, text=f"Progress: {len(sections_complete)}/4 sections complete")

    # Duck badge progress (local import to avoid circular dependency)
    try:
        from products.waiting_room.advisor_prep.utils import get_duck_progress, is_all_ducks_earned

        duck_progress = get_duck_progress()
        if duck_progress["earned_count"] > 0:
            duck_display = "🦆" * duck_progress["earned_count"]
            if is_all_ducks_earned():
                st.success(
                    f"🎉 {duck_display} **All Ducks in a Row!** You've completed all prep sections."
                )
            else:
                st.info(
                    f"{duck_display} **{duck_progress['earned_count']}/4 Ducks Earned** — Keep going!"
                )
    except ImportError:
        pass  # Duck badges not available, skip display

    st.markdown("---")

    # Load section configs
    sections = _load_section_configs()

    # Render section cards
    st.markdown("### Preparation Sections")

    cols = st.columns(2)

    for idx, section in enumerate(sections):
        with cols[idx % 2]:
            is_complete = section["key"] in sections_complete

            # Section card
            with st.container():
                st.markdown(f"### {section['icon']} {section['title']}")
                st.markdown(section["description"])

                if is_complete:
                    st.success("✓ Complete")
                else:
                    st.caption("Not started")

                button_label = "Review" if is_complete else "Start"
                if st.button(
                    f"{button_label} →",
                    key=f"section_{section['key']}",
                    use_container_width=True,
                    type="primary" if not is_complete else "secondary",
                ):
                    st.session_state["advisor_prep_current_section"] = section["key"]
                    log_event("advisor_prep.section.started", {"section": section["key"]})
                    st.rerun()

                st.markdown("---")

    # Navigation
    st.markdown("### Navigation")
    col_nav1, col_nav2 = st.columns(2)

    with col_nav1:
        if st.button("← Return to Waiting Room", type="secondary", use_container_width=True):
            route_to("hub_waiting")

    with col_nav2:
        if progress == 100:
            if st.button("✓ All Done", type="primary", use_container_width=True):
                log_event("advisor_prep.completed", {"sections_complete": 4})
                route_to("hub_waiting")


def _load_section_configs() -> list:
    """Load all section JSON configs.

    Returns:
        List of section config dicts
    """
    config_dir = Path(__file__).parent / "config"
    section_keys = ["personal", "financial", "housing", "medical"]

    sections = []
    for key in section_keys:
        config_path = config_dir / f"{key}.json"
        with open(config_path) as f:
            sections.append(json.load(f))

    return sections


# =============================================================================
# SECTION RENDERING
# =============================================================================


def _render_section(section_key: str):
    """Render a specific section module.

    Args:
        section_key: Section identifier (personal, financial, housing, medical)
    """
    # Import appropriate module
    if section_key == "personal":
        from .modules import personal

        personal.render()
    elif section_key == "financial":
        from .modules import financial

        financial.render()
    elif section_key == "housing":
        from .modules import housing

        housing.render()
    elif section_key == "medical":
        from .modules import medical

        medical.render()
    else:
        st.error(f"Unknown section: {section_key}")
        if st.button("← Back to Menu"):
            st.session_state.pop("advisor_prep_current_section", None)
            st.rerun()
