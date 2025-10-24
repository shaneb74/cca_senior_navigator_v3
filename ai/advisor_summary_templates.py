"""
LLM Narrative Templates for Advisor Summary Drawers

These templates generate natural-language paragraphs for internal advisor dashboards,
describing what the system knows about each person based on GCP, Cost Planner, and CareFlags data.

Target audience: Internal business and advisor stakeholders
Tone: Warm, empathetic, factual - suitable for internal reports
Length: 80-120 words per drawer
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class AdvisorSummaryContext:
    """Context data for generating advisor summary narratives."""
    
    # Profile Context
    person_a_name: str
    person_a_age_range: str
    relationship_type: str
    geo_zip: str
    support_network_low: bool
    low_access: bool
    home_carry: bool
    dual_household: bool
    
    # Guided Care Plan
    recommended_tier: str
    allowed_tiers: List[str]
    move_timeline: str
    room_type: str
    care_flags: List[str]
    
    # Cost Planner
    monthly_cost: float
    household_income: float
    total_assets: float
    years_funded: float
    va_benefits_eligible: bool
    assets_low: bool
    assets_high: bool
    benefits_present: bool
    rx_costs_high: bool
    transportation_needed: bool
    auto_present: bool
    family_travel_needed: bool


# Template 1: About the Person
ABOUT_PERSON_TEMPLATE = """
Write a comprehensive demographic and social profile for [person_a_name] that gives advisors a complete picture of their current situation and what additional context may be needed.

Include a detailed assessment of:

DEMOGRAPHIC PROFILE:
- Full name, age range, and current living arrangement
- Geographic location and community context
- Household composition and family dynamics
- Primary decision-maker and relationship to care recipient

SOCIAL SUPPORT ASSESSMENT:
- Family support network strength and proximity
- Available informal caregivers and their capacity
- Community connections and social isolation factors
- Transportation access and mobility independence
- Emergency contact availability and response capability

CURRENT LIVING SITUATION:
- Housing type, ownership status, and suitability for aging in place
- Home safety assessment needs and accessibility modifications required
- Neighborhood resources and service availability
- Financial obligations related to current housing

GAPS REQUIRING ADVISOR FOLLOW-UP:
- Missing demographic information that impacts care planning
- Unassessed family dynamics or caregiver stress factors
- Unknown community resources or support systems
- Unclear decision-making authority or legal considerations

This should be a thorough profile that helps advisors understand the complete social and environmental context, not a brief introduction. Include specific details about what we know versus what still needs to be explored in advisor conversations.
"""

# Template 2: Housing Preferences  
HOUSING_PREFERENCES_TEMPLATE = """
Write a comprehensive housing and care setting assessment for [person_a_name] that provides advisors with detailed information about housing preferences, readiness for transition, and what additional housing-related context is needed.

Include a thorough analysis of:

CARE SETTING PREFERENCES:
- Detailed exploration of preferred care environments and settings
- Specific amenities, services, and community features desired
- Cultural, religious, or lifestyle preferences affecting housing choice
- Pet ownership, hobbies, or special accommodation needs

TRANSITION READINESS AND TIMELINE:
- Current readiness to consider care options and move from current home
- Emotional attachment to current home and community
- Family agreement or disagreement about care transitions
- Preferred timeline for exploring options versus actual move timing
- Seasonal or family event considerations affecting timing

FINANCIAL CONSIDERATIONS FOR HOUSING:
- Current housing costs and ongoing obligations
- Proceeds expected from home sale and timeline for sale
- Rental income potential if keeping current property
- Moving costs, deposits, and transition expenses anticipated

LOCATION AND COMMUNITY PREFERENCES:
- Desired proximity to family members, friends, or healthcare providers
- Transportation needs and access to community resources
- Climate or geographic preferences if considering relocation
- Specific community features important to quality of life

GAPS REQUIRING ADVISOR EXPLORATION:
- Unresolved housing decisions or family disagreements
- Financial implications not yet calculated or understood
- Care needs that may affect housing suitability over time
- Legal or estate planning considerations related to housing decisions

This should provide advisors with a complete housing and transition assessment, highlighting both confirmed preferences and areas needing further exploration during advisor consultations.
"""

# Template 3: Medical & Care Information
MEDICAL_CARE_TEMPLATE = """
Describe what the system has learned about [person_a_name]'s care needs based on their care flags: [care_flags].

Translate care flags into natural language:
- moderate_cognitive_decline/severe_cognitive_decline → memory changes or cognitive concerns
- mobility_limited/falls_risk → mobility challenges, stability concerns
- adl_support_high → needs assistance with daily activities
- chronic_conditions → ongoing health conditions requiring management
- medication_management → medication oversight needs
- behavioral_concerns → behavioral changes or challenges
- safety_concerns → safety supervision requirements
- caregiver_fatigue → family caregiver stress

Emphasize care coordination needs and support requirements rather than deficits. Use respectful, person-centered language.

Style: Professional medical summary focusing on care needs and coordination.
Length: 80-120 words.
"""

# Template 4: Financial Overview
FINANCIAL_OVERVIEW_TEMPLATE = """
Write a comprehensive financial assessment for [person_a_name] that provides advisors with detailed information about their complete financial picture and identifies areas requiring additional financial planning consultation.

Include a thorough analysis of:

INCOME ASSESSMENT:
- Complete breakdown of all monthly income sources (Social Security, pensions, retirement accounts, employment, rental income, family support)
- Stability and predictability of each income stream
- Potential changes to income over time (retirement timing, pension adjustments, Social Security optimization)
- Tax implications and net versus gross income considerations

