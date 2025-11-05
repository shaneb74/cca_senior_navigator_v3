"""
PFMA v3 - Plan with My Advisor (Booking-First Model)

Simplified single-step appointment booking:
1. Check prerequisites via MCIP (requires Cost Planner)
2. Show friendly gate if prerequisites missing
3. Single booking form with strict validation
4. Publish AdvisorAppointment to MCIP when complete
5. Route to Waiting Room for optional Advisor Prep

Key changes from v2:
- Single step (booking only) vs 5 steps
- No verification sections (moved to optional Advisor Prep)
- Immediate handoff to Waiting Room
- Booking = complete (no multi-step progress tracking)
"""

import uuid
from datetime import datetime

import streamlit as st

from core.events import log_event
from core.mcip import MCIP, AdvisorAppointment
from core.nav import route_to
from core.navi import render_navi_panel


def render():
    """Main entry point for PFMA v3."""

    # Log mount with Cost Planner state
    cost = st.session_state.get("cost", {})
    g = st.session_state.get("gcp", {})

    chosen_path = cost.get("path_choice")
    zip_code = cost.get("inputs", {}).get("zip")
    home_hours = cost.get("home_hours_scalar")
    published_tier = g.get("published_tier")

    print(
        f"[FA_MOUNT] chosen_path={chosen_path} zip={zip_code} "
        f"hours={home_hours} tier={published_tier}"
    )

    # Step 1: Check prerequisites via MCIP
    if not _check_prerequisites():
        # Render Navi for gate screen
        render_navi_panel(location="product", product_key="pfma_v3", module_config=None)
        _render_gate()
        return

    # Step 2: Check if already booked
    appt = MCIP.get_advisor_appointment()
    if appt and appt.scheduled:
        # Already booked - show confirmation and route options
        render_navi_panel(location="product", product_key="pfma_v3", module_config=None)
        _render_confirmation(appt)
        return

    # Step 3: Render Navi panel (single intelligence layer)
    render_navi_panel(location="product", product_key="pfma_v3", module_config=None)

    # Step 4: Render booking form
    _render_booking_form()


# =============================================================================
# PREREQUISITE CHECKING (MCIP Integration)
# =============================================================================


def _check_prerequisites() -> bool:
    """Check if user has completed required products via MCIP.

    Returns:
        True if prerequisites met, False otherwise
    """
    # Require Cost Planner completion
    financial = MCIP.get_financial_profile()
    return financial is not None


def _render_gate():
    """Show friendly gate requiring Cost Planner completion."""
    st.markdown("## 📅 Plan with My Advisor")

    st.info(
        "**Ready to talk to a live advisor?**\n\n"
        "Before scheduling your appointment, please complete the **Cost Planner** "
        "so we can help you have the most productive conversation possible."
    )

    # Show what user has completed
    st.markdown("#### Your Progress")

    care_rec = MCIP.get_care_recommendation()
    financial = MCIP.get_financial_profile()

    col1, col2 = st.columns(2)

    with col1:
        if care_rec:
            st.success("✓ **Guided Care Plan** complete")
        else:
            st.warning("○ Guided Care Plan not started")

    with col2:
        if financial:
            st.success("✓ **Cost Planner** complete")
        else:
            st.error("✗ **Cost Planner required**")

    st.markdown("---")

    if st.button("← Return to Lobby", type="secondary"):
        route_to("hub_lobby")

    if st.button("Go to Cost Planner →", type="primary"):
        # Navigate to Cost Planner v2 auth step (will show fake auth page)
        st.session_state.cost_v2_step = "auth"
        st.query_params["page"] = "cost_v2"
        st.rerun()


# =============================================================================
# BOOKING FORM
# =============================================================================


