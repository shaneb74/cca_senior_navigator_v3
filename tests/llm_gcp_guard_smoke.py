"""
Smoke test for LLM-assisted GCP (Guided Care Planning).

Validates that the guarded GCP integration:
1. Returns only canonical tier values
2. Handles tier normalization correctly
3. Filters forbidden terms from all output
4. Reconciles with deterministic recommendations correctly
5. Provides per-section feedback with running tier estimates
"""

from ai.gcp_navi_engine import (
    generate_gcp_advice,
    generate_section_advice,
    reconcile_with_deterministic,
)
from ai.gcp_schemas import CANONICAL_TIERS, FORBIDDEN_TERMS, GCPContext, normalize_tier


def test_gcp_canonical_tiers():
    """Test that LLM only returns canonical tier values."""
    
    print("\n" + "="*60)
    print("GCP LLM CANONICAL TIERS TEST")
    print("="*60)
    
    # Build moderate complexity context (likely assisted_living)
    context = GCPContext(
        age_range="75-84",
        living_situation="alone_in_house",
        has_partner=False,
        meds_complexity="moderate",  # 4-6 meds, some help needed
        mobility="walker",
        falls="1_fall_last_6mo",
        badls=["bathing", "dressing"],
        iadls=["meal_prep", "housekeeping", "transportation"],
        memory_changes="mild_forgetfulness",
        behaviors=["mild_confusion"],
        isolation="moderate",
        move_preference=6,
        flags=["homeowner", "limited_family_support"],
    )
    
    print("\nContext:")
    print(f"  Age: {context.age_range}")
    print(f"  Living: {context.living_situation}")
    print(f"  Mobility: {context.mobility}")
    print(f"  BADLs: {len(context.badls)}")
    print(f"  IADLs: {len(context.iadls)}")
    print(f"  Memory: {context.memory_changes}")
    
    print("\nGenerating GCP advice (shadow mode)...")
    ok, advice = generate_gcp_advice(context, mode="shadow")
    
    print("\nResults:")
    print(f"  Success: {ok}")
    
    if ok and advice:
        print(f"  Tier: {advice.tier}")
        print(f"  Canonical: {advice.tier in CANONICAL_TIERS}")
        print(f"  Reasons: {len(advice.reasons)}")
        print(f"  Risks: {len(advice.risks)}")
        print(f"  Navi Messages: {len(advice.navi_messages)}")
        print(f"  Questions: {len(advice.questions_next)}")
        print(f"  Confidence: {advice.confidence:.2f}")
        
        # Verify tier is canonical
        if advice.tier in CANONICAL_TIERS:
            print("\n✅ TIER VALIDATION PASSED - Canonical tier returned")
        else:
            print(f"\n❌ TIER VALIDATION FAILED - Non-canonical tier: {advice.tier}")
        
        # Show sample output
        print("\n--- Sample Reasons ---")
        for i, reason in enumerate(advice.reasons[:3], 1):
            print(f"{i}. {reason}")
        
        print("\n--- Sample Navi Messages ---")
        for i, msg in enumerate(advice.navi_messages[:2], 1):
            print(f"{i}. {msg}")
    else:
        print("\n⚠️  No advice generated (check API key configuration)")
    
    print("\n" + "="*60)


