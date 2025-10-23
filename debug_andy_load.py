#!/usr/bin/env python3
"""
Debug script to simulate loading Andy's profile and check MCIP status.

This simulates what happens when:
1. Andy's profile is loaded from JSON
2. Data is merged into session state
3. MCIP.initialize() is called
4. MCIP.get_product_summary("gcp_v4") is called
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Simulate Streamlit session_state
class MockSessionState(dict):
    """Mock session state for testing outside Streamlit."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"session_state has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def get(self, key, default=None):
        return super().get(key, default)

def load_profile(uid: str) -> dict[str, Any]:
    """Load demo profile from JSON."""
    profile_path = Path(f"data/users/demo/{uid}.json")
    if not profile_path.exists():
        print(f"❌ Profile not found: {profile_path}")
        return {}

    with open(profile_path) as f:
        data = json.load(f)

    print(f"✅ Loaded profile: {profile_path}")
    return data

def merge_into_state(session_state, data):
    """Merge loaded data into session state."""
    for key, value in data.items():
        session_state[key] = value
    print(f"✅ Merged {len(data)} keys into session state")

def check_mcip_state(session_state):
    """Check what MCIP sees after initialization."""
    print("\n" + "="*60)
    print("CHECKING MCIP STATE")
    print("="*60)

    # Check if mcip_contracts exists
    if "mcip_contracts" not in session_state:
        print("❌ No mcip_contracts in session_state")
        return

    print("✅ mcip_contracts exists")

    contracts = session_state["mcip_contracts"]

    # Check care_recommendation
    if "care_recommendation" not in contracts:
        print("❌ No care_recommendation in mcip_contracts")
        return

    print("✅ care_recommendation exists in mcip_contracts")

    care_rec = contracts["care_recommendation"]

    # Check key fields
    tier = care_rec.get("tier")
    status = care_rec.get("status")
    tier_score = care_rec.get("tier_score")
    confidence = care_rec.get("confidence")

    print("\ncare_recommendation fields:")
    print(f"  tier: {tier}")
    print(f"  tier_score: {tier_score}")
    print(f"  confidence: {confidence}")
    print(f"  status: {status}")

    # Check if this would pass MCIP's checks
    print("\nWould MCIP recognize this as complete?")
    print(f"  Has tier? {tier is not None}")
    print(f"  Status not 'new' or None? {status not in ['new', None]}")

    if tier and status not in ["new", None]:
        print("\n✅ YES - Should show as complete!")
    else:
        print("\n❌ NO - Would not show as complete")
        if not tier:
            print("  Reason: tier is None or missing")
        if status in ["new", None]:
            print(f"  Reason: status is '{status}'")

def test_mcip_initialize(session_state):
    """Simulate what MCIP.initialize() does."""
    print("\n" + "="*60)
    print("SIMULATING MCIP.initialize()")
    print("="*60)

    # This is what MCIP.initialize() does
    STATE_KEY = "mcip"

    if STATE_KEY not in session_state:
        # Create default structure
        session_state[STATE_KEY] = {
            "care_recommendation": None,
            "financial_profile": None,
            "advisor_appointment": None,
            "journey": {
                "current_hub": "concierge",
                "completed_products": [],
                "unlocked_products": ["gcp"],
                "recommended_next": "gcp",
            },
            "waiting_room": {
                "advisor_prep_status": "not_started",
                "trivia_status": "not_started",
                "current_focus": "advisor_prep",
            },
            "events": [],
        }
        print("✅ Created default MCIP state")

    # Now restore from mcip_contracts if available
    if "mcip_contracts" in session_state:
        import copy
        contracts = session_state["mcip_contracts"]

        print("\n📦 Restoring from mcip_contracts:")

        if "care_recommendation" in contracts and contracts["care_recommendation"]:
            session_state[STATE_KEY]["care_recommendation"] = copy.deepcopy(
                contracts["care_recommendation"]
            )
            print("  ✅ Restored care_recommendation")
        else:
            print("  ❌ care_recommendation missing or empty")

        if "journey" in contracts and contracts["journey"]:
            session_state[STATE_KEY]["journey"] = copy.deepcopy(contracts["journey"])
            print("  ✅ Restored journey")
        else:
            print("  ❌ journey missing or empty")
    else:
        print("❌ No mcip_contracts to restore from")

    # Show what's in MCIP state now
    print("\nMCIP state after initialize:")
    mcip_state = session_state[STATE_KEY]
    care_rec = mcip_state.get("care_recommendation")

    if care_rec:
        print("  care_recommendation:")
        print(f"    tier: {care_rec.get('tier')}")
        print(f"    status: {care_rec.get('status')}")
        print(f"    confidence: {care_rec.get('confidence')}")
    else:
        print("  care_recommendation: None")

    journey = mcip_state.get("journey", {})
    print("  journey:")
    print(f"    completed_products: {journey.get('completed_products')}")
    print(f"    unlocked_products: {journey.get('unlocked_products')}")

def test_get_care_recommendation(session_state):
    """Simulate MCIP.get_care_recommendation()."""
    print("\n" + "="*60)
    print("SIMULATING MCIP.get_care_recommendation()")
    print("="*60)

    STATE_KEY = "mcip"

    rec_data = session_state.get(STATE_KEY, {}).get("care_recommendation")

    print(f"rec_data: {rec_data is not None}")

    if rec_data:
        status = rec_data.get("status")
        print(f"status: {status}")
        print(f"status not in ['new', None]: {status not in ['new', None]}")

        if status not in ["new", None]:
            print("\n✅ Would return CareRecommendation object")
            return True
        else:
            print(f"\n❌ Would return None (status is '{status}')")
            return False
    else:
        print("\n❌ Would return None (rec_data is None)")
        return False

def test_get_product_summary(session_state):
    """Simulate MCIP.get_product_summary('gcp_v4')."""
    print("\n" + "="*60)
    print("SIMULATING MCIP.get_product_summary('gcp_v4')")
    print("="*60)

    # First check if get_care_recommendation would return something
    has_rec = test_get_care_recommendation(session_state)

    if has_rec:
        print("\n✅ GCP tile would show: status='complete'")
        print("✅ GCP tile would display care tier and confidence")
    else:
        print("\n❌ GCP tile would show: status='not_started'")
        print("❌ GCP tile would show: 'Get your personalized care recommendation'")

def main():
    """Run the simulation."""
    print("\n" + "="*80)
    print("ANDY PROFILE LOAD SIMULATION")
    print("="*80)

    # Create mock session state
    session_state = MockSessionState()

    # Load Andy's profile
    uid = "andy_assisted_gcp_complete"
    profile_data = load_profile(uid)

    if not profile_data:
        return

    # Merge into session state (what app.py does)
    merge_into_state(session_state, profile_data)

    # Check what we got
    check_mcip_state(session_state)

    # Simulate MCIP.initialize()
    test_mcip_initialize(session_state)

    # Test get_product_summary
    test_get_product_summary(session_state)

    print("\n" + "="*80)
    print("SIMULATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
