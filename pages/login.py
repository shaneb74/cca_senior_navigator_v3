from textwrap import dedent

import streamlit as st

from core.nav import route_to
from core.state import authenticate_user
from core.ui import img_src


def render():
    """Render login page - simple auth toggle (no real authentication)."""

    # Check if form was submitted
    if st.query_params.get("action") == "login":
        # Get form data from session state (set by JavaScript)
        name = st.session_state.get("_login_name", "Sarah")
        email = st.session_state.get("_login_email", "sarah@example.com")

        # Toggle auth on
        authenticate_user(name=name, email=email)

        # Clear query params and redirect to hub
        st.query_params.clear()
        route_to("hub_concierge")
        st.rerun()

    # Show form UI
    logo = img_src("static/images/logos/cca_logo.png")

    body_html = dedent(
        f"""
        <style>
        .login-bg{{
          min-height:100vh;
          background:linear-gradient(180deg, rgba(230,238,255,0.55) 0%, rgba(247,249,255,0.95) 60%, #ffffff 100%);
          padding:48px 24px 80px;
          display:flex;
          justify-content:center;
        }}
        .login-shell{{
          max-width:720px;
          width:100%;
          background:#ffffff;
          border-radius:28px;
          box-shadow:0 28px 70px rgba(15,23,42,0.12);
          padding:48px 56px 56px;
          display:grid;
          gap:32px;
        }}
        .login-brand{{display:flex;align-items:center;gap:18px;}}
        .login-brand img{{height:48px;width:auto;}}
        .login-brand span{{font-size:1.15rem;font-weight:700;color:#1f2a44;}}
        .login-top{{display:flex;align-items:center;gap:12px;font-size:0.95rem;}}
        .login-top a{{display:inline-flex;align-items:center;gap:8px;color:#2563eb;text-decoration:none;font-weight:600;}}
        .login-headline h1{{margin:0;font-size:2.2rem;font-weight:800;color:#111827;line-height:1.25;}}
        .login-headline p{{margin:8px 0 0;color:#4b5563;font-size:1.02rem;}}
        .login-form{{display:grid;gap:18px;}}
        .login-field{{display:grid;gap:8px;}}
        .login-field label{{font-weight:600;color:#1f2937;font-size:0.95rem;}}
        .login-input{{position:relative;}}
        .login-input input{{width:100%;height:54px;border-radius:14px;border:1px solid #d7dfec;padding:0 48px 0 18px;font-size:1rem;font-weight:500;color:#0f172a;background:#fff;box-shadow:0 2px 8px rgba(15,23,42,0.06) inset;}}
        .login-input svg{{position:absolute;right:18px;top:50%;transform:translateY(-50%);width:20px;height:20px;fill:#64748b;}}
        .login-input input:focus{{outline:none;border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,0.18);}}
        .login-actions{{display:flex;gap:12px;flex-wrap:wrap;}}
        .login-actions button{{flex:1 1 180px;height:48px;border-radius:14px;border:none;font-size:1.05rem;font-weight:700;cursor:pointer;transition:transform 0.18s ease, box-shadow 0.18s ease;}}
        .login-primary{{background:#2563eb;color:#fff;box-shadow:0 12px 22px rgba(37,99,235,0.22);}}
        .login-primary:hover{{transform:translateY(-1px);box-shadow:0 14px 26px rgba(37,99,235,0.28);}}
        .login-secondary{{background:#edf3ff;color:#2563eb;}}
        .login-secondary:hover{{transform:translateY(-1px);box-shadow:0 10px 20px rgba(148,163,184,0.25);}}
        @media(max-width:720px){{
          .login-shell{{padding:40px 28px;}}
          .login-actions button{{flex:1 1 100%;}}
        }}
        </style>
        <section class="login-bg">
          <div class="login-shell">
            <div class="login-brand">
              <img src="{logo}" alt="Concierge Care Senior Navigator"/>
              <span>Concierge Care Senior Navigator</span>
            </div>
            <div class="login-top">
              <a href="?page=welcome">&#8592; Back</a>
            </div>
            <div class="login-headline">
              <h1>Welcome back to Senior Navigator</h1>
              <p>Log in to pick up where you left off.</p>
            </div>
            <div class="login-form">
              <div class="login-field">
                <label for="login-name">Name<span style="color:#dc2626;">*</span></label>
                <div class="login-input">
                  <input id="login-name" type="text" placeholder="Your name" value="Sarah" />
                </div>
              </div>
              <div class="login-field">
                <label for="login-email">Email<span style="color:#dc2626;">*</span></label>
                <div class="login-input">
                  <input id="login-email" type="email" placeholder="Your email" value="sarah@example.com" />
                  <svg viewBox="0 0 24 24"><path d="M12 12.713 3 6.75V18q0 .825.587 1.413Q4.175 20 5 20h14q.825 0 1.412-.587Q21 18.825 21 18V6.75Zm0-1.963L20.85 6H3.15Z"/></svg>
                </div>
              </div>
              <div style="padding:8px;background:#eff6ff;border-radius:8px;font-size:0.9rem;color:#1e40af;">
                💡 <strong>Demo Mode:</strong> Just click "Log in" to toggle authentication. No password needed!
              </div>
            </div>
          </div>
        </section>
        """
    )

    # Login page has its own custom layout, no header/footer
    st.markdown(body_html, unsafe_allow_html=True)

    # Add Streamlit login button below
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Log in (Toggle Auth On)", use_container_width=True, type="primary"):
            # Get values from form (use defaults)
            authenticate_user(name="Sarah", email="sarah@example.com")
            st.success("✅ Logged in as Sarah!")
            st.info("Redirecting to Concierge Hub...")
            st.balloons()
            route_to("hub_concierge")
            st.rerun()
