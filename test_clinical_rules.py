#!/usr/bin/env python3
"""
Test clinical escalation rules in hours engine.

Demonstrates deterministic fallback that matches LLM reasoning patterns.
"""
from ai.hours_engine import calculate_baseline_hours_weighted
from ai.hours_schemas import HoursContext


def test_case(name: str, context: HoursContext, expected_band: str | None = None):
    """Run test case and display results."""
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")
    
    # Display inputs
    print(f"\nInputs:")
    print(f"  BADLs: {context.badls_count} ({', '.join(context.badls_list) if context.badls_list else 'none'})")
    print(f"  IADLs: {context.iadls_count} ({', '.join(context.iadls_list) if context.iadls_list else 'none'})")
    print(f"  Cognitive: {context.cognitive_level or 'none'}")
    print(f"  Falls: {context.falls or 'none'}")
    print(f"  Mobility: {context.mobility or 'independent'}")
    print(f"  Overnight: {context.overnight_needed}")
    print(f"  Meds complexity: {context.meds_complexity or 'none'}")
    print(f"  Primary support: {context.primary_support or 'unknown'}")
    
    behaviors = []
    if context.wandering:
        behaviors.append("wandering")
    if context.aggression:
        behaviors.append("aggression")
    if context.sundowning:
        behaviors.append("sundowning")
    if getattr(context, 'elopement', False):
        behaviors.append("elopement")
    if getattr(context, 'confusion', False):
        behaviors.append("confusion")
    
    if behaviors:
        print(f"  Behaviors: {', '.join(behaviors)}")
    
    # Calculate
    result = calculate_baseline_hours_weighted(context)
    
    print(f"\n✅ Result: {result}")
    
    if expected_band:
        status = "✅ PASS" if result == expected_band else "❌ FAIL"
        print(f"Expected: {expected_band} → {status}")
    
    return result


def main():
    """Run all test cases."""
    print("\n" + "="*70)
    print("CLINICAL RULES TEST SUITE")
    print("Testing deterministic escalation logic matching LLM patterns")
    print("="*70)
    
    # Test 1: Toileting rule (availability requirement)
    test_case(
        "Rule 1: Toileting requires availability",
        HoursContext(
            badls_count=1,
            badls_list=["toileting"],
            iadls_count=0,
            iadls_list=[],
            cognitive_level="none",
        ),
        expected_band="4-8h"  # Should escalate from <1h due to toileting
    )
    
    # Test 2: Moderate cognitive + multiple risks
    test_case(
        "Rule 2: Moderate cognitive + 3 safety risks → 24h",
        HoursContext(
            badls_count=3,
            badls_list=["bathing", "dressing", "toileting"],
            iadls_count=2,
            iadls_list=["meal_preparation", "medication_management"],
            cognitive_level="moderate",
            wandering=True,
            sundowning=True,
            falls="multiple",
            mobility="walker",
        ),
        expected_band="24h"  # Should escalate to 24h due to cognitive + multiple risks
    )
    
    # Test 3: Overnight needs + multiple risk factors
    test_case(
        "Rule 3: Overnight needs + multiple risks → 24h",
        HoursContext(
            badls_count=2,
            badls_list=["bathing", "toileting"],
            iadls_count=1,
            iadls_list=["medication_management"],
            cognitive_level="mild",
            overnight_needed=True,
            falls="multiple",
            meds_complexity="complex",
            wandering=True,
        ),
        expected_band="24h"  # Overnight + 3 risks (falls, meds, wandering)
    )
    
    # Test 4: Multiple falls + mobility + ADLs
    test_case(
        "Rule 4: Multiple falls + walker + ADLs → 4-8h minimum",
        HoursContext(
            badls_count=2,
            badls_list=["bathing", "dressing"],
            iadls_count=1,
            iadls_list=["housekeeping"],
            falls="multiple",
            mobility="walker",
            cognitive_level="none",
        ),
        expected_band="4-8h"  # Falls + mobility + ADLs → safety escalation
    )
    
    # Test 5: Complex meds + cognitive impairment
    test_case(
        "Rule 5: Complex meds + moderate cognitive → 4-8h minimum",
        HoursContext(
            badls_count=1,
            badls_list=["medication_management"],
            iadls_count=2,
            iadls_list=["medication_management", "meal_preparation"],
            cognitive_level="moderate",
            meds_complexity="complex",
        ),
        expected_band="4-8h"  # Complex meds + cognitive → supervision needed
    )
    
    # Test 6: No support + moderate needs
    test_case(
        "Rule 6: No regular support + moderate needs → 4-8h",
        HoursContext(
            badls_count=2,
            badls_list=["bathing", "dressing"],
            iadls_count=3,
            iadls_list=["meal_preparation", "housekeeping", "transportation"],
            primary_support="none",
            cognitive_level="mild",
        ),
        expected_band="4-8h"  # No support + needs → escalate
    )
    
    # Test 7: Minimal needs (no escalation)
    test_case(
        "No escalation: Light support only",
        HoursContext(
            badls_count=1,
            badls_list=["bathing"],
            iadls_count=1,
            iadls_list=["housekeeping"],
            cognitive_level="none",
        ),
        expected_band="<1h"  # Should stay at <1h (no escalation triggers)
    )
    
    # Test 8: Complex case with all 9 behaviors
    test_case(
        "Complex: All 9 behaviors + severe cognitive",
        HoursContext(
            badls_count=4,
            badls_list=["bathing", "dressing", "toileting", "eating"],
            iadls_count=3,
            iadls_list=["meal_preparation", "medication_management", "finances"],
            cognitive_level="severe",
            wandering=True,
            aggression=True,
            sundowning=True,
            repetitive_questions=True,
            # Add remaining 5 behaviors
            elopement=True,
            confusion=True,
            judgment=True,
            hoarding=True,
            sleep=True,
            falls="frequent",
            mobility="wheelchair",
            overnight_needed=True,
            meds_complexity="complex",
        ),
        expected_band="24h"  # Should definitely be 24h
    )
    
    print(f"\n{'='*70}")
    print("TESTS COMPLETE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

