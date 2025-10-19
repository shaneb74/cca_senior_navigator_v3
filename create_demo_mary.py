"""
Create Demo Mary Profile

Creates a complete demo user profile for Mary with:
- Memory Care recommendation (high acuity)
- 5-year financial runway
- Complete GCP and Cost Planner data
- More severe memory issues than Sarah

Usage:
    python3 create_demo_mary.py

Output:
    data/users/demo/demo_mary_full_data.json
"""

import json
from pathlib import Path


def create_mary_profile():
    """Create Mary's complete demo profile."""
    
    # GCP Assessment Data - Memory Care (High Acuity)
    # Even higher scores than Sarah - more severe impairment
    gcp_assessment = {
        "mobility": {
            "walking": "no",  # Cannot walk independently
            "stairs": "no",  # Cannot manage stairs
            "transfers": "no",  # Needs full transfer assistance
            "wheelchair": "yes"  # Uses wheelchair
        },
        "self_care": {
            "bathing": "no",  # Needs full assistance
            "dressing": "no",  # Needs full assistance
            "toileting": "no",  # Needs full assistance
            "eating": "sometimes",  # Needs prompting/help
            "grooming": "no"  # Needs full assistance
        },
        "cognitive": {
            "memory_issues": "severe",  # KEY: Severe memory issues
            "gets_lost": "yes",  # Gets lost frequently
            "forgets_medications": "yes",  # Cannot manage meds
            "confusion_time": "yes",  # Constant confusion
            "poor_judgment": "yes",  # Very poor judgment
            "communication_difficulty": "yes"  # Trouble communicating
        },
        "health": {
            "chronic_conditions": ["diabetes", "hypertension", "heart_disease"],
            "recent_falls": "yes",  # Multiple falls
            "incontinence": "yes",  # Full incontinence
            "vision_issues": "yes",
            "hearing_issues": "yes",
            "swallowing_difficulty": "yes"  # Aspiration risk
        },
        "safety": {
            "lives_alone": "no",  # Cannot live alone
            "emergency_response": "no",  # Cannot respond
            "stove_safety": "no",  # Unsafe with appliances
            "medication_management": "no",  # Cannot manage
            "wandering_risk": "yes",  # High wandering risk
            "aggression_risk": "yes"  # Behavioral issues
        },
        "social": {
            "social_isolation": "yes",
            "caregiver_available": "yes",  # Family exhausted
            "activities_participation": "no",
            "depression_anxiety": "yes",
            "caregiver_burnout": "yes"  # Caregiver stress high
        }
    }
    
    # Calculate GCP scores for Memory Care High Acuity
    # High acuity typically requires: 26-35+ points with severe cognitive impairment
    gcp_scores = {
        "total_score": 28,  # High acuity memory care
        "mobility_score": 5,
        "self_care_score": 6,  # All ADLs need assistance
        "cognitive_score": 7,  # Severe cognitive impairment
        "health_score": 5,
        "safety_score": 5,  # Maximum safety concerns
        "social_score": 0
    }
    
    gcp_flags = {
        "memory_issues_severe": True,  # KEY flag
        "all_adl_limitations": True,  # All ADLs affected
        "fall_risk_high": True,
        "medication_management_impossible": True,
        "safety_concerns_critical": True,
        "wandering_risk": True,
        "behavioral_issues": True,
        "aspiration_risk": True,
        "incontinence": True,
        "caregiver_burnout": True,
        "cannot_live_alone": True
    }
    
    # Care Recommendation - Memory Care High Acuity
    care_recommendation = {
        # Core MCIP CareRecommendation fields
        "tier": "memory_care_high_acuity",
        "tier_score": 28.0,
        "tier_rankings": [
            ("memory_care_high_acuity", 28.0),
            ("memory_care", 24.0),
            ("assisted_living", 16.0),
            ("in_home", 8.0),
            ("no_care_needed", 1.0)
        ],
        "confidence": 0.95,  # 95% confidence
        "flags": [
            {"type": "memory_issues_severe", "severity": "critical"},
            {"type": "all_adl_limitations", "severity": "critical"},
            {"type": "wandering_risk", "severity": "high"},
            {"type": "behavioral_issues", "severity": "high"},
            {"type": "fall_risk_high", "severity": "high"},
            {"type": "aspiration_risk", "severity": "medium"},
            {"type": "caregiver_burnout", "severity": "high"}
        ],
        "rationale": [
            "Severe memory impairment with constant confusion",
            "All ADLs require full assistance (bathing, dressing, toileting, eating)",
            "High risk: wandering, falls, behavioral issues",
            "Cannot live alone or manage any daily tasks independently",
            "Requires 24/7 specialized memory care with behavioral support"
        ],
        "generated_at": "2025-10-18T11:00:00Z",
        "version": "4.0",
        "input_snapshot_id": "mary_demo_v1",
        "rule_set": "gcp_v4_standard",
        "next_step": {
            "product": "cost_planner",
            "route": "cost_v2"
        },
        "status": "complete",
        "last_updated": "2025-10-18T11:00:00Z",
        "needs_refresh": False,
        
        # Extra fields for demo/debugging
        "tier_label": "Memory Care (High Acuity)",
        "assessment_data": gcp_assessment,
        "scores": gcp_scores
    }
    
    # Financial Profile - 5 years (60 months) timeline
    financial_profile = {
        # Core MCIP FinancialProfile fields
        "estimated_monthly_cost": 9500.0,  # High acuity memory care is most expensive
        "coverage_percentage": 33.7,  # ($3200 / $9500) * 100
        "gap_amount": -6300.0,  # Large monthly shortfall
        "runway_months": 60,  # Exactly 5 years
        "confidence": 0.90,  # 90% confidence
        "generated_at": "2025-10-18T11:05:00Z",
        "status": "complete",
        
        # Extra fields for demo/debugging (not in MCIP contract)
        "monthly_income": 3200,
        "total_liquid_assets": 225000,
        "years_covered": 5.0,
        "timeline_category": "medium_term",
        "funding_strategy": "spend_down"
    }
    
    # Cost Planner Assessment Data
    cost_planner_modules = {
        "income": {
            "status": "done",
            "progress": 100,
            "data": {
                "has_partner": "no_partner",
                "partner_income_monthly": 0,
                "shared_finance_notes": "",
                "ss_monthly": 2200,
                "pension_monthly": 1000,
                "employment_status": "not_employed",
                "employment_income": 0,
                "other_income": 0,
                "annuity_monthly": 0,
                "retirement_distributions_monthly": 0,
                "dividends_interest_monthly": 0,
                "rental_income_monthly": 0,
                "alimony_support_monthly": 0,
                "ltc_insurance_monthly": 0,
                "family_support_monthly": 0,
                "total_monthly": 3200
            }
        },
        "assets": {
            "status": "done",
            "progress": 100,
            "data": {
                "asset_has_partner": "no_partner",
                "asset_legal_restrictions": "",
                "cash_liquid_total": 75000,
                "checking_balance": 25000,
                "savings_cds_balance": 50000,
                "brokerage_total": 150000,
                "brokerage_mf_etf": 100000,
                "brokerage_stocks_bonds": 50000,
                "retirement_total": 0,
                "retirement_traditional": 0,
                "retirement_roth": 0,
                "home_equity_estimate": 0,
                "real_estate_other": 0,
                "life_insurance_cash_value": 0,
                "total_liquid": 225000
            }
        },
        "care_costs": {
            "status": "done",
            "progress": 100,
            "data": {
                "care_type": "memory_care_high_acuity",
                "base_monthly_cost": 8500,
                "additional_services": 1000,  # Behavioral support, specialized care
                "estimated_monthly": 9500
            }
        },
        "timeline": {
            "status": "done",
            "progress": 100,
            "data": financial_profile
        }
    }
    
    # MCIP Contracts
    mcip_contracts = {
        "care_recommendation": care_recommendation,
        "financial_profile": financial_profile,
        "journey": {
            "completed_products": ["gcp", "cost_planner"],
            "unlocked_products": ["gcp", "cost_planner", "pfma"],
            "current_product": None,
            "last_activity": "2025-10-18T11:05:00Z"
        }
    }
    
    # Tiles
    tiles = {
        "gcp_v4": {
            "status": "done",
            "progress": 100.0,
            "last_updated": "2025-10-18T11:00:00Z",
            "data": {
                "tier": "memory_care_high_acuity",
                "score": 28,
                "confidence": 0.95
            }
        },
        "cost_planner_v2": {
            "status": "done",
            "progress": 100.0,
            "last_updated": "2025-10-18T11:05:00Z",
            "data": {
                "years_covered": 5.0,
                "monthly_gap": -6300,
                "timeline": "medium_term"
            }
        }
    }
    
    # Complete user profile
    profile = {
        "uid": "demo_mary_full_data",
        "created_at": 1729260000.0,
        "last_updated": 1729260000.0,
        "profile": {
            "name": "Mary Complete",
            "email": "mary@demo.test",
            "person_name": "Mary",
            "relationship": "self"
        },
        "mcip_contracts": mcip_contracts,
        "tiles": tiles,
        "cost_v2_modules": cost_planner_modules,
        "gcp_care_recommendation": care_recommendation,
        "preferences": {},
        "progress": {}
    }
    
    return profile


