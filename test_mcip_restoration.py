#!/usr/bin/env python3
"""
Debug Script: Test MCIP Restoration After FAQ Navigation

This simulates the exact flow that's failing:
1. Complete GCP
2. Navigate to FAQ (state persists)
3. Return to hub (MCIP.initialize() called)
4. Check if completion state is preserved
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_mcip_restoration_debug():
    """Test MCIP restoration with detailed logging."""
    print("🔍 MCIP Restoration Debug Test\n")
    
    # Mock st.session_state
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP
    
    # Step 1: Initialize MCIP (fresh)
    print("=" * 70)
    print("STEP 1: Fresh Initialization")
    print("=" * 70)
    MCIP.initialize()
    print(f"✓ MCIP initialized")
    print(f"  mcip exists: {'mcip' in st.session_state}")
    print(f"  mcip_contracts exists: {'mcip_contracts' in st.session_state}")
    print(f"  Journey: {st.session_state['mcip']['journey']}")
    
    # Step 2: Complete GCP
    print("\n" + "=" * 70)
    print("STEP 2: Complete GCP")
    print("=" * 70)
    MCIP.mark_product_complete("gcp")
    print(f"✓ Marked GCP complete")
    print(f"  mcip journey: {st.session_state['mcip']['journey']}")
    print(f"  mcip_contracts journey: {st.session_state['mcip_contracts']['journey']}")
    
    # Step 3: Simulate navigation (MCIP.initialize() called again)
    print("\n" + "=" * 70)
    print("STEP 3: Navigate to FAQ (state persists)")
    print("=" * 70)
    print("  (No changes - FAQ doesn't modify MCIP state)")
    
    # Step 4: Return to hub - MCIP.initialize() called
    print("\n" + "=" * 70)
    print("STEP 4: Return to Hub (MCIP.initialize() called)")
    print("=" * 70)
    print(f"  BEFORE reinit:")
    print(f"    mcip exists: {'mcip' in st.session_state}")
    print(f"    mcip_contracts exists: {'mcip_contracts' in st.session_state}")
    print(f"    mcip journey: {st.session_state['mcip']['journey']}")
    print(f"    mcip_contracts journey: {st.session_state['mcip_contracts']['journey']}")
    
    MCIP.initialize()
    
    print(f"\n  AFTER reinit:")
    print(f"    mcip exists: {'mcip' in st.session_state}")
    print(f"    mcip_contracts exists: {'mcip_contracts' in st.session_state}")
    print(f"    mcip journey: {st.session_state['mcip']['journey']}")
    print(f"    mcip_contracts journey: {st.session_state['mcip_contracts']['journey']}")
    
    # Step 5: Check if GCP is still complete
    print("\n" + "=" * 70)
    print("STEP 5: Verify GCP Still Complete")
    print("=" * 70)
    is_complete = MCIP.is_product_complete("gcp")
    completed_list = st.session_state['mcip']['journey']['completed_products']
    
    print(f"  MCIP.is_product_complete('gcp'): {is_complete}")
    print(f"  completed_products list: {completed_list}")
    print(f"  'gcp' in completed_products: {'gcp' in completed_list}")
    
    if is_complete and 'gcp' in completed_list:
        print("\n✅ SUCCESS: GCP completion preserved!")
        return True
    else:
        print("\n❌ FAILURE: GCP completion lost!")
        print("\nDEBUG INFO:")
        print(f"  Full mcip state: {st.session_state['mcip']}")
        print(f"  Full mcip_contracts: {st.session_state['mcip_contracts']}")
        return False


def test_with_manual_corruption():
    """Test what happens if we manually corrupt mcip but keep mcip_contracts intact."""
    print("\n\n" + "=" * 70)
    print("🔍 Test: Manual Corruption of mcip State")
    print("=" * 70)
    
    class MockSessionState(dict):
        pass
    
    import streamlit as st
    import copy
    st.session_state = MockSessionState()
    
    from core.mcip import MCIP
    
    # Initialize and complete GCP
    MCIP.initialize()
    MCIP.mark_product_complete("gcp")
    print("✓ GCP completed and saved to mcip_contracts")
    
    # Save the correct contracts
    saved_contracts = copy.deepcopy(st.session_state['mcip_contracts'])
    
    # Corrupt the mcip runtime state (simulate stale data)
    print("\n✓ Corrupting mcip runtime state...")
    st.session_state['mcip']['journey']['completed_products'] = []
    st.session_state['mcip']['journey']['unlocked_products'] = []
    
    # Restore the correct contracts (simulate persistence)
    st.session_state['mcip_contracts'] = saved_contracts
    
    print(f"  mcip (corrupted): {st.session_state['mcip']['journey']}")
    print(f"  mcip_contracts (correct): {st.session_state['mcip_contracts']['journey']}")
    
    # Call initialize - should restore from contracts
    print("\n✓ Calling MCIP.initialize()...")
    MCIP.initialize()
    
    print(f"\n  After initialize:")
    print(f"  mcip: {st.session_state['mcip']['journey']}")
    print(f"  mcip_contracts: {st.session_state['mcip_contracts']['journey']}")
    
    is_complete = MCIP.is_product_complete("gcp")
    if is_complete:
        print("\n✅ SUCCESS: State restored from mcip_contracts!")
        return True
    else:
        print("\n❌ FAILURE: State NOT restored from mcip_contracts!")
        return False


if __name__ == "__main__":
    try:
        result1 = test_mcip_restoration_debug()
        result2 = test_with_manual_corruption()
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Test 1 (Normal Flow): {'✅ PASS' if result1 else '❌ FAIL'}")
        print(f"Test 2 (Corruption Recovery): {'✅ PASS' if result2 else '❌ FAIL'}")
        
        if result1 and result2:
            print("\n🎉 All tests passed! MCIP restoration is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Review the debug output above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
