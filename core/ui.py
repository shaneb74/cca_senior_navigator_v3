from typing import Optional
import base64, mimetypes, pathlib, sys, functools

import streamlit as st
from core.nav import route_to

from .nav import PRODUCTS

# Resolve repository root (…/cca_senior_navigator_v3)
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


@functools.lru_cache(maxsize=128)
def img_src(rel_path: str) -> str:
    """
    Return a base64 data URI for an image at repo-relative rel_path.
    Example: img_src("static/images/hero.png")
    """
    safe_rel = rel_path.lstrip("/").replace("\\", "/")
    p = (_REPO_ROOT / safe_rel).resolve()
    if not p.exists():
        print(f"[WARN] Missing static image: {safe_rel} (resolved: {p})", file=sys.stderr)
        return ""
    mime, _ = mimetypes.guess_type(p.name)
    try:
        data = p.read_bytes()
    except Exception as e:
        print(f"[ERROR] Failed to read image {p}: {e}", file=sys.stderr)
        return ""
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime or 'image/png'};base64,{b64}"


def header(app_title: str, current_key: str, pages: dict):
    links = []
    for key, meta in pages.items():
        # Skip hidden pages
        if meta.get("hidden", False):
            continue
        active = " is-active" if key == current_key else ""
        links.append(f'<a class="nav-link{active}" href="?page={key}">{meta["label"]}</a>')
    html = f"""
    <header class="header">
      <div class="container header__inner">
        <div class="brand">{app_title}</div>
        <nav class="nav cluster">{''.join(links)}</nav>
      </div>
    </header>
    """
    st.markdown(html, unsafe_allow_html=True)


def footer():
    html = """
    <footer class="footer">
      <div class="container footer__inner">
        <div class="muted">© Senior Navigator</div>
        <div class="cluster">
          <a class="nav-link" href="?page=terms">Terms</a>
          <a class="nav-link" href="?page=privacy">Privacy</a>
          <a class="nav-link" href="?page=about">About</a>
        </div>
      </div>
    </footer>
    """
    st.markdown(html, unsafe_allow_html=True)


def page_container_open():
    st.markdown('<main class="container stack">', unsafe_allow_html=True)


def page_container_close():
    st.markdown("</main>", unsafe_allow_html=True)


def hub_section(title: str, right_meta: Optional[str] = None):
    right = f'<div class="tile-meta">{right_meta}</div>' if right_meta else ""
    st.markdown(
        f"""<section class="container section">
<div class="tile-head">
  <h2 class="section-title">{title}</h2>
  {right}
</div>
</section>""",
        unsafe_allow_html=True,
    )


def tiles_open():
    st.markdown('<div class="container"><div class="tiles">', unsafe_allow_html=True)


def tiles_close():
    st.markdown("</div></div>", unsafe_allow_html=True)


def tile_open(size: str = "md"):
    size_class = "tile--md" if size == "md" else "tile--lg"
    st.markdown(f'<article class="tile {size_class}">', unsafe_allow_html=True)


def tile_close():
    st.markdown("</article>", unsafe_allow_html=True)


def render_product_tile(product_key: str, state: dict):
    """Render a product tile with status, progress, and actions."""
    status_class = f"tile--{state['status']}"
    progress = state['progress']
    title = PRODUCTS[product_key]['title']
    
    # Mock outputs for now; in production, aggregate from modules
    if product_key == "gcp":
        summary = "Recommendation: In-Home Care"
    elif product_key == "cost_planner":
        summary = "Est. cost $4,200 / Runway 3.8 yrs"
    else:
        summary = "Not started"
    
    html = f"""
<div class="tile-head">
  <div class="tile-title">{title}</div>
  <span class="badge {status_class}">{state['status'].replace('_', ' ').title()}</span>
</div>
<div class="tile-progress">
  <div class="progress-bar" style="width: {progress}%"></div>
</div>
<p class="tile-meta">{summary}</p>
<div class="kit-row">
  <a class="btn btn--primary" href="?page={product_key}">Continue</a>
  <a class="btn btn--secondary" href="?page={product_key}">See responses</a>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_module_tile(product_key: str, module_key: str, state: dict):
    """Render a module tile with status, progress, outputs, and actions."""
    status_class = f"tile--{state['status']}"
    progress = state['progress']
    title = module_key.replace('_', ' ').title()
    
    outputs_html = ""
    if state['outputs']:
        primary_output = state['outputs'][0]
        outputs_html = f'<p class="tile-meta">{primary_output["label"]}<br><strong>{primary_output["value"]}</strong></p>'
        for output in state['outputs'][1:]:
            outputs_html += f'<p class="tile-meta">{output["label"]}: {output["value"]}</p>'
    
    completed_at = state.get('completed_at', '')
    if completed_at:
        outputs_html += f'<p class="tile-meta">Last updated: {completed_at}</p>'
    
    html = f"""
