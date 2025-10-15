#!/usr/bin/env python3
"""
Test Script: FAQ Navigation Bug Fix

Tests that visiting FAQ and returning to hub preserves Cost Planner unlock state.

Bug Scenario:
1. Complete GCP → Cost Planner unlocks
2. Go to FAQ page
3. Return to hub → Cost Planner re-locks (BUG!)

Root Cause:
- MCIP.initialize() only restored from mcip_contracts on FRESH initialization
- If st.session_state["mcip"] already existed, contracts were not restored
- FAQ navigation caused MCIP.initialize() to run with existing state
- Stale journey data (completed_products = []) was used

Fix:
- MCIP.initialize() now ALWAYS restores from mcip_contracts if available
- This ensures completion state persists even when mcip state already exists

Usage:
    python test_faq_navigation_fix.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_faq_navigation_preserves_unlock():
    """Test that FAQ navigation preserves Cost Planner unlock state."""
    print("🧪 Testing FAQ Navigation Fix\n")
    
    # Mock st.session_state
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP
    from core.product_tile import ProductTileHub, tile_is_unlocked
    
    # Step 1: Initialize MCIP (fresh)
    print("Step 1: Fresh Initialization")
    MCIP.initialize()
    print(f"  ✓ MCIP initialized")
    print(f"  Journey: {st.session_state['mcip']['journey']}")
    
    # Step 2: Complete GCP
    print("\nStep 2: Complete GCP")
    MCIP.mark_product_complete("gcp")
    print(f"  ✓ Marked GCP complete")
    print(f"  Completed: {st.session_state['mcip']['journey']['completed_products']}")
    print(f"  Contracts: {st.session_state.get('mcip_contracts', {}).get('journey', {}).get('completed_products', [])}")
    
    # Step 3: Check Cost Planner unlocks
    print("\nStep 3: Verify Cost Planner Unlocks")
    cost_tile = ProductTileHub(
        key="cost_v2",
        title="Cost Planner",
        locked=False,
        unlock_requires=["gcp:complete"],
    )
    is_unlocked = tile_is_unlocked(cost_tile, st.session_state)
    print(f"  Cost Planner unlocked: {is_unlocked}")
    assert is_unlocked, "❌ Cost Planner should be unlocked after GCP completion"
    print("  ✓ Cost Planner unlocked (as expected)")
    
    # Step 4: Simulate navigation to FAQ (MCIP state persists)
    print("\nStep 4: Simulate Navigation to FAQ")
    print("  (MCIP state in st.session_state['mcip'] persists)")
    print("  (mcip_contracts also persists)")
    
    # Step 5: Simulate returning to hub - MCIP.initialize() called again
    print("\nStep 5: Return to Hub (MCIP.initialize() called again)")
    
    # BEFORE FIX: The else branch in initialize() would NOT restore from mcip_contracts
    # AFTER FIX: initialize() ALWAYS restores from mcip_contracts
    
    MCIP.initialize()
    print(f"  ✓ MCIP.initialize() called (st.session_state['mcip'] already exists)")
    print(f"  Journey after reinit: {st.session_state['mcip']['journey']}")
    print(f"  Completed: {st.session_state['mcip']['journey']['completed_products']}")
    
    # Step 6: Check Cost Planner still unlocked
    print("\nStep 6: Verify Cost Planner STILL Unlocked")
    is_unlocked = tile_is_unlocked(cost_tile, st.session_state)
    print(f"  Cost Planner unlocked: {is_unlocked}")
    
    assert is_unlocked, "❌ BUG: Cost Planner re-locked after FAQ navigation!"
    print("  ✓ Cost Planner STILL unlocked (fix works!)")
    
    # Verify MCIP sees GCP as complete
    assert MCIP.is_product_complete("gcp"), "❌ MCIP doesn't see GCP as complete"
    print("  ✓ MCIP.is_product_complete('gcp') = True")
    
    print("\n✅ TEST PASSED: FAQ navigation preserves unlock state!")


def test_multiple_navigation_cycles():
    """Test that multiple page navigations don't corrupt state."""
    print("\n\n🧪 Testing Multiple Navigation Cycles\n")
    
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP
    from core.product_tile import ProductTileHub, tile_is_unlocked
    
    # Initialize and complete GCP
    MCIP.initialize()
    MCIP.mark_product_complete("gcp")
    print("✓ GCP completed")
    
    cost_tile = ProductTileHub(
        key="cost_v2",
        title="Cost Planner",
        locked=False,
        unlock_requires=["gcp:complete"],
    )
    
    # Simulate 5 navigation cycles (hub → FAQ → hub → FAQ → hub...)
    for i in range(5):
        print(f"\nCycle {i+1}: Navigate to FAQ and back")
        
        # Simulate MCIP.initialize() being called again
        MCIP.initialize()
        
        # Check state
        is_unlocked = tile_is_unlocked(cost_tile, st.session_state)
        completed = st.session_state['mcip']['journey']['completed_products']
        
        print(f"  Completed products: {completed}")
        print(f"  Cost Planner unlocked: {is_unlocked}")
        
        assert "gcp" in completed, f"❌ GCP completion lost after cycle {i+1}"
        assert is_unlocked, f"❌ Cost Planner re-locked after cycle {i+1}"
        print(f"  ✓ State preserved after cycle {i+1}")
    
    print("\n✅ State preserved across 5 navigation cycles!")


