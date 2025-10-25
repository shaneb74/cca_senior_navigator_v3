"""
FAQ Page - AI Advisor "Navi"

Conversational AI advisor interface with dynamic question suggestions.
Questions rotate based on user context (care flags, cost planner flags).
Maintains archive of previously asked questions.

FLAG-DRIVEN PERSONALIZATION:
- Uses NaviOrchestrator.get_suggested_questions() for centralized flag logic
- Surfaces 3 most relevant questions at any time
- Auto-refreshes as user completes products and flags change

LLM-POWERED FAQ (Stage 3):
- Natural language query via TF-IDF retrieval
- Grounded answers using ai/llm_mediator with policy enforcement
- Max 120 words, no hallucinations, safe CTAs only
"""

from typing import Any
import json

import streamlit as st
import numpy as np

from core.flags import get_all_flags
from core.mcip import MCIP
from core.nav import route_to
from core.navi import NaviOrchestrator


# ==============================================================================
# QUESTION DATABASE LOADER
# ==============================================================================
@st.cache_data
def load_faq_items() -> list[dict[str, Any]]:
    """Load FAQ questions from config/faq.json.
    
    Returns:
        List of FAQ question dicts with schema:
        {
            "id": str,
            "question": str,
            "answer": str,
            "tags": list[str],
            "triggers": list[str],
            "flags": list[str],
            "priority": int,
            "category": str,
            "ctas": list[dict]
        }
    """
    with open("config/faq.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_faq_policy() -> dict[str, Any]:
    """Load FAQ policy guardrails from config/faq_policy.json.
    
    Returns:
        Policy dict with schema:
        {
            "allowed_products": list[str],
            "allowed_terms": list[str],
            "banned_phrases": list[str],
            "fallback_name": str,
            "default_cta": dict
        }
    """
    with open("config/faq_policy.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# RETRIEVAL LAYER (TF-IDF)
# ==============================================================================
@st.cache_data
def retrieve_faq(query: str, faqs: list[dict], k: int = 3) -> list[dict]:
    """Retrieve top-k most relevant FAQs using TF-IDF cosine similarity.
    
    Args:
        query: User's natural language question
        faqs: List of FAQ dicts from load_faq_items()
        k: Number of results to return (default 3)
        
    Returns:
        List of top-k FAQ dicts with similarity > 0, sorted by relevance
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Combine question + answer for richer matching
        texts = [f"{f['question']} {f['answer']}" for f in faqs]
        
        vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        X = vectorizer.fit_transform(texts)
        q_vec = vectorizer.transform([query])
        
        sims = cosine_similarity(q_vec, X).flatten()
        top_idx = np.argsort(sims)[::-1][:k]
        
        # Only return results with positive similarity
        return [faqs[i] for i in top_idx if sims[i] > 0]
    except Exception as e:
        print(f"[FAQ_RETRIEVAL_ERROR] {e}")
        return []


# ==============================================================================
# CORPORATE KNOWLEDGE LOADER + RETRIEVER (Stage 3.5)
# ==============================================================================
@st.cache_data
def load_corp_chunks() -> list[dict[str, Any]]:
    """Load corporate knowledge chunks from config/corp_knowledge.jsonl.
    
    Returns:
        List of chunk dicts with schema:
        {
            "doc_id": str,
            "url": str,
            "title": str,
            "heading": str,
            "text": str,
            "last_fetched": str,
            "tags": list[str]
        }
    """
    try:
        import os
        chunks_path = "config/corp_knowledge.jsonl"
        if not os.path.exists(chunks_path):
            print(f"[CORP_KNOWLEDGE_WARN] {chunks_path} not found - run 'make sync-site'")
            return []
        
        chunks = []
        with open(chunks_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    chunks.append(json.loads(line))
                except Exception:
                    pass
        return chunks
    except Exception as e:
        print(f"[CORP_CHUNKS_ERROR] {e}")
        return []


@st.cache_data
def retrieve_corp(query: str, chunks: list[dict], k: int = 5) -> list[dict]:
    """Retrieve top-k most relevant corp knowledge chunks using TF-IDF.
    
    Args:
        query: User's natural language question
        chunks: List of chunk dicts from load_corp_chunks()
        k: Number of results to return (default 5)
        
    Returns:
        List of top-k chunk dicts with similarity > 0, sorted by relevance
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        if not chunks:
            return []
        
        # Combine heading + text for richer matching
        texts = [f"{c['heading']} {c['text']}" for c in chunks]
        
        vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        X = vectorizer.fit_transform(texts)
        q_vec = vectorizer.transform([query])
        
        sims = cosine_similarity(q_vec, X).flatten()
        top_idx = np.argsort(sims)[::-1][:k]
        
        # Only return results with positive similarity
        return [chunks[i] for i in top_idx if sims[i] > 0]
    except Exception as e:
        print(f"[CORP_RETRIEVAL_ERROR] {e}")
        return []


# Load question database from JSON
QUESTION_DATABASE = load_faq_items()


# ==============================================================================
# LEGACY HARDCODED DATABASE (removed - now loaded from config/faq.json)
# ==============================================================================
# Preserved for reference only - all questions now externalized
_LEGACY_QUESTION_DATABASE = [
    # DEFAULT QUESTIONS - shown when no flags exist
    {
        "flags": [],  # Always available
        "priority": 3,
        "category": "planning",
        "question": "Where do I start with care planning?",
        "triggers": [
            "care plan",
            "where do i start",
            "how to start",
            "care planning",
            "getting started",
        ],
        "response": "Let's get started with a clear plan. The **Guided Care Plan** is a 10-15 minute assessment that:\n- Evaluates current care needs\n- Identifies safety concerns\n- Recommends personalized care options\n\nNext, use the **Cost Planner** to estimate costs and explore funding. Then, connect with an expert via **Plan for My Advisor** in the Concierge Hub.",
    },
    {
        "flags": [],
        "priority": 3,
        "category": "cost",
        "question": "What does Medicare cover for care?",
        "triggers": ["medicare", "medi care"],
        "response": "Let's clarify Medicare's role in care. **Medicare does not cover long-term custodial care** (like help with daily tasks), but it may cover:\n- Short-term skilled nursing (up to 100 days post-hospitalization)\n- Limited home health services for medical needs\n- Hospice care for end-of-life support\n\nFor ongoing care, explore Medicaid, VA benefits, or private pay. The **Cost Planner** can help you find funding options.",
    },
    {
        "flags": [],
        "priority": 3,
        "category": "planning",
        "question": "What are my next steps after planning?",
        "triggers": ["next", "what now", "what should i do", "how to proceed", "what's next"],
        "response": "You're on the right track! Here's how to move forward:\n1. **Assess Needs**: Use the **Guided Care Plan** to understand care requirements.\n2. **Estimate Costs**: Run the **Cost Planner** to see expenses and funding options.\n3. **Get Expert Help**: Schedule a **Plan for My Advisor** consultation in the Concierge Hub.\n4. **Take Action**: Implement your plan with professional support.\n\nStart or continue in the Concierge Hub — we're here to help every step of the way!",
    },
    # SAFETY & URGENCY FLAGS (Priority 1)
    {
        "flags": ["fall_risk", "mobility_concern"],
        "priority": 1,
        "category": "care",
        "question": "How can I reduce fall risk at home?",
        "triggers": ["fall risk", "falling", "fall prevention", "home safety", "grab bars"],
        "response": "**Fall prevention is critical.** Here's what to do now:\n\n**Immediate actions:**\n- Remove tripping hazards (rugs, cords, clutter)\n- Improve lighting in hallways and stairs\n- Install grab bars in bathroom\n- Consider medical alert device\n\n**Home modifications:**\n- Non-slip mats in bathroom\n- Raised toilet seat\n- Stair railings on both sides\n- Night lights in bedroom/bathroom path\n\n**Cost:** $500–$2,000 for basic modifications. VA benefits may cover some costs for veterans. Use the **Cost Planner's home modification module** to get estimates.",
    },
    {
        "flags": ["cog_moderate", "cog_severe", "cognitive_decline"],
        "priority": 1,
        "category": "care",
        "question": "What's the difference between Memory Care and Assisted Living?",
        "triggers": ["memory care", "assisted living", "difference", "dementia care", "alzheimer"],
        "response": "**Assisted Living:**\n- For seniors who need help with daily activities\n- Average: $5,500/month\n- Standard staffing and supervision\n- Mix of independent and assisted residents\n\n**Memory Care:**\n- Specialized for dementia/Alzheimer's\n- Average: $7,200/month (higher for high acuity)\n- Secured environment (prevent wandering)\n- Staff trained in cognitive care\n- Specialized activities and therapies\n\n**Memory care is appropriate when:**\n- Cognitive decline creates safety risks\n- Wandering or getting lost\n- Needs 24/7 supervision\n- Requires specialized engagement\n\nUse the **Guided Care Plan** to assess needs, then check local pricing with the **Cost Planner**.",
    },
    {
        "flags": ["medication_management", "med_complexity"],
        "priority": 1,
        "category": "care",
        "question": "Who can help manage medications safely?",
        "triggers": [
            "medication",
            "meds",
            "medication management",
            "pill management",
            "prescriptions",
        ],
        "response": "**Medication safety is critical.** Options for help:\n\n**In-Home Care:**\n- Caregivers can provide medication reminders\n- Some agencies offer medication administration (requires licensed staff)\n- Cost: $28–$40/hour\n\n**Assisted Living/Memory Care:**\n- Staff provides medication management\n- Included in monthly cost (~$5,500–$7,200/month)\n\n**Technology Solutions:**\n- Pill dispensers with alarms ($50–$300)\n- Smart pill boxes that notify family\n- Pharmacy auto-refill services\n\n**Important:** Complex medication regimens may require licensed nursing care. Discuss with your doctor.",
    },
    # VETERAN FLAGS (Priority 2)
    {
        "flags": ["veteran_eligible", "is_veteran"],
        "priority": 2,
        "category": "benefits",
        "question": "Am I eligible for VA Aid & Attendance benefits?",
        "triggers": ["va", "veteran", "aid and attendance", "veterans benefits", "va benefits"],
        "response": "We're here to support veterans and their families. You may qualify for **VA Aid & Attendance** or Community Care programs to help cover care costs.\n\n**Eligibility often includes:**\n- Being a veteran or surviving spouse\n- Wartime service (even 1 day during wartime period)\n- Needing help with daily activities (ADLs)\n- Meeting income and asset limits\n\n**Benefit amounts:**\n- Veteran with spouse: up to $2,431/month\n- Single veteran: up to $2,050/month\n- Surviving spouse: up to $1,318/month\n\n**What it covers:**\n- In-home care\n- Assisted living\n- Memory care\n\nCheck your eligibility with the **VA Benefits module** in the Cost Planner to see how much support you can get.",
    },
    {
        "flags": ["veteran_eligible", "is_veteran", "is_home_owner"],
        "priority": 2,
        "category": "benefits",
        "question": "Can VA help with home modifications for safety?",
        "triggers": ["va home", "home modification veteran", "hisa", "va home improvements"],
        "response": "Yes! The VA offers several programs to help veterans make homes safer:\n\n**HISA Grant (Home Improvements and Structural Alterations):**\n- Up to $6,800 for service-connected disabilities\n- Up to $2,000 for non-service-connected\n- Covers ramps, grab bars, widened doorways, roll-in showers\n\n**SAH/SHA Grants (for service-connected disabilities):**\n- SAH: up to $101,754 for specially adapted housing\n- SHA: up to $20,387 for home modifications\n\n**Application:** Work with your VA social worker or contact your regional VA office.\n\nUse the **Cost Planner's home modification module** to estimate costs and apply for VA grants.",
    },
    # HOME CARE & IN-HOME FLAGS (Priority 2)
    # HOME CARE & IN-HOME FLAGS (Priority 2)
    {
        "flags": ["in_home_care", "home_care_recommended"],
        "priority": 2,
        "category": "cost",
        "question": "How much does in-home care cost in my area?",
        "triggers": [
            "home care cost",
            "home care price",
            "cost of home care",
            "in-home care cost",
            "how much",
        ],
        "response": "Non-medical in-home care typically costs **$28–$40/hour**, depending on your area. For 20 hours a week, that's about **$2,400–$3,200/month**.\n\n**Factors affecting cost:**\n- Geographic location (urban vs. rural)\n- Hours per week needed\n- Specialized care (dementia care costs more)\n- Agency vs. independent caregiver\n\n**Typical care packages:**\n- Light support (10 hrs/week): $1,200–$1,600/month\n- Part-time (20 hrs/week): $2,400–$3,200/month\n- Full-time (40 hrs/week): $4,800–$6,400/month\n\nSince prices vary by location, use the **Cost Planner** with your ZIP code to get a personalized estimate and explore funding options.",
    },
    {
        "flags": ["is_home_owner", "aging_in_place"],
        "priority": 2,
        "category": "planning",
        "question": "How can I make my home safer for aging in place?",
        "triggers": [
            "aging in place",
            "home safety",
            "home modification",
            "stay at home",
            "modifications",
        ],
        "response": "Making your home safer can help you or your loved one stay independent. **Common modifications:**\n\n**Bathroom ($500–$2,000):**\n- Grab bars near toilet and shower\n- Non-slip mats\n- Raised toilet seat\n- Walk-in tub or roll-in shower ($3,000–$10,000)\n\n**Mobility ($1,000–$15,000):**\n- Wheelchair ramps\n- Stairlifts ($3,000–$5,000)\n- Widened doorways\n- Lever door handles\n\n**General Safety ($200–$1,000):**\n- Improved lighting\n- Remove trip hazards\n- Night lights\n- Medical alert system\n\n**Funding options:**\n- VA benefits (HISA grants for veterans)\n- Medicaid waivers (some states)\n- Home equity or personal savings\n\nThe **Cost Planner** can help you estimate costs and identify funding for home modifications.",
    },
    # COGNITIVE CARE FLAGS (Priority 2)
    {
        "flags": ["cog_moderate", "cog_severe", "dementia_care"],
        "priority": 2,
        "category": "care",
        "question": "What is memory care and how much does it cost?",
        "triggers": ["memory care", "dementia", "alzheimer", "alzheimers", "memory care cost"],
        "response": "Memory care provides specialized support for those with Alzheimer's or dementia in a safe, structured environment.\n\n**Average costs:**\n- Standard memory care: $7,200/month\n- High-acuity care: $9,000+/month\n- Geographic variation: $5,000–$12,000/month\n\n**Services include:**\n- Secured facilities (prevent wandering)\n- Specialized staff and cognitive therapies\n- 24/7 supervision\n- Structured daily activities\n- Medication management\n- Memory-focused programming\n\n**When is memory care needed?**\n- Moderate to severe cognitive decline\n- Safety concerns (wandering, leaving stove on)\n- Needs 24/7 supervision\n- Caregiver burnout\n\nUse the **Guided Care Plan** to assess needs, then check local pricing with the **Cost Planner**.",
    },
    {
        "flags": ["caregiver_strain", "family_caregiver"],
        "priority": 2,
        "category": "support",
        "question": "What support is available for family caregivers?",
        "triggers": [
            "caregiver support",
            "respite care",
            "family caregiver",
            "caregiver help",
            "caregiver burnout",
        ],
        "response": "Caring for a loved one is rewarding but challenging. **Respite care and support services** can give you a break:\n\n**In-Home Respite:**\n- Professional caregiver comes to your home\n- Cost: $28–$40/hour\n- Flexible scheduling (few hours to overnight)\n\n**Adult Day Programs:**\n- Social activities and supervision during the day\n- Cost: $50–$150/day\n- Usually 8am–5pm, meals included\n\n**Short-Term Facility Care:**\n- Assisted living or memory care for a few days/weeks\n- Cost: $200–$400/day\n\n**Support Groups:**\n- Often free or low-cost\n- Emotional support and practical tips\n- Many available online\n\n**Funding may be available through:**\n- VA benefits for veterans' families\n- Medicaid waivers (some states)\n- Long-term care insurance\n\nExplore your options with the **Cost Planner** and connect with a **Plan for My Advisor** expert for guidance.",
    },
    # MEDICAID FLAGS (Priority 2)
    {
        "flags": ["medicaid_likely", "has_medicaid", "financial_gap"],
        "priority": 2,
        "category": "benefits",
        "question": "Does Medicaid cover long-term care?",
        "triggers": ["medicaid", "medical aid", "medicaid coverage", "medicaid long term care"],
        "response": "Medicaid can help with long-term care costs, but eligibility varies by state.\n\n**Typical eligibility:**\n- Income below ~$2,800/month (varies by state)\n- Assets below ~$2,000 (individual, excludes home in some cases)\n- A medical need for care\n\n**What Medicaid covers:**\n- Nursing home care (all states)\n- Assisted living (many states, through waivers)\n- In-home care (varies by state)\n- Memory care (varies by state)\n\n**Spousal protections:**\n- Healthy spouse can keep home\n- Can keep ~$30,000–$150,000 in assets (varies by state)\n- Minimum monthly income allowance (~$2,500)\n\n**Important:** Rules vary significantly by state. Some states have 5-year look-back period for asset transfers.\n\nThe **Medicaid module** in the Cost Planner will guide you through eligibility and strategies to protect your assets.",
    },
    {
        "flags": ["medicaid_likely", "has_assets"],
        "priority": 2,
        "category": "benefits",
        "question": "How can I protect assets and still qualify for Medicaid?",
        "triggers": ["medicaid", "asset", "protect", "spend down", "medicaid planning"],
        "response": "Yes, there are legal ways to protect assets and qualify for Medicaid:\n\n**Strategies:**\n- **Spousal protections** — Healthy spouse can keep home, car, ~$150,000+ in assets\n- **Irrevocable trusts** — Must be set up 5 years before applying (look-back period)\n- **Caregiver child exemption** — Transfer home to child who provided care 2+ years\n- **Medicaid Annuities** — Convert countable assets to income stream\n- **Spend-down** — Pay off debts, home improvements, prepay funeral\n\n**Important considerations:**\n- 5-year look-back period for asset transfers\n- Penalties for improper transfers\n- State-specific rules vary significantly\n- Timing is critical\n\n**Critical:** These require expert guidance. Improper transfers can cause penalties and delay Medicaid eligibility.\n\nPlan for My Advisor can connect you with elder law specialists who understand your state's rules.",
    },
    # COST & AFFORDABILITY FLAGS (Priority 2)
    {
        "flags": ["financial_gap", "cost_concern"],
        "priority": 2,
        "category": "cost",
        "question": "How can I afford care for my loved one?",
        "triggers": ["afford", "pay for", "budget", "how to pay", "can i afford", "funding"],
        "response": 'We understand care costs can feel overwhelming, but there are ways to make it work:\n\n**Funding sources:**\n- **VA Benefits**: Aid & Attendance for eligible veterans (up to $2,431/month)\n- **Medicaid**: Covers long-term care if you qualify\n- **Long-term care insurance**: Check your policy for coverage\n- **Home equity**: Reverse mortgage, home equity loan, or home sale\n- **Life insurance**: Some policies have accelerated death benefits or can be sold\n- **Retirement accounts**: 401(k) or IRA withdrawals\n- **Family support**: Combine family care with paid help\n\n**Strategies to reduce costs:**\n- Start with fewer hours and increase as needed\n- Share caregivers with other families\n- Use adult day programs instead of full-day care\n- Combine family caregiving with professional help\n\n**Financial planning:**\n- Create a monthly care budget\n- Project costs over 3-5 years ("runway")\n- Apply for benefits early (processing takes time)\n- Consider tax deductions for medical expenses\n\nThe **Cost Planner\'s financial modules** will help you identify eligible funding sources and create a budget.',
    },
    {
        "flags": ["is_home_owner", "financial_gap"],
        "priority": 2,
        "category": "cost",
        "question": "Should I use home equity to pay for care?",
        "triggers": ["home equity", "reverse mortgage", "sell home", "home sale", "house equity"],
        "response": "Home equity can fund care, but consider carefully:\n\n**Options:**\n- **Sell the home** — Full proceeds available immediately (minus selling costs)\n- **Reverse mortgage** — Monthly payments or line of credit, keep ownership\n- **Home equity loan** — Lump sum, requires monthly payments (may not fit fixed income)\n- **Home equity line of credit (HELOC)** — Flexibility, requires monthly payments\n\n**Questions to ask:**\n- Will your loved one return home?\n- Is there a healthy spouse still living there?\n- Do you want to preserve it for heirs?\n- What's the Medicaid impact? (Home may be exempt asset)\n- What are the tax implications?\n\n**Reverse mortgage details:**\n- Available to homeowners 62+\n- No monthly payments required\n- Loan repaid when home is sold or owner passes\n- Can fund care while preserving Medicaid eligibility (in some cases)\n\n**Important:** This decision affects Medicaid planning, inheritance, and long-term options. Consult with a **Plan for My Advisor** expert and consider elder law guidance.",
    },
    # ASSISTED LIVING FLAGS (Priority 3)
    {
        "flags": ["assisted_living_recommended", "assisted_living"],
        "priority": 3,
        "category": "care",
        "question": "What is assisted living and how much does it cost?",
        "triggers": ["assisted living", "assisted care", "assisted living cost"],
        "response": "Assisted living offers 24/7 support in a community setting for those needing help with daily activities.\n\n**Average costs:**\n- National average: $5,500/month\n- Geographic range: $3,500–$8,000/month\n- Additional care services: +$500–$2,000/month\n\n**What's included:**\n- Private or shared apartment\n- Three meals daily and snacks\n- Housekeeping and laundry\n- Personal care assistance (bathing, dressing, medication reminders)\n- Social activities and transportation\n- 24/7 staff availability\n\n**What costs extra:**\n- Higher levels of care\n- Medication management\n- Specialized therapies\n- Beauty salon services\n\n**When is assisted living appropriate?**\n- Needs help with 2+ daily activities (ADLs)\n- Social isolation at home\n- Home safety concerns\n- Family caregiver burnout\n\nEnter your ZIP code in the **Cost Planner** to get local estimates and compare facilities.",
    },
    # SKILLED NURSING FLAGS (Priority 3)
    {
        "flags": ["skilled_nursing_recommended", "high_medical_needs"],
        "priority": 3,
        "category": "care",
        "question": "What is skilled nursing care and when is it needed?",
        "triggers": ["skilled nursing", "nursing home", "nursing facility", "snf"],
        "response": "Skilled nursing facilities provide 24/7 medical care for those with complex health needs.\n\n**Average costs:**\n- Semi-private room: $8,000–$9,500/month\n- Private room: $9,000–$12,000/month\n- Geographic variation: $6,000–$15,000/month\n\n**Services include:**\n- 24/7 licensed nursing care\n- Medical monitoring and treatments\n- Rehabilitation services (PT, OT, speech therapy)\n- Medication management\n- Personal care and meals\n- Wound care, IV therapy, feeding tubes\n\n**When is skilled nursing needed?**\n- Post-hospital recovery requiring skilled care\n- Complex medical conditions (tracheostomy, ventilator)\n- Advanced dementia with medical complications\n- End-stage illness requiring palliative care\n- Multiple chronic conditions requiring constant monitoring\n\n**Medicare coverage:**\n- Up to 100 days post-hospitalization (first 20 days fully covered)\n- Must have 3+ day hospital stay first\n- Only covers skilled nursing, not custodial care\n\nUse the **Cost Planner** to get local pricing and explore funding options like Medicaid or long-term care insurance.",
    },
    # HOSPICE/PALLIATIVE FLAGS (Priority 2)
    {
        "flags": ["end_of_life", "hospice_appropriate", "palliative_care"],
        "priority": 2,
        "category": "care",
        "question": "What is hospice care and is it covered by Medicare?",
        "triggers": ["hospice", "palliative care", "end of life care", "comfort care"],
        "response": "Hospice and palliative care focus on comfort and quality of life for those with serious illnesses.\n\n**Hospice care:**\n- For those with life expectancy of 6 months or less\n- Focuses on comfort, not cure\n- Usually covered by Medicare, Medicaid, or insurance\n- Can be provided at home, facility, or hospital\n\n**What Medicare hospice covers:**\n- Nursing care and doctor visits\n- Medical equipment and supplies\n- Medications for symptom control\n- Physical, occupational, and speech therapy\n- Social worker and counseling services\n- Short-term respite care for family caregivers\n- Grief counseling for family\n\n**Cost:**\n- Medicare covers ~95% of hospice costs\n- Small copays for medications ($5) and respite care\n- No copays for most services\n\n**Palliative care:**\n- Can be provided alongside curative treatment\n- Focuses on symptom management and quality of life\n- Cost: $500–$2,000/month for non-Medicare-covered services\n- Medicare may cover some palliative services\n\n**Important:** Hospice doesn't mean giving up hope—it means prioritizing comfort and quality time with loved ones.\n\nUse the **Cost Planner** to explore coverage and start with the **Guided Care Plan** to assess needs.",
    },
    # INSURANCE FLAGS (Priority 3)
    {
        "flags": ["has_ltc_insurance"],
        "priority": 3,
        "category": "benefits",
        "question": "How does my long-term care insurance work?",
        "triggers": [
            "long term care insurance",
            "ltc insurance",
            "insurance for care",
            "ltc policy",
        ],
        "response": "Long-term care insurance can help cover costs for home care, assisted living, or nursing homes. Coverage depends on your policy:\n\n**Common policy features:**\n- **Daily benefit**: Typically $100–$300/day\n- **Waiting period**: Often 90 days before benefits start (you pay out-of-pocket first)\n- **Benefit period**: 2–5 years of coverage (some unlimited)\n- **Inflation protection**: Benefit amount increases over time\n\n**What's typically covered:**\n- In-home care (most policies)\n- Assisted living\n- Memory care\n- Skilled nursing\n- Adult day care\n\n**What's usually NOT covered:**\n- Care provided by family members\n- Services during waiting period\n- Pre-existing conditions (sometimes)\n\n**Action steps:**\n1. Review your policy document carefully\n2. Understand your daily benefit and waiting period\n3. Check if provider needs to be approved\n4. File claim early (waiting period starts when claim is filed)\n5. Keep detailed records of care expenses\n\nReview your policy details and use the **Cost Planner** to see how insurance fits into your budget.",
    },
    # GENERAL PLANNING (Priority 3)
    {
        "flags": [],
        "priority": 3,
        "category": "planning",
        "question": "How do I talk to my family about care planning?",
        "triggers": ["talk to", "family", "conversation", "family meeting", "discuss care"],
        "response": 'Having the care conversation with family can be difficult. Here\'s how:\n\n**Preparation tips:**\n- Start early before a crisis\n- Focus on safety and quality of life, not "giving up independence"\n- Share specific concerns (falls, medications, isolation)\n- Come with objective data (care plan results, costs, options)\n\n**Conversation structure:**\n1. **Express concern with love** — "I\'m worried about your safety and want to help"\n2. **Share specific observations** — "I\'ve noticed you\'ve fallen twice this month"\n3. **Present options, not ultimatums** — "Let\'s look at a few ways to keep you safe"\n4. **Include the person receiving care** — Honor their preferences and dignity\n5. **Focus on maintaining independence** — "This will help you stay in control"\n\n**Bring data:**\n- Guided Care Plan assessment results\n- Cost Planner estimates\n- Doctor\'s recommendations\n- Options that match their preferences\n\n**Common resistance:**\n- "I\'m fine" → Acknowledge feelings, share specific concerns\n- "Too expensive" → Show funding options (VA, Medicaid, etc.)\n- "I don\'t want to be a burden" → Emphasize family wants to help\n\n**Remember:** This is a process, not a one-time talk. Be patient and revisit the conversation as needs change.\n\nThe Guided Care Plan and Cost Planner give you objective information to frame the conversation.',
    },
]


# ==============================================================================
# DYNAMIC QUESTION SELECTION ENGINE
# ==============================================================================


def _get_active_flags() -> set[str]:
    """Extract all active care and cost flags from session state.

    Returns:
        Set of flag strings (e.g., {'fall_risk', 'veteran_eligible', 'cog_moderate'})
    """
    active_flags: set[str] = set()

    # Get GCP handoff flags
    handoff = st.session_state.get("handoff", {})
    gcp_state = handoff.get("gcp", {})
    gcp_flags = gcp_state.get("flags", {})

    # Add all TRUE GCP flags
    for flag_name, flag_value in gcp_flags.items():
        if flag_value:
            active_flags.add(flag_name)

    # Get GCP care recommendation and derive flags
    care_recommendation = gcp_state.get("recommendation", "")
    if care_recommendation:
        rec_lower = care_recommendation.lower()
        if "in-home" in rec_lower or "in_home" in rec_lower:
            active_flags.add("in_home_care")
            active_flags.add("home_care_recommended")
        if "assisted living" in rec_lower:
            active_flags.add("assisted_living")
            active_flags.add("assisted_living_recommended")
        if "memory care" in rec_lower:
            active_flags.add("memory_care")
            active_flags.add("dementia_care")
        if "skilled nursing" in rec_lower:
            active_flags.add("skilled_nursing_recommended")
            active_flags.add("high_medical_needs")

    # Get Cost Planner state
    cost_data = st.session_state.get("cost_data", {})

    # Veteran status
    is_veteran = cost_data.get("is_veteran", False)
    if is_veteran:
        active_flags.add("is_veteran")
        active_flags.add("veteran_eligible")

    # Home ownership
    is_home_owner = cost_data.get("is_home_owner", False)
    if is_home_owner:
        active_flags.add("is_home_owner")
        active_flags.add("aging_in_place")

    # Medicaid status
    has_medicaid = cost_data.get("has_medicaid", False)
    medicaid_likely = cost_data.get("medicaid_likely", False)
    if has_medicaid or medicaid_likely:
        active_flags.add("has_medicaid")
        active_flags.add("medicaid_likely")

    # Long-term care insurance
    has_ltc_insurance = cost_data.get("has_ltc_insurance", False)
    if has_ltc_insurance:
        active_flags.add("has_ltc_insurance")

    # Financial gap detection
    monthly_income = cost_data.get("monthly_income", 0)
    estimated_cost = cost_data.get("estimated_monthly_cost", 0)
    if estimated_cost > 0 and monthly_income > 0:
        if monthly_income < estimated_cost:
            active_flags.add("financial_gap")
            active_flags.add("cost_concern")

    # Assets
    total_assets = cost_data.get("total_assets", 0)
    if total_assets > 50000:
        active_flags.add("has_assets")

    return active_flags


def _build_suggested_questions(
    active_flags: set[str], asked_questions: list[str]
) -> list[dict[str, Any]]:
    """Build pool of relevant questions based on active flags.

    Args:
        active_flags: Set of active flag strings from user's context
        asked_questions: List of question text strings already asked

    Returns:
        List of question dicts, sorted by relevance (priority + flag matches)
    """
    scored_questions = []

    for q in QUESTION_DATABASE:
        # Skip if already asked
        if q["question"] in asked_questions:
            continue

        # Calculate relevance score
        question_flags = set(q["flags"])

        # If question has no flags, it's a default question (always available)
        if not question_flags:
            # Base score for default questions
            score = 100 - q["priority"] * 10
        else:
            # Score based on flag matches
            matches = len(active_flags & question_flags)
            if matches == 0:
                # No flag match, skip this question
                continue

            # Higher priority = higher score (priority 1 is most urgent)
            priority_boost = (4 - q["priority"]) * 20  # Priority 1 = 60, 2 = 40, 3 = 20
            match_boost = matches * 15  # Each matched flag adds 15 points

            score = priority_boost + match_boost

        scored_questions.append(
            {
                "question": q,
                "score": score,
                "matches": len(active_flags & question_flags) if question_flags else 0,
            }
        )

    # Sort by score (highest first)
    scored_questions.sort(key=lambda x: x["score"], reverse=True)

    # Return question objects
    return [sq["question"] for sq in scored_questions]


def _get_top_3_suggestions() -> list[str]:
    """Get 3 best questions to display right now.

    Returns:
        List of 3 question text strings
    """
    asked = st.session_state.get("ai_asked_questions", [])
    active_flags = _get_active_flags()

    # Build pool of relevant questions
    question_pool = _build_suggested_questions(active_flags, asked)

    # If we have fewer than 3 questions, reset asked history (except most recent 3)
    if len(question_pool) < 3:
        st.session_state["ai_asked_questions"] = asked[-3:] if len(asked) > 3 else []
        question_pool = _build_suggested_questions(
            active_flags, st.session_state["ai_asked_questions"]
        )

    # Take top 3 from sorted, relevant questions
    top_questions = question_pool[:3]

    # If still not enough, add default questions
    if len(top_questions) < 3:
        default_questions = [q for q in QUESTION_DATABASE if not q["flags"]]
        for dq in default_questions:
            if dq["question"] not in [tq["question"] for tq in top_questions]:
                top_questions.append(dq)
            if len(top_questions) >= 3:
                break

    return [q["question"] for q in top_questions[:3]]


def _get_navi_response(question_text: str) -> str:
    """Generate Navi's response to a question.

    Uses the question database to match questions by exact text or triggers.

    Args:
        question_text: User's question string

    Returns:
        Response text from database or fallback response
    """
    q_lower = question_text.lower()

    # Try exact match first
    for q in QUESTION_DATABASE:
        if q["question"].lower() == q_lower:
            return q["answer"]

    # Try trigger matching
    for q in QUESTION_DATABASE:
        for trigger in q["triggers"]:
            if trigger.lower() in q_lower:
                return q["answer"]

    # Legacy fallback for unmatched questions
    return _get_legacy_response(question_text)


def _get_legacy_response(question: str) -> str:
    """Legacy fallback responses for questions not yet in database.

    TODO: Eventually migrate all of these into the main QUESTION_DATABASE.
    """
    q = question.lower()

    # Urgency/warning signs
    if "urgent" in q or "warning sign" in q or "need care now" in q:
        return (
            "**Urgent warning signs requiring immediate action:**\n"
            "🚨 Falls or near-falls becoming frequent\n"
            "🚨 Forgetting medications or taking incorrectly\n"
            "🚨 Weight loss, poor nutrition\n"
            "🚨 Unable to manage personal hygiene\n"
            "🚨 Wandering or getting lost\n"
            "🚨 Burns from cooking/smoking\n"
            "🚨 Signs of self-neglect\n\n"
            "If you see these, don't wait. Contact your doctor and consider emergency respite care while you set up a longer-term plan."
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


# ==============================================================================
# PAGE RENDER
# ==============================================================================


def render():
    """Render AI Advisor FAQ page with modern chat interface."""
    
    # CSS Styling
    st.markdown("""
    <style>
      /* Center the experience */
      .faq-wrap { max-width: 960px; margin: 0 auto; padding: 12px 20px 28px; }
      .faq-head h1 { margin: 0 0 6px; font-size: 2rem; }
      .faq-head p  { color:#64748B; margin:0 0 20px; font-size: 1.05rem; }

      /* Recommended chips */
      .chips { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0 20px; }

      /* Chat area */
      .chat { display:flex; flex-direction:column; gap:16px; margin: 20px 0; min-height: 200px; }
      .msg-wrapper { display: flex; width: 100%; }
      .msg-wrapper.user { justify-content: flex-end; }
      .msg-wrapper.assistant { justify-content: flex-start; }
      
      .msg { max-width: 75%; padding:12px 16px; border-radius:16px; line-height:1.6; word-wrap: break-word; }
      .msg.user { background:#DCFCE7; border:1px solid #86EFAC; border-bottom-right-radius: 4px; }
      .msg.assistant { background:#F8FAFC; border:1px solid #E5E7EB; border-bottom-left-radius: 4px; }

      /* Sources & CTA */
      .sources { color:#6B7280; font-size:0.875rem; margin-top:8px; }
      .source-pill { 
        background:#EEF2FF; 
        border:1px solid #C7D2FE; 
        border-radius:12px; 
        padding:3px 10px; 
        margin:4px 4px 4px 0; 
        display:inline-block;
        font-size: 0.85rem;
      }
      
      .msg-divider { border-top: 1px solid #E5E7EB; margin: 12px 0; }

      @media (max-width: 768px) {
        .msg { max-width: 90%; }
        .faq-wrap { padding: 8px 12px 20px; }
      }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for chat
    if "faq_chat" not in st.session_state:
        st.session_state["faq_chat"] = []
    if "faq_composer" not in st.session_state:
        st.session_state["faq_composer"] = ""
    if "faq_send_now" not in st.session_state:
        st.session_state["faq_send_now"] = False
    
    # Header
    st.markdown('<div class="faq-wrap">', unsafe_allow_html=True)
    st.markdown(
        '<div class="faq-head"><h1>Ask the AI Advisor</h1>'
        '<p>Short, on-point answers grounded in our FAQ and company knowledge.</p></div>',
        unsafe_allow_html=True
    )
    
    # ─── Recommended Questions (3 chips) ───
    st.markdown("**Recommended questions:**")
    
    # Curated high-value questions
    recommendations = [
        "How long does the Guided Care Plan take?",
        "What does the Cost Planner do?",
        "Do I need a diagnosis for Memory Care?"
    ]
    
    cols = st.columns(3)
    for i, rec_q in enumerate(recommendations):
        if cols[i].button(
            rec_q,
            key=f"rec_chip_{i}",
            use_container_width=True,
            help="Click to ask"
        ):
            st.session_state["faq_composer"] = rec_q
            st.session_state["faq_send_now"] = True
            st.rerun()
    
    st.markdown("---")
    
    # ─── Chat Transcript ───
    chat = st.session_state["faq_chat"]
    
    if not chat:
        st.info("💡 Click a recommended question above or type your own to start chatting.")
    else:
        st.markdown('<div class="chat">', unsafe_allow_html=True)
        
        for idx, msg in enumerate(chat):
            role = msg["role"]
            text = msg["text"]
            
            if role == "user":
                st.markdown(
                    f'<div class="msg-wrapper user"><div class="msg user">{text}</div></div>',
                    unsafe_allow_html=True
                )
            else:  # assistant
                st.markdown(
                    f'<div class="msg-wrapper assistant"><div class="msg assistant">{text}</div></div>',
                    unsafe_allow_html=True
                )
                
                # Sources (if FAQ)
                sources = msg.get("sources", [])
                if sources:
                    pills_html = " ".join([
                        f'<span class="source-pill">{src}</span>'
                        for src in sources[:3]  # Max 3 visible
                    ])
                    st.markdown(
                        f'<div class="sources">📚 Sources: {pills_html}</div>',
                        unsafe_allow_html=True
                    )
                
                # CTA Button
                cta = msg.get("cta")
                if cta:
                    if st.button(
                        cta["label"],
                        key=f"cta_{idx}_{cta['route']}",
                        type="secondary",
                        use_container_width=False
                    ):
                        route_to(cta["route"])
                
                # Feedback buttons
                st.markdown("")  # Spacing
                fb_col1, fb_col2 = st.columns([1, 1])
                with fb_col1:
                    if st.button("👍 Helpful", key=f"fb_yes_{idx}"):
                        from core.events import log_event
                        log_event("faq_feedback", {"helpful": True, "msg_idx": idx})
                        st.toast("Thanks for the feedback!", icon="✅")
                with fb_col2:
                    if st.button("👎 Not helpful", key=f"fb_no_{idx}"):
                        from core.events import log_event
                        log_event("faq_feedback", {"helpful": False, "msg_idx": idx})
                        st.toast("Thanks — we'll improve this!", icon="📝")
                
                # Divider after each assistant message
                if idx < len(chat) - 1:
                    st.markdown('<div class="msg-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ─── Composer ───
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_q = st.text_input(
            "Ask about planning, costs, eligibility, or our company…",
            key="faq_composer_input",
            placeholder="e.g., What is assisted living? Who is CCA?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_clicked = st.button("Send", type="primary", key="faq_send_btn")
    
    # Also trigger on chip click
    send_now = st.session_state.pop("faq_send_now", False)
    should_send = send_clicked or send_now
    
    # If chip was clicked, use the stored composer value
    if send_now and st.session_state.get("faq_composer"):
        user_q = st.session_state["faq_composer"]
        st.session_state["faq_composer"] = ""
    
    # ─── Process Question ───
    if should_send and user_q and user_q.strip():
        q = user_q.strip()
        
        # Add user message
        st.session_state["faq_chat"].append({"role": "user", "text": q})
        
        with st.spinner("🤔 Thinking..."):
            # Load policy
            policy = load_faq_policy()
            
            # ─── ROUTING: Corp Knowledge vs FAQ ───
            corp_keywords = [
                "cca", "concierge care advisors", "leadership", "team",
                "about", "founded", "business since", "history",
                "who is", "who are", "company", "organization"
            ]
            is_corp_query = any(kw in q.lower() for kw in corp_keywords)
            
            if is_corp_query:
                # Try corporate knowledge first
                corp_chunks = load_corp_chunks()
                corp_hits = retrieve_corp(q, corp_chunks, k=5)
                
                if corp_hits:
                    from core.state import get_current_name
                    from ai.llm_mediator import answer_corp
                    
                    name = get_current_name() or policy.get("fallback_name", "the person you're helping")
                    result = answer_corp(q, name, corp_hits, policy)
                    
                    # Format sources for display
                    source_titles = [f"{s['title']}" for s in result.get("sources", [])[:3]]
                    
                    msg = {
                        "role": "assistant",
                        "text": result["answer"],
                        "sources": source_titles,
                        "cta": None  # Corp answers don't have CTAs
                    }
                    
                    # Log corp query
                    from core.events import log_event
                    log_event("corp_llm", {
                        "query": q,
                        "retrieved_ids": [c["doc_id"] for c in corp_hits],
                        "used_sources": [s.get("url", "") for s in result.get("sources", [])],
                        "name_present": bool(st.session_state.get("person_a_name")),
                    })
                    
                    st.session_state["faq_chat"].append(msg)
                    st.rerun()
            
            # ─── FAQ Path ───
            if not is_corp_query or not corp_hits:
                faqs = load_faq_items()
                retrieved = retrieve_faq(q, faqs, k=3)
                
                if retrieved:
                    from core.state import get_current_name
                    from ai.llm_mediator import answer_faq
                    
                    name = get_current_name() or policy.get("fallback_name", "the person you're helping")
                    result = answer_faq(q, name, retrieved, policy)
                    
                    # Map source IDs to FAQ questions for display
                    used_ids = set(result.get("sources", []))
                    source_titles = [
                        f["question"][:50] + ("..." if len(f["question"]) > 50 else "")
                        for f in retrieved if f["id"] in used_ids
                    ]
                    
                    msg = {
                        "role": "assistant",
                        "text": result["answer"],
                        "sources": source_titles,
                        "cta": result.get("cta")
                    }
                    
                    # Log FAQ query
                    from core.events import log_event
                    log_event("faq_llm", {
                        "query": q,
                        "retrieved_ids": [f["id"] for f in retrieved],
                        "used_sources": result.get("sources", []),
                        "cta_route": (result.get("cta") or {}).get("route"),
                        "name_present": bool(st.session_state.get("person_a_name")),
                    })
                else:
                    # No results fallback
                    msg = {
                        "role": "assistant",
                        "text": "We don't have that in our FAQ yet. You can start the Guided Care Plan to get a tailored next step.",
                        "sources": [],
                        "cta": {"label": "Open Guided Care Plan", "route": "gcp_intro"}
                    }
                    
                    # Log no-result query
                    from core.events import log_event
                    log_event("faq_llm", {
                        "query": q,
                        "retrieved_ids": [],
                        "used_sources": [],
                        "cta_route": "gcp_intro",
                        "name_present": bool(st.session_state.get("person_a_name")),
                    })
                
                st.session_state["faq_chat"].append(msg)
                st.rerun()
    
    # ─── Controls ───
    col_clear, col_back = st.columns([1, 1])
    
    with col_clear:
        if st.button("�️ Clear chat", key="clear_chat_btn", help="Reset conversation"):
            st.session_state["faq_chat"] = []
            st.rerun()
    
    with col_back:
        if st.button("← Back to Hub", key="back_to_hub_btn", use_container_width=True):
            route_to("hub_concierge")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close faq-wrap


def _ask_question(question: str):
    """Process a question - add to thread, mark as asked, get response."""
    # Add to thread
    st.session_state["ai_thread"].append(("user", question))
    st.session_state["ai_thread"].append(("assistant", _get_navi_response(question)))

    # Add to asked questions (for filtering suggestions)
    st.session_state["ai_asked_questions"].append(question)


def _get_suggested_questions_pool() -> list:
    """Generate pool of suggested questions based on user context and flags.

    Uses NaviOrchestrator for centralized flag-driven question logic.
    """

    # Get centralized flags from all products/modules
    flags = get_all_flags()

    # Get completed products for context
    progress = MCIP.get_journey_progress()
    completed_products = progress.get("completed_products", [])

    # Use NaviOrchestrator for centralized question generation
    questions = NaviOrchestrator.get_suggested_questions(flags, completed_products)

    # Filter out already asked questions
    asked = set(st.session_state.get("ai_asked_questions", []))
    available = [q for q in questions if q not in asked]

    # If we've asked everything, reset and show all again
    if len(available) < 3:
        available = questions

    return available
