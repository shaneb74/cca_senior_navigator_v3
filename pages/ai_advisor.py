"""
AI Advisor Page - Navi Redesign 2.0

Clean, contextual FAQ interface showcasing Navi as the app's expert guide.
Features dynamic question suggestions, fake GPT flow with typing indicator,
and session-persistent conversation history.

DESIGN PRINCIPLES:
- Navi's signature blue without overwhelming the page
- Minimalist layout with comfortable read width (720-840px)
- Clean hierarchy and generous whitespace
- Smart question rotation based on context
- Action-oriented responses with module cross-links
"""

import streamlit as st
import time
import random
from typing import List, Dict, Set, Any, Optional

from core.nav import route_to


# ==============================================================================
# NAVI QUESTION DATABASE
# ==============================================================================
# Questions tagged by topic for contextual matching
# Responses are short, skimmable, action-oriented with cross-links
#
# FLAG ALIGNMENT:
# - All "registry_flags" use EXISTING flag names from core/flags.py FLAG_REGISTRY
# - Questions automatically appear when any of their registry_flags are True
# - DO NOT create new flags - only use flags that exist in the registry
# ==============================================================================

QUESTION_DATABASE = {
    # CARE PLANNING (no specific flags - always available)
    "start": {
        "question": "Where do I start with care planning?",
        "topic": "planning",
        "keywords": ["start", "begin", "planning", "where", "how"],
        "registry_flags": [],  # Always available
        "response": """**Let's build your care plan step by step.**

Start with the **Guided Care Plan** in the Concierge Hub (10-15 min):
• Assess current needs and safety concerns
• Get personalized care recommendations
• Understand next steps

Then use the **Cost Planner** to:
• Estimate monthly care costs
• Explore funding options (VA, Medicaid, insurance)
• See how long your resources will last

Finally, **book an advisor call** when you're ready for expert guidance.

💡 **Start in the Concierge Hub** — I'll guide you through each step."""
    },
    "medicare": {
        "question": "What does Medicare cover for long-term care?",
        "topic": "benefits",
        "keywords": ["medicare", "coverage", "cover"],
        "registry_flags": [],  # Always available
        "response": """**Important: Medicare does NOT cover long-term custodial care.**

Medicare only covers:
• Short-term skilled nursing (up to 100 days post-hospital)
• Limited home health for medical needs
• Hospice care

For ongoing help with daily tasks (bathing, dressing, meals), you'll need:
• Medicaid (if eligible)
• VA benefits (for veterans)
• Long-term care insurance
• Private pay

💡 **Check eligibility with the VA Benefits or Medicaid modules in Cost Planner.**"""
    },
    "next_steps": {
        "question": "What are my next steps after completing assessments?",
        "topic": "planning",
        "keywords": ["next", "after", "now what", "then"],
        "registry_flags": [],  # Always available
        "response": """**You're making progress! Here's your roadmap:**

✅ **Completed assessments** — You understand needs and costs
📋 **Next: Take action**
1. Review your care recommendation and cost estimates
2. Share results with family for aligned decisions
3. Research specific providers or facilities
4. Apply for benefits (VA, Medicaid) if eligible
5. Book an advisor call for personalized guidance

💡 **Use "Plan with My Advisor" in the Concierge Hub** to connect with an expert who can help implement your plan."""
    },
    
    # SAFETY & URGENCY (triggered by safety/fall flags)
    "fall_risk": {
        "question": "How can I reduce fall risk at home?",
        "topic": "safety",
        "keywords": ["fall", "falling", "safety", "home"],
        "registry_flags": ["falls_multiple", "falls_risk", "moderate_safety_concern", "high_safety_concern"],
        "response": """**Fall prevention is critical. Act now:**

**Immediate actions:**
• Remove tripping hazards (rugs, cords, clutter)
• Install grab bars in bathroom ($100-300)
• Improve lighting (hallways, stairs)
• Add night lights to bedroom-bathroom path

**Home modifications:**
• Non-slip mats in tub/shower
• Raised toilet seat
• Stair railings on both sides
• Medical alert device ($30-50/month)

**Cost:** $500-2,000 for basic modifications
**Funding:** VA HISA grants cover modifications for eligible veterans

💡 **Veterans: Check eligibility with the VA Benefits module in Cost Planner.**"""
    },
    "memory_care": {
        "question": "What's the difference between Memory Care and Assisted Living?",
        "topic": "care",
        "keywords": ["memory care", "assisted living", "difference", "dementia", "alzheimer"],
        "registry_flags": ["mild_cognitive_decline", "moderate_cognitive_decline", "severe_cognitive_risk", "memory_support"],
        "response": """**Key differences at a glance:**

**Assisted Living** (~$5,500/month)
• Help with daily activities
• Standard staffing and supervision
• Mix of independent residents

**Memory Care** (~$7,200/month)
• Specialized for dementia/Alzheimer's
• Secured environment (prevents wandering)
• Staff trained in cognitive care
• Specialized therapies and activities

**Choose Memory Care when:**
• Cognitive decline creates safety risks
• Person wanders or gets lost
• Needs 24/7 supervision
• Behavioral changes require specialized care

💡 **Get a care recommendation with the Guided Care Plan, then check local pricing with Cost Planner.**"""
    },
    "medication_management": {
        "question": "Who can help manage medications safely?",
        "topic": "care",
        "keywords": ["medication", "meds", "medication management", "pill management", "prescriptions"],
        "registry_flags": ["medication_management", "chronic_present", "chronic_conditions"],
        "response": """**Medication safety is critical.** Options for help:

**In-Home Care:**
• Caregivers can provide medication reminders
• Some agencies offer medication administration (requires licensed staff)
• Cost: $28–$40/hour

**Assisted Living/Memory Care:**
• Staff provides medication management
• Included in monthly cost (~$5,500–$7,200/month)

**Technology Solutions:**
• Pill dispensers with alarms ($50–$300)
• Smart pill boxes that notify family
• Pharmacy auto-refill services

**Important:** Complex medication regimens may require licensed nursing care. Discuss with your doctor.

💡 **Explore care options with the Guided Care Plan and estimate costs with Cost Planner.**"""
    },
    
    # VETERANS (triggered by ADL/dependence flags)
    "va_benefits": {
        "question": "Am I eligible for VA Aid & Attendance benefits?",
        "topic": "veterans",
        "keywords": ["va", "veteran", "aid attendance", "benefits"],
        "registry_flags": ["veteran_aanda_risk", "moderate_dependence", "high_dependence", "adl_support_high"],
        "response": """**VA may help cover care costs — here's how:**

**Eligibility often includes:**
• Wartime service (even 1 day during wartime period)
• Needing help with daily activities
• Meeting income/asset limits

**Benefit amounts (2024):**
• Veteran with spouse: up to $2,431/month
• Single veteran: up to $2,050/month
• Surviving spouse: up to $1,318/month

**What it covers:**
• In-home care
• Assisted living
• Memory care

**Processing time:** 3-6 months, so apply early

💡 **Check eligibility with the VA Benefits module in Cost Planner.**"""
    },
    
    # COSTS & FUNDING (no specific flags - always relevant)
    "home_care_cost": {
        "question": "How much does in-home care cost?",
        "topic": "costs",
        "keywords": ["home care", "cost", "price", "in-home"],
        "registry_flags": [],  # Always relevant for cost planning
        "response": """**In-home care typically costs $28-40/hour.**

**Common care packages:**
• Light support (10 hrs/week): $1,200-1,600/month
• Part-time (20 hrs/week): $2,400-3,200/month
• Full-time (40 hrs/week): $4,800-6,400/month

**Cost factors:**
• Geographic location (urban costs more)
• Specialized care (dementia care adds 15-20%)
• Agency vs. independent caregiver

**Funding options:**
• VA Aid & Attendance (up to $2,431/month)
• Medicaid home care waivers (state-dependent)
• Long-term care insurance
• Private pay

💡 **Get personalized estimates with the Cost Planner using your ZIP code.**"""
    },
    "afford_care": {
        "question": "How can I afford care for my loved one?",
        "topic": "costs",
        "keywords": ["afford", "pay", "budget", "funding", "expensive"],
        "registry_flags": [],  # Always relevant for cost planning
        "response": """**Care costs feel overwhelming, but there are solutions:**

**Explore these funding sources:**
• **VA Benefits** — Up to $2,431/month for eligible veterans
• **Medicaid** — Covers care if income/assets qualify
• **Home equity** — Reverse mortgage, home sale, or HELOC
• **Life insurance** — Some policies have living benefits
• **LTC insurance** — Check your policy coverage

**Strategies to reduce costs:**
• Start with fewer hours, increase as needed
• Combine family care with paid help
• Use adult day programs (cheaper than full-day care)

**Create a financial plan:**
1. Estimate monthly care cost
2. Identify all funding sources
3. Calculate your "runway" (how long funds last)
4. Apply for benefits early (processing takes months)

💡 **Use the Cost Planner's financial modules to build your funding strategy.**"""
    },
    "medicaid": {
        "question": "Does Medicaid cover long-term care?",
        "topic": "benefits",
        "keywords": ["medicaid", "medical aid", "coverage"],
        "registry_flags": [],  # Always relevant for benefits planning
        "response": """**Yes, Medicaid covers long-term care if you qualify.**

**Typical eligibility:**
• Income below ~$2,800/month (varies by state)
• Assets below ~$2,000 (individual, home often exempt)
• Medical need for care

**What Medicaid covers:**
• Nursing home care (all states)
• Assisted living (many states, via waivers)
• In-home care (varies by state)
• Memory care (varies by state)

**Spousal protections:**
• Healthy spouse can keep home
• Can keep ~$30,000-150,000 in assets
• Minimum monthly income allowance

**Important:** Rules vary by state. 5-year look-back period for asset transfers.

💡 **The Medicaid Navigation module in Cost Planner guides you through eligibility and planning strategies.**"""
    },
    
    # PLANNING & FAMILY (triggered by high dependence or caregiver flags)
    "family_conversation": {
        "question": "How do I talk to my family about care?",
        "topic": "planning",
        "keywords": ["talk", "family", "conversation", "discuss"],
        "registry_flags": ["no_support", "limited_support", "high_dependence", "moderate_dependence"],
        "response": """**The care conversation is challenging. Here's how to approach it:**

**Before the conversation:**
• Start early, before a crisis
• Gather objective data (assessment results, costs)
• Focus on safety and quality of life, not "giving up"

**During the conversation:**
1. **Express concern with love** — "I'm worried about your safety"
2. **Share specific observations** — "You've fallen twice this month"
3. **Present options, not ultimatums** — "Let's explore ways to keep you safe"
4. **Include the person** — Honor their preferences and dignity
5. **Focus on independence** — "This helps you stay in control"

**Common resistance:**
• "I'm fine" → Acknowledge feelings, share specific concerns
• "Too expensive" → Show funding options
• "I don't want to be a burden" → Family wants to help

**Bring data:**
• Guided Care Plan results
• Cost Planner estimates
• Doctor's recommendations

💡 **Use the Guided Care Plan and Cost Planner to frame conversations with objective information.**"""
    }
}

