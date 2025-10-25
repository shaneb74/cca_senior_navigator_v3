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
            import base64
            b64 = base64.b64encode(hero).decode("utf-8")
            st.markdown(
                f"""
                <div class="gcp-hero-card">
                  <img class="gcp-hero-img" src="data:image/png;base64,{b64}" alt="Planning together at a table" />
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("📋 Planning your care journey...")

    # Minimal CSS clamp for hero and responsive stacking
        st.markdown(
                """
                <style>
                    /* Card styling for hero */
                    .gcp-hero-card {
                            border-radius: 12px;
                            box-shadow: 0 12px 28px rgba(16, 24, 40, 0.18);
                            overflow: hidden;
                            background: #ffffff;
                            border: 10px solid #ffffff; /* Polaroid-style frame */
                            width: clamp(220px, 28vw, 380px); /* Significantly reduced size */
                            transform: rotate(24deg); /* Natural tilt */
                            transform-origin: center;
                    }
                        .gcp-hero-img { width: 100%; height: auto; border-radius: 8px; display: block; }
                    @media (max-width: 900px) {
                            .gcp-hero-card { width: clamp(200px, 60vw, 320px); }
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