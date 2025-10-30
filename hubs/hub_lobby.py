# hubs/hub_lobby.py
"""
Lobby Hub - Visual Dashboard Entry Point

Modernized dashboard design matching Senior Navigator design system.
Provides entry point to core products: GCP, Cost Planner, PFMA, and FAQ.
"""

import streamlit as st
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

__all__ = ["render"]


def render(ctx=None) -> None:
    """Render the Lobby Hub with modernized dashboard styling."""
    
    # Load dashboard CSS
    st.markdown(
        f"<style>{open('core/styles/dashboard.css').read()}</style>",
        unsafe_allow_html=True
    )
    
    # Render header
    render_header_simple(active_route="hub_lobby")
    
    # Page title
    st.title("Senior Navigator Dashboard")
    st.markdown("Choose a tool to get started with your care planning journey.")
    
    # Dashboard cards in grid layout
    with st.container():
        st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
        
        # Card 1: Guided Care Plan
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("Guided Care Plan")
        st.markdown('<p class="subtext">Explore and compare care options.</p>', unsafe_allow_html=True)
        if st.button("Start", key="gcp_start"):
            from core.nav import route_to
            route_to("gcp_v4")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Card 2: Cost Planner
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("Cost Planner")
        st.markdown('<p class="subtext">Estimate and plan financial coverage.</p>', unsafe_allow_html=True)
        if st.button("Start", key="cost_start"):
            from core.nav import route_to
            route_to("cost_intro")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Card 3: Plan With My Advisor
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("Plan With My Advisor")
        st.markdown('<p class="subtext">Schedule and prepare for your next advisor meeting.</p>', unsafe_allow_html=True)
        if st.button("Open", key="pfma_open"):
            from core.nav import route_to
            route_to("pfma_v3")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Card 4: FAQs & Answers
        st.markdown('<div class="dashboard-card gradient-box">', unsafe_allow_html=True)
        st.subheader("FAQs & Answers")
        st.markdown('<p class="subtext">Instant help from NAVI AI.</p>', unsafe_allow_html=True)
        if st.button("Open", key="faq_open"):
            from core.nav import route_to
            route_to("faq")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Render footer
    render_footer_simple()
