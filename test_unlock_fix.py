#!/usr/bin/env python3
"""
Test Script: Verify Unlock Logic Fix

Tests that completing GCP unlocks Cost Planner and persists across sessions.

Usage:
    python test_unlock_fix.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_mcip_unlock_logic():
    """Test that MCIP completion tracking works with unlock requirements."""
    print("🧪 Testing MCIP Unlock Logic Fix\n")
    
    # Mock st.session_state
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    # Initialize MCIP
    from core.mcip import MCIP
    MCIP.initialize()
    
    print("✓ MCIP initialized")
    print(f"  Journey: {st.session_state['mcip']['journey']}")
    
    # Mark GCP as complete
    MCIP.mark_product_complete("gcp")
    print("\n✓ Marked GCP as complete")
    print(f"  Completed products: {st.session_state['mcip']['journey']['completed_products']}")
    
    # Check if product is marked complete
    assert MCIP.is_product_complete("gcp"), "GCP should be marked complete"
    print("✓ MCIP.is_product_complete('gcp') = True")
    
    # Test unlock logic
    from core.product_tile import _evaluate_requirement
    
    # Test requirement: "gcp:complete"
    result = _evaluate_requirement("gcp:complete", st.session_state)
    print(f"\n✓ _evaluate_requirement('gcp:complete', state) = {result}")
    assert result, "gcp:complete requirement should be True"
    
    # Test requirement: "cost:complete" (should be False)
    result2 = _evaluate_requirement("cost:complete", st.session_state)
    print(f"✓ _evaluate_requirement('cost:complete', state) = {result2}")
    assert not result2, "cost:complete requirement should be False"
    
    print("\n✅ All tests passed!")


def test_persistence():
    """Test that MCIP contracts persist to user file."""
    print("\n\n🧪 Testing MCIP Persistence\n")
    
    # Mock st.session_state
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    # Initialize MCIP
    from core.mcip import MCIP
    MCIP.initialize()
    
    # Mark GCP complete
    MCIP.mark_product_complete("gcp")
    
    # Check that mcip_contracts exists
    assert "mcip_contracts" in st.session_state, "mcip_contracts should be in session_state"
    print("✓ mcip_contracts exists in session_state")
    
    contracts = st.session_state["mcip_contracts"]
    print(f"  Contracts: {list(contracts.keys())}")
    
    # Check that journey is saved
    assert "journey" in contracts, "journey should be in mcip_contracts"
    assert "gcp" in contracts["journey"]["completed_products"], "gcp should be in completed_products"
    print("✓ Journey state saved to mcip_contracts")
    print(f"  Completed: {contracts['journey']['completed_products']}")
    
    # Test extract_user_state
    from core.session_store import extract_user_state, USER_PERSIST_KEYS
    
    print(f"\n✓ USER_PERSIST_KEYS: {USER_PERSIST_KEYS}")
    assert "mcip_contracts" in USER_PERSIST_KEYS, "mcip_contracts should be in USER_PERSIST_KEYS"
    
    # Extract user state
    user_state = extract_user_state(st.session_state)
    print(f"\n✓ Extracted user state keys: {list(user_state.keys())}")
    assert "mcip_contracts" in user_state, "mcip_contracts should be extracted"
    
    # Save to disk
    from core.session_store import save_user, load_user
    import uuid
    
    test_uid = f"test_{uuid.uuid4().hex[:8]}"
    print(f"\n✓ Saving to user file: {test_uid}")
    
    save_user(test_uid, user_state)
    
    # Load back
    loaded = load_user(test_uid)
    print(f"✓ Loaded user data keys: {list(loaded.keys())}")
    
    assert "mcip_contracts" in loaded, "mcip_contracts should be loaded"
    assert "journey" in loaded["mcip_contracts"], "journey should be in loaded mcip_contracts"
    assert "gcp" in loaded["mcip_contracts"]["journey"]["completed_products"], \
        "gcp should be in loaded completed_products"
    
    print("✓ Journey state persisted and restored correctly")
    print(f"  Completed: {loaded['mcip_contracts']['journey']['completed_products']}")
    
    # Cleanup
    from core.session_store import delete_user
    delete_user(test_uid)
    print(f"\n✓ Cleaned up test user file")
    
    print("\n✅ All persistence tests passed!")


def test_full_flow():
    """Test complete flow: GCP completion → Cost Planner unlock → Persistence → Restore."""
    print("\n\n🧪 Testing Full Flow (GCP → Cost Planner Unlock → Persist → Restore)\n")
    
    # Mock st.session_state
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP
    from core.product_tile import ProductTileHub
    from core.session_store import save_user, load_user, delete_user, extract_user_state
    import uuid
    
    # Step 1: Fresh user
    print("Step 1: Fresh User - Cost Planner Locked")
    MCIP.initialize()
    
    cost_tile = ProductTileHub(
        key="cost_v2",
        title="Cost Planner",
        locked=False,  # Will be checked by unlock_requires
        unlock_requires=["gcp:complete"],
    )
    
    from core.product_tile import tile_is_unlocked
    is_unlocked = tile_is_unlocked(cost_tile, st.session_state)
    print(f"  Cost Planner unlocked: {is_unlocked}")
    assert not is_unlocked, "Cost Planner should be locked (GCP not complete)"
    print("  ✓ Cost Planner locked (as expected)")
    
    # Step 2: Complete GCP
    print("\nStep 2: Complete GCP")
    MCIP.mark_product_complete("gcp")
    is_unlocked = tile_is_unlocked(cost_tile, st.session_state)
    print(f"  Cost Planner unlocked: {is_unlocked}")
    assert is_unlocked, "Cost Planner should be unlocked (GCP complete)"
    print("  ✓ Cost Planner unlocked (as expected)")
    
    # Step 3: Save to disk
    print("\nStep 3: Save User Data to Disk")
    test_uid = f"test_{uuid.uuid4().hex[:8]}"
    user_state = extract_user_state(st.session_state)
    save_user(test_uid, user_state)
    print(f"  ✓ Saved to data/users/{test_uid}.json")
    
    # Step 4: Clear session (simulate app restart)
    print("\nStep 4: Simulate App Restart (Clear Session)")
    st.session_state.clear()
    print("  ✓ Session state cleared")
    
    # Step 5: Restore from disk
    print("\nStep 5: Restore User Data from Disk")
    loaded = load_user(test_uid)
    for key, value in loaded.items():
        if key not in ['uid', 'created_at', 'last_updated']:
            st.session_state[key] = value
    print(f"  ✓ Loaded from data/users/{test_uid}.json")
    
    # Step 6: Reinitialize MCIP (should restore from mcip_contracts)
    print("\nStep 6: Reinitialize MCIP")
    MCIP.initialize()
    print(f"  Completed products: {st.session_state['mcip']['journey']['completed_products']}")
    assert MCIP.is_product_complete("gcp"), "GCP should still be complete after restore"
    print("  ✓ GCP completion restored")
    
    # Step 7: Check Cost Planner unlock again
    print("\nStep 7: Verify Cost Planner Still Unlocked")
    is_unlocked = tile_is_unlocked(cost_tile, st.session_state)
    print(f"  Cost Planner unlocked: {is_unlocked}")
    assert is_unlocked, "Cost Planner should still be unlocked after restore"
    print("  ✓ Cost Planner still unlocked (persistence works!)")
    
    # Cleanup
    delete_user(test_uid)
    print(f"\n✓ Cleaned up test user file")
    
    print("\n✅ Full flow test passed! Unlock state persists across sessions!")


if __name__ == "__main__":
    try:
        test_mcip_unlock_logic()
        test_persistence()
        test_full_flow()
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\n✅ The unlock logic fix is working correctly")
        print("✅ MCIP contracts persist to data/users/<uid>.json")
        print("✅ Completion state survives app restarts")
        print("\nNext steps:")
        print("  1. Test in the actual app (streamlit run app.py)")
        print("  2. Complete GCP → verify Cost Planner unlocks")
        print("  3. Return to hub → verify Cost Planner STAYS unlocked")
        print("  4. Restart app → verify completion persists")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