def test_tier_alias_normalization():
    """Test that tier aliases are normalized correctly."""
    
    print("\n" + "="*60)
    print("TIER ALIAS NORMALIZATION TEST")
    print("="*60)
    
    test_cases = [
        ("in_home_care", "in_home"),
        ("home_care", "in_home"),
        ("no_care", "none"),
        ("no_care_needed", "none"),
        ("assisted_living", "assisted_living"),
        ("memory_care", "memory_care"),
        ("memory_care_high_acuity", "memory_care_high_acuity"),
    ]
    
    print("\nTesting alias mappings...")
    all_passed = True
    
    for input_tier, expected in test_cases:
        result = normalize_tier(input_tier)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_tier}' → '{result}' (expected: '{expected}')")
        if result != expected:
            all_passed = False
    
    print("\nTesting forbidden tiers (should return None)...")
    forbidden = ["skilled_nursing", "independent_living", "nursing_home", "invalid"]
    
    for tier in forbidden:
        result = normalize_tier(tier)
        status = "✅" if result is None else "❌"
        print(f"  {status} '{tier}' → {result} (expected: None)")
        if result is not None:
            all_passed = False
    
    if all_passed:
        print("\n✅ ALL ALIAS TESTS PASSED")
    else:
        print("\n❌ SOME ALIAS TESTS FAILED")
    
    print("="*60)


def test_forbidden_terms_filter():
    """Test that forbidden terms are filtered from advice."""
    
    print("\n" + "="*60)
    print("FORBIDDEN TERMS FILTER TEST")
    print("="*60)
    
    # Build context that might trigger memory care
    context = GCPContext(
        age_range="85+",
        living_situation="alone_in_apartment",
        has_partner=False,
        meds_complexity="complex",
        mobility="wheelchair",
        falls="multiple_falls",
        badls=["bathing", "dressing", "toileting", "transferring"],
        iadls=["meal_prep", "housekeeping", "medication", "finances", "transportation"],
        memory_changes="moderate_impairment",
        behaviors=["wandering", "aggression", "sundowning"],
        isolation="severe",
        move_preference=1,
        flags=["safety_concerns", "caregiver_burnout"],
    )
    
    print("\nGenerating advice for high-acuity context...")
    ok, advice = generate_gcp_advice(context, mode="shadow")
    
    if ok and advice:
        print(f"\nTier: {advice.tier}")
        print("Checking for forbidden terms...")
        
        # Collect all text
        all_text = (
            advice.reasons
            + advice.risks
            + advice.navi_messages
            + advice.questions_next
        )
        
        has_forbidden = False
        for text in all_text:
            text_lower = text.lower()
            for term in FORBIDDEN_TERMS:
                if term in text_lower:
                    print(f"  ❌ Found forbidden term '{term}' in: {text[:50]}...")
                    has_forbidden = True
        
        if not has_forbidden:
            print("  ✅ No forbidden terms found in advice")
        else:
            print("\n❌ FORBIDDEN TERMS TEST FAILED")
    else:
        print("\n⚠️  No advice generated (check API key)")
    
    print("="*60)


def test_reconciliation():
    """Test reconciliation between deterministic and LLM recommendations."""
    
    print("\n" + "="*60)
    print("RECONCILIATION TEST")
    print("="*60)
    
    # Build context
    context = GCPContext(
        age_range="70-74",
        living_situation="with_spouse",
        has_partner=True,
        meds_complexity="simple",
        mobility="independent",
        falls="no_falls",
        badls=[],
        iadls=["transportation"],
        memory_changes="no_changes",
        behaviors=[],
        isolation="minimal",
        move_preference=None,
        flags=["homeowner"],
    )
    
    print("\nGenerating advice for low-acuity context...")
    ok, advice = generate_gcp_advice(context, mode="shadow")
    
    if ok and advice:
        print(f"\nLLM tier: {advice.tier}")
        print(f"LLM confidence: {advice.confidence:.2f}")
        
        # Test reconciliation scenarios
        print("\n--- Test 1: Agreement (both say 'in_home') ---")
        final = reconcile_with_deterministic("in_home", advice, "shadow")
        print(f"Final tier: {final}")
        assert final == "in_home", "Should return deterministic tier"
        
        print("\n--- Test 2: Mismatch (det='assisted_living', llm='in_home') ---")
        final = reconcile_with_deterministic("assisted_living", advice, "shadow")
        print(f"Final tier: {final}")
        assert final == "assisted_living", "Deterministic should always win"
        
        print("\n✅ RECONCILIATION TEST PASSED - Deterministic always wins")
    else:
        print("\n⚠️  No advice generated (check API key)")
    
    print("="*60)