def test_contracts_restoration_priority():
    """Test that mcip_contracts is the source of truth."""
    print("\n\n🧪 Testing Contracts Restoration Priority\n")
    
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    import copy
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP
    
    # Step 1: Initialize and complete GCP
    MCIP.initialize()
    MCIP.mark_product_complete("gcp")
    print("✓ Step 1: GCP completed, saved to mcip_contracts")
    print(f"  mcip_contracts journey: {st.session_state['mcip_contracts']['journey']}")
    
    # Step 2: Save mcip_contracts, then corrupt mcip state (simulate stale data)
    print("\n✓ Step 2: Corrupt mcip state (simulate stale data)")
    
    # Make a deep copy of mcip_contracts to preserve the truth
    saved_contracts = copy.deepcopy(st.session_state['mcip_contracts'])
    
    # Corrupt mcip runtime state
    st.session_state["mcip"]["journey"]["completed_products"] = []
    
    # Restore the saved contracts (simulate what persistence would do)
    st.session_state['mcip_contracts'] = saved_contracts
    
    print(f"  mcip journey (corrupted): {st.session_state['mcip']['journey']}")
    print(f"  mcip_contracts journey (truth): {st.session_state['mcip_contracts']['journey']}")
    
    # Step 3: Call MCIP.initialize() - should restore from mcip_contracts
    print("\n✓ Step 3: Call MCIP.initialize() - should restore from mcip_contracts")
    MCIP.initialize()
    
    restored_completed = st.session_state['mcip']['journey']['completed_products']
    print(f"  mcip journey (after init): {st.session_state['mcip']['journey']}")
    print(f"  Completed products: {restored_completed}")
    
    assert "gcp" in restored_completed, "❌ Failed to restore from mcip_contracts"
    print("  ✓ State restored from mcip_contracts (correct source of truth)")
    
    print("\n✅ mcip_contracts is the authoritative source!")


if __name__ == "__main__":
    try:
        test_faq_navigation_preserves_unlock()
        test_multiple_navigation_cycles()
        test_contracts_restoration_priority()
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\n✅ FAQ navigation no longer re-locks Cost Planner")
        print("✅ State persists across multiple page navigations")
        print("✅ mcip_contracts is the authoritative source of truth")
        print("\nFix: MCIP.initialize() now ALWAYS restores from mcip_contracts")
        print("     This ensures completion state survives page navigations")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
