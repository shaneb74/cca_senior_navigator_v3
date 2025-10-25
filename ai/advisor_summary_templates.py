"""
LLM Narrative Templates for Advisor Summary Drawers

These templates generate natural-language paragraphs for internal advisor dashboards,
describing what the system knows about each person based on GCP, Cost Planner, and CareFlags data.

Target audience: Internal business and advisor stakeholders
Tone: Warm, empathetic, factual - suitable for internal reports
Length: 80-120 words per drawer

PERSONALIZATION STYLE RULES:
- Always refer to the care recipient by their first name: {person_first_name}
- Use possessive form when appropriate: {person_possessive} 
- Avoid generic "the client" or "this person" language
- Example: "Shane's medical history includes..." not "The client's medical history includes..."
- Example: "Mary needs assistance with..." not "This person needs assistance with..."
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from core.name_utils import first_name, possessive


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
    
    # Cost Planner Basic
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
    
    # Detailed Income Breakdown
    social_security: float = 0.0
    pension: float = 0.0
    retirement_401k: float = 0.0
    roth_ira: float = 0.0
    traditional_ira: float = 0.0
    employment: float = 0.0
    rental_income: float = 0.0
    investment_income: float = 0.0
    family_support: float = 0.0
    other_income: float = 0.0
    
    # Detailed Asset Breakdown
    checking_accounts: float = 0.0
    savings_accounts: float = 0.0
    money_market: float = 0.0
    cds: float = 0.0
    retirement_401k_balance: float = 0.0
    traditional_ira_balance: float = 0.0
    roth_ira_balance: float = 0.0
    brokerage: float = 0.0
    home_value: float = 0.0
    investment_real_estate: float = 0.0
    life_insurance_cash: float = 0.0
    personal_property: float = 0.0
    
    # Detailed Debt Breakdown
    mortgage_balance: float = 0.0
    heloc_balance: float = 0.0
    credit_card_debt: float = 0.0
    auto_loans: float = 0.0
    personal_loans: float = 0.0
    medical_debt: float = 0.0
    other_debt: float = 0.0
    
    # Insurance Coverage
    medicare_a: bool = False
    medicare_b: bool = False
    medicare_supplement: bool = False
    medicare_advantage: bool = False
    ltc_insurance: bool = False
    life_insurance: float = 0.0
    disability_insurance: bool = False
    
    # About Person Fields
    age_years: int = 0
    gender: str = "Not captured"
    city: str = "Not captured"
    state: str = "Not captured"
    current_living_situation: str = "Not captured"
    housing_type: str = "Not captured"
    housing_ownership_status: str = "Not captured"
    lives_with_status: str = "Not captured"
    marital_status: str = "Not captured"
    adult_children_proximity: str = "Not captured"
    primary_caregiver_relationship: str = "Not captured"
    emergency_contact_available: bool = False
    family_support_strength: str = "Not captured"
    social_isolation_level: str = "Not captured"
    transportation_independence: str = "Not captured"
    neighbor_support_available: str = "Not captured"
    social_engagement_level: str = "Not captured"
    decision_maker_relationship: str = "Not captured"
    legal_documents_status: str = "Not captured"
    financial_poa_status: str = "Not captured"
    healthcare_poa_status: str = "Not captured"
    advanced_directives_status: str = "Not captured"
    
    # Housing Preferences Fields
    monthly_housing_costs: float = 0.0
    property_taxes_annual: float = 0.0
    home_insurance_annual: float = 0.0
    preferred_care_setting: str = "Not captured"
    aging_in_place_preference: str = "Not captured"
    move_timeline_months: int = 0
    move_readiness_level: str = "Not captured"
    family_setting_agreement: str = "Not captured"
    stay_near_current_location: str = "Not captured"
    proximity_to_family_preference: str = "Not captured"
    proximity_to_healthcare_preference: str = "Not captured"
    transportation_dependency: str = "Not captured"
    community_features_priorities: str = "Not captured"
    accessibility_modifications_needed: str = "Not captured"
    safety_modifications_needed: str = "Not captured"
    home_maintenance_challenges: str = "Not captured"
    property_management_challenges: str = "Not captured"
    emotional_readiness_for_move: str = "Not captured"
    financial_readiness_for_move: str = "Not captured"
    family_support_for_transition: str = "Not captured"
    care_needs_urgency: str = "Not captured"
    
    # Medical & Care Fields
    cognitive_status_level: str = "Not captured"
    memory_changes_reported: str = "Not captured"
    decision_making_independence: str = "Not captured"
    orientation_status: str = "Not captured"
    executive_function_level: str = "Not captured"
    primary_medical_diagnoses: str = "Not captured"
    chronic_conditions_list: str = "Not captured"
    recent_hospitalizations: str = "Not captured"
    mobility_status: str = "Not captured"
    fall_history_6months: str = "Not captured"
    vision_impairment_level: str = "Not captured"
    hearing_impairment_level: str = "Not captured"
    bathing_independence_level: str = "Not captured"
    dressing_independence_level: str = "Not captured"
    toileting_independence_level: str = "Not captured"
    transferring_independence_level: str = "Not captured"
    continence_status: str = "Not captured"
    feeding_independence_level: str = "Not captured"
    medication_management_ability: str = "Not captured"
    meal_preparation_ability: str = "Not captured"
    housekeeping_ability: str = "Not captured"
    financial_management_ability: str = "Not captured"
    phone_use_ability: str = "Not captured"
    current_care_hours_weekly: float = 0.0
    professional_services_current: str = "Not captured"
    medical_equipment_used: str = "Not captured"
    home_health_services: str = "Not captured"
    behavioral_concerns_present: str = "Not captured"
    depression_screening_results: str = "Not captured"
    anxiety_concerns_present: str = "Not captured"
    sleep_disturbances_reported: str = "Not captured"
    current_medications_count: int = 0
    medication_compliance_level: str = "Not captured"
    pharmacy_management_type: str = "Not captured"
    specialist_providers_seeing: str = "Not captured"
    provider_communication_needs: str = "Not captured"
    care_plan_update_frequency: str = "Not captured"
    family_caregiver_support_needs: str = "Not captured"
    emergency_response_plan_status: str = "Not captured"


# Template 1: About the Person
ABOUT_PERSON_TEMPLATE = """
Generate a structured data summary for {person_first_name} showing EXACTLY what demographic and social information we have captured in our system, organized by category. This is for advisor review to understand data completeness.

