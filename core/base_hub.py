import streamlit as st
from core.state import get_user_ctx


class BaseHub:
    """Base class for all hub pages with consistent layout and styling."""

    def __init__(self, title, icon, description):
        self.title = title
        self.icon = icon
        self.description = description

    def render_header(self):
        """Render the common header structure."""
        # Login Banner
        st.markdown(
            """
            <div class="login-banner">
                <span>Log in for a better experience — continue where you left off, with your information kept secure and confidential following HIPAA guidelines.</span>
                <button class="close-btn" onclick="this.parentElement.style.display='none'">×</button>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Main Header
        person_name = st.session_state.get("person_name", "John")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f'<h1 class="main-title">{self.title.upper()}</h1>', unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"""
                <div class="assessment-info">
                    <span>Assessment for someone: {person_name}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Add +", key="add_person", help="Add another person"):
                # Add person functionality
                pass

    def render_footer(self):
        """Render the common footer structure."""
        # Footer Navigation
        st.markdown(
            """
            <div class="footer-nav">
                <div class="footer-columns">
                    <div class="footer-column">
                        <h5>Concierge Care Senior Navigator</h5>
                        <ul>
                            <li><a href="#">Landing</a></li>
                            <li><a href="#">Dashboard</a></li>
                            <li><a href="#">Login</a></li>
                            <li><a href="#">Sign In</a></li>
                            <li><a href="#">Account</a></li>
                        </ul>
                    </div>
                    <div class="footer-column">
                        <h5>Our Tools</h5>
                        <ul>
                            <li><a href="#">Guided Care Plan</a></li>
                            <li><a href="#">Cost Estimator</a></li>
                            <li><a href="#">Get Connected</a></li>
                            <li><a href="#">AI Agent</a></li>
                            <li><a href="#">Media Center</a></li>
                            <li><a href="#">AI Health Check</a></li>
                        </ul>
                    </div>
                    <div class="footer-column">
                        <h5>Concierge Care Advisors</h5>
                        <ul>
                            <li><a href="#">Home</a></li>
                            <li><a href="#">Contact</a></li>
                            <li><a href="#">Log In</a></li>
                        </ul>
                    </div>
                    <div class="footer-column">
                        <h5>For Partners</h5>
                        <ul>
                            <li><a href="#">Sign up</a></li>
                            <li><a href="#">Log in</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Bottom Footer
        st.markdown(
            """
            <div class="bottom-footer">
                <div class="bottom-footer-content">
                    <div class="copyright">© 2025 Concierge Care Senior Navigator™</div>
                    <div class="footer-links">
                        <a href="#">Terms & Conditions</a>
                        <a href="#">Privacy Policy</a>
                    </div>
                    <div class="social-icons">
                        <a href="#" class="social-icon">📷</a>
                        <a href="#" class="social-icon">📘</a>
                        <a href="#" class="social-icon">🐦</a>
                        <a href="#" class="social-icon">📺</a>
                        <a href="#" class="social-icon">💼</a>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    def render_css(self):
        """Render the common CSS styles."""
        st.markdown(
            """
            <style>
            .login-banner {
                background-color: #F5F5F5;
                width: 100%;
                max-width: 1200px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 20px;
                margin: 0 auto 20px auto;
                font-family: sans-serif;
                font-size: 12px;
                color: #333333;
            }
            .login-banner .close-btn {
                background: none;
                border: none;
                color: #007BFF;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .main-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto 30px auto;
                padding: 0 20px;
            }
            .main-title {
                font-family: sans-serif;
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                text-transform: uppercase;
                margin: 0;
            }
            .assessment-info {
                display: flex;
                align-items: center;
                gap: 10px;
                font-family: sans-serif;
                font-size: 16px;
                color: #333333;
            }
            .add-btn {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 3px;
                width: 60px;
                height: 30px;
                font-size: 12px;
                cursor: pointer;
            }
            .content-section {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }
            .section-card {
                background-color: white;
                border-radius: 5px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .section-title {
                display: flex;
                align-items: center;
                gap: 10px;
                font-family: sans-serif;
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
            }
            .section-icon {
                color: #007BFF;
                font-size: 20px;
            }
            .section-text {
                font-family: sans-serif;
                font-size: 12px;
                color: #333333;
                margin-bottom: 15px;
                line-height: 1.4;
            }
            .button-row {
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                align-items: center;
            }
            .btn {
                border: none;
                border-radius: 3px;
                font-family: sans-serif;
                font-size: 12px;
                cursor: pointer;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 5px;
            }
            .btn-gray {
                background-color: #666666;
                color: white;
            }
            .btn-blue {
                background-color: #007BFF;
                color: white;
            }
            .btn-green {
                background-color: #28A745;
                color: white;
            }
            .btn-glow {
                background-color: #007BFF;
                color: white;
                box-shadow: 0 0 10px rgba(255, 192, 203, 0.3);
            }
            .separator {
                border: none;
                border-top: 1px solid #E0E0E0;
                margin: 20px 0;
            }
            .additional-services {
                text-align: center;
                margin: 40px 0 20px 0;
            }
            .services-title {
                font-family: sans-serif;
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 20px;
            }
            .service-cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            .service-card {
                background-color: white;
                border-radius: 5px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .service-icon {
                color: #007BFF;
                font-size: 40px;
            }
            .service-content h4 {
                font-family: sans-serif;
                font-size: 14px;
                color: #333333;
                margin: 0 0 5px 0;
            }
            .service-content p {
                font-family: sans-serif;
                font-size: 12px;
                color: #666666;
                margin: 0;
            }
            .footer-nav {
                background-color: #F8F9FA;
                padding: 30px 20px;
                margin-top: 40px;
            }
            .footer-columns {
                max-width: 1200px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
            }
            .footer-column h5 {
                font-family: sans-serif;
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
                text-transform: uppercase;
            }
            .footer-column ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            .footer-column li {
                margin-bottom: 10px;
            }
            .footer-column a {
                font-family: sans-serif;
                font-size: 12px;
                color: #333333;
                text-decoration: none;
            }
            .footer-column a:hover {
                color: #007BFF;
            }
            .bottom-footer {
                background-color: white;
                padding: 20px;
                border-top: 1px solid #E0E0E0;
            }
            .bottom-footer-content {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .copyright {
                font-family: sans-serif;
                font-size: 10px;
                color: #666666;
            }
            .footer-links {
                display: flex;
                gap: 20px;
            }
            .footer-links a {
                font-family: sans-serif;
                font-size: 10px;
                color: #666666;
                text-decoration: none;
            }
            .social-icons {
                display: flex;
                gap: 5px;
            }
            .social-icon {
                color: #666666;
                font-size: 20px;
                text-decoration: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    def render(self):
        """Main render method - override in subclasses."""
        # Set page config
        st.set_page_config(page_title=self.title, layout="wide")

        # Render common CSS
        self.render_css()

        # Render header
        self.render_header()

        # Render content area (to be overridden by subclasses)
        self.render_content()

        # Render footer
        self.render_footer()

    def render_content(self):
        """Override this method in subclasses to provide specific content."""
        pass