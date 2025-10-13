"""
Quick test script for logic_v3.py hybrid scoring.

Run: python test_logic_v3.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from products.gcp.modules.care_recommendation.logic_v3 import derive_outcome


def test_scenario(name: str, answers: dict, expected_tier: int = None):
    """Test a scoring scenario."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    
    result = derive_outcome(answers, {"debug": True})
    
    print(f"\n✅ RESULT:")
    print(f"  Recommendation: {result.recommendation}")
    print(f"  Tier: {result.summary.get('tier')}")
    print(f"  Score: {result.summary.get('total_score')}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Flags: {sorted(result.flags.keys())}")
    print(f"\n📋 SUMMARY:")
    for point in result.summary.get('points', []):
        print(f"  • {point}")
    
    if expected_tier is not None:
        actual_tier = result.summary.get('tier')
        status = "✅ PASS" if actual_tier == expected_tier else f"❌ FAIL (expected tier {expected_tier})"
        print(f"\n{status}")
    
    return result


def main():
    print("\n" + "="*60)
    print("TESTING GCP V3 HYBRID SCORING LOGIC")
    print("="*60)
    
    # Test 1: High-acuity memory care (CSV OVERRIDE rule)
    test_scenario(
        "High-Acuity Memory Care Override",
        {
            "memory_changes": "Severe memory issues or diagnosis like dementia or Alzheimer's",
            "primary_support": "No regular support",
            "hours_per_day": "Less than 1 hour",  # Added to trigger no_support flag
            "mobility": "Uses cane or walker",
            "falls": "One fall",
            "help_overall": "Regular – needs daily assistance",
            "meds_complexity": "Moderate – daily meds, some complexity"
        },
        expected_tier=4
    )
    
    # Test 2: Independent senior
    test_scenario(
        "Independent Senior - No Care Needed",
        {
            "memory_changes": "No concerns",
            "primary_support": "Family/friends",  # Has family nearby but doesn't need daily help
            "mobility": "Walks independently",
            "falls": "No falls in the past six months",
            "help_overall": "None – fully independent",  
            "meds_complexity": "None",  
            "chronic_conditions": [],
            "badls": [],
            "iadls": [],
            "hours_per_day": "Less than 1 hour",  # Occasional check-ins only
            "mood": "Great – always positive"
        },
        expected_tier=0
    )
    
    # Test 3: Assisted living - moderate needs
    test_scenario(
        "Assisted Living - Moderate Needs",
        {
            "memory_changes": "Occasional forgetfulness",
            "primary_support": "Family/friends",
            "mobility": "Uses cane or walker",
            "falls": "One fall",
            "help_overall": "Regular – needs daily assistance",
            "meds_complexity": "Moderate – daily meds, some complexity",
            "chronic_conditions": ["Diabetes", "Hypertension"],
            "badls": ["Bathing/Showering"],
            "iadls": ["Meal preparation", "Housekeeping"],
            "hours_per_day": "4–8 hours",
            "mood": "Mostly good",
            "isolation": "No – easily accessible"
        },
        expected_tier=2
    )
    
    # Test 4: Memory care - cognitive decline with behaviors
    test_scenario(
        "Memory Care - Moderate Cognitive + Behaviors",
        {
            "memory_changes": "Moderate memory or thinking issues",
            "behaviors": ["Wandering", "Confusion or disorientation", "Sundowning"],
            "primary_support": "Family/friends",
            "mobility": "Uses wheelchair or scooter",
            "falls": "Multiple falls",
            "help_overall": "Extensive – needs full-time support",
            "meds_complexity": "Complex – many meds or caregiver-managed",
            "chronic_conditions": ["Diabetes", "CHF", "Stroke"],
            "badls": ["Bathing/Showering", "Toileting", "Transferring"],
            "iadls": ["Meal preparation", "Medication management"],
            "hours_per_day": "24-hour support",
            "mood": "Okay – ups and downs"
        },
        expected_tier=3
    )
    
    # Test 5: In-home with support
    test_scenario(
        "In-Home with Support",
        {
            "memory_changes": "Occasional forgetfulness",
            "primary_support": "Paid caregiver",
            "mobility": "Uses cane or walker",
            "falls": "No falls in the past six months",
            "help_overall": "Occasional – some help with a few tasks",
            "meds_complexity": "Simple – a few meds, easy to manage",
            "chronic_conditions": ["Hypertension"],
            "badls": [],
            "iadls": ["Meal preparation", "Transportation"],
            "hours_per_day": "4–8 hours",
            "mood": "Mostly good"
        },
        expected_tier=1
    )
    
    # Test 6: Falls + No Support Override
    test_scenario(
        "Assisted Living - Falls + No Support Override",
        {
            "memory_changes": "No concerns",
            "primary_support": "No regular support",
            "mobility": "Uses cane or walker",
            "falls": "Multiple falls",
            "help_overall": "Occasional – some help with a few tasks",
            "meds_complexity": "Simple – a few meds, easy to manage",
            "chronic_conditions": [],
            "badls": [],
            "iadls": [],
            "hours_per_day": "Less than 1 hour",
            "mood": "Great – always positive"
        },
        expected_tier=2  # Should be escalated to Assisted Living
    )
    
    # Test 7: Strong support modifier
    test_scenario(
        "Strong Support Reduces Tier",
        {
            "memory_changes": "Occasional forgetfulness",
            "primary_support": "Family/friends",
            "mobility": "Uses cane or walker",
            "falls": "One fall",
            "help_overall": "Regular – needs daily assistance",
            "meds_complexity": "Moderate – daily meds, some complexity",
            "chronic_conditions": ["Diabetes"],
            "badls": ["Bathing/Showering"],
            "iadls": ["Meal preparation"],
            "hours_per_day": "24-hour support",  # Strong support
            "mood": "Mostly good"
        },
        expected_tier=1  # Should be reduced from 2 to 1 by strong support modifier
    )
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
