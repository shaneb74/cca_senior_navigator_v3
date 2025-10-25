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
from core.name_utils import first_name, possessive


class AdvisorSummaryEngine:
    """LLM engine for generating advisor summary narratives."""
    
    @staticmethod
    def _personalize_template(template: str, person_name: str) -> str:
        """
        Process personalization tokens in LLM templates.
        
        Args:
            template: Template string with personalization tokens
            person_name: Full name of the care recipient
            
        Returns:
            Template with personalization tokens replaced
        """
        if not person_name or person_name == "the care recipient":
            # Fallback to generic language when no name available
            person_first_name = "the care recipient"
            person_possessive = "their"
        else:
            person_first_name = first_name(person_name)
            person_possessive = possessive(person_first_name)
        
        # Replace personalization tokens in template
        personalized_template = template.replace("{person_first_name}", person_first_name)
        personalized_template = personalized_template.replace("{person_possessive}", person_possessive)
        
        return personalized_template
    
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
            
            # Cost Planner data with detailed breakdown
            financial_data = st.session_state.get("financial_assessment_complete", {})
            cost_data = financial_data.get("cost_summary", {})
            
            # Extract detailed income breakdown
            income_breakdown = financial_data.get("income_breakdown", {})
            social_security = income_breakdown.get("social_security", 0.0)
            pension = income_breakdown.get("pension", 0.0)
            retirement_401k = income_breakdown.get("401k_withdrawals", 0.0)
            roth_ira = income_breakdown.get("roth_distributions", 0.0)
            traditional_ira = income_breakdown.get("traditional_ira", 0.0)
            employment = income_breakdown.get("employment", 0.0)
            rental_income = income_breakdown.get("rental", 0.0)
            investment_income = income_breakdown.get("investment", 0.0)
            family_support = income_breakdown.get("family_support", 0.0)
            other_income = income_breakdown.get("other", 0.0)
            
            monthly_cost = cost_data.get("monthly_total", 0.0)
            household_income = financial_data.get("household_income", 0.0)
            
            # Extract detailed asset breakdown
            asset_breakdown = financial_data.get("asset_breakdown", {})
            checking_accounts = asset_breakdown.get("checking", 0.0)
            savings_accounts = asset_breakdown.get("savings", 0.0)
            money_market = asset_breakdown.get("money_market", 0.0)
            cds = asset_breakdown.get("certificates_deposit", 0.0)
            retirement_401k_balance = asset_breakdown.get("401k_balance", 0.0)
            traditional_ira_balance = asset_breakdown.get("traditional_ira_balance", 0.0)
            roth_ira_balance = asset_breakdown.get("roth_ira_balance", 0.0)
            brokerage = asset_breakdown.get("brokerage", 0.0)
            home_value = asset_breakdown.get("primary_residence", 0.0)
            investment_real_estate = asset_breakdown.get("investment_property", 0.0)
            life_insurance_cash = asset_breakdown.get("life_insurance_cash", 0.0)
            personal_property = asset_breakdown.get("personal_property", 0.0)
            
            total_assets = financial_data.get("total_assets", 0.0)
            
            # Extract debt breakdown
            debt_breakdown = financial_data.get("debt_breakdown", {})
            mortgage_balance = debt_breakdown.get("mortgage", 0.0)
            heloc_balance = debt_breakdown.get("heloc", 0.0)
            credit_card_debt = debt_breakdown.get("credit_cards", 0.0)
            auto_loans = debt_breakdown.get("auto_loans", 0.0)
            personal_loans = debt_breakdown.get("personal_loans", 0.0)
            medical_debt = debt_breakdown.get("medical_debt", 0.0)
            other_debt = debt_breakdown.get("other_debt", 0.0)
            
            # Extract insurance coverage
            insurance_data = financial_data.get("insurance_coverage", {})
            medicare_a = insurance_data.get("medicare_part_a", False)
            medicare_b = insurance_data.get("medicare_part_b", False)
            medicare_supplement = insurance_data.get("medicare_supplement", False)
            medicare_advantage = insurance_data.get("medicare_advantage", False)
            ltc_insurance = insurance_data.get("long_term_care", False)
            life_insurance = insurance_data.get("life_insurance_amount", 0.0)
            disability_insurance = insurance_data.get("disability", False)
            
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
                
                # Cost Planner Basic
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
                family_travel_needed=family_travel_needed,
                
                # Detailed Income Breakdown
                social_security=social_security,
                pension=pension,
                retirement_401k=retirement_401k,
                roth_ira=roth_ira,
                traditional_ira=traditional_ira,
                employment=employment,
                rental_income=rental_income,
                investment_income=investment_income,
                family_support=family_support,
                other_income=other_income,
                
                # Detailed Asset Breakdown
                checking_accounts=checking_accounts,
                savings_accounts=savings_accounts,
                money_market=money_market,
                cds=cds,
                retirement_401k_balance=retirement_401k_balance,
                traditional_ira_balance=traditional_ira_balance,
                roth_ira_balance=roth_ira_balance,
                brokerage=brokerage,
                home_value=home_value,
                investment_real_estate=investment_real_estate,
                life_insurance_cash=life_insurance_cash,
                personal_property=personal_property,
                
                # Detailed Debt Breakdown
                mortgage_balance=mortgage_balance,
                heloc_balance=heloc_balance,
                credit_card_debt=credit_card_debt,
                auto_loans=auto_loans,
                personal_loans=personal_loans,
                medical_debt=medical_debt,
                other_debt=other_debt,
                
                # Insurance Coverage
                medicare_a=medicare_a,
                medicare_b=medicare_b,
                medicare_supplement=medicare_supplement,
                medicare_advantage=medicare_advantage,
                ltc_insurance=ltc_insurance,
                life_insurance=life_insurance,
                disability_insurance=disability_insurance
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
            
            # Personalize the template with name context
            personalized_template = AdvisorSummaryEngine._personalize_template(
                template, context.person_a_name
            )
            
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
            
            # Create system and user prompts for LLM API
            system_prompt = f"""You are an expert geriatric care advisor generating comprehensive assessment reports for professional review. 
Generate natural-language paragraphs following template guidelines with warm, empathetic, factual tone suitable for internal advisor reports. 
Focus on specific captured data rather than generic descriptions. Return only the paragraph text, no additional formatting or explanation.

PERSONALIZATION STYLE RULES:
- Always refer to the care recipient by their first name: {first_name(context.person_a_name) if context.person_a_name != "the care recipient" else "the care recipient"}
- Use possessive form when appropriate: {possessive(first_name(context.person_a_name)) if context.person_a_name != "the care recipient" else "their"}
- Avoid generic "the client" or "this person" language
- Example: "{first_name(context.person_a_name) if context.person_a_name != "the care recipient" else "The care recipient"} has Medicare coverage..." not "The client has Medicare coverage..."
"""
            
            user_prompt = f"""
{personalized_template}

Context Data:
{chr(10).join(f'- {key}: {value}' for key, value in context_vars.items())}

Generate a comprehensive assessment paragraph following the template guidelines above using the specific context data provided.
"""
            
            # Generate using LLM
            client = LLMClient()
            response = client.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt
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