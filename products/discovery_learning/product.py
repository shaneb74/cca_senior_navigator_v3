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
    
    # Hero Title with Subtitle
    st.markdown('<h1 class="discovery-title">✨ Welcome to Your Discovery Journey</h1>', unsafe_allow_html=True)
    st.markdown('<p class="discovery-subtitle">Your step-by-step guide to understanding care options and planning confidently.</p>', unsafe_allow_html=True)
    
    # Navi intro box
    st.markdown("""
    <div class="navi-box">
        <p><b>Hi, I'm Navi.</b> I'll help you discover everything Senior Navigator can do — and guide you step by step.</p>
        <p>We'll explore how this app helps you and your loved ones make confident care decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Intro paragraph
    st.markdown("""
    <div style="text-align: center;">
        <h3 class="discovery-intro" style="text-align: center;">
            Concierge Care Advisors Senior Navigator — a revolutionary way to navigate the complexities of Senior Care Options.<br>
            Learn about your Options & Cost.
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Embedded YouTube video
    st.markdown("""
    <div class="video-container">
        <iframe class="video-frame"
            src="https://www.youtube.com/embed/BSJMIRI59b4"
            title="Curious about Senior Living?"
            frameborder="0"
            allowfullscreen>
        </iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Ask Navi section
    st.markdown('<h3 class="ask-navi-title">💬 Ask Navi</h3>', unsafe_allow_html=True)
    
    navi_query = st.text_input(
        "Ask me anything...",
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
        
        st.info(f"**Navi:** {response}")
    
    # Quick question buttons
    st.markdown('<div class="ask-navi-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("How long does the Guided Care Plan take?", use_container_width=True, key="faq_1"):
            # Display response directly without modifying widget state
            st.info("**Navi:** The Guided Care Plan takes about 5-10 minutes. You'll answer questions about daily living, health needs, and safety concerns. I'll be with you every step, explaining what each question means.")
    with col2:
        if st.button("What does the Cost Planner do?", use_container_width=True, key="faq_2"):
            # Display response directly without modifying widget state
            st.info("**Navi:** After your care recommendation, you'll access the Cost Planner. It provides detailed estimates for different care types, including in-home care, assisted living, and memory care options.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Mark as viewed
    if "discovery_learning_viewed" not in st.session_state:
        st.session_state["discovery_learning_viewed"] = True
    
    # === Discovery Journey CTA Section ===
    st.markdown("""
    <div class="cta-wrapper">
      <div class="cta-note">
        <p>
          When you return to the Lobby, this journey will remain active until all its steps are completed.
          Once finished, it will move automatically to your <strong>My Completed Journeys</strong> section below.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="footer-cta-text">Ready to begin your journey?</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="cta-actions">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⬅ Return to Lobby", use_container_width=True, key="return_lobby", type="secondary"):
            st.query_params.clear()
            st.query_params["page"] = "hub_lobby"
            st.rerun()
    
    with col2:
        if st.button("✅ Complete My Discovery Journey", type="primary", use_container_width=True, key="complete_discovery"):
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
    /* === Global Styles === */
    body, .main {
        font-family: "Inter", "Segoe UI", Roboto, sans-serif;
        color: #1A1C2B;
    }

    /* === Title Section === */
    .discovery-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #0E1E54;
        text-align: center;
        margin: 0 auto 1.25rem;
        line-height: 1.15;
    }
    .discovery-subtitle {
        font-size: 1.15rem;
        font-weight: 500;
        text-align: center;
        color: #4b4f63;
        margin-bottom: 2.25rem;
    }

    /* === Navi Box === */
    .navi-box {
        background: linear-gradient(180deg, #f8f9ff 0%, #f3f4fe 100%);
        border-left: 6px solid #4b52c2;
        border-radius: 12px;
        padding: 1.5rem 1.75rem;
        margin: 0 auto 2.5rem;
        max-width: 760px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }
    .navi-box b {
        font-size: 1.05rem;
        color: #10174a;
    }
    .navi-box p {
        font-size: 1rem;
        line-height: 1.55;
        color: #32395e;
        margin: 0.4rem 0;
    }

    /* === Intro Paragraph === */
    .discovery-intro {
        font-size: 1.05rem;
        color: #2b2e42;
        text-align: center !important;
        line-height: 1.6;
        max-width: 720px;
        margin: 0 auto 2rem !important;
        display: block;
    }

    /* === Video === */
    .video-container {
        text-align: center;
        margin-bottom: 2.75rem;
    }
    .video-frame {
        width: 92%;
        max-width: 780px;
        aspect-ratio: 16 / 9;
        border-radius: 18px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.15);
    }

    /* === Ask Navi Section === */
    .ask-navi-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0E1E54;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Style the text input */
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        padding: 0.9rem !important;
        font-size: 1rem !important;
        max-width: 720px !important;
        width: 90% !important;
    }
    
    /* FAQ buttons */
    .ask-navi-buttons {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.8rem;
        margin-top: 1rem;
        max-width: 760px;
        margin-left: auto;
        margin-right: auto;
    }

    /* === Footer Buttons === */
    .footer-buttons {
        display: flex;
        justify-content: center;
        gap: 1.25rem;
        margin-top: 2.5rem;
    }
    
    .footer-cta-text {
        text-align: center;
        margin-top: 2.5rem;
        font-weight: 600;
        color: #1A1C2B;
    }

    @media (max-width: 768px) {
        .discovery-title {
            font-size: 2.1rem;
        }
        .video-frame {
            height: auto;
        }
        .footer-buttons {
            flex-direction: column;
            align-items: center;
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
