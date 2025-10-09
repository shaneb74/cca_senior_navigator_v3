import streamlit as st

from core.ui import hub_section, tile_close, tile_open, tiles_close, tiles_open


def _status_badge(done: bool) -> str:
    txt = "Completed ✓" if done else "Next step ✽"
    cls = "badge success" if done else "badge"
    return f'<span class="{cls}">{txt}</span>'


def _btn(label: str, href: str, kind: str = "primary") -> str:
    return f'<a class="btn btn--{kind}" href="{href}">{label}</a>'


def render():
    meta = 'Assessment <span class="badge">For someone</span> <span class="badge">John</span>'
    hub_section("Dashboard", right_meta=meta)

    gcp_done = bool(st.session_state.get("gcp_completed", False))
    cost_done = bool(st.session_state.get("cost_planner_completed", False))
    advisor_done = bool(st.session_state.get("advisor_completed", False))

    tiles_open()

    tile_open("md")
    st.markdown(
        f"""
      <div class="tile-head">
        <div class="tile-title">Guided Care Plan</div>
        <span class="badge info">Guided Care Plan</span>
      </div>
      <p class="tile-meta">Understand health, safety, and care needs to determine the right care setting.</p>
      <div class="kit-row">
        {_btn("See responses", "?page=gcp", "secondary")}
        {_btn("Start over", "?page=gcp", "ghost")}
        {_status_badge(gcp_done)}
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        f"""
      <div class="tile-head">
        <div class="tile-title">Cost Planner</div>
        <span class="badge info">Cost Estimator</span>
      </div>
      <p class="tile-meta">Estimate and plan costs for each care option, with automatic updates based on your selections.</p>
      <div class="kit-row">
        {_btn("Start", "?page=cost_planner")}
        {_status_badge(cost_done)}
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        f"""
      <div class="tile-head">
        <div class="tile-title">Plan with My Advisor</div>
        <span class="badge info">Get Connected</span>
      </div>
      <p class="tile-meta">Work one-on-one with a certified care advisor to review options and next steps.</p>
      <div class="kit-row">
        {_btn("Get connected", "?page=waiting_room")}
        {_status_badge(advisor_done)}
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        f"""
      <div class="tile-head">
        <div class="tile-title">FAQs &amp; Answers</div>
        <span class="badge info">AI Agent</span>
      </div>
      <p class="tile-meta">Receive instant, tailored assistance from our advanced AI chat.</p>
      <div class="kit-row">
        {_btn("Open", "?page=ai_advisor")}
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tiles_close()

    hub_section("Additional services")
    tiles_open()

    tile_open("md")
    st.markdown(
        f"""
      <div class="tile-head">
        <div class="tile-title">AI Health Check</div>
      </div>
      <p class="tile-meta">Get insights about overall body health.</p>
      <div class="kit-row">
        {_btn("Open", "?page=trusted_partners&partner=seniorlife")}
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        f"""
      <div class="tile-head">
        <div class="tile-title">Resource Library</div>
      </div>
      <p class="tile-meta">Media Center</p>
      <div class="kit-row">
        {_btn("Open", "?page=hub_learning")}
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tiles_close()
