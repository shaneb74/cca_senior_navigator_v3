# hubs/resources.py
"""
Resources Hub - Educational Resources and Self-Service Tools

This hub mirrors the Concierge Hub in layout, styling, and functionality.
Includes Navi at the top and the Additional Services section below.
"""

import html

import streamlit as st

from core.additional_services import get_additional_services
from core.base_hub import render_dashboard_body
from core.mcip import MCIP
from core.navi import render_navi_panel
from core.product_tile import ProductTileHub
from ui.footer_simple import render_footer_simple
from ui.header_simple import render_header_simple

__all__ = ["render"]


def render(ctx=None) -> None:
    """Render the Resources Hub with Navi orchestration."""
    
    # Load dashboard CSS for consistency
    st.markdown(
        f"<style>{open('core/styles/dashboard.css').read()}</style>",
        unsafe_allow_html=True
    )
    
    # Render header
    render_header_simple(active_route="resources")

    # Initialize MCIP
    MCIP.initialize()

    # Show save confirmation if returning
    save_msg = st.session_state.pop("_show_save_message", None)
    if save_msg:
        product_name = {
            "fall_risk": "Fall Risk",
            "disease_mgmt": "Disease Management Program",
            "home_safety": "Home Safety Check",
            "home_health": "Find Home Health",
            "dme": "Find DME",
            "med_manage": "Medication Management",
            "predictive_health": "Predictive Health Analytics",
        }.get(save_msg.get("product", ""), "resource")

        prog = save_msg.get("progress", 0)

        if prog >= 100:
            st.success(f"✅ {product_name} complete!")
        else:
            st.info(f"💾 Progress saved! You're {prog:.0f}% through {product_name}.")

    person_name = st.session_state.get("person_name", "").strip()
    person = person_name if person_name else "you"

    # Build hub order
    hub_order = {
        "hub_id": "resources",
        "ordered_products": [
            "med_manage",
            "predictive_health",
            "fall_risk",
            "disease_mgmt",
            "home_safety",
            "home_health",
            "dme",
        ],
        "reason": "Explore helpful resources and tools",
        "total": 7,
        "next_step": "med_manage",
    }
    hub_order["next_route"] = f"?page={hub_order['next_step']}"

    # Build product tiles
    cards = [
        _build_med_manage_tile(),
        _build_predictive_health_tile(),
        _build_fall_risk_tile(),
        _build_disease_mgmt_tile(),
        _build_home_safety_tile(),
        _build_home_health_tile(),
        _build_dme_tile(),
    ]

    # Get additional services
    additional = get_additional_services("resources")

    # Build chips
    chips = [{"label": "Resources"}]
    if person_name:
        chips.append({"label": f"For {person}", "variant": "muted"})
    chips.append({"label": "Self-service tools"})

    alert_html = _build_saved_progress_alert(save_msg)

    # Use callback pattern to render Navi AFTER header but BEFORE body
    def render_content():
        # Render Navi panel (after header, before hub content)
        render_navi_panel(location="hub", hub_key="resources")

        # Render hub body HTML WITHOUT title/subtitle/chips (Navi replaces them)
        body_html = render_dashboard_body(
            title=None,  # Skip title - Navi provides context
            subtitle=None,  # Skip subtitle - Navi provides context
            chips=None,  # Skip chips - Navi provides status
            hub_guide_block=None,
            hub_order=hub_order,
            cards=cards,
            additional_services=additional,  # Include in HTML for proper layout
        )

        full_html = (alert_html or "") + body_html
        st.markdown(full_html, unsafe_allow_html=True)

    # Render content with Navi
    render_content()
    
    # Render footer
    render_footer_simple()


def _build_saved_progress_alert(save_msg: dict | None) -> str:
    """Build progress alert banner."""
    if not save_msg:
        return ""

    product_name = {
        "fall_risk": "Fall Risk",
        "disease_mgmt": "Disease Management Program",
        "home_safety": "Home Safety Check",
        "home_health": "Find Home Health",
        "dme": "Find DME",
        "med_manage": "Medication Management",
        "predictive_health": "Predictive Health Analytics",
    }.get(save_msg.get("product", ""), "resource")

    prog = save_msg.get("progress", 0)
    if prog >= 100:
        message = f"✅ {product_name} complete!"
        style = {"bg": "#ecfdf5", "border": "#bbf7d0", "color": "#047857"}
    else:
        message = f"💾 Progress saved! You're {prog:.0f}% through {product_name}."
        style = {"bg": "#eff6ff", "border": "#bfdbfe", "color": "#1d4ed8"}

    return (
        '<div style="margin-bottom:20px;padding:16px 20px;border-radius:14px;'
        f'background:{style["bg"]};border:1px solid {style["border"]};color:{style["color"]};"'
        f">{html.escape(message)}</div>"
    )


