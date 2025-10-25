"""
GCP v4 Intro Page - Custom centered layout with refreshed copy

Goals:
- Keep Navi header from product shell untouched
- Introduce warmer, context-aware lead copy with bullet reminders
- Maintain hero image on the right with subtle tilt
"""

import json
from html import escape as html_escape
from typing import Any

import streamlit as st

from core.content_contract import build_token_context, resolve_content


@st.cache_resource
def _load_planning_bytes() -> bytes | None:
    try:
        with open("static/images/planning.png", "rb") as f:
            return f.read()
    except Exception:
        return None


def load_intro_overrides() -> dict[str, Any]:
    """Load intro copy overrides from config, supporting legacy filename."""
    paths = [
        "config/gcp_intro.overrides.json",
        "config/gcp_intro_overrides.json",
    ]
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            continue
    return {}


def render_intro_step() -> None:
    """Render the custom intro step with responsive layout and tailored copy."""
    # Resolve content (overrides + tokens) using current session context
    ctx = build_token_context(st.session_state, snapshot=None)
    overrides = load_intro_overrides()
    resolved = resolve_content({"copy": overrides.get("copy", {})}, context=ctx)
    copy = resolved.get("copy", {})

    # Determine helper copy based on who the plan is for
    relationship = st.session_state.get("planning_for_relationship", "")
    relationship_type = st.session_state.get("relationship_type", "")
    is_self = relationship == "self" or relationship_type == "Myself"

    helper_text = copy.get("helper_self") if is_self else copy.get("helper_supporter")
    if not helper_text:
        helper_text = copy.get("helper")
    if helper_text:
        helper_text = html_escape(helper_text)

    title_text = html_escape(copy.get("page_title", ""))
    lead_text = html_escape(copy.get("lead", ""))

    points = [point for point in copy.get("points", []) if point]
    points_html = ""
    if points:
        items = "".join(
            f"<li><span class='dot'></span><span>{html_escape(point)}</span></li>" for point in points
        )
        points_html = f"<ul class='intro-points'>{items}</ul>"

    # Prepare hero image markup (single source, placed differently per breakpoint)
    hero_bytes = _load_planning_bytes()
    if hero_bytes:
        import base64

        encoded = base64.b64encode(hero_bytes).decode("utf-8")
        hero_block = (
            "<div class='gcp-hero-card'>"
            f"<img class='gcp-hero-img' src='data:image/png;base64,{encoded}' alt='Planning together at a table' />"
            "</div>"
        )
    else:
        hero_block = (
            "<div class='gcp-hero-card placeholder'>"
            "<div class='placeholder-text'>We'll add a guiding image here soon.</div>"
            "</div>"
        )

    hero_desktop = f"<div class='intro-media intro-media--desktop'>{hero_block}</div>"
    hero_mobile = f"<div class='intro-media intro-media--mobile'>{hero_block}</div>"

    # Inject scoped CSS for layout and typography (ASCII only)
    st.markdown(
        """
        <style>
          #gcp-intro.intro-wrap { max-width: 1100px; margin: -8px auto 0; padding: 0 24px 20px; }
          #gcp-intro .intro-grid { display: grid; grid-template-columns: minmax(0,1.05fr) minmax(0,0.95fr); gap: 32px; align-items: center; }
          #gcp-intro .intro-copy { display: flex; flex-direction: column; gap: 14px; }
          #gcp-intro .intro-heading { font-size: 1.9rem; font-weight: 700; color: #0d1f4b; margin: 0; line-height: 1.2; }
          #gcp-intro .lead { font-size: 1.08rem; color: #1f2a44; line-height: 1.6; margin: 0; max-width: 60ch; }
          #gcp-intro .helper { color: #1f3c88; font-size: 1rem; font-weight: 600; margin: 4px 0 0; }
          #gcp-intro .intro-points { margin: 12px 0 0; padding: 0; list-style: none; }
          #gcp-intro .intro-points li { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 10px; color: #1f2937; font-size: 0.98rem; line-height: 1.5; }
          #gcp-intro .intro-points li .dot { width: 12px; height: 12px; border-radius: 50%; background: #1f3c88; margin-top: 6px; flex-shrink: 0; }
          #gcp-intro .intro-media { display: flex; justify-content: flex-end; }
          #gcp-intro .intro-media--mobile { display: none !important; justify-content: center; margin: 4px 0 0; }
          .gcp-hero-card { border-radius: 16px; box-shadow: 0 18px 32px rgba(16,24,40,.18); overflow: hidden; background: #fff; border: 12px solid #fff; width: clamp(260px, 34vw, 440px); transform: rotate(5deg); transform-origin: center; }
          .gcp-hero-card.placeholder { display: flex; align-items: center; justify-content: center; padding: 24px; }
          .gcp-hero-card .placeholder-text { color: #475569; font-weight: 500; text-align: center; }
          .gcp-hero-img { width: 100%; height: auto; border-radius: 12px; display: block; }
          @media (max-width: 900px) {
            #gcp-intro .intro-grid { grid-template-columns: 1fr; gap: 20px; }
            #gcp-intro .intro-copy { gap: 12px; }
            #gcp-intro .intro-media--desktop { display: none !important; }
            #gcp-intro .intro-media--mobile { display: flex !important; order: 1; }
            #gcp-intro .intro-copy > .lead { order: 2; }
            #gcp-intro .intro-copy > .helper { order: 3; }
            #gcp-intro .intro-copy > .intro-points { order: 4; }
            .gcp-hero-card { width: clamp(220px, 78vw, 360px); transform: rotate(3deg); }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    layout_html = f"""
        <div id=\"gcp-intro\" class=\"intro-wrap\">
          <div class=\"intro-grid\">
            <div class=\"intro-copy\">
              <div class=\"intro-heading\">{title_text}</div>
              {hero_mobile}
              <p class=\"lead\">{lead_text}</p>
              {f"<p class='helper'>{helper_text}</p>" if helper_text else ""}
              {points_html}
            </div>
            {hero_desktop}
          </div>
        </div>
    """

    st.markdown(layout_html, unsafe_allow_html=True)


def should_use_custom_intro() -> bool:
    current_step_id = st.session_state.get("gcp_current_step_id", "")
    return current_step_id == "intro"


def render_custom_intro_if_needed() -> bool:
    if should_use_custom_intro():
        render_intro_step()
        return True
    return False
