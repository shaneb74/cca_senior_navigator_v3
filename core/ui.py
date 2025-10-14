import base64
import functools
import mimetypes
import pathlib
import sys
from typing import Optional

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


def safe_img_src(filename: str) -> str:
    """
    Resolve a static image by delegating to layout.static_url while avoiding circular imports.
    Accepts bare filenames or repo-relative static paths.
    """
    try:
        from layout import static_url  # type: ignore
    except Exception:
        return ""
    candidates = []
    clean = filename.lstrip("/").replace("\\", "/")
    candidates.append(clean)
    if not clean.startswith("logos/"):
        candidates.append(f"logos/{clean}")
    if not clean.startswith("images/"):
        candidates.append(f"images/{clean}")
    if not clean.startswith("static/images/"):
        candidates.append(f"static/images/{clean}")
    for candidate in candidates:
        try:
            return static_url(candidate)
        except FileNotFoundError:
            continue
    return ""


def header(app_title: str, current_key: str, pages: dict):
    from layout import \
        render_header  # local import to avoid circular at module load

    render_header(active_route=current_key)


def page_container_open():
    st.markdown('<main class="container stack">', unsafe_allow_html=True)


def page_container_close():
    st.markdown("</main>", unsafe_allow_html=True)


def hub_section(title: str, right_meta: Optional[str] = None):
    right = f'<div class="tile-meta"><span>{right_meta}</span></div>' if right_meta else ""
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
    progress = state["progress"]
    title = PRODUCTS[product_key]["title"]

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
<div class="tile-meta"><span>{summary}</span></div>
<div class="kit-row">
  <a class="btn btn--primary" href="?page={product_key}">Continue</a>
  <a class="btn btn--secondary" href="?page={product_key}">See responses</a>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_module_tile(product_key: str, module_key: str, state: dict):
    """Render a module tile with status, progress, outputs, and actions."""
    status_class = f"tile--{state['status']}"
    progress = state["progress"]
    title = module_key.replace("_", " ").title()

    meta_spans: list[str] = []
    if state["outputs"]:
        primary_output = state["outputs"][0]
        meta_spans.append(
            f'<span>{primary_output["label"]}: <strong>{primary_output["value"]}</strong></span>'
        )
        for output in state["outputs"][1:]:
            meta_spans.append(f'<span>{output["label"]}: {output["value"]}</span>')

    completed_at = state.get("completed_at", "")
    if completed_at:
        meta_spans.append(f"<span>Last updated: {completed_at}</span>")

    outputs_html = f'<div class="tile-meta">{"".join(meta_spans)}</div>' if meta_spans else ""

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


def render_hub_tile(
    title,
    badge,
    label,
    value,
    status,
    primary_label,
    secondary_label=None,
    primary_action=None,
    secondary_action=None,
):
    """
    Renders a standardized hub module tile using the design system.
    Use this in hub pages to maintain visual and behavioral consistency.
    """
    # Status classes for badges
    status_class = {
        "done": "success",
        "doing": "warning",
        "new": "info",
        "locked": "",
    }.get(status, "")

    status_text = {
        "done": "Completed",
        "doing": "In Progress",
        "new": "Not Started",
        "locked": "Locked",
    }.get(status, "")

    # Create unique keys for the buttons
    primary_key = f"{title.lower().replace(' ', '_').replace('&', 'and')}_primary"
    secondary_key = f"{title.lower().replace(' ', '_').replace('&', 'and')}_secondary"

    # Render the tile using design system classes with buttons inside
    st.markdown(
        f"""
    <article class="tile tile--{status if status != 'locked' else 'locked'}">
      <div class="tile-head">
        <h3 class="tile-title">{title}</h3>
        <span class="badge {status_class}">{badge}</span>
      </div>
      
            <div class="tile-meta"><span>{label}</span></div>
            <div class="tile-value">{value}</div>
            <div class="tile-status-note">{status_text}</div>
            <div class="tile-actions">
    """,
        unsafe_allow_html=True,
    )

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
    st.markdown("</div></article>", unsafe_allow_html=True)