PERSONALIZATION STYLE RULES:
- Always refer to the care recipient by their first name: {person_first_name}
- Use possessive form when appropriate: {person_possessive}
- Example: "{person_first_name} lives alone in..." not "The client lives alone in..."
- Example: "{person_possessive} family support includes..." not "The family support includes..."

Show actual data categorization that we have captured, using the following format:

**BASIC DEMOGRAPHICS**
- Name: {person_first_name}
- Age: [age_years] years old (if captured)
- Gender: [gender] (if captured)
- ZIP Code: [geo_zip]
- City/State: [city], [state] (if captured)
- Relationship: Assessment completed by [relationship_type]

**LIVING SITUATION**
- Current Living: [current_living_situation] (if captured)
- Housing Type: [housing_type] (if captured)
- Ownership Status: [housing_ownership_status] (if captured)
- Lives With: [lives_with_status] (if captured)
- Marital Status: [marital_status] (if captured)

**FAMILY & SUPPORT NETWORK**
- Adult Children: [adult_children_proximity] (if captured)
- Primary Caregiver: [primary_caregiver_relationship] (if captured)
- Emergency Contact: [emergency_contact_available]
- Family Support Level: [family_support_strength] (if captured)
- Social Isolation Risk: [social_isolation_level] (if captured)
- Transportation Access: [transportation_independence] (if captured)

