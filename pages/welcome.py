from __future__ import annotations

import html
from textwrap import dedent
from typing import Dict, Optional, Sequence

import streamlit as st

from core.nav import route_to
from core.ui import img_src
from layout import render_page, static_url

_CSS_FLAG = "_welcome_css_main"

_PILLS: Dict[str, Dict[str, Optional[str]]] = {
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

_PILL_SETS: Dict[str, Sequence[str]] = {
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
        .header{display:none!important;}
        .welcome-brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--ink);}
        .welcome-brand__logo{height:32px;width:auto;display:block;}
        .welcome-brand__text{display:flex;flex-direction:column;font-weight:600;line-height:1.05;}
        .welcome-brand__text span:last-child{font-weight:700;font-size:1rem;}
        .welcome-header__inner{display:flex;align-items:center;justify-content:space-between;gap:24px;}
        .welcome-auth{margin-left:auto;display:flex;align-items:center;}

        /* spacing tightened */
        .section-hero{padding:56px 0 28px;}
        .hero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:32px;align-items:center;}

        .hero-eyebrow{font-weight:700;color:var(--brand-700);letter-spacing:.04em;margin-bottom:.75rem;}

        /* headline refined */
        .hero-title{
          font-weight:700;
          color:var(--ink);
          font-size:clamp(2.6rem,4.2vw,3.6rem);
          line-height:1.06;
          letter-spacing:-.01em;
          margin:0 0 16px;
          text-wrap:balance;
        }

        /* subhead a touch bolder & tighter */
        .hero-sub{
          color:var(--ink-600);
          font-size:1.05rem;
          line-height:1.55;
          font-weight:500;
          max-width:44ch;
          margin:0 0 24px;
        }

        .cta-row{display:flex;gap:14px;flex-wrap:wrap;}
        .cta-row .btn--primary{background:linear-gradient(90deg,#2563eb,#3b82f6);border-color:#2563eb;}
        .welcome-hero-media{position:relative;display:flex;justify-content:flex-end;padding-right:2%;}
        .welcome-hero-frame{position:relative;background:#fff;border-radius:24px;padding:14px;border:1px solid #e8eff8;box-shadow:0 26px 60px rgba(15,23,42,.18);transform:rotate(-2.2deg);}
        .welcome-hero-frame::after{content:"";position:absolute;inset:12px;border:1px solid rgba(15,23,42,.07);border-radius:18px;}
        .welcome-hero-photo{border-radius:18px;overflow:hidden;}
        .welcome-hero-photo img{display:block;border-radius:18px;}

        /* section header: sentence case, closer to content */
        .section--tight{padding:18px 0 6px;}
        .welcome-section-title{
          text-transform:none;
          letter-spacing:.02em;
          font-size:1.35rem;
          margin:0;
          color:var(--ink);
          font-weight:800;
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

        .welcome-context-sentinel,
        .context-card-sentinel{display:none;}
        @supports(selector(div:has(.welcome-context-sentinel))){
          div.block-container:has(.welcome-context-sentinel){
            padding-top:0!important;
            padding-bottom:0!important;
          }
          div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel){
            background:#fff;
            padding:72px 0;
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
              padding:48px 0;
            }
            div[data-testid="stVerticalBlock"]:has(.welcome-context-sentinel) > div[data-testid="stHorizontalBlock"]{
              flex-direction:column;
              gap:28px;
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
        .context-form-row{display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap;}
        .context-input{flex:1 1 220px;}
        .context-submit{flex:0 0 160px;}
        .context-submit .stButton{width:100%;}
        .context-submit .stButton button{width:100%;height:48px;border-radius:14px;font-weight:700;border:none;background:linear-gradient(90deg,#2563eb,#3b82f6);color:#fff;}
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


def _go_to(page_path: Optional[str], fallback_route: Optional[str]) -> None:
    switch_fn = getattr(st, "switch_page", None)
    if page_path and callable(switch_fn):
        try:
            switch_fn(page_path)
            return
        except Exception:
            pass
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
    submit_route: Optional[str] = "hub_concierge",
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
        icon = ""
        if key == "someone":
            icon = "<svg viewBox='0 0 24 24'><path d='M8 11a3 3 0 1 0-3-3 3 3 0 0 0 3 3zm8-2a2.5 2.5 0 1 0-2.5-2.5A2.5 2.5 0 0 0 16 9zM4 18.5C4 15.46 6.63 14 10 14s6 1.46 6 4.5V20H4zM17 14c-1.08 0-2.05.19-2.91.52A4.3 4.3 0 0 1 16.5 17v.5H20V17c0-2-1.55-3-3-3z'/></svg>"
        elif key == "self":
            icon = "<svg viewBox='0 0 24 24'><path d='M12 12a3.5 3.5 0 1 0-3.5-3.5A3.5 3.5 0 0 0 12 12zm0 2c-3.31 0-7 1.64-7 4.5V20h14v-1.5C19 15.64 15.31 14 12 14z'/></svg>"
        else:
            icon = "<svg viewBox='0 0 24 24'><path d='M9 6.5A2.5 2.5 0 0 1 11.5 4h1A2.5 2.5 0 0 1 15 6.5V7h2.5A2.5 2.5 0 0 1 20 9.5V17a2 2 0 0 1-2 2h-3v-2h3V9.5a.5.5 0 0 0-.5-.5H15v1a1 1 0 0 1-2 0v-1h-2v1a1 1 0 0 1-2 0v-1H6.5a.5.5 0 0 0-.5.5V17h3v2H6a2 2 0 0 1-2-2V9.5A2.5 2.5 0 0 1 6.5 7H9z'/></svg>"
        classes = "context-pill-link"
        if key == safe_active:
            classes += " is-active"
        pill_links.append(
            f"<a href='?page={route}' class='{classes}' data-pill='{key}' {'aria-current="page"' if key == safe_active else ''}>{icon}<span>{html.escape(cfg['label'])}</span></a>"
        )

    with left_col:
        st.markdown('<span class="context-card-sentinel"></span>', unsafe_allow_html=True)

        st.markdown(
            _clean_html(
                f"""
                <div class="context-top">
                  <div class="context-pill-group">{''.join(pill_links)}</div>
                  <a class="context-close" href="?page=welcome" aria-label="Back to welcome">×</a>
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

        if submitted and name_value.strip():
            st.session_state["person_name"] = name_value.strip()
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


def _welcome_content(ctx: Optional[dict] = None) -> None:
    _inject_welcome_css()

    hero_url = static_url("hero.png")
    family_main = static_url("welcome_someone_else.png")
    self_main = static_url("welcome_self.png")

    st.markdown(
        _clean_html(
            f"""
            <main>
              <section class="container section-hero">
                <div class="hero-grid">
                  <div>
                    <p class="hero-eyebrow">Concierge Care Advisors</p>
                    <h1 class="hero-title">Care decisions are hard. You don’t have to make them alone.</h1>
                    <p class="hero-sub">
                      Talk with a no-cost advisor who helps your family navigate senior living
                      choices clearly, confidently, and compassionately.
                    </p>
                    <div class="cta-row">
                      <a href="?page=hub_concierge" class="btn btn--primary wl-btn">Start Now</a>
                      <a href="?page=login" class="btn btn--secondary">Log in</a>
                    </div>
                  </div>
                  <div class="welcome-hero-media">
                    <div class="welcome-hero-frame">
                      <div class="welcome-hero-photo">
                        <img src="{hero_url}" alt="Care professional supporting senior" />
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
                      <img src="{family_main}" alt="Family gathering outdoors" />
                    </div>
                    <p class="card-head">I would like to <strong>support my loved ones</strong></p>
                    <p class="card-meta">For a loved one</p>
                    <p class="dashboard-description">
                      Helping you make confident care decisions for someone you love.
                    </p>
                    <div class="card-actions">
                      <a href="?page=someone_else" class="btn btn--primary">For someone</a>
                    </div>
                  </article>

                  <article class="card welcome-card">
                    <div class="welcome-card-media">
                      <img src="{self_main}" alt="Senior lifestyle" />
                    </div>
                    <p class="card-head">I'm looking for <strong>support just for myself</strong></p>
                    <p class="card-meta">For myself</p>
                    <p class="dashboard-description">
                      Plan for your own future care with trusted guidance and peace of mind.
                    </p>
                    <div class="card-actions">
                      <a href="?page=self" class="btn btn--primary">For myself</a>
                    </div>
                  </article>
                </div>
              </section>
            </main>
            """
        ),
        unsafe_allow_html=True,
    )


def render(ctx: Optional[dict] = None) -> None:
    render_page(_welcome_content, ctx, show_header=True, show_footer=True)


__all__ = ["render", "render_welcome_card"]
