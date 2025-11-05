"""
PFMA v3 - Plan with My Advisor (Booking-First Model)

Enhanced appointment booking with preferences collection:
1. Check prerequisites via MCIP (requires Cost Planner)
2. Show friendly gate if prerequisites missing
3. Single booking form with strict validation
4. Collect customer preferences for CRM matching
5. Publish AdvisorAppointment to MCIP when complete
6. Route to Waiting Room for optional Advisor Prep

Key changes from v2:
- Single step (booking only) vs 5 steps
- Added "More About {Name}" preferences collection
- No verification sections (moved to optional Advisor Prep)
- Enhanced CRM matching data collection
- Booking = complete (no multi-step progress tracking)
"""

import uuid
from datetime import datetime

import streamlit as st

from core.events import log_event
from core.mcip import MCIP, AdvisorAppointment
from core.nav import route_to
from core.navi import render_navi_panel
from core.preferences import PreferencesManager, CustomerPreferences


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

    # Step 2: Check appointment and preferences status
    appt = MCIP.get_advisor_appointment()
    preferences = PreferencesManager.get_preferences()
    
    # Check what screen to show based on state
    show_preferences = (
        appt and appt.scheduled and  # Appointment is booked
        not st.session_state.get("pfma_preferences_complete", False) and  # Preferences not marked complete
        not st.session_state.get("pfma_skip_preferences", False)  # User hasn't chosen to skip
    )
    
    if show_preferences:
        # Show preferences collection screen
        render_navi_panel(location="product", product_key="pfma_v3", module_config=None)
        _render_preferences_collection(appt)
        return
    elif appt and appt.scheduled:
        # Already booked and preferences handled - show confirmation
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

    # Force rerun to show preferences collection (not confirmation yet)
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
# PREFERENCES COLLECTION SCREEN  
# =============================================================================