# Topic-based question groupings for chip rotation
TOPIC_POOLS = {
    "default": ["start", "medicare", "next_steps"],
    "planning": ["start", "next_steps", "family_conversation"],
    "safety": ["fall_risk", "memory_care"],
    "veterans": ["va_benefits", "fall_risk"],
    "costs": ["home_care_cost", "afford_care", "medicaid"],
    "benefits": ["medicare", "va_benefits", "medicaid"],
}

# Fallback response for unmatched questions
FALLBACK_RESPONSE = """**That's a thoughtful question.**

I'm still learning, but here's what I can help with:
• Care planning and next steps
• Costs and funding options (VA, Medicaid, insurance)
• When different care levels are appropriate
• Safety and home modifications

**Try asking about:**
• Medicare or Medicaid coverage
• VA benefits for veterans
• Home care costs in your area
• How to afford care
• Memory care vs. assisted living

💡 **Or click one of the suggested questions above for detailed guidance.**"""


# ==============================================================================
# QUESTION MATCHING & SUGGESTION ENGINE
# ==============================================================================

def _match_question(user_input: str) -> Optional[Dict[str, Any]]:
    """Match user input to a question in the database.
    
    Args:
        user_input: User's question text
        
    Returns:
        Question dict if match found, None otherwise
    """
    user_lower = user_input.lower().strip()
    
    # Try exact match first
    for q_data in QUESTION_DATABASE.values():
        if q_data["question"].lower() == user_lower:
            return q_data
    
    # Try keyword matching
    for q_data in QUESTION_DATABASE.values():
        for keyword in q_data["keywords"]:
            if keyword in user_lower:
                return q_data
    
    return None


