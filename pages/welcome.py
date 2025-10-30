from __future__ import annotations

import html
from collections.abc import Sequence
from textwrap import dedent

import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from core.state import is_authenticated
from core.ui import img_src
from core.url_helpers import add_uid_to_href
from layout import static_url  # Keep static_url for now
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple

# Phase 5: Contextual Guidance Layer
try:
    from apps.navi_core.context_manager import update_context
    from apps.navi_core.guidance_manager import get_guidance
    from apps.navi_core.progress_manager import mark_page_complete
    _GUIDANCE_AVAILABLE = True
except ImportError:
    _GUIDANCE_AVAILABLE = False

_CSS_FLAG = "_welcome_css_main"

_PILLS: dict[str, dict[str, str | None]] = {
    "someone": {
        "label": "For someone",
        "page": "pages/someone_else.py",
        "fallback": "for_someone",
    },
    "self": {
        "label": "For me",
        "page": "pages/self.py",
        "fallback": "for_me_contextual",
    },
    "pro": {
        "label": "Professional",
        "page": "pages/professionals.py",
        "fallback": None,
    },
}

_PILL_ROUTES = {
    "someone": "someone_else",
    "self": "self",
    "pro": "professionals",
}

_PILL_SETS: dict[str, Sequence[str]] = {
    "someone": ("someone", "self"),
    "self": ("someone", "self"),
    "pro": ("someone", "self", "pro"),
}


def _clean_html(markup: str) -> str:
    lines = dedent(markup).splitlines()
    return "\n".join(line.lstrip() for line in lines if line or line == "")