def _render_preferences_collection(appt: AdvisorAppointment):
    """Render 'More About {Name}' preferences collection screen."""
    
    # Get customer name from profile or appointment
    profile = st.session_state.get("profile", {})
    customer_name = profile.get("name", "you")
    
    # Apply clean CSS
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1200px !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"## More About {customer_name}")
    st.markdown(
        f"**Great! Your appointment is confirmed.** To help your advisor provide the best recommendations, "
        f"please share a bit more about {customer_name}'s preferences and situation."
    )
    
    # Show appointment confirmation briefly
    with st.expander("📅 Your Appointment Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Confirmation:** {appt.confirmation_id}")
            st.markdown(f"**Type:** {appt.type.title()}")
        with col2:
            st.markdown(f"**Preferred Time:** {appt.time}")
            if appt.contact_email:
                st.markdown(f"**Email:** {appt.contact_email}")

    st.markdown("---")

    # Get or create preferences
    preferences = PreferencesManager.get_preferences()
    if not preferences:
        # Create default preferences based on GCP recommendation
        care_rec = MCIP.get_care_recommendation()
        care_tier = care_rec.tier if care_rec else "assisted_living"
        preferences = PreferencesManager.create_default_preferences(care_tier)

    # Form for preferences collection
    st.markdown("### Preferences & Situation")
    
    # Store form data in session state for persistence across reruns
    if "preferences_form" not in st.session_state:
        st.session_state["preferences_form"] = {
            "preferred_regions": preferences.preferred_regions,
            "max_distance": preferences.max_distance_miles,
            "care_environment": preferences.care_environment_preference,
            "move_timeline": preferences.move_timeline,
            "budget_comfort": preferences.budget_comfort_level,
            "activity_preferences": preferences.activity_preferences,
            "family_contact": preferences.primary_family_contact,
            "family_location": preferences.family_location,
            "current_support": preferences.current_support_level,
            "move_triggers": preferences.move_triggers,
        }

    form_data = st.session_state["preferences_form"]

    # Geographic Preferences
    with st.expander("🗺️ **Location & Geographic Preferences**", expanded=True):
        st.markdown("*Help us find communities in the right areas*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            regions = st.multiselect(
                "Preferred regions/areas",
                options=[
                    "bellevue_area", "seattle", "eastside", "north_seattle", "south_seattle",
                    "tacoma", "spokane", "vancouver_wa", "olympia", "everett", "washington_state"
                ],
                default=form_data.get("preferred_regions", []),
                format_func=lambda x: {
                    "bellevue_area": "Bellevue Area",
                    "seattle": "Seattle",
                    "eastside": "Eastside (Bellevue, Redmond, Kirkland)",
                    "north_seattle": "North Seattle",
                    "south_seattle": "South Seattle", 
                    "tacoma": "Tacoma Area",
                    "spokane": "Spokane Area",
                    "vancouver_wa": "Vancouver, WA",
                    "olympia": "Olympia Area",
                    "everett": "Everett Area",
                    "washington_state": "Anywhere in Washington State"
                }.get(x, x.replace("_", " ").title()),
                help="Select areas you'd prefer for community locations"
            )
            form_data["preferred_regions"] = regions
        
        with col2:
            max_distance = st.selectbox(
                "Maximum distance preference",
                options=[None, 5, 10, 15, 25, 50],
                index=[None, 5, 10, 15, 25, 50].index(form_data.get("max_distance")),
                format_func=lambda x: "No preference" if x is None else f"Within {x} miles",
                help="Maximum distance from current location or family"
            )
            form_data["max_distance"] = max_distance

    # Care & Timeline Preferences
    with st.expander("🏠 **Care Level & Timeline**", expanded=True):
        st.markdown("*Help us understand care needs and timing*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            care_env = st.selectbox(
                "Preferred care environment",
                options=["independent", "assisted_living", "memory_care", "in_home", "exploring"],
                index=["independent", "assisted_living", "memory_care", "in_home", "exploring"].index(
                    form_data.get("care_environment", "assisted_living")
                ),
                format_func=lambda x: {
                    "independent": "Independent Living",
                    "assisted_living": "Assisted Living", 
                    "memory_care": "Memory Care",
                    "in_home": "In-Home Care",
                    "exploring": "Still exploring options"
                }.get(x, x.replace("_", " ").title()),
                help="Based on your assessment results and preferences"
            )
            form_data["care_environment"] = care_env
        
        with col2:
            timeline = st.selectbox(
                "Move timeline",
                options=["immediate", "2_4_weeks", "2_3_months", "exploring", "future_planning"],
                index=["immediate", "2_4_weeks", "2_3_months", "exploring", "future_planning"].index(
                    form_data.get("move_timeline", "exploring")
                ),
                format_func=lambda x: {
                    "immediate": "Immediate (within 2 weeks)",
                    "2_4_weeks": "2-4 weeks",
                    "2_3_months": "2-3 months", 
                    "exploring": "Exploring options",
                    "future_planning": "Future planning"
                }.get(x, x.replace("_", " ").title()),
                help="What's your preferred timeline for a potential move?"
            )
            form_data["move_timeline"] = timeline

    # Budget & Lifestyle
    with st.expander("💰 **Budget & Lifestyle Preferences**", expanded=True):
        st.markdown("*Help us find communities that match your needs and budget*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            budget = st.selectbox(
                "Budget comfort level",
                options=["tight", "moderate", "comfortable", "luxury"],
                index=["tight", "moderate", "comfortable", "luxury"].index(
                    form_data.get("budget_comfort", "moderate")
                ),
                format_func=lambda x: {
                    "tight": "Budget-conscious",
                    "moderate": "Moderate budget",
                    "comfortable": "Comfortable budget", 
                    "luxury": "Premium/luxury options"
                }.get(x, x.title()),
                help="What budget range feels most comfortable?"
            )
            form_data["budget_comfort"] = budget
        
        with col2:
            activities = st.multiselect(
                "Activity preferences",
                options=["fitness", "arts", "social", "quiet", "outdoors", "games", "music", "crafts"],
                default=form_data.get("activity_preferences", []),
                format_func=lambda x: {
                    "fitness": "Fitness & Exercise",
                    "arts": "Arts & Crafts",
                    "social": "Social Activities",
                    "quiet": "Quiet Spaces",
                    "outdoors": "Outdoor Activities",
                    "games": "Games & Cards", 
                    "music": "Music & Entertainment",
                    "crafts": "Crafts & Hobbies"
                }.get(x, x.title()),
                help="What types of activities are most appealing?"
            )
            form_data["activity_preferences"] = activities

    # Family & Support Context
    with st.expander("👥 **Family & Support Context**", expanded=True):
        st.markdown("*Help us understand the support system and family involvement*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            family_contact = st.text_input(
                "Primary family contact/decision maker",
                value=form_data.get("family_contact", ""),
                placeholder="e.g., Sarah (daughter), John (son)",
                help="Who is the main family contact or decision maker?"
            )
            form_data["family_contact"] = family_contact
            
            family_location = st.selectbox(
                "Family location",
                options=["nearby", "distant", "out_of_state", "none"],
                index=["nearby", "distant", "out_of_state", "none"].index(
                    form_data.get("family_location", "nearby")
                ),
                format_func=lambda x: {
                    "nearby": "Nearby (within 30 minutes)",
                    "distant": "Distant (1+ hours away)",
                    "out_of_state": "Out of state",
                    "none": "No close family"
                }.get(x, x.replace("_", " ").title()),
                help="Where is the primary family support located?"
            )
            form_data["family_location"] = family_location
        
        with col2:
            current_support = st.selectbox(
                "Current support level",
                options=["independent", "family_help", "hired_care", "minimal"],
                index=["independent", "family_help", "hired_care", "minimal"].index(
                    form_data.get("current_support", "independent")
                ),
                format_func=lambda x: {
                    "independent": "Mostly independent",
                    "family_help": "Some family help",
                    "hired_care": "Has hired care",
                    "minimal": "Minimal support"
                }.get(x, x.replace("_", " ").title()),
                help="What's the current level of support or assistance?"
            )
            form_data["current_support"] = current_support
            
            move_triggers = st.multiselect(
                "What's prompting consideration of a move?",
                options=["safety_concern", "family_worry", "planned_transition", "health_change", "social_isolation", "home_maintenance"],
                default=form_data.get("move_triggers", []),
                format_func=lambda x: {
                    "safety_concern": "Safety concerns",
                    "family_worry": "Family worry/concern",
                    "planned_transition": "Planned life transition",
                    "health_change": "Health changes",
                    "social_isolation": "Social isolation",
                    "home_maintenance": "Home maintenance burden"
                }.get(x, x.replace("_", " ").title()),
                help="What factors are leading to this exploration? (Select all that apply)"
            )
            form_data["move_triggers"] = move_triggers

    st.markdown("---")

    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.caption("This information helps your advisor provide personalized recommendations.")
    
    with col2:
        if st.button("Skip for Now", use_container_width=True):
            # User chose to skip preferences
            st.session_state["pfma_skip_preferences"] = True
            _complete_pfma_process()
            st.rerun()
    
    with col3:
        if st.button("Save & Continue", type="primary", use_container_width=True):
            # Save preferences and mark as complete
            _save_preferences_and_complete(form_data)
            st.rerun()


