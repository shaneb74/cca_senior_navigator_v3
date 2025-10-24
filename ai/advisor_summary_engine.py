"""
Advisor Summary LLM Engine

Generates natural-language narratives for internal advisor dashboards using 
structured data from GCP, Cost Planner, and session state.

This module creates four narrative "drawers" for advisor stakeholders:
1. About the Person - Introduction and living situation
2. Housing Preferences - Preferred care setting and timeline  
3. Medical & Care Information - Care needs and coordination requirements
4. Financial Overview - Budget and funding timeline

Target audience: Internal business and advisor stakeholders
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Mock streamlit for testing
    class MockStreamlit:
        class session_state:
            @classmethod
            def get(cls, key, default=None):
                return default
    st = MockStreamlit()

try:
    from ai.llm_client import LLMClient
    LLM_CLIENT_AVAILABLE = True
except ImportError:
    LLM_CLIENT_AVAILABLE = False
    # Mock LLMClient for testing
    class MockLLMClient:
        def generate_completion(self, prompt, max_tokens=200, temperature=0.7):
            return "Mock LLM response for testing purposes."
    LLMClient = MockLLMClient

from ai.advisor_summary_templates import (
    ABOUT_PERSON_TEMPLATE,
    HOUSING_PREFERENCES_TEMPLATE, 
    MEDICAL_CARE_TEMPLATE,
    FINANCIAL_OVERVIEW_TEMPLATE,
    AdvisorSummaryContext
)


class AdvisorSummaryEngine:
    """LLM engine for generating advisor summary narratives."""
    
    @staticmethod
    def build_advisor_context_from_session() -> Optional[AdvisorSummaryContext]:
        """
        Build AdvisorSummaryContext from current Streamlit session state.
        
        Returns:
            AdvisorSummaryContext object or None if insufficient data
        """
        try:
            # Get profile context
            person_a_name = st.session_state.get("person_a_name", "the care recipient")
            person_a_age_range = st.session_state.get("person_a_age_range", "their eighties")
            relationship_type = st.session_state.get("relationship_type", "family member")
            geo_zip = st.session_state.get("geo_zip", "their local area")
            
            # Support and access flags
            support_network_low = st.session_state.get("support_network_low", False)
            low_access = st.session_state.get("low_access", False) 
            home_carry = st.session_state.get("home_carry", True)
            dual_household = st.session_state.get("dual_household", False)
            
            # GCP data
            care_recommendation = st.session_state.get("care_recommendation", {})
            recommended_tier = care_recommendation.get("tier", "assisted_living")
            
            # Get allowed tiers from GCP results
            gcp_results = st.session_state.get("gcp_results", {})
            allowed_tiers = gcp_results.get("allowed_tiers", [recommended_tier])
            
            move_timeline = st.session_state.get("move_timeline", "flexible")
            room_type = st.session_state.get("room_type", "one_bedroom")
            
            # Care flags from various sources
            care_flags = []
            
            # Add flags from care_recommendation
            if isinstance(care_recommendation, dict):
                tier_flags = care_recommendation.get("flags", [])
                if isinstance(tier_flags, list):
                    care_flags.extend(tier_flags)
            
            # Add flags from session state flag manager
            flag_manager_flags = st.session_state.get("flag_manager_flags", {})
            for flag_name, flag_value in flag_manager_flags.items():
                if flag_value and flag_name not in care_flags:
                    care_flags.append(flag_name)
            
            # Add common care flags from session state
            common_flags = [
                "moderate_cognitive_decline", "severe_cognitive_decline",
                "mobility_limited", "falls_risk", "adl_support_high",
                "chronic_conditions", "medication_management", 
                "behavioral_concerns", "safety_concerns", "memory_support",
                "memory_care_high_acuity", "caregiver_fatigue"
            ]
            
            for flag in common_flags:
                if st.session_state.get(flag, False) and flag not in care_flags:
                    care_flags.append(flag)
            
            # Cost Planner data
            financial_data = st.session_state.get("financial_assessment_complete", {})
            cost_data = financial_data.get("cost_summary", {})
            
            monthly_cost = cost_data.get("monthly_total", 0.0)
            household_income = financial_data.get("household_income", 0.0)
            total_assets = financial_data.get("total_assets", 0.0)
            
            # Calculate years funded
            years_funded = 0.0
            if monthly_cost > 0 and total_assets > 0:
                years_funded = total_assets / (monthly_cost * 12)
            
            # Benefits and asset flags
            va_benefits_eligible = st.session_state.get("va_benefits_eligible", False)
            assets_low = st.session_state.get("assets_low", False)
            assets_high = st.session_state.get("assets_high", False) 
            benefits_present = st.session_state.get("benefits_present", False)
            rx_costs_high = st.session_state.get("rx_costs_high", False)
            transportation_needed = st.session_state.get("transportation_needed", False)
            auto_present = st.session_state.get("auto_present", True)
            family_travel_needed = st.session_state.get("family_travel_needed", False)
            
            return AdvisorSummaryContext(
                # Profile Context
                person_a_name=person_a_name,
                person_a_age_range=person_a_age_range,
                relationship_type=relationship_type,
                geo_zip=geo_zip,
                support_network_low=support_network_low,
                low_access=low_access,
                home_carry=home_carry,
                dual_household=dual_household,
                
                # Guided Care Plan
                recommended_tier=recommended_tier,
                allowed_tiers=allowed_tiers,
                move_timeline=move_timeline,
                room_type=room_type,
                care_flags=care_flags,
                
                # Cost Planner
                monthly_cost=monthly_cost,
                household_income=household_income,
                total_assets=total_assets,
                years_funded=years_funded,
                va_benefits_eligible=va_benefits_eligible,
                assets_low=assets_low,
                assets_high=assets_high,
                benefits_present=benefits_present,
                rx_costs_high=rx_costs_high,
                transportation_needed=transportation_needed,
                auto_present=auto_present,
                family_travel_needed=family_travel_needed
            )
            
        except Exception as e:
            print(f"[ADVISOR_SUMMARY] Failed to build context: {e}")
            return None
    
    @staticmethod
    def generate_drawer_narrative(
        drawer_type: str, 
        context: AdvisorSummaryContext
    ) -> Optional[str]:
        """
        Generate a single drawer narrative using LLM.
        
        Args:
            drawer_type: One of 'about_person', 'housing_preferences', 
                        'medical_care', 'financial_overview'
            context: AdvisorSummaryContext with structured data
            
        Returns:
            Generated narrative paragraph or None if generation fails
        """
        try:
            # Get appropriate template
            templates = {
                "about_person": ABOUT_PERSON_TEMPLATE,
                "housing_preferences": HOUSING_PREFERENCES_TEMPLATE,
                "medical_care": MEDICAL_CARE_TEMPLATE, 
                "financial_overview": FINANCIAL_OVERVIEW_TEMPLATE
            }
            
            template = templates.get(drawer_type)
            if not template:
                print(f"[ADVISOR_SUMMARY] Unknown drawer type: {drawer_type}")
                return None
            
            # Build context variables for template substitution
            context_vars = asdict(context)
            
            # Format care flags as readable list
            if context_vars["care_flags"]:
                context_vars["care_flags"] = ", ".join(context_vars["care_flags"])
            else:
                context_vars["care_flags"] = "none identified"
            
            # Format monetary values
            context_vars["monthly_cost"] = f"{context_vars['monthly_cost']:,.0f}"
            context_vars["household_income"] = f"{context_vars['household_income']:,.0f}"
            context_vars["total_assets"] = f"{context_vars['total_assets']:,.0f}"
            context_vars["years_funded"] = f"{context_vars['years_funded']:.1f}"
            
            # Create the full prompt with context injection
            prompt = f"""
{template}

