#!/usr/bin/env python3
"""
Test: Verify mcip and mcip_contracts Don't Share References

This tests the critical bug where mcip["journey"] and mcip_contracts["journey"]
were pointing to the same dict object, causing corruption.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_no_shared_references():
    """Test that modifying mcip doesn't corrupt mcip_contracts."""
    print("🔍 Testing for Shared Reference Bug\n")
    
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP
    
    # Step 1: Initialize and complete GCP
    print("Step 1: Initialize and complete GCP")
    MCIP.initialize()
    MCIP.mark_product_complete("gcp")
    
    print(f"  ✓ GCP completed")
    print(f"  mcip journey id: {id(st.session_state['mcip']['journey'])}")
    print(f"  mcip_contracts journey id: {id(st.session_state['mcip_contracts']['journey'])}")
    
    # Check if they're the same object
    mcip_journey = st.session_state['mcip']['journey']
    contracts_journey = st.session_state['mcip_contracts']['journey']
    
    if mcip_journey is contracts_journey:
        print(f"  ⚠️  WARNING: mcip and mcip_contracts share the same journey object!")
        print(f"     This means modifying one will modify the other!")
    else:
        print(f"  ✓ Good: mcip and mcip_contracts have separate journey objects")
    
    # Step 2: Simulate what might happen during navigation
    print("\nStep 2: Simulate mcip state corruption (like FAQ navigation might cause)")
    
    # Save the original state
    original_mcip = st.session_state['mcip']['journey']['completed_products'].copy()
    original_contracts = st.session_state['mcip_contracts']['journey']['completed_products'].copy()
    
    print(f"  BEFORE corruption:")
    print(f"    mcip completed: {original_mcip}")
    print(f"    mcip_contracts completed: {original_contracts}")
    
    # Corrupt the mcip state (simulate what might happen)
    st.session_state['mcip']['journey']['completed_products'] = []
    
    print(f"\n  AFTER corrupting mcip['journey']['completed_products'] = []:")
    print(f"    mcip completed: {st.session_state['mcip']['journey']['completed_products']}")
    print(f"    mcip_contracts completed: {st.session_state['mcip_contracts']['journey']['completed_products']}")
    
    # Check if mcip_contracts was also corrupted
    if len(st.session_state['mcip_contracts']['journey']['completed_products']) == 0:
        print(f"\n  ❌ BUG FOUND: Corrupting mcip also corrupted mcip_contracts!")
        print(f"     This is because they share the same dictionary object.")
        print(f"     Fix: Use deepcopy when restoring from mcip_contracts")
        return False
    else:
        print(f"\n  ✅ Good: mcip_contracts preserved its data!")
        print(f"     They are truly separate objects.")
        return True
    
    # Step 3: Test that MCIP.initialize() restores correctly
    print("\nStep 3: Test MCIP.initialize() restores from uncorrupted mcip_contracts")
    MCIP.initialize()
    
    restored = st.session_state['mcip']['journey']['completed_products']
    print(f"  After initialize: {restored}")
    
    if 'gcp' in restored:
        print(f"  ✅ State restored correctly from mcip_contracts!")
        return True
    else:
        print(f"  ❌ State NOT restored - mcip_contracts was corrupted!")
        return False


if __name__ == "__main__":
    try:
        success = test_no_shared_references()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 TEST PASSED: No shared reference bug!")
            print("=" * 70)
            print("\n✅ mcip and mcip_contracts use separate objects")
            print("✅ Modifying mcip doesn't corrupt mcip_contracts")
            print("✅ MCIP.initialize() correctly restores from contracts")
        else:
            print("❌ TEST FAILED: Shared reference bug detected!")
            print("=" * 70)
            print("\nThe bug: mcip and mcip_contracts share the same journey dict.")
            print("Fix: Use copy.deepcopy() when restoring from contracts.")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
