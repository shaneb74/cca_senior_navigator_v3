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
Write a short paragraph that introduces [person_a_name], who is in their [person_a_age_range] and currently lives in the [geo_zip] area. 

Consider their living situation:
- If [dual_household] is true, mention they live with family or a partner
- If [dual_household] is false, mention they live independently or alone
- If [support_network_low] is true, note limited family support nearby
- If [low_access] is true, mention challenges accessing services or support

Include information about who is helping with planning based on [relationship_type] (spouse, adult child, etc.).

Style: Warm introduction that establishes the person's current situation and support context. Use their first name throughout.
Length: 80-120 words.
"""

# Template 2: Housing Preferences  
HOUSING_PREFERENCES_TEMPLATE = """
Summarize [person_a_name]'s preferred living arrangement based on their [recommended_tier] recommendation and planning preferences.

Include details about:
- Housing type preference based on [recommended_tier] (Independent Living, Assisted Living, Memory Care, etc.)
- Room preference from [room_type] (studio, one-bedroom, two-bedroom)
- Move timeline from [move_timeline] (immediate, 3-6 months, flexible, etc.)
- Home plans: if [home_carry] is true, mention keeping their current home; if false, mention selling

Focus on their expressed preferences and desired setting rather than just the recommendation.

Style: Factual summary of housing goals and timeline preferences.
Length: 80-120 words.
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
Create a financial summary for [person_a_name] based on their cost planning data.

Include information about:
- Projected monthly care budget: approximately $[monthly_cost]
- Funding timeline: estimated [years_funded] years of coverage
- Asset situation: if [assets_low] mention limited assets, if [assets_high] mention substantial assets
- Income sources: reference [household_income] and any relevant details
- Benefits: if [va_benefits_eligible] mention potential VA benefits, if [benefits_present] mention existing benefits
- Special considerations: if [rx_costs_high] mention medication costs, if [transportation_needed] or [family_travel_needed] mention transportation factors

Focus on affordability range and funding timeline rather than giving financial advice.

Style: Neutral financial overview suitable for advisor planning.
Length: 80-120 words.
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
This plan is for Margaret, who is in her late seventies and currently lives alone in the Baton Rouge area (70808). She has limited access to nearby family and occasionally relies on neighbors for support. Her daughter is assisting with planning and exploring options that would keep Margaret close to familiar surroundings while ensuring she receives appropriate care and oversight.
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