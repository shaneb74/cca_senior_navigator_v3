"""
Quick validation script for Navi & Cost Planner enhancements

Run this to verify:
1. COST_ADJUSTMENTS dictionary is valid
2. get_active_adjustments() calculates correctly
3. Personalization detection logic works
"""

def test_cost_adjustments():
    """Test COST_ADJUSTMENTS dictionary and calculations."""
    print("=" * 60)
    print("TEST 1: COST_ADJUSTMENTS Dictionary")
    print("=" * 60)
    
    from products.cost_planner_v2.utils.cost_calculator import COST_ADJUSTMENTS, CostCalculator
    
    # Verify all flags are present
    expected_flags = [
        "memory_support",
        "mobility_limited", 
        "adl_support_high",
        "medication_management",
        "behavioral_concerns",
        "falls_risk",
        "chronic_conditions"
    ]
    
    print(f"\nExpected flags: {len(expected_flags)}")
    print(f"Actual flags: {len(COST_ADJUSTMENTS)}")
    
    missing = [f for f in expected_flags if f not in COST_ADJUSTMENTS]
    if missing:
        print(f"❌ MISSING FLAGS: {missing}")
        return False
    
    print("✅ All expected flags present")
    
    # Verify structure of each adjustment
    print("\nFlag Details:")
    for flag_id, data in COST_ADJUSTMENTS.items():
        print(f"  {flag_id}:")
        print(f"    - Percentage: {data['percentage']*100:.0f}%")
        print(f"    - Label: {data['label']}")
        print(f"    - Rationale: {data['rationale'][:50]}...")
        
        # Verify required keys
        required_keys = ['percentage', 'label', 'rationale']
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            print(f"    ❌ MISSING KEYS: {missing_keys}")
            return False
    
    print("\n✅ All flags have required structure")
    
    # Test cumulative calculation
    print("\n" + "=" * 60)
    print("TEST 2: Cumulative Calculation")
    print("=" * 60)
    
    # Scenario: $5000 base with cognitive + mobility + medication flags
    test_flags = ["memory_support", "mobility_limited", "medication_management"]
    base_amount = 5000.0
    care_tier = "assisted_living"
    
    print(f"\nScenario:")
    print(f"  Base Amount: ${base_amount:,.0f}")
    print(f"  Active Flags: {', '.join(test_flags)}")
    print(f"  Care Tier: {care_tier}")
    
    adjustments = CostCalculator.get_active_adjustments(test_flags, care_tier, base_amount)
    
    print(f"\nAdjustments Applied:")
    running_total = base_amount
    for adj in adjustments:
        print(f"  {adj['label']}: +{adj['percentage']:.0f}% = ${adj['amount']:,.0f}")
        running_total += adj['amount']
    
    total_increase = sum(adj['amount'] for adj in adjustments)
    print(f"\nTotal Increase: ${total_increase:,.0f}")
    print(f"Final Amount: ${running_total:,.0f}")
    
    # Verify cumulative (not additive)
    # Expected: 5000 * 1.20 = 6000, then 6000 * 1.15 = 6900, then 6900 * 1.08 = 7452
    expected_final = base_amount * 1.20 * 1.15 * 1.08
    if abs(running_total - expected_final) < 1.0:  # Allow $1 rounding error
        print(f"✅ Cumulative calculation correct (expected ${expected_final:,.0f})")
    else:
        print(f"❌ Calculation mismatch (expected ${expected_final:,.0f}, got ${running_total:,.0f})")
        return False
    
    # Test high-acuity tier
    print("\n" + "=" * 60)
    print("TEST 3: High-Acuity Tier Adjustment")
    print("=" * 60)
    
    high_acuity_flags = []
    high_acuity_base = 6500.0
    high_acuity_tier = "memory_care_high_acuity"
    
    print(f"\nScenario:")
    print(f"  Base Amount: ${high_acuity_base:,.0f}")
    print(f"  Active Flags: (none)")
    print(f"  Care Tier: {high_acuity_tier}")
    
    high_acuity_adjustments = CostCalculator.get_active_adjustments(
        high_acuity_flags, 
        high_acuity_tier, 
        high_acuity_base
    )
    
    if len(high_acuity_adjustments) == 1 and high_acuity_adjustments[0]['flag_id'] == 'high_acuity_tier':
        print(f"✅ High-acuity adjustment applied: +{high_acuity_adjustments[0]['percentage']:.0f}%")
        print(f"   Amount: ${high_acuity_adjustments[0]['amount']:,.0f}")
    else:
        print(f"❌ High-acuity adjustment not found or incorrect")
        return False
    
    return True


def test_personalization_detection():
    """Test personalization detection logic."""
    print("\n" + "=" * 60)
    print("TEST 4: Personalization Detection (Navi Recommended)")
    print("=" * 60)
    
    from core.additional_services import _detect_personalization, REGISTRY
    
    # Mock context with some flags
    test_ctx = {
        "flags": {
            "cognitive_risk": True,
            "fall_risk": True,
            "meds_management_needed": True
        }
    }
    
    print("\nTest Context Flags:")
    for flag, value in test_ctx["flags"].items():
        print(f"  - {flag}: {value}")
    
    # Test tiles that should be "personalized" (Navi Recommended)
    personalized_tiles = [
        "omcare",  # triggered by meds_management_needed
        "seniorlife_ai",  # triggered by cognitive_risk
        "fall_prevention"  # triggered by fall_risk
    ]
    
    print("\nExpected Navi Recommended Tiles:")
    for tile_key in personalized_tiles:
        tile = next((t for t in REGISTRY if t['key'] == tile_key), None)
        if tile:
            result = _detect_personalization(tile, test_ctx)
            if result == "personalized":
                print(f"  ✅ {tile_key}: {result} → '🤖 Navi Recommended' label + blue gradient")
            else:
                print(f"  ❌ {tile_key}: {result} (expected 'personalized')")
                return False
    
    # Test tiles that should have NO label (general utilities)
    utility_tiles = ["learning_center", "care_network"]
    
    print("\nExpected NO Label (General Utilities):")
    for tile_key in utility_tiles:
        tile = next((t for t in REGISTRY if t['key'] == tile_key), None)
        if tile:
            result = _detect_personalization(tile, test_ctx)
            if result is None:
                print(f"  ✅ {tile_key}: {result} → NO label, NO gradient (standard card)")
            else:
                print(f"  ❌ {tile_key}: {result} (expected None)")
                return False
    
    print("\n💡 KEY RULE: Only flag-triggered services get 'Navi Recommended' label")
    print("   General utilities appear without labels or gradients")
    
    return True


if __name__ == "__main__":
    print("\n" + "🧪 NAVI & COST PLANNER ENHANCEMENTS - VALIDATION TESTS" + "\n")
    
    success = True
    
    try:
        if not test_cost_adjustments():
            success = False
    except Exception as e:
        print(f"\n❌ Cost adjustments test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    try:
        if not test_personalization_detection():
            success = False
    except Exception as e:
        print(f"\n❌ Personalization test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nReady for manual testing in Streamlit!")
        print("Run: streamlit run app.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print("\nReview errors above and fix before deploying.")
    print()
