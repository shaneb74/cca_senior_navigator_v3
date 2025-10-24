#!/usr/bin/env python3
"""
Create Demo Mary Memory Care Profile

Uses specified requirements to generate pre-configured demo user with complete
GCP and Cost Planner data for high-acuity memory care scenario.

This profile contains:
- Memory Care High Acuity recommendation (32 points, 95 percent confidence)
- 8 care flags including severe cognitive decline, wandering, behavioral issues
- Complete Income and Assets assessments using restored field structure
- Total monthly income: $8,000
- Total assets: $1,950,000
  - Liquid Assets: $150,000 checking 30k savings 100k cash 20k
  - Investments: $800,000 stocks bonds 400k funds 350k other 50k
  - Retirement: $500,000 traditional 400k roth 100k pension 0
  - Real Estate: $450,000 home equity 450k other 0
  - Life Insurance: $50,000
- Estimated monthly cost: $12,000
- Financial runway: 180 months 15 years

Usage:
    python3 create_demo_mary.py

Prerequisites:
    - App must be stopped will fail if app is running due to file lock
    - Run from project root directory
"""

import json
from pathlib import Path

# UID MUST be prefixed with demo for protected demo loading
UID = "demo_mary_memory_care"

data = {
    "uid": UID,
    "auth": {
        "user_id": UID,
        "is_authenticated": True,
        "name": "Mary Memory Care",
        "email": "mary.memorycare@demo.test"
    },
    "profile": {
        "name": "Mary",
        "age_range": "80+",
        "location": "Newport Beach, CA",
        "zip_code": "92660",
        "relationship": "self",
        "qualifiers": {
            "is_on_medicaid": False,
            "is_veteran": False,
            "service_connected_disability": False,
            "has_spouse": False,
            "spouse_needs_care": False,
            "is_homeowner": True
        }
    },
    "cost_v2_qualifiers": {
        "is_on_medicaid": False,
        "is_veteran": False,
        "service_connected_disability": False,
        "has_spouse": False,
        "spouse_needs_care": False,
        "is_homeowner": True
    },
    "flags": {
        "is_veteran": False,
        "memory_care_high_acuity": True,
        "wandering_risk": True,
        "behavioral_issues": True,
        "enable_cost_planner_v2": True
    },
    "gcp_care_recommendation": {
        "progress": 100.0,
        "status": "done",
        "tier": "memory_care_high_acuity",
        "tier_score": 32.0,
        "confidence": 0.95,
        "age_range": "80+",
        "living_situation": "cannot_live_alone",
        "isolation": "very",
        "flags": {
            "memory_care_high_acuity": True,
            "severe_cognitive_decline": True,
            "all_adl_limitations": True,
            "wandering_risk": True,
            "behavioral_issues": True,
            "fall_risk_high": True,
            "aspiration_risk": True,
            "incontinence": True,
            "caregiver_burnout": True
        },
        "meds_complexity": "complex",
        "mobility": "wheelchair",
        "falls": "multiple",
        "chronic_conditions": ["alzheimers_advanced", "diabetes", "hypertension"],
        "additional_conditions": ["incontinence", "swallowing_difficulty"],
        "memory_changes": "severe",
        "mood": "agitated",
        "behaviors": ["wandering", "aggression", "sundowning"],
        "help_overall": "dependent",
        "badls": ["bathing", "dressing", "toileting", "eating", "mobility", "grooming"],
        "iadls": ["cooking", "shopping", "finances", "med_management", "phone", "transportation", "housekeeping"],
        "hours_per_day": "24h",
        "primary_support": "none"
    },
    "gcp_v4_published": True,
    "cost_v2_modules": {
        "income": {
            "status": "completed",
            "progress": 100,
            "data": {
                "has_partner": "no_partner",
                "partner_income_monthly": 0.0,
                "shared_finance_notes": "",
                "ss_monthly": 2800.0,
                "pension_monthly": 3200.0,
                "employment_status": "not_employed",
                "employment_income": 0.0,
                "other_income": 0.0,
                "annuity_monthly": 0.0,
                "retirement_distributions_monthly": 2000.0,
                "dividends_interest_monthly": 0.0,
                "rental_income_monthly": 0.0,
                "alimony_support_monthly": 0.0,
                "ltc_insurance_monthly": 0.0,
                "family_support_monthly": 0.0,
                "status": "done",
                "completed_at": "2025-01-20 10:00:00",
                "total_monthly_income": 8000.0
            }
        },
        "assets": {
            "status": "completed",
            "progress": 100,
            "data": {
                "asset_has_partner": "no_partner",
                "asset_legal_restrictions": "",
                "checking_balance": 30000.0,
                "savings_cds_balance": 100000.0,
                "cash_on_hand": 20000.0,
                "brokerage_stocks_bonds": 400000.0,
                "brokerage_mf_etf": 350000.0,
                "brokerage_other": 50000.0,
                "retirement_traditional": 400000.0,
                "retirement_roth": 100000.0,
                "retirement_pension_value": 0.0,
                "home_equity_estimate": 450000.0,
                "real_estate_other": 0.0,
                "life_insurance_cash_value": 50000.0,
                "status": "done",
                "completed_at": "2025-01-20 10:05:00",
                "total_asset_value": 1950000.0,
                "total_asset_debt": 0.0,
                "net_asset_value": 1950000.0
            }
        }
    },
    "cost_v2_step": "exit",
    "cost_v2_guest_mode": False,
    "cost_v2_triage": {},
    "cost_v2_quick_estimate": {
        "estimate": {
            "monthly_base": 9500,
            "monthly_adjusted": 12000.0,
            "annual": 144000.0,
            "three_year": 432000.0,
            "five_year": 720000.0,
            "multiplier": 1.26,
            "region_name": "Newport Beach CA Coastal Orange County",
            "care_tier": "memory_care_high_acuity",
            "breakdown": {
                "base_cost": 9500,
                "regional_adjustment": 2470.0,
                "high_acuity_addon": 30.0
            }
        },
        "care_tier": "memory_care_high_acuity",
        "zip_code": "92660"
    },
    "mcip_contracts": {
        "care_recommendation": {
            "tier": "memory_care_high_acuity",
            "tier_score": 32.0,
            "tier_rankings": [
                ["memory_care_high_acuity", 32.0],
                ["memory_care", 26.0],
                ["assisted_living", 18.0],
                ["in_home", 10.0],
                ["no_care_needed", 2.0]
            ],
            "confidence": 0.95,
            "flags": [
                {
                    "id": "severe_cognitive_decline",
                    "label": "Severe Cognitive Impairment",
                    "description": "Advanced Alzheimers disease with constant confusion",
                    "tone": "error",
                    "priority": 1,
                    "cta": {"label": "Find Memory Care", "route": "partners"}
                },
                {
                    "id": "all_adl_limitations",
                    "label": "All ADLs Require Assistance",
                    "description": "Needs full help with all ADLs",
                    "tone": "error",
                    "priority": 1,
                    "cta": {"label": "Learn About Care", "route": "learning"}
                },
                {
                    "id": "wandering_risk",
                    "label": "High Wandering Risk",
                    "description": "Frequent wandering episodes",
                    "tone": "warning",
                    "priority": 1,
                    "cta": {"label": "Explore Secured Units", "route": "partners"}
                },
                {
                    "id": "behavioral_issues",
                    "label": "Behavioral Challenges",
                    "description": "Agitation aggression sundowning",
                    "tone": "warning",
                    "priority": 2,
                    "cta": {"label": "Behavioral Support", "route": "learning"}
                }
            ],
            "rationale": [
                "Based on 32 points we recommend Memory Care High Acuity",
                "Severe Alzheimers disease",
                "All 6 ADLs require full assistance",
                "High-risk behaviors wandering aggression",
                "Medical complexities aspiration incontinence falls",
                "Family caregivers unable to provide safe care"
            ],
            "generated_at": "2025-01-20T10:10:00Z",
            "version": "4.0.0",
            "input_snapshot_id": "gcp_v4_mary_20250120",
            "rule_set": "standard_2025_q4",
            "next_step": {
                "product": "cost_planner",
                "route": "cost_v2",
                "label": "Calculate Costs"
            },
            "status": "complete",
            "last_updated": "2025-01-20T10:10:00Z",
            "needs_refresh": False
        },
        "financial_profile": {
            "estimated_monthly_cost": 12000.0,
            "coverage_percentage": 66.67,
            "gap_amount": 4000.0,
            "runway_months": 180,
            "confidence": 0.92,
            "generated_at": "2025-01-20T10:15:00",
            "status": "complete"
        },
        "advisor_appointment": None,
        "journey": {
            "current_hub": "concierge",
            "completed_products": ["gcp", "gcp_v4", "cost_planner", "cost_v2"],
            "unlocked_products": ["gcp", "gcp_v4", "cost_planner", "cost_v2", "facility_finder", "pfma"],
            "recommended_next": "facility_finder"
        },
        "waiting_room": {
            "advisor_prep_status": "not_started",
            "trivia_status": "not_started",
            "current_focus": "advisor_prep"
        }
    },
    "tiles": {
        "gcp_v4": {
            "progress": 100.0,
            "status": "done",
            "tier": "memory_care_high_acuity",
            "confidence": 0.95,
            "tier_score": 32.0
        },
        "cost_planner_v2": {
            "status": "done",
            "progress": 100,
            "assessments": {
                "income": {
                    "has_partner": "no_partner",
                    "ss_monthly": 2800.0,
                    "pension_monthly": 3200.0,
                    "retirement_distributions_monthly": 2000.0,
                    "status": "done",
                    "total_monthly_income": 8000.0
                },
                "assets": {
                    "asset_has_partner": "no_partner",
                    "checking_balance": 30000.0,
                    "savings_cds_balance": 100000.0,
                    "cash_on_hand": 20000.0,
                    "brokerage_stocks_bonds": 400000.0,
                    "brokerage_mf_etf": 350000.0,
                    "brokerage_other": 50000.0,
                    "retirement_traditional": 400000.0,
                    "retirement_roth": 100000.0,
                    "retirement_pension_value": 0.0,
                    "home_equity_estimate": 450000.0,
                    "real_estate_other": 0.0,
                    "life_insurance_cash_value": 50000.0,
                    "status": "done",
                    "total_asset_value": 1950000.0,
                    "total_asset_debt": 0.0,
                    "net_asset_value": 1950000.0
                }
            }
        }
    },
    "progress": {},
    "preferences": {},
    "last_updated": 1737370800.0,
    "created_at": 1737370800.0
}

