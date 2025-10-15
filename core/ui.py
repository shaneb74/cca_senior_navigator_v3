import base64
import functools
import mimetypes
import pathlib
import sys
from typing import Optional

import streamlit as st

from core.nav import route_to
from core.session_store import safe_rerun

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
                        safe_rerun()
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
            context["tier"] = care_rec.tier
            context["confidence"] = int(care_rec.confidence * 100)
    except:
        pass
    
    try:
        financial = MCIP.get_financial_profile()
        if financial:
            context["monthly_cost"] = f"${financial.estimated_monthly_cost:,.0f}"
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


def render_navi_guide_bar(
    text: str,
    subtext: Optional[str] = None,
    icon: str = "🤖",
    show_progress: bool = False,
    current_step: Optional[int] = None,
    total_steps: Optional[int] = None,
    color: str = "#8b5cf6"
) -> None:
    """Render persistent Navi guide bar at top of page.
    
    DEPRECATED: Use render_navi_panel_v2() for hub pages.
    This legacy function remains for product/module pages.
    
    Args:
        text: Main message from Navi (required)
        subtext: Additional context/explanation (optional)
        icon: Emoji icon (default: 🤖)
        show_progress: Whether to show progress indicator
        current_step: Current step number (for progress)
        total_steps: Total steps (for progress)
        color: Primary color for gradient (default: purple)
    """
    # Build progress indicator if needed
    progress_html = ""
    if show_progress and current_step is not None and total_steps is not None:
        # Build progress badge inline to avoid escaping issues
        progress_badge = f'<div style="font-size: 12px; font-weight: 500; padding: 4px 12px; background: rgba(255,255,255,0.2); border-radius: 12px; white-space: nowrap;">{current_step}/{total_steps}</div>'
    else:
        progress_badge = ""
    
    # Build subtext HTML if provided
    subtext_html = f'<div style="font-size: 12px; opacity: 0.9;">{subtext}</div>' if subtext else ''
    
    # Render compact guide bar (all as one HTML block to avoid escaping)
    html = f"""
        <div style="
            background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
            padding: 12px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            color: white;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 24px; flex-shrink: 0;">
                {icon}
            </div>
            <div style="flex: 1; min-width: 0;">
                <div style="font-size: 14px; font-weight: 600; margin-bottom: 2px;">
                    {text}
                </div>
                {subtext_html}
            </div>
            {progress_badge}
        </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def render_navi_panel_v2(
    title: str,
    reason: str,
    encouragement: dict,
    context_chips: list[dict],
    primary_action: dict,
    secondary_action: Optional[dict] = None,
    progress: Optional[dict] = None,
    alert_html: Optional[str] = None
) -> None:
    """Render refined Navi panel with structured layout using Streamlit native components."""
    from core.nav import route_to
    
    # Inject CSS for Navi panel V2 (matches product tile styling)
    navi_css = """
    <style>
    .navi-panel-v2 {
        max-width: 1120px;
        margin: 0 auto;
        background: #ffffff;
        border: 1px solid #e6edf5;
        border-radius: 20px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
        padding: 32px;
        transition: box-shadow 0.16s ease;
    }
    .navi-panel-v2__header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    .navi-panel-v2__eyebrow {
        font-size: 11px;
        font-weight: 800;
        color: #2563eb;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .navi-panel-v2__progress {
        font-size: 11px;
        font-weight: 600;
        padding: 6px 12px;
        background: rgba(37, 99, 235, 0.08);
        border: 1px solid rgba(37, 99, 235, 0.15);
        border-radius: 12px;
        color: #2563eb;
    }
    .navi-panel-v2__title {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 8px 0;
        line-height: 1.3;
    }
    .navi-panel-v2__reason {
        font-size: 16px;
        color: #475569;
        margin: 0 0 20px 0;
        line-height: 1.5;
    }
    .navi-panel-v2__encouragement {
        padding: 12px 16px;
        border-radius: 10px;
        margin: 0 0 20px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 15px;
        color: #1e293b;
        line-height: 1.4;
    }
    .navi-panel-v2__encouragement--getting_started { background: #eff6ff; border: 1px solid #dbeafe; }
    .navi-panel-v2__encouragement--in_progress { background: #eff6ff; border: 1px solid #dbeafe; }
    .navi-panel-v2__encouragement--nearly_there { background: #fef3c7; border: 1px solid #fde68a; }
    .navi-panel-v2__encouragement--complete { background: #f0fdf4; border: 1px solid #bbf7d0; }
    .navi-panel-v2__chips-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        margin: 0 0 12px 0;
    }
    .navi-panel-v2__chips {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }
    .navi-panel-v2__chip {
        flex: 1;
        min-width: 140px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        box-shadow: 0 1px 2px rgba(15,23,42,.04);
    }
    .navi-panel-v2__chip-label {
        font-size: 11px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .navi-panel-v2__chip-value {
        font-size: 15px;
        color: #0f172a;
        font-weight: 700;
    }
    .navi-panel-v2__chip-sublabel {
        font-size: 11px;
        color: #64748b;
        margin-top: 2px;
    }
    </style>
    """
    st.markdown(navi_css, unsafe_allow_html=True)
    
    # Build HTML components
    progress_badge = ""
    if progress and progress.get('current') is not None and progress.get('total'):
        progress_badge = f'<div class="navi-panel-v2__progress">Step {progress["current"]}/{progress["total"]}</div>'
    
    # Build context chips
    chips_html = ""
    if context_chips:
        chip_items = []
        for chip in context_chips:
            sublabel_html = ""
            if chip.get('sublabel'):
                sublabel_html = f'<div class="navi-panel-v2__chip-sublabel">{chip["sublabel"]}</div>'
            
            chip_items.append(f'<div class="navi-panel-v2__chip"><div class="navi-panel-v2__chip-label"><span>{chip.get("icon", "")}</span><span>{chip.get("label", "")}</span></div><div class="navi-panel-v2__chip-value">{chip.get("value", "Not set")}</div>{sublabel_html}</div>')
        
        chips_html = f'<div class="navi-panel-v2__chips-label">What I know so far:</div><div class="navi-panel-v2__chips">{"".join(chip_items)}</div>'
    
    # Get encouragement status
    status = encouragement.get('status', 'in_progress')
    
    # Build action buttons HTML with correct routing parameter (?page=)
    actions_html = ""
    if secondary_action:
        primary_href = f"?page={primary_action.get('route', '')}" if primary_action.get('route') else "#"
        secondary_href = f"?page={secondary_action.get('route', '')}" if secondary_action.get('route') else "#"
        actions_html = f'<div style="display: flex; gap: 12px; margin-top: 18px;"><a class="dashboard-cta dashboard-cta--primary" href="{primary_href}" style="flex: 2;">{primary_action["label"]}</a><a class="dashboard-cta dashboard-cta--ghost" href="{secondary_href}" style="flex: 1;">{secondary_action["label"]}</a></div>'
    else:
        primary_href = f"?page={primary_action.get('route', '')}" if primary_action.get('route') else "#"
        actions_html = f'<div style="margin-top: 18px;"><a class="dashboard-cta dashboard-cta--primary" href="{primary_href}" style="width: 100%; text-align: center;">{primary_action["label"]}</a></div>'
    
    # Build complete panel HTML (flat structure, no inner wrapper)
    # Include alert if provided (appears before title)
    alert_section = alert_html if alert_html else ""
    panel_html = f'<div class="navi-panel-v2"><div class="navi-panel-v2__header"><div class="navi-panel-v2__eyebrow">🤖 Navi</div>{progress_badge}</div>{alert_section}<div class="navi-panel-v2__title">{title}</div><div class="navi-panel-v2__reason">{reason}</div><div class="navi-panel-v2__encouragement navi-panel-v2__encouragement--{status}"><span style="font-size: 18px;">{encouragement.get("icon", "💪")}</span><span>{encouragement.get("text", "")}</span></div>{chips_html}{actions_html}</div>'
    
    st.markdown(panel_html, unsafe_allow_html=True)


