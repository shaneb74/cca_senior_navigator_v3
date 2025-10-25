"""
GCP v4 Intro Page - Custom centered layout with compact Navi and hero

Visual/design goals:
- Centered container with two-column responsive grid
- Compact Navi (no banners) with title + single line
- Hero image with subtle tilt and frame
- Copy via overrides with token interpolation
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

    Header title may be shown by the engine; this view focuses on Navi + body + hero.
    """
    # Resolve content (overrides + tokens)
    ctx = build_token_context(st.session_state, snapshot=None)
    overrides = load_intro_overrides()
    resolved = resolve_content({"copy": overrides.get("copy", {})}, context=ctx)
    C = resolved.get("copy", {})

    # Inject page-scoped CSS (wrapper, grid, hero, and compact Navi reset)
    st.markdown(
        """
        <style>
          /* Centered wrapper */
          #gcp-intro.intro-wrap { max-width: 1100px; margin: 0 auto; padding: 8px 24px 24px; }
          #gcp-intro h3 { margin: 10px 0 8px; }
          #gcp-intro .lead { margin-top: 8px; font-size: 1.05rem; color: #0d1f4b; line-height: 1.5; }
          #gcp-intro .helper { color: #6b7280; font-size: 0.9rem; margin-top: 4px; }
          #gcp-intro .intro-grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 28px; align-items: center; }

          /* Tilted hero card */
          .gcp-hero-card { border-radius: 12px; box-shadow: 0 12px 28px rgba(16,24,40,.18); overflow: hidden; background: #fff; border: 10px solid #fff; width: clamp(240px, 32vw, 440px); transform: rotate(18deg); transform-origin: center; }
          .gcp-hero-img { width: 100%; height: auto; border-radius: 8px; display: block; }

          @media (max-width: 900px) {
            #gcp-intro .intro-grid { grid-template-columns: 1fr; gap: 18px; }
            .gcp-hero-card { width: clamp(220px, 70vw, 360px); }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Wrapper start
    st.markdown('<div id="gcp-intro" class="intro-wrap">', unsafe_allow_html=True)

    # Compact Navi (title + one line only)
    try:
        from core.ui import render_navi_panel_v2
        render_navi_panel_v2(
            title=C.get("navi_title"),
            reason=C.get("navi_line", ""),
            encouragement={"icon": "", "text": "", "status": "in_progress"},
            context_chips=[],
            primary_action={"label": "", "route": ""},
            variant="compact",
        )
    except Exception:
        pass

    # Two-column layout: text left, image right
    st.markdown('<div class="intro-grid">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div>
          <h3>{C.get('page_title','')}</h3>
          <p class="lead">{C.get('lead','')}</p>
          <p class="helper">{C.get('helper','')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hero column
    hero = _load_planning_bytes()
    if hero:
        import base64
        b64 = base64.b64encode(hero).decode("utf-8")
        st.markdown(
            f"""
            <div class="hero">
              <div class="gcp-hero-card">
                <img class="gcp-hero-img" src="data:image/png;base64,{b64}" alt="Planning together at a table" />
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("📋 Planning your care journey...")

    st.markdown('</div>', unsafe_allow_html=True)  # end grid
    st.markdown('</div>', unsafe_allow_html=True)  # end wrapper


def should_use_custom_intro() -> bool:
    current_step_id = st.session_state.get("gcp_current_step_id", "")
    return current_step_id == "intro"


def render_custom_intro_if_needed() -> bool:
    if should_use_custom_intro():
        render_intro_step()
        return True
    return False