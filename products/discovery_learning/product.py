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
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def render():
    """Render Discovery Learning - elegant story-driven welcome with video."""
    
    # Render header
    render_header_simple(active_route="discovery_learning")
    
    # Initialize MCIP
    MCIP.initialize()
    
    # Inject custom CSS for this page
    _inject_discovery_styles()
    
    # ========================================
    # SECTION: HERO
    # ========================================
    st.markdown('<h1 class="discovery-title">✨ Welcome to Your Discovery Path</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p class="discovery-subtitle">
        A simple step-by-step walkthrough to explore care options and plan confidently with Senior Navigator.
    </p>
    """, unsafe_allow_html=True)
    
    # Hero CTA button
    if st.button("Begin My Discovery →", type="primary", use_container_width=False, key="hero_begin"):
        # Scroll to video section (visual feedback)
        st.toast("Let's start with a quick video overview!")
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # ========================================
    # SECTION: VIDEO OVERVIEW
    # ========================================
    st.markdown('<h3 class="section-title">🎥 Learn About the Navigator</h3>', unsafe_allow_html=True)
    
    # Embedded YouTube video
    st.markdown("""
    <div class="video-container">
        <iframe class="video-frame"
            src="https://www.youtube.com/embed/BSJMIRI59b4"
            title="Learn About Senior Navigator"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
        </iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("See how the Guided Care Plan and Cost Planner work together to help families make informed decisions.")
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # ========================================
    # SECTION: ASK NAVI — LLM
    # ========================================
    st.markdown('<h3 class="section-title">🤖 Meet Navi — Your Digital Advisor</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="navi-intro">
        <p>"Hi, I'm Navi! Ask me anything about Senior Navigator—how to get started, how the Care Plan works, or what the Cost Planner does."</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat input
    navi_query = st.chat_input("Type your question to Navi...")
    
    if navi_query:
        # Simple contextual responses
        responses = {
            "discovery": "The Discovery Path is your introduction to Senior Navigator. It takes about 10-15 minutes and helps you understand what we offer and how I can guide you through your care planning process.",
            "care plan": "The Guided Care Plan takes about 5-10 minutes. You'll answer questions about daily living, health needs, and safety concerns. I'll be with you every step, explaining what each question means.",
            "long": "Most families complete the Discovery Path in 10-15 minutes. The full Guided Care Plan adds another 5-10 minutes. You can always save and come back later.",
            "cost": "After your care recommendation, you'll access the Cost Planner. It provides detailed estimates for different care types, including in-home care, assisted living, and memory care options.",
            "path": "The Discovery Path is your introduction to Senior Navigator. It takes about 10-15 minutes and helps you understand what we offer.",
        }
        
        # Simple keyword matching
        response = None
        query_lower = navi_query.lower()
        for key, answer in responses.items():
            if key in query_lower:
                response = answer
                break
        
        if not response:
            response = "That's a great question! I'm here to help you understand your care planning journey. Try asking about the Discovery Path, Care Plan, costs, or how long things take."
        
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"**Navi:** {response}")
    
    # Quick Questions buttons
    st.markdown('<p class="quick-questions-label">Quick Questions:</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("What is the Discovery Path?", use_container_width=True, key="faq_discovery"):
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown("**Navi:** The Discovery Path is your introduction to Senior Navigator. It takes about 10-15 minutes and helps you understand what we offer and how I can guide you through your care planning process.")
    
    with col2:
        if st.button("How long does the Care Plan take?", use_container_width=True, key="faq_duration"):
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown("**Navi:** The Guided Care Plan takes about 5-10 minutes. You'll answer questions about daily living, health needs, and safety concerns. I'll be with you every step, explaining what each question means.")
    
    with col3:
        if st.button("What does the Cost Planner do?", use_container_width=True, key="faq_cost"):
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown("**Navi:** After your care recommendation, you'll access the Cost Planner. It provides detailed estimates for different care types, including in-home care, assisted living, and memory care options.")
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Mark as viewed
    if "discovery_learning_viewed" not in st.session_state:
        st.session_state["discovery_learning_viewed"] = True
    
    # ========================================
    # SECTION: READINESS / CTA
    # ========================================
    st.markdown('<h3 class="section-title">🚀 Ready to Get Started?</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="steps-list">
        <p><strong>Steps to begin:</strong></p>
        <ul>
            <li>① Watch the video   ✅</li>
            <li>② Ask Navi          💬</li>
            <li>③ Begin your Path   🚀</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Return to Lobby", use_container_width=True, key="return_lobby", type="secondary"):
            st.query_params.clear()
            st.query_params["page"] = "hub_lobby"
            st.rerun()
    
    with col2:
        if st.button("✅ Complete My Discovery Path", type="primary", use_container_width=True, key="complete_discovery"):
            # Mark as complete
            _mark_complete()
            # Advance to planning phase
            advance_to("planning")
            # Navigate back to Lobby
            st.query_params.clear()
            st.query_params["page"] = "hub_lobby"
            st.rerun()
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Render footer
    render_footer_simple()


def _inject_discovery_styles():
    """Inject elegant styling for Discovery Journey page."""
    st.markdown("""
    <style>
    /* === Global Styles === */
    body, .main {
        font-family: "Inter", "Segoe UI", Roboto, sans-serif;
        color: #1A1C2B;
    }

    /* === Hero Section === */
    .discovery-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #0E1E54;
        text-align: center;
        margin: 2rem auto 1.25rem;
        line-height: 1.15;
    }
    .discovery-subtitle {
        font-size: 1.15rem;
        font-weight: 500;
        text-align: center;
        color: #4b4f63;
        margin: 0 auto 2rem;
        max-width: 700px;
        line-height: 1.5;
    }

    /* === Section Titles === */
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0E1E54;
        text-align: center;
        margin: 3rem auto 1.5rem;
    }

    /* === Video Section === */
    .video-container {
        text-align: center;
        margin: 2rem auto 1rem;
    }
    .video-frame {
        width: 92%;
        max-width: 780px;
        aspect-ratio: 16 / 9;
        border-radius: 18px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.15);
    }

    /* === Ask Navi Section === */
    .navi-intro {
        background: #f8f9fe;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 12px;
        padding: 1.5rem 1.75rem;
        margin: 0 auto 1.5rem;
        max-width: 760px;
        box-shadow: 0 4px 12px rgba(124, 92, 255, 0.08);
        transition: box-shadow 0.2s ease;
    }
    .navi-intro:hover {
        box-shadow: 0 6px 16px rgba(124, 92, 255, 0.12);
    }
    .navi-intro p {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #32395e;
        margin: 0;
        text-align: center;
    }
    
    .quick-questions-label {
        text-align: center;
        font-weight: 600;
        font-size: 1rem;
        color: #4b4f63;
        margin: 1.5rem 0 0.8rem;
    }

    /* === Readiness / CTA Section === */
    .steps-list {
        background: #f8f9fe;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 0 auto 2rem;
        max-width: 600px;
    }
    .steps-list p {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0E1E54;
        margin-bottom: 1rem;
    }
    .steps-list ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .steps-list li {
        font-size: 1.05rem;
        color: #32395e;
        padding: 0.5rem 0;
        line-height: 1.6;
    }

    /* === Button Styling === */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    div.stButton > button[kind="primary"] {
        background-color: #5b4cf0;
        border: none;
    }
    
    div.stButton > button[kind="primary"]:hover {
        background-color: #4a3dd6;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(91, 76, 240, 0.3);
    }

    /* === Mobile Responsive === */
    @media (max-width: 768px) {
        .discovery-title {
            font-size: 2.1rem;
        }
        .section-title {
            font-size: 1.5rem;
        }
        .video-frame {
            width: 98%;
        }
        .steps-list {
            padding: 1.25rem 1.5rem;
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
