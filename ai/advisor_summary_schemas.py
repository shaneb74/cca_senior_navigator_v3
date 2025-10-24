"""
Pydantic schemas for Advisor Summary LLM outputs

These schemas ensure structured, consistent output from the LLM 
for advisor summary drawer narratives.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class AdvisorDrawerNarrative(BaseModel):
    """Single advisor summary drawer narrative."""
    
    drawer_type: str = Field(
        description="Type of drawer: about_person, housing_preferences, medical_care, or financial_overview"
    )
    
    narrative: str = Field(
        description="Natural language narrative paragraph (80-120 words)",
        min_length=50,
        max_length=200
    )
    
    word_count: int = Field(
        description="Word count of the narrative"
    )
    
    confidence: float = Field(
        description="Confidence score for narrative quality (0.0-1.0)",
        ge=0.0,
        le=1.0
    )


class AdvisorSummaryResponse(BaseModel):
    """Complete advisor summary with all four drawers."""
    
    about_person: AdvisorDrawerNarrative = Field(
        description="Introduction and living situation narrative"
    )
    
    housing_preferences: AdvisorDrawerNarrative = Field(
        description="Preferred care setting and timeline narrative"
    )
    
    medical_care: AdvisorDrawerNarrative = Field(
        description="Care needs and coordination narrative"
    )
    
    financial_overview: AdvisorDrawerNarrative = Field(
        description="Budget and funding timeline narrative"
    )
    
    person_name: str = Field(
        description="Name of the care recipient"
    )
    
    generated_at: str = Field(
        description="ISO timestamp of generation"
    )
    
    data_completeness: float = Field(
        description="Completeness score of input data (0.0-1.0)",
        ge=0.0,
        le=1.0
    )


class AdvisorSummaryRequest(BaseModel):
    """Request schema for advisor summary generation."""
    
    # Profile Context
    person_a_name: str = Field(description="Care recipient's first name")
    person_a_age_range: str = Field(description="Age range (e.g., 'late seventies')")
    relationship_type: str = Field(description="Relationship of planner to recipient")
    geo_zip: str = Field(description="ZIP code or geographic area")
    support_network_low: bool = Field(description="Limited family support nearby")
    low_access: bool = Field(description="Challenges accessing services")
    home_carry: bool = Field(description="Plans to keep current home")
    dual_household: bool = Field(description="Lives with family/partner")
    
    # Guided Care Plan
    recommended_tier: str = Field(description="Recommended care tier")
    allowed_tiers: List[str] = Field(description="All eligible care tiers")
    move_timeline: str = Field(description="Preferred move timeline")
    room_type: str = Field(description="Preferred room/apartment type")
    care_flags: List[str] = Field(description="List of care requirement flags")
    
    # Cost Planner
    monthly_cost: float = Field(description="Projected monthly care cost")
    household_income: float = Field(description="Monthly household income")
    total_assets: float = Field(description="Total available assets")
    years_funded: float = Field(description="Estimated years of funding")
    va_benefits_eligible: bool = Field(description="Eligible for VA benefits")
    assets_low: bool = Field(description="Limited asset availability")
    assets_high: bool = Field(description="Substantial asset availability")
    benefits_present: bool = Field(description="Current benefits in place")
    rx_costs_high: bool = Field(description="High medication costs")
    transportation_needed: bool = Field(description="Transportation assistance needed")
    auto_present: bool = Field(description="Has personal vehicle")
    family_travel_needed: bool = Field(description="Family travel required for visits")


class AdvisorSummaryError(BaseModel):
    """Error response for advisor summary generation."""
    
    error_type: str = Field(description="Type of error encountered")
    error_message: str = Field(description="Human-readable error description")
    failed_drawers: List[str] = Field(description="Drawers that failed to generate")
    fallback_used: bool = Field(description="Whether fallback content was used")
    retry_suggested: bool = Field(description="Whether retry is recommended")


# Example data for testing schemas
EXAMPLE_REQUEST = AdvisorSummaryRequest(
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
    care_flags=["moderate_cognitive_decline", "mobility_limited", "medication_management"],
    
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


def validate_advisor_summary_schemas():
    """Test function to validate the schemas work correctly."""
    from datetime import datetime
    
    print("=== Testing Advisor Summary Schemas ===\n")
    
    # Test request schema
    print("✅ AdvisorSummaryRequest Schema:")
    print(f"Person: {EXAMPLE_REQUEST.person_a_name}, {EXAMPLE_REQUEST.person_a_age_range}")
    print(f"Recommended Care: {EXAMPLE_REQUEST.recommended_tier}")
    print(f"Care Flags: {', '.join(EXAMPLE_REQUEST.care_flags)}")
    print(f"Monthly Cost: ${EXAMPLE_REQUEST.monthly_cost:,.0f}")
    print(f"Years Funded: {EXAMPLE_REQUEST.years_funded}")
    
    # Test drawer narrative schema
    print("\n✅ AdvisorDrawerNarrative Schema:")
    example_narrative = AdvisorDrawerNarrative(
        drawer_type="about_person",
        narrative="This plan is for Margaret, who is in her late seventies and currently lives alone in the Baton Rouge area. She has limited access to nearby family and occasionally relies on neighbors for support.",
        word_count=35,
        confidence=0.9
    )
    print(f"Drawer Type: {example_narrative.drawer_type}")
    print(f"Word Count: {example_narrative.word_count}")
    print(f"Confidence: {example_narrative.confidence}")
    print(f"Narrative: {example_narrative.narrative}")
    
    # Test complete response schema  
    print("\n✅ AdvisorSummaryResponse Schema:")
    example_response = AdvisorSummaryResponse(
        about_person=example_narrative,
        housing_preferences=AdvisorDrawerNarrative(
            drawer_type="housing_preferences",
            narrative="Margaret has expressed interest in Assisted Living communities that provide independence and support with daily activities.",
            word_count=20,
            confidence=0.85
        ),
        medical_care=AdvisorDrawerNarrative(
            drawer_type="medical_care", 
            narrative="Margaret experiences moderate memory changes and mild mobility challenges that affect her daily stability.",
            word_count=16,
            confidence=0.9
        ),
        financial_overview=AdvisorDrawerNarrative(
            drawer_type="financial_overview",
            narrative="Margaret's projected monthly budget for care is approximately $4,200, supported by Social Security and savings.",
            word_count=17,
            confidence=0.8
        ),
        person_name="Margaret",
        generated_at=datetime.now().isoformat(),
        data_completeness=0.95
    )
    
    print(f"Person: {example_response.person_name}")
    print(f"Generated: {example_response.generated_at}")
    print(f"Data Completeness: {example_response.data_completeness}")
    print(f"All Drawers: {len([example_response.about_person, example_response.housing_preferences, example_response.medical_care, example_response.financial_overview])}")
    
    print("\n✅ All schemas validated successfully!")
    
    return example_response


if __name__ == "__main__":
    validate_advisor_summary_schemas()