def _render_booking_form():
    """Render single-step appointment booking form."""

    # Apply clean CSS with proper width constraint
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1000px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## 📅 Schedule Your Consultation")

    st.markdown(
        "Book a **free 30-minute consultation** with a care advisor who will help you "
        "navigate options, coordinate benefits, and connect with trusted partners."
    )

    # Initialize form state with demo data for testing/demos
    if "pfma_v3_form" not in st.session_state:
        # Prepopulate with dummy data for quick testing/demos
        st.session_state["pfma_v3_form"] = {
            "name": "Shane",
            "email": "sarah@example.com",
            "phone": "555-123-4567",
            "timezone": "America/New_York",
            "type": "video",
            "preferred_time": "Morning (8am-12pm)",
            "notes": "",
        }
        log_event("pfma.booking.started", {})

    form_data = st.session_state["pfma_v3_form"]

    # Form fields
    st.markdown("### Your Information")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Full Name *",
            value=form_data.get("name", ""),
            placeholder="Sarah Johnson",
            help="Your name as you'd like the advisor to address you",
        )
        if name != form_data.get("name"):
            form_data["name"] = name
            log_event("pfma.booking.field_edited", {"field": "name"})

    with col2:
        email = st.text_input(
            "Email Address",
            value=form_data.get("email", ""),
            placeholder="sarah@example.com",
            help="We'll send your confirmation here (email OR phone required)",
        )
        if email != form_data.get("email"):
            form_data["email"] = email
            log_event("pfma.booking.field_edited", {"field": "email"})

    col3, col4 = st.columns(2)

    with col3:
        phone = st.text_input(
            "Phone Number",
            value=form_data.get("phone", ""),
            placeholder="555-123-4567",
            help="For appointment reminders (email OR phone required)",
        )
        if phone != form_data.get("phone"):
            form_data["phone"] = phone
            log_event("pfma.booking.field_edited", {"field": "phone"})

    with col4:
        timezone = st.selectbox(
            "Timezone *",
            options=[
                "America/New_York",
                "America/Chicago",
                "America/Denver",
                "America/Los_Angeles",
                "America/Phoenix",
                "America/Anchorage",
                "Pacific/Honolulu",
            ],
            index=0,
            format_func=_format_timezone,
            help="Your local timezone for scheduling",
        )
        if timezone != form_data.get("timezone"):
            form_data["timezone"] = timezone
            log_event("pfma.booking.field_edited", {"field": "timezone"})

    st.markdown("### Appointment Preferences")

    col5, col6 = st.columns(2)

    with col5:
        appointment_type = st.selectbox(
            "Appointment Type *",
            options=["video", "phone"],
            format_func=lambda x: {
                "video": "📹 Video Call",
                "phone": "📞 Phone Call",
            }.get(x, x),
            help="How would you like to meet with your advisor?",
        )
        if appointment_type != form_data.get("type"):
            form_data["type"] = appointment_type
            log_event("pfma.booking.field_edited", {"field": "type"})

    with col6:
        preferred_time = st.selectbox(
            "Preferred Time",
            options=["Morning (8am-12pm)", "Afternoon (12pm-5pm)", "Evening (5pm-8pm)", "Flexible"],
            help="We'll do our best to match your preference",
        )
        if preferred_time != form_data.get("preferred_time"):
            form_data["preferred_time"] = preferred_time
            log_event("pfma.booking.field_edited", {"field": "preferred_time"})

    # Notes field
    notes = st.text_area(
        "Additional Notes (Optional)",
        value=form_data.get("notes", ""),
        placeholder="Any specific topics you'd like to discuss or scheduling constraints...",
        help="Share anything that will help us prepare for your consultation",
        max_chars=500,
    )
    if notes != form_data.get("notes"):
        form_data["notes"] = notes
        log_event("pfma.booking.field_edited", {"field": "notes"})

    # Validation and submit
    st.markdown("---")

    col_submit1, col_submit2 = st.columns([3, 1])

    with col_submit1:
        st.caption("*Required fields. Email OR phone required for confirmation.")

    with col_submit2:
        if st.button("📅 Book Appointment", type="primary", use_container_width=True):
            _handle_booking_submit(form_data)


def _format_timezone(tz: str) -> str:
    """Format timezone for display."""
    tz_map = {
        "America/New_York": "Eastern (ET)",
        "America/Chicago": "Central (CT)",
        "America/Denver": "Mountain (MT)",
        "America/Los_Angeles": "Pacific (PT)",
        "America/Phoenix": "Arizona (MST)",
        "America/Anchorage": "Alaska (AKT)",
        "Pacific/Honolulu": "Hawaii (HST)",
    }
    return tz_map.get(tz, tz)


