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
    
    # Hero Title
    st.markdown('<h1 class="discovery-title">✨ Welcome to Your Discovery Journey</h1>', unsafe_allow_html=True)
    
    # Navi intro box
    st.markdown("""
    <div class="navi-box">
        <p><b>Hi, I'm Navi.</b> I'll help you discover everything Senior Navigator can do — and guide you step by step.</p>
        <p class="subtext">We'll explore how this app helps you and your loved ones make confident care decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Intro paragraph
    st.markdown("""
    <p class="discovery-intro">
        Concierge Care Advisors Senior Navigator — a revolutionary way to navigate the complexities of Senior Care Options.<br>
        Learn about your Options & Cost.
    </p>
    """, unsafe_allow_html=True)
    
    # Embedded YouTube video (smaller, centered)
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    st.markdown("""
    <iframe 
        width="560" 
        height="315" 
        src="https://www.youtube.com/embed/eHFcJSS-2l4" 
        title="Curious about Senior Living?" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen
        class="video-frame">
    </iframe>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
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
            st.session_state["navi_discovery_query"] = "How long does the Guided Care Plan take?"
            st.rerun()
    with col2:
        if st.button("What does the Cost Planner do?", use_container_width=True, key="faq_2"):
            st.session_state["navi_discovery_query"] = "What does the Cost Planner do?"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Mark as viewed
    if "discovery_learning_viewed" not in st.session_state:
        st.session_state["discovery_learning_viewed"] = True
    
    # Closing CTA Section
    st.markdown('<p style="margin-top:1.5rem; font-size:1.05rem; text-align:center; font-weight:500;">Ready to begin your journey?</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Return to Lobby", use_container_width=True, key="return_lobby"):
            st.query_params.clear()
            st.query_params["page"] = "hub_lobby"
            st.rerun()
    
    with col2:
        if st.button("✅ Continue to Care Plan", type="primary", use_container_width=True, key="continue_gcp"):
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
    /* === Layout === */
    .main {
        padding: 2rem 3rem;
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
    }

    /* === Title === */
    .discovery-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: #0E1E54;
        text-align: center;
        margin: 0 auto 1.25rem;
        line-height: 1.2;
    }

    /* === Navi box === */
    .navi-box {
        background: #f7f8ff;
        border-left: 5px solid #5b5fc7;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin: 0 auto 2rem;
        max-width: 720px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .navi-box p {
        margin: 0.25rem 0;
        line-height: 1.5;
    }
    .navi-box b {
        color: #0E1E54;
        font-weight: 700;
    }
    .navi-box .subtext {
        color: #596080;
        font-size: 0.95rem;
    }

    /* === Intro text === */
    .discovery-intro {
        color: #222;
        font-size: 1.05rem;
        line-height: 1.55;
        text-align: center;
        max-width: 700px;
        margin: 0 auto 2rem;
    }

    /* === Video === */
    .video-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2.25rem;
    }
    .video-frame {
        width: 90%;
        max-width: 720px;
        height: 405px;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }

    /* === Ask Navi === */
    .ask-navi-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0E1E54;
        margin-bottom: 0.75rem;
        text-align: center;
    }
    
    /* Style the text input */
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 0.95rem !important;
        border: 1px solid #dce0e6 !important;
    }
    
    /* FAQ buttons */
    .ask-navi-buttons {
        margin-top: 0.75rem;
        margin-bottom: 2rem;
        max-width: 720px;
        margin-left: auto;
        margin-right: auto;
    }

    /* === Footer buttons === */
    .footer-buttons {
        display: flex;
        gap: 1rem;
        margin: 2rem auto 2rem auto;
        max-width: 600px;
    }

    /* === Responsive === */
    @media (max-width: 768px) {
        .main {
            padding: 1rem 1.5rem;
        }
        
        .discovery-title {
            font-size: 1.5rem;
        }
        
        .navi-box {
            padding: 1rem;
            max-width: 100%;
        }
        
        .discovery-intro {
            font-size: 0.95rem;
        }
        
        .video-frame {
            height: 220px;
        }
        
        .ask-navi-title {
            font-size: 1.2rem;
        }
        
        .footer-buttons {
            flex-direction: column;
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