<div class="tile-head">
  <div class="tile-title">{title}</div>
  <span class="badge {status_class}">{state['status'].replace('_', ' ').title()}</span>
</div>
<div class="tile-progress">
  <div class="progress-bar" style="width: {progress}%"></div>
</div>
{outputs_html}
<div class="kit-row">
  <a class="btn btn--primary" href="?page={product_key}_{module_key}">Continue</a>
  <a class="btn btn--secondary" href="?page={product_key}_{module_key}">See responses</a>
  <a class="btn btn--ghost" href="?page={product_key}_{module_key}">Start over</a>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_hub_tile(title, badge, label, value, status, primary_label, secondary_label=None, primary_action=None, secondary_action=None):
    """
    Renders a standardized hub module tile using the design system.
    Use this in hub pages to maintain visual and behavioral consistency.
    """
    # Status classes for badges
    status_class = {
        "done": "success",
        "doing": "warning", 
        "new": "info",
        "locked": ""
    }.get(status, "")

    status_text = {
        "done": "Completed",
        "doing": "In Progress",
        "new": "Not Started",
        "locked": "Locked"
    }.get(status, "")

    # Create unique keys for the buttons
    primary_key = f"{title.lower().replace(' ', '_').replace('&', 'and')}_primary"
    secondary_key = f"{title.lower().replace(' ', '_').replace('&', 'and')}_secondary"

    # Render the tile using design system classes with buttons inside
    st.markdown(f"""
    <article class="tile tile--{status if status != 'locked' else 'locked'}">
      <div class="tile-head">
        <h3 class="tile-title">{title}</h3>
        <span class="badge {status_class}">{badge}</span>
      </div>
      
      <div class="tile-meta">{label}</div>
      <div style="font-size: 1.25rem; font-weight: 700; color: var(--ink); margin: var(--space-3) 0;">
        {value}
      </div>
      
      <div style="margin-top: var(--space-4); font-size: 0.9rem; color: var(--ink-500);">
        {status_text}
      </div>
      
      <div class="card-actions" style="margin-top: var(--space-6);">
    """, unsafe_allow_html=True)

    # Create buttons within the tile using Streamlit columns for proper layout
    if secondary_label:
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button(primary_label, key=primary_key, use_container_width=True):
                if primary_action:
                    primary_action()
                else:
                    # Default navigation based on title
                    if "Guided Care Plan" in title:
                        route_to("gcp")
                    elif "Cost Planner" in title:
                        route_to("cost_planner")
                    elif "Plan with My Advisor" in title:
                        route_to("pfma")
                    elif "FAQs & Answers" in title or "FAQ Center" in title:
                        route_to("faqs")

        with col2:
            if st.button(secondary_label, key=secondary_key, use_container_width=True):
                if secondary_action:
                    secondary_action()
                else:
                    # Default secondary actions
                    if "Start over" in secondary_label and "Guided Care Plan" in title:
                        st.session_state["gcp_answers"] = {}
                        st.session_state["gcp_section"] = 0
                        st.rerun()
    else:
        # Single button layout - full width
        if st.button(primary_label, key=primary_key, use_container_width=True):
            if primary_action:
                primary_action()
            else:
                # Default navigation based on title
                if "Guided Care Plan" in title:
                    route_to("gcp")
                elif "Cost Planner" in title:
                    route_to("cost_planner")
                elif "Plan with My Advisor" in title:
                    route_to("pfma")
                elif "FAQs & Answers" in title or "FAQ Center" in title:
                    route_to("faqs")

    # Close the card-actions div and tile
    st.markdown('</div></article>', unsafe_allow_html=True)