"""Discovery Learning Product - First-Touch Onboarding

Phase 5A: First-touch onboarding experience that introduces NAVI and the journey.
Phase 5B: Refactored to use learning_template.py for consistent UX.

Purpose:
- Welcome new users to Senior Navigator
- Introduce NAVI persona and capabilities
- Explain the three-phase journey (Discovery → Planning → Post-Planning)
- Provide scoped NAVI chat for questions about the platform

Flow:
1. Welcome and NAVI introduction
2. Journey overview with phase visualization
3. Scoped NAVI chat for platform questions
4. Continue to GCP or return to Lobby
"""

from core.learning_template import render_learning


def render():
    """Render Discovery Learning using the learning template.
    
    Phase 5B: Uses standardized learning_template for consistent UX.
    """
    
    # Introduction text
    intro = """
### 👋 Welcome to Senior Navigator!

Hi, I'm **NAVI** — your personal guide through the senior care planning process. 
I'm here to help you explore options, understand costs, and make informed decisions 
with confidence and support every step of the way.

💡 **What Makes This Different:**
- **Personalized & Empathetic** - Your journey is unique, and I'll adapt to your needs
- **Expert-Backed** - Our recommendations are based on industry standards and clinical expertise
- **At Your Pace** - No pressure, no rush. Take the time you need to feel confident

Let's take a moment to understand what we'll do together.
"""
    
    # Content sections
    sections = [
        {
            "title": "🎯 What We'll Do Together",
            "content": """
We'll guide you through three key phases:

**1. Discovery Phase 🔵**
- Complete the Guided Care Plan to understand your care needs
- Get a personalized care recommendation
- Learn what your recommendation means

**2. Planning Phase 🟢**
- Explore cost estimates and financial options
- Connect with professional advisors
- Build your personalized care plan

**3. Post-Planning Phase 🟣**
- Access additional resources and support services
- Prepare for advisor consultations
- Continue learning with educational content

Each phase builds on the last, but you can always move at your own pace.
"""
        },
        {
            "title": "🧭 Your Journey Ahead",
            "content": """
```
Discovery  →  Planning  →  Post-Planning
   🔵           🟢             🟣
```

**Right now:** You're in the **Discovery Phase**  
**Next step:** Complete your Guided Care Plan to get started

Don't worry — I'll be with you every step of the way, providing guidance and answering 
your questions as they come up.
"""
        },
    ]
    
    # Resources
    resources = [
        {
            "type": "link",
            "url": "https://www.conciergecareadvisors.com/about",
            "title": "About Concierge Care Advisors",
            "description": "Learn more about our team and mission"
        },
        {
            "type": "link",
            "url": "https://www.medicare.gov/what-medicare-covers/what-part-a-covers/long-term-care",
            "title": "Understanding Long-Term Care",
            "description": "Medicare's guide to long-term care options"
        },
    ]
    
    # Render using learning template
    render_learning(
        title="🧭 Start Your Discovery Journey",
        intro=intro,
        topic="senior_navigator_overview",
        resources=resources,
        phase="discovery",
        tile_key="discovery_learning",
        sections=sections,
        next_route="gcp_v4",  # Continue to GCP after completion
    )


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
            # Phase 5K: Direct navigation to lobby
            st.query_params.clear()
            st.query_params["page"] = "hub_lobby"
            st.rerun()
    
    with col2:
        if st.button("Complete Discovery Journey", type="primary", use_container_width=True):
            # Mark as complete
            _mark_complete()
            # Show success message
            st.success("✅ Discovery Journey marked as complete! You can now find it in Completed Journeys.")
            # Advance to planning phase
            advance_to("planning")
            # Phase 5K: Return to lobby instead of navigating to GCP
            # User can start GCP from lobby when ready
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
