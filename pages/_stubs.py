from typing import List, Optional, Tuple

import streamlit as st

from core.nav import route_to


def _page(title: str, desc: str, ctas: Optional[List[Tuple[str, str]]] = None):
    st.header(title)
    st.write(desc)
    if ctas:
        for label, target in ctas:
            if st.button(label, key=f"cta-{title}-{target}"):
                route_to(target)


def render_welcome():
    st.markdown(
        """
<section class="container stack">
  <div class="grid">
    <div class="card grid-span-7 stack-sm">
      <div class="card-head">Welcome to Senior Navigator</div>
      <div class="card-meta">Clarity for seniors, caregivers, and professionals.</div>
      <p>Start a guided plan or explore resources. You can switch at any time.</p>
      <div class="card-actions mt-space-4">
        <a class="btn btn--primary" href="?page=welcome_contextual">Get Started</a>
        <a class="btn btn--secondary" href="?page=professionals">I’m a Professional</a>
      </div>
    </div>
    <div class="card grid-span-5 text-center">
      <img class="img-responsive img-rounded" src="/static/images/Hero.png" alt="Senior Navigator" />
    </div>
  </div>
  <div class="banner banner--info">
    National guidance with local context. You control how much you share.
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_contextual():
    st.markdown(
        """
<section class="container stack">
  <div class="grid">
    <article class="card grid-span-6 stack-sm">
      <div class="card-head">Who are you planning for?</div>
      <div class="choice-pills mt-space-4">
        <span class="pill is-selected">Myself</span>
        <span class="pill">A loved one</span>
        <span class="pill">A patient (professional)</span>
      </div>
      <div class="card-actions mt-space-4">
        <a class="btn btn--primary" href="?page=waiting_room">Continue</a>
        <a class="btn btn--ghost" href="?page=welcome">Back</a>
      </div>
    </article>
    <article class="card grid-span-6 text-center">
      <img class="img-responsive img-rounded" src="/static/images/contextual_welcome_self.png" alt="Contextual Welcome" />
    </article>
  </div>
</section>
        """,
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
    st.markdown(
        """
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
      <img class="img-responsive img-rounded" src="/static/images/login.png" alt="Status" />
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
