"""
GCP v4 Intro Page - Custom two-column layout with hero image

Visual-only restyle:
- Two-column responsive layout (text left, image right)
- Hero image with rounded frame and shadow
- Copy via overrides with token interpolation
- Single page title handled by module header (no duplicates here)
"""

import json
import streamlit as st

from core.content_contract import build_token_context, resolve_content


@st.cache_resource
def _load_planning_bytes() -> bytes | None:
    try:
        with open("static/images/planning.png", "rb") as f:
            return f.read()
    except Exception:
        return None


def load_intro_overrides() -> dict:
    """Load intro copy overrides from config.

    Prefers config/gcp_intro.overrides.json; falls back to legacy underscore name.
    """
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
    """Render custom intro step with two-column layout and hero image.

    Header/title is rendered by the module engine; we render body + hero only.
    """
    # Resolve content (overrides + tokens)
    ctx = build_token_context(st.session_state, snapshot=None)
    overrides = load_intro_overrides()
    resolved = resolve_content({"copy": overrides.get("copy", {})}, context=ctx)
    C = resolved.get("copy", {})

    # Two-column layout: text left, image right
    col1, col2 = st.columns([7, 5], vertical_alignment="center")

    with col1:
        st.markdown(C.get("lead", ""))
        st.caption(C.get("helper", ""))

    with col2:
        hero = _load_planning_bytes()
        if hero:
            st.image(hero, use_container_width=True, caption=None)
        else:
            st.info("📋 Planning your care journey...")

    # Minimal CSS clamp for hero and responsive stacking
    st.markdown(
        """
        <style>
          /* Prefer scoping to Streamlit image container */
          .stImage img { max-width: 560px; height: auto; }
          @media (max-width: 900px) {
            .stImage img { max-width: 100%; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def should_use_custom_intro() -> bool:
    current_step_id = st.session_state.get("gcp_current_step_id", "")
    return current_step_id == "intro"


def render_custom_intro_if_needed() -> bool:
    if should_use_custom_intro():
        render_intro_step()
        return True
    return False