**CARE FLAGS - SOCIAL/SUPPORT**
List each social/support flag we have captured:
- Support Network Low: [support_network_low] (if flagged)
- Low Access: [low_access] (if flagged)
- Dual Household: [dual_household] (if flagged)
- Transportation Needed: [transportation_needed] (if flagged)
- Family Travel Needed: [family_travel_needed] (if flagged)

**DECISION-MAKING & LEGAL**
- Primary Decision Maker: [decision_maker_relationship] (if captured)
- Legal Documents: [legal_documents_status] (if captured)
- Financial POA: [financial_poa_status] (if captured)
- Healthcare POA: [healthcare_poa_status] (if captured)
- Advanced Directives: [advanced_directives_status] (if captured)

**DATA GAPS REQUIRING ADVISOR FOLLOW-UP**
List specific missing demographic/social information about {person_first_name}:
- [List any categories showing "Not captured"]
- Family dynamics assessment needed for {person_first_name}
- Legal documentation verification required for {person_possessive} care planning
- Support network capacity evaluation needed for {person_possessive} situation

Use the actual data from session state and show "Not captured" for any category where we don't have information. Be specific about what demographic and social data we have about {person_first_name} versus what's missing.
"""

# Template 2: Housing Preferences  
HOUSING_PREFERENCES_TEMPLATE = """
Generate a structured data summary for {person_first_name} showing EXACTLY what housing and care setting information we have captured in our system, organized by category. This is for advisor review to understand data completeness.

PERSONALIZATION STYLE RULES:
- Always refer to the care recipient by their first name: {person_first_name}
- Use possessive form when appropriate: {person_possessive}
- Example: "{person_first_name} prefers to stay in..." not "The client prefers to stay in..."
- Example: "{person_possessive} current home value is..." not "The current home value is..."

Show actual data categorization that we have captured, using the following format:

**CURRENT HOUSING DATA**
- Housing Type: [housing_type] (if captured)
- Ownership Status: [housing_ownership_status] (if captured)
- Home Value: $[home_value] (if captured)
- Monthly Housing Costs: $[monthly_housing_costs] (if captured)
- Property Taxes (Annual): $[property_taxes_annual] (if captured)
- Home Insurance (Annual): $[home_insurance_annual] (if captured)
- Mortgage Balance: $[mortgage_balance] (if captured)

**CARE RECOMMENDATION FOR {person_first_name}**
- Recommended Care Tier: [recommended_tier]
- Allowed Care Tiers: [allowed_tiers]
- Move Timeline: [move_timeline]
- Room Type Preference: [room_type] (if captured)

**HOUSING FLAGS - CAPTURED**
List each housing-related flag we have captured for {person_first_name}:
- Home Carry: [home_carry] (if flagged)
- Home Suitable for Aging: [home_suitable] (if captured)
- Accessibility Modifications Needed: [accessibility_modifications_needed] (if captured)
- Safety Modifications Needed: [safety_modifications_needed] (if captured)

**{person_possessive} CARE SETTING PREFERENCES**
- Preferred Care Setting: [preferred_care_setting] (if captured)
- Aging in Place Preference: [aging_in_place_preference] (if captured)
- Move Timeline (Months): [move_timeline_months] (if captured)
- Move Readiness Level: [move_readiness_level] (if captured)
- Family Agreement on Setting: [family_setting_agreement] (if captured)

**{person_possessive} LOCATION PREFERENCES**
- Stay Near Current Location: [stay_near_current_location] (if captured)
- Proximity to Family: [proximity_to_family_preference] (if captured)
- Proximity to Healthcare: [proximity_to_healthcare_preference] (if captured)
- Transportation Dependency: [transportation_dependency] (if captured)
- Community Features Important: [community_features_priorities] (if captured)

**HOME MODIFICATION NEEDS FOR {person_first_name}**
- Home Maintenance Challenges: [home_maintenance_challenges] (if captured)
- Property Management Issues: [property_management_challenges] (if captured)
- Emotional Readiness for Move: [emotional_readiness_for_move] (if captured)
- Financial Readiness for Move: [financial_readiness_for_move] (if captured)

