"""Discovery Learning Product - AI-Enhanced Onboarding

Phase Post-CSS: Lightweight, Navi-guided experience with embedded AI/FAQ functionality.

Purpose:
- Welcome new users to Senior Navigator with conversational introduction
- Introduce NAVI persona and capabilities
- Provide contextual Q&A within the page
- Maintain progress tracking and seamless navigation

Flow:
1. Navi-guided introduction
2. Quick FAQ section
3. Completion tracking
"""


import streamlit as st

from core.journeys import advance_to
from core.mcip import MCIP
from core.navi_dialogue import render_navi_message
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def render():
    """Render Discovery Learning product - AI-enhanced onboarding."""
    
    # Render header
    render_header_simple(active_route="discovery_learning")
    
    # Initialize MCIP
    MCIP.initialize()
    
    # Page title
    st.markdown("### 🌟 Welcome to Your Discovery Journey")
    
    # Navi-guided introduction
    render_navi_message(
        {
            "icon": "🧭",
            "text": "Hi, I'm Navi. I'll walk you through what this app can do — and answer any questions along the way.",
            "subtext": "Let's explore Senior Navigator together."
        },
        show_cta=False
    )
    
    st.write("""
This is your introduction to how **Senior Navigator** works — including:
- How to start your Discovery Journey
- What the Guided Care Plan does
- How to explore cost planning options
- What to expect from your advisor experience
""")
    
    # Quick FAQ section
    st.markdown("#### Quick Answers")
    
    faq_items = [
        ("⏱️ How long does this take?", "Most families complete Discovery in about 10–15 minutes."),
        ("🧭 What happens next?", "You'll move on to your Guided Care Plan, where Navi personalizes your recommendations."),
        ("💰 What about costs?", "After your care recommendation, you'll get detailed cost estimates in the Cost Planner."),
        ("👥 Can I get help?", "Yes! You can schedule time with our professional advisors at any point in your journey.")
    ]
    
    for question, answer in faq_items:
        with st.expander(question):
            st.write(answer)
    
    st.markdown("---")
    
    # Mark as viewed
    if "discovery_learning_viewed" not in st.session_state:
        st.session_state["discovery_learning_viewed"] = True
    
    # Completion section
    st.success("When you're ready, click below to mark this step finished.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Return to Lobby", use_container_width=True):
            st.query_params.clear()
            st.query_params["page"] = "hub_lobby"
            st.rerun()
    
    with col2:
        if st.button("✅ Complete Discovery Journey", type="primary", use_container_width=True):
            # Mark as complete
            _mark_complete()
            # Show success message
            st.success("✅ Discovery Journey complete! Returning to Lobby...")
            # Advance to planning phase
            advance_to("planning")
            # Return to lobby
            st.query_params.clear()
            st.query_params["page"] = "hub_lobby"
            st.rerun()
    
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
