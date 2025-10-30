"""Discovery Learning Product - Phase 5A

First-touch onboarding experience that introduces NAVI and orients users
to the Senior Navigator application.

Purpose:
- Welcome users to the application
- Introduce NAVI as their guide
- Explain what to expect in the discovery journey
- Set expectations for the care planning process

Flow:
1. Welcome message and NAVI introduction
2. Overview of the discovery process
3. What to expect next
4. Continue to Guided Care Plan

Phase: Discovery (first tile in journey)
"""

import streamlit as st

from core.journeys import advance_to, get_current_journey
from core.mcip import MCIP
from core.nav import route_to
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def render():
    """Render Discovery Learning product - first-touch onboarding."""
    
    # Render header
    render_header_simple(active_route="discovery_learning")
    
    # Initialize MCIP
    MCIP.initialize()
    
    # Page title
    st.title("🧭 Start Your Discovery Journey")
    
    # Welcome section
    st.markdown("### Welcome to Senior Navigator!")
    
    # NAVI introduction
    st.markdown("""
    > 👋 **Hi, I'm NAVI** — your personal guide through this care planning journey.
    >
    > I'm here to help you understand your options, explore what's available, and 
    > make informed decisions about care for you or your loved one.
    """)
    
    st.markdown("---")
    
    # What to expect
    st.markdown("### 🎯 What We'll Do Together")
    
    st.info("""
    **Together, we'll explore:**
    
    - 🏥 **Your Care Needs** - Understand current health, daily living, and safety considerations
    - 💰 **Cost Planning** - Get realistic estimates for different care options
    - 👥 **Your Support Network** - Identify resources and assistance available to you
    - 📋 **Next Steps** - Create a clear action plan moving forward
    
    This isn't just about numbers and assessments — it's about understanding your unique 
    situation and finding the right path forward.
    """)
    
    # Journey overview
    st.markdown("---")
    st.markdown("### 🗺️ Your Journey Ahead")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Discovery Phase**  
        🔵 Where you are now
        
        - Welcome & orientation
        - Guided Care Plan
        - Learn about options
        """)
    
    with col2:
        st.markdown("""
        **Planning Phase**  
        🟢 Coming next
        
        - Cost estimation
        - Financial planning
        - Advisor scheduling
        """)
    
    with col3:
        st.markdown("""
        **Post-Planning**  
        🟣 After planning
        
        - Clinical reviews
        - Ongoing support
        - Resource connections
        """)
    
    # What makes this different
    st.markdown("---")
    st.markdown("### ✨ What Makes This Different")
    
    st.success("""
    **Personalized & Empathetic**  
    Every family's situation is unique. I'll adapt my guidance based on your specific needs, 
    timeline, and preferences. No one-size-fits-all solutions here.
    
    **Expert-Backed**  
    Our recommendations come from years of experience helping families navigate senior care. 
    You'll get access to trusted advisors when you need them.
    
    **At Your Pace**  
    Take your time. Save your progress. Come back when you're ready. There's no rush, 
    and you can revisit any section at any time.
    """)
    
    # Getting started
    st.markdown("---")
    st.markdown("### 🚀 Ready to Begin?")
    
    st.markdown("""
    Your first step is the **Guided Care Plan** — a 5-minute assessment that helps us 
    understand your situation and recommend the right level of care.
    
    Don't worry — I'll be with you every step of the way, explaining what each question 
    means and why it matters.
    """)
    
    # Mark as viewed
    if "discovery_learning_viewed" not in st.session_state:
        st.session_state["discovery_learning_viewed"] = True
    
    # Continue buttons
    st.markdown("<br/>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Return to Lobby", use_container_width=True):
            route_to("hub_lobby")
    
    with col2:
        if st.button("Continue to Guided Care Plan →", type="primary", use_container_width=True):
            # Mark as complete
            _mark_complete()
            # Advance to planning phase
            advance_to("planning")
            # Navigate to GCP
            route_to("gcp_v4")
    
    # Render footer
    render_footer_simple()


def _mark_complete():
    """Mark Discovery Learning as complete in MCIP."""
    st.session_state["discovery_learning_complete"] = True
    
    # Mark as complete in MCIP
    try:
        MCIP.mark_product_complete("discovery_learning")
        print("[DISCOVERY_LEARNING] Marked as complete in MCIP")
    except Exception as e:
        print(f"[DISCOVERY_LEARNING] Error marking complete: {e}")
