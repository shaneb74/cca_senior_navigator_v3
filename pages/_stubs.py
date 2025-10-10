from typing import List, Optional, Tuple
import streamlit as st

from core.nav import route_to
from core.ui import img_src


def _page(title: str, desc: str, ctas: Optional[List[Tuple[str, str]]] = None):
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        f"""
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      {title}
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      {desc}
    </p>
  </div>
        """,
        unsafe_allow_html=True,
    )
    
    if ctas:
        st.markdown('<div class="card-actions" style="justify-content: center; margin-top: var(--space-6);">', unsafe_allow_html=True)
        for label, target in ctas:
            st.markdown(f'<a class="btn btn--primary" href="?page={target}" style="margin: 0 var(--space-2);">{label}</a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</section>', unsafe_allow_html=True)


def render_welcome():
    hero = img_src("static/images/hero.png")
    someone_img = img_src("static/images/welcome_someone_else.png")
    self_img = img_src("static/images/welcome_self.png")
    st.markdown(
        f"""<section class="container section-hero">
<div class="hero-grid">
  <div>
    <div class="hero-eyebrow">Concierge Care Advisors</div>
    <h1 class="hero-title">Senior Navigator</h1>
    <p class="hero-sub">Expert advisors - no cost. Helping families navigate the most important senior living decisions with clarity and compassion.</p>
    <div class="cta-row">
      <a class="btn btn--primary" href="?page=welcome_contextual">Start Now</a>
      <a class="btn btn--secondary" href="?page=login">Log in or sign up</a>
    </div>
  </div>
  <div>
    <img class="card-photo" src="{hero}" alt="Senior and caregiver"/>
  </div>
</div>
</section>

<section class="container stack">
<h2>How We Can Help You</h2>
<div class="cards-2">
  <article class="card card--hover">
    <img class="card-photo" src="{someone_img}" alt="Supporting others"/>
    <div class="card-head">Supporting Others</div>
    <div class="card-meta">For a loved one</div>
    <p>Helping you make confident care decisions for someone you love.</p>
    <div class="card-actions">
      <a class="btn btn--primary" href="?page=for_someone">For someone</a>
    </div>
  </article>

  <article class="card card--hover">
    <img class="card-photo" src="{self_img}" alt="Getting ready for myself"/>
    <div class="card-head">Getting Ready for Myself</div>
    <div class="card-meta">For myself</div>
    <p>Plan for your own future care with trusted guidance and peace of mind.</p>
    <div class="card-actions">
      <a class="btn btn--primary" href="?page=for_me_contextual">For me</a>
    </div>
  </article>
</div>
</section>""",
        unsafe_allow_html=True,
    )