def save_demo_profile(profile: dict) -> None:
    """Save Mary's profile to protected demo directory."""
    demo_dir = Path("data/users/demo")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = demo_dir / "demo_mary_full_data.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    file_size = output_file.stat().st_size
    
    print("\n" + "="*60)
    print("✅ Mary Demo Profile Created Successfully!")
    print("="*60)
    print(f"\n📄 File: {output_file}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print("\n📋 Profile Details:")
    print("   • Care Recommendation: Memory Care High Acuity (95% confidence)")
    print("   • GCP Score: 28 points (high acuity tier)")
    print("   • Key Issues:")
    print("     - SEVERE memory impairment, constant confusion")
    print("     - ALL ADLs need full assistance (0 independence)")
    print("     - Wheelchair-bound, incontinence, behavioral issues")
    print("     - Cannot live alone, high wandering/fall risk")
    print("     - Diabetes, hypertension, heart disease, aspiration risk")
    print("   • Financial Timeline: 5.0 years (exactly)")
    print("   • Monthly Income: $3,200")
    print("   • Total Assets: $225,000")
    print("   • Monthly Care Cost: $9,500 (high acuity memory care)")
    print("   • Monthly Shortfall: -$6,300")
    print("\n🔐 Protected Source:")
    print("   • Located in: data/users/demo/ (read-only)")
    print("   • Working copy: data/users/demo_mary_full_data.json")
    print("   • Auto-refreshed on each login")
    print("\n🚀 To Use:")
    print("   1. Restart Streamlit app")
    print("   2. Open fresh browser/incognito window")
    print("   3. Click 'Mary Complete' button on login page")
    print("   4. View High Acuity Memory Care recommendation & 5 year timeline")
    print("\n" + "="*60)


if __name__ == "__main__":
    profile = create_mary_profile()
    save_demo_profile(profile)
