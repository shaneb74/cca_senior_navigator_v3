"""Learn About My Recommendation - Educational Bridge Product

Phase 4B: Educational and empathetic step between GCP and Cost Planner.
Helps users understand their recommendation before planning costs or scheduling advisors.

Flow:
1. Display personalized care recommendation from GCP
2. NAVI provides educational context and resources
3. User reads and reflects
4. Continue to Cost Planner when ready

Architecture:
- Reads care recommendation from MCIP
- Provides tier-specific educational content
- Tracks completion in MCIP for tile state
- Routes to Cost Planner on continue
"""

import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def render():
    """Render Learn About My Recommendation product."""
    
    # Render header
    render_header_simple(active_route="learn_recommendation")
    
    # Initialize MCIP
    MCIP.initialize()
    
    # Get care recommendation
    care_rec = MCIP.get_care_recommendation()
    
    if not care_rec or not care_rec.tier:
        # No recommendation available - redirect to GCP
        st.warning("⚠️ Please complete your Guided Care Plan first to see your recommendation.")
        if st.button("Start Guided Care Plan"):
            route_to("gcp_v4")
        render_footer_simple()
        return
    
    # Get user name for personalization
    person_name = st.session_state.get("person_name", "")
    
    # Page title
    st.title("🧭 Understanding Your Care Recommendation")
    
    # NAVI Introduction
    st.markdown("---")
    st.markdown(f"""
    ### 👋 Hi{f", {person_name}" if person_name else ""}! I'm NAVI
    
    Before we dive into costs and planning, let's take a moment to understand what your 
    care recommendation means and how it can support you or your loved one.
    """)
    
    # Display recommendation
    st.markdown("---")
    
    # Map tier to display name
    tier_display_map = {
        "in_home": "In-Home Care",
        "in_home_care": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (Enhanced Support)",
        "independent": "Independent Living",
    }
    
    tier_display = tier_display_map.get(care_rec.tier, care_rec.tier.replace("_", " ").title())
    
    st.success(f"### 🎯 Your Recommended Care Level: **{tier_display}**")
    
    # Tier-specific educational content
    _render_tier_education(care_rec.tier, person_name)
    
    # Reflection questions
    st.markdown("---")
    st.markdown("### 💭 Questions to Consider")
    _render_reflection_questions(care_rec.tier)
    
    # Additional resources
    st.markdown("---")
    with st.expander("📚 Learn More About This Care Option"):
        _render_additional_resources(care_rec.tier)
    
    # Mark as viewed
    if "learn_recommendation_viewed" not in st.session_state:
        st.session_state["learn_recommendation_viewed"] = True
    
    # Continue to Cost Planner
    st.markdown("---")
    st.markdown("### 🎯 Ready to Continue?")
    st.markdown("Next, we'll help you understand the costs associated with this care level.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Return to Lobby", use_container_width=True):
            route_to("hub_lobby")
    
    with col2:
        if st.button("Continue to Cost Planner →", type="primary", use_container_width=True):
            # Mark as complete
            _mark_complete()
            # Navigate to Cost Planner
            route_to("cost_intro")
    
    # Render footer
    render_footer_simple()


