"""
Plan for My Advisor (PFMA) Product

Multi-step flow that transitions users from self-guided planning to advisor consultation:
0. Intro - Welcome and overview
1. Appointment Booking - Schedule advisor call (Duck 1)
2. Verify Care Needs - Confirm care preferences (Duck 2)
3. Verify Household/Legal - Confirm household and legal status (Duck 3)
4. Verify Benefits/Coverage - Confirm insurance and benefits (Duck 4)
5. Completion - All done!
"""

import streamlit as st

from core.nav import route_to


def render():
    """Main entry point for PFMA product."""
    
    # Initialize PFMA state
    if "pfma" not in st.session_state:
        st.session_state["pfma"] = {
            "step": 0,
            "ducks_earned": 0,
            "appointment": {},
            "verifications": {}
        }
    
    # Check if user completed Cost Planner (gate condition)
    cost_planner_progress = float(st.session_state.get("cost_planner", {}).get("progress", 0))
    
    if cost_planner_progress < 100:
        _render_cost_planner_gate()
        return
    
    # Get current step
    pfma = st.session_state["pfma"]
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


def _render_cost_planner_gate():
    """Show gate requiring Cost Planner completion."""
    st.markdown("## 🚧 Cost Planner Required")
    st.info(
        "**Before planning with an Advisor, please complete the Cost Planner.**\n\n"
        "The Cost Planner helps you understand your care costs and prepares you "
        "for a more productive conversation with your Advisor."
    )
    
    cost_planner_progress = float(st.session_state.get("cost_planner", {}).get("progress", 0))
    if cost_planner_progress > 0:
        st.progress(cost_planner_progress / 100, text=f"Cost Planner Progress: {cost_planner_progress:.0f}%")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Hub", use_container_width=True):
            route_to("hub_concierge")
    with col2:
        if st.button("Continue Cost Planner →", type="primary", use_container_width=True):
            route_to("cost")


def _render_duck_progress_sidebar():
    """Show duck progress in sidebar."""
    pfma = st.session_state.get("pfma", {})
    ducks = pfma.get("ducks_earned", 0)
    
    st.sidebar.markdown("### 🦆 Your Progress")
    st.sidebar.markdown(f"**Ducks Earned:** {ducks}/4")
    
    # Visual duck display
    duck_display = "🦆" * ducks + "⚪" * (4 - ducks)
    st.sidebar.markdown(f"### {duck_display}")
    st.sidebar.progress(ducks / 4, text=f"{ducks * 25}% Complete")


def _render_intro():
    """Step 0: Intro page."""
    st.markdown("## 🦆 Plan for My Advisor")
    st.markdown("### Welcome! Let's prepare for your advisor consultation.")
    
    st.write(
        "You've completed your Cost Planner — great work! Now let's get you ready "
        "to meet with a live advisor who can help you implement your care plan."
    )
    
    st.markdown("#### What We'll Do:")
    st.markdown("""
    1. 📅 **Book Your Appointment** — Choose your preferred contact method and time
    2. ✅ **Verify Care Needs** — Confirm the care recommendations from your Care Plan
    3. 🏠 **Verify Household & Legal** — Confirm your household and legal status
    4. 💰 **Verify Benefits & Coverage** — Confirm your insurance and benefits
    
    **Earn a duck 🦆 for each step you complete!**
    """)
    
    if st.button("Let's Get Started →", type="primary", use_container_width=True):
        st.session_state["pfma"]["step"] = 1
        st.rerun()
    
    if st.button("← Back to Hub", use_container_width=True):
        route_to("hub_concierge")


