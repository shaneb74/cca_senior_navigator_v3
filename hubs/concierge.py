import streamlit as st

from core.ui import hub_section, tile_close, tile_open, tiles_close, tiles_open


def render():
    hub_section("Dashboard", right_meta='Assessment <span class="badge">For someone</span> <span class="badge">John</span>')
    tiles_open()

    tile_open("md")
    st.markdown(
        """<div class="tile-head">
  <div class="tile-title">Understand the situation</div>
  <span class="badge info">Guided Care Plan</span>
</div>
<p class="tile-meta">Recommendation<br><strong>In-Home Care</strong></p>
<div class="kit-row">
  <a class="btn btn--primary" href="?page=gcp">Start Assessment</a>
  <a class="btn btn--secondary" href="?page=ai_advisor">See responses</a>
  <a class="btn btn--ghost" href="?page=welcome_contextual">Start over</a>
</div>""",
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        """<div class="tile-head">
  <div class="tile-title">Understand the costs</div>
  <span class="badge info">Cost Estimator</span>
</div>
<p class="tile-meta">Assess cost structure across care settings. Estimate updates automatically.</p>
<div class="kit-row">
  <a class="btn btn--primary" href="?page=waiting_room">Start</a>
  <span class="tile-meta">Next step ✽</span>
</div>""",
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        """<div class="tile-head">
  <div class="tile-title">Connect with an advisor to plan the care</div>
  <span class="badge info">Get Connected</span>
</div>
<p class="tile-meta">Whenever you’re ready to meet with an advisor.</p>
<div class="kit-row">
  <a class="btn btn--primary" href="?page=waiting_room">Get connected</a>
</div>""",
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        """<div class="tile-head">
  <div class="tile-title">FAQs &amp; Answers</div>
  <span class="badge info">AI Agent</span>
</div>
<p class="tile-meta">Receive instant, tailored assistance from our advanced AI chat.</p>
<div class="kit-row">
  <a class="btn btn--primary" href="?page=ai_advisor">Open</a>
</div>""",
        unsafe_allow_html=True,
    )
    tile_close()

    tiles_close()