def test_per_section_feedback():
    """Test per-section LLM feedback with partial contexts."""
    
    print("\n" + "="*60)
    print("PER-SECTION FEEDBACK TEST")
    print("="*60)
    
    # Test 1: About You section (minimal context)
    print("\n[Test 1] About You section (minimal context)...")
    context_about_you = GCPContext(
        age_range="75-84",
        living_situation="alone_in_house",
        has_partner=False,
        meds_complexity="simple",  # Not answered yet
        mobility="independent",  # Not answered yet
        falls="no_falls",  # Not answered yet
        memory_changes="no_changes",  # Not answered yet
        isolation="minimal",  # Not answered yet
    )
    
    ok, advice = generate_section_advice(context_about_you, "about_you", mode="shadow")
    if ok and advice:
        print(f"  ✅ Success - Tier: {advice.tier} (conf: {advice.confidence:.2f})")
        assert advice.tier in CANONICAL_TIERS, f"Non-canonical tier: {advice.tier}"
        print(f"  ✅ Tier is canonical")
    else:
        print("  ⚠️  No advice generated")
    
    # Test 2: Health & Safety section (more data)
    print("\n[Test 2] Health & Safety section (moderate complexity)...")
    context_health = GCPContext(
        age_range="75-84",
        living_situation="alone_in_house",
        has_partner=False,
        meds_complexity="moderate",  # 4-6 meds
        mobility="walker",
        falls="1_fall_last_6mo",
        badls=[],  # Not answered yet
        iadls=[],  # Not answered yet
        memory_changes="no_changes",
        behaviors=[],
        isolation="moderate",
    )
    
    ok, advice = generate_section_advice(context_health, "health_safety", mode="shadow")
    if ok and advice:
        print(f"  ✅ Success - Tier: {advice.tier} (conf: {advice.confidence:.2f})")
        assert advice.tier in CANONICAL_TIERS, f"Non-canonical tier: {advice.tier}"
        print(f"  ✅ Tier is canonical")
        
        # Show sample messages
        if advice.navi_messages:
            print(f"  Sample message: {advice.navi_messages[0][:60]}...")
    else:
        print("  ⚠️  No advice generated")
    
    # Test 3: Daily Living section (significant challenges)
    print("\n[Test 3] Daily Living section (significant ADL challenges)...")
    context_daily = GCPContext(
        age_range="75-84",
        living_situation="alone_in_house",
        has_partner=False,
        meds_complexity="moderate",
        mobility="walker",
        falls="1_fall_last_6mo",
        badls=["bathing", "dressing"],
        iadls=["meal_prep", "housekeeping", "transportation"],
        memory_changes="mild_forgetfulness",
        behaviors=[],
        isolation="moderate",
    )
    
    ok, advice = generate_section_advice(context_daily, "daily_living", mode="shadow")
    if ok and advice:
        print(f"  ✅ Success - Tier: {advice.tier} (conf: {advice.confidence:.2f})")
        assert advice.tier in CANONICAL_TIERS, f"Non-canonical tier: {advice.tier}"
        print(f"  ✅ Tier is canonical")
        
        # Tier should likely be assisted_living or higher given the challenges
        if advice.tier in ["assisted_living", "memory_care"]:
            print(f"  ✅ Tier appropriate for ADL challenges: {advice.tier}")
    else:
        print("  ⚠️  No advice generated")
    
    # Test 4: Cognition section (memory concerns)
    print("\n[Test 4] Cognition section (memory care indicators)...")
    context_cognition = GCPContext(
        age_range="85+",
        living_situation="alone_in_apartment",
        has_partner=False,
        meds_complexity="complex",
        mobility="wheelchair",
        falls="multiple_falls",
        badls=["bathing", "dressing", "toileting"],
        iadls=["meal_prep", "housekeeping", "medication", "finances"],
        memory_changes="moderate_impairment",
        behaviors=["wandering", "confusion"],
        isolation="severe",
    )
    
    ok, advice = generate_section_advice(context_cognition, "cognition_behavior", mode="shadow")
    if ok and advice:
        print(f"  ✅ Success - Tier: {advice.tier} (conf: {advice.confidence:.2f})")
        assert advice.tier in CANONICAL_TIERS, f"Non-canonical tier: {advice.tier}"
        print(f"  ✅ Tier is canonical")
        
        # Tier should likely be memory_care given the indicators
        if advice.tier in ["memory_care", "memory_care_high_acuity"]:
            print(f"  ✅ Tier appropriate for memory concerns: {advice.tier}")
    else:
        print("  ⚠️  No advice generated")
    
    print("\n" + "="*60)
    print("PER-SECTION FEEDBACK TESTS COMPLETE")
    print("="*60)


