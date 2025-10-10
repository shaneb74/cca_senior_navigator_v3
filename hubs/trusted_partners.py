import streamlit as st
from core.nav import route_to
from core.state import get_user_ctx
from core.base_hub import BaseHub


class TrustedPartnersHub(BaseHub):
    def __init__(self):
        super().__init__(
            title="Trusted Partners Hub",
            icon="🤝",
            description="Verified care providers and senior living communities in your area."
        )

    def render_content(self):
        # Get dynamic data
        person_name = st.session_state.get("person_name", "John")
        location = st.session_state.get("location", "Your Area")
        verified_partners = st.session_state.get("verified_partners", 23)

        # Main Content Area - Two Column Layout
        col1, col2 = st.columns(2)

        # Left Column
        with col1:
            # Home Care Agencies Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Home Care Agencies</span>
                        <span class="section-icon">🏠</span>
                    </div>
                    <div class="section-text">
                        Licensed and verified home care providers in {location}.
                    </div>
                    <div class="button-row">
                        <button class="btn btn-blue">View agencies</button>
                        <button class="btn btn-gray">Compare services</button>
                    </div>
                </div>
                <hr class="separator">
                """,
                unsafe_allow_html=True
            )

            # Senior Communities Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Senior Communities</span>
                        <span class="section-icon">🏢</span>
                    </div>
                    <div class="section-text">
                        Independent living, assisted living, and memory care options.
                    </div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <button class="btn btn-blue" style="width: 120px; height: 40px;">Explore options</button>
                    </div>
                    <div class="button-row">
                        <button class="btn btn-gray" style="width: 120px; height: 40px;">Virtual tours</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Right Column
        with col2:
            # Financial Advisors Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Financial Advisors</span>
                        <span class="section-icon">💼</span>
                    </div>
                    <div class="section-text">
                        Certified financial advisors specializing in senior care planning.
                    </div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <button class="btn btn-blue" style="width: 100px; height: 40px;">Find advisor</button>
                    </div>
                    <div class="button-row">
                        <button class="btn btn-gray" style="width: 80px; height: 40px;">Resource center</button>
                    </div>
                </div>
                <hr class="separator">
                """,
                unsafe_allow_html=True
            )

            # Partner Network Section
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="section-title">
                        <span>Partner Network</span>
                        <span class="section-icon">🌐</span>
                    </div>
                    <div class="section-text">
                        Access our network of verified healthcare and service providers.
                    </div>
                    <div style="margin: 15px 0;">
                        <div style="background: #E5E7EB; border-radius: 10px; height: 8px; overflow: hidden;">
                            <div style="background: #F59E0B; height: 100%; width: {min(verified_partners * 4, 100)}%; border-radius: 10px;"></div>
                        </div>
                        <div style="text-align: center; font-size: 14px; color: #6B7280; margin-top: 5px;">
                            {verified_partners} Verified Partners
                        </div>
                    </div>
                    <div style="text-align: center;">
                        <button class="btn btn-blue" style="width: 100px; height: 40px;">Browse network</button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Additional Services Section
        st.markdown(
            """
            <div class="additional-services">
                <h3 class="services-title">Additional Services</h3>
                <div class="service-cards">
                    <div class="service-card">
                        <div class="service-icon">🚗</div>
                        <div class="service-content">
                            <h4>Transportation</h4>
                            <p>Medical and non-medical transport</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Book</button>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">🍽️</div>
                        <div class="service-content">
                            <h4>Meal Services</h4>
                            <p>Nutritious meal delivery options</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Order</button>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">🛍️</div>
                        <div class="service-content">
                            <h4>Personal Shopping</h4>
                            <p>Grocery and personal item delivery</p>
                        </div>
                        <button class="btn btn-blue" style="width: 80px; height: 30px;">Shop</button>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render():
    hub = TrustedPartnersHub()
    hub.render()
