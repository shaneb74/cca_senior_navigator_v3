"""
Create Demo Sarah Profile

Creates a complete demo user profile for Sarah with:
- Memory Care recommendation
- Diabetes, hypertension, moderate memory issues
- Multiple ADL limitations
- Financial timeline: 8.5 years
- Complete GCP and Cost Planner data

Usage:
    python3 create_demo_sarah.py

Output:
    data/users/demo/demo_sarah_cost_planner.json
"""

import json
from pathlib import Path


def create_sarah_profile():
    """Create Sarah's complete demo profile."""
    
    # GCP Assessment Data - Memory Care tier
    # Higher scores in memory, safety, and ADL categories
    gcp_assessment = {
        "mobility": {
            "walking": "sometimes",  # Needs assistance
            "stairs": "no",  # Cannot manage stairs
            "transfers": "sometimes",  # Needs help
            "wheelchair": "no"
        },
        "self_care": {
            "bathing": "no",  # Needs full assistance
            "dressing": "sometimes",  # Needs help
            "toileting": "sometimes",  # Needs assistance
            "eating": "yes",  # Can eat independently
            "grooming": "sometimes"  # Needs help
        },
        "cognitive": {
            "memory_issues": "moderate",  # KEY: Moderate memory issues
            "gets_lost": "yes",  # Gets lost/confused
            "forgets_medications": "yes",  # Forgets meds
            "confusion_time": "yes",  # Time/place confusion
            "poor_judgment": "yes"  # Poor judgment/decisions
        },
        "health": {
            "chronic_conditions": ["diabetes", "hypertension"],  # Multiple conditions
            "recent_falls": "yes",  # Fall risk
            "incontinence": "sometimes",  # Occasional
            "vision_issues": "yes",  # Vision problems
            "hearing_issues": "no"
        },
        "safety": {
            "lives_alone": "yes",  # Living alone is risky
            "emergency_response": "no",  # Cannot respond
            "stove_safety": "no",  # Unsafe with stove
            "medication_management": "no",  # Cannot manage meds
            "wandering_risk": "yes"  # Wanders/gets lost
        },
        "social": {
            "social_isolation": "yes",  # Isolated
            "caregiver_available": "yes",  # Has family support
            "activities_participation": "no",  # Not participating
            "depression_anxiety": "yes"  # Mental health concerns
        }
    }
    
    # Calculate GCP scores for Memory Care tier
    # Memory Care typically requires: 20-28+ points with high memory/safety flags
    gcp_scores = {
        "total_score": 24,  # Memory Care range
        "mobility_score": 4,
        "self_care_score": 5,
        "cognitive_score": 6,  # High cognitive needs
        "health_score": 4,
        "safety_score": 5,  # High safety concerns
        "social_score": 0
    }
    
    gcp_flags = {
        "memory_issues_moderate_severe": True,  # KEY flag
        "multiple_adl_limitations": True,  # 3+ ADLs
        "fall_risk": True,
        "medication_management_issues": True,
        "safety_concerns": True,
        "wandering_risk": True,  # Memory care indicator
        "lives_alone_with_limitations": True,
        "chronic_conditions": True,
        "social_isolation": True,
        "caregiver_stress": False  # Has support
    }
    
    # Care Recommendation - Memory Care (with all required MCIP fields)
    care_recommendation = {
        # Core MCIP CareRecommendation fields
        "tier": "memory_care",
        "tier_score": 24.0,
        "tier_rankings": [
            ("memory_care", 24.0),
            ("assisted_living", 18.0),
            ("in_home", 12.0),
            ("no_care_needed", 3.0)
        ],
        "confidence": 0.88,  # 88% confidence
        "flags": [
            {"type": "memory_issues_moderate_severe", "severity": "high"},
            {"type": "wandering_risk", "severity": "high"},
            {"type": "multiple_adl_limitations", "severity": "high"},
            {"type": "fall_risk", "severity": "medium"},
            {"type": "medication_management_issues", "severity": "high"},
            {"type": "safety_concerns", "severity": "high"}
        ],
        "rationale": [
            "Moderate memory issues with confusion and poor judgment",
            "Multiple ADL limitations requiring assistance",
            "Safety concerns: wandering risk, cannot manage medications",
            "Lives alone with multiple fall risks",
            "Specialized memory care environment recommended"
        ],
        "generated_at": "2025-10-18T10:30:00Z",
        "version": "4.0",
        "input_snapshot_id": "sarah_demo_v1",
        "rule_set": "gcp_v4_standard",
        "next_step": {
            "product": "cost_planner",
            "route": "cost_v2"
        },
        "status": "complete",
        "last_updated": "2025-10-18T10:30:00Z",
        "needs_refresh": False,
        
        # Extra fields for demo/debugging (not in MCIP contract)
        "tier_label": "Memory Care",
        "assessment_data": gcp_assessment,
        "scores": gcp_scores
    }
    
    # Financial Profile - 8.5 years timeline
    financial_profile = {
        # Core MCIP FinancialProfile fields
        "estimated_monthly_cost": 8500.0,  # Memory care is expensive
        "coverage_percentage": 56.5,  # ($4800 / $8500) * 100
        "gap_amount": -3700.0,  # Monthly shortfall
        "runway_months": 102,  # 8.5 years (102 months)
        "confidence": 0.85,  # 85% confidence
        "generated_at": "2025-10-18T10:35:00Z",
        "status": "complete",
        
        # Extra fields for demo/debugging (not in MCIP contract)
        "monthly_income": 4800,
        "total_liquid_assets": 142000,
        "years_covered": 8.5,
        "timeline_category": "medium_term",
        "funding_strategy": "spend_down"
    }
    
    # Cost Planner Assessment Data
    cost_planner_modules = {
        "income": {
            "status": "done",
            "progress": 100,
            "data": {
                "social_security": 2400,
                "pension": 1800,
                "investment_income": 600,
                "other_income": 0,
                "total_monthly": 4800
            }
        },
        "assets": {
            "status": "done",
            "progress": 100,
            "data": {
                "savings_checking": 45000,
                "investments": 82000,
                "home_equity": 15000,  # Modest home equity
                "other_assets": 0,
                "total_liquid": 142000
            }
        },
        "care_costs": {
            "status": "done",
            "progress": 100,
            "data": {
                "care_type": "memory_care",
                "base_monthly_cost": 7500,
                "additional_services": 1000,  # Higher medical needs
                "estimated_monthly": 8500
            }
        },
        "timeline": {
            "status": "done",
            "progress": 100,
            "data": financial_profile
        }
    }
    
    # MCIP Contracts - Complete data structure
    mcip_contracts = {
        "care_recommendation": care_recommendation,
        "financial_profile": financial_profile,
        "journey": {
            "completed_products": ["gcp", "cost_planner"],
            "unlocked_products": ["gcp", "cost_planner", "pfma"],
            "current_product": None,
            "last_activity": "2025-10-18T10:35:00Z"
        }
    }
    
    # Tiles - Product completion status
    tiles = {
        "gcp_v4": {
            "status": "done",
            "progress": 100.0,
            "last_updated": "2025-10-18T10:30:00Z",
            "data": {
                "tier": "memory_care",
                "score": 24,
                "confidence": 0.88
            }
        },
        "cost_planner_v2": {
            "status": "done",
            "progress": 100.0,
            "last_updated": "2025-10-18T10:35:00Z",
            "data": {
                "years_covered": 8.5,
                "monthly_gap": -3700,
                "timeline": "medium_term"
            }
        }
    }
    
    # Complete user profile
    profile = {
        "uid": "demo_sarah_cost_planner",
        "created_at": 1729258200.0,  # Oct 18, 2025
        "last_updated": 1729258200.0,
        "profile": {
            "name": "Sarah",
            "email": "sarah@example.com",
            "person_name": "Mom",  # Planning for her mother
            "relationship": "adult_child"
        },
        "mcip_contracts": mcip_contracts,
        "tiles": tiles,
        "cost_v2_modules": cost_planner_modules,
        "gcp_care_recommendation": care_recommendation,  # Legacy compatibility
        "preferences": {},
        "progress": {}
    }
    
    return profile


