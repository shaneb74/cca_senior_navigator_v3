#!/usr/bin/env python3
"""
Create pre-configured John Test demo user profile.

This script creates a complete user profile for "John Test" with:
- Completed GCP (Guided Care Plan) with Assisted Living recommendation
- Completed Cost Planner with all financial assessments
- Care flags: diabetes, mild_cognitive, medication_complexity, mobility_limited, 
  medication_management, confusion_behavioral

Run this script with the Streamlit app STOPPED:
    python3 create_demo_john.py
"""

import json
import os
from pathlib import Path

# Demo John Test profile data - EXACT COPY from user's working session
data = {
    "uid": "demo_john_cost_planner",
    "created_at": 1760818352.985611,
    "last_updated": 1760818352.98561,
    # GCP v4 Complete Answers (leads to Assisted Living recommendation)
    "gcp_care_recommendation": {
        # About You section
        "age_range": "75_84",
        "living_situation": "alone",
        "isolation": "accessible",
        # Medication & Mobility section
        "meds_complexity": "complex",  # 3 points + flags
        "mobility": "walker",  # 1 point + moderate_mobility
        "falls": "one",  # 1 point + moderate_safety_concern
        "chronic_conditions": ["diabetes", "hypertension", "arthritis"],  # 3 points + chronic_present
        "additional_conditions": [],
        # Cognition & Mental Health section
        "memory_changes": "occasional",  # 1 point + mild_cognitive_decline
        "mood": "mostly_good",  # 1 point + moderate_risk
        "behaviors": ["confusion"],  # 1 point + moderate_safety_concern
        # Daily Living section
        "help_overall": "daily_help",  # 2 points + moderate_dependence
        "badls": ["bathing", "dressing", "transferring"],  # 3 points + moderate_dependence + veteran_aanda_risk
        "iadls": ["meal_prep", "med_management"],  # 2 points + moderate_dependence + veteran_aanda_risk
        "hours_per_day": "4-8h",  # 2 points
        "primary_support": "family"  # 1 point
        # Total score: 21 points → Assisted Living (17-24 range)
    },
    "mcip_contracts": {
        "care_recommendation": {
            "tier": "assisted_living",
            "tier_score": 21.0,
            "tier_rankings": [
                ["memory_care", 32.0],
                ["assisted_living", 21.0],
                ["in_home", 12.5],
                ["no_care_needed", 4.0],
                ["memory_care_high_acuity", 19.5]
            ],
            "confidence": 0.85,
            "flags": [
                {
                    "id": "chronic_present",
                    "label": "Chronic Conditions",
                    "description": "One or more chronic health conditions requiring management",
                    "tone": "info",
                    "priority": 2
                },
                {
                    "id": "moderate_mobility",
                    "label": "Mobility Assistance Needed",
                    "description": "Uses cane or walker, may need accessibility modifications",
                    "tone": "info",
                    "priority": 3
                },
                {
                    "id": "moderate_safety_concern",
                    "label": "Safety Monitoring Needed",
                    "description": "One fall or safety concerns that warrant attention",
                    "tone": "warning",
                    "priority": 2
                },
                {
                    "id": "mild_cognitive_decline",
                    "label": "Mild Memory Changes",
                    "description": "Occasional forgetfulness that may benefit from monitoring",
                    "tone": "info",
                    "priority": 3
                },
                {
                    "id": "moderate_dependence",
                    "label": "Regular Assistance Needed",
                    "description": "Needs regular help with daily activities",
                    "tone": "warning",
                    "priority": 2
                },
                {
                    "id": "veteran_aanda_risk",
                    "label": "Veteran A&A Eligible",
                    "description": "May qualify for VA Aid & Attendance benefits",
                    "tone": "info",
                    "priority": 3
                }
            ],
            "rationale": [
                "Based on 21 points, we recommend: Assisted Living",
                "Daily Living: 8 points",
                "  • Regular – needs daily assistance",
                "Medication Mobility: 8 points",
                "  • Complex – many meds or caregiver-managed",
                "Cognition Mental Health: 3 points"
            ],
            "suggested_next_product": "cost_planner_v2",
            "generated_at": 1729180800,
            "version": "v2025.10",
            "status": "completed",
            "last_updated": 1729180800,
            "needs_refresh": False
        },
        "financial_profile": {
            "total_monthly_income": 4500,
            "ss_monthly": 2200,
            "pension_monthly": 1800,
            "employment_monthly": 0,
            "other_income_monthly": 500,
            "total_liquid_assets": 285000,
            "checking_savings": 45000,
            "investment_accounts": 240000,
            "primary_residence_value": 650000,
            "primary_residence_has_debt": False,
            "has_ltc_insurance": False,
            "ltc_monthly_benefit": 0,
            "estimated_monthly_cost": 5940,
            "coverage_percentage": 75.8,
            "monthly_gap": 1440,
            "runway_months": 197.9,
            "created_at": 1729180800,
            "source": "cost_planner_v2"
        },
        "journey": {
            "current_hub": "financial",
            "completed_products": ["gcp_v4", "cost_planner_v2"],
            "unlocked_products": ["gcp_v4", "cost_planner_v2", "pfma_v3"],
            "recommended_next": "pfma_v3"
        }
    },
    "tiles": {
        "gcp_v4": {
            "status": "completed",
            "progress": 100.0,
            "last_step": 5,
            "last_updated": 1729180800,
            "saved_state": {
                "progress": 100.0,
                "status": "completed",
                "age_range": "75_84",
                "living_situation": "alone",
                "isolation": "accessible",
                "meds_complexity": "complex",
                "mobility": "walker",
                "falls": "one",
                "chronic_conditions": ["diabetes", "hypertension", "arthritis"],
                "memory_changes": "occasional",
                "mood": "mostly_good",
                "behaviors": ["confusion"],
                "help_overall": "daily_help",
                "badls": ["bathing", "dressing", "transferring"],
                "iadls": ["meal_prep", "med_management"],
                "hours_per_day": "4-8h",
                "primary_support": "family"
            }
        },
        "cost_planner_v2": {
            "status": "completed",
            "progress": 100.0,
            "last_updated": 1729180800
        }
    },
    "product_tiles_v2": {
        "gcp_v4": {
            "status": "completed",
            "progress": 100.0,
            "badge": "complete"
        },
        "cost_planner_v2": {
            "status": "completed",
            "progress": 100.0,
            "badge": "complete"
        },
        "pfma_v3": {
            "status": "unlocked",
            "progress": 0.0,
            "badge": "ready"
        }
    },
    "preferences": {
        "theme": "light",
        "notifications_enabled": True
    },
    "auth": {
        "is_authenticated": True,
        "user_id": "demo_john_cost_planner",
        "name": "John Test",
        "email": "john@demo.test"
    },
    "flags": {
        "cost_planner_v2_enabled": True,
        "gcp_v4_enabled": True
    },
    "cost_v2_step": "exit",
    "cost_v2_guest_mode": False,
    "cost_v2_triage": {
        "is_on_medicaid": False,
        "is_veteran": True,
        "is_homeowner": True
    },
    "cost_v2_qualifiers": {
        "is_on_medicaid": False,
        "is_veteran": True,
        "is_homeowner": True
    },
    "cost_v2_current_module": "medicaid_navigation",
    "cost_v2_modules": {
        "income": {
            "status": "completed",
            "progress": 100,
            "data": {
                "ss_monthly": 2200,
                "pension_monthly": 1800,
                "employment_status": "retired",
                "employment_monthly": 0,
                "has_partner": "no_partner",
                "shared_finance_notes": "",
                "partner_income_monthly": 0,
                "retirement_withdrawals_monthly": 0,
                "rental_income_monthly": 0,
                "ltc_insurance_monthly": 0,
                "family_support_monthly": 0,
                "periodic_income_avg_monthly": 500,
                "periodic_income_frequency": "quarterly",
                "periodic_income_notes": "Small dividend payments from investment portfolio",
                "other_income_monthly": 0,
                "total_monthly_income": 4500
            }
        },
        "assets": {
            "status": "completed",
            "progress": 100,
            "data": {
                "checking_savings": 45000,
                "investment_accounts": 240000,
                "primary_residence_value": 650000,
                "primary_residence_has_debt": False,
                "primary_residence_mortgage_balance": 0,
                "primary_residence_liquidity_window": "6_to_12_months",
                "home_sale_interest": False,
                "other_real_estate": 0,
                "other_real_estate_has_debt": False,
                "other_real_estate_debt_balance": 0,
                "other_resources": 0,
                "asset_has_partner": "no_partner",
                "asset_legal_restrictions": "",
                "liquid_assets_has_loan": False,
                "liquid_assets_loan_balance": 0,
                "asset_secured_loans": 0,
                "asset_other_debts": 0,
                "total_liquid_assets": 285000,
                "total_illiquid_assets": 650000
            }
        },
        "va_benefits": {
            "status": "completed",
            "progress": 100,
            "data": {
                "is_veteran": True,
                "service_branch": "Navy",
                "service_start_year": 1966,
                "service_end_year": 1970,
                "disability_rating": 30,
                "receives_va_pension": False,
                "va_pension_monthly": 0,
                "receives_aid_attendance": False,
                "aid_attendance_monthly": 0,
                "interested_in_benefits": True
            }
        },
        "health_insurance": {
            "status": "completed",
            "progress": 100,
            "data": {
                "primary_coverage": "medicare",
                "has_medicare": True,
                "medicare_part_a": True,
                "medicare_part_b": True,
                "medicare_part_d": True,
                "has_medigap": True,
                "medigap_plan": "Plan G",
                "medigap_premium_monthly": 185,
                "has_medicare_advantage": False,
                "medicare_advantage_premium_monthly": 0,
                "has_medicaid": False,
                "medicaid_type": "",
                "has_private_insurance": False,
                "private_insurance_premium_monthly": 0,
                "total_health_insurance_cost_monthly": 185
            }
        },
        "life_insurance": {
            "status": "completed",
            "progress": 100,
            "data": {
                "has_life_insurance": True,
                "policy_type": "term",
                "death_benefit": 100000,
                "cash_value": 0,
                "monthly_premium": 125,
                "has_ltc_rider": False,
                "ltc_rider_monthly_benefit": 0,
                "policy_notes": "Term policy expires in 3 years"
            }
        },
        "medicaid_navigation": {
            "status": "completed",
            "progress": 100,
            "data": {
                "currently_on_medicaid": False,
                "interested_in_medicaid": True,
                "medicaid_planning_stage": "researching",
                "has_consulted_elder_law": False,
                "spend_down_concerns": True,
                "asset_protection_interest": True,
                "medicaid_notes": "Interested in learning about eligibility and planning options"
            }
        }
    },
    "cost_v2_income": {
        "ss_monthly": 2200,
        "pension_monthly": 1800,
        "employment_status": "retired",
        "total_monthly_income": 4500
    },
    "cost_v2_assets": {
        "checking_savings": 45000,
        "investment_accounts": 240000,
        "primary_residence_value": 650000,
        "total_liquid_assets": 285000
    },
    "cost_v2_va_benefits": {
        "is_veteran": True,
        "service_branch": "Navy",
        "disability_rating": 30,
        "interested_in_benefits": True
    },
    "cost_v2_health_insurance": {
        "primary_coverage": "medicare",
        "has_medicare": True,
        "has_medigap": True,
        "medigap_premium_monthly": 185
    },
    "cost_v2_life_insurance": {
        "has_life_insurance": True,
        "policy_type": "term",
        "monthly_premium": 125
    },
    "cost_v2_medicaid_navigation": {
        "currently_on_medicaid": False,
        "interested_in_medicaid": True
    },
    "cost_v2_advisor_notes": {
        "care_concerns": "Managing diabetes, medication complexity, and mild cognitive decline. Needs assistance with mobility and daily activities.",
        "financial_goals": "Maintain independence as long as possible while ensuring care needs are met. Interested in Medicaid planning for asset protection.",
        "timeline": "Evaluating assisted living options within 3-6 months",
        "additional_notes": "Family lives out of state. Wants to stay in Bay Area near medical providers."
    },
    "cost_v2_schedule_advisor": {
        "requested": False,
        "preferred_contact": "email",
        "preferred_time": "morning",
        "notes": ""
    },
    "cost_v2_quick_estimate": {
        "estimate": {
            "monthly_base": 5400,
            "monthly_adjusted": 5940,
            "annual": 71280,
            "three_year": 213840,
            "five_year": 356400,
            "multiplier": 1.1,
            "region_name": "Seattle, WA",
            "care_tier": "assisted_living",
            "breakdown": {
                "base_cost": 5400,
                "regional_adjustment": 540,
                "severe_cognitive_addon": 0,
                "mobility_transferring_addon": 0,
                "high_adl_support_addon": 0,
                "medication_management_addon": 0,
                "behavioral_support_addon": 0,
                "total": 5940
            }
        },
        "care_tier": "assisted_living",
        "zip_code": "98101"
    },
    "cost_planner_v2_published": True,
    "cost_planner_v2_complete": True
}

