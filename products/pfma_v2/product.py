"""
PFMA v2 - Plan with My Advisor

Universal Product Pattern Implementation:
1. Check prerequisites via MCIP (requires Cost Planner)
2. Show friendly gate if prerequisites missing
3. Run product logic (multi-step appointment booking flow)
4. Publish AdvisorAppointment to MCIP when complete
5. Mark product complete in journey
"""

from datetime import datetime, timedelta
from typing import Optional
import streamlit as st

from core.mcip import MCIP, AdvisorAppointment
from core.nav import route_to


def render():
    """Main entry point for PFMA v2."""
    
    # Step 1: Check prerequisites via MCIP
    if not _check_prerequisites():
        _render_gate()
        return
    
    # Step 2: Initialize PFMA state
    _initialize_state()
    
    # Step 3: Show MCIP context at top
    _render_mcip_context()
    
    # Step 4: Get current step and route
    pfma = st.session_state["pfma_v2"]
    step = pfma.get("step", 0)
    
    # Show duck progress in sidebar
    _render_duck_progress_sidebar()
    
    # Route to appropriate step
    if step == 0:
        _render_intro()
    elif step == 1:
        _render_appointment_booking()
    elif step == 2:
        _render_verify_care_needs()
    elif step == 3:
        _render_verify_household_legal()
    elif step == 4:
        _render_verify_benefits_coverage()
    elif step == 5:
        _render_completion()
    else:
        st.error(f"❌ Unknown step: {step}")
        if st.button("← Return to Hub"):
            route_to("hub_concierge")


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
    
    # Get MCIP context
    care_rec = MCIP.get_care_recommendation()
    financial = MCIP.get_financial_profile()
    
    st.info(
        "**Ready to talk to a live advisor?**\n\n"
        "Before scheduling your appointment, please complete the Cost Planner "
        "so we can help you have the most productive conversation possible."
    )
    
    # Show what user has completed
    st.markdown("#### Your Progress")
    
    if care_rec:
        st.success(f"✅ **Guided Care Plan Complete** - Recommended: {care_rec.tier.replace('_', ' ').title()}")
    else:
        st.warning("⏳ **Guided Care Plan** - Not started")
    
    if financial:
        st.success(f"✅ **Cost Planner Complete** - Monthly estimate: ${financial.estimated_monthly_cost:,.0f}")
    else:
        st.warning("⏳ **Cost Planner** - Not completed")
        st.markdown(
            "👉 **Complete the Cost Planner** to understand your care costs "
            "before meeting with an advisor."
        )
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Hub", use_container_width=True):
            route_to("hub_concierge")
    with col2:
        if not financial:
            if st.button("Start Cost Planner →", type="primary", use_container_width=True):
                route_to("cost_v2")


def _initialize_state():
    """Initialize PFMA v2 state structure."""
    if "pfma_v2" not in st.session_state:
        st.session_state["pfma_v2"] = {
            "step": 0,
            "ducks_earned": 0,
            "appointment": {},
            "verifications": {},
            "published_to_mcip": False
        }


def _render_mcip_context():
    """Show MCIP context at top of page."""
    care_rec = MCIP.get_care_recommendation()
    financial = MCIP.get_financial_profile()
    
    person_name = st.session_state.get("person_name", "your loved one")
    
    if care_rec and financial:
        tier_display = care_rec.tier.replace("_", " ").title()
        cost_display = f"${financial.estimated_monthly_cost:,.0f}/month"
        
        st.info(
            f"**Planning for {person_name}:**  \n"
            f"Care Level: {tier_display} | Estimated Cost: {cost_display}"
        )


# =============================================================================
# DUCK PROGRESS SIDEBAR
# =============================================================================

def _render_duck_progress_sidebar():
    """Show duck progress in sidebar."""
    pfma = st.session_state.get("pfma_v2", {})
    ducks = pfma.get("ducks_earned", 0)
    
    st.sidebar.markdown("### 🦆 Your Progress")
    st.sidebar.markdown(f"**Ducks Earned:** {ducks}/4")
    
    # Visual duck display
    duck_display = "🦆" * ducks + "⚪" * (4 - ducks)
    st.sidebar.markdown(f"### {duck_display}")
    st.sidebar.progress(ducks / 4, text=f"{ducks * 25}% Complete")


# =============================================================================
# STEP RENDERING
# =============================================================================

