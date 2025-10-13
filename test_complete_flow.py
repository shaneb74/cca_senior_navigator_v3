#!/usr/bin/env python3
"""
Comprehensive test to verify the COMPLETE data flow from logic → engine → hub → Cost Planner.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("COMPLETE GCP DATA FLOW VALIDATION")
print("=" * 80)

# Step 1: Test derive_outcome directly
print("\n" + "=" * 80)
print("STEP 1: Test derive_outcome() function")
print("=" * 80)

from products.gcp.modules.care_recommendation.logic import derive_outcome, TIER_NAMES

test_answers = {
    'help_overall': 'Some help with daily tasks',
    'memory_changes': 'Moderate – noticeable confusion',
    'primary_support': 'Family member',
    'meds_complexity': 'Moderate – daily meds',
    'mobility': 'Walker',
    'falls': 'One in past year',
    'badls': ['bathing'],
    'iadls': ['meal_prep', 'housekeeping'],
    'behaviors': ['confusion']
}

outcome = derive_outcome(test_answers, {})
print(f"\n✅ derive_outcome() returned:")
print(f"   Type: {type(outcome).__name__}")
print(f"   Recommendation: '{outcome.recommendation}'")
print(f"   Tier: {outcome.summary.get('tier')}")
print(f"   Score: {outcome.summary.get('total_score')}")

# Step 2: Verify recommendation string format
print("\n" + "=" * 80)
print("STEP 2: Verify recommendation string format")
print("=" * 80)

rec_str = outcome.recommendation
print(f"\nRecommendation string: '{rec_str}'")
print(f"Has uppercase: {any(c.isupper() for c in rec_str)}")
print(f"Has slash: {'/' in rec_str}")
print(f"Has hyphen: {'-' in rec_str}")

# Check if it's in TIER_NAMES
tier_values = list(TIER_NAMES.values())
if rec_str in tier_values:
    print(f"✅ Recommendation is in TIER_NAMES: {tier_values}")
else:
    print(f"❌ Recommendation NOT in TIER_NAMES!")
    print(f"   TIER_NAMES values: {tier_values}")

# Step 3: Simulate engine handoff creation
print("\n" + "=" * 80)
print("STEP 3: Simulate engine handoff creation (_ensure_outcomes)")
print("=" * 80)

handoff_data = {
    "recommendation": outcome.recommendation,
    "flags": dict(outcome.flags),
    "tags": list(outcome.tags),
    "domain_scores": dict(outcome.domain_scores),
}

print(f"\nHandoff data structure:")
print(f"   recommendation: '{handoff_data['recommendation']}'")
print(f"   flags: {len(handoff_data['flags'])} flags")
print(f"   tags: {len(handoff_data['tags'])} tags")
print(f"   domain_scores: {len(handoff_data['domain_scores'])} domains")

# Step 4: Simulate concierge hub reading
print("\n" + "=" * 80)
print("STEP 4: Simulate concierge hub reading (hubs/concierge.py lines 48-52)")
print("=" * 80)

# This is what concierge does:
recommendation = handoff_data.get("recommendation")
recommendation_display = str(recommendation).replace('_', ' ').title() if recommendation else None

print(f"\nConcierge processing:")
print(f"   Input: '{recommendation}'")
print(f"   After .replace('_', ' ').title(): '{recommendation_display}'")

# Build reason (line 54-57)
reason = (
    f"Based on your {recommendation_display} recommendation"
    if recommendation
    else None
)

print(f"   MCIP reason: '{reason}'")

# Build status text (line 61-63)
gcp_status_text = None
if recommendation_display:  # Assuming 100% progress
    gcp_status_text = f"✓ {recommendation_display}"

print(f"   GCP status text: '{gcp_status_text}'")

# Build tile description HTML (lines 70-73)
gcp_desc_html = None
if recommendation_display:  # Assuming 100% progress
    gcp_desc_html = f'<span class="tile-recommendation">Recommendation: {recommendation_display}</span>'

print(f"   GCP desc HTML: '{gcp_desc_html}'")

# Step 5: Simulate Cost Planner gate check
print("\n" + "=" * 80)
print("STEP 5: Simulate Cost Planner gate check (products/cost_planner/product.py line 41)")
print("=" * 80)

# Simulate session state
simulated_gcp_state = {
    "progress": 100.0,
    "status": "done",
    "care_tier": outcome.recommendation,
    "_outcomes": {"recommendation": outcome.recommendation}
}

gcp_progress = float(simulated_gcp_state.get("progress", 0))
print(f"\nCost Planner check:")
print(f"   gcp_progress = {gcp_progress}")

if gcp_progress < 100:
    print(f"   ❌ GATE BLOCKS ACCESS (progress < 100)")
else:
    print(f"   ✅ GATE ALLOWS ACCESS (progress >= 100)")

# Step 6: Simulate Cost Planner handoff read
print("\n" + "=" * 80)
print("STEP 6: Simulate Cost Planner handoff read (products/cost_planner/cost_estimate_v2.py)")
print("=" * 80)

# Simulate what Cost Planner does
from products.cost_planner.cost_estimate_v2 import TIER_TO_CARE_TYPE

cp_recommendation = handoff_data.get("recommendation")
print(f"\nCost Planner reads:")
print(f"   handoff['gcp']['recommendation']: '{cp_recommendation}'")

if cp_recommendation in TIER_TO_CARE_TYPE:
    care_type = TIER_TO_CARE_TYPE[cp_recommendation]
    print(f"   ✅ Maps to care type: '{care_type}'")
else:
    print(f"   ❌ NO MAPPING FOUND!")
    print(f"\n   Available mappings in TIER_TO_CARE_TYPE:")
    for key, value in TIER_TO_CARE_TYPE.items():
        print(f"      '{key}' → '{value}'")

# Step 7: Check _get_recommendation formatting
print("\n" + "=" * 80)
print("STEP 7: Simulate _get_recommendation() formatting (core/modules/engine.py line 605)")
print("=" * 80)

# Simulate _get_recommendation logic
test_rec = outcome.recommendation

# Check if properly formatted (line 607-609)
is_formatted = any(c.isupper() for c in test_rec) or "/" in test_rec or "-" in test_rec

print(f"\nRecommendation: '{test_rec}'")
print(f"Has uppercase/slash/hyphen: {is_formatted}")

if is_formatted:
    formatted_output = f"Based on your answers, we recommend {test_rec}."
    print(f"✅ Uses as-is: '{formatted_output}'")
else:
    # Would normalize and look up in mapping
    rec_key = test_rec.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
    print(f"❌ Would normalize to: '{rec_key}' and look up in mapping")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

issues = []

# Check 1: Recommendation string format
if not any(c.isupper() for c in outcome.recommendation):
    issues.append("❌ Recommendation has no uppercase letters (won't trigger as-is path)")

# Check 2: Hub display
if not recommendation_display:
    issues.append("❌ Concierge hub won't display recommendation (None)")

# Check 3: Gate check
if gcp_progress < 100:
    issues.append("❌ Cost Planner gate will block (progress < 100)")

# Check 4: Cost Planner mapping
if cp_recommendation not in TIER_TO_CARE_TYPE:
    issues.append(f"❌ Cost Planner can't map recommendation: '{cp_recommendation}'")

if issues:
    print("\n❌ ISSUES FOUND:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\n✅ ALL CHECKS PASSED!")
    print("\nData flow should work correctly:")
    print(f"  1. derive_outcome() returns: '{outcome.recommendation}'")
    print(f"  2. Engine sets handoff['gcp']['recommendation'] = '{handoff_data['recommendation']}'")
    print(f"  3. Concierge displays: '{gcp_status_text}'")
    print(f"  4. Cost Planner gates: {'OPEN' if gcp_progress >= 100 else 'CLOSED'}")
    print(f"  5. Cost Planner maps to: '{TIER_TO_CARE_TYPE.get(cp_recommendation, 'UNKNOWN')}'")

print("\n" + "=" * 80)
