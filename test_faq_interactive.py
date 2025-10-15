#!/usr/bin/env python3
"""
Interactive Test: Reproduce FAQ Navigation Bug

Run this and follow the prompts to manually verify the bug is fixed.
This will help identify where the state is being lost.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("=" * 70)
    print("🔍 INTERACTIVE FAQ NAVIGATION BUG TEST")
    print("=" * 70)
    print()
    print("This test will walk you through the exact steps to reproduce the bug.")
    print("Follow the instructions and report what you see in the actual app.")
    print()
    
    input("Press Enter to start the test...")
    
    print("\n" + "=" * 70)
    print("STEP 1: Start the App")
    print("=" * 70)
    print()
    print("Run: streamlit run app.py")
    print()
    input("Press Enter when the app is running...")
    
    print("\n" + "=" * 70)
    print("STEP 2: Complete GCP")
    print("=" * 70)
    print()
    print("1. Navigate to the GCP product")
    print("2. Complete all questions until progress reaches 100%")
    print("3. Return to the Concierge Hub")
    print()
    input("Press Enter when GCP is complete...")
    
    print("\n" + "=" * 70)
    print("STEP 3: Verify Cost Planner Unlocked")
    print("=" * 70)
    print()
    print("Check the Cost Planner tile in the Concierge Hub:")
    print()
    response = input("Is Cost Planner UNLOCKED? (y/n): ").lower().strip()
    
    if response != 'y':
        print("\n❌ UNEXPECTED: Cost Planner should be unlocked after GCP!")
        print("This suggests the first fix (unlock logic) isn't working.")
        print("Check commit 2f9e9df is applied.")
        return False
    
    print("✅ Good! Cost Planner is unlocked.")
    
    print("\n" + "=" * 70)
    print("STEP 4: Navigate to Cost Planner")
    print("=" * 70)
    print()
    print("1. Click on the Cost Planner tile")
    print("2. Verify it opens (you should see the Cost Planner page)")
    print("3. Click 'Back to Hub' or use navigation to return to Concierge Hub")
    print()
    input("Press Enter after returning to the hub...")
    
    print("\n" + "=" * 70)
    print("STEP 5: Verify Cost Planner Still Unlocked")
    print("=" * 70)
    print()
    response = input("Is Cost Planner STILL UNLOCKED? (y/n): ").lower().strip()
    
    if response != 'y':
        print("\n❌ BUG: Cost Planner re-locked after visiting it!")
        print("This is unexpected - check the unlock logic.")
        return False
    
    print("✅ Good! Cost Planner is still unlocked.")
    
    print("\n" + "=" * 70)
    print("STEP 6: Navigate to FAQ (CRITICAL TEST)")
    print("=" * 70)
    print()
    print("1. Click on the FAQ tile")
    print("2. Wait for FAQ page to load")
    print("3. You should see the Navi chatbot interface")
    print()
    input("Press Enter when you're on the FAQ page...")
    
    print("\n" + "=" * 70)
    print("STEP 7: Return to Hub from FAQ")
    print("=" * 70)
    print()
    print("1. Click the '← Back to Hub' button on the FAQ page")
    print("2. Wait for the Concierge Hub to load")
    print()
    input("Press Enter when you're back on the hub...")
    
    print("\n" + "=" * 70)
    print("STEP 8: CHECK - Is Cost Planner Still Unlocked?")
    print("=" * 70)
    print()
    print("⚠️  CRITICAL: This is where the bug occurs!")
    print()
    response = input("Is Cost Planner STILL UNLOCKED? (y/n): ").lower().strip()
    
    if response != 'y':
        print("\n❌ BUG REPRODUCED: Cost Planner re-locked after FAQ navigation!")
        print()
        print("Debug steps:")
        print("1. Open browser console (F12)")
        print("2. Look for any JavaScript errors")
        print("3. Check Streamlit logs in terminal")
        print()
        print("Common causes:")
        print("- mcip_contracts not being saved to disk")
        print("- mcip_contracts being cleared/reset")
        print("- MCIP.initialize() not restoring from contracts")
        print("- Persistence layer not loading mcip_contracts")
        print()
        return False
    
    print("\n✅ SUCCESS: Cost Planner is STILL unlocked!")
    print()
    print("The bug appears to be fixed! Let's verify persistence...")
    
    print("\n" + "=" * 70)
    print("STEP 9: Test Persistence (Optional but Recommended)")
    print("=" * 70)
    print()
    print("1. Note your browser session (don't close it)")
    print("2. Stop the Streamlit server (Ctrl+C in terminal)")
    print("3. Restart: streamlit run app.py")
    print("4. Refresh the browser page")
    print()
    response = input("Do you want to test persistence? (y/n): ").lower().strip()
    
    if response == 'y':
        input("\nPress Enter after restarting the app and refreshing browser...")
        
        print("\n" + "=" * 70)
        print("STEP 10: Verify Persistence")
        print("=" * 70)
        print()
        response = input("Is Cost Planner STILL UNLOCKED after app restart? (y/n): ").lower().strip()
        
        if response != 'y':
            print("\n❌ PERSISTENCE BUG: State not saved to disk!")
            print()
            print("Check:")
            print("- data/users/<uid>.json file exists")
            print("- mcip_contracts is in USER_PERSIST_KEYS")
            print("- save_user() is being called after page render")
            return False
        
        print("\n✅ PERSISTENCE WORKS: State survived app restart!")
    
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("The FAQ navigation bug appears to be fixed!")
    print()
    print("If you're still seeing issues, please provide:")
    print("1. Exact steps where it fails")
    print("2. Browser console errors (F12)")
    print("3. Streamlit terminal output")
    print("4. Contents of data/users/<uid>.json")
    print()
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
