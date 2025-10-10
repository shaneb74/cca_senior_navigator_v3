import streamlit as st
from core.nav import route_to
from core.state import get_user_ctx
from core.base_hub import BaseHub


class WaitingRoomHub(BaseHub):
    def __init__(self):
        super().__init__(
            title="Waiting Room Hub",
            icon="🕐",
            description="Track your appointment status and complete pre-visit tasks."
        )

    def render_content(self):
        # Get dynamic data
        person_name = st.session_state.get("person_name", "John")
        appointment_status = st.session_state.get("appointment_status", "Scheduled")
        appointment_time = st.session_state.get("appointment_time", "Dr. Smith - Oct 15, 2025")

        # Main Content Area - Two Column Layout
        col1, col2 = st.columns(2)

        # Left Column
        with col1:
            # Appointment Status Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Appointment Status</span>
                        <span class="section-icon">📅</span>
                    </div>
                    <div class="section-text">
                        Track your upcoming appointment and get reminders.
                    </div>
                    <div class="button-row">
                        <button class="btn btn-blue">View details</button>
                        <button class="btn btn-gray">Reschedule</button>
                    </div>
                </div>
                <hr class="separator">
                """,
                unsafe_allow_html=True
            )

            # Virtual Waiting Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Virtual Waiting</span>
                        <span class="section-icon">📹</span>
                    </div>
                    <div class="section-text">
                        Join your virtual waiting room when it's time for your appointment.
                    </div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <button class="btn btn-blue" style="width: 120px; height: 40px;">Join call</button>
                    </div>
                    <div class="button-row">
                        <button class="btn btn-gray" style="width: 120px; height: 40px;">Estimated wait</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Right Column
        with col2:
            # Preparation Guide Section
            prep_completed = st.session_state.get("prep_completed", False)
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Preparation Guide</span>
                        <span class="section-icon">📋</span>
                    </div>
                    <div class="section-text">
                        {"Complete your pre-appointment checklist and bring required documents." if not prep_completed else "All preparation tasks completed - you're ready for your appointment!"}
                    </div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <button class="btn btn-blue" style="width: 100px; height: 40px;">Check list</button>
                    </div>
                    <div class="button-row">
                        <button class="btn btn-gray" style="width: 80px; height: 40px;">Questions</button>
                    </div>
                </div>
                <hr class="separator">
                """,
                unsafe_allow_html=True
            )

            # Transportation Section
            st.markdown(
                """
                <div class="section-card">
                    <div class="section-title">
                        <span>Transportation</span>
                        <span class="section-icon">🚗</span>
                    </div>
                    <div class="section-text">
                        Arrange transportation to and from your appointment.
                    </div>
                    <div style="text-align: center;">
                        <button class="btn btn-blue" style="width: 100px; height: 40px;">Book ride</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Additional Services Section
        st.markdown(
            """
            <div class="additional-services">
                <h3 class="services-title">Appointment Resources</h3>
                <div class="service-cards">
                    <div class="service-card">
                        <div class="service-icon">📱</div>
                        <div class="service-content">
                            <h4>Appointment Reminder</h4>
                            <p>Get notified before your appointment</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Set up</button>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">📄</div>
                        <div class="service-content">
                            <h4>Document Prep</h4>
                            <p>Prepare required paperwork</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Start</button>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render():
    hub = WaitingRoomHub()
    hub.render()
