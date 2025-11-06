"""
Care Preparation Product

Post-appointment preparation that branches based on care recommendation:
- Community-based care (AL/MC): Gather preferences for facility matching
- In-home care: Acknowledge care needs as discussion topics

This is a conversational acknowledgment of care flags rather than re-asking questions.
"""

import streamlit as st
from typing import Optional

from core.mcip import MCIP
from core.events import log_event
from core.name_utils import personalize, section_header
from core.navi import render_navi_panel


def render():
    """Main render function for care preparation product."""
    
    # Get care recommendation and determine path
    care_rec = MCIP.get_care_recommendation()
    tier = care_rec.tier if care_rec else None
    flags = st.session_state.get("flags", [])
    
    # Get person name for personalization
    person_name = st.session_state.get("person_name") or st.session_state.get("planning_for_name", "")
    care_recipient_name = st.session_state.get("care_recipient_name", person_name)
    
    # Header
    st.markdown(f"## {section_header('Preparing for Your Consultation')}")
    
    # Branch based on care tier
    if tier in ("assisted_living", "memory_care", "memory_care_high_acuity"):
        _render_community_path(tier, flags, care_recipient_name)
    elif tier in ("in_home", "in_home_care"):
        _render_inhome_path(tier, flags, care_recipient_name)
    else:
        # Fallback for unknown tier
        _render_general_path(tier, care_recipient_name)
    
    # Navi panel for guidance
    render_navi_panel()


