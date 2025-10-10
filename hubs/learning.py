import streamlit as st
from core.nav import route_to
from core.state import get_user_ctx
from core.base_hub import BaseHub


class LearningHub(BaseHub):
    def __init__(self):
        super().__init__(
            title="Learning & Resources Hub",
            icon="📚",
            description="Educational content and tools to support your senior care journey."
        )

    def render_content(self):
        # Get dynamic data
        person_name = st.session_state.get("person_name", "John")
        learning_progress = st.session_state.get("learning_progress", 0)
        completed_resources = st.session_state.get("completed_resources", [])

        # Main Content Area - Two Column Layout
        col1, col2 = st.columns(2)

        # Left Column
        with col1:
            # Caregiver Guides Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Caregiver Guides</span>
                        <span class="section-icon">📖</span>
                    </div>
                    <div class="section-text">
                        Comprehensive guides for caregivers and family members.
                    </div>
                    <div class="button-row">
                        <button class="btn btn-blue">Browse guides</button>
                        <button class="btn btn-gray">Most popular</button>
                    </div>
                </div>
                <hr class="separator">
                """,
                unsafe_allow_html=True
            )

            # Video Library Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Video Library</span>
                        <span class="section-icon">🎥</span>
                    </div>
                    <div class="section-text">
                        Educational videos on senior care topics and procedures.
                    </div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <button class="btn btn-blue" style="width: 120px; height: 40px;">Watch now</button>
                    </div>
                    <div class="button-row">
                        <button class="btn btn-gray" style="width: 120px; height: 40px;">Categories</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Right Column
        with col2:
            # FAQ Center Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>FAQ Center</span>
                        <span class="section-icon">❓</span>
                    </div>
                    <div class="section-text">
                        Find answers to common questions about senior care services.
                    </div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <button class="btn btn-blue" style="width: 100px; height: 40px;">Search FAQs</button>
                    </div>
                    <div class="button-row">
                        <button class="btn btn-gray" style="width: 80px; height: 40px;">Contact support</button>
                    </div>
                </div>
                <hr class="separator">
                """,
                unsafe_allow_html=True
            )

            # Learning Progress Section
            progress_percentage = min(learning_progress, 100)
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Learning Progress</span>
                        <span class="section-icon">📊</span>
                    </div>
                    <div class="section-text">
                        Track your progress through educational content.
                    </div>
                    <div style="margin: 15px 0;">
                        <div style="background: #E5E7EB; border-radius: 10px; height: 8px; overflow: hidden;">
                            <div style="background: #3B82F6; height: 100%; width: {progress_percentage}%; border-radius: 10px;"></div>
                        </div>
                        <div style="text-align: center; font-size: 14px; color: #6B7280; margin-top: 5px;">
                            {progress_percentage}% Complete
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <button class="btn btn-blue" style="width: 100px; height: 40px;">Continue</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Additional Resources Section
        st.markdown(
            """
            <div class="additional-services">
                <h3 class="services-title">Additional Resources</h3>
                <div class="service-cards">
                    <div class="service-card">
                        <div class="service-icon">📱</div>
                        <div class="service-content">
                            <h4>Interactive Tools</h4>
                            <p>Calculators and assessment tools</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Explore</button>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">👥</div>
                        <div class="service-content">
                            <h4>Community Forum</h4>
                            <p>Connect with other caregivers</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Join</button>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">📧</div>
                        <div class="service-content">
                            <h4>Newsletter</h4>
                            <p>Stay updated with latest resources</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Subscribe</button>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render():
    hub = LearningHub()
    hub.render()