**DATA GAPS REQUIRING ADVISOR FOLLOW-UP**
List specific missing housing-related information about {person_first_name}:
- [List any categories showing "Not captured"]
- Home safety assessment needed for {person_possessive} situation
- Family housing discussions required for {person_possessive} care planning
- Care setting cost comparisons needed for {person_possessive} options
- Legal/estate planning implications to explore for {person_possessive} housing decisions

Use the actual data from session state and show "Not captured" for any category where we don't have information. Be specific about what housing and care setting data we have about {person_first_name} versus what's missing.
"""

# Template 3: Medical & Care Information
MEDICAL_CARE_TEMPLATE = """
Generate a structured data summary for {person_first_name} showing EXACTLY what medical and care information we have captured in our system, organized by category. This is for advisor review to understand data completeness.

PERSONALIZATION STYLE RULES:
- Always refer to the care recipient by their first name: {person_first_name}
- Use possessive form when appropriate: {person_possessive}
- Example: "{person_first_name} experiences mild cognitive changes..." not "The client experiences mild cognitive changes..."
- Example: "{person_possessive} medical history includes..." not "The medical history includes..."

Show actual data categorization that we have captured, using the following format:

**CARE FLAGS - CAPTURED FOR {person_first_name}**
List each care flag we have captured from the assessment:
[care_flags] - translate each flag as follows:
- mild_cognitive_decline: {person_first_name} shows mild cognitive changes
- moderate_cognitive_decline: {person_first_name} has moderate cognitive decline identified
- severe_cognitive_risk: {person_first_name} has severe cognitive risks present
- moderate_safety_concern: Moderate safety concerns identified for {person_first_name}
- high_safety_concern: High safety concerns present for {person_first_name}
- falls_multiple: {person_first_name} has multiple falls reported
- moderate_mobility: {person_first_name} has moderate mobility limitations
- high_mobility_dependence: {person_first_name} has high mobility dependence
- moderate_adl_support: {person_first_name} needs moderate ADL support
- high_adl_dependence: {person_first_name} has high ADL dependence
- adl_support_high: {person_first_name} requires high ADL support
- depression_moderate: {person_first_name} has moderate depression identified
- anxiety_behavioral: {person_first_name} has anxiety/behavioral concerns
- isolation_social: {person_first_name} has social isolation concerns
- chronic_conditions: {person_first_name} has chronic conditions present
- medication_management: {person_first_name} needs medication management
- mobility_limited: {person_first_name} has mobility limitations
- behavioral_concerns: {person_first_name} has behavioral concerns noted
- safety_concerns: {person_first_name} needs safety supervision
- memory_support: {person_first_name} requires memory support
- memory_care_high_acuity: {person_first_name} has memory care high acuity needs
- caregiver_fatigue: Caregiver fatigue present in {person_possessive} care

**COST PLANNER FLAGS - HEALTH RELATED FOR {person_first_name}**
- VA Benefits Eligible: [va_benefits_eligible]
- Benefits Present: [benefits_present]
- RX Costs High: [rx_costs_high]
- Auto Present: [auto_present]

**{person_possessive} CHRONIC CONDITIONS DATA**
Show conditions from conditions registry if captured:
- Chronic Conditions List: [chronic_conditions_list] (if captured)
- Primary Medical Diagnoses: [primary_medical_diagnoses] (if captured)

**{person_possessive} FUNCTIONAL STATUS DATA**
Show actual functional data if captured:
- Current Care Hours Weekly: [current_care_hours_weekly] hours (if captured)
- Professional Services: [professional_services_current] (if captured)
- Medical Equipment Used: [medical_equipment_used] (if captured)
- Home Health Services: [home_health_services] (if captured)