def _get_suggested_questions(exclude: List[str] = None) -> List[str]:
    """Get 3-6 suggested question chips based on context and active flags.
    
    Dynamically filters questions based on flags set by Guided Care Plan and Cost Planner.
    Questions with empty registry_flags are always available (base questions).
    Questions with registry_flags only appear when at least one flag is active.
    
    Args:
        exclude: List of question keys to exclude (recently asked)
        
    Returns:
        List of question texts to display as chips
    """
    from core import flags
    
    exclude = exclude or []
    
    # Get active flags from user's journey
    active_flags_dict = flags.get_all_flags()
    active_flag_keys = set(active_flags_dict.keys())
    
    # Separate questions into categories
    always_available = []  # Empty registry_flags (base questions)
    flag_matched = []      # Has registry_flags that match active flags
    flag_unmatched = []    # Has registry_flags but none match
    
    for key, q_data in QUESTION_DATABASE.items():
        if key in exclude:
            continue
            
        registry_flags = q_data.get("registry_flags", [])
        
        if not registry_flags:
            # Always show questions with empty registry_flags
            always_available.append(key)
        else:
            # Check if any registry flag matches active flags
            matching_flags = set(registry_flags) & active_flag_keys
            if matching_flags:
                # Prioritize by number of matching flags
                flag_matched.append((key, len(matching_flags)))
            else:
                flag_unmatched.append(key)
    
    # Sort flag-matched questions by number of matches (descending)
    flag_matched.sort(key=lambda x: x[1], reverse=True)
    flag_matched_keys = [key for key, _ in flag_matched]
    
    # Build priority pool: flag-matched > always-available > unmatched
    priority_pool = flag_matched_keys + always_available
    
    # If we have enough from priority pool, use those
    if len(priority_pool) >= 3:
        available = priority_pool
    else:
        # Not enough questions, include some unmatched
        available = priority_pool + flag_unmatched
    
    # If we've asked too many questions, reset with just the last 3
    if len(available) < 3:
        recent_asked = st.session_state.get("ai_asked_keys", [])
        exclude = recent_asked[-3:] if len(recent_asked) > 3 else []
        # Re-run the filtering without exclusions
        available = [key for key in QUESTION_DATABASE.keys() if key not in exclude]
    
    # Shuffle available questions (but flag-matched stay near top)
    if len(flag_matched_keys) > 0 and len(available) > len(flag_matched_keys):
        # Keep flag-matched at top, shuffle the rest
        top_tier = flag_matched_keys[:3]  # Top 3 flag matches always shown
        rest = [k for k in available if k not in top_tier]
        random.shuffle(rest)
        available = top_tier + rest
    else:
        random.shuffle(available)
    
    # Take 3-6 questions
    num_suggestions = min(6, len(available))
    selected_keys = available[:num_suggestions]
    
    # Return question texts
    return [QUESTION_DATABASE[key]["question"] for key in selected_keys]


