"""
Professionals Landing Page - Demo Version

This page shows the Professional Hub with Professional-specific Navi.
For demo purposes only - authentication is disabled.
"""

import streamlit as st

from core.base_hub import render_dashboard_body
from core.navi import render_navi_panel
from core.product_tile import ProductTileHub
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def _build_professional_tiles():
    """Build the 6 Professional product tiles for demo."""
    
    # Demo data
    pending_actions = 7
    new_referrals = 3
    cases_needing_updates = 5
    
    tiles = [
        ProductTileHub(
            key="prof-dashboard",
            title="Professional Dashboard",
            desc="Overview and priorities",
            blurb="At-a-glance priorities and recent activity across all your cases.",
            badges=[{"label": "7 new", "tone": "brand"}],
            meta_lines=[
                f"{pending_actions} pending actions",
                f"{new_referrals} new referrals today",
            ],
            primary_label="Open Dashboard",
            primary_route="?go=hub_professional",
            order=10,
        ),
        ProductTileHub(
            key="prof-client-list",
            title="Client List / Search",
            desc="Find and access client profiles",
            blurb="Find clients and open their profiles with full case history.",
            meta_lines=[
                "Search by name, ID, or case number",
                "Quick filters for active cases",
            ],
            primary_label="Find a Client",
            primary_route="?go=hub_professional",
            order=20,
        ),
        ProductTileHub(
            key="prof-case-mgmt",
            title="Case Management & Referrals",
            desc="Track cases and referrals",
            blurb="Create, track, and update cases or referrals with integrated notes.",
            badges=[{"label": f"{cases_needing_updates} due", "tone": "neutral"}],
            meta_lines=[
                f"{cases_needing_updates} cases need updates",
                "Automated status tracking",
            ],
            primary_label="Manage Cases",
            primary_route="?go=hub_professional",
            order=30,
        ),
        ProductTileHub(
            key="prof-scheduling",
            title="Scheduling + Analytics",
            desc="Appointments and metrics",
            blurb="Manage appointments and view engagement metrics across your caseload.",
            badges=[{"label": "3 due today", "tone": "ai"}],
            meta_lines=[
                "Calendar integration available",
                "Weekly performance reports",
            ],
            primary_label="View Schedule",
            primary_route="?go=hub_professional",
            order=40,
        ),
        ProductTileHub(
            key="prof-recidivism",
            title="Recidivism Assessment / Solutions",
            desc="View assessments and flags",
            blurb="Open assessment summaries and recidivism-risk flags for your clients.",
            meta_lines=[
                "Risk scores and alerts included",
                "Historical comparison views",
            ],
            primary_label="View Assessments",
            primary_route="?go=hub_professional",
            order=50,
        ),
        ProductTileHub(
            key="prof-crm",
            title="Advisor Mode Navi (CRM Query Engine)",
            desc="Professional CRM insights",
            blurb="Professional-grade CRM queries and quick insights powered by AI.",
            badges=[{"label": "Beta", "tone": "ai"}],
            meta_lines=[
                "Natural language queries",
                "Export to reports or share links",
            ],
            primary_label="Open CRM",
            primary_route="?go=hub_professional",
            order=60,
        ),
    ]
    
    return tiles


def render(ctx=None):
    """Render Professional page with Professional-specific Navi."""
    
    # Build Professional tiles
    tiles = _build_professional_tiles()
    
    # Use callback pattern to render Navi AFTER header
    def render_content():
        # Render Professional-specific Navi panel
        render_navi_panel(location="hub", hub_key="professional")
        
        # Render hub body HTML WITHOUT title/subtitle (Navi replaces them)
        body_html = render_dashboard_body(
            title=None,
            subtitle=None,
            hub_guide_block=None,  # Navi replaces any hub guide
            cards=tiles,
        )
        st.markdown(body_html, unsafe_allow_html=True)
    
    # Render with simple header/footer
    render_header_simple(active_route="professionals")
    render_content()
    render_footer_simple()