def main():
    # Ensure directory exists
    users_dir = Path("data/users")
    users_dir.mkdir(parents=True, exist_ok=True)
    
    # File path
    file_path = users_dir / "demo_john_cost_planner.json"
    
    # Write file
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("✅ John Test demo profile created successfully!")
        print(f"\n📄 File: {file_path}")
        print(f"👤 UID: {data['uid']}")
        print(f"📍 Location: {data['profile']['location']} (ZIP: {data['profile']['zip_code']})")
        print(f"\n🏥 Care Recommendation: {data['mcip_contracts']['care_recommendation']['tier'].upper().replace('_', ' ')}")
        print(f"   Score: {data['mcip_contracts']['care_recommendation']['tier_score']} points")
        print(f"   Confidence: {data['mcip_contracts']['care_recommendation']['confidence']*100:.0f}%")
        print(f"\n🏷️  Care Flags ({len(data['mcip_contracts']['care_recommendation']['flags'])}):")
        for flag in data['mcip_contracts']['care_recommendation']['flags']:
            print(f"   - {flag['label']}")
        print(f"\n� GCP Assessment Complete:")
        print(f"   Age: {data['gcp_care_recommendation']['age_range']}")
        print(f"   Mobility: {data['gcp_care_recommendation']['mobility']}")
        print(f"   Memory: {data['gcp_care_recommendation']['memory_changes']}")
        print(f"   ADL Support: {', '.join(data['gcp_care_recommendation']['badls'])}")
        print(f"   IADL Support: {', '.join(data['gcp_care_recommendation']['iadls'])}")
        print(f"\n�💰 Financial Summary:")
        print(f"   Monthly Income: ${data['cost_v2_income']['total_monthly_income']:,}")
        print(f"   Liquid Assets: ${data['cost_v2_assets']['total_liquid_assets']:,}")
        print(f"   Veteran: {data['cost_v2_va_benefits']['is_veteran']} (Navy, 30% disability)")
        print(f"   Estimated Care Cost: ${data['cost_v2_quick_estimate']['estimate']['monthly_adjusted']:,}/month ({data['cost_v2_quick_estimate']['estimate']['region_name']})")
        print(f"   Monthly Gap: ${data['mcip_contracts']['financial_profile']['monthly_gap']:,}")
        print(f"   Runway: {data['mcip_contracts']['financial_profile']['runway_months']:.1f} months")
        print(f"\n✅ Both GCP and Cost Planner completed and published!")
        print(f"🎯 Next Step: PFMA (Personal Financial Management Assistant) ready")
        print(f"\n🚀 To use: Login as 'John Test' in the app")
        
    except Exception as e:
        print(f"❌ Error creating file: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