def _find_question_key(question_text: str) -> Optional[str]:
    """Find the database key for a question text.
    
    Args:
        question_text: Display text of the question
        
    Returns:
        Database key if found, None otherwise
    """
    for key, q_data in QUESTION_DATABASE.items():
        if q_data["question"] == question_text:
            return key
    return None


def _get_navi_response(user_input: str) -> str:
    """Generate Navi's response to user input.
    
    Args:
        user_input: User's question text
        
    Returns:
        Response text
    """
    # Try to match question
    matched = _match_question(user_input)
    
    if matched:
        return matched["response"]
    else:
        return FALLBACK_RESPONSE


# ==============================================================================
# UI COMPONENTS
# ==============================================================================

def _render_typing_indicator():
    """Show Navi thinking animation for 600-900ms."""
    with st.spinner("✨ Navi is thinking..."):
        time.sleep(random.uniform(0.6, 0.9))


def _render_message_bubble(role: str, content: str):
    """Render a message bubble.
    
    Args:
        role: 'user' or 'navi'
        content: Message text
    """
    if role == "user":
        st.markdown(
            f"""<div class="faq-message faq-message--user">
{content}
</div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""<div class="faq-message faq-message--navi">
<div class="faq-navi-icon">✨</div>
<div class="faq-navi-content">{content}</div>
</div>""",
            unsafe_allow_html=True
        )


# ==============================================================================
# MAIN RENDER FUNCTION
# ==============================================================================

