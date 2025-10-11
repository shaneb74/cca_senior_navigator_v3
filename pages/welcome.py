import streamlit as st

from core.ui import img_src
from ui.welcome_shared import inject_welcome_css


def render():
    inject_welcome_css()

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
      <a class="btn btn--primary wl-btn" href="?page=welcome_contextual">Start Now</a>
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
