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
from core.crm_ids import convert_to_customer, get_crm_status


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

    # Initialize form state with contextual prefill from Welcome/Audience
    if "pfma_v3_form" not in st.session_state:
        # Get context from session state
        relationship_type = st.session_state.get("relationship_type", "")
        person_name = st.session_state.get("person_name") or st.session_state.get("planning_for_name", "")
        planning_for = st.session_state.get("planning_for_relationship", "")
        
        # Determine if planning for self
        is_self = (
            relationship_type == "Myself" or 
            planning_for == "self" or
            relationship_type == "Self"
        )
        
        # Set defaults based on context
        if is_self:
            # User is care recipient
            default_relation = "Self"
            default_attendee = person_name if person_name else ""
            default_care_recipient = person_name if person_name else ""
        else:
            # User is helping someone else
            default_relation = relationship_type if relationship_type and relationship_type != "Myself" else "Daughter/Son"
            default_attendee = ""  # We don't know attendee name yet
            default_care_recipient = person_name if person_name else ""
        
        st.session_state["pfma_v3_form"] = {
            "attendee_name": default_attendee,
            "relation": default_relation,
            "care_recipient_name": default_care_recipient,
            "email": "",
            "phone": "",
            "timezone": "America/New_York",
            "type": "video",
            "preferred_time": "Morning (8am-12pm)",
            "notes": "",
        }
        log_event("pfma.booking.started", {"is_self": is_self, "prefilled": bool(person_name)})

    form_data = st.session_state["pfma_v3_form"]

    # Form fields
    st.markdown("### Your Information")
    
    st.caption("💡 *Pre-filled from earlier answers — you can edit if this isn't right.*")
    
    # Debug: Show current form data and option to clear
    if st.checkbox("🔧 Debug: Show form data", help="Developer option to inspect form state"):
        st.json(form_data)
        if st.button("Clear Form Data", help="Clear cached form data for testing"):
            st.session_state["pfma_v3_form"] = {}
            st.rerun()

    # Who will attend the appointment?
    st.markdown("**Who will we be talking to during this appointment?** *")
    col1, col2 = st.columns(2)
    
    with col1:
        attendee_first = st.text_input(
            "First Name",
            value=form_data.get("attendee_first", ""),
            placeholder="First name",
            help="Attendee's first name",
            key="attendee_first"
        )
        if attendee_first != form_data.get("attendee_first"):
            form_data["attendee_first"] = attendee_first
            log_event("pfma.booking.field_edited", {"field": "attendee_first"})
    
    with col2:
        attendee_last = st.text_input(
            "Last Name",
            value=form_data.get("attendee_last", ""),
            placeholder="Last name",
            help="Attendee's last name",
            key="attendee_last"
        )
        if attendee_last != form_data.get("attendee_last"):
            form_data["attendee_last"] = attendee_last
            log_event("pfma.booking.field_edited", {"field": "attendee_last"})
    
    # Combine for display
    attendee_name = f"{attendee_first} {attendee_last}".strip()
    form_data["attendee_name"] = attendee_name
    
    relation = st.selectbox(
        "Relation to the person needing care *",
        options=["Self", "Spouse/Partner", "Daughter/Son", "Other Family", "Friend/Advocate", "Professional"],
        index=["Self", "Spouse/Partner", "Daughter/Son", "Other Family", "Friend/Advocate", "Professional"].index(
            form_data.get("relation", "Self")
        ) if form_data.get("relation") in ["Self", "Spouse/Partner", "Daughter/Son", "Other Family", "Friend/Advocate", "Professional"] else 0,
        help="Your relationship to the care recipient",
    )
    if relation != form_data.get("relation"):
        form_data["relation"] = relation
        log_event("pfma.booking.field_edited", {"field": "relation"})
    
    # Conditional: Show care recipient name if relation != Self
    if relation != "Self":
        st.markdown("**Name of the person needing care** *")
        st.caption("🔒 *We'll never contact this person without your consent.*")
        
        col1a, col2a = st.columns(2)
        with col1a:
            care_recipient_first = st.text_input(
                "First Name",
                value=form_data.get("care_recipient_first", ""),
                placeholder="First name",
                help="Care recipient's first name",
                key="care_recipient_first"
            )
            if care_recipient_first != form_data.get("care_recipient_first"):
                form_data["care_recipient_first"] = care_recipient_first
                log_event("pfma.booking.field_edited", {"field": "care_recipient_first"})
        
        with col2a:
            care_recipient_last = st.text_input(
                "Last Name",
                value=form_data.get("care_recipient_last", ""),
                placeholder="Last name",
                help="Care recipient's last name",
                key="care_recipient_last"
            )
            if care_recipient_last != form_data.get("care_recipient_last"):
                form_data["care_recipient_last"] = care_recipient_last
                log_event("pfma.booking.field_edited", {"field": "care_recipient_last"})
        
        # Combine for display
        care_recipient_name = f"{care_recipient_first} {care_recipient_last}".strip()
        form_data["care_recipient_name"] = care_recipient_name
    else:
        # If Self, attendee and care recipient are the same
        form_data["care_recipient_first"] = attendee_first
        form_data["care_recipient_last"] = attendee_last
        form_data["care_recipient_name"] = attendee_name

    st.markdown("---")

    # Contact Information
    col3, col4 = st.columns(2)

    with col3:
        email = st.text_input(
            "Email Address",
            value=form_data.get("email", ""),
            placeholder="sarah@example.com",
            help="We'll send your confirmation here (email OR phone required)",
        )
        if email != form_data.get("email"):
            form_data["email"] = email
            log_event("pfma.booking.field_edited", {"field": "email"})

    with col4:
        phone = st.text_input(
            "Phone Number",
            value=form_data.get("phone", ""),
            placeholder="555-123-4567",
            help="For appointment reminders (email OR phone required)",
        )
        if phone != form_data.get("phone"):
            form_data["phone"] = phone
            log_event("pfma.booking.field_edited", {"field": "phone"})

    # Timezone
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

    # Convert to customer in CRM (appointment booking makes them a customer)
    try:
        # Get name components
        care_recipient_first = form_data.get("care_recipient_first", "").strip()
        care_recipient_last = form_data.get("care_recipient_last", "").strip()
        attendee_first = form_data.get("attendee_first", "").strip()
        attendee_last = form_data.get("attendee_last", "").strip()
        relation = form_data.get("relation", "Self")
        contact_email = form_data.get("email", "").strip() or None
        contact_phone = form_data.get("phone", "").strip() or None
        
        # Use care recipient name for CRM record (first + last)
        if care_recipient_first or care_recipient_last:
            crm_first = care_recipient_first or "Unknown"
            crm_last = care_recipient_last or "Unknown"
        else:
            crm_first = attendee_first or "Unknown"
            crm_last = attendee_last or "Unknown"
        
        crm_name = f"{crm_first} {crm_last}".strip()
        
        # If still no name, use a fallback
        if crm_name == "Unknown Unknown" or not crm_name:
            crm_name = f"Appointment-{confirmation_id}"
        
        print(f"[PFMA] Converting to customer: '{crm_name}' (relation: '{relation}')")
        
        customer_id = convert_to_customer(
            name=crm_name,
            email=contact_email,
            phone=contact_phone,
            source="appointment_booking"
        )
        crm_status = get_crm_status()
        print(f"[PFMA] Appointment booked - CRM Status: {crm_status}")
    except Exception as e:
        print(f"[PFMA] CRM conversion failed: {e}")
        # Don't fail the booking if CRM has issues

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

    # Attendee first name required
    if not form_data.get("attendee_first", "").strip():
        errors.append("Attendee first name is required")
    
    # Attendee last name required
    if not form_data.get("attendee_last", "").strip():
        errors.append("Attendee last name is required")

    # Relation required
    if not form_data.get("relation"):
        errors.append("Relationship to care recipient is required")

    # Care recipient name required if relation != Self
    relation = form_data.get("relation", "Self")
    if relation != "Self":
        if not form_data.get("care_recipient_first", "").strip():
            errors.append("Care recipient's first name is required")
        if not form_data.get("care_recipient_last", "").strip():
            errors.append("Care recipient's last name is required")

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

    st.markdown("---")
    
    # Post-booking branching based on care type
    care_rec = MCIP.get_care_recommendation()
    tier = care_rec.tier if care_rec else None
    flags = st.session_state.get("flags", [])
    
    if tier in ("assisted_living", "memory_care", "memory_care_high_acuity"):
        # Community-based care path
        st.markdown("### 🏘️ Preparing for Your Consultation")
        
        st.write(
            "Your advisor will help you find communities that match your needs. "
            "Based on your care assessment, we'll focus on facilities that can provide:"
        )
        
        # Acknowledge care flags conversationally
        focus_areas = []
        if any(f in flags for f in ["cog_moderate", "cog_severe", "moderate_cognitive_decline", "memory_care_dx"]):
            focus_areas.append("**Memory care support** with specialized cognitive programs")
        if any(f in flags for f in ["medication_management", "med_complexity"]):
            focus_areas.append("**Professional medication management** with trained nursing staff")
        if any(f in flags for f in ["mobility_limited", "fall_risk", "falls_multiple"]):
            focus_areas.append("**Enhanced mobility support** and fall prevention measures")
        if any(f in flags for f in ["behavioral_concerns", "wandering_risk"]):
            focus_areas.append("**Secure environments** with behavioral support")
        if any(f in flags for f in ["adl_support_high", "multiple_adl_limitations"]):
            focus_areas.append("**Comprehensive personal care** assistance with daily activities")
        
        if focus_areas:
            for area in focus_areas:
                st.markdown(f"- {area}")
            st.markdown("")
            st.success("✓ Your advisor will match you with communities equipped to handle these specific needs.")
        else:
            st.markdown("- **Quality care services** tailored to your specific situation")
            st.markdown("- **Safe, comfortable living** environments")
        
        st.markdown("")
        st.info(
            "💡 **Come prepared** to discuss location preferences, budget considerations, "
            "and any questions about community amenities or care levels."
        )
        
    elif tier in ("in_home", "in_home_care"):
        # In-home care path
        st.markdown("### 🏡 Preparing for Your Consultation")
        
        st.write(
            "Your advisor will help you set up in-home care that keeps you safe and comfortable. "
            "Based on your care assessment, be prepared to discuss:"
        )
        
        # Acknowledge care flags conversationally
        discussion_topics = []
        if any(f in flags for f in ["medication_management", "med_complexity"]):
            discussion_topics.append("**Medication management** – Setting up reliable systems for complex medication schedules")
        if any(f in flags for f in ["cog_moderate", "cognitive_decline"]):
            discussion_topics.append("**Cognitive support** – Memory aids and routines to maintain independence")
        if any(f in flags for f in ["mobility_limited", "fall_risk", "falls_multiple"]):
            discussion_topics.append("**Home safety modifications** – Fall prevention and mobility equipment")
        if any(f in flags for f in ["no_support", "limited_support", "caregiver_strain"]):
            discussion_topics.append("**Building your support network** – Professional caregivers and family coordination")
        if any(f in flags for f in ["adl_support_high", "multiple_adl_limitations"]):
            discussion_topics.append("**Personal care assistance** – Help with bathing, dressing, and daily activities")
        if any(f in flags for f in ["nutrition_risk", "meal_prep_difficulty"]):
            discussion_topics.append("**Meal preparation and nutrition** – Ensuring proper nutrition and hydration")
        
        if discussion_topics:
            for topic in discussion_topics:
                st.markdown(f"- {topic}")
            st.markdown("")
            st.success("✓ Your advisor will help you address each of these areas with practical solutions.")
        else:
            st.markdown("- **Home accessibility** and safety considerations")
            st.markdown("- **Caregiver support** and scheduling")
            st.markdown("- **Daily living assistance** options")
        
        st.markdown("")
        st.info(
            "💡 **Think about** your daily routines, who can help regularly, "
            "and any concerns about staying safe at home. Your advisor will create a personalized plan."
        )

    # Next steps - Route to care prep or back to hub
    st.markdown("### What's Next")

    # Check if care_prep is appropriate
    if tier in ("assisted_living", "memory_care", "memory_care_high_acuity", "in_home", "in_home_care"):
        st.markdown(
            "**Let's gather a few preferences** to make your consultation more productive. "
            "This will only take a few minutes and will help your advisor prepare personalized recommendations."
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Continue to Preferences →", type="primary", use_container_width=True):
                log_event("pfma.route_to_care_prep", {"tier": tier})
                route_to("care_prep")
        
        st.markdown("")
        st.caption("Or skip this step and return to the Lobby – your advisor will still contact you within 24 hours.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Skip & Return to Lobby", use_container_width=True):
                log_event("lobby.return", {"from_product": "pfma_v3", "skipped_care_prep": True})
                # Mark Planning journey complete
                from core.journeys import mark_journey_complete
                mark_journey_complete("planning")
                route_to("hub_lobby")
    else:
        # No care prep needed for general/unknown tier
        st.markdown(
            "**One of our advisors will contact you within the next 24 hours** to confirm your consultation time. "
            "In the meantime, feel free to explore additional resources in the Lobby."
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

