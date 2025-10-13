"""
Validation script for GCP v3 recommendation output compatibility.

Validates that:
1. Recommendation strings match Cost Planner expectations
2. Required flags are present for additional_services visibility
3. OutcomeContract structure is correct for handoff
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from products.gcp.modules.care_recommendation.logic_v3 import derive_outcome, TIER_NAMES


# Cost Planner expected mapping (from cost_estimate_v2.py)
COST_PLANNER_EXPECTED = {
    "Independent / In-Home": "no_care",
    "In-Home Care": "in_home_care",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "High-Acuity Memory Care": "memory_care_high_acuity",
}

# additional_services expected flags (from additional_services.py)
ADDITIONAL_SERVICES_FLAGS = {
    "cognitive_risk": ["For SeniorLife AI visibility"],
    "meds_management_needed": ["For Omcare visibility"],
    "fall_risk": ["For SeniorLife AI visibility"],
}


def validate_recommendation_strings():
    """Validate that all tier names match Cost Planner expectations."""
    print("\n" + "="*70)
    print("VALIDATION: Recommendation Strings")
    print("="*70)
    
    all_valid = True
    for tier, rec_name in TIER_NAMES.items():
        if rec_name not in COST_PLANNER_EXPECTED:
            print(f"❌ Tier {tier}: '{rec_name}' NOT in Cost Planner mapping")
            all_valid = False
        else:
            cost_type = COST_PLANNER_EXPECTED[rec_name]
            print(f"✅ Tier {tier}: '{rec_name}' → Cost Planner: '{cost_type}'")
    
    return all_valid


def validate_flags_for_services():
    """Validate that required flags are generated for additional_services."""
    print("\n" + "="*70)
    print("VALIDATION: Additional Services Flags")
    print("="*70)
    
    test_cases = [
        {
            "name": "Moderate Cognitive (should set cognitive_risk)",
            "answers": {"memory_changes": "Moderate memory or thinking issues"},
            "expected_flags": ["cognitive_risk", "cog_moderate"]
        },
        {
            "name": "Severe Cognitive (should set cognitive_risk)",
            "answers": {"memory_changes": "Severe memory issues or diagnosis like dementia or Alzheimer's"},
            "expected_flags": ["cognitive_risk", "cog_severe"]
        },
        {
            "name": "Complex Meds (should set meds_management_needed)",
            "answers": {"meds_complexity": "Complex – many meds or caregiver-managed"},
            "expected_flags": ["meds_management_needed"]
        },
        {
            "name": "Moderate Meds (should set meds_management_needed)",
            "answers": {"meds_complexity": "Moderate – daily meds, some complexity"},
            "expected_flags": ["meds_management_needed"]
        },
        {
            "name": "Multiple Falls (should set fall_risk)",
            "answers": {"falls": "Multiple falls"},
            "expected_flags": ["fall_risk", "falls_multiple"]
        },
    ]
    
    all_valid = True
    for test in test_cases:
        result = derive_outcome(test["answers"], {})
        flags_present = all(flag in result.flags for flag in test["expected_flags"])
        
        if flags_present:
            print(f"✅ {test['name']}")
            print(f"   Flags: {sorted([f for f in result.flags.keys() if f in test['expected_flags']])}")
        else:
            print(f"❌ {test['name']}")
            print(f"   Expected: {test['expected_flags']}")
            print(f"   Got: {sorted(result.flags.keys())}")
            all_valid = False
    
    return all_valid


def validate_outcome_contract_structure():
    """Validate OutcomeContract structure for handoff."""
    print("\n" + "="*70)
    print("VALIDATION: OutcomeContract Structure")
    print("="*70)
    
    test_answers = {
        "memory_changes": "Moderate memory or thinking issues",
        "mobility": "Uses cane or walker",
        "help_overall": "Regular – needs daily assistance",
        "primary_support": "Family/friends",
        "hours_per_day": "4–8 hours",
        "meds_complexity": "Moderate – daily meds, some complexity",
        "falls": "One fall",
        "chronic_conditions": ["Diabetes"]
    }
    
    result = derive_outcome(test_answers, {})
    
    required_fields = {
        "recommendation": str,
        "confidence": (int, float),
        "flags": dict,
        "tags": list,
        "domain_scores": dict,
        "summary": dict,
        "routing": dict,
        "audit": dict
    }
    
    all_valid = True
    for field, expected_type in required_fields.items():
        value = getattr(result, field, None)
        if value is None:
            print(f"❌ Missing field: {field}")
            all_valid = False
        elif not isinstance(value, expected_type):
            print(f"❌ Wrong type for {field}: expected {expected_type}, got {type(value)}")
            all_valid = False
        else:
            print(f"✅ {field}: {type(value).__name__}")
    
    # Validate summary contains required keys
    summary_keys = ["points", "total_score", "tier"]
    for key in summary_keys:
        if key not in result.summary:
            print(f"❌ Missing summary key: {key}")
            all_valid = False
        else:
            print(f"✅ summary.{key}: {type(result.summary[key]).__name__}")
    
    return all_valid


def validate_cost_planner_integration():
    """Simulate Cost Planner mapping logic."""
    print("\n" + "="*70)
    print("VALIDATION: Cost Planner Integration")
    print("="*70)
    
    # Test each tier
    test_scenarios = [
        (0, "Independent / In-Home", "no_care"),
        (1, "In-Home Care", "in_home_care"),
        (2, "Assisted Living", "assisted_living"),
        (3, "Memory Care", "memory_care"),
        (4, "High-Acuity Memory Care", "memory_care_high_acuity"),
    ]
    
    all_valid = True
    for tier, expected_rec, expected_cost_type in test_scenarios:
        actual_rec = TIER_NAMES.get(tier)
        if actual_rec != expected_rec:
            print(f"❌ Tier {tier}: Expected '{expected_rec}', got '{actual_rec}'")
            all_valid = False
        else:
            actual_cost_type = COST_PLANNER_EXPECTED.get(actual_rec, "UNKNOWN")
            if actual_cost_type != expected_cost_type:
                print(f"❌ '{actual_rec}' maps to '{actual_cost_type}', expected '{expected_cost_type}'")
                all_valid = False
            else:
                print(f"✅ Tier {tier}: '{actual_rec}' → '{actual_cost_type}'")
    
    return all_valid


def main():
    print("\n" + "="*70)
    print("GCP V3 OUTPUT VALIDATION")
    print("Validating compatibility with Cost Planner & additional_services")
    print("="*70)
    
    results = {
        "Recommendation Strings": validate_recommendation_strings(),
        "Additional Services Flags": validate_flags_for_services(),
        "OutcomeContract Structure": validate_outcome_contract_structure(),
        "Cost Planner Integration": validate_cost_planner_integration(),
    }
    
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ GCP v3 output is compatible with Cost Planner and additional_services")
        return 0
    else:
        print("\n⚠️  SOME VALIDATIONS FAILED")
        print("❌ Fix issues before deploying")
        return 1


if __name__ == "__main__":
    sys.exit(main())
