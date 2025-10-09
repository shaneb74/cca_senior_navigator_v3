import streamlit as st
from core.ui import hub_section, tile_close, tile_open, tiles_close, tiles_open


def render():
    gcp_done = bool(st.session_state.get("gcp_completed"))
    cp_done = bool(st.session_state.get("cost_planner_completed"))
    medicaid_flag = st.session_state.get("flags", {}).get("medicaid", False)

    gcp_cta = (
        "<a class='btn btn--secondary' href='?page=gcp'>See responses</a>"
        if gcp_done
        else "<a class='btn btn--primary' href='?page=gcp'>Start</a>"
    )
    cp_cta = (
        "<a class='btn btn--primary' href='?page=cost_planner'>Open</a>"
        if cp_done
        else "<a class='btn btn--primary' href='?page=cost_planner'>Start</a>"
    )
    gcp_badge = "<span class='badge success'>Completed ✓</span>" if gcp_done else ""
    cp_badge = "<span class='badge success'>Completed ✓</span>" if cp_done else ""

    hub_section("Concierge Care Hub")
    tiles_open()

    tile_open("md")
    st.markdown(
        f"""
      <div class="tile-head">
        <div class="tile-title">Guided Care Plan</div>
        <span class="badge info">Decision support</span>
      </div>
      <p class="tile-meta">Answer a few questions to get a personalized next-step recommendation.</p>
      <div class="kit-row">
        {gcp_cta}
        <a class="btn btn--ghost" href="?page=gcp&reset=1">Start over</a>
        {gcp_badge}
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
        <span class="badge info">Estimate</span>
      </div>
      <p class="tile-meta">See an estimated monthly cost for the recommended care and adjust inputs.</p>
      <div class="kit-row">
        {cp_cta}
        {cp_badge}
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    advisor_cta = (
        "<span class='badge'>Unavailable for Medicaid</span>"
        if medicaid_flag
        else "<a class='btn btn--primary' href='?page=waiting_room'>Get connected</a>"
    )
    st.markdown(
        f"""
      <div class="tile-head">
        <div class="tile-title">Plan with my advisor</div>
        <span class="badge info">Get connected</span>
      </div>
      <p class="tile-meta">Meet with an advisor to map next steps.</p>
      <div class="kit-row">
        {advisor_cta}
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        """
      <div class="tile-head">
        <div class="tile-title">FAQs &amp; Answers</div>
        <span class="badge info">AI Agent</span>
      </div>
      <p class="tile-meta">Instant, tailored assistance from our AI agent, Navi.</p>
      <div class="kit-row">
        <a class="btn btn--primary" href="?page=ai_advisor">Open</a>
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tiles_close()

    hub_section("Additional Services")
    tiles_open()

    tile_open("md")
    st.markdown(
        """
      <div class="tile-head">
        <div class="tile-title">AI Health Check</div>
        <span class="badge info">Senior Life AI</span>
      </div>
      <p class="tile-meta">Cognitive health assessment from our trusted partner.</p>
      <div class="kit-row">
        <a class="btn btn--secondary" href="?page=trusted_partners">Open in Trusted Partners</a>
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tile_open("md")
    st.markdown(
        """
      <div class="tile-head">
        <div class="tile-title">Resource Library</div>
        <span class="badge info">Learning Center</span>
      </div>
      <p class="tile-meta">Guides, checklists, and definitions to help you prepare.</p>
      <div class="kit-row">
        <a class="btn btn--secondary" href="?page=hub_learning">Open</a>
      </div>
    """,
        unsafe_allow_html=True,
    )
    tile_close()

    tiles_close()
