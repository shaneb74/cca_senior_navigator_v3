"""Discovery Learning Product - Human-Centered Welcome Screen

Phase Post-CSS: Beautiful, emotionally intelligent onboarding page.

This is the first page many users see — it must feel like home:
warm, intelligent, effortless. Modern SaaS-quality onboarding with Navi guidance.

Visual Direction:
- Clean white space, soft navy text, subtle accents
- Rounded corners, gentle shadows, no unnecessary borders
- Balanced typography with generous spacing
- Fully responsive (mobile-friendly)

Structure:
1. Hero with Navi introduction
2. Three horizontal info tiles
3. Inline Navi search (conversational, no expanders)
4. Centered CTA section
"""

import streamlit as st

from core.journeys import advance_to
from core.mcip import MCIP
from core.navi_dialogue import render_navi_message
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def render():
    """Render Discovery Learning - elegant Navi-guided welcome."""
    
    # Render header
    render_header_simple(active_route="discovery_learning")
    
    # Initialize MCIP
    MCIP.initialize()
    
    # Inject custom CSS for this page
    _inject_discovery_styles()
    
    # Hero / Navi Introduction
    st.markdown('<div class="discovery-hero">', unsafe_allow_html=True)
    st.markdown("## ✨ Welcome to Your Discovery Journey")
    
    render_navi_message(
        {
            "icon": "🧭",
            "text": "Hi, I'm Navi. I'll help you discover everything Senior Navigator can do — and guide you step by step.",
            "subtext": "We'll explore how this app helps you and your loved ones make confident care decisions."
        },
        show_cta=False
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Informational Overview - Three Horizontal Tiles
    st.markdown('<div class="info-tiles-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-tile">
            <div class="tile-icon">🧭</div>
            <h3 class="tile-title">Guided Care Plan</h3>
            <p class="tile-description">Answer a few questions and get a personalized care path.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-tile">
            <div class="tile-icon">💰</div>
            <h3 class="tile-title">Cost Planner</h3>
            <p class="tile-description">Estimate expenses, compare care types, and understand funding options.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-tile">
            <div class="tile-icon">🎨</div>
            <h3 class="tile-title">Visual Insights</h3>
            <p class="tile-description">DALL·E creates visuals that bring your care plan to life.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Ask Navi - Inline conversational search
    st.markdown('<div class="ask-navi-section">', unsafe_allow_html=True)
    st.markdown("### 💬 Ask Navi")
    
    navi_query = st.text_input(
        "Ask me anything about your journey...",
        key="navi_discovery_query",
        label_visibility="collapsed",
        placeholder="What is the Discovery Journey? How long does the Care Plan take?"
    )
    
    if navi_query:
        # Simple contextual responses
        responses = {
            "discovery": "The Discovery Journey is your introduction to Senior Navigator. It takes about 10-15 minutes and helps you understand what we offer and how I can guide you through your care planning process.",
            "care plan": "The Guided Care Plan takes about 5-10 minutes. You'll answer questions about daily living, health needs, and safety concerns. I'll be with you every step, explaining what each question means.",
            "long": "Most families complete the Discovery Journey in 10-15 minutes. The full Guided Care Plan adds another 5-10 minutes. You can always save and come back later.",
            "information": "Your information is private and secure. We use it only to personalize your care recommendations and cost estimates. You control what you share with advisors.",
            "cost": "After your care recommendation, you'll access the Cost Planner. It provides detailed estimates for different care types, including in-home care, assisted living, and memory care options.",
        }
        
        # Simple keyword matching
        response = None
        query_lower = navi_query.lower()
        for key, answer in responses.items():
            if key in query_lower:
                response = answer
                break
        
        if not response:
            response = "That's a great question! I'm here to help you understand your care planning journey. Try asking about the Discovery Journey, Care Plan, costs, or how long things take."
        
        st.markdown(f"""
        <div class="navi-response">
            <strong>Navi:</strong> {response}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Mark as viewed
    if "discovery_learning_viewed" not in st.session_state:
        st.session_state["discovery_learning_viewed"] = True
    
    # Closing CTA Section
    st.markdown('<div class="cta-section">', unsafe_allow_html=True)
    st.markdown('<p class="cta-message">Ready to begin your journey?</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Return to Lobby", use_container_width=True):
            st.query_params.clear()
            st.query_params["page"] = "hub_lobby"
            st.rerun()
    
    with col2:
        if st.button("✅ Continue to Care Plan", type="primary", use_container_width=True):
            # Mark as complete
            _mark_complete()
            # Advance to planning phase
            advance_to("planning")
            # Navigate to GCP
            st.query_params.clear()
            st.query_params["page"] = "gcp_v4"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render footer
    render_footer_simple()


def _inject_discovery_styles():
    """Inject elegant styling for Discovery Journey page."""
    st.markdown("""
    <style>
    /* Discovery Journey - Clean, Human-Centered Design */
    
    .discovery-hero {
        margin-top: 2rem;
        margin-bottom: 3rem;
        text-align: center;
    }
    
    .discovery-hero h2 {
        color: var(--text-primary, #0b132b);
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    
    /* Info Tiles - Horizontal Cards */
    .info-tiles-container {
        display: flex;
        gap: 1.5rem;
        margin: 2rem 0 3rem 0;
    }
    
    .info-tile {
        background: #f9fafb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        text-align: center;
    }
    
    .info-tile:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .tile-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .tile-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary, #0b132b);
        margin-bottom: 0.75rem;
    }
    
    .tile-description {
        font-size: 0.9rem;
        color: var(--text-muted, #64748b);
        line-height: 1.5;
        margin: 0;
    }
    
    /* Ask Navi Section - Inline conversational */
    .ask-navi-section {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .ask-navi-section h3 {
        color: var(--text-primary, #0b132b);
        font-size: 1.2rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .navi-response {
        margin-top: 1rem;
        padding: 1rem;
        background: #f0f4ff;
        border-left: 3px solid #4f46e5;
        border-radius: 8px;
        color: var(--text-primary, #0b132b);
        line-height: 1.6;
    }
    
    /* CTA Section - Centered, clean */
    .cta-section {
        text-align: center;
        margin-top: 3rem;
        margin-bottom: 2rem;
    }
    
    .cta-message {
        font-size: 1.1rem;
        color: var(--text-primary, #0b132b);
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* Responsive - Stack tiles on mobile */
    @media (max-width: 768px) {
        .info-tiles-container {
            flex-direction: column;
        }
        
        .info-tile {
            margin-bottom: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def _mark_complete():
    """Mark Discovery Learning as complete in MCIP."""
    st.session_state["discovery_learning_complete"] = True
    
    # Mark as complete in MCIP
    try:
        MCIP.mark_product_complete("discovery_learning")
        print("[DISCOVERY_LEARNING] Marked as complete in MCIP")
    except Exception as e:
        print(f"[DISCOVERY_LEARNING] Error marking complete: {e}")
