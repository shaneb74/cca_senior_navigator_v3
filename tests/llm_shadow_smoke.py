"""
Smoke test for LLM shadow mode.

Validates that the LLM integration can:
1. Build valid CPContext from typical Cost Planner data
2. Generate advice without errors
3. Validate response against CPAdvice schema
4. Handle tier normalization and forbidden terms
"""

from ai.navi_engine import (
    FORBIDDEN_TERMS,
    generate_safe,
    generate_safe_with_normalization,
    normalize_tier,
)
from ai.schemas import CPContext


def test_shadow_mode_basic():
    """Test basic shadow mode generation with typical context."""

    # Build typical Cost Planner context
    context = CPContext(
        tier="assisted_living",
        has_partner=True,
        move_preference="within_6_months",
        keep_home=False,
        monthly_adjusted=5500.0,
        region="pacific",
        flags=["homeowner", "medicaid_planning_needed"],
        top_reasons=["mobility_issues", "medication_management", "companionship"],
    )

    print("\n" + "="*60)
    print("LLM SHADOW MODE SMOKE TEST")
    print("="*60)
    print("\nContext:")
    print(f"  Tier: {context.tier}")
    print(f"  Has Partner: {context.has_partner}")
    print(f"  Monthly Cost: ${context.monthly_adjusted:,.2f}")
    print(f"  Region: {context.region}")
    print(f"  Flags: {context.flags}")
    print(f"  Top Reasons: {context.top_reasons}")

    # Generate advice
    print("\nGenerating advice...")
    success, advice = generate_safe(context, mode="shadow")

    # Report results
    print("\nResults:")
    print(f"  Success: {success}")

    if success and advice:
        print(f"  Messages: {len(advice.messages)}")
        print(f"  Insights: {len(advice.insights)}")
        print(f"  Questions: {len(advice.questions_next)}")
        print(f"  Adjustments: {len(advice.proposed_adjustments or {})}")
        print(f"  Confidence: {advice.confidence:.2f}")

        print("\n--- Sample Messages ---")
        for i, msg in enumerate(advice.messages, 1):
            print(f"{i}. {msg}")

        print("\n--- Sample Insights ---")
        for i, insight in enumerate(advice.insights, 1):
            print(f"{i}. {insight}")

        print("\n--- Sample Questions ---")
        for i, q in enumerate(advice.questions_next, 1):
            print(f"{i}. {q}")

        print("\n" + "="*60)
        print("✅ SMOKE TEST PASSED")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("⚠️  SMOKE TEST FAILED - No advice generated")
        print("    (This is expected if OPENAI_API_KEY not set)")
        print("="*60)


def test_shadow_mode_edge_cases():
    """Test edge cases: minimal context, no flags, etc."""

    print("\n" + "="*60)
    print("EDGE CASE TESTS")
    print("="*60)

    # Test 1: Minimal context
    print("\n[Test 1] Minimal context (no flags, no reasons)...")
    context_minimal = CPContext(
        tier="none",
        has_partner=False,
        monthly_adjusted=0.0,
        region="midwest",
    )
    success, advice = generate_safe(context_minimal, mode="shadow")
    print(f"  Result: {'✅ Success' if success else '⚠️  Failed'}")

    # Test 2: High-acuity care
    print("\n[Test 2] High-acuity memory care...")
    context_high_acuity = CPContext(
        tier="memory_care_high_acuity",
        has_partner=True,
        monthly_adjusted=12000.0,
        region="northeast",
        flags=["veteran", "medicaid_likely"],
        top_reasons=["advanced_dementia", "safety_concerns"],
    )
    success, advice = generate_safe(context_high_acuity, mode="shadow")
    print(f"  Result: {'✅ Success' if success else '⚠️  Failed'}")

    # Test 3: Home care preference
    print("\n[Test 3] In-home care with keep_home=True...")
    context_home = CPContext(
        tier="in_home",
        has_partner=True,
        keep_home=True,
        monthly_adjusted=4500.0,
        region="south",
        flags=["homeowner", "strong_family_support"],
        top_reasons=["prefer_aging_at_home"],
    )
    success, advice = generate_safe(context_home, mode="shadow")
    print(f"  Result: {'✅ Success' if success else '⚠️  Failed'}")

    print("\n" + "="*60)
    print("EDGE CASE TESTS COMPLETE")
    print("="*60)


def test_tier_normalization():
    """Test tier normalization and forbidden terms filtering."""

    print("\n" + "="*60)
    print("TIER NORMALIZATION & GUARDRAIL TESTS")
    print("="*60)

    # Test 1: Alias normalization
    print("\n[Test 1] Tier alias normalization...")
    test_cases = [
        ("in_home_care", "in_home"),
        ("home_care", "in_home"),
        ("no_care", "none"),
        ("assisted_living", "assisted_living"),  # Already canonical
        ("memory_care", "memory_care"),  # Already canonical
    ]

    for input_tier, expected in test_cases:
        result = normalize_tier(input_tier)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_tier}' → '{result}' (expected: '{expected}')")

    # Test 2: Forbidden tiers rejected
    print("\n[Test 2] Forbidden tiers rejected...")
    forbidden_tiers = ["skilled_nursing", "independent_living", "nursing_home", "invalid_tier"]

    for tier in forbidden_tiers:
        result = normalize_tier(tier)
        status = "✅" if result is None else "❌"
        print(f"  {status} '{tier}' → {result} (expected: None)")

    # Test 3: Integration test with generate_safe_with_normalization
    print("\n[Test 3] Integration: Alias normalization in generate_safe_with_normalization...")
    success, advice = generate_safe_with_normalization(
        tier="in_home_care",  # Alias
        has_partner=False,
        move_preference=None,
        keep_home=True,
        monthly_adjusted=3000.0,
        region="midwest",
        flags=[],
        top_reasons=[],
        mode="shadow",
    )
    print(f"  Result: {'✅ Success (alias normalized to in_home)' if success else '⚠️  Failed'}")

    # Test 4: Integration test with forbidden tier
    print("\n[Test 4] Integration: Forbidden tier skipped...")
    success, advice = generate_safe_with_normalization(
        tier="skilled_nursing",  # Forbidden
        has_partner=False,
        move_preference=None,
        keep_home=False,
        monthly_adjusted=8000.0,
        region="south",
        flags=[],
        top_reasons=[],
        mode="shadow",
    )
    expected_fail = not success
    status = "✅" if expected_fail else "❌"
    print(f"  {status} Forbidden tier rejected: {expected_fail} (expected: True)")

    # Test 5: Check forbidden terms don't appear in advice
    print("\n[Test 5] Forbidden terms filter...")
    if success and advice:
        has_forbidden = False
        all_text = " ".join(advice.messages + advice.insights + advice.questions_next).lower()
        for term in FORBIDDEN_TERMS:
            if term in all_text:
                print(f"  ❌ Found forbidden term: '{term}'")
                has_forbidden = True

        if not has_forbidden:
            print("  ✅ No forbidden terms found in advice")
    else:
        print("  ✅ No advice generated (forbidden tier correctly skipped)")

    print("\n" + "="*60)
    print("TIER NORMALIZATION & GUARDRAIL TESTS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    # Run smoke tests
    test_shadow_mode_basic()
    test_shadow_mode_edge_cases()
    test_tier_normalization()