def render():
    """Render the AI Advisor page with Navi redesign."""
    
    # Inject custom CSS for this page
    st.markdown("""
<style>
/* Page container - comfortable read width */
.faq-container {
    max-width: 840px;
    margin: 0 auto;
    padding: var(--space-6) var(--space-4);
}

/* Navi Banner Header - matches styling from other pages */
.navi-banner-advisor {
    background: #ffffff;
    border: 1px solid #e6edf5;
    border-left: 3px solid #4A90E2;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: var(--space-8);
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
}

.navi-banner-advisor__eyebrow {
    font-size: 11px;
    font-weight: 800;
    color: #4A90E2;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 12px;
}

.navi-banner-advisor__eyebrow .navi-icon {
    font-size: 14px;
}

.navi-banner-advisor__title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 8px 0;
    line-height: 1.3;
}

.navi-banner-advisor__description {
    font-size: 1rem;
    color: #475569;
    margin: 0;
    line-height: 1.5;
}

/* Section spacing */
.faq-section {
    margin-bottom: var(--space-8);
}

.faq-section-title {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: var(--space-4);
}

/* Suggested question chips */
.faq-chips {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
    margin-bottom: var(--space-6);
}

.faq-chip {
    display: inline-block;
    padding: var(--space-2) var(--space-4);
    background: white;
    border: 1.5px solid #E0E7FF;
    border-radius: 24px;
    font-size: 0.9375rem;
    color: var(--ink);
    cursor: pointer;
    transition: all 0.2s ease;
}

.faq-chip:hover {
    background: #F5F8FF;
    border-color: #4A90E2;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(74, 144, 226, 0.15);
}

.faq-chip:focus {
    outline: 2px solid #4A90E2;
    outline-offset: 2px;
}

/* Input section */
.faq-input-section {
    margin-bottom: var(--space-6);
}

/* Message bubbles */
.faq-message {
    margin-bottom: var(--space-5);
    animation: fadeInDown 0.3s ease;
}

.faq-message--user {
    text-align: left;
    padding: var(--space-3) var(--space-4);
    background: #F8F9FA;
    border-radius: 16px;
    border-left: 3px solid var(--ink-300);
    font-size: 1rem;
    color: var(--ink);
    max-width: 90%;
}

.faq-message--navi {
    display: flex;
    gap: var(--space-3);
    align-items: flex-start;
    padding: var(--space-4);
    background: #F5F8FF;
    border: 1px solid #E0E7FF;
    border-radius: 16px;
    max-width: 95%;
}

.faq-navi-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
}

.faq-navi-content {
    flex: 1;
    font-size: 1rem;
    line-height: 1.6;
    color: var(--ink);
}

.faq-navi-content strong {
    color: var(--ink);
    font-weight: 700;
}

.faq-navi-content ul,
.faq-navi-content ol {
    margin: var(--space-2) 0;
    padding-left: var(--space-5);
}

.faq-navi-content li {
    margin-bottom: var(--space-1);
}

/* Conversation section */
.faq-conversation {
    margin-top: var(--space-6);
    padding-top: var(--space-6);
    border-top: 1px solid var(--ink-100);
}

.faq-empty-state {
    text-align: center;
    padding: var(--space-8) var(--space-4);
    color: var(--ink-500);
    font-size: 0.9375rem;
}

/* Guardrail footer */
.faq-guardrail {
    text-align: center;
    font-size: 0.875rem;
    color: var(--ink-500);
    margin: var(--space-8) 0 var(--space-6);
    padding: var(--space-3);
    background: #F8F9FA;
    border-radius: 8px;
}

/* Animations */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .faq-container {
        padding: var(--space-4) var(--space-3);
    }
    
    .faq-chips {
        gap: var(--space-2);
    }
    
    .faq-chip {
        font-size: 0.875rem;
        padding: var(--space-2) var(--space-3);
    }
}

/* Accessibility - respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
    .faq-chip,
    .faq-message {
        animation: none !important;
        transition: none !important;
    }
    
    .faq-chip:hover {
        transform: none;
    }
}
</style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "ai_thread" not in st.session_state:
        st.session_state["ai_thread"] = []
    if "ai_asked_keys" not in st.session_state:
        st.session_state["ai_asked_keys"] = []
    if "ai_current_input" not in st.session_state:
        st.session_state["ai_current_input"] = ""
    
    # Container wrapper
    st.markdown('<div class="faq-container">', unsafe_allow_html=True)
    
    # Navi Banner Header (consistent with other pages)
    st.markdown("""
<div class="navi-banner-advisor">
    <div class="navi-banner-advisor__eyebrow">
        <span class="navi-icon">✨</span> NAVI — YOUR EXPERT ADVISOR
    </div>
    <h1 class="navi-banner-advisor__title">AI Advisor</h1>
    <p class="navi-banner-advisor__description">
        I'm Navi — your expert advisor. Ask about care options, costs, benefits, 
        and next steps. I'll point you to the right tools.
    </p>
</div>
    """, unsafe_allow_html=True)
    
    # Suggested Questions section
    st.markdown('<div class="faq-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="faq-section-title">Suggested Questions</h2>', unsafe_allow_html=True)
    
    # Get suggested questions (exclude recently asked)
    suggested = _get_suggested_questions(exclude=st.session_state["ai_asked_keys"])
    
    # Render chips
    cols = st.columns(min(len(suggested), 3))
    for i, question in enumerate(suggested):
        col_idx = i % len(cols)
        with cols[col_idx]:
            if st.button(
                question,
                key=f"faq_chip_{i}",
                use_container_width=True,
                help="Click to ask this question"
            ):
                # Ask question and refresh chips
                _ask_question(question)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Ask Me Anything section
    st.markdown('<div class="faq-section faq-input-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="faq-section-title">Ask Me Anything</h2>', unsafe_allow_html=True)
    
    # Text input with Enter to send
    user_input = st.text_input(
        "Your question",
        value=st.session_state.get("ai_current_input", ""),
        placeholder="e.g., How can I afford home care?",
        key="ai_text_input",
        label_visibility="collapsed"
    )
    
    # Buttons row
    col1, col2 = st.columns([3, 1])
    with col1:
        send_clicked = st.button(
            "Send",
            type="primary",
            use_container_width=True,
            key="ai_send_btn"
        )
    with col2:
        clear_clicked = st.button(
            "Clear chat",
            use_container_width=True,
            key="ai_clear_btn"
        )
    
    # Handle send action (button or Enter key via text input change)
    if send_clicked and user_input.strip():
        _ask_question(user_input.strip())
        st.session_state["ai_current_input"] = ""
        st.rerun()
    
    # Handle clear action
    if clear_clicked:
        st.session_state["ai_thread"] = []
        st.session_state["ai_asked_keys"] = []
        st.session_state["ai_current_input"] = ""
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Conversation section
    st.markdown('<div class="faq-conversation">', unsafe_allow_html=True)
    st.markdown('<h2 class="faq-section-title">Questions I\'ve Asked</h2>', unsafe_allow_html=True)
    
    thread = st.session_state.get("ai_thread", [])
    
    if not thread:
        st.markdown("""
<div class="faq-empty-state">
    💡 Click a suggested question above or type your own to start chatting with Navi.
</div>
        """, unsafe_allow_html=True)
    else:
        # Render messages in reverse chronological order (newest first)
        # This keeps new answers at the top, just below the section title
        for role, message in reversed(thread):
            if role == "user":
                _render_message_bubble("user", message)
            else:
                _render_message_bubble("navi", message)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Guardrail footer
    st.markdown("""
<div class="faq-guardrail">
    Navi offers information, not medical or legal advice.
</div>
    """, unsafe_allow_html=True)
    
    # Back to Hub button
    st.markdown('<div style="margin-top: var(--space-6);">', unsafe_allow_html=True)
    if st.button("← Back to Hub", use_container_width=True, key="faq_back_to_hub"):
        route_to("hub_concierge")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)


def _ask_question(question: str):
    """Process a question: show typing indicator, add to thread, track question key.
    
    Args:
        question: Question text from user
    """
    # Show typing indicator
    _render_typing_indicator()
    
    # Get Navi's response
    response = _get_navi_response(question)
    
    # Add to thread
    st.session_state["ai_thread"].append(("user", question))
    st.session_state["ai_thread"].append(("navi", response))
    
    # Track question key for chip rotation (if it's a suggested question)
    question_key = _find_question_key(question)
    if question_key and question_key not in st.session_state["ai_asked_keys"]:
        st.session_state["ai_asked_keys"].append(question_key)