def _render_appointment_booking():
    """Step 1: Book appointment with advisor."""
    st.markdown("## 📅 Book Your Advisor Appointment")
    st.write("Let's schedule a time to connect with your dedicated advisor.")
    
    pfma = st.session_state["pfma"]
    appointment = pfma.get("appointment", {})
    
    # Ensure stored method matches available options
    current_method = appointment.get("method", "Phone Call")
    if current_method not in {"Phone Call", "Video Call"}:
        current_method = "Phone Call"
    
    # Contact method
    contact_method = st.radio(
        "How would you like to connect?",
        ["Phone Call", "Video Call"],
        index=["Phone Call", "Video Call"].index(current_method)
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
        placeholder="e.g., I'd like to discuss Medicaid planning..."
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
    """Step 2: Verify care needs from GCP."""
    st.markdown("## ✅ Verify Care Needs")
    st.write("Let's confirm the care recommendations from your Guided Care Plan.")
    
    # Get GCP recommendation
    gcp = st.session_state.get("gcp", {})
    recommendation = gcp.get("recommendation", {})
    care_type = recommendation.get("care_type", "Not specified")
    
    st.info(f"**Recommended Care Level:** {care_type}")
    
    pfma = st.session_state["pfma"]
    verifications = pfma.get("verifications", {})
    
    # Verification questions
    st.markdown("#### Please confirm:")
    
    care_confirmed = st.radio(
        "Does this care level still match your loved one's current needs?",
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
    st.write("Let's confirm your household situation and legal arrangements.")
    
    pfma = st.session_state["pfma"]
    verifications = pfma.get("verifications", {})
    
    # Get data from Cost Planner if available
    cost_planner = st.session_state.get("cost_planner", {})
    profile = cost_planner.get("profile", {})
    
    st.markdown("#### Household")
    
    living_situation = st.selectbox(
        "Current living situation:",
        ["Living alone", "Living with spouse/partner", "Living with family", "Assisted living", "Other"],
        index=["Living alone", "Living with spouse/partner", "Living with family", "Assisted living", "Other"].index(
            verifications.get("living_situation", profile.get("living_situation", "Living alone"))
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
    st.write("Let's confirm your insurance and benefits information.")
    
    pfma = st.session_state["pfma"]
    verifications = pfma.get("verifications", {})
    
    # Get data from Cost Planner if available
    cost_planner = st.session_state.get("cost_planner", {})
    profile = cost_planner.get("profile", {})
    
    st.markdown("#### Insurance")
    
    has_medicare = st.checkbox(
        "Medicare",
        value=verifications.get("has_medicare", profile.get("has_medicare", False))
    )
    
    has_medicaid = st.checkbox(
        "Medicaid",
        value=verifications.get("has_medicaid", profile.get("has_medicaid", False))
    )
    
    has_ltc_insurance = st.checkbox(
        "Long-term care insurance",
        value=verifications.get("has_ltc_insurance", profile.get("has_ltc_insurance", False))
    )
    
    st.markdown("#### Veterans Benefits")
    
    is_veteran = st.checkbox(
        "Veteran or surviving spouse",
        value=verifications.get("is_veteran", profile.get("is_veteran", False))
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
            pfma["verifications"]["is_veteran"] = is_veteran
            pfma["verifications"]["va_benefits_status"] = va_benefits_status
            
            # Award final duck
            if pfma.get("ducks_earned", 0) == 3:
                pfma["ducks_earned"] = 4
                st.balloons()
            
            pfma["step"] = 5
            st.rerun()


def _render_completion():
    """Step 5: Completion page."""
    st.markdown("## 🎉 You're All Set!")
    st.success("**All 4 ducks earned!** 🦆🦆🦆🦆")
    
    st.write(
        "Thank you for completing your Plan for My Advisor! "
        "Our team will reach out within 1-2 business days to schedule your consultation."
    )
    
    pfma = st.session_state.get("pfma", {})
    appointment = pfma.get("appointment", {})
    
    st.markdown("#### Your Appointment Request")
    st.info(f"""
    **Contact Method:** {appointment.get('method', 'Not specified')}  
    **Preferred Time:** {appointment.get('time_window', 'Not specified')}  
    **Email:** {appointment.get('email', 'Not provided')}  
    {f"**Phone:** {appointment.get('phone', '')}" if appointment.get('phone') else ""}
    """)
    
    st.markdown("#### What's Next?")
    st.markdown("""
    1. **Review your email** — We'll send a confirmation with next steps
    2. **Gather documents** — Have any relevant financial/legal documents ready
    3. **Prepare questions** — Write down any specific questions you have
    4. **Your appointment** — Meet with your dedicated advisor
    """)
    
    # Mark PFMA as complete and update achievement
    if "pfma" not in st.session_state:
        st.session_state["pfma"] = {}
    st.session_state["pfma"]["progress"] = 100
    st.session_state["pfma"]["achievement"] = "🦆🦆🦆🦆 All Ducks in a Row"
    st.session_state["pfma"]["completed"] = True
    
    if st.button("← Return to Hub", type="primary", use_container_width=True):
        route_to("hub_concierge")