**{person_possessive} MEDICATION & TREATMENT DATA**
- Current Medications Count: [current_medications_count] (if captured)
- Medication Compliance: [medication_compliance_level] (if captured)
- Pharmacy Management: [pharmacy_management_type] (if captured)
- Specialist Providers: [specialist_providers_seeing] (if captured)

**{person_possessive} BEHAVIORAL & MENTAL HEALTH DATA**
- Behavioral Concerns: [behavioral_concerns_present] (if captured)
- Depression Screening: [depression_screening_results] (if captured)
- Anxiety Status: [anxiety_concerns_present] (if captured)
- Sleep Issues: [sleep_disturbances_reported] (if captured)

**{person_possessive} CARE COORDINATION DATA**
- Provider Communication: [provider_communication_needs] (if captured)
- Care Plan Updates: [care_plan_update_frequency] (if captured)
- Family Caregiver Support: [family_caregiver_support_needs] (if captured)
- Emergency Response Plan: [emergency_response_plan_status] (if captured)

**DATA GAPS REQUIRING ADVISOR FOLLOW-UP FOR {person_first_name}**
List specific missing medical/care information about {person_first_name}:
- [List any categories showing "Not captured"]
- Recent medical assessments needed for {person_first_name}
- Care provider coordination required for {person_possessive} care team
- Family caregiver stress evaluation needed for {person_possessive} support network
- Emergency planning discussions required for {person_possessive} safety

Use the actual data from session state and care flags. Show "Not captured" for any category where we don't have information about {person_first_name}. Be specific about what medical and care data we have about {person_first_name} versus what requires further assessment.
"""

# Template 4: Financial Overview
FINANCIAL_OVERVIEW_TEMPLATE = """
Generate a comprehensive financial assessment report for {person_first_name} that shows EXACTLY what specific financial data we have captured in our system, organized by category. This is for advisor review to understand data completeness.

PERSONALIZATION STYLE RULES:
- Always refer to the care recipient by their first name: {person_first_name}
- Use possessive form when appropriate: {person_possessive}
- Example: "{person_first_name} has Social Security income of..." not "The client has Social Security income of..."
- Example: "{person_possessive} monthly care costs are estimated at..." not "The monthly care costs are estimated at..."

Show actual data categorization that we have captured, using the following format:

**{person_possessive} INCOME SOURCES (Monthly)**
List each specific income source we have captured with amounts:
- Social Security: $[amount] (if captured)
- Pension/Retirement: $[amount] (if captured) 
- 401k/403b Withdrawals: $[amount] (if captured)
- Roth IRA Distributions: $[amount] (if captured)
- Traditional IRA Withdrawals: $[amount] (if captured)
- Employment Income: $[amount] (if captured)
- Rental Income: $[amount] (if captured)
- Investment Income: $[amount] (if captured)
- Family Support: $[amount] (if captured)
- Other Income: $[amount] (if captured)
Total Monthly Income Available for {person_first_name}: $[total_monthly_income]

**{person_possessive} ASSET CATEGORIES**
List each specific asset type we have captured with values:
- Checking Accounts: $[amount] (if captured)
- Savings Accounts: $[amount] (if captured)
- Money Market Accounts: $[amount] (if captured)
- Certificates of Deposit: $[amount] (if captured)
- 401k/403b Accounts: $[amount] (if captured)
- Traditional IRA: $[amount] (if captured)
- Roth IRA: $[amount] (if captured)
- Brokerage/Investment Accounts: $[amount] (if captured)
- Primary Residence Value: $[amount] (if captured)
- Investment Real Estate: $[amount] (if captured)
- Life Insurance Cash Value: $[amount] (if captured)
- Personal Property/Vehicles: $[amount] (if captured)
Total Assets Available for {person_first_name}: $[total_assets]

**{person_possessive} DEBT AND LIABILITIES**
List each specific debt category we have captured:
- Mortgage Balance: $[amount] (if captured)
- Home Equity Line of Credit: $[amount] (if captured)
- Credit Card Debt: $[amount] (if captured)
- Auto Loans: $[amount] (if captured)
- Personal Loans: $[amount] (if captured)
- Medical Debt: $[amount] (if captured)
- Other Debt: $[amount] (if captured)
Total Debt Affecting {person_possessive} Care Planning: $[total_debt]