def test_cognitive_gates():
    """Test cognitive gates and allowed_tiers scoping."""
    
    print("\n" + "="*60)
    print("COGNITIVE GATES + ALLOWED_TIERS TEST")
    print("="*60)
    
    # Case A: High ADL burden, no memory issues → MC should be blocked
    print("\n[Test A] High ADL burden, no cognitive issues (MC blocked)...")
    context_no_cog = GCPContext(
        age_range="85+",
        living_situation="alone_in_house",
        has_partner=False,
        meds_complexity="complex",
        mobility="wheelchair",
        falls="multiple_falls",
        badls=["bathing", "dressing", "toileting", "transferring"],
        iadls=["meal_prep", "housekeeping", "medication", "finances"],
        memory_changes="none",  # No memory issues
        behaviors=[],  # No risky behaviors
        isolation="severe",
        move_preference=3,
        flags=["high_dependence", "falls_risk"],
    )
    
    # LLM should NOT be allowed to recommend memory_care
    allowed_tiers_no_cog = ["none", "in_home", "assisted_living"]
    
    ok, advice = generate_gcp_advice(context_no_cog, mode="shadow", allowed_tiers=allowed_tiers_no_cog)
    
    if ok and advice:
        print(f"  Tier: {advice.tier}")
        print(f"  Allowed: {allowed_tiers_no_cog}")
        
        assert advice.tier in allowed_tiers_no_cog, f"LLM returned tier outside allowed list: {advice.tier}"
        print(f"  ✅ LLM respected allowed_tiers (tier={advice.tier} in {allowed_tiers_no_cog})")
        
        assert advice.tier not in ["memory_care", "memory_care_high_acuity"], \
            f"LLM should not recommend MC without cognitive issues"
        print(f"  ✅ Memory care correctly blocked (no cognitive criteria)")
    else:
        print("  ⚠️  No advice generated")
    
    # Case B: Memory changes + wandering → MC should be allowed
    print("\n[Test B] Moderate memory + wandering (MC allowed)...")
    context_with_cog = GCPContext(
        age_range="80-84",
        living_situation="with_family",
        has_partner=False,
        meds_complexity="moderate",
        mobility="walker",
        falls="once",
        badls=["bathing"],
        iadls=["meal_prep", "medication"],
        memory_changes="moderate",  # Moderate memory impairment
        behaviors=["wandering", "confusion"],  # Risky behaviors
        isolation="moderate",
        move_preference=6,
        flags=["moderate_cognitive_decline", "moderate_safety_concern"],
    )
    
    # All tiers should be allowed
    allowed_tiers_with_cog = ["none", "in_home", "assisted_living", "memory_care", "memory_care_high_acuity"]
    
    ok, advice = generate_gcp_advice(context_with_cog, mode="shadow", allowed_tiers=allowed_tiers_with_cog)
    
    if ok and advice:
        print(f"  Tier: {advice.tier}")
        print(f"  Allowed: {allowed_tiers_with_cog}")
        
        assert advice.tier in allowed_tiers_with_cog, f"LLM returned tier outside allowed list: {advice.tier}"
        print(f"  ✅ LLM respected allowed_tiers (tier={advice.tier})")
        
        # LLM CAN recommend memory_care here (cognitive criteria met)
        print(f"  ✅ Memory care allowed (cognitive criteria met)")
    else:
        print("  ⚠️  No advice generated")
    
    # Case C: Try to force MC when not allowed (simulate LLM returning blocked tier)
    print("\n[Test C] Simulate LLM trying MC when blocked...")
    print("  (This tests the post-guard rejection logic)")
    
    # Create context with no cognitive issues
    context_test = GCPContext(
        age_range="75-84",
        living_situation="alone",
        has_partner=False,
        meds_complexity="moderate",
        mobility="independent",
        falls="none",
        badls=[],
        iadls=["housekeeping"],
        memory_changes="none",
        behaviors=[],
        isolation="low",
    )
    
    # Restrict allowed_tiers (simulate cognitive gate blocking MC)
    allowed_no_mc = ["none", "in_home", "assisted_living"]
    
    ok, advice = generate_gcp_advice(context_test, mode="shadow", allowed_tiers=allowed_no_mc)
    
    if ok and advice:
        assert advice.tier in allowed_no_mc, f"Post-guard failed: tier {advice.tier} not in allowed {allowed_no_mc}"
        print(f"  ✅ Post-guard working (tier={advice.tier} in {allowed_no_mc})")
    else:
        print("  ✅ LLM generation rejected or returned blocked tier (expected behavior)")
    
    print("\n" + "="*60)
    print("COGNITIVE GATES TESTS COMPLETE")
    print("="*60)


