import streamlit as st
from core.nav import route_to
from core.state import get_user_ctx
from core.base_hub import BaseHub


class ProfessionalHub(BaseHub):
    def __init__(self):
        super().__init__(
            title="Professional Hub",
            icon="💼",
            description="Tools and resources for discharge planners, social workers, and care partners."
        )

    def render_content(self):
        # Get dynamic data
        person_name = st.session_state.get("person_name", "John")
        professional_role = st.session_state.get("professional_role", "Care Coordinator")
        active_cases = st.session_state.get("active_cases", 3)

        # Main Content Area - Two Column Layout
        col1, col2 = st.columns(2)

        # Left Column
        with col1:
            # Care Coordination Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Care Coordination</span>
                        <span class="section-icon">🤝</span>
                    </div>
                    <div class="section-text">
                        Comprehensive care planning and coordination services.
                    </div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <button class="btn btn-blue" style="width: 140px; height: 40px;">Schedule consultation</button>
                    </div>
                    <div class="button-row">
                        <button class="btn btn-gray" style="width: 120px; height: 40px;">View cases</button>
                    </div>
                </div>
                <hr class="separator">
                """,
                unsafe_allow_html=True
            )

            # Legal Services Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Legal Services</span>
                        <span class="section-icon">⚖️</span>
                    </div>
                    <div class="section-text">
                        Estate planning, guardianship, and legal support services.
                    </div>
                    <div class="button-row">
                        <button class="btn btn-blue">Find attorney</button>
                        <button class="btn btn-gray">Document prep</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Right Column
        with col2:
            # Financial Planning Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Financial Planning</span>
                        <span class="section-icon">💰</span>
                    </div>
                    <div class="section-text">
                        Specialized financial guidance for seniors and families.
                    </div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <button class="btn btn-blue" style="width: 120px; height: 40px;">Book appointment</button>
                    </div>
                    <div class="button-row">
                        <button class="btn btn-gray" style="width: 80px; height: 40px;">Resource center</button>
                    </div>
                </div>
                <hr class="separator">
                """,
                unsafe_allow_html=True
            )

            # Case Management Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Case Management</span>
                        <span class="section-icon">📋</span>
                    </div>
                    <div class="section-text">
                        Track and manage active cases and client progress.
                    </div>
                    <div style="margin: 15px 0;">
                        <div style="background: #E5E7EB; border-radius: 10px; height: 8px; overflow: hidden;">
                            <div style="background: #10B981; height: 100%; width: {min(active_cases * 25, 100)}%; border-radius: 10px;"></div>
                        </div>
                        <div style="text-align: center; font-size: 14px; color: #6B7280; margin-top: 5px;">
                            {active_cases} Active Cases
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <button class="btn btn-blue" style="width: 100px; height: 40px;">Manage cases</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Professional Resources Section
        st.markdown(
            """
            <div class="additional-services">
                <h3 class="services-title">Professional Resources</h3>
                <div class="service-cards">
                    <div class="service-card">
                        <div class="service-icon">📊</div>
                        <div class="service-content">
                            <h4>Analytics Dashboard</h4>
                            <p>Track outcomes and performance metrics</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">View</button>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">📚</div>
                        <div class="service-content">
                            <h4>Training Center</h4>
                            <p>Professional development resources</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Access</button>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">👥</div>
                        <div class="service-content">
                            <h4>Network Directory</h4>
                            <p>Connect with care providers</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Browse</button>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render():
    hub = ProfessionalHub()
    hub.render()