**{person_possessive} INSURANCE COVERAGE**
List each specific insurance type we have captured:
- Medicare Part A: [coverage status] (if captured)
- Medicare Part B: [coverage status] (if captured)
- Medicare Supplement: [coverage status] (if captured)
- Medicare Advantage: [coverage status] (if captured)
- Long-Term Care Insurance: [coverage status] (if captured)
- Life Insurance: [coverage amount] (if captured)
- Disability Insurance: [coverage status] (if captured)

**{person_possessive} BENEFITS AND ENTITLEMENTS**
List each specific benefit we have captured:
- Veterans Benefits Eligibility: [status] (if captured)
- Medicaid Qualification: [status] (if captured)
- Food Stamps/SNAP: [status] (if captured)
- Energy Assistance: [status] (if captured)
- Property Tax Exemptions: [status] (if captured)

**{person_possessive} CARE FUNDING PROJECTIONS**
Show specific calculations we have made for {person_first_name}:
- Assisted Living Monthly Cost: $[monthly_cost] (if calculated)
- Memory Care Monthly Cost: $[monthly_cost] (if calculated)
- Home Care Monthly Cost: $[monthly_cost] (if calculated)
- Years {person_first_name} Can Be Funded at Current Spending: [years] (if calculated)
- Medicaid Spend-Down Timeline for {person_first_name}: [timeline] (if calculated)

**DATA GAPS REQUIRING ADVISOR FOLLOW-UP FOR {person_first_name}**
List specific categories where we lack information about {person_possessive} financial situation:
- [List any income sources not captured]
- [List any asset categories not assessed]
- [List any insurance coverage not verified]
- [List any benefits not evaluated]
- [List any debt obligations not documented]