def _render_community_path(tier: str, flags: list, person_name: str):
    """Render community-based care preparation (AL/MC facilities)."""
    
    st.markdown(f"""
    ### 🏘️ Finding the Right Community for {person_name}
    
    Your advisor will help you find facilities equipped to provide the care {person_name} needs. 
    Let's gather some preferences to make your consultation more productive.
    """)
    
    # Show what we know from care assessment
    if flags:
        st.markdown("#### 🎯 What Your Advisor Will Focus On")
        st.markdown(personalize(
            "Based on {NAME_POS} care assessment, your advisor will look for communities that can handle:"
        ).replace("{NAME_POS}", f"{person_name}'s"))
        
        focus_areas = _get_community_focus_areas(flags)
        for area in focus_areas:
            st.markdown(f"- {area}")
        
        st.info("✓ Your advisor will match you with communities equipped to handle these specific needs.")
        st.markdown("---")
    
    # Community preferences form
    st.markdown("#### 📍 Your Community Preferences")
    
    with st.form("community_preferences"):
        # Location
        st.markdown("**Where would you like to search?**")
        location = st.text_input(
            "Preferred location",
            value=st.session_state.get("location_preference", ""),
            placeholder="City, state, or 'near family'",
            help="Enter a specific city/state or describe proximity to family"
        )
        
        # Move timeline
        timeline = st.selectbox(
            "When are you hoping to make a move?",
            [
                "Immediately",
                "Within 3 months",
                "Within 6 months",
                "Within 1 year",
                "More than 1 year",
                "Not planning to move"
            ],
            index=0
        )
        
        # Budget (optional)
        st.markdown("**Budget considerations** (optional)")
        col1, col2 = st.columns(2)
        with col1:
            budget_min = st.number_input(
                "Minimum monthly budget",
                min_value=0,
                max_value=20000,
                value=st.session_state.get("budget_min", 3000),
                step=500,
                help="Typical range: $3,000 - $10,000+"
            )
        with col2:
            budget_max = st.number_input(
                "Maximum monthly budget",
                min_value=0,
                max_value=20000,
                value=st.session_state.get("budget_max", 6000),
                step=500,
                help="Your advisor can help identify funding options"
            )
        
        # Priorities
        priorities = st.multiselect(
            "What matters most to you? (Select all that apply)",
            [
                "Cost",
                "Location",
                "Quality of care",
                "Social activities",
                "Medical services",
                "Pet-friendly",
                "Family proximity",
                "Safety/security"
            ],
            default=st.session_state.get("housing_priorities", [])
        )
        
        # Room type preference
        room_preference = st.selectbox(
            "Room preference",
            [
                "Private room",
                "Shared room",
                "No preference"
            ],
            index=0
        )
        
        # Pet considerations
        has_pet = st.checkbox(
            f"Does {person_name} have a pet that needs accommodation?",
            value=st.session_state.get("has_pet", False)
        )
        
        if has_pet:
            pet_details = st.text_input(
                "Pet details",
                placeholder="e.g., Small dog, indoor cat",
                value=st.session_state.get("pet_details", "")
            )
        else:
            pet_details = ""
        
        # Additional notes
        notes = st.text_area(
            "Any other preferences or concerns?",
            value=st.session_state.get("community_notes", ""),
            placeholder="Cultural preferences, special requirements, concerns, etc.",
            help="Your advisor will review these before your consultation"
        )
        
        submitted = st.form_submit_button("Save Preferences", type="primary", use_container_width=True)
        
        if submitted:
            # Save preferences to session and MCIP
            preferences = {
                "care_type": "community",
                "tier": tier,
                "location": location,
                "timeline": timeline,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "priorities": priorities,
                "room_preference": room_preference,
                "has_pet": has_pet,
                "pet_details": pet_details if has_pet else "",
                "notes": notes
            }
            
            # Save to session state
            st.session_state["care_prep_preferences"] = preferences
            st.session_state["location_preference"] = location
            st.session_state["move_timeline"] = timeline
            st.session_state["budget_min"] = budget_min
            st.session_state["budget_max"] = budget_max
            st.session_state["housing_priorities"] = priorities
            st.session_state["has_pet"] = has_pet
            st.session_state["pet_details"] = pet_details
            st.session_state["community_notes"] = notes
            
            # Save to MCIP for advisor review
            _save_to_mcip(preferences)
            
            # Log event
            log_event("care_prep.community_preferences_saved", preferences)
            
            st.success("✅ Preferences saved! Your advisor will review these before your consultation.")
            st.balloons()
            
            # Mark product complete
            MCIP.mark_product_complete("care_prep")
            
            st.markdown("---")
            st.markdown("### What's Next?")
            st.info("Your advisor will use these preferences to prepare a personalized list of recommended communities.")
    
    # Navigation button (outside form to avoid API exception)
    if st.session_state.get("care_prep_complete", False):
        st.markdown("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("← Back to Hub", use_container_width=True):
                from core.nav import route_to
                route_to("hub_lobby")


def _render_inhome_path(tier: str, flags: list, person_name: str):
    """Render in-home care preparation (acknowledgment-based)."""
    
    st.markdown(f"""
    ### 🏡 Preparing for In-Home Care for {person_name}
    
    Your advisor will help you set up the right care and support systems at home. 
    Based on your care assessment, here's what you'll discuss during your consultation.
    """)
    
    # Show discussion topics based on flags (non-interrogative)
    if flags:
        st.markdown("#### 💡 Discussion Topics with Your Advisor")
        
        discussion_topics = _get_inhome_discussion_topics(flags)
        
        if discussion_topics:
            st.markdown(personalize(
                "Your advisor will help you address these areas for {NAME}:"
            ).replace("{NAME}", person_name))
            
            for topic in discussion_topics:
                st.markdown(f"- {topic}")
            
            st.success("✓ Your advisor will help you address each of these areas with practical solutions.")
        else:
            st.markdown("Your advisor will discuss comprehensive in-home care options tailored to your situation.")
        
        st.markdown("---")
    
    # Simple preferences form (lighter than community path)
    st.markdown("#### 📋 A Few Quick Details")
    
    with st.form("inhome_preferences"):
        # Location (for caregiver availability)
        location = st.text_input(
            "What area will care be provided?",
            value=st.session_state.get("location_preference", ""),
            placeholder="City, state",
            help="Helps your advisor identify available caregivers in your area"
        )
        
        # Timeline
        timeline = st.selectbox(
            "When do you need care to start?",
            [
                "Immediately",
                "Within 3 months",
                "Within 6 months",
                "Within 1 year",
                "More than 1 year",
                "Just exploring options"
            ],
            index=0
        )
        
        # Budget awareness
        budget_known = st.radio(
            "Do you have a monthly budget in mind?",
            ["Yes, I have a budget range", "No, I need help understanding costs"],
            index=1
        )
        
        if budget_known == "Yes, I have a budget range":
            col1, col2 = st.columns(2)
            with col1:
                budget_min = st.number_input(
                    "Minimum monthly budget",
                    min_value=0,
                    max_value=20000,
                    value=st.session_state.get("budget_min", 2000),
                    step=500
                )
            with col2:
                budget_max = st.number_input(
                    "Maximum monthly budget",
                    min_value=0,
                    max_value=20000,
                    value=st.session_state.get("budget_max", 5000),
                    step=500
                )
        else:
            budget_min = 0
            budget_max = 0
        
        # Current support
        current_support = st.selectbox(
            f"Does {person_name} currently have any caregiving support?",
            [
                "No support currently",
                "Family provides some help",
                "Professional caregiver (part-time)",
                "Professional caregiver (full-time)",
                "Other"
            ]
        )
        
        # Additional notes
        notes = st.text_area(
            "Any specific concerns or priorities?",
            value=st.session_state.get("inhome_notes", ""),
            placeholder="Specific times needed, special requirements, concerns, etc.",
            help="Your advisor will review these before your consultation"
        )
        
        submitted = st.form_submit_button("Save Details", type="primary", use_container_width=True)
        
        if submitted:
            # Save preferences to session and MCIP
            preferences = {
                "care_type": "in_home",
                "tier": tier,
                "location": location,
                "timeline": timeline,
                "budget_known": budget_known == "Yes, I have a budget range",
                "budget_min": budget_min,
                "budget_max": budget_max,
                "current_support": current_support,
                "notes": notes
            }
            
            # Save to session state
            st.session_state["care_prep_preferences"] = preferences
            st.session_state["location_preference"] = location
            st.session_state["move_timeline"] = timeline
            st.session_state["budget_min"] = budget_min
            st.session_state["budget_max"] = budget_max
            st.session_state["inhome_notes"] = notes
            
            # Save to MCIP for advisor review
            _save_to_mcip(preferences)
            
            # Log event
            log_event("care_prep.inhome_preferences_saved", preferences)
            
            st.success("✅ Details saved! Your advisor will review these before your consultation.")
            st.balloons()
            
            # Mark product complete
            MCIP.mark_product_complete("care_prep")
            
            st.markdown("---")
            st.markdown("### What's Next?")
            st.info("Your advisor will prepare a customized care plan and caregiver options for your consultation.")
    
    # Navigation button (outside form to avoid API exception)
    if st.session_state.get("care_prep_complete", False):
        st.markdown("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("← Back to Hub", use_container_width=True):
                from core.nav import route_to
                route_to("hub_lobby")


def _render_general_path(tier: Optional[str], person_name: str):
    """Fallback for unknown care tier."""
    
    st.markdown(f"""
    ### 📋 Preparing for Your Consultation
    
    Your advisor will help you explore care options for {person_name}. 
    Let's gather a few details to make your consultation more productive.
    """)
    
    with st.form("general_preferences"):
        location = st.text_input(
            "Preferred location for care",
            value=st.session_state.get("location_preference", ""),
            placeholder="City, state"
        )
        
        timeline = st.selectbox(
            "Timeline for making decisions",
            [
                "Immediately",
                "Within 3 months",
                "Within 6 months",
                "Within 1 year",
                "More than 1 year",
                "Just exploring options"
            ],
            index=5
        )
        
        notes = st.text_area(
            "What would you like to discuss with your advisor?",
            placeholder="Questions, concerns, priorities, etc."
        )
        
        submitted = st.form_submit_button("Save Details", type="primary", use_container_width=True)
        
        if submitted:
            preferences = {
                "care_type": "general",
                "tier": tier or "unknown",
                "location": location,
                "timeline": timeline,
                "notes": notes
            }
            
            st.session_state["care_prep_preferences"] = preferences
            _save_to_mcip(preferences)
            
            log_event("care_prep.general_preferences_saved", preferences)
            
            st.success("✅ Details saved!")
            MCIP.mark_product_complete("care_prep")
    
    # Navigation button (outside form to avoid API exception)
    if st.session_state.get("care_prep_complete", False):
        st.markdown("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("← Back to Hub", use_container_width=True):
                from core.nav import route_to
                route_to("hub_lobby")


def _get_community_focus_areas(flags: list) -> list:
    """Convert care flags to community focus areas."""
    areas = []
    
    # Cognitive care
    if any(f in flags for f in ["cog_moderate", "cog_severe", "moderate_cognitive_decline", "memory_care_dx"]):
        areas.append("**Memory care support** with specialized cognitive programs and secure environments")
    
    # Medication management
    if any(f in flags for f in ["medication_management", "med_complexity"]):
        areas.append("**Professional medication management** with trained nursing staff")
    
    # Mobility and falls
    if any(f in flags for f in ["mobility_limited", "fall_risk", "falls_multiple"]):
        areas.append("**Fall prevention and mobility assistance** with accessible layouts and support equipment")
    
    # Behavioral/wandering
    if any(f in flags for f in ["behavioral_concerns", "wandering_risk"]):
        areas.append("**Secure environment** with behavioral health support and monitoring")
    
    # High ADL needs
    if any(f in flags for f in ["adl_support_high", "multiple_adl_limitations"]):
        areas.append("**Comprehensive personal care assistance** with trained caregivers available 24/7")
    
    # Social isolation / support needs
    if any(f in flags for f in ["no_support", "limited_support", "caregiver_strain"]):
        areas.append("**Active social community** with engaging activities and family support programs")
    
    return areas


def _get_inhome_discussion_topics(flags: list) -> list:
    """Convert care flags to in-home discussion topics."""
    topics = []
    
    # Medication management
    if any(f in flags for f in ["medication_management", "med_complexity"]):
        topics.append("**Medication management** – Setting up reliable systems and professional oversight")
    
    # Cognitive support
    if any(f in flags for f in ["cog_moderate", "cog_severe", "moderate_cognitive_decline", "memory_care_dx"]):
        topics.append("**Cognitive support** – Memory aids, routines, and caregiver training for dementia care")
    
    # Mobility and safety
    if any(f in flags for f in ["mobility_limited", "fall_risk", "falls_multiple"]):
        topics.append("**Home safety modifications** – Fall prevention, assistive devices, and accessibility improvements")
    
    # Behavioral support
    if any(f in flags for f in ["behavioral_concerns", "wandering_risk"]):
        topics.append("**Behavioral health support** – Specialized training for caregivers and monitoring systems")
    
    # ADL assistance
    if any(f in flags for f in ["adl_support_high", "multiple_adl_limitations"]):
        topics.append("**Personal care assistance** – Finding qualified caregivers for bathing, dressing, and daily activities")
    
    # Caregiver support
    if any(f in flags for f in ["no_support", "limited_support", "caregiver_strain"]):
        topics.append("**Caregiver coordination** – Building a support network and respite care options")
    
    # Nutrition
    if "nutrition_support" in flags:
        topics.append("**Meal preparation support** – Nutrition planning and specialized dietary needs")
    
    return topics


def _save_to_mcip(preferences: dict):
    """Save care prep preferences to MCIP for advisor review."""
    
    # Get existing appointment
    appt = MCIP.get_advisor_appointment()
    if appt:
        # Store preferences in appointment notes for advisor
        if not appt.notes:
            appt.notes = ""
        
        # Format preferences for advisor
        pref_summary = "\n\n--- Care Preparation Preferences ---\n"
        pref_summary += f"Care Type: {preferences.get('care_type', 'unknown')}\n"
        pref_summary += f"Location: {preferences.get('location', 'Not specified')}\n"
        pref_summary += f"Timeline: {preferences.get('timeline', 'Not specified')}\n"
        
        if preferences.get('budget_min') and preferences.get('budget_max'):
            pref_summary += f"Budget: ${preferences['budget_min']:,} - ${preferences['budget_max']:,}/month\n"
        
        if preferences.get('priorities'):
            pref_summary += f"Priorities: {', '.join(preferences['priorities'])}\n"
        
        if preferences.get('room_preference'):
            pref_summary += f"Room: {preferences['room_preference']}\n"
        
        if preferences.get('has_pet'):
            pref_summary += f"Pet: {preferences.get('pet_details', 'Yes')}\n"
        
        if preferences.get('current_support'):
            pref_summary += f"Current Support: {preferences['current_support']}\n"
        
        if preferences.get('notes'):
            pref_summary += f"Notes: {preferences['notes']}\n"
        
        appt.notes = (appt.notes or "") + pref_summary
        MCIP.set_advisor_appointment(appt)
    
    # Also store in session for other products to access
    st.session_state["care_prep_complete"] = True
