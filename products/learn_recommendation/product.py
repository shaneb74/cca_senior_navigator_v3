"""Learn About My Recommendation - Educational Bridge Product

Phase 4B: Educational and empathetic step between GCP and Cost Planner.
Helps users understand their recommendation before planning costs or scheduling advisors.

Phase 5A enhancements:
- Extended NAVI dialogue with phase-aware guidance
- Interactive "Tell Me More" button with deeper educational content
- Enhanced resource linking and next-step guidance
- Integration with journey phase tracking

Phase Post-CSS: Redesigned to match Discovery Journey layout
- Story-driven single-column design
- Embedded YouTube video for care recommendation education
- Enhanced typography and spacing
- Mobile responsive design

Flow:
1. Display personalized care recommendation from GCP
2. NAVI provides educational context
3. Video explains the care level
4. User reads and reflects
5. Continue to Cost Planner when ready

Architecture:
- Reads care recommendation from MCIP
- Provides tier-specific educational content and videos
- Tracks completion in MCIP for tile state
- Routes to Cost Planner on continue
"""

import streamlit as st

from core.mcip import MCIP
from core.nav import route_to
from core.journeys import advance_to
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple


def render():
    """Render Learn About My Recommendation product - Discovery Journey style."""
    
    # Render header
    render_header_simple(active_route="learn_recommendation")
    
    # Initialize MCIP
    MCIP.initialize()
    
    # Inject custom CSS for this page
    _inject_learn_recommendation_styles()
    
    # Get care recommendation
    care_rec = MCIP.get_care_recommendation()
    
    # TEMPORARY: Default to Assisted Living for preview if no recommendation
    if not care_rec or not care_rec.tier:
        # Create a mock care recommendation for preview
        from types import SimpleNamespace
        care_rec = SimpleNamespace(tier="assisted_living")
        st.info("ℹ️ **Preview Mode:** Showing Assisted Living example. Complete your Guided Care Plan to see your personalized recommendation.")
    
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
    
    # Get user name for personalization
    person_name = st.session_state.get("person_name", "")
    
    # Hero Title with Subtitle
    st.markdown(f'<h1 class="learn-title">🧭 Understanding Your Care Recommendation</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="learn-subtitle">Let\'s explore what <strong>{tier_display}</strong> means for you.</p>', unsafe_allow_html=True)
    
    # Navi intro box
    st.markdown(f"""
    <div class="navi-box">
        <p><b>Hi{f", {person_name}" if person_name else ""}! I'm Navi.</b> Based on your Guided Care Plan assessment, we've identified <strong>{tier_display}</strong> as your recommended care level.</p>
        <p>Before we explore costs, let's understand what this means and how it can support your needs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Intro paragraph
    st.markdown("""
    <div style="text-align: center;">
        <h3 class="learn-intro" style="text-align: center;">
            This video explains everything you need to know about your recommended care option.<br>
            Take your time and ask questions as you learn.
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Embedded YouTube video - Currently using Assisted Living example
    # TODO: Add tier-specific video mapping when more videos are available
    video_id = _get_video_for_tier(care_rec.tier)
    
    st.markdown(f"""
    <div class="video-container">
        <iframe class="video-frame"
            src="https://www.youtube.com/embed/{video_id}"
            title="Understanding {tier_display}"
            frameborder="0"
            allowfullscreen>
        </iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Ask Navi section
    st.markdown('<h3 class="ask-navi-title">💬 Questions About Your Recommendation?</h3>', unsafe_allow_html=True)
    
    navi_query = st.text_input(
        "Ask me anything...",
        key="navi_learn_query",
        label_visibility="collapsed",
        placeholder="What does this care level include? How much does it cost?"
    )
    
    if navi_query:
        # Simple contextual responses based on care tier
        response = _get_navi_response(navi_query, care_rec.tier, tier_display)
        st.info(f"**Navi:** {response}")
    
    # Quick question buttons
    st.markdown('<div class="ask-navi-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"What does {tier_display} include?", use_container_width=True, key="faq_1"):
            st.info(f"**Navi:** {_get_tier_description(care_rec.tier, tier_display)}")
    with col2:
        if st.button("How much does this typically cost?", use_container_width=True, key="faq_2"):
            st.info("**Navi:** Great question! That's exactly what we'll explore in the Cost Planner next. You'll see detailed estimates including monthly costs, payment options, and potential financial assistance.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    
    # Mark as viewed
    if "learn_recommendation_viewed" not in st.session_state:
        st.session_state["learn_recommendation_viewed"] = True
    
    # Closing CTA Section
    st.markdown('<p class="footer-cta-text">Ready to explore costs and next steps?</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="footer-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("← Return to Lobby", use_container_width=True, key="return_lobby"):
            route_to("hub_lobby")
    
    with col2:
        if st.button("✅ Continue to Cost Planner", type="primary", use_container_width=True, key="continue_cost"):
            # Mark as complete
            _mark_complete()
            # Advance to planning phase
            advance_to("planning")
            # Navigate to Cost Planner
            route_to("cost_intro")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render footer
    render_footer_simple()


def _mark_complete():
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
    """Render additional educational resources - Phase 5A Enhanced."""
    
    st.markdown("""
    **🌐 Trusted Educational Resources:**
    - 📖 [A Place for Mom - Care Options Guide](https://www.aplaceformom.com/senior-care-resources)
    - 🏥 [Medicare - Long-Term Care Information](https://www.medicare.gov/what-medicare-covers/what-part-a-covers/long-term-care)
    - 💼 [Eldercare Locator - Find Local Resources](https://eldercare.acl.gov/)
    - 🧠 [Alzheimer's Association - Care Options](https://www.alz.org/help-support/caregiving)
    - 🏡 [AARP Caregiving Resource Center](https://www.aarp.org/caregiving/)
    
    **📞 Questions? I'm Here to Help:**
    
    After you complete the Cost Planner, you can schedule a personalized consultation with 
    your Care Advisor to discuss:
    - Specific facility or provider recommendations in your area
    - Detailed cost breakdowns and payment options
    - How to tour facilities or interview in-home care agencies
    - Family discussion strategies and decision-making support
    
    **🎯 Your Next Steps:**
    1. ✅ Review the cost estimates in the Cost Planner
    2. 💬 Discuss options with family members and loved ones
    3. 📅 Schedule a call with your Care Advisor to ask detailed questions
    4. 🏢 Tour facilities or interview in-home care providers
    5. 📋 Create a decision timeline that feels right for you
    
    ---
    
    💙 **Remember:** There's no "perfect" answer—only the right choice for your unique situation. 
    Take the time you need, ask questions, and trust your instincts. I'll be here to guide you 
    every step of the way.
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


def _inject_learn_recommendation_styles():
    """Inject Discovery Journey-style CSS for Learn About My Recommendation page."""
    st.markdown("""
    <style>
    /* === Global Styles === */
    body, .main {
        font-family: "Inter", "Segoe UI", Roboto, sans-serif;
        color: #1A1C2B;
    }

    /* === Title Section === */
    .learn-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #0E1E54;
        text-align: center;
        margin: 0 auto 1.25rem;
        line-height: 1.15;
    }
    .learn-subtitle {
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
    .learn-intro {
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
        .learn-title {
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


def _get_video_for_tier(tier: str) -> str:
    """Get the appropriate video ID for the care tier.
    
    Currently only Assisted Living video is available.
    TODO: Add videos for other tiers as they become available.
    """
    # Video mapping - will expand as more videos are created
    video_map = {
        "assisted_living": "EJ-GtXlY8Hw",  # Assisted Living video
        # Add more mappings as videos become available:
        # "memory_care": "VIDEO_ID",
        # "in_home": "VIDEO_ID",
        # etc.
    }
    
    # Default to assisted living video for now
    return video_map.get(tier, "EJ-GtXlY8Hw")


def _get_tier_description(tier: str, tier_display: str) -> str:
    """Get description of what the care tier includes."""
    
    descriptions = {
        "in_home": "In-Home Care allows you to stay in your own home with professional caregivers helping with daily activities like bathing, dressing, meals, and medication. Care schedules are flexible and can be adjusted as needs change.",
        
        "assisted_living": "Assisted Living communities provide private apartments with 24/7 staff support, three meals daily, social activities, medication management, housekeeping, and help with daily activities. It's a great balance of independence and support.",
        
        "memory_care": "Memory Care communities offer specialized support for those with Alzheimer's or dementia. Features include secure environments, trained staff, structured routines, cognitive therapies, and lower staff-to-resident ratios for personalized attention.",
        
        "memory_care_high_acuity": "Enhanced Memory Care provides the highest level of dementia support with specialized nursing, advanced safety features, intensive behavioral management, and round-the-clock specialized care.",
        
        "independent": "Independent Living communities offer maintenance-free apartments or cottages with amenities like dining, fitness centers, social activities, and transportation. Perfect for active seniors who want convenience and community without daily care needs."
    }
    
    return descriptions.get(tier, f"{tier_display} provides the appropriate level of support based on your assessment, ensuring safety, comfort, and quality of life.")


def _get_navi_response(query: str, tier: str, tier_display: str) -> str:
    """Generate contextual response based on user query and their care tier."""
    
    query_lower = query.lower()
    
    # Keyword-based responses
    if "cost" in query_lower or "price" in query_lower or "expensive" in query_lower:
        return "That's exactly what we'll explore next in the Cost Planner! You'll see detailed monthly costs, payment options, and potential financial assistance programs. Every situation is unique, so the Cost Planner will give you personalized estimates."
    
    elif "include" in query_lower or "what is" in query_lower or "services" in query_lower:
        return _get_tier_description(tier, tier_display)
    
    elif "how long" in query_lower or "timeline" in query_lower:
        return "There's no rush on this decision. Most families take 2-4 weeks to tour options, compare costs, and make their choice. Some need to move quickly due to safety concerns, while others plan months in advance. We'll help you move at the pace that's right for you."
    
    elif "family" in query_lower or "discuss" in query_lower:
        return "Involving family is so important! After reviewing the Cost Planner, you can schedule a consultation with your Care Advisor who can join family discussions and answer everyone's questions. We also have resources to help guide these conversations."
    
    elif "tour" in query_lower or "visit" in query_lower:
        return "Great idea! After you complete the Cost Planner, your Care Advisor can help you schedule tours at communities in your area. They'll share insider tips on what to look for and questions to ask during your visits."
    
    elif "different" in query_lower or "other option" in query_lower or "change" in query_lower:
        return f"Your recommendation of {tier_display} is based on your assessment, but it's not set in stone. If you'd like to explore other care levels, your Care Advisor can discuss alternatives during your consultation. Many communities also offer 'continuum of care' that adjusts as needs change."
    
    else:
        return "Great question! I'm here to help you understand your care recommendation. The video above covers the key points, and you'll get detailed cost information in the next step. For specific questions about communities in your area or family situations, your Care Advisor consultation (available after the Cost Planner) is the best resource."
