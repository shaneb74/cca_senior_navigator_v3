#!/usr/bin/env python3
"""
Create Demo John Test Profile - Version 2

Uses EXACT profile data from working user session to generate pre-configured
demo user with complete GCP and Cost Planner data.

This profile contains:
- Assisted Living recommendation (18 points)
- 9 care flags including veteran benefits, cognitive concerns, mobility
- Complete Income & Assets assessments (using restored field structure)
- Total monthly income: $6,200
- Total assets: $205,000
  - Liquid Assets: $5,000 (checking: $2k, savings: $3k, cash: $0)
  - Investments: $20,000 (stocks/bonds: $5k, funds: $15k, other: $0)
  - Retirement: $0 (traditional: $0, roth: $0, pension: $0)
  - Real Estate: $175,000 (home equity: $175k, other: $0)
  - Life Insurance: $5,000

Usage:
    python3 create_demo_john_v2.py

Prerequisites:
    - App must be stopped (will fail if app is running due to file lock)
    - Run from project root directory
"""

import json
from pathlib import Path

# EXACT profile data from user's working session
# This is a complete, tested profile that successfully loads in the app
data = {
    "gcp_care_recommendation": {
        "progress": 100.0,
        "status": "done",
        "age_range": "under_65",
        "living_situation": "alone",
        "isolation": "somewhat",
        "flags": {
            "low_access": True,
            "moderate_dependence": True,
            "chronic_present": True,
            "moderate_mobility": True,
            "moderate_safety_concern": True,
            "moderate_cognitive_decline": True,
            "moderate_risk": True,
            "veteran_aanda_risk": True,
            "limited_support": True
        },
        "meds_complexity": "complex",
        "mobility": "walker",
        "falls": "one",
        "chronic_conditions": [
            "diabetes",
            "hypertension",
            "arthritis"
        ],
        "additional_conditions": [],
        "memory_changes": "moderate",
        "mood": "okay",
        "behaviors": [
            "confusion"
        ],
        "help_overall": "independent",
        "badls": [
            "mobility"
        ],
        "iadls": [
            "finances",
            "med_management"
        ],
        "hours_per_day": "1-3h",
        "primary_support": "family"
    },
    "auth": {
        "user_id": "demo_john_cost_planner",
        "is_authenticated": True
    },
    "cost_v2_modules": {
        "income": {
            "status": "completed",
            "progress": 100,
            "data": {
                "has_partner": "no_partner",
                "partner_income_monthly": 0.0,
                "shared_finance_notes": "",
                "ss_monthly": 2400.0,
                "pension_monthly": 0.0,
                "employment_status": "not_employed",
                "employment_income": 0.0,
                "other_income": 500.0,
                "annuity_monthly": 0.0,
                "retirement_distributions_monthly": 2300.0,
                "dividends_interest_monthly": 0.0,
                "rental_income_monthly": 0.0,
                "alimony_support_monthly": 0.0,
                "ltc_insurance_monthly": 1000.0,
                "family_support_monthly": 0.0,
                "status": "done",
                "completed_at": "2025-10-18 15:11:43",
                "total_monthly_income": 6200.0
            }
        },
        "assets": {
            "status": "completed",
            "progress": 100,
            "data": {
                "asset_has_partner": "no_partner",
                "asset_legal_restrictions": "",
                # Liquid Assets (3 fields) = $5,000
                "checking_balance": 2000.0,
                "savings_cds_balance": 3000.0,
                "cash_on_hand": 0.0,  # RESTORED FIELD
                # Investments (3 fields) = $20,000
                "brokerage_stocks_bonds": 5000.0,
                "brokerage_mf_etf": 15000.0,
                "brokerage_other": 0.0,  # RESTORED FIELD
                # Retirement (3 fields) = $0
                "retirement_traditional": 0.0,
                "retirement_roth": 0.0,
                "retirement_pension_value": 0.0,  # RESTORED FIELD
                # Real Estate (2 fields - Advanced mode) = $175,000
                "home_equity_estimate": 175000.0,
                "real_estate_other": 0.0,
                # Life Insurance (1 field) = $5,000
                "life_insurance_cash_value": 5000.0,
                "status": "done",
                "completed_at": "2025-10-18 15:12:13",
                "total_asset_value": 205000.0,
                "net_asset_value": 205000.0
            }
        }
    },
    "gcp_v4_published": True,
    "profile": {
        "qualifiers": {
            "is_on_medicaid": False,
            "is_veteran": True,
            "is_homeowner": False
        }
    },
    "cost_v2_qualifiers": {
        "is_on_medicaid": False,
        "is_veteran": True,
        "is_homeowner": False
    },
    "mcip_contracts": {
        "care_recommendation": {
            "tier": "assisted_living",
            "tier_score": 18.0,
            "tier_rankings": [
                ["memory_care_high_acuity", 70.0],
                ["memory_care", 32.0],
                ["assisted_living", 18.0],
                ["in_home", 12.5],
                ["no_care_needed", 4.0]
            ],
            "confidence": 0.73,
            "flags": [
                {
                    "id": "low_access",
                    "label": "Limited Service Access",
                    "description": "Somewhat isolated location with limited healthcare access",
                    "tone": "info",
                    "priority": 3,
                    "cta": {
                        "label": "See Available Services",
                        "route": "partners",
                        "filter": "home_care"
                    }
                },
                {
                    "id": "moderate_dependence",
                    "label": "Regular Assistance Needed",
                    "description": "Needs regular help with daily activities",
                    "tone": "warning",
                    "priority": 2,
                    "cta": {
                        "label": "Learn About Care Options",
                        "route": "learning",
                        "filter": "daily_living_support"
                    }
                },
                {
                    "id": "chronic_present",
                    "label": "Chronic Conditions",
                    "description": "One or more chronic health conditions requiring management",
                    "tone": "info",
                    "priority": 2,
                    "cta": {
                        "label": "Learn About Health Management",
                        "route": "learning",
                        "filter": "health_management"
                    }
                },
                {
                    "id": "moderate_mobility",
                    "label": "Mobility Assistance Needed",
                    "description": "Uses cane or walker, may need accessibility modifications",
                    "tone": "info",
                    "priority": 3,
                    "cta": {
                        "label": "Learn About Mobility Support",
                        "route": "learning",
                        "filter": "mobility_support"
                    }
                },
                {
                    "id": "moderate_safety_concern",
                    "label": "Safety Monitoring Needed",
                    "description": "One fall or safety concerns that warrant attention",
                    "tone": "warning",
                    "priority": 2,
                    "cta": {
                        "label": "See Safety Resources",
                        "route": "learning",
                        "filter": "safety"
                    }
                },
                {
                    "id": "moderate_cognitive_decline",
                    "label": "Moderate Memory Concerns",
                    "description": "Noticeable memory or thinking difficulties requiring support",
                    "tone": "warning",
                    "priority": 1,
                    "cta": {
                        "label": "Find Memory Care Resources",
                        "route": "partners",
                        "filter": "memory_care"
                    }
                },
                {
                    "id": "moderate_risk",
                    "label": "Emotional Support Helpful",
                    "description": "Emotional ups and downs that could benefit from support",
                    "tone": "info",
                    "priority": 3,
                    "cta": {
                        "label": "Explore Wellness Resources",
                        "route": "learning",
                        "filter": "mental_health"
                    }
                },
                {
                    "id": "veteran_aanda_risk",
                    "label": "Veteran A&A Eligible",
                    "description": "May qualify for VA Aid & Attendance benefits",
                    "tone": "info",
                    "priority": 3,
                    "cta": {
                        "label": "Learn About VA Benefits",
                        "route": "learning",
                        "filter": "veteran_benefits"
                    }
                },
                {
                    "id": "limited_support",
                    "label": "Limited Caregiver Availability",
                    "description": "Limited caregiver support may not be sufficient",
                    "tone": "info",
                    "priority": 2,
                    "cta": {
                        "label": "Explore Support Options",
                        "route": "learning",
                        "filter": "caregiver_support"
                    }
                }
            ],
            "rationale": [
                "Based on 18 points, we recommend: Assisted Living",
                "Medication Mobility: 8 points",
                "  • Complex – many meds or caregiver-managed",
                "Daily Living: 5 points",
                "  • Mobility",
                "Cognition Mental Health: 4 points"
            ],
            "generated_at": "2025-10-18T20:09:30.122321Z",
            "version": "4.0.0",
            "input_snapshot_id": "gcp_v4_anon_20251018_200930",
            "rule_set": "standard_2025_q4",
            "next_step": {
                "product": "cost_planner",
                "route": "cost_v2",
                "label": "Calculate Costs",
                "reason": "Calculate financial impact of Assisted Living care"
            },
            "status": "complete",
            "last_updated": "2025-10-18T20:09:30.122351Z",
            "needs_refresh": False
        },
        "financial_profile": {
            "estimated_monthly_cost": 9089.055359999998,
            "coverage_percentage": 68.21390952557694,
            "gap_amount": 2889.0553599999985,
            "runway_months": 10,
            "confidence": 1.0,
            "generated_at": "2025-10-18T15:12:32.954466",
            "status": "complete"
        },
        "advisor_appointment": None,
        "journey": {
            "current_hub": "concierge",
            "completed_products": ["gcp"],
            "unlocked_products": ["gcp", "cost_planner", "pfma"],
            "recommended_next": "cost_planner"
        },
        "waiting_room": {
            "advisor_prep_status": "not_started",
            "trivia_status": "not_started",
            "current_focus": "advisor_prep"
        }
    },
    "flags": {
        "is_veteran": True,
        "medicaid_planning_interest": False
    },
    "cost_v2_step": "exit",
    "progress": {},
    "tiles": {
        "gcp_v4": {
            "progress": 100.0,
            "status": "done",
            "last_step": 5,
            "saved_state": {
                "progress": 80.0,
                "status": "doing",
                "age_range": "under_65",
                "living_situation": "alone",
                "isolation": "somewhat",
                "flags": {
                    "low_access": True,
                    "moderate_dependence": True,
                    "chronic_present": True,
                    "moderate_mobility": True,
                    "moderate_safety_concern": True,
                    "moderate_cognitive_decline": True,
                    "moderate_risk": True,
                    "veteran_aanda_risk": True,
                    "limited_support": True
                },
                "meds_complexity": "complex",
                "mobility": "walker",
                "falls": "one",
                "chronic_conditions": ["diabetes", "hypertension", "arthritis"],
                "additional_conditions": [],
                "memory_changes": "moderate",
                "mood": "okay",
                "behaviors": ["confusion"],
                "help_overall": "independent",
                "badls": ["mobility"],
                "iadls": ["finances", "med_management"],
                "hours_per_day": "1-3h",
                "primary_support": "family"
            }
        },
        "cost_planner_v2": {
            "assessments": {
                "income": {
                    "has_partner": "no_partner",
                    "partner_income_monthly": 0.0,
                    "shared_finance_notes": "",
                    "ss_monthly": 2400.0,
                    "pension_monthly": 0.0,
                    "employment_status": "not_employed",
                    "employment_income": 0.0,
                    "other_income": 500.0,
                    "annuity_monthly": 0.0,
                    "retirement_distributions_monthly": 2300.0,
                    "dividends_interest_monthly": 0.0,
                    "rental_income_monthly": 0.0,
                    "alimony_support_monthly": 0.0,
                    "ltc_insurance_monthly": 1000.0,
                    "family_support_monthly": 0.0,
                    "status": "done",
                    "completed_at": "2025-10-18 15:11:43",
                    "total_monthly_income": 6200.0
                },
                "assets": {
                    "asset_has_partner": "no_partner",
                    "asset_legal_restrictions": "",
                    # Liquid Assets (3 fields) = $5,000
                    "checking_balance": 2000.0,
                    "savings_cds_balance": 3000.0,
                    "cash_on_hand": 0.0,
                    # Investments (3 fields) = $20,000
                    "brokerage_stocks_bonds": 5000.0,
                    "brokerage_mf_etf": 15000.0,
                    "brokerage_other": 0.0,
                    # Retirement (3 fields) = $0
                    "retirement_traditional": 0.0,
                    "retirement_roth": 0.0,
                    "retirement_pension_value": 0.0,
                    # Real Estate (2 fields - Advanced mode) = $175,000
                    "home_equity_estimate": 175000.0,
                    "real_estate_other": 0.0,
                    # Life Insurance (1 field) = $5,000
                    "life_insurance_cash_value": 5000.0,
                    "status": "done",
                    "completed_at": "2025-10-18 15:12:13",
                    "total_asset_value": 205000.0,
                    "net_asset_value": 205000.0
                }
            }
        }
    },
    "cost_v2_quick_estimate": {
        "estimate": {
            "monthly_base": 4500,
            "monthly_adjusted": 9089.055359999998,
            "annual": 109068.66431999998,
            "three_year": 327205.99295999995,
            "five_year": 545343.3215999999,
            "multiplier": 1.15,
            "region_name": "Seattle (Downtown/Core)",
            "care_tier": "assisted_living",
            "breakdown": {
                "base_cost": 4500,
                "regional_adjustment": 674.9999999999995,
                "severe_cognitive_addon": 1035.0,
                "high_adl_support_addon": 621.0,
                "medication_management_addon": 546.48,
                "behavioral_care_addon": 885.2975999999999,
                "chronic_conditions_addon": 826.27776
            }
        },
        "care_tier": "assisted_living",
        "zip_code": "98101"
    },
    "preferences": {},
    "uid": "demo_john_cost_planner",
    "last_updated": 1760818352.98561,
    "created_at": 1760818352.985611
}