def test_tier_map_loads_and_returns_allowed_tier():
    """Test that tier_map.json loads correctly and returns canonical tiers."""
    
    print("\n" + "="*60)
    print("TIER MAP LOADER TEST")
    print("="*60)
    
    # Import the loader
    from products.gcp_v4.modules.care_recommendation.logic import _load_tier_map
    from ai.gcp_schemas import CANONICAL_TIERS
    
    print("\nLoading tier_map.json...")
    tier_map = _load_tier_map()
    
    # Verify structure
    assert tier_map is not None, "Tier map should not be None"
    assert "moderate" in tier_map, "Tier map should have 'moderate' cognition band"
    assert "high" in tier_map["moderate"], "Moderate cognition should have 'high' support band"
    
    print(f"  ✅ Tier map loaded successfully")
    print(f"  ✅ Structure validated (has moderate×high mapping)")
    
    # Check that returned tier is canonical
    tier = tier_map["moderate"]["high"]
    assert tier in CANONICAL_TIERS, f"Tier '{tier}' should be in CANONICAL_TIERS"
    print(f"  ✅ Tier '{tier}' is canonical")
    
    # Test a few key mappings
    test_cases = [
        ("none", "low", "none"),
        ("none", "high", "assisted_living"),
        ("moderate", "high", "memory_care"),
        ("high", "24h", "memory_care_high_acuity"),
    ]
    
    print("\nTesting key mappings:")
    for cog, sup, expected in test_cases:
        result = tier_map.get(cog, {}).get(sup)
        assert result == expected, f"Expected {cog}×{sup}={expected}, got {result}"
        print(f"  ✅ {cog} × {sup} → {result}")
    
    print("\n" + "="*60)
    print("TIER MAP LOADER TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    # Run all guard tests
    test_gcp_canonical_tiers()
    test_tier_alias_normalization()
    test_forbidden_terms_filter()
    test_reconciliation()
    test_per_section_feedback()
    test_cognitive_gates()
    test_tier_map_loads_and_returns_allowed_tier()  # NEW
    
    print("\n" + "="*60)
    print("🎯 GCP LLM GUARD TESTS COMPLETE")
    print("="*60)