def _build_fall_risk_tile() -> ProductTileHub:
    """Build Fall Risk tile."""
    return ProductTileHub(
        key="fall_risk",
        title="Fall Risk",
        desc="Identify and manage fall risk factors.",
        blurb="Learn about fall prevention strategies, home modifications, and safety assessments to reduce the risk of falls and injuries.",
        image_square=None,  # Phase 5E: No PNG, CSS icon
        meta_lines=["≈5 min • Auto-saves"],
        primary_label="Start",
        primary_route="?page=fall_risk",
        progress=0,
        variant="teal",
        order=30,
        visible=True,
        locked=False,
    )


def _build_disease_mgmt_tile() -> ProductTileHub:
    """Build Disease Management Program tile."""
    return ProductTileHub(
        key="disease_mgmt",
        title="Disease Management Program",
        desc="Ongoing disease management support and coordination.",
        blurb="Access information on chronic disease management programs, care coordination, and support services to help manage ongoing health conditions.",
        image_square=None,  # Phase 5E: No PNG, CSS icon
        meta_lines=["≈8 min • Auto-saves"],
        primary_label="Start",
        primary_route="?page=disease_mgmt",
        progress=0,
        variant="teal",
        order=40,
        visible=True,
        locked=False,
    )


def _build_home_safety_tile() -> ProductTileHub:
    """Build Home Safety Check tile."""
    return ProductTileHub(
        key="home_safety",
        title="Home Safety Check",
        desc="Safety assessments and recommendations for home environments.",
        blurb="Evaluate your home for safety hazards and receive personalized recommendations for modifications and improvements to create a safer living space.",
        image_square="home_safety.png",
        meta_lines=["≈10 min • Auto-saves"],
        primary_label="Start",
        primary_route="?page=home_safety",
        progress=0,
        variant="teal",
        order=50,
        visible=True,
        locked=False,
    )


def _build_home_health_tile() -> ProductTileHub:
    """Build Find Home Health tile."""
    return ProductTileHub(
        key="home_health",
        title="Find Home Health",
        desc="Locate home health care services in your area.",
        blurb="Search for qualified home health agencies, compare services and ratings, and find the right home care provider to meet your needs.",
        image_square="home_health.png",
        meta_lines=["≈5 min • Auto-saves"],
        primary_label="Start",
        primary_route="?page=home_health",
        progress=0,
        variant="teal",
        order=60,
        visible=True,
        locked=False,
    )


def _build_dme_tile() -> ProductTileHub:
    """Build Find DME tile."""
    return ProductTileHub(
        key="dme",
        title="Find DME",
        desc="Identify and source durable medical equipment (DME).",
        blurb="Discover what DME you may need, learn about coverage options, and find local suppliers for mobility aids, bathroom safety equipment, and more.",
        image_square="dme.png",
        meta_lines=["≈6 min • Auto-saves"],
        primary_label="Start",
        primary_route="?page=dme",
        progress=0,
        variant="teal",
        order=70,
        visible=True,
        locked=False,
    )


def _build_med_manage_tile() -> ProductTileHub:
    """Build Medication Management tile."""
    return ProductTileHub(
        key="med_manage",
        title="Medication Management",
        desc="Connected support for safe and reliable medication routines.",
        blurb="Smart medication management made simple. Ensure medications are taken correctly and on time with connected support powered by Omcare. Remote dispensing and monitoring tools help promote safety, independence, and peace of mind — especially for those managing complex medication schedules. Easily track doses, manage reminders, and stay connected to care support teams.",
        image_square="med_manage.png",
        meta_lines=["≈5 min • Auto-saves"],
        primary_label="Start",
        primary_route="?page=med_manage",
        progress=0,
        variant="teal",
        order=10,
        visible=True,
        locked=False,
    )


def _build_predictive_health_tile() -> ProductTileHub:
    """Build Predictive Health Analytics tile."""
    return ProductTileHub(
        key="predictive_health",
        title="Predictive Health Analytics",
        desc="AI-powered insights for cognitive and mobility health.",
        blurb="Smarter insights for safer living. Predictive Health Analytics, powered by Senior Life AI, uses advanced technology to detect early signs of cognitive decline and fall risk. It analyzes changes in mobility, speech, and other daily patterns to help you and your loved ones take proactive steps toward well-being. Stay ahead of potential risks with continuous insight and guidance.",
        image_square="predictive_health.png",
        meta_lines=["≈6 min • Auto-saves"],
        primary_label="Start",
        primary_route="?page=predictive_health",
        progress=0,
        variant="teal",
        order=20,
        visible=True,
        locked=False,
    )