def _render_intro():
    """Step 0: Intro page."""
    st.markdown("## 🦆 Plan with My Advisor")
    st.markdown("### Welcome! Let's prepare for your advisor consultation.")
    
    person_name = st.session_state.get("person_name", "your loved one")
    
    st.write(
        f"You've completed your Care Plan and Cost Planner — great work! "
        f"Now let's get you ready to meet with a live advisor who can help you "
        f"implement the care plan for {person_name}."
    )
    
    st.markdown("#### What We'll Do:")
    st.markdown("""
    1. 📅 **Book Your Appointment** — Choose your preferred contact method and time
    2. ✅ **Verify Care Needs** — Confirm the care recommendations from your Care Plan
    3. 🏠 **Verify Household & Legal** — Confirm household and legal status
    4. 💰 **Verify Benefits & Coverage** — Confirm insurance and benefits
    
    **Earn a duck 🦆 for each step you complete!**
    """)
    
    if st.button("Let's Get Started →", type="primary", use_container_width=True):
        st.session_state["pfma_v2"]["step"] = 1
        st.rerun()
    
    if st.button("← Back to Hub", use_container_width=True):
        route_to("hub_concierge")


def _render_appointment_booking():
    """Step 1: Book appointment with advisor."""
    st.markdown("## 📅 Book Your Advisor Appointment")
    st.write("Let's schedule a time to connect with your dedicated advisor.")
    
    pfma = st.session_state["pfma_v2"]
    appointment = pfma.get("appointment", {})
    
    # Contact method
    contact_method = st.radio(
        "How would you like to connect?",
        ["Phone Call", "Video Call", "In-Person Meeting"],
        index=["Phone Call", "Video Call", "In-Person Meeting"].index(
            appointment.get("method", "Phone Call")
        )
    )
    
    # Date selection
    st.markdown("#### Preferred Date")
    min_date = datetime.now().date() + timedelta(days=1)
    max_date = datetime.now().date() + timedelta(days=30)
    
    preferred_date = st.date_input(
        "Select your preferred date",
        value=appointment.get("date", min_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Time preference
    time_window = st.selectbox(
        "What time of day works best?",
        ["Morning (9 AM - 12 PM)", "Afternoon (12 PM - 5 PM)", "Evening (5 PM - 8 PM)"],
        index=["Morning (9 AM - 12 PM)", "Afternoon (12 PM - 5 PM)", "Evening (5 PM - 8 PM)"].index(
            appointment.get("time_window", "Morning (9 AM - 12 PM)")
        )
    )
    
    # Contact info
    phone = st.text_input("Phone Number", value=appointment.get("phone", ""))
    email = st.text_input("Email Address", value=appointment.get("email", ""))
    
    # Special requests
    notes = st.text_area(
        "Any special requests or topics you'd like to discuss?",
        value=appointment.get("notes", ""),
        placeholder="e.g., I'd like to discuss Medicaid planning, veteran benefits, etc."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            pfma["step"] = 0
            st.rerun()
    with col2:
        if st.button("Book Appointment →", type="primary", use_container_width=True):
            # Save appointment data
            pfma["appointment"] = {
                "method": contact_method,
                "date": preferred_date.isoformat(),
                "time_window": time_window,
                "phone": phone,
                "email": email,
                "notes": notes
            }
            
            # Award duck if first time
            if pfma.get("ducks_earned", 0) == 0:
                pfma["ducks_earned"] = 1
                st.balloons()
            
            pfma["step"] = 2
            st.rerun()


def _render_verify_care_needs():
    """Step 2: Verify care needs from MCIP."""
    st.markdown("## ✅ Verify Care Needs")
    st.write("Let's confirm the care recommendations from your Guided Care Plan.")
    
    # Get care recommendation from MCIP
    care_rec = MCIP.get_care_recommendation()
    
    if care_rec:
        tier_display = care_rec.tier.replace("_", " ").title()
        st.info(f"**Recommended Care Level:** {tier_display}")
        
        # Show confidence and rationale
        st.markdown(f"**Confidence:** {care_rec.confidence * 100:.0f}%")
        
        if care_rec.rationale:
            with st.expander("📋 View Recommendation Rationale"):
                for reason in care_rec.rationale:
                    st.markdown(f"- {reason}")
    else:
        st.warning("Care recommendation not found. Please complete the Guided Care Plan first.")
    
    pfma = st.session_state["pfma_v2"]
    verifications = pfma.get("verifications", {})
    
    # Verification questions
    st.markdown("#### Please confirm:")
    
    care_confirmed = st.radio(
        "Does this care level still match current needs?",
        ["Yes, this is accurate", "No, needs have changed"],
        index=0 if verifications.get("care_confirmed") == "Yes, this is accurate" else 1
    )
    
    if care_confirmed == "No, needs have changed":
        care_changes = st.text_area(
            "What has changed?",
            value=verifications.get("care_changes", ""),
            placeholder="Describe how care needs have evolved..."
        )
    else:
        care_changes = ""
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            pfma["step"] = 1
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            # Save verification
            if "verifications" not in pfma:
                pfma["verifications"] = {}
            pfma["verifications"]["care_confirmed"] = care_confirmed
            pfma["verifications"]["care_changes"] = care_changes
            
            # Award duck if this is the second step
            if pfma.get("ducks_earned", 0) == 1:
                pfma["ducks_earned"] = 2
                st.balloons()
            
            pfma["step"] = 3
            st.rerun()


def _render_verify_household_legal():
    """Step 3: Verify household and legal status."""
    st.markdown("## 🏠 Verify Household & Legal Status")
    st.write("Let's confirm household situation and legal arrangements.")
    
    pfma = st.session_state["pfma_v2"]
    verifications = pfma.get("verifications", {})
    
    st.markdown("#### Household")
    
    living_situation = st.selectbox(
        "Current living situation:",
        ["Living alone", "Living with spouse/partner", "Living with family", "Assisted living", "Memory care", "Other"],
        index=["Living alone", "Living with spouse/partner", "Living with family", "Assisted living", "Memory care", "Other"].index(
            verifications.get("living_situation", "Living alone")
        )
    )
    
    st.markdown("#### Legal Arrangements")
    
    has_poa = st.radio(
        "Is there a Power of Attorney (POA) in place?",
        ["Yes", "No", "In progress"],
        index=["Yes", "No", "In progress"].index(verifications.get("has_poa", "No"))
    )
    
    has_advance_directive = st.radio(
        "Are advance directives (living will, healthcare proxy) in place?",
        ["Yes", "No", "In progress"],
        index=["Yes", "No", "In progress"].index(verifications.get("has_advance_directive", "No"))
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            pfma["step"] = 2
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            # Save verification
            pfma["verifications"]["living_situation"] = living_situation
            pfma["verifications"]["has_poa"] = has_poa
            pfma["verifications"]["has_advance_directive"] = has_advance_directive
            
            # Award duck if this is the third step
            if pfma.get("ducks_earned", 0) == 2:
                pfma["ducks_earned"] = 3
                st.balloons()
            
            pfma["step"] = 4
            st.rerun()


def _render_verify_benefits_coverage():
    """Step 4: Verify insurance and benefits."""
    st.markdown("## 💰 Verify Benefits & Coverage")
    st.write("Let's confirm insurance and benefits information.")
    
    pfma = st.session_state["pfma_v2"]
    verifications = pfma.get("verifications", {})
    
    st.markdown("#### Insurance")
    
    has_medicare = st.checkbox(
        "Medicare",
        value=verifications.get("has_medicare", False)
    )
    
    has_medicaid = st.checkbox(
        "Medicaid",
        value=verifications.get("has_medicaid", False)
    )
    
    has_ltc_insurance = st.checkbox(
        "Long-term care insurance",
        value=verifications.get("has_ltc_insurance", False)
    )
    
    has_private_insurance = st.checkbox(
        "Private health insurance",
        value=verifications.get("has_private_insurance", False)
    )
    
    st.markdown("#### Veterans Benefits")
    
    is_veteran = st.checkbox(
        "Veteran or surviving spouse",
        value=verifications.get("is_veteran", False)
    )
    
    if is_veteran:
        va_benefits_status = st.selectbox(
            "VA benefits status:",
            ["Not enrolled", "Enrolled but not receiving care benefits", "Receiving care benefits", "Applied - pending"],
            index=["Not enrolled", "Enrolled but not receiving care benefits", "Receiving care benefits", "Applied - pending"].index(
                verifications.get("va_benefits_status", "Not enrolled")
            )
        )
    else:
        va_benefits_status = None
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            pfma["step"] = 3
            st.rerun()
    with col2:
        if st.button("Complete →", type="primary", use_container_width=True):
            # Save verification
            pfma["verifications"]["has_medicare"] = has_medicare
            pfma["verifications"]["has_medicaid"] = has_medicaid
            pfma["verifications"]["has_ltc_insurance"] = has_ltc_insurance
            pfma["verifications"]["has_private_insurance"] = has_private_insurance
            pfma["verifications"]["is_veteran"] = is_veteran
            pfma["verifications"]["va_benefits_status"] = va_benefits_status
            
            # Award final duck
            if pfma.get("ducks_earned", 0) == 3:
                pfma["ducks_earned"] = 4
                st.balloons()
            
            pfma["step"] = 5
            st.rerun()


def _render_completion():
    """Step 5: Completion page with MCIP publishing."""
    st.markdown("## 🎉 You're All Set!")
    st.success("**All 4 ducks earned!** 🦆🦆🦆🦆")
    
    person_name = st.session_state.get("person_name", "your loved one")
    
    st.write(
        f"Thank you for completing your Plan for My Advisor preparation! "
        f"Our team will reach out within 1-2 business days to schedule your consultation about {person_name}'s care."
    )
    
    pfma = st.session_state.get("pfma_v2", {})
    appointment = pfma.get("appointment", {})
    
    # Show appointment details
    st.markdown("#### Your Appointment Request")
    date_str = appointment.get("date", "Not specified")
    if date_str != "Not specified":
        try:
            date_obj = datetime.fromisoformat(date_str)
            date_display = date_obj.strftime("%B %d, %Y")
        except:
            date_display = date_str
    else:
        date_display = date_str
    
    st.info(f"""
    **Contact Method:** {appointment.get('method', 'Not specified')}  
    **Preferred Date:** {date_display}  
    **Preferred Time:** {appointment.get('time_window', 'Not specified')}  
    **Email:** {appointment.get('email', 'Not provided')}  
    {f"**Phone:** {appointment.get('phone', '')}" if appointment.get('phone') else ""}
    """)
    
    if appointment.get("notes"):
        with st.expander("📝 Special Requests"):
            st.write(appointment.get("notes"))
    
    # Publish to MCIP if not already done
    if not pfma.get("published_to_mcip", False):
        _publish_to_mcip()
        pfma["published_to_mcip"] = True
        st.session_state["pfma_v2"] = pfma
    
    st.markdown("#### What's Next?")
    st.markdown("""
    1. **Review your email** — We'll send a confirmation with next steps
    2. **Gather documents** — Have any relevant financial/legal documents ready
    3. **Prepare questions** — Write down any specific questions you have
    4. **Your appointment** — Meet with your dedicated advisor
    """)
    
    # Show MCIP journey summary
    _render_journey_summary()
    
    if st.button("← Return to Hub", type="primary", use_container_width=True):
        route_to("hub_concierge")


# =============================================================================
# MCIP PUBLISHING
# =============================================================================

def _publish_to_mcip():
    """Publish AdvisorAppointment to MCIP when PFMA complete."""
    pfma = st.session_state.get("pfma_v2", {})
    appointment_data = pfma.get("appointment", {})
    
    # Build AdvisorAppointment dataclass
    appointment = AdvisorAppointment(
        scheduled=True,
        date=appointment_data.get("date", ""),
        time=appointment_data.get("time_window", ""),
        type=appointment_data.get("method", "Phone Call").lower().replace(" ", "_"),
        confirmation_id=f"PFMA-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        generated_at=datetime.utcnow().isoformat() + "Z",
        status="scheduled"
    )
    
    # Publish to MCIP
    MCIP.publish_appointment(appointment)
    
    # Mark PFMA as complete in journey
    MCIP.mark_product_complete("pfma")
    
    st.success("✅ Appointment request published to your care plan!")


def _render_journey_summary():
    """Show complete journey summary from MCIP."""
    st.markdown("---")
    st.markdown("#### 🎯 Your Complete Care Plan Journey")
    
    care_rec = MCIP.get_care_recommendation()
    financial = MCIP.get_financial_profile()
    appointment = MCIP.get_advisor_appointment()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### Guided Care Plan")
        if care_rec:
            tier_display = care_rec.tier.replace("_", " ").title()
            st.success(f"✅ {tier_display}")
            st.caption(f"Confidence: {care_rec.confidence * 100:.0f}%")
        else:
            st.info("⏳ Not completed")
    
    with col2:
        st.markdown("##### Cost Planner")
        if financial:
            st.success(f"✅ ${financial.estimated_monthly_cost:,.0f}/month")
            if financial.runway_months > 0:
                st.caption(f"Runway: {financial.runway_months} months")
        else:
            st.info("⏳ Not completed")
    
    with col3:
        st.markdown("##### Advisor Appointment")
        if appointment and appointment.scheduled:
            st.success(f"✅ {appointment.type.replace('_', ' ').title()}")
            st.caption(f"Confirmation: {appointment.confirmation_id}")
        else:
            st.info("⏳ Not scheduled")
    
    # Show journey progress
    progress = MCIP.get_journey_progress()
    completed_count = progress.get("completed_count", 0)
    total_products = 3  # GCP, Cost Planner, PFMA
    
    st.progress(completed_count / total_products, text=f"{completed_count}/{total_products} Products Complete")
