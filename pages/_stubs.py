
from typing import List, Optional, Tuple
import streamlit as st

from core.nav import route_to
from core.ui import img_src


def _page(title: str, desc: str, ctas: Optional[List[Tuple[str, str]]] = None):
    st.header(title)
    st.write(desc)
    if ctas:
        for label, target in ctas:
            if st.button(label, key=f"cta-{title}-{target}"):
                route_to(target)


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
      <a class="btn btn--primary" href="?page=welcome_contextual&who=someone">For someone</a>
    </div>
  </article>

  <article class="card card--hover">
    <img class="card-photo" src="{self_img}" alt="Getting ready for myself"/>
    <div class="card-head">Getting Ready for Myself</div>
    <div class="card-meta">For myself</div>
    <p>Plan for your own future care with trusted guidance and peace of mind.</p>
    <div class="card-actions">
      <a class="btn btn--primary" href="?page=welcome_contextual&who=me">For me</a>
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

    st.markdown(
        f"""<section class="canvas-soft">
<div class="container center-wrap">
  <div>
    <div class="modal-card stack-sm">
      <div class="toggle">
        <a class="pill{' is-selected' if not is_me else ''}" href="?page=welcome_contextual&who=someone">For someone</a>
        <a class="pill{' is-selected' if is_me else ''}" href="?page=welcome_contextual&who=me">For me</a>
      </div>
      <h3 class="mt-space-4">{title_copy}</h3>
      <p>{body_copy}</p>
      <div class="field mt-space-3">
        <label>{name_label}</label>
        <input class="input" placeholder="Type a name"/>
      </div>
      <div class="card-actions mt-space-4">
        <a class="btn btn--primary" href="?page=hub_concierge">Continue</a>
        <a class="btn btn--ghost" href="?page=welcome">Close</a>
      </div>
      <p class="helper-note mt-space-4">If you want to assess several people, you can move on to the next step later.</p>
    </div>
  </div>
  <div class="photo-stack" aria-hidden="true">
    <img class="photo-back" src="{photo_back}" alt=""/>
    <img class="photo-front" src="{photo_front}" alt=""/>
  </div>
</div>
</section>""",
        unsafe_allow_html=True,
    )


def render_pro_welcome():
    _page(
        "Professional Welcome",
        "Entry for discharge planners and partners.",
        [("Pro Contextual", "pro_welcome_contextual")],
    )


def render_pro_welcome_contextual():
    _page(
        "Pro Contextual Welcome",
        "Contextualized pro entry.",
        [("Professionals", "professionals")],
    )


def render_professionals():
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
    _page(
        "Login",
        "Auth form placeholder.",
        [("My Account", "my_account")],
    )


def render_ai_advisor():
    _page("AI Advisor (Navi)", "Conversation surface placeholder.")


def render_documents():
    _page("Documents", "Uploads and document listing. Auth required.")


def render_exports():
    _page("Exports", "PDF/CSV bundle generator. Auth required.")


def render_waiting_room():
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
    _page("Trusted Partners", "Partner directory and disclosures.")


def render_my_account():
    _page(
        "My Account",
        "Profile, preferences, and consent history.",
        [("Privacy Policy", "privacy"), ("Terms of Use", "terms")],
    )


def render_terms():
    _page("Terms of Use", "Versioned legal surface.")


def render_privacy():
    _page("Privacy Policy", "Versioned privacy surface.")


def render_about():
    _page("About Us", "Company, mission, and contact.")