def main():
    demo_dir = Path("data/users/demo")
    demo_dir.mkdir(parents=True, exist_ok=True)
    output_file = demo_dir / f"{UID}.json"

    if output_file.exists():
        print(f"Warning Profile file already exists: {output_file}")
        response = input("Overwrite yes or no: ").strip().lower()
        if response not in ["yes", "y"]:
            print("Aborted")
            return

    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        file_size = output_file.stat().st_size
        line_count = len(output_file.read_text().splitlines())

        print("Profile created successfully")
        print(f"File: {output_file}")
        print(f"Size: {file_size} bytes")
        print(f"Lines: {line_count}")
        print(f"UID: {data['uid']}")
        print(f"Care Tier: {data['mcip_contracts']['care_recommendation']['tier']}")
        print(f"Tier Score: {data['mcip_contracts']['care_recommendation']['tier_score']} points")
        print(f"Confidence: {data['mcip_contracts']['care_recommendation']['confidence']}")
        print(f"Monthly Income: ${data['cost_v2_modules']['income']['data']['total_monthly_income']}")
        print(f"Net Assets: ${data['cost_v2_modules']['assets']['data']['net_asset_value']}")
        print(f"Est Monthly Cost: ${data['mcip_contracts']['financial_profile']['estimated_monthly_cost']}")
        print(f"Monthly Gap: ${data['mcip_contracts']['financial_profile']['gap_amount']}")
        print(f"Runway: {data['mcip_contracts']['financial_profile']['runway_months']} months 15 years")
        print(f"Protected source: {output_file}")
        print("Working copy: data/users/demo_mary_memory_care.json")

    except PermissionError:
        print("ERROR Could not write file Is the app running")
        return
    except Exception as e:
        print(f"ERROR: {e}")
        return

if __name__ == "__main__":
    main()