def _save_preferences_and_complete(form_data: dict):
    """Save preferences and complete PFMA process."""
    
    # Create preferences object
    preferences = CustomerPreferences(
        preferred_regions=form_data.get("preferred_regions", []),
        max_distance_miles=form_data.get("max_distance"),
        care_environment_preference=form_data.get("care_environment", "assisted_living"),
        move_timeline=form_data.get("move_timeline", "exploring"),
        budget_comfort_level=form_data.get("budget_comfort", "moderate"),
        activity_preferences=form_data.get("activity_preferences", []),
        primary_family_contact=form_data.get("family_contact", ""),
        family_location=form_data.get("family_location", "nearby"),
        current_support_level=form_data.get("current_support", "independent"),
        move_triggers=form_data.get("move_triggers", []),
        completion_status="complete",
    )
    
    # Save preferences
    PreferencesManager.save_preferences(preferences)
    
    # Mark preferences as complete
    st.session_state["pfma_preferences_complete"] = True
    
    # Complete PFMA process
    _complete_pfma_process()
    
    # Log preferences completion
    log_event(
        "pfma.preferences.completed",
        {
            "regions_count": len(preferences.preferred_regions),
            "care_environment": preferences.care_environment_preference,
            "timeline": preferences.move_timeline,
            "budget_level": preferences.budget_comfort_level,
            "has_family_contact": bool(preferences.primary_family_contact),
        }
    )


def _complete_pfma_process():
    """Complete the PFMA process and mark as done."""
    # Mark PFMA complete (using canonical key)
    MCIP.mark_product_complete("pfma")
    print("[PFMA] Marked PFMA/My Advisor complete")
    
    # Clear form data
    if "preferences_form" in st.session_state:
        del st.session_state["preferences_form"]


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

    # Show preferences status
    preferences = PreferencesManager.get_preferences()
    if preferences and preferences.completion_status == "complete":
        st.success("✅ **Preferences collected** - Your advisor will have detailed information about your needs and preferences.")
    elif st.session_state.get("pfma_skip_preferences", False):
        st.info("ℹ️ **Preferences skipped** - You can always share more details during your appointment.")

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

