from textwrap import dedent

import streamlit as st

from core.ui import img_src


def _signup_markup() -> str:
    hero = img_src("static/images/login.png")
    logo = img_src("static/images/logos/cca_logo.png")

    return dedent(
        f"""
        <style>
        .auth-bg{{
          min-height:100vh;
          background:radial-gradient(circle at top left, rgba(230,238,255,0.65), rgba(247,249,255,0.95));
          padding:48px 24px;
          display:flex;
          align-items:center;
          justify-content:center;
        }}
        .auth-shell{{
          max-width:1120px;
          width:100%;
          background:#fff;
          border-radius:32px;
          box-shadow:0 32px 80px rgba(15,23,42,0.15);
          display:grid;
          grid-template-columns:minmax(0,1.15fr) minmax(0,0.85fr);
          overflow:hidden;
        }}
        .auth-pane{{
          padding:56px 64px;
          display:flex;
          flex-direction:column;
          gap:32px;
        }}
        .auth-brand{{display:flex;align-items:center;gap:16px;}}
        .auth-brand img{{height:48px;width:auto;}}
        .auth-brand span{{font-size:1.1rem;font-weight:700;color:#1f2a44;}}
        .auth-heading h1{{margin:0;font-size:2.3rem;font-weight:800;color:#111827;line-height:1.2;}}
        .auth-heading p{{margin:12px 0 0;color:#4b5563;font-size:1.05rem;line-height:1.7;max-width:46ch;}}
        .auth-benefits{{list-style:none;margin:0;padding:0;display:grid;gap:12px;}}
        .auth-benefits li{{display:flex;align-items:flex-start;gap:12px;color:#1f2937;font-size:1rem;line-height:1.55;}}
        .auth-benefits svg{{flex-shrink:0;width:20px;height:20px;fill:#2563eb;}}
        .auth-form{{display:grid;gap:18px;}}
        .auth-field{{display:grid;gap:8px;}}
        .auth-field label{{font-weight:600;color:#1f2937;font-size:0.95rem;}}
        .auth-input{{position:relative;}}
        .auth-input input{{width:100%;height:54px;border-radius:14px;border:1px solid #d7dfec;padding:0 48px 0 18px;font-size:1rem;font-weight:500;color:#0f172a;background:#fff;box-shadow:0 2px 8px rgba(15,23,42,0.06) inset;}}
        .auth-input svg{{position:absolute;right:18px;top:50%;transform:translateY(-50%);width:20px;height:20px;fill:#64748b;}}
        .auth-input input:focus{{outline:none;border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,0.18);}}
        .password-hint{{font-size:0.82rem;color:#6b7280;line-height:1.6;}}
        .password-hint span{{display:inline-flex;align-items:center;gap:4px;margin-right:12px;}}
        .auth-consent{{display:flex;align-items:flex-start;gap:10px;font-size:0.88rem;color:#4b5563;line-height:1.6;}}
        .auth-consent input{{margin-top:4px;}}
        .auth-actions{{display:flex;flex-wrap:wrap;gap:12px;}}
        .auth-actions button{{flex:1 1 180px;height:48px;border-radius:14px;border:none;font-size:1.05rem;font-weight:700;cursor:pointer;transition:transform 0.18s ease, box-shadow 0.18s ease;}}
        .auth-primary{{background:#2563eb;color:#fff;box-shadow:0 12px 22px rgba(37,99,235,0.22);}}
        .auth-primary:hover{{transform:translateY(-1px);box-shadow:0 14px 26px rgba(37,99,235,0.28);}}
        .auth-secondary{{background:#edf3ff;color:#2563eb;}}
        .auth-secondary:hover{{transform:translateY(-1px);box-shadow:0 10px 20px rgba(148,163,184,0.25);}}
        .auth-terms{{font-size:0.82rem;color:#6b7280;}}
        .auth-terms a{{color:#2563eb;text-decoration:none;font-weight:600;}}
        .oauth-divider{{display:flex;align-items:center;gap:16px;font-size:0.9rem;color:#6b7280;}}
        .oauth-divider::before,.oauth-divider::after{{content:"";flex:1;height:1px;background:linear-gradient(90deg,rgba(148,163,184,0.35),rgba(148,163,184,0));}}
        .oauth-divider::after{{background:linear-gradient(90deg,rgba(148,163,184,0),rgba(148,163,184,0.35));}}
        .oauth-grid{{display:flex;flex-wrap:wrap;gap:12px;}}
        .oauth-btn{{flex:1 1 180px;height:48px;border-radius:14px;border:1px solid #d7dfec;background:#fff;color:#1f2937;font-weight:600;font-size:0.95rem;display:inline-flex;align-items:center;justify-content:center;gap:10px;cursor:pointer;transition:box-shadow 0.18s ease,border-color 0.18s ease;}}
        .oauth-btn:hover{{border-color:#2563eb;box-shadow:0 12px 24px rgba(37,99,235,0.15);}}
        .oauth-btn svg{{width:20px;height:20px;}}
        .oauth-apple{{background:#0f172a;color:#fff;border-color:#0f172a;}}
        .oauth-facebook{{background:#1b74e4;color:#fff;border-color:#1b74e4;}}
        .auth-visual{{background:#f8f9fd;display:flex;align-items:center;justify-content:center;padding:36px;}}
        .auth-visual img{{width:100%;max-width:520px;border-radius:28px;box-shadow:0 32px 70px rgba(15,23,42,0.25);object-fit:cover;}}
        @media(max-width:960px){{
          .auth-shell{{grid-template-columns:1fr;}}
          .auth-visual{{order:-1;padding:28px;}}
          .auth-pane{{padding:40px 32px;}}
        }}
        @media(max-width:640px){{
          .auth-pane{{padding:36px 24px;}}
          .oauth-btn{{flex:1 1 100%;}}
        }}
        </style>
        <section class="auth-bg">
          <div class="auth-shell">
            <div class="auth-pane">
              <div class="auth-brand">
                <img src="{logo}" alt="Concierge Care Senior Navigator"/>
                <span>Concierge Care Senior Navigator</span>
              </div>
              <div class="auth-heading">
                <h1>Sign up</h1>
                <p>There's never any cost to you. Creating an account unlocks additional support and benefits.</p>
              </div>
              <ul class="auth-benefits">
                <li>
                  <svg viewBox="0 0 24 24"><path d="M9.5 17.25 4.75 12.5l1.4-1.4L9.5 14.5l8.35-8.35 1.4 1.4Z"/></svg>
                  Assess multiple people with our tools
                </li>
                <li>
                  <svg viewBox="0 0 24 24"><path d="M12 22q-3.35 0-5.675-2.325Q4 17.35 4 14V8q0-.825.587-1.412Q5.175 6 6 6h3V4q0-.825.587-1.412Q10.175 2 11 2h2q.825 0 1.412.588Q15 3.175 15 4v2h3q.825 0 1.412.588Q20 7.175 20 8v6q0 3.35-2.325 5.675Q15.35 22 12 22Zm-1-18v2h2V4Zm1 16q2.5 0 4.25-1.75T17 14V8H7v6q0 2.5 1.75 4.25T12 20Zm0-6Z"/></svg>
                  Eligibility to get additional free benefits
                </li>
                <li>
                  <svg viewBox="0 0 24 24"><path d="M20 3q.825 0 1.412.587Q22 4.175 22 5v14q0 .825-.588 1.412Q20.825 21 20 21H4q-.825 0-1.412-.588Q2 19.825 2 19V5q0-.825.588-1.413Q3.175 3 4 3Zm-4 14h4V7h-4Zm-2-2q-.825 0-1.412-.588Q12 13.825 12 13V7q0-.825.588-1.413Q13.175 5 14 5h2q.825 0 1.412.587Q18 6.175 18 7v6q0 .825-.588 1.412Q16.825 15 16 15Zm-8 2h4v-2H8v-2h4v-2H8V9h4V7H8q-.825 0-1.412.587Q6 8.175 6 9v6q0 .825.588 1.412Q7.175 17 8 17Z"/></svg>
                  Connect with our advisor to get individual consultation and support
                </li>
              </ul>
              <form class="auth-form">
                <div class="auth-field">
                  <label for="signup-email">Email<span style="color:#dc2626;">*</span></label>
                  <div class="auth-input">
                    <input id="signup-email" type="email" placeholder="Provide your email" required />
                    <svg viewBox="0 0 24 24"><path d="M12 12.713 3 6.75V18q0 .825.587 1.413Q4.175 20 5 20h14q.825 0 1.412-.587Q21 18.825 21 18V6.75Zm0-1.963L20.85 6H3.15Z"/></svg>
                  </div>
                </div>
                <div class="auth-field">
                  <label for="signup-password">Password<span style="color:#dc2626;">*</span></label>
                  <div class="auth-input">
                    <input id="signup-password" type="password" placeholder="Provide your password" required />
                    <svg viewBox="0 0 24 24"><path d="M17 10h-1V7.5q0-1.875-1.312-3.188Q13.375 3 11.5 3T8.312 4.312Q7 5.625 7 7.5V10H6q-.825 0-1.412.588Q4 11.175 4 12v7q0 .825.588 1.413Q5.175 21 6 21h11q.825 0 1.413-.587Q19 19.825 19 19v-7q0-.825-.587-1.412Q17.825 10 17 10Zm-5.5-5q.65 0 1.075.425Q13 5.85 13 6.5V10H10V6.5q0-.65.425-1.075Q10.85 5 11.5 5Z"/></svg>
                  </div>
                </div>
                <div class="password-hint">
                  Ensure your password is both safe and strong:
                  <div style="margin-top:6px;">
                    <span>○ 8 characters</span>
                    <span>○ one uppercase letter</span>
                    <span>○ one lowercase letter</span>
                    <span>○ one digit</span>
                    <span>○ one special character ! @ # $ % ^ &amp; *</span>
                  </div>
                </div>
                <label class="auth-consent">
                  <input type="checkbox" required />
                  <span>I consent to the collection of my consumer health data. If I am consenting on behalf of someone else, I have proper authorization to do so.</span>
                </label>
                <div class="auth-terms">
                  By sharing your contact information, you agree to our <a href="#">Terms &amp; Conditions</a> and <a href="#">Privacy Policy</a>.
                </div>
                <div class="auth-actions">
                  <button type="submit" class="auth-primary">Sign up</button>
                  <button type="button" class="auth-secondary" onclick="window.location.href='?page=login'">I have an account</button>
                </div>
              </form>
              <div class="oauth-divider">Or continue with</div>
              <div class="oauth-grid">
                <button type="button" class="oauth-btn oauth-apple">
                  <svg viewBox="0 0 24 24"><path d="M16.365 1.43c0 1.14-.463 2.188-1.207 2.94-.772.781-1.93 1.38-3.07 1.301-.141-1.119.39-2.29 1.214-3.09.805-.781 2.227-1.34 3.063-1.151zM19.938 17.337c-.637 1.444-.94 2.074-1.752 3.342-1.137 1.717-2.739 3.858-4.7 3.873-1.758.015-2.205-1.139-4.103-1.127-1.898.01-2.39 1.141-4.147 1.127-1.961-.015-3.457-1.951-4.594-3.663-3.152-4.756-3.486-10.337-1.548-13.285 1.381-2.135 3.565-3.386 5.618-3.386 2.094 0 3.41 1.151 5.142 1.151 1.688 0 2.714-1.151 5.116-1.151 1.852 0 3.804.998 5.177 2.718-.135.082-3.351 1.95-3.316 5.812.033 4.606 4.066 6.137 4.106 6.154z"/></svg>
                  Apple
                </button>
                <button type="button" class="oauth-btn">
                  <svg viewBox="0 0 533.5 544.3"><path fill="#4285f4" d="M533.5 278.4c0-17.4-1.4-34.8-4.3-51.9H272v98.4h146.9c-6.3 34-25 62.8-53.2 82.1v68h85.9c50.2-46.2 81.9-114.2 81.9-196.6z"/><path fill="#34a853" d="M272 544.3c72.5 0 133.6-23.9 178.1-64.7l-85.9-68c-23.9 16.1-54.6 25.5-92.2 25.5-70.9 0-131-47.9-152.4-112.3H31.3v70.9C75.5 479.4 166 544.3 272 544.3z"/><path fill="#fbbc04" d="M119.6 324.8c-10.4-30.9-10.4-64.2 0-95.1V158.8H31.3c-41.7 82.8-41.7 180.9 0 263.7l88.3-70.9z"/><path fill="#ea4335" d="M272 107.7c38.5-.6 75.6 14.1 103.3 40.9l77.1-77.1C405 24.9 345.4 0 272 0 166 0 75.5 64.9 31.3 158.8l88.3 70.9C141 155.6 201.1 107.7 272 107.7z"/></svg>
                  Google
                </button>
                <button type="button" class="oauth-btn oauth-facebook">
                  <svg viewBox="0 0 24 24"><path d="M13.5 22v-7h2.5l.5-3h-3v-2c0-.87.28-1.5 1.5-1.5h1.6V5.25c-.28-.04-1.23-.12-2.35-.12-2.33 0-3.93 1.43-3.93 4.04V12H7v3h3.32v7Z"/></svg>
                  Facebook
                </button>
              </div>
            </div>
            <div class="auth-visual">
              <img src="{hero}" alt="Family meeting with advisor"/>
            </div>
          </div>
        </section>
        """
    )


def render():
    # Signup page has its own custom layout, no header/footer
    st.markdown(_signup_markup(), unsafe_allow_html=True)