def render_welcome_contextual():
    mode = st.query_params.get("who", "someone")
    is_me = mode == "me"
    photo_back = img_src("static/images/contextual_self.png") if is_me else img_src("static/images/contextual_someone_else.png")
    # foreground cards from design
    photo_front = img_src("static/images/tell_us_about_you.png") if is_me else img_src("static/images/tell_us_about_them.png")
    title_copy = "Getting Ready for Myself" if is_me else "Supporting Others"
    body_copy = (
        "Plan for your own future care with trusted guidance and peace of mind."
        if is_me
        else "Helping you make confident care decisions for someone you love."
    )
    name_label = "What's your name?" if is_me else "What's their name?"

    # Don't initialize person_name - let it remain unset if not provided

    # Apply the canvas background
    st.markdown(
        """<style>
        .main .block-container {
            background: #E6EEFF;
            min-height: 72vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    # Create the layout using Streamlit columns
    col1, col2 = st.columns([0.9, 1.1])

    with col1:
        st.markdown(
            f"""<div class="modal-card stack-sm">
      <div class="toggle">
        <a class="pill{' is-selected' if not is_me else ''}" href="?page=welcome_contextual&who=someone">For someone</a>
        <a class="pill{' is-selected' if is_me else ''}" href="?page=welcome_contextual&who=me">For me</a>
      </div>
      <h3 class="mt-space-4">{title_copy}</h3>
      <p>{body_copy}</p>""",
            unsafe_allow_html=True,
        )

        # Use Streamlit text input to capture the name
        current_name = st.session_state.get("person_name", "")
        person_name = st.text_input(
            name_label,
            value=current_name,
            placeholder="Type a name",
            key="person_name_input"
        )

        # Update session state when name changes
        if person_name != current_name:
            st.session_state["person_name"] = person_name

        st.markdown(
            f"""
      <div class="card-actions mt-space-4">
        <a class="btn btn--primary" href="?page=hub_concierge">Continue</a>
        <a class="btn btn--ghost" href="?page=welcome">Close</a>
      </div>
      <p class="helper-note mt-space-4">If you want to assess several people, you can move on to the next step later.</p>
    </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div class="photo-stack" aria-hidden="true">
    <img class="photo-back" src="{photo_back}" alt=""/>
    <img class="photo-front" src="{photo_front}" alt=""/>
  </div>""",
            unsafe_allow_html=True,
        )


def render_for_someone():
    """Dedicated page for 'For Someone' flow."""
    photo_back = img_src("static/images/contextual_someone_else.png")
    photo_front = img_src("static/images/tell_us_about_them.png")
    title_copy = "Supporting Others"
    body_copy = "Helping you make confident care decisions for someone you love."
    name_label = "What's their name?"

    # Apply the canvas background
    st.markdown(
        """<style>
        .main .block-container {
            background: #E6EEFF;
            min-height: 72vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    # Create the layout using Streamlit columns
    col1, col2 = st.columns([0.9, 1.1])

    with col1:
        st.markdown(
            f"""<div class="modal-card stack-sm">
      <div class="toggle">
        <a class="pill is-selected" href="?page=for_someone">For someone</a>
        <a class="pill" href="?page=for_me_contextual">For me</a>
      </div>
      <h3 class="mt-space-4">{title_copy}</h3>
      <p>{body_copy}</p>""",
            unsafe_allow_html=True,
        )

        # Use Streamlit text input to capture the name
        current_name = st.session_state.get("person_name", "")
        person_name = st.text_input(
            name_label,
            value=current_name,
            placeholder="Type a name",
            key="person_name_input"
        )

        # Update session state when name changes
        if person_name != current_name:
            st.session_state["person_name"] = person_name

        st.markdown(
            f"""
      <div class="card-actions mt-space-4">
        <a class="btn btn--primary" href="?page=hub_concierge">Continue</a>
        <a class="btn btn--ghost" href="?page=welcome">Close</a>
      </div>
      <p class="helper-note mt-space-4">If you want to assess several people, you can move on to the next step later.</p>
    </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div class="photo-stack" aria-hidden="true">
    <img class="photo-back" src="{photo_back}" alt=""/>
    <img class="photo-front" src="{photo_front}" alt=""/>
  </div>""",
            unsafe_allow_html=True,
        )


def render_for_me_contextual():
    """Dedicated page for 'For Me' flow."""
    photo_back = img_src("static/images/contextual_self.png")
    photo_front = img_src("static/images/tell_us_about_you.png")
    title_copy = "Getting Ready for Myself"
    body_copy = "Plan for your own future care with trusted guidance and peace of mind."
    name_label = "What's your name?"

    # Apply the canvas background
    st.markdown(
        """<style>
        .main .block-container {
            background: #E6EEFF;
            min-height: 72vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    # Create the layout using Streamlit columns
    col1, col2 = st.columns([0.9, 1.1])

    with col1:
        st.markdown(
            f"""<div class="modal-card stack-sm">
      <div class="toggle">
        <a class="pill" href="?page=for_someone">For someone</a>
        <a class="pill is-selected" href="?page=for_me_contextual">For me</a>
      </div>
      <h3 class="mt-space-4">{title_copy}</h3>
      <p>{body_copy}</p>""",
            unsafe_allow_html=True,
        )

        # Use Streamlit text input to capture the name
        current_name = st.session_state.get("person_name", "")
        person_name = st.text_input(
            name_label,
            value=current_name,
            placeholder="Type a name",
            key="person_name_input"
        )

        # Update session state when name changes
        if person_name != current_name:
            st.session_state["person_name"] = person_name

        st.markdown(
            f"""
      <div class="card-actions mt-space-4">
        <a class="btn btn--primary" href="?page=hub_concierge">Continue</a>
        <a class="btn btn--ghost" href="?page=welcome">Close</a>
      </div>
      <p class="helper-note mt-space-4">If you want to assess several people, you can move on to the next step later.</p>
    </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""<div class="photo-stack" aria-hidden="true">
    <img class="photo-back" src="{photo_back}" alt=""/>
    <img class="photo-front" src="{photo_front}" alt=""/>
  </div>""",
            unsafe_allow_html=True,
        )


def render_pro_welcome():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      Professional Welcome
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Entry for discharge planners and partners.
    </p>
  </div>
  <div class="card-actions" style="justify-content: center; margin-top: var(--space-6);">
    <a class="btn btn--primary" href="?page=pro_welcome_contextual" style="margin: 0 var(--space-2);">Pro Contextual</a>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_pro_welcome_contextual():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      Pro Contextual Welcome
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Contextualized pro entry.
    </p>
  </div>
  <div class="card-actions" style="justify-content: center; margin-top: var(--space-6);">
    <a class="btn btn--primary" href="?page=professionals" style="margin: 0 var(--space-2);">Professionals</a>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_professionals():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container stack">
  <div class="card stack-sm">
    <div class="card-head">Professional Hub</div>
    <div class="card-meta">For discharge planners, social workers, and placement partners.</div>
    <div class="grid">
      <div class="card card--hover grid-span-6 stack-sm">
        <div class="card-head">Submit a referral</div>
        <p>Share essentials securely so our advisor can reach the family within one business day.</p>
        <div class="card-actions mt-space-4">
          <a class="btn btn--primary" href="?page=trusted_partners">Trusted Partners</a>
          <a class="btn btn--ghost" href="?page=about">About Us</a>
        </div>
      </div>
      <div class="card card--hover grid-span-6 stack-sm">
        <div class="card-head">Resources</div>
        <p>Downloadable checklists, eligibility overviews, and care setting definitions.</p>
        <div class="card-actions mt-space-4">
          <a class="btn btn--secondary" href="?page=privacy">Privacy Policy</a>
          <a class="btn btn--ghost" href="?page=terms">Terms</a>
        </div>
      </div>
    </div>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_login():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      Login
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Auth form placeholder.
    </p>
  </div>
  <div class="card-actions" style="justify-content: center; margin-top: var(--space-6);">
    <a class="btn btn--primary" href="?page=my_account" style="margin: 0 var(--space-2);">My Account</a>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_ai_advisor():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      AI Advisor (Navi)
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Conversation surface placeholder.
    </p>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_documents():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      Documents
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Uploads and document listing. Auth required.
    </p>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_exports():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      Exports
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      PDF/CSV bundle generator. Auth required.
    </p>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_waiting_room():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    status_img = img_src("static/images/login.png")
    st.markdown(
        f"""
<section class="container stack">
  <div class="banner banner--success">You’re booked. An advisor will follow up within 24 hours.</div>
  <div class="grid">
    <div class="card grid-span-8 stack-sm">
      <div class="card-head">Ducks in a Row</div>
      <div class="card-meta">Complete these quick tasks to prep your call.</div>
      <ul class="list-unstyled stack-xs">
        <li><span class="chip status success"><span class="dot"></span> Contact details confirmed</span></li>
        <li><span class="chip status"><span class="dot"></span> Upload recent medication list</span></li>
        <li><span class="chip status"><span class="dot"></span> Confirm living situation</span></li>
      </ul>
      <div class="card-actions mt-space-4">
        <a class="btn btn--primary" href="?page=ai_advisor">Ask Navi</a>
        <a class="btn btn--ghost" href="?page=documents">Open Documents</a>
      </div>
    </div>
    <div class="card grid-span-4 text-center">
      <img class="img-responsive img-rounded" src="{status_img}" alt="Status" />
    </div>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_trusted_partners():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      Trusted Partners
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Partner directory and disclosures.
    </p>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_my_account():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      My Account
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Profile, preferences, and consent history.
    </p>
  </div>
  <div class="card-actions" style="justify-content: center; margin-top: var(--space-6);">
    <a class="btn btn--primary" href="?page=privacy" style="margin: 0 var(--space-2);">Privacy Policy</a>
    <a class="btn btn--primary" href="?page=terms" style="margin: 0 var(--space-2);">Terms of Use</a>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_terms():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      Terms of Use
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Versioned legal surface.
    </p>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_privacy():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      Privacy Policy
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Versioned privacy surface.
    </p>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_about():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      About Us
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Company, mission, and contact.
    </p>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_faqs():
    # Apply consistent styling like other pages
    st.markdown(
        """<style>
        .main .block-container {
            background: var(--bg);
            min-height: 80vh;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
<section class="container section">
  <div class="text-center" style="margin-bottom: var(--space-8);">
    <h1 style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.15; color: var(--ink); margin-bottom: var(--space-4);">
      FAQs & Answers
    </h1>
    <p style="color: var(--ink-600); max-width: 48ch; margin: 0 auto; font-size: 1.1rem;">
      Common questions and answers about senior care navigation and our services.
    </p>
  </div>
  <div class="card-actions" style="justify-content: center; margin-top: var(--space-6);">
    <a class="btn btn--primary" href="?page=hub_concierge" style="margin: 0 var(--space-2);">Back to Hub</a>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_signup():
    # Apply custom styling for the signup page
    st.markdown(
        """
        <style>
        .main .block-container {
            background: #F5F5F5;
            min-height: 100vh;
            font-family: sans-serif;
        }
        .logo-section {
            display: flex;
            align-items: center;
            padding: 20px 0;
            margin-bottom: 20px;
        }
        .logo-icon {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            color: #007BFF;
        }
        .logo-text {
            color: #333333;
            font-size: 14px;
            font-weight: normal;
            margin: 0;
        }
        .signup-card {
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 10px;
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        .signup-title {
            color: #333333;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        .signup-subtitle {
            color: #666666;
            font-size: 12px;
            text-align: center;
            max-width: 300px;
            margin: 0 auto 20px auto;
        }
        .benefits-list {
            margin-bottom: 20px;
        }
        .benefit-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            color: #333333;
            font-size: 12px;
        }
        .benefit-icon {
            width: 10px;
            height: 10px;
            margin-right: 8px;
            flex-shrink: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-label {
            color: #333333;
            font-size: 12px;
            margin-bottom: 5px;
            display: block;
        }
        .form-input-container {
            position: relative;
            display: flex;
            align-items: center;
        }
        .form-input {
            width: 200px;
            height: 30px;
            padding: 0 35px 0 10px;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            font-size: 14px;
        }
        .input-icon {
            position: absolute;
            right: 10px;
            width: 20px;
            height: 20px;
            color: #666666;
            cursor: pointer;
        }
        .password-requirements {
            color: #666666;
            font-size: 10px;
            margin-bottom: 15px;
        }
        .requirement-item {
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }
        .checkbox-custom {
            width: 15px;
            height: 15px;
            margin-right: 8px;
        }
        .consent-text {
            color: #666666;
            font-size: 10px;
            margin-bottom: 10px;
        }
        .terms-link {
            color: #007BFF;
            font-size: 10px;
            text-align: center;
            display: block;
            margin-bottom: 20px;
        }
        .button-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .btn-signup {
            background: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            width: 120px;
            height: 40px;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .btn-login {
            background: #D3D3D3;
            color: #333333;
            border: none;
            border-radius: 5px;
            width: 120px;
            height: 30px;
            font-size: 12px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .image-container {
            text-align: center;
            padding: 20px;
        }
        .signup-image {
            max-width: 550px;
            max-height: 400px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Top Section - Logo and Title
    st.markdown(
        """
        <div class="logo-section">
            <div class="logo-icon">🐦</div>
            <h2 class="logo-text">Concierge Care Senior Navigator</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Main Content Area - Two Column Layout
    col1, col2 = st.columns(2, gap="medium")

    # Left Column - Form Section
    with col1:
        st.markdown(
            """
            <div class="signup-card">
                <h1 class="signup-title">Sign up</h1>
                <p class="signup-subtitle">There's never any cost to you. Creating an account unlocks additional support and benefits.</p>
                
                <div class="benefits-list">
                    <div class="benefit-item">
                        <span class="benefit-icon" style="color: #007BFF;">✓</span>
                        Assess multiple people with our tools
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon" style="color: #007BFF;">✓</span>
                        Eligibility to get additional free benefits.
                    </div>
                    <div class="benefit-item">
                        <span class="benefit-icon" style="color: #007BFF;">🎧</span>
                        Connect with our advisor to get individual consultation and support.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Form Fields
        with st.container():
            # Email Field
            st.markdown('<label class="form-label">Email *</label>', unsafe_allow_html=True)
            email = st.text_input("", placeholder="Enter your email", key="signup_email", label_visibility="collapsed")
            
            # Password Field with visibility toggle
            st.markdown('<label class="form-label">Password *</label>', unsafe_allow_html=True)
            password_visible = st.session_state.get("password_visible", False)
            password = st.text_input("", 
                                   placeholder="Enter your password", 
                                   type="password" if not password_visible else "default",
                                   key="signup_password", 
                                   label_visibility="collapsed")
            
            # Password visibility toggle button
            if st.button("👁️", key="toggle_password", help="Toggle password visibility"):
                st.session_state["password_visible"] = not password_visible
                st.rerun()
            
            # Password Requirements
            st.markdown(
                """
                <div class="password-requirements">
                    <div>Ensure your password is both safe and strong:</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Password requirement checkboxes
            req_8_chars = st.checkbox("8 characters", key="req_8_chars", label_visibility="collapsed")
            req_uppercase = st.checkbox("one uppercase letter", key="req_uppercase", label_visibility="collapsed")
            req_lowercase = st.checkbox("one lowercase letter", key="req_lowercase", label_visibility="collapsed")
            req_digit = st.checkbox("one digit", key="req_digit", label_visibility="collapsed")
            req_special = st.checkbox("one special character ! @ # $ % ^ & *", key="req_special", label_visibility="collapsed")
            
            # Consent Checkbox
            consent = st.checkbox("I consent to the collection of my consumer health data. If I am consenting on behalf of someone else, I have proper authorization to do so.", 
                                key="consent_checkbox", label_visibility="collapsed")
            
            # Terms Link
            st.markdown(
                """
                <div class="terms-link">
                    By sharing your contact information, you agree to our <a href="?page=terms">Terms & Conditions</a> and <a href="?page=privacy">Privacy Policy</a>.
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Buttons
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.button("Sign up", key="signup_button", use_container_width=True):
                    # Handle signup logic here
                    st.success("Account created successfully!")
                    
            with col_btn2:
                if st.button("I have an account", key="login_button", use_container_width=True):
                    route_to("login")

    # Right Column - Image Section
    with col2:
        login_image = img_src("static/images/login.png")
        st.markdown(
            f"""
            <div class="image-container">
                <img src="{login_image}" alt="Login" class="signup-image">
            </div>
            """,
            unsafe_allow_html=True
        )