ASSET EVALUATION:
- Detailed inventory of liquid assets (savings, checking, CDs, money market accounts)
- Investment portfolio composition and risk tolerance
- Real estate holdings including primary residence and investment properties
- Personal property of significant value and collectibles
- Retirement accounts (401k, IRA, Roth IRA) and withdrawal strategies

LIABILITIES AND ONGOING OBLIGATIONS:
- Current debt obligations (mortgage, credit cards, loans, lines of credit)
- Monthly fixed expenses and discretionary spending patterns
- Insurance premiums and coverage gaps
- Tax liabilities and estate planning considerations

CARE FUNDING ANALYSIS:
- Projected monthly care costs for different levels of care
- Funding timeline calculations under various scenarios
- Long-term care insurance coverage and benefit details
- Veterans benefits eligibility and application status
- Medicaid planning considerations and asset protection strategies

BENEFITS AND ENTITLEMENTS:
- Current benefits received and optimization opportunities
- Potential benefits not yet claimed or applied for
- Insurance coverage for healthcare, long-term care, and life insurance
- Family financial support capacity and willingness

GAPS REQUIRING ADVISOR CONSULTATION:
- Incomplete financial information or documentation needed
- Estate planning updates or legal document reviews required
- Tax planning opportunities or concerns
- Insurance coverage adequacy assessment
- Long-term financial sustainability questions
- Family financial planning coordination needs

This should provide advisors with a complete financial picture and clear understanding of what additional financial planning work is needed during their consultation.
"""


def generate_advisor_summary_prompts() -> Dict[str, str]:
    """
    Return the four LLM prompt templates for advisor summary generation.
    
    Returns:
        Dictionary with drawer names as keys and prompt templates as values
    """
    return {
        "about_person": ABOUT_PERSON_TEMPLATE,
        "housing_preferences": HOUSING_PREFERENCES_TEMPLATE, 
        "medical_care": MEDICAL_CARE_TEMPLATE,
        "financial_overview": FINANCIAL_OVERVIEW_TEMPLATE
    }


# Example context for testing
EXAMPLE_CONTEXT = AdvisorSummaryContext(
    # Profile Context
    person_a_name="Margaret",
    person_a_age_range="late seventies", 
    relationship_type="adult_child",
    geo_zip="70808",
    support_network_low=True,
    low_access=True,
    home_carry=True,
    dual_household=False,
    
    # Guided Care Plan
    recommended_tier="assisted_living",
    allowed_tiers=["independent_living", "assisted_living"],
    move_timeline="flexible",
    room_type="one_bedroom",
    care_flags=["moderate_cognitive_decline", "mobility_limited", "medication_management", "chronic_conditions"],
    
    # Cost Planner
    monthly_cost=4200.0,
    household_income=3800.0,
    total_assets=180000.0,
    years_funded=4.5,
    va_benefits_eligible=True,
    assets_low=False,
    assets_high=False,
    benefits_present=True,
    rx_costs_high=False,
    transportation_needed=True,
    auto_present=False,
    family_travel_needed=False
)


# Example outputs (what the LLM should generate)
EXAMPLE_OUTPUTS = {
    "about_person": """
# Example outputs (comprehensive advisor reports)
EXAMPLE_OUTPUTS = {
    "about_person": "Comprehensive demographic and social profile covering living situation, family dynamics, support network, and gaps requiring advisor follow-up.",
    "housing_preferences": "Detailed housing assessment covering care setting preferences, transition readiness, financial considerations, and areas needing advisor exploration.", 
    "medical_care": "Margaret experiences moderate memory changes and mild mobility challenges. Care flags: moderate_cognitive_decline, mobility_limited, medication_management, chronic_conditions.",
    "financial_overview": "Comprehensive financial assessment covering income sources, asset evaluation, liabilities, care funding analysis, benefits assessment, and gaps requiring advisor consultation."
}
""".strip(),

    "housing_preferences": """
Margaret has expressed interest in Assisted Living communities that provide both independence and support with daily activities. She would prefer a one-bedroom apartment with services like meal preparation and housekeeping. Her move timeline is flexible, allowing time to research suitable communities nearby. She plans to keep her current home for now while exploring her options.
""".strip(),

    "medical_care": """
Margaret experiences moderate memory changes and mild mobility challenges that affect her daily stability. Her medical history includes ongoing health conditions requiring regular monitoring, and she takes several daily medications that benefit from professional oversight. Her care plan emphasizes consistent routines, medication management, and access to assistance when needed to maintain safety and independence.
""".strip(),

    "financial_overview": """
Margaret's projected monthly budget for care is approximately $4,200, which will require careful coordination of her current income and assets. Based on her Social Security, pension income, and available savings, she is estimated to be funded for roughly four to five years of Assisted Living. She may also qualify for Veterans Aid & Attendance benefits, which could extend her coverage timeline.
""".strip()
}


if __name__ == "__main__":
    """Test the template system"""
    print("=== Advisor Summary Templates ===\n")
    
    templates = generate_advisor_summary_prompts()
    
    for drawer_name, template in templates.items():
        print(f"## {drawer_name.replace('_', ' ').title()}")
        print(template)
        print("\n" + "="*50 + "\n")
    
    print("=== Example Outputs ===\n")
    
    for drawer_name, example in EXAMPLE_OUTPUTS.items():
        print(f"## {drawer_name.replace('_', ' ').title()}")
        print(example)
        print("\n" + "-"*30 + "\n")