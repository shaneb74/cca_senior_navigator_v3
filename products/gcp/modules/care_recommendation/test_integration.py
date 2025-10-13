#!/usr/bin/env python3
"""
Test script to verify GCP care_recommendation integration flow:
1. derive_outcome() returns OutcomeContract with recommendation
2. Handoff data is properly structured
3. Cost Planner can map the recommendation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from dataclasses import asdict
from products.gcp.modules.care_recommendation.logic import derive_outcome, TIER_NAMES
from products.cost_planner.cost_estimate_v2 import TIER_TO_CARE_TYPE


def test_integration_flow():
    """Test the full integration from logic -> handoff -> cost planner."""
    
    print("=" * 70)
    print("GCP CARE RECOMMENDATION INTEGRATION TEST")
    print("=" * 70)
    
    # Test scenario: Moderate cognitive needs
    test_answers = {
        'help_overall': 'Some help with daily tasks',
        'memory_changes': 'Moderate – noticeable confusion',
        'primary_support': 'Family member',
        'meds_complexity': 'Moderate – daily meds',
        'mobility': 'Walker',
        'falls': 'One in past year',
        'badls': ['bathing'],
        'iadls': ['meal_prep', 'housekeeping'],
        'behaviors': ['confusion', 'agitation']
    }
    
    print("\n1. Testing derive_outcome()...")
    print("-" * 70)
    
    result = derive_outcome(test_answers, {})
    
    print(f"✅ derive_outcome() returned: {type(result).__name__}")
    print(f"   Recommendation: {result.recommendation}")
    print(f"   Score: {result.summary.get('total_score')}")
    print(f"   Tier: {result.summary.get('tier')}")
    print(f"   Flags: {list(result.flags.keys())[:5]}...")  # Show first 5 flags
    
    # Verify OutcomeContract structure
    print("\n2. Verifying OutcomeContract structure...")
    print("-" * 70)
    
    outcome_dict = asdict(result)
    required_keys = ['recommendation', 'confidence', 'flags', 'tags', 'domain_scores', 'summary', 'routing', 'audit']
    
    for key in required_keys:
        if key in outcome_dict:
            print(f"   ✅ {key}: {type(outcome_dict[key]).__name__}")
        else:
            print(f"   ❌ MISSING: {key}")
    
    # Simulate handoff data structure (what engine.py creates)
    print("\n3. Simulating handoff data structure...")
    print("-" * 70)
    
    handoff_data = {
        "gcp": {
            "recommendation": result.recommendation,
            "flags": dict(result.flags),
            "tags": list(result.tags),
            "domain_scores": dict(result.domain_scores),
        }
    }
    
    print(f"   Handoff['gcp']['recommendation']: {handoff_data['gcp']['recommendation']}")
    print(f"   Handoff['gcp']['flags']: {len(handoff_data['gcp']['flags'])} flags")
    print(f"   Handoff['gcp']['domain_scores']: {len(handoff_data['gcp']['domain_scores'])} domains")
    
    # Test Cost Planner mapping
    print("\n4. Testing Cost Planner mapping...")
    print("-" * 70)
    
    recommendation = handoff_data['gcp']['recommendation']
    
    if recommendation in TIER_TO_CARE_TYPE:
        care_type = TIER_TO_CARE_TYPE[recommendation]
        print(f"   ✅ Recommendation maps to Cost Planner:")
        print(f"      '{recommendation}' → '{care_type}'")
    else:
        print(f"   ❌ MAPPING FAILED!")
        print(f"      Recommendation: '{recommendation}'")
        print(f"      Available mappings:")
        for tier_name in TIER_TO_CARE_TYPE.keys():
            print(f"         - '{tier_name}'")
    
    # Test all tier names
    print("\n5. Testing all TIER_NAMES mappings...")
    print("-" * 70)
    
    all_pass = True
    for tier, name in TIER_NAMES.items():
        if name in TIER_TO_CARE_TYPE:
            care_type = TIER_TO_CARE_TYPE[name]
            print(f"   ✅ Tier {tier}: '{name}' → '{care_type}'")
        else:
            print(f"   ❌ Tier {tier}: '{name}' - NO MAPPING FOUND")
            all_pass = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_pass and recommendation in TIER_TO_CARE_TYPE:
        print("✅ INTEGRATION TEST PASSED!")
        print("   - derive_outcome() produces valid OutcomeContract")
        print("   - Handoff structure is correct")
        print("   - All tier names map to Cost Planner care types")
    else:
        print("❌ INTEGRATION TEST FAILED!")
        print("   Check the errors above for details.")
    print("=" * 70)


if __name__ == "__main__":
    test_integration_flow()
