"""
Login Page - OAuth Mock-up + Simple Toggle Authentication

Features:
- OAuth buttons (Apple, Google, Facebook) - mock UI only
- Email/name fallback (toggle auth, no real passwords)
- Guest mode option
- Clean design matching app aesthetics

For demo/MVP: All auth is toggle-based (no real OAuth/passwords).
Future: Wire OAuth buttons to real providers.
"""

import streamlit as st

from core.nav import route_to
from core.state import authenticate_user, is_authenticated
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple


def render(ctx=None):
    """Render login page with OAuth mock-up and simple auth toggle."""
    
    # If already authenticated, redirect to hub
    if is_authenticated():
        route_to(push=False, page="hub_lobby")
        return
    
    # Render header (with "Log In" link active)
    render_header_simple(active_route="login")
    
    # Inject login-specific CSS
    _inject_login_css()
    
    # Render login form
    _render_login_form()
    
    # Render footer
    render_footer_simple()


def _inject_login_css():
    """Inject login page styles matching app design system."""
    st.markdown(
        """
        <style>
        /* Reset Streamlit container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 100%;
        }
        
        /* Login page background */
        .main {
            background: var(--bg, #f8fafc);
        }
        
        /* Login container */
        .login-section {
            min-height: 70vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: var(--space-8) var(--space-4);
        }
        
        .login-card {
            background: white;
            border-radius: 12px;
            padding: var(--space-8);
            max-width: 440px;
            width: 100%;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--ink);
            margin-bottom: var(--space-2);
            text-align: center;
        }
        
        .login-subtitle {
            color: var(--ink-600);
            text-align: center;
            margin-bottom: var(--space-6);
            font-size: 0.95rem;
        }
        
        .oauth-buttons {
            display: flex;
            flex-direction: column;
            gap: var(--space-3);
            margin-bottom: var(--space-4);
        }
        
        .oauth-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 12px 20px;
            border: 1px solid var(--ink-200);
            border-radius: 8px;
            background: white;
            color: var(--ink);
            font-weight: 500;
            font-size: 0.95rem;
            text-decoration: none;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .oauth-btn:hover {
            background: var(--bg);
            border-color: var(--ink-300);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .oauth-btn--apple {
            background: #000;
            color: white;
            border-color: #000;
        }
        
        .oauth-btn--apple:hover {
            background: #1a1a1a;
            border-color: #1a1a1a;
        }
        
        .oauth-btn--google {
            background: white;
            border-color: #dadce0;
        }
        
        .oauth-btn--facebook {
            background: #1877f2;
            color: white;
            border-color: #1877f2;
        }
        
        .oauth-btn--facebook:hover {
            background: #166fe5;
            border-color: #166fe5;
        }
        
        .oauth-icon {
            width: 20px;
            height: 20px;
            object-fit: contain;
        }
        
        .login-divider {
            text-align: center;
            color: var(--ink-400);
            margin: var(--space-5) 0;
            font-size: 0.875rem;
            position: relative;
        }
        
        .login-divider::before,
        .login-divider::after {
            content: "";
            position: absolute;
            top: 50%;
            width: 40%;
            height: 1px;
            background: var(--ink-200);
        }
        
        .login-divider::before {
            left: 0;
        }
        
        .login-divider::after {
            right: 0;
        }
        
        .guest-text {
            text-align: center;
            color: var(--ink-500);
            font-size: 0.875rem;
            margin-top: var(--space-4);
        }
        
        .back-link {
            text-align: center;
            margin-top: var(--space-4);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_login_form():
    """Render login form with OAuth buttons and email fallback."""
    
    # Add some vertical spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Use columns to center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Title
        st.markdown(
            '<h1 class="login-title">Sign In</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="login-subtitle">Welcome back to Concierge Care Advisors</p>',
            unsafe_allow_html=True,
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # OAuth Buttons (Mock UI - no real OAuth for demo)
        # Apple Sign In
        if st.button(
            "🍎 Continue with Apple",
            use_container_width=True,
            key="oauth_apple",
        ):
            # Mock OAuth - just toggle auth with default name
            authenticate_user(name="Demo User", email="demo@apple.com")
            st.success("✅ Signed in with Apple!")
            st.rerun()
        
        # Google Sign In
        if st.button(
            "🔵 Continue with Google",
            use_container_width=True,
            key="oauth_google",
        ):
            # Mock OAuth - just toggle auth with default name
            authenticate_user(name="Demo User", email="demo@gmail.com")
            st.success("✅ Signed in with Google!")
            st.rerun()
        
        # Facebook Sign In
        if st.button(
            "📘 Continue with Facebook",
            use_container_width=True,
            key="oauth_facebook",
        ):
            # Mock OAuth - just toggle auth with default name
            authenticate_user(name="Demo User", email="demo@facebook.com")
            st.success("✅ Signed in with Facebook!")
            st.rerun()
        
        # Divider
        st.markdown(
            '<div class="login-divider">or sign in with email</div>',
            unsafe_allow_html=True,
        )
        
        # Email/Name form (fallback)
        name = st.text_input(
            "Name",
            value="Sarah",
            placeholder="Enter your name",
            key="login_name",
        )
        
        email = st.text_input(
            "Email",
            value="sarah@example.com",
            placeholder="you@example.com",
            key="login_email",
        )
        
        # Sign In button
        if st.button(
            "Sign In with Email",
            type="primary",
            use_container_width=True,
            key="login_submit",
        ):
            if name and email:
                authenticate_user(name=name, email=email)
                st.success(f"✅ Welcome, {name}!")
                st.rerun()
            else:
                st.error("Please enter both name and email.")
        
        # Guest option
        st.markdown(
            '<p class="guest-text">Don\'t want to sign in?</p>',
            unsafe_allow_html=True,
        )
        
        if st.button(
            "Continue as Guest",
            type="secondary",
            use_container_width=True,
            key="login_guest",
        ):
            route_to(push=False, page="hub_lobby")
        
        # Back link
        st.markdown("---")
        if st.button("← Back to Welcome", key="login_back", use_container_width=True):
            route_to(push=False, page="welcome")