def main():
    """Create the John Test profile file."""
    # Ensure demo directory exists
    demo_dir = Path("data/users/demo")
    demo_dir.mkdir(parents=True, exist_ok=True)

    # Output file path (in protected demo directory)
    output_file = demo_dir / "demo_john_cost_planner.json"

    # Check if app is running (file might be locked)
    if output_file.exists():
        print(f"⚠️  Profile file already exists: {output_file}")
        response = input("Overwrite? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("❌ Aborted.")
            return

    # Write profile to file
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Get file size
        file_size = output_file.stat().st_size
        line_count = len(output_file.read_text().splitlines())

        print("✅ Profile created successfully!")
        print(f"   File: {output_file}")
        print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"   Lines: {line_count:,}")
        print()
        print("📋 Profile Summary:")
        print(f"   UID: {data['uid']}")
        print(f"   Care Tier: {data['mcip_contracts']['care_recommendation']['tier']}")
        print(f"   Tier Score: {data['mcip_contracts']['care_recommendation']['tier_score']} points")
        print(f"   Confidence: {data['mcip_contracts']['care_recommendation']['confidence']:.0%}")
        print(f"   Care Flags: {len(data['mcip_contracts']['care_recommendation']['flags'])}")
        print()
        print("💰 Financial Summary:")
        print(f"   Monthly Income: ${data['cost_v2_modules']['income']['data']['total_monthly_income']:,.0f}")
        print(f"   Net Assets: ${data['cost_v2_modules']['assets']['data']['net_asset_value']:,.0f}")
        print(f"   Est. Monthly Cost: ${data['mcip_contracts']['financial_profile']['estimated_monthly_cost']:,.0f}")
        print(f"   Monthly Gap: ${data['mcip_contracts']['financial_profile']['gap_amount']:,.0f}")
        print(f"   Runway: {data['mcip_contracts']['financial_profile']['runway_months']} months")
        print()
        print("🎯 Next Steps:")
        print("   1. Start the app: streamlit run app.py")
        print("   2. Navigate to login page")
        print("   3. Click 'John Test' button")
        print("   4. Verify GCP shows Assisted Living with 9 care flags")
        print("   5. Verify Cost Planner shows Income & Assets complete")
        print()
        print("💡 Demo Profile Behavior:")
        print(f"   • Protected source: {output_file}")
        print("   • Working copy: data/users/demo_john_cost_planner.json")
        print("   • Each login starts with fresh copy from demo/")
        print("   • Changes saved to working copy during session")
        print("   • Source in demo/ is never modified")

    except PermissionError:
        print("❌ ERROR: Could not write file. Is the app running?")
        print("   Stop the app first: pkill -9 streamlit")
        return
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return


if __name__ == "__main__":
    main()