Use the actual data from session state and show "Not captured" for any category where we don't have information about {person_first_name}. Be specific about amounts, account types, and coverage details for {person_possessive} financial planning rather than using generic descriptions.
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
    
    # Cost Planner Basic
    monthly_cost=4200.0,
    household_income=3800.0,
    total_assets=280000.0,
    years_funded=5.5,
    va_benefits_eligible=True,
    assets_low=False,
    assets_high=False,
    benefits_present=True,
    rx_costs_high=False,
    transportation_needed=True,
    auto_present=False,
    family_travel_needed=False,
    
    # Detailed Income Breakdown
    social_security=1900.0,
    pension=800.0,
    retirement_401k=300.0,
    roth_ira=150.0,
    traditional_ira=0.0,
    employment=0.0,
    rental_income=0.0,
    investment_income=250.0,
    family_support=0.0,
    other_income=0.0,
    
    # Detailed Asset Breakdown
    checking_accounts=15000.0,
    savings_accounts=45000.0,
    money_market=25000.0,
    cds=30000.0,
    retirement_401k_balance=85000.0,
    traditional_ira_balance=0.0,
    roth_ira_balance=35000.0,
    brokerage=25000.0,
    home_value=180000.0,
    investment_real_estate=0.0,
    life_insurance_cash=8000.0,
    personal_property=12000.0,
    
    # Detailed Debt Breakdown
    mortgage_balance=0.0,
    heloc_balance=0.0,
    credit_card_debt=2500.0,
    auto_loans=0.0,
    personal_loans=0.0,
    medical_debt=0.0,
    other_debt=0.0,
    
    # Insurance Coverage
    medicare_a=True,
    medicare_b=True,
    medicare_supplement=True,
    medicare_advantage=False,
    ltc_insurance=False,
    life_insurance=25000.0,
    disability_insurance=False,
    
    # About Person Fields
    age_years=77,
    gender="Female",
    city="Baton Rouge",
    state="Louisiana",
    current_living_situation="Lives alone in own home",
    housing_type="Single-family house",
    housing_ownership_status="Owns home outright",
    lives_with_status="Lives alone",
    marital_status="Widowed",
    adult_children_proximity="Children live 30+ minutes away",
    primary_caregiver_relationship="Adult daughter",
    emergency_contact_available=True,
    family_support_strength="Moderate - family available but limited",
    social_isolation_level="Some isolation concerns",
    transportation_independence="Limited - family assistance needed",
    neighbor_support_available="Minimal neighbor contact",
    social_engagement_level="Reduced from previous",
    decision_maker_relationship="Self with family input",
    legal_documents_status="Basic will in place",
    financial_poa_status="Not captured",
    healthcare_poa_status="Not captured",
    advanced_directives_status="Not captured",
    
    # Housing Preferences Fields
    monthly_housing_costs=850.0,
    property_taxes_annual=2400.0,
    home_insurance_annual=1200.0,
    preferred_care_setting="Assisted living",
    aging_in_place_preference="Open to transition",
    move_timeline_months=6,
    move_readiness_level="Emotionally preparing",
    family_setting_agreement="Family supports assisted living",
    stay_near_current_location="Prefer to stay in Baton Rouge area",
    proximity_to_family_preference="Within 30 minutes of daughter",
    proximity_to_healthcare_preference="Access to current doctors",
    transportation_dependency="High - needs transportation assistance",
    community_features_priorities="Social activities and meal programs",
    accessibility_modifications_needed="Bathroom grab bars needed",
    safety_modifications_needed="Better lighting and non-slip surfaces",
    home_maintenance_challenges="Yard work and home repairs difficult",
    property_management_challenges="Managing utilities and maintenance",
    emotional_readiness_for_move="Gradually accepting need for change",
    financial_readiness_for_move="Assets sufficient for transition",
    family_support_for_transition="Strong family support for move",
    care_needs_urgency="Moderate - safety concerns increasing",
    
    # Medical & Care Fields
    cognitive_status_level="Mild cognitive changes",
    memory_changes_reported="Short-term memory concerns",
    decision_making_independence="Independent with complex decisions",
    orientation_status="Oriented to person, place, time",
    executive_function_level="Some difficulty with complex tasks",
    primary_medical_diagnoses="Hypertension, diabetes, arthritis",
    chronic_conditions_list="Type 2 diabetes, high blood pressure, osteoarthritis",
    recent_hospitalizations="None in past 12 months",
    mobility_status="Walks with cane for stability",
    fall_history_6months="One fall in bathroom 3 months ago",
    vision_impairment_level="Wears glasses, vision adequate",
    hearing_impairment_level="Mild hearing loss, no hearing aids",
    bathing_independence_level="Independent with grab bars",
    dressing_independence_level="Independent",
    toileting_independence_level="Independent",
    transferring_independence_level="Independent with assistance",
    continence_status="Continent",
    feeding_independence_level="Independent",
    medication_management_ability="Uses pill organizer, family oversight",
    meal_preparation_ability="Simple meals only",
    housekeeping_ability="Light housekeeping only",
    financial_management_ability="Family assists with complex finances",
    phone_use_ability="Independent",
    current_care_hours_weekly=6.0,
    professional_services_current="Housekeeper twice monthly",
    medical_equipment_used="Cane, shower chair",
    home_health_services="None currently",
    behavioral_concerns_present="Mild anxiety about safety",
    depression_screening_results="Not formally screened",
    anxiety_concerns_present="Anxiety about living alone",
    sleep_disturbances_reported="Occasional insomnia",
    current_medications_count=5,
    medication_compliance_level="Good with family oversight",
    pharmacy_management_type="Local pharmacy with delivery",
    specialist_providers_seeing="Endocrinologist, cardiologist",
    provider_communication_needs="Daughter attends appointments",
    care_plan_update_frequency="Quarterly with daughter",
    family_caregiver_support_needs="Respite care needed occasionally",
    emergency_response_plan_status="Medical alert system in place"
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