def _handle_booking_submit(form_data: dict):
    """Validate and process booking submission."""

    # Validate
    is_valid, errors = _validate_booking(form_data)

    if not is_valid:
        # Log validation errors
        log_event("pfma.booking.validation_error", {"errors": errors})

        # Show errors
        for error in errors:
            st.error(f"❌ {error}")
        return

    # Create appointment
    confirmation_id = str(uuid.uuid4())[:8].upper()

    appointment = AdvisorAppointment(
        scheduled=True,
        date=datetime.now().isoformat(),  # Will be updated by scheduling team
        time=form_data.get("preferred_time", "TBD"),
        type=form_data.get("type", "video"),
        confirmation_id=confirmation_id,
        contact_email=form_data.get("email", ""),
        contact_phone=form_data.get("phone", ""),
        timezone=form_data.get("timezone", "America/New_York"),
        notes=form_data.get("notes", ""),
        generated_at=datetime.now().isoformat(),
        status="scheduled",
        prep_sections_complete=[],
        prep_progress=0,
    )

    # Save to MCIP
    MCIP.set_advisor_appointment(appointment)

    # Mark PFMA complete (using canonical key)
    MCIP.mark_product_complete("pfma")
    print("[PFMA] Marked PFMA/My Advisor complete")

    # Log events
    log_event(
        "pfma.booking.submitted",
        {
            "appointment_type": appointment.type,
            "timezone": appointment.timezone,
            "has_email": bool(appointment.contact_email),
            "has_phone": bool(appointment.contact_phone),
        },
    )

    log_event(
        "pfma.appointment.requested", {"confirmation_id": confirmation_id, "type": appointment.type}
    )

    # Clear form
    st.session_state["pfma_v3_form"] = {}

    # Force rerun to show confirmation
    st.rerun()


def _validate_booking(form_data: dict) -> tuple[bool, list[str]]:
    """Validate booking form data.

    Returns:
        (is_valid, errors) tuple
    """
    errors = []

    # Name required
    if not form_data.get("name", "").strip():
        errors.append("Full Name is required")

    # Email OR phone required (not both mandatory)
    email = form_data.get("email", "").strip()
    phone = form_data.get("phone", "").strip()

    if not email and not phone:
        errors.append("Please provide either Email or Phone for confirmation")

    # Email format validation (if provided)
    if email and "@" not in email:
        errors.append("Please provide a valid email address")

    # Timezone required
    if not form_data.get("timezone"):
        errors.append("Timezone is required")

    # Appointment type required
    if not form_data.get("type"):
        errors.append("Appointment type is required")

    return (len(errors) == 0, errors)


# =============================================================================
# CONFIRMATION SCREEN
# =============================================================================


def _render_confirmation(appt: AdvisorAppointment):
    """Render confirmation screen for already-booked appointment."""

    # Apply clean CSS with width constraint
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1000px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Appointment Confirmed")

    st.markdown(f"**Your consultation is scheduled!**\n\nConfirmation ID: **{appt.confirmation_id}**")

    # Appointment details in container
    with st.container():
        st.markdown("### Appointment Details")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Type:** {appt.type.title()}")
            st.markdown(f"**Timezone:** {_format_timezone(appt.timezone)}")
            if appt.contact_email:
                st.markdown(f"**Email:** {appt.contact_email}")

        with col2:
            st.markdown(f"**Status:** {appt.status.title()}")
            st.markdown(f"**Preferred Time:** {appt.time}")
            if appt.contact_phone:
                st.markdown(f"**Phone:** {appt.contact_phone}")

        if appt.notes:
            st.markdown("**Notes:**")
            st.info(appt.notes)

    # Next steps
    st.markdown("### Next Steps")

    st.markdown(
        "**While you wait for your appointment:**\n\n"
        "Visit the **Lobby** to prepare for your consultation. "
        "Complete optional prep sections to help your advisor provide personalized guidance."
    )

    # Action button - End of planning journey
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Return to Lobby", type="primary", use_container_width=True):
            log_event("lobby.return", {"from_product": "pfma_v3"})
            # Mark Planning journey complete
            from core.journeys import mark_journey_complete
            mark_journey_complete("planning")
            route_to("hub_lobby")

