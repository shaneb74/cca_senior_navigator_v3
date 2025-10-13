"""
FAQ Page - AI Advisor "Navi"

Conversational AI advisor interface with dynamic question suggestions.
Questions rotate based on user context (care flags, cost planner flags).
Maintains archive of previously asked questions.
"""

import streamlit as st
import random


# Question database with flags and triggers
QUESTION_DATABASE = [
    {
        "flag": "home_care_cost",
        "triggers": ["home care cost", "home care price", "cost of home care", "in-home care cost", "how much"],
        "question": "How much does home care cost?",
        "follow_ups": ["How can I afford care for my loved one?", "Does Medicaid cover long-term care?"],
        "response": "Non-medical in-home care typically costs **$28–$40/hour**, depending on your area. For 20 hours a week, that's about **$2,400–$3,200/month**. Since prices vary by location, use the **Cost Planner** in the Concierge Hub with your ZIP code to get a personalized estimate and explore funding options."
    },
    {
        "flag": "va",
        "triggers": ["va", "veteran", "aid and attendance", "veterans benefits"],
        "question": "Can VA benefits help with care costs?",
        "follow_ups": ["What are my next steps after planning?", "How can I afford care for my loved one?"],
        "response": "We're here to support veterans and their families. You may qualify for **VA Aid & Attendance** or Community Care programs to help cover care costs. Eligibility often includes:\n- Being a veteran or surviving spouse\n- Needing help with daily activities\n- Meeting income and asset limits\nCheck your eligibility with the **VA Benefits module** in the Cost Planner to see how much support you can get."
    },
    {
        "flag": "medicaid",
        "triggers": ["medicaid", "medical aid"],
        "question": "Does Medicaid cover long-term care?",
        "follow_ups": ["How can I afford care for my loved one?", "What are my next steps after planning?"],
        "response": "Medicaid can help with long-term care costs, but eligibility varies by state. Typically, you'll need:\n- Income below ~$2,800/month (varies by state)\n- Assets below ~$2,000 (individual, excludes home in some cases)\n- A medical need for care\nThe **Medicaid module** in the Cost Planner will guide you through eligibility and strategies to protect your assets."
    },
    {
        "flag": "medicare",
        "triggers": ["medicare", "medi care"],
        "question": "What does Medicare cover for care?",
        "follow_ups": ["How can I afford care for my loved one?", "Does Medicaid cover long-term care?"],
        "response": "Let's clarify Medicare's role in care. **Medicare does not cover long-term custodial care** (like help with daily tasks), but it may cover:\n- Short-term skilled nursing (up to 100 days post-hospitalization)\n- Limited home health services for medical needs\n- Hospice care for end-of-life support\nFor ongoing care, explore Medicaid, VA benefits, or private pay. The **Cost Planner** can help you find funding options."
    },
    {
        "flag": "next",
        "triggers": ["next", "what now", "what should i do", "how to proceed", "what's next"],
        "question": "What are my next steps after planning?",
        "follow_ups": ["How can I afford care for my loved one?", "Where do I start with care planning?"],
        "response": "You're on the right track! Here's how to move forward:\n1. **Assess Needs**: Use the **Guided Care Plan** to understand care requirements.\n2. **Estimate Costs**: Run the **Cost Planner** to see expenses and funding options.\n3. **Get Expert Help**: Schedule a **Plan for My Advisor** consultation in the Concierge Hub.\n4. **Take Action**: Implement your plan with professional support.\nStart or continue in the Concierge Hub — we're here to help every step of the way!"
    },
    {
        "flag": "assisted_living",
        "triggers": ["assisted living", "assisted care"],
        "question": "What is assisted living and its cost?",
        "follow_ups": ["How can I afford care for my loved one?", "What is memory care for dementia?"],
        "response": "Assisted living offers 24/7 support in a community setting for those needing help with daily activities. Average costs are:\n- **National average**: $5,500/month\n- **Range**: $3,500–$8,000/month, depending on location and services\nThis includes:\n- Private or shared apartment\n- Meals and housekeeping\n- Personal care and social programs\nEnter your ZIP code in the **Cost Planner** to get local estimates."
    },
    {
        "flag": "memory_care",
        "triggers": ["memory care", "dementia", "alzheimer", "alzheimers"],
        "question": "What is memory care for dementia?",
        "follow_ups": ["How can I afford care for my loved one?", "What is assisted living and its cost?"],
        "response": "Memory care provides specialized support for those with Alzheimer's or dementia in a safe, structured environment. Costs are typically:\n- **Average**: $7,200/month\n- **High-acuity care**: $9,000+/month\nServices include:\n- Secured facilities\n- Specialized staff and cognitive therapies\n- 24/7 supervision\nUse the **Guided Care Plan** to assess needs, then check local pricing with the **Cost Planner**."
    },
    {
        "flag": "afford",
        "triggers": ["afford", "pay for", "budget", "how to pay", "can i afford"],
        "question": "How can I afford care for my loved one?",
        "follow_ups": ["Can VA benefits help with care costs?", "Does Medicaid cover long-term care?"],
        "response": "We understand care costs can feel overwhelming, but there are ways to make it work:\n- **VA Benefits**: Aid & Attendance for eligible veterans\n- **Medicaid**: Covers long-term care if you qualify\n- **Long-term care insurance**: Check your policy for coverage\n- **Home equity**: Options like reverse mortgages or home sale\n- **Family support**: Combine family care with paid help\nThe **Cost Planner's financial modules** will help you identify eligible funding sources and create a budget."
    },
    {
        "flag": "care_plan",
        "triggers": ["care plan", "where do i start", "how to start", "care planning"],
        "question": "Where do I start with care planning?",
        "follow_ups": ["What are my next steps after planning?", "How can I afford care for my loved one?"],
        "response": "Let's get started with a clear plan. The **Guided Care Plan** is a 10-15 minute assessment that:\n- Evaluates current care needs\n- Identifies safety concerns\n- Recommends personalized care options\nNext, use the **Cost Planner** to estimate costs and explore funding. Then, connect with an expert via **Plan for My Advisor** in the Concierge Hub."
    },
    {
        "flag": "skilled_nursing",
        "triggers": ["skilled nursing", "nursing home", "nursing facility"],
        "question": "What is skilled nursing care?",
        "follow_ups": ["How can I afford care for my loved one?", "Does Medicaid cover long-term care?"],
        "response": "Skilled nursing facilities provide 24/7 medical care for those with complex health needs. Costs typically range from:\n- **National average**: $8,000–$12,000/month\n- **Private room**: $9,000+/month\nServices include:\n- Medical care and monitoring\n- Rehabilitation services\n- Personal care and meals\nUse the **Cost Planner** to get local pricing and explore funding options like Medicaid or long-term care insurance."
    },
    {
        "flag": "home_modification",
        "triggers": ["home modification", "home safety", "aging in place", "grab bars", "ramps"],
        "question": "How can I make my home safer?",
        "follow_ups": ["How can I afford care for my loved one?", "Can VA benefits help with care costs?"],
        "response": "Making your home safer can help you or your loved one stay independent. Common modifications include grab bars, ramps, and stairlifts. Costs vary:\n- **Minor modifications**: $500–$2,000\n- **Major renovations**: $5,000–$15,000+\nSome funding options:\n- VA benefits (e.g., HISA grants for veterans)\n- Medicaid waivers (in some states)\n- Home equity or personal savings\nThe **Cost Planner** can help you estimate costs and identify funding for home modifications."
    },
    {
        "flag": "caregiver_support",
        "triggers": ["caregiver support", "respite care", "family caregiver", "caregiver help"],
        "question": "What support is available for caregivers?",
        "follow_ups": ["How can I afford care for my loved one?", "What are my next steps after planning?"],
        "response": "Caring for a loved one is rewarding but challenging. Respite care and support services can give you a break. Options include:\n- **In-home respite**: $28–$40/hour\n- **Adult day programs**: $50–$150/day\n- **Support groups**: Often free or low-cost\nFunding may be available through VA benefits or Medicaid. Explore your options with the **Cost Planner** and connect with a **Plan for My Advisor** expert for guidance."
    },
    {
        "flag": "hospice",
        "triggers": ["hospice", "palliative care", "end of life care"],
        "question": "What is hospice or palliative care?",
        "follow_ups": ["How can I afford care for my loved one?", "Does Medicare cover home care?"],
        "response": "Hospice and palliative care focus on comfort and quality of life for those with serious illnesses. Costs vary:\n- **Hospice**: Often covered by Medicare or Medicaid\n- **Palliative care**: $500–$2,000/month for non-Medicare-covered services\nServices include:\n- Pain management\n- Emotional and spiritual support\n- Family caregiver support\nUse the **Cost Planner** to explore coverage and start with the **Guided Care Plan** to assess needs."
    },
    {
        "flag": "ltc_insurance",
        "triggers": ["long term care insurance", "ltc insurance", "insurance for care"],
        "question": "How does long-term care insurance work?",
        "follow_ups": ["How can I afford care for my loved one?", "Does Medicaid cover long-term care?"],
        "response": "Long-term care insurance can help cover costs for home care, assisted living, or nursing homes. Coverage depends on your policy:\n- **Daily benefit**: Typically $100–$300/day\n- **Waiting period**: Often 90 days before benefits start\n- **Covered services**: Check for home care, assisted living, or memory care\nReview your policy details and use the **Cost Planner** to see how insurance fits into your budget."
    },
]