Context Data:
{chr(10).join(f'- {key}: {value}' for key, value in context_vars.items())}

Generate a natural-language paragraph following the template guidelines above.
Use warm, empathetic, factual tone suitable for internal advisor reports.
Length: 80-120 words.
Return only the paragraph text, no additional formatting or explanation.
"""
            
            # Generate using LLM
            client = LLMClient()
            response = client.generate_completion(
                prompt=prompt,
                max_tokens=200,
                temperature=0.7
            )
            
            if response and response.strip():
                return response.strip()
            else:
                print(f"[ADVISOR_SUMMARY] Empty response for {drawer_type}")
                return None
                
        except Exception as e:
            print(f"[ADVISOR_SUMMARY] Generation failed for {drawer_type}: {e}")
            return None
    
    @staticmethod
    def generate_all_drawers(context: Optional[AdvisorSummaryContext] = None) -> Dict[str, str]:
        """
        Generate all four advisor summary drawers.
        
        Args:
            context: Optional pre-built context, otherwise built from session
            
        Returns:
            Dictionary with drawer names as keys and generated narratives as values
        """
        if context is None:
            context = AdvisorSummaryEngine.build_advisor_context_from_session()
        
        if not context:
            return {
                "about_person": "Insufficient profile data available.",
                "housing_preferences": "Housing preferences not yet captured.",
                "medical_care": "Care assessment pending completion.",
                "financial_overview": "Financial information not available."
            }
        
        results = {}
        drawer_types = ["about_person", "housing_preferences", "medical_care", "financial_overview"]
        
        for drawer_type in drawer_types:
            narrative = AdvisorSummaryEngine.generate_drawer_narrative(drawer_type, context)
            
            if narrative:
                results[drawer_type] = narrative
            else:
                # Fallback messages
                fallbacks = {
                    "about_person": f"This plan is for {context.person_a_name}, who is in their {context.person_a_age_range}.",
                    "housing_preferences": f"{context.person_a_name} is exploring {context.recommended_tier.replace('_', ' ')} options.",
                    "medical_care": f"{context.person_a_name}'s care needs are being assessed.",
                    "financial_overview": f"Financial planning is in progress for {context.person_a_name}."
                }
                results[drawer_type] = fallbacks[drawer_type]
        
        return results


def test_advisor_summary_generation():
    """Test function for advisor summary generation."""
    from ai.advisor_summary_templates import EXAMPLE_CONTEXT
    
    print("=== Testing Advisor Summary Generation ===\n")
    
    # Test with example context
    engine = AdvisorSummaryEngine()
    drawers = engine.generate_all_drawers(EXAMPLE_CONTEXT)
    
    for drawer_name, narrative in drawers.items():
        print(f"## {drawer_name.replace('_', ' ').title()}")
        print(narrative)
        print("\n" + "-"*50 + "\n")


if __name__ == "__main__":
    test_advisor_summary_generation()