def _inject_welcome_css() -> None:
    if st.session_state.get(_CSS_FLAG):
        return

    css = dedent(
        """
        .welcome-brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink);}
        .welcome-brand__logo{height:32px;width:auto;display:block;}
        .welcome-brand__text{display:flex;flex-direction:column;font-weight:600;line-height:1.05;}
        .welcome-brand__text span:last-child{font-weight:700;font-size:1rem;}
        .welcome-header__inner{display:flex;align-items:center;justify-content:space-between;gap:24px;}
        .welcome-auth{margin-left:auto;display:flex;align-items:center;}

        /* hero spacing: provide breathing room now that the global container is flush */
        .section-hero{padding:24px 0 16px;}
        .hero-grid{
          display:grid;
          grid-template-columns:minmax(0,1.25fr) minmax(0,0.75fr);
          gap:36px;
          align-items:center;
        }

        .hero-eyebrow{font-weight:700;color:var(--brand-700);letter-spacing:.04em;margin-bottom:.75rem;}

        /* headline refined - increased by 20% more */
        .hero-title{
          font-weight:700;
          color:var(--ink);
          font-size:clamp(3.4rem,5.4vw,4.6rem);
          line-height:1.04;
          letter-spacing:-.01em;
          margin:0 0 16px;
          text-wrap:balance;
        }

        /* subhead 20% larger */
        .hero-sub{
          color:var(--ink-600);
          font-size:1.26rem;
          line-height:1.55;
          font-weight:500;
          max-width:60ch;
          width:100%;
          text-wrap:balance;
          text-align:left;
          hyphens:auto;
          margin:0 0 24px;
        }

        .cta-row{display:flex;gap:14px;flex-wrap:wrap;}
        .cta-row .btn--primary{background:linear-gradient(90deg,#2563eb,#3b82f6);border-color:#2563eb;}
        .welcome-hero-media{position:relative;display:flex;justify-content:flex-end;padding-right:2%;transform:scale(1.05);transform-origin:center right;}
        .welcome-hero-frame{position:relative;background:#fff;border-radius:24px;padding:14px;border:1px solid #e8eff8;box-shadow:0 26px 60px rgba(15,23,42,.18);transform:rotate(-2.2deg);}
        .welcome-hero-frame::after{content:"";position:absolute;inset:12px;border:1px solid rgba(15,23,42,.07);border-radius:18px;}
        .welcome-hero-photo{border-radius:18px;overflow:hidden;}
        .welcome-hero-photo img{display:block;border-radius:18px;}

        /* section header: tightened spacing dramatically */
        .section--tight{padding:4px 0 2px;}
        .welcome-section-title{
          text-transform:none;
          letter-spacing:.02em;
          font-size:1.35rem;
          margin:0 0 12px;
          color:var(--ink);
          font-weight:800;
        }

        /* Remove top padding from cards section to bring closer to title */
        .section--tight + .section{
          padding-top:0 !important;
        }

        .cards-2{display:grid;gap:32px;grid-template-columns:1fr 1fr;}
        .welcome-card{position:relative;padding:28px;border-radius:20px;background:#fff;border:1px solid #e6edf5;box-shadow:0 18px 42px rgba(15,23,42,.12);}
        .welcome-card-media{position:relative;margin-bottom:30px;}
        .welcome-card-media img{display:block;border-radius:16px;box-shadow:0 12px 32px rgba(15,23,42,.14);}
        /* .welcome-card-icon{position:absolute;top:-24px;right:20px;width:44px;height:44px;border-radius:16px;background:#f1f5ff;border:1px solid #dbe7ff;display:flex;align-items:center;justify-content:center;}
        .welcome-card-icon svg{width:22px;height:22px;fill:var(--brand-600);} */
        .welcome-card .card-head{font-size:1.05rem;margin-bottom:6px;font-weight:700;color:var(--ink);}
        .welcome-card .card-meta{color:var(--ink-500);margin-bottom:10px;font-size:.95rem;}
        .welcome-card .dashboard-description{color:var(--ink-500);margin-bottom:20px;line-height:1.55;}
        .welcome-card .card-actions{display:flex;justify-content:flex-end;}

        /* Professional Login section */
        .professional-login{
          padding:40px;
          background:#fff;
          border:1px solid #e6edf5;
          border-radius:20px;
          box-shadow:0 18px 42px rgba(15,23,42,.12);
          text-align:center;
        }
        .professional-login__title{
          font-size:1.5rem;
          font-weight:700;
          color:var(--ink);
          margin:0 0 12px;
        }
        .professional-login__message{
          font-size:1.05rem;
          color:var(--ink-600);
          margin:0 0 20px;
        }
        .professional-login__roles{
          font-size:0.95rem;
          color:var(--ink-500);
          margin:0 0 28px;
          font-weight:500;
        }
        .professional-login__button .btn{
          display:inline-flex;
          align-items:center;
          justify-content:center;
          height:auto;
          padding:12px 32px;
          border-radius:12px;
          background:#111827;
          color:#fff;
          text-decoration:none;
          font-weight:700;
          font-size:1rem;
          transition:all 0.2s ease;
        }

        .welcome-context-sentinel,
        .context-card-sentinel{display:none;}
        @supports(selector(div:has(.welcome-context-sentinel))){
          div.block-container:has(.welcome-context-sentinel){
            padding-top:0!important;
            padding-bottom:0!important;
          }
          div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel){
            background:#fff;
            padding:40px 0;
          }
          div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel) > div[data-testid="stHorizontalBlock"]{
            max-width:880px;
            width:100%;
            margin:0 auto;
            padding:0 24px;
            gap:40px;
            align-items:center;
            flex-wrap:nowrap;
          }
          div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]{
            padding:0!important;
          }
          div[data-testid="column"]:has(.context-card-sentinel){
            display:flex;
          }
          div[data-testid="column"]:has(.context-card-sentinel) > div[data-testid="stVerticalBlock"]{
            background:#fff;
            border-radius:24px;
            padding:36px 36px 32px;
            box-shadow:0 28px 68px rgba(15,23,42,.18);
            border:1px solid rgba(210,223,255,.72);
            width:100%;
          }
          div[data-testid="column"]:has(.context-card-sentinel) div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]{
            margin:0;
          }
        }
        @supports(selector(div:has(.welcome-context-sentinel))){
          @media(max-width:1024px){
            div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel){
              padding:32px 0;
            }
            div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel) > div[data-testid="stHorizontalBlock"]{
              flex-direction:column;
              gap:28px;
            }
            div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child{
              order:2;
            }
            div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child{
              order:1;
            }
          }
        }
        .context-card{position:relative;background:#fff;border-radius:24px;padding:36px 36px 32px;box-shadow:0 28px 68px rgba(15,23,42,.18);}
        .context-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:22px;gap:16px;}
        .context-pill-group{display:flex;gap:8px;flex-wrap:wrap;}
        .context-pill-link{
          display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:999px;
          border:1px solid #d9e3f8;background:#f1f4ff;color:#1f2937;font-weight:700;text-decoration:none;
          font-size:.95rem;transition:all .18s ease;line-height:1;
        }
        .context-pill-link svg{width:18px;height:18px;fill:#64748b;}
        .context-pill-link.is-active{background:#111827;border-color:#111827;color:#fff;box-shadow:0 12px 28px rgba(17,24,39,.35);}
        .context-pill-link.is-active svg{fill:#fff;}
        .context-pill-link:hover:not(.is-active){background:#e5ecff;border-color:#c7d7fb;color:#0f172a;}
        .context-close{
          display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:50%;
          background:#eef2ff;border:1px solid #dbe3ff;color:#475569;font-size:1.2rem;font-weight:700;text-decoration:none;
        }
        .context-close:hover{background:#e1e7ff;color:#1f2937;}
        .context-title{font-size:1.35rem;font-weight:700;margin:12px 0 28px;line-height:1.45;}
        
        /* === White Background (Reset from Blue Gradient) === */
        
        /* White background globally */
        .stApp {
          background-color: #ffffff !important;
        }
        
        /* Centered card container */
        .audience-card {
          background: #ffffff;
          border-radius: 20px;
          padding: 2.5rem;
          max-width: 560px;
          box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
          position: relative;
          z-index: 5;
        }
        
        /* Pills container */
        .pill-container {
          display: flex;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        
        /* Pill wrapper styling */
        .pill-wrapper {
          flex: 1;
        }
        
        .pill-wrapper .stButton button {
          border-radius: 999px !important;
          font-weight: 600 !important;
          padding: 0.5rem 1.2rem !important;
          background: #F3F6FA !important;
          color: #1B2A4A !important;
          border: 1px solid #E0E5ED !important;
          transition: all 0.25s ease-in-out !important;
          font-size: 0.95rem !important;
          width: 100% !important;
          cursor: pointer !important;
        }
        
        /* Active pill: Black background */
        .pill-wrapper.active .stButton button {
          background: #0B132B !important;
          color: #fff !important;
          border: none !important;
        }
        
        /* Hover effect */
        .pill-wrapper .stButton button:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.08) !important;
        }
        
        /* Hero image positioning - positioned absolutely to overlap */
        .audience-background {
          position: absolute !important;
          right: 0;
          top: 60px;
          width: 50%;
          max-width: 700px;
          z-index: 1;
          opacity: 0.95;
        }
        
        /* Ensure card content is above background */
        .audience-card * {
          position: relative;
          z-index: 10;
        }
        
        /* Adjust context styling for centered card layout */
        @supports(selector(div:has(.welcome-context-sentinel))){
          div.block-container:has(.welcome-context-sentinel){
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: none !important;
          }
          div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel){
            background: transparent !important;
            padding: 40px 0;
          }
          div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel) > div[data-testid="stHorizontalBlock"]{
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
            padding: 0 24px;
            gap: 60px;
            align-items: center;
            flex-wrap: nowrap;
          }
        }
        
        /* Active pill: Deep navy gradient with glow */
        .context-top .stButton button[data-baseweb="button"][kind="primary"] {
          background: linear-gradient(180deg, #0B132B, #1E254A) !important;
          color: white !important;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
          border: none !important;
        }
        
        /* Accessibility: Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
          .context-top .stButton>button {
            transition: none !important;
          }
        }
        
        /* Mobile: Stack pills vertically */
        @media (max-width: 768px) {
          .audience-toggle-container {
            flex-direction: column;
          }
          .context-top .stButton {
            width: 100%;
          }
        }
        
        /* Smooth fade-in to eliminate visible flashing on state updates */
        .stApp {
          animation: fadein 0.2s ease-in;
        }
        @keyframes fadein {
          from { opacity: 0.92; }
          to { opacity: 1; }
        }
        
        .context-form-section{margin-bottom:20px;}
        .context-label{display:block;font-weight:600;color:var(--ink);margin-bottom:8px;font-size:.95rem;}
        .context-form-row{display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap;}
        .context-input{flex:1 1 220px;}
        .context-submit{flex:0 0 160px;}
        .context-submit .stButton{width:100%;}
        .context-submit .stButton button{width:100%;height:48px;border-radius:14px;font-weight:700;border:none;background:linear-gradient(90deg,#2563eb,#3b82f6);color:#fff !important;}
        .context-note{margin-top:24px;background:#eaf2ff;border:1px solid #d5e4ff;border-radius:16px;padding:16px 20px;color:#1f3b7a;font-size:.95rem;font-weight:500;}
        .context-image{position:relative;display:flex;justify-content:center;align-items:center;padding:12px;}
        .context-collage{position:relative;display:inline-block;}
        .context-collage__base{margin:0;position:relative;display:block;padding:22px;background:#fff;border-radius:30px;box-shadow:0 40px 70px rgba(15,23,42,.22);transform:rotate(-4deg);}
        .context-collage__base img{display:block;border-radius:22px;width:100%;max-width:520px;}
        .context-collage__photo{position:absolute;box-shadow:0 26px 60px rgba(15,23,42,.24);border-radius:24px;background:#fff;padding:16px;}
        .context-collage__photo--one{right:-8%;top:6%;width:52%;transform:rotate(8deg);}
        .context-collage__photo--two{right:4%;bottom:-14%;width:48%;transform:rotate(-10deg);}
        .context-collage__photo img{display:block;border-radius:18px;}

        .welcome-footer{background:#fff;border-top:1px solid #e6edf5;margin-top:88px;padding:28px 0;}
        .welcome-footer .welcome-footer-grid{display:none!important;}
        .welcome-footer-bottom.ordered-footer{display:flex;flex-wrap:wrap;gap:18px;align-items:center;color:var(--ink-500);font-size:.95rem;}
        .welcome-footer-bottom.ordered-footer a{text-decoration:none;color:var(--ink-500);font-weight:500;}
        .welcome-footer-bottom.ordered-footer a:hover{color:var(--ink);}

        @media(min-width:1280px){
          .hero-grid { gap: 28px; }
        }
        @media(max-width:1024px){
          .hero-grid{grid-template-columns:1fr;gap:32px;}
          .welcome-hero-media{padding-right:0;justify-content:center;}
          .cards-2{grid-template-columns:1fr;}
          .welcome-context__inner{grid-template-columns:1fr;}
        }
        @media(max-width:720px){
          .context-form-row{flex-direction:column;}
          .context-submit{width:100%;flex:1 1 auto;}
          .context-note{font-size:.9rem;}
        }
        @media(max-width:420px){
          .hero-title{font-size:2.2rem;line-height:1.08;}
        }
        """
    )

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.session_state[_CSS_FLAG] = True