def render():
    """Render AI Advisor FAQ page."""
    
    st.markdown("## AI Advisor")
    st.subheader("I'm Navi — your expert advisor.")
    st.write("I help you see the whole map: care paths, hidden costs, decisions no one talks about. For your loved one.")
    
    # Initialize session state
    if "ai_thread" not in st.session_state:
        st.session_state["ai_thread"] = []
    if "ai_asked_questions" not in st.session_state:
        st.session_state["ai_asked_questions"] = []
    if "ai_suggested_pool" not in st.session_state:
        st.session_state["ai_suggested_pool"] = _get_suggested_questions_pool()
    
    st.markdown("#### Suggested Questions")
    
    # Get 3 dynamic questions based on user context
    suggested = _get_top_3_suggestions()
    
    # Display 3 question buttons
    cols = st.columns(3)
    for i, question in enumerate(suggested):
        if cols[i].button(question, use_container_width=True, key=f"faq_suggested_{i}"):
            _ask_question(question)
            st.rerun()
    
    st.markdown("#### Ask Me Anything")
    
    # Chat input
    prompt = st.text_input(
        "Your question…", 
        key="ai_input", 
        placeholder="e.g., How can I afford home care?",
        value=""
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Send", type="primary", key="ai_send", use_container_width=True):
            if prompt.strip():
                _ask_question(prompt.strip())
                st.rerun()
    with col2:
        if st.button("Clear chat", key="ai_clear", use_container_width=True):
            st.session_state["ai_thread"] = []
            st.session_state["ai_asked_questions"] = []
            st.rerun()
    
    st.divider()
    
    # Display conversation thread
    st.markdown("#### Questions I've Asked")
    
    thread = st.session_state.get("ai_thread", [])
    
    if not thread:
        st.caption("💡 Click a suggested question above or type your own to start chatting with Navi.")
    else:
        for role, msg in thread:
            if role == "user":
                st.markdown(f"**You:** {msg}")
            else:
                st.markdown(f"**Navi:** {msg}")
                st.markdown("")  # Spacing
    
    st.divider()
    
    # Back to hub
    if st.button("← Back to Hub", key="back_to_hub", use_container_width=True):
        st.query_params.clear()
        st.query_params["page"] = "concierge"
        st.rerun()


def _ask_question(question: str):
    """Process a question - add to thread, mark as asked, get response."""
    # Add to thread
    st.session_state["ai_thread"].append(("user", question))
    st.session_state["ai_thread"].append(("assistant", _get_navi_response(question)))
    
    # Add to asked questions (for filtering suggestions)
    st.session_state["ai_asked_questions"].append(question)


def _get_suggested_questions_pool() -> list:
    """Generate pool of suggested questions based on user context and flags."""
    
    # Get user context from session state
    handoff = st.session_state.get("handoff", {})
    gcp_state = handoff.get("gcp", {})
    cost_planner_state = st.session_state.get("cost_planner_base", {})
    cost_data = st.session_state.get("cost_data", {})
    
    # Get GCP flags from handoff
    gcp_flags = gcp_state.get("flags", {})
    care_recommendation = gcp_state.get("recommendation", "")
    # care_recommendation is now a string (e.g., "In-Home Care", "Assisted Living")
    care_type = care_recommendation.lower().replace(" ", "_") if care_recommendation else ""
    
    # Get Cost Planner profile flags
    profile = cost_planner_state.get("profile", {})
    is_veteran = profile.get("is_veteran", False)
    is_home_owner = profile.get("is_home_owner", False)
    has_medicaid = profile.get("has_medicaid", False)
    
    # Build active flags set
    active_flags = set()
    
    # Always include these general flags
    active_flags.add("next")
    active_flags.add("care_plan")
    active_flags.add("afford")
    
    # Care type flags from GCP
    if "in-home" in care_type.lower() or "in_home" in care_type.lower():
        active_flags.add("home_care_cost")
        active_flags.add("home_modification")
    if "assisted living" in care_type.lower():
        active_flags.add("assisted_living")
    if "memory care" in care_type.lower() or gcp_flags.get("cognitive_decline"):
        active_flags.add("memory_care")
    if "skilled nursing" in care_type.lower():
        active_flags.add("skilled_nursing")
    
    # Veteran flags
    if is_veteran or gcp_flags.get("is_veteran"):
        active_flags.add("va")
    
    # Medicaid flags
    if has_medicaid or gcp_flags.get("medicaid_likely"):
        active_flags.add("medicaid")
    
    # Medicare (always relevant for seniors)
    active_flags.add("medicare")
    
    # Home owner flags
    if is_home_owner:
        active_flags.add("home_modification")
    
    # Caregiver support
    if gcp_flags.get("caregiver_strain") or gcp_flags.get("family_caregiver"):
        active_flags.add("caregiver_support")
    
    # Hospice/palliative care
    if gcp_flags.get("end_of_life") or gcp_flags.get("hospice_appropriate"):
        active_flags.add("hospice")
    
    # Long-term care insurance
    if cost_data.get("has_ltc_insurance"):
        active_flags.add("ltc_insurance")
    
    # Build question pool from database based on active flags
    questions = []
    for item in QUESTION_DATABASE:
        if item["flag"] in active_flags:
            questions.append(item["question"])
    
    # Always return at least 3 questions
    if len(questions) < 3:
        # Add all questions from database as fallback
        questions = [item["question"] for item in QUESTION_DATABASE]
    
    return questions


def _get_top_3_suggestions() -> list:
    """Get 3 questions to display, excluding already asked."""
    asked = st.session_state.get("ai_asked_questions", [])
    pool = st.session_state.get("ai_suggested_pool", [])
    
    # Filter out already asked questions
    available = [q for q in pool if q not in asked]
    
    # If we've exhausted the pool, reset asked questions (except most recent 5)
    if len(available) < 3:
        st.session_state["ai_asked_questions"] = asked[-5:] if len(asked) > 5 else []
        available = [q for q in pool if q not in st.session_state["ai_asked_questions"]]
    
    # Return 3 random questions from available
    return random.sample(available, min(3, len(available)))


def _get_navi_response(question: str) -> str:
    """Generate Navi's response to a question.
    
    Uses the question database to match questions by triggers.
    Falls back to legacy rule-based responses if no match found.
    
    TODO: Replace with actual GPT/LLM integration.
    """
    q = question.lower()
    
    # Try to match question from database using triggers
    for item in QUESTION_DATABASE:
        for trigger in item["triggers"]:
            if trigger.lower() in q:
                return item["response"]
    
    # Legacy fallback responses for questions not in database yet
    
    # Family conversations
    if "talk to" in q and "family" in q:
        return (
            "Having the care conversation with family can be difficult. Here's how:\n\n"
            "**Tips:**\n"
            "- Start early before a crisis\n"
            "- Focus on safety and quality of life, not \"giving up independence\"\n"
            "- Share specific concerns (falls, medications, isolation)\n"
            "- Present options, not ultimatums\n"
            "- Include the person receiving care in decisions\n"
            "- Come with data (care plan, costs, options)\n\n"
            "The Guided Care Plan and Cost Planner give you objective information to frame the conversation."
        )
    
    # Urgency/warning signs
    if "urgent" in q or "warning sign" in q or "need care now" in q:
        return (
            "**Urgent warning signs requiring immediate action:**\n"
            "🚨 Falls or near-falls becoming frequent\n"
            "🚨 Forgetting medications or taking incorrectly\n"
            "🚨 Weight loss, poor nutrition\n"
            "🚨 Unable to manage personal hygiene\n"
            "🚨 Wandering or getting lost\n"
            "� Burns from cooking/smoking\n"
            "🚨 Signs of self-neglect\n\n"
            "If you see these, don't wait. Contact your doctor and consider emergency respite care while you set up a longer-term plan."
        )
    
    # Assisted living vs memory care
    if ("assisted living" in q or "memory care" in q) and ("difference" in q or "vs" in q or "versus" in q):
        return (
            "**Assisted Living:**\n"
            "- For seniors who need help with daily activities\n"
            "- Average: $5,500/month\n"
            "- Standard staffing and supervision\n"
            "- Mix of independent and assisted residents\n\n"
            "**Memory Care:**\n"
            "- Specialized for dementia/Alzheimer's\n"
            "- Average: $7,200/month (higher for high acuity)\n"
            "- Secured environment (prevent wandering)\n"
            "- Staff trained in cognitive care\n"
            "- Specialized activities and therapies\n\n"
            "Memory care is appropriate when cognitive decline creates safety risks."
        )
    
    # Medicaid spend-down (legacy - kept for compatibility)
    if "medicaid" in q and "spend-down" in q:
        return (
            "Medicaid spend-down strategies help you qualify while protecting assets:\n\n"
            "**Permitted strategies:**\n"
            "- Pay off debts (mortgage, medical bills)\n"
            "- Home improvements\n"
            "- Prepay funeral expenses\n"
            "- Purchase exempt assets (car, personal items)\n"
            "- Caregiver agreements with family\n\n"
            "**Important:** Work with an elder law attorney. Some transfers can cause penalties. "
            "The Cost Planner connects you with qualified professionals."
        )
    
    if "medicaid" in q and ("asset" in q or "protect" in q):
        return (
            "Yes, there are legal ways to protect assets and qualify for Medicaid:\n\n"
            "**Options:**\n"
            "- **Spousal protections** — Healthy spouse can keep home, car, ~$150,000+ in assets\n"
            "- **Irrevocable trusts** — Must be set up 5 years before applying\n"
            "- **Caregiver child exemption** — Transfer home to child who provided care 2+ years\n"
            "- **Medicaid Annuities** — Convert countable assets to income stream\n\n"
            "**Critical:** These require expert guidance. Improper transfers can cause penalties. "
            "Plan for My Advisor can connect you with elder law specialists."
        )
    
    # Home equity (legacy - kept for compatibility)
    if "home equity" in q or "reverse mortgage" in q:
        return (
            "Home equity can fund care, but consider carefully:\n\n"
            "**Options:**\n"
            "- **Sell the home** — Full proceeds available immediately\n"
            "- **Reverse mortgage** — Monthly payments or line of credit, keep ownership\n"
            "- **Home equity loan** — Requires monthly payments (may not fit fixed income)\n\n"
            "**Considerations:**\n"
            "- Will your loved one return home?\n"
            "- Is there a healthy spouse still living there?\n"
            "- Do you want to preserve it for heirs?\n"
            "- Medicaid impact (home may be exempt asset)\n\n"
            "An advisor can help you weigh these trade-offs."
        )
    
    # Default response
    return (
        "That's a thoughtful question. Here's what I'd consider:\n\n"
        "Care planning involves balancing safety, quality of life, and affordability. "
        "The best approach depends on your specific situation — care needs, budget, family support, and personal preferences.\n\n"
        "**I can help with:**\n"
        "- Care costs and funding options\n"
        "- VA and Medicaid benefits\n"
        "- When different care levels are appropriate\n"
        "- Next steps in your planning process\n\n"
        "Try asking something more specific, or click one of the suggested questions above!"
    )
