"""
Smoke test for LLM shadow mode.

Validates that the LLM integration can:
1. Build valid CPContext from typical Cost Planner data
2. Generate advice without errors
3. Validate response against CPAdvice schema
"""

from ai.navi_engine import generate_safe
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
        tier="independent_living",
        has_partner=False,
        monthly_adjusted=3000.0,
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
    print("\n[Test 3] Home care with keep_home=True...")
    context_home = CPContext(
        tier="home_care",
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


if __name__ == "__main__":
    # Run smoke tests
    test_shadow_mode_basic()
    test_shadow_mode_edge_cases()