def _go_to(page_path: str | None, fallback_route: str | None) -> None:
    # Always use route_to() for consistent navigation behavior
    # This ensures UID is preserved and navigation stays in same tab
    if fallback_route:
        try:
            route_to(fallback_route)
        except Exception:
            pass


def render_welcome_card(
    *,
    active: str,
    title: str,
    placeholder: str,
    note: str,
    image_path: str,
    submit_route: str | None = "hub_lobby",
) -> None:
    _inject_welcome_css()

    safe_active = active if active in _PILLS else "someone"
    pill_keys = _PILL_SETS.get(safe_active, ("someone", "self"))

    photo_data = img_src(image_path)
    alt_text = {
        "someone": "Care team supporting family members",
        "self": "Senior smiling outdoors",
        "pro": "Advisor supporting clients",
    }.get(safe_active, "Welcome illustration")

    context_container = st.container()
    with context_container:
        st.markdown('<span class="welcome-context-sentinel"></span>', unsafe_allow_html=True)
        left_col, right_col = st.columns([1.05, 0.95], gap="large")

    pill_links = []
    for key in pill_keys:
        cfg = _PILLS[key]
        route = _PILL_ROUTES.get(key) or cfg.get("fallback") or "welcome"
        # REMOVED: SVG icons that were causing black blob flash during transitions
        icon = ""  # No icons - they were causing the flash
        classes = "context-pill-link"
        if key == safe_active:
            classes += " is-active"

        # Build aria-current attribute separately to avoid quote nesting issues
        aria_attr = 'aria-current="page"' if key == safe_active else ""
        href_with_uid = add_uid_to_href(f"?page={route}")
        pill_links.append(
            f"<a href='{href_with_uid}' class='{classes}' data-pill='{key}' {aria_attr}>{icon}<span>{html.escape(cfg['label'])}</span></a>"
        )

    with left_col:
        st.markdown('<span class="context-card-sentinel"></span>', unsafe_allow_html=True)

        back_href = add_uid_to_href("?page=welcome")
        st.markdown(
            _clean_html(
                f"""
                <div class="context-top">
                  <div class="context-pill-group">{"".join(pill_links)}</div>
                  <a class="context-close" href="{back_href}" aria-label="Back to welcome">×</a>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<h1 class="context-title">{html.escape(title)}</h1>',
            unsafe_allow_html=True,
        )

        form = st.form(f"welcome-form-{safe_active}", clear_on_submit=False)
        with form:
            st.markdown('<div class="context-form-row">', unsafe_allow_html=True)
            input_col, button_col = st.columns([3, 2], gap="small")
            with input_col:
                st.markdown('<div class="context-input">', unsafe_allow_html=True)
                name_value = st.text_input(
                    placeholder,
                    key=f"welcome-name-{safe_active}",
                    label_visibility="collapsed",
                    placeholder=placeholder,
                )
                st.markdown("</div>", unsafe_allow_html=True)
            with button_col:
                st.markdown('<div class="context-submit">', unsafe_allow_html=True)
                submitted = st.form_submit_button("Continue")
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Handle form submission - allow navigation with or without a name
        if submitted:
            # Store relationship context using standard relationship_type
            if safe_active == "someone":
                st.session_state["relationship_type"] = "Parent"  # Default for planning for someone else
                st.session_state["planning_for_relationship"] = "someone_else"
            elif safe_active == "self":
                st.session_state["relationship_type"] = "Myself"
                st.session_state["planning_for_relationship"] = "self"

            # Store person's name for personalization throughout the app
            from core.state_name import set_person_name
            if name_value and name_value.strip():
                set_person_name(name_value.strip())
            else:
                # Clear names if exists, allowing generic terms to be used
                set_person_name("")

            # Navigate regardless of whether name was provided
            if submit_route:
                _go_to(None, submit_route)

        clean_note = note.strip()
        if clean_note:
            st.markdown(
                f'<div class="context-note">{html.escape(clean_note)}</div>',
                unsafe_allow_html=True,
            )

    with right_col:
        if photo_data:
            st.markdown(
                '<div class="context-image"><div class="context-collage">'
                f'<figure class="context-collage__base"><img src="{photo_data}" alt="{html.escape(alt_text)}" /></figure>'
                "</div></div>",
                unsafe_allow_html=True,
            )
        elif safe_active == "someone":
            base_img = static_url("contextual_someone_else.png")
            st.markdown(
                _clean_html(
                    f"""
                    <div class="context-image">
                      <div class="context-collage">
                        <figure class="context-collage__base"><img src="{base_img}" alt="Family support collage" /></figure>
                      </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )


def _welcome_body(
    primary_label: str = "Start Now",
    primary_route: str = "someone_else",
    show_secondary: bool = True,
) -> str:
    """Generate welcome page body with dynamic CTA buttons.

    Args:
        primary_label: Text for primary button
        primary_route: Route for primary button (page name or route key)
        show_secondary: Whether to show the "Log in" button
    """
    hero_url = static_url("hero.png")
    family_main = static_url("welcome_someone_else.png")
    self_main = static_url("welcome_self.png")

    # Build CTA buttons with UID preservation
    primary_href = add_uid_to_href(f"?page={primary_route}")
    cta_html = (
        f'<a href="{primary_href}" class="btn btn--primary wl-btn">{html.escape(primary_label)}</a>'
    )
    if show_secondary:
        login_href = add_uid_to_href("?page=login")
        cta_html += (
            f'\n                      <a href="{login_href}" class="btn btn--secondary">Log in</a>'
        )

    return _clean_html(
        f"""
            <main>
              <section class="container section-hero">
                <div class="hero-grid">
                  <div>
                    <p class="hero-eyebrow">Concierge Care Advisors</p>
                    <h1 class="hero-title">Care decisions are hard. You don't have to make them alone.</h1>
                    <p class="hero-sub">
                      Get personalized guidance from a trusted advisor.
                      We help your family explore senior living options with clarity, care, and confidence—always at no cost.
                    </p>
                    <div class="cta-row">
                      {cta_html}
                    </div>
                  </div>
                  <div class="welcome-hero-media">
                    <div class="welcome-hero-frame">
                      <div class="welcome-hero-photo">
                        {f'<img src="{hero_url}" alt="Care professional supporting senior" />' if hero_url else ''}
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section class="container section section--tight">
                <h2 class="welcome-section-title">How we can help</h2>
              </section>

              <section class="container section">
                <div class="cards-2">
                  <article class="card welcome-card">
                    <div class="welcome-card-media">
                      {f'<img src="{family_main}" alt="Family gathering outdoors" />' if family_main else ''}
                    </div>
                    <p class="card-head">I would like to <strong>support my loved ones</strong></p>
                    <p class="card-meta">For a loved one</p>
                    <p class="dashboard-description">
                      Helping you make confident care decisions for someone you love.
                    </p>
                    <div class="card-actions">
                      <a href="{add_uid_to_href("?page=audience&mode=someone")}" class="btn btn--primary">For someone</a>
                    </div>
                  </article>

                  <article class="card welcome-card">
                    <div class="welcome-card-media">
                      {f'<img src="{self_main}" alt="Senior lifestyle" />' if self_main else ''}
                    </div>
                    <p class="card-head">I'm looking for <strong>support just for myself</strong></p>
                    <p class="card-meta">For myself</p>
                    <p class="dashboard-description">
                      Plan for your own future care with trusted guidance and peace of mind.
                    </p>
                    <div class="card-actions">
                      <a href="{add_uid_to_href("?page=audience&mode=self")}" class="btn btn--primary">For myself</a>
                    </div>
                  </article>
                </div>
              </section>

              <section class="container section">
                <div class="professional-login">
                  <h2 class="professional-login__title">Professional Login</h2>
                  <p class="professional-login__message">Login here to access your personalized dashboards.</p>
                  <p class="professional-login__roles">Discharge Planners • Nurses • Physicians • Social Workers • Geriatric Care Managers</p>
                  <div class="professional-login__button">
                    <a href="{add_uid_to_href("?page=hub_professional")}" class="btn btn--primary">🔐 For Professionals</a>
                  </div>
                </div>
              </section>
            </main>
            """
    )


def render(ctx: dict | None = None) -> None:
    """Render welcome page with adaptive behavior based on auth state."""
    # Phase 5: Track page context for contextual guidance
    if _GUIDANCE_AVAILABLE:
        update_context("Welcome")
        mark_page_complete("Welcome")
    
    # ============================================================
    # AUTHENTICATION DISABLED FOR DEVELOPMENT TESTING
    # ============================================================
    # Logout handler temporarily disabled - role switching removed
    # The following code is intentionally commented out:
    #
    # if st.query_params.get("logout") == "1":
    #     switch_to_member()
    #     st.query_params.clear()
    #     st.query_params["page"] = "welcome"
    #     st.rerun()
    # ============================================================

    _inject_welcome_css()

    # Determine button state based on authentication and planning context
    authenticated = is_authenticated()
    has_planning_context = st.session_state.get("planning_for_name") or st.session_state.get(
        "person_name"
    )

    # Button configuration based on state
    if not authenticated:
        # State: Not logged in - route to unified audience page
        primary_label = "Start Now"
        primary_route = "audience"
        show_secondary = True
    elif authenticated and not has_planning_context:
        # State: Logged in, no planning context - route to unified audience page
        primary_label = "Start Planning"
        primary_route = "audience"
        show_secondary = False
    else:
        # State: Logged in, planning context known
        # Use Navi's recommendation for next action
        next_action = MCIP.get_recommended_next_action()
        primary_label = "Continue where you left off"
        primary_route = next_action.get("route", "hub_lobby")
        show_secondary = False

    # Render with simple header/footer (no layout.py wrapper)
    render_header_simple(active_route="welcome")

    # Render body HTML directly
    body_html = _welcome_body(
        primary_label=primary_label,
        primary_route=primary_route,
        show_secondary=show_secondary,
    )
    st.markdown(body_html, unsafe_allow_html=True)

    render_footer_simple()


__all__ = ["render", "render_welcome_card"]
