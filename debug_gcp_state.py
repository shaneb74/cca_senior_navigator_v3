#!/usr/bin/env python3
"""
Debug script to check GCP session state after outcomes are computed.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Simulate what should be in session state after GCP completion
print("=" * 70)
print("GCP SESSION STATE DEBUG")
print("=" * 70)

# What the module engine SHOULD set
print("\n1. What engine sets after outcomes are computed:")
print("-" * 70)

gcp_state = {
    "progress": 100.0,
    "status": "done",
    "care_tier": "Assisted Living",  # Set from outcome.recommendation
    "_step": 5,  # Final step (results)
    "_outcomes": {
        "recommendation": "Assisted Living",
        "confidence": 0.85,
        "flags": {"cognitive_risk": True, "fall_risk": False},
        "tags": ["moderate_needs"],
        "domain_scores": {"cognitive": 9, "adl_iadl": 15},
        "summary": {"total_score": 31, "tier": 2, "points": [...]},
        "routing": {},
        "audit": {}
    }
}

print(f"st.session_state['gcp'] = {{")
for key, value in gcp_state.items():
    if key == "_outcomes":
        print(f"    '{key}': {{ ... OutcomeContract data ... }},")
    else:
        print(f"    '{key}': {repr(value)},")
print(f"}}")

# Handoff data
print("\n2. What engine sets in handoff for Cost Planner:")
print("-" * 70)

handoff_data = {
    "gcp": {
        "recommendation": "Assisted Living",
        "flags": {"cognitive_risk": True, "fall_risk": False},
        "tags": ["moderate_needs"],
        "domain_scores": {"cognitive": 9, "adl_iadl": 15}
    }
}

print(f"st.session_state['handoff'] = {{")
print(f"    'gcp': {{")
print(f"        'recommendation': 'Assisted Living',")
print(f"        'flags': {{ ... }},")
print(f"        'tags': [ ... ],")
print(f"        'domain_scores': {{ ... }}")
print(f"    }}")
print(f"}}")

# Cost Planner check
print("\n3. Cost Planner gate check:")
print("-" * 70)

gcp_progress = gcp_state.get("progress", 0)
print(f"gcp_progress = st.session_state.get('gcp', {{}}).get('progress', 0)")
print(f"gcp_progress = {gcp_progress}")
print(f"")
if gcp_progress >= 100:
    print("✅ Gate check PASSES - Cost Planner accessible")
else:
    print(f"❌ Gate check FAILS - Progress is {gcp_progress}, needs 100")

# Cost Planner handoff check
print("\n4. Cost Planner handoff data check:")
print("-" * 70)

recommendation = handoff_data["gcp"].get("recommendation")
print(f"recommendation = st.session_state.get('handoff', {{}}).get('gcp', {{}}).get('recommendation')")
print(f"recommendation = {repr(recommendation)}")
print(f"")
if recommendation:
    print(f"✅ Recommendation found: '{recommendation}'")
else:
    print("❌ Recommendation missing!")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

issues = []

if gcp_progress < 100:
    issues.append("- GCP progress not set to 100")

if not recommendation:
    issues.append("- Handoff recommendation missing")

if issues:
    print("❌ ISSUES FOUND:")
    for issue in issues:
        print(issue)
    print("\nLikely causes:")
    print("1. _ensure_outcomes() not being called")
    print("2. derive_outcome() erroring silently")
    print("3. results_step_id not matching actual step")
    print("4. User didn't reach results step")
else:
    print("✅ All session state should be correct!")
    print("\nIf Cost Planner is still gated:")
    print("1. Check browser console for errors")
    print("2. Check terminal console for [DEBUG] output")
    print("3. Verify user completed all required GCP questions")
    print("4. Check st.session_state directly in Streamlit")

print("=" * 70)