def render_mcip_journey_status() -> None:
    """Render Navi journey status banner showing progress and next action.
    
    Navi is your AI guide through the senior care journey.
    Now powered by structured dialogue system from navi_dialogue.json.
    
    Shows contextual guidance based on journey phase:
    - getting_started: Welcome and first product intro
    - in_progress: Celebration + next product guidance
    - nearly_there: Almost done + final product
    - complete: Celebration + export/share
    
    Includes gamification:
    - Achievement badges for each completed product
    - Visual celebrations on completion
    - "Share My Results" button when complete
    """
    from core.mcip import MCIP
    from core.state import get_user_ctx, is_authenticated, get_user_name
    from core.navi_dialogue import NaviDialogue
    
    # Get journey data
    progress = MCIP.get_journey_progress()
    next_action = MCIP.get_recommended_next_action()
    
    completed = progress["completed_count"]
    completed_products = progress["completed_products"]
    total = 3  # GCP, Cost Planner, PFMA
    
    # Build context for Navi dialogue
    context = {
        "name": get_user_name() or "there",
    }
    
    # Add contract data to context if available
    try:
        care_rec = MCIP.get_care_recommendation()
        if care_rec:
            context["tier"] = care_rec.recommended_tier
            context["confidence"] = int(care_rec.confidence_score * 100)
    except:
        pass
    
    try:
        financial = MCIP.get_financial_profile()
        if financial:
            context["monthly_cost"] = f"${financial.monthly_cost:,.0f}"
            context["runway_months"] = financial.runway_months
    except:
        pass
    
    # Map MCIP status to dialogue phase
    status = next_action["status"]
    phase_map = {
        "complete": "complete",
        "nearly_there": "nearly_there",
        "in_progress": "in_progress",
        "getting_started": "getting_started"
    }
    phase = phase_map.get(status, "getting_started")
    
    # Get Navi's message from dialogue system
    navi_message = NaviDialogue.get_journey_message(phase, is_authenticated(), context)
    
    # Extract message components
    icon = navi_message.get("icon", "🤖")
    main_text = navi_message.get("text", "")
    subtext = navi_message.get("subtext", "")
    cta_text = navi_message.get("cta", "")
    
    # Prefix Navi branding to main text
    if not main_text.startswith("🤖"):
        if status == "complete":
            main_text = f"🤖 Navi says: {main_text}"
        else:
            main_text = f"🤖 Navi: {main_text}"
    
    # Achievement badges for completed products
    badges_html = _render_achievement_badges(completed_products)
    
    # Status-based styling
    color_map = {
        "complete": "#10b981",       # Green
        "nearly_there": "#f59e0b",   # Amber
        "in_progress": "#3b82f6",    # Blue
        "getting_started": "#8b5cf6" # Purple
    }
    bg_color = color_map.get(status, "#8b5cf6")
    
    # Add confetti on complete
    if status == "complete":
        _render_celebration_effect()
    
    # Render banner with Navi branding
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {bg_color} 0%, {bg_color}dd 100%);
            border-radius: 12px;
            padding: 20px 24px;
            margin: 20px 0;
            color: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 4px solid rgba(255,255,255,0.4);
        ">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="font-size: 32px;">{icon}</div>
                <div style="flex: 1;">
                    <div style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">
                        {main_text}
                    </div>
                    <div style="font-size: 14px; opacity: 0.9;">
                        {subtext}
                    </div>
                    {badges_html}
                </div>
                {f'<div style="font-size: 14px; font-weight: 500; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 20px;">{completed}/{total}</div>' if status != "complete" else ''}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Navigate to next action
        if status != "complete" and next_action.get("route"):
            if st.button(f"→ {next_action['action']}", key=f"mcip_nav_{next_action['route']}", use_container_width=True):
                route_to(next_action["route"])
    
    with col2:
        # Share/Export results (always available if any progress)
        if completed > 0:
            if st.button("📤 Share My Results", key="mcip_share_results", use_container_width=True):
                route_to("export_results")


def _render_achievement_badges(completed_products: list) -> str:
    """Render achievement badges for completed products.
    
    Args:
        completed_products: List of completed product keys
    
    Returns:
        HTML string with badges
    """
    badges = {
        "gcp": {"emoji": "🧭", "title": "Care Navigator", "color": "#8b5cf6"},
        "cost_planner": {"emoji": "💰", "title": "Financial Planner", "color": "#3b82f6"},
        "pfma": {"emoji": "📅", "title": "Appointment Setter", "color": "#f59e0b"}
    }
    
    if not completed_products:
        return ""
    
    badges_html = '<div style="display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap;">'
    
    for product_key in completed_products:
        badge = badges.get(product_key)
        if badge:
            badges_html += f"""
                <div style="
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 6px 12px;
                    background: rgba(255,255,255,0.25);
                    border-radius: 20px;
                    font-size: 13px;
                    font-weight: 500;
                    backdrop-filter: blur(10px);
                ">
                    <span style="font-size: 16px;">{badge['emoji']}</span>
                    <span>✓ {badge['title']}</span>
                </div>
            """
    
    badges_html += '</div>'
    return badges_html


def _render_celebration_effect() -> None:
    """Render confetti/celebration effect when journey is complete.
    
    Uses CSS animation for visual dopamine hit.
    """
    st.markdown("""
        <style>
        @keyframes confetti {
            0% { transform: translateY(-100%) rotate(0deg); opacity: 1; }
            100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
        }
        .confetti {
            position: fixed;
            width: 10px;
            height: 10px;
            background: #f59e0b;
            animation: confetti 3s ease-in-out infinite;
            z-index: 9999;
            pointer-events: none;
        }
        .confetti:nth-child(2n) { background: #10b981; animation-delay: 0.3s; }
        .confetti:nth-child(3n) { background: #3b82f6; animation-delay: 0.6s; }
        .confetti:nth-child(4n) { background: #8b5cf6; animation-delay: 0.9s; }
        </style>
        <div class="confetti" style="left: 20%;"></div>
        <div class="confetti" style="left: 40%;"></div>
        <div class="confetti" style="left: 60%;"></div>
        <div class="confetti" style="left: 80%;"></div>
    """, unsafe_allow_html=True)