def save_demo_profile(profile: dict) -> None:
    """Save Sarah's profile to protected demo directory."""
    # Ensure demo directory exists
    demo_dir = Path("data/users/demo")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to protected demo directory
    output_file = demo_dir / "demo_sarah_cost_planner.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    file_size = output_file.stat().st_size
    
    print("\n" + "="*60)
    print("✅ Sarah Demo Profile Created Successfully!")
    print("="*60)
    print(f"\n📄 File: {output_file}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print("\n📋 Profile Details:")
    print("   • Care Recommendation: Memory Care (88% confidence)")
    print("   • GCP Score: 24 points (memory care tier)")
    print("   • Key Issues:")
    print("     - Moderate memory issues, confusion, wandering")
    print("     - Multiple ADL limitations (bathing, dressing, toileting)")
    print("     - Diabetes, hypertension")
    print("     - Safety concerns, fall risk")
    print("   • Financial Timeline: 8.5 years")
    print("   • Monthly Income: $4,800")
    print("   • Total Assets: $142,000")
    print("   • Monthly Care Cost: $8,500 (memory care)")
    print("   • Monthly Shortfall: -$3,700")
    print("\n🔐 Protected Source:")
    print("   • Located in: data/users/demo/ (read-only)")
    print("   • Working copy: data/users/demo_sarah_cost_planner.json")
    print("   • Auto-refreshed on each login")
    print("\n🚀 To Use:")
    print("   1. Restart Streamlit app")
    print("   2. Open fresh browser/incognito window")
    print("   3. Click 'Sarah' button on login page")
    print("   4. View Memory Care recommendation & 8.5 year timeline")
    print("\n" + "="*60)


if __name__ == "__main__":
    profile = create_sarah_profile()
    save_demo_profile(profile)
