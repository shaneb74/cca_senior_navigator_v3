#!/usr/bin/env python3
"""
Test weighted hours system against known scenarios.
"""
from ai.hours_schemas import HoursContext
from ai.hours_engine import baseline_hours, calculate_baseline_hours_weighted

def test_case(name: str, context: HoursContext):
    """Run single test case."""
    old = baseline_hours(context)
    new = calculate_baseline_hours_weighted(context)
    print(f"\n{name}")
    print(f"  Old (simple thresholds): {old}")
    print(f"  New (weighted scoring): {new}")
    print(f"  {'✅ CHANGED' if old != new else '⚠️  SAME'}")
    return old, new

def main():
    print("=" * 60)
    print("WEIGHTED HOURS SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Light needs (1 BADL, no cognitive)
    print("\n[Test 1: Light Needs]")
    test_case(
        "1 BADL (bathing), no cognitive issues",
        HoursContext(
            badls_count=1,
            badls_list=["bathing"],
            iadls_count=0,
            iadls_list=[],
            cognitive_level="none",
        )
    )
    
    # Test 2: Moderate needs (2 BADLs, mild cognitive)
    print("\n[Test 2: Moderate Needs]")
    test_case(
        "2 BADLs (bathing, dressing), mild cognitive",
        HoursContext(
            badls_count=2,
            badls_list=["bathing", "dressing"],
            iadls_count=0,
            iadls_list=[],
            cognitive_level="mild",
        )
    )
    
    # Test 3: Toileting needs (availability vs task time)
    print("\n[Test 3: Toileting Availability]")
    test_case(
        "Toileting only (should be higher due to 24/7 availability)",
        HoursContext(
            badls_count=1,
            badls_list=["toileting"],
            iadls_count=0,
            iadls_list=[],
            cognitive_level="none",
        )
    )
    
    # Test 4: Moderate dementia with wandering
    print("\n[Test 4: Dementia + Wandering]")
    test_case(
        "3 BADLs + moderate dementia + wandering",
        HoursContext(
            badls_count=3,
            badls_list=["bathing", "dressing", "toileting"],
            iadls_count=0,
            iadls_list=[],
            cognitive_level="moderate",
            wandering=True,
        )
    )
    
    # Test 5: Heavy needs (overnight + severe cognitive)
    print("\n[Test 5: Heavy Needs]")
    test_case(
        "Toileting + severe cognitive + overnight",
        HoursContext(
            badls_count=1,
            badls_list=["toileting"],
            iadls_count=0,
            iadls_list=[],
            cognitive_level="severe",
            overnight_needed=True,
        )
    )
    
    # Test 6: Multiple IADLs
    print("\n[Test 6: IADL Focus]")
    test_case(
        "3 IADLs (medication, meals, housekeeping)",
        HoursContext(
            badls_count=0,
            badls_list=[],
            iadls_count=3,
            iadls_list=["medication_management", "meal_preparation", "housekeeping"],
            cognitive_level="none",
        )
    )
    
    # Test 7: Fall risk multiplier
    print("\n[Test 7: Fall Risk]")
    test_case(
        "2 BADLs + multiple falls",
        HoursContext(
            badls_count=2,
            badls_list=["bathing", "transferring"],
            iadls_count=0,
            iadls_list=[],
            falls="multiple",
            cognitive_level="none",
        )
    )
    
    print("\n" + "=" * 60)
    print("KEY IMPROVEMENTS TO OBSERVE:")
    print("- Toileting should score higher (availability vs task time)")
    print("- Cognitive multipliers should increase hours proportionally")
    print("- Behavior flags should add incremental hours")
    print("- Fall risk should apply multiplier to total")
    print("=" * 60)

if __name__ == "__main__":
    main()