def _render_tier_education(tier: str, person_name: str):
    """Render educational content specific to care tier."""
    
    if tier in ("in_home", "in_home_care"):
        st.info("""
        ### 🏡 What In-Home Care Means
        
        In-home care allows you to stay in the comfort of your own home while receiving 
        professional support with daily activities. This care is flexible and can be adjusted 
        as needs change.
        
        **What to Expect:**
        - ✅ Stay in your familiar environment
        - ✅ Personalized care schedule (hourly or daily)
        - ✅ Help with activities like bathing, dressing, meals, medication
        - ✅ Companionship and social engagement
        - ✅ Family involvement remains strong
        
        **Key Considerations:**
        - Home safety modifications may be needed
        - Family or neighbors provide additional oversight
        - Care hours can be increased as needs grow
        """)
    
    elif tier == "assisted_living":
        st.info("""
        ### 🏘️ What Assisted Living Means
        
        Assisted Living communities provide a supportive environment where residents maintain 
        independence while receiving help with daily activities, meals, and wellness programs.
        
        **What to Expect:**
        - ✅ Private or semi-private apartment-style living
        - ✅ 24/7 staff availability for assistance
        - ✅ Three meals daily plus snacks
        - ✅ Social activities, events, and outings
        - ✅ Medication management and reminders
        - ✅ Housekeeping and laundry services
        
        **Key Considerations:**
        - Community living with neighbors and social opportunities
        - Less isolation than living alone at home
        - Staff trained in senior care and safety
        - Most communities offer varying levels of care as needs change
        """)
    
    elif tier in ("memory_care", "memory_care_high_acuity"):
        st.info("""
        ### 🧠 What Memory Care Means
        
        Memory Care communities are specialized environments designed for individuals with 
        Alzheimer's, dementia, or other cognitive conditions. They provide enhanced safety, 
        structured routines, and therapeutic activities.
        
        **What to Expect:**
        - ✅ Secure environment to prevent wandering
        - ✅ Staff specially trained in dementia care
        - ✅ Structured daily routines and memory-enhancing activities
        - ✅ Lower staff-to-resident ratios for personalized attention
        - ✅ Cognitive therapies and engagement programs
        - ✅ 24/7 supervision and support
        
        **Key Considerations:**
        - Environment designed to reduce confusion and anxiety
        - Family education and support groups often available
        - Focus on dignity, comfort, and quality of life
        - Care plans adapted as cognitive needs evolve
        """)
    
    elif tier == "independent":
        st.info("""
        ### 🌟 What Independent Living Means
        
        Independent Living communities are designed for active seniors who don't need daily 
        assistance but want the convenience, social opportunities, and amenities of community living.
        
        **What to Expect:**
        - ✅ Apartment or cottage-style homes
        - ✅ Maintenance-free living (no yard work, repairs)
        - ✅ Social activities, fitness centers, dining options
        - ✅ Transportation services
        - ✅ Emergency call systems for peace of mind
        
        **Key Considerations:**
        - Focus on lifestyle and convenience rather than care
        - Great for those who want community without losing independence
        - Many communities offer "continuum of care" if needs change
        """)
    
    else:
        st.info(f"""
        ### 📋 About Your Care Recommendation
        
        Based on your assessment, we've recommended **{tier.replace("_", " ").title()}** as the 
        most appropriate care level. This will help ensure safety, support, and quality of life.
        """)


def _render_reflection_questions(tier: str):
    """Render reflective questions to help users process recommendation."""
    
    questions = [
        "💭 How does this recommendation align with your expectations?",
        "🏡 What concerns or questions do you have about this care option?",
        "👨‍👩‍👧‍👦 Who in your family or support network should you discuss this with?",
        "⏰ What's your timeline for making a decision or taking next steps?",
    ]
    
    for question in questions:
        st.markdown(f"- {question}")
    
    st.caption("*These are private reflections - you don't need to answer here. "
               "Think about these questions as you explore your options.*")


def _render_additional_resources(tier: str):
    """Render additional educational resources."""
    
    st.markdown("""
    **Educational Resources:**
    - 📖 [A Place for Mom - Care Options Guide](https://www.aplaceformom.com/)
    - 🏥 [Medicare - Long-Term Care Information](https://www.medicare.gov/what-medicare-covers/what-part-a-covers/long-term-care)
    - 💼 [Eldercare Locator - Find Local Resources](https://eldercare.acl.gov/)
    - 📞 **Questions?** Reach out to your Care Advisor after scheduling your appointment
    
    **Next Steps:**
    1. Review the cost estimates in the Cost Planner
    2. Discuss options with family members
    3. Schedule a call with your Care Advisor to ask questions
    4. Tour facilities or interview in-home care providers
    """)


def _mark_complete():
    """Mark Learn About Recommendation as complete in MCIP."""
    # Set completion flag in session state
    st.session_state["learn_recommendation_complete"] = True
    
    # Mark as complete in MCIP
    try:
        MCIP.mark_product_complete("learn_recommendation")
        print("[LEARN_REC] Marked as complete in MCIP")
    except Exception as e:
        print(f"[LEARN_REC] Error marking complete: {e}")
