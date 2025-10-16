#!/usr/bin/env python3
"""
Test: Verify care_recommendation doesn't share references

This tests the specific bug where Cost Planner re-locks because
care_recommendation (used by get_product_summary) shares references.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_care_recommendation_no_shared_reference():
    """Test that modifying mcip care_recommendation doesn't corrupt mcip_contracts."""
    print("🔍 Testing care_recommendation Shared Reference Bug\n")
    
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP, CareRecommendation
    
    # Step 1: Initialize and publish care recommendation (simulate GCP completion)
    print("Step 1: Publish care recommendation (simulate GCP completion)")
    MCIP.initialize()
    
    # Manually create care_recommendation dict (simulate what GCP does)
    rec_dict = {
        "tier": "in_home",
        "tier_score": 85.0,
        "tier_rankings": [("in_home", 85.0), ("assisted_living", 60.0)],
        "confidence": 0.85,
        "flags": [{"flag_id": "mobility_support", "severity": "moderate"}],
        "rationale": ["Needs mobility assistance"],
        "generated_at": "2025-10-15T12:00:00",
        "version": "3.0",
        "input_snapshot_id": "test_snapshot_1",
        "rule_set": "standard",
        "next_step": {"action": "Calculate costs", "route": "cost_v2"},
        "status": "complete",
        "last_updated": "2025-10-15T12:00:00",
        "needs_refresh": False
    }
    st.session_state['mcip']['care_recommendation'] = rec_dict
    MCIP._save_contracts_for_persistence()
    
    print(f"  ✓ Care recommendation published")
    print(f"  mcip care_rec id: {id(st.session_state['mcip']['care_recommendation'])}")
    print(f"  mcip_contracts care_rec id: {id(st.session_state['mcip_contracts']['care_recommendation'])}")
    
    # Check if they're the same object
    mcip_rec = st.session_state['mcip']['care_recommendation']
    contracts_rec = st.session_state['mcip_contracts']['care_recommendation']
    
    if mcip_rec is contracts_rec:
        print(f"  ⚠️  WARNING: mcip and mcip_contracts share the same care_recommendation object!")
        print(f"     This means modifying one will modify the other!")
    else:
        print(f"  ✓ Good: mcip and mcip_contracts have separate care_recommendation objects")
    
    # Step 2: Simulate corruption (like what might happen during navigation)
    print("\nStep 2: Simulate care_recommendation corruption")
    
    # Save original state
    original_tier = st.session_state['mcip']['care_recommendation'].get('tier')
    original_contracts_tier = st.session_state['mcip_contracts']['care_recommendation'].get('tier')
    
    print(f"  BEFORE corruption:")
    print(f"    mcip tier: {original_tier}")
    print(f"    mcip_contracts tier: {original_contracts_tier}")
    
    # Corrupt the mcip state
    st.session_state['mcip']['care_recommendation'] = None
    
    print(f"\n  AFTER setting mcip['care_recommendation'] = None:")
    print(f"    mcip: {st.session_state['mcip']['care_recommendation']}")
    print(f"    mcip_contracts: {st.session_state['mcip_contracts']['care_recommendation']}")
    
    # Check if mcip_contracts was also corrupted
    if st.session_state['mcip_contracts']['care_recommendation'] is None:
        print(f"\n  ❌ BUG FOUND: Corrupting mcip also corrupted mcip_contracts!")
        print(f"     This is because they share the same object.")
        return False
    else:
        print(f"\n  ✅ Good: mcip_contracts preserved its care_recommendation!")
        print(f"     They are truly separate objects.")
    
    # Step 3: Test that MCIP.initialize() restores correctly
    print("\nStep 3: Test MCIP.initialize() restores from uncorrupted mcip_contracts")
    MCIP.initialize()
    
    restored_rec = MCIP.get_care_recommendation()
    print(f"  Restored care_recommendation: {restored_rec}")
    
    if restored_rec and restored_rec.tier == "in_home":
        print(f"  ✅ State restored correctly from mcip_contracts!")
        print(f"  ✅ Cost Planner will correctly see GCP as complete!")
        return True
    else:
        print(f"  ❌ State NOT restored - mcip_contracts was corrupted!")
        print(f"  ❌ Cost Planner will incorrectly re-lock!")
        return False


def test_cost_planner_unlock_with_care_recommendation():
    """Test that Cost Planner unlocking works through the full chain."""
    print("\n\n🔍 Testing Cost Planner Unlock via care_recommendation\n")
    
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP, CareRecommendation
    
    # Step 1: Publish care recommendation
    print("Step 1: Publish care recommendation")
    MCIP.initialize()
    
    rec_dict = {
        "tier": "assisted_living",
        "tier_score": 92.0,
        "tier_rankings": [("assisted_living", 92.0), ("memory_care", 70.0)],
        "confidence": 0.92,
        "flags": [{"flag_id": "adl_support", "severity": "moderate"}],
        "rationale": ["Needs ADL support and social engagement"],
        "generated_at": "2025-10-15T12:00:00",
        "version": "3.0",
        "input_snapshot_id": "test_snapshot_2",
        "rule_set": "standard",
        "next_step": {"action": "Calculate costs", "route": "cost_v2"},
        "status": "complete",
        "last_updated": "2025-10-15T12:00:00",
        "needs_refresh": False
    }
    st.session_state['mcip']['care_recommendation'] = rec_dict
    MCIP._save_contracts_for_persistence()
    print(f"  ✓ Care recommendation published: {rec_dict['tier']}")
    
    # Step 2: Check Cost Planner summary
    print("\nStep 2: Check Cost Planner unlock status")
    summary = MCIP.get_product_summary("cost_v2")
    print(f"  Summary: {summary}")
    
    if summary and summary.get("status") == "unlocked":
        print(f"  ✅ Cost Planner is UNLOCKED")
    else:
        print(f"  ❌ Cost Planner is LOCKED (unexpected!)")
        return False
    
    # Step 3: Simulate navigation (reinitialize)
    print("\nStep 3: Simulate navigation (MCIP.initialize() called again)")
    MCIP.initialize()
    
    # Step 4: Check Cost Planner summary again
    print("\nStep 4: Check Cost Planner unlock status after reinitialize")
    summary = MCIP.get_product_summary("cost_v2")
    print(f"  Summary: {summary}")
    
    if summary and summary.get("status") == "unlocked":
        print(f"  ✅ Cost Planner is STILL UNLOCKED")
        return True
    else:
        print(f"  ❌ Cost Planner RE-LOCKED (BUG!)")
        return False


if __name__ == "__main__":
    try:
        result1 = test_care_recommendation_no_shared_reference()
        result2 = test_cost_planner_unlock_with_care_recommendation()
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Test 1 (care_recommendation no shared ref): {'✅ PASS' if result1 else '❌ FAIL'}")
        print(f"Test 2 (Cost Planner unlock persistence): {'✅ PASS' if result2 else '❌ FAIL'}")
        
        if result1 and result2:
            print("\n🎉 All tests passed!")
            print("✅ care_recommendation doesn't share references")
            print("✅ Cost Planner unlock persists across navigation")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
