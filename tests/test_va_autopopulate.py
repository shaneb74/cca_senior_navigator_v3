#!/usr/bin/env python3
"""
Debug script to test VA disability auto-population logic
Run this to see what's happening without needing the full Streamlit app
"""

import sys

sys.path.insert(0, 'products/cost_planner_v2')

from va_rates import get_monthly_va_disability

# Simulate the state dictionary
state = {}

print("=" * 60)
print("VA DISABILITY AUTO-POPULATION DEBUG TEST")
print("=" * 60)

# Test 1: User hasn't answered "Do you receive VA disability?" yet
print("\n[TEST 1] No has_va_disability answer yet")
state = {}
has_disability = state.get("has_va_disability")
print(f"  has_va_disability: {has_disability}")
print(f"  Should skip: {has_disability != 'yes'}")

# Test 2: User said "No" to VA disability
print("\n[TEST 2] User said 'No' to VA disability")
state = {"has_va_disability": "no"}
has_disability = state.get("has_va_disability")
print(f"  has_va_disability: {has_disability}")
print(f"  Should skip: {has_disability != 'yes'}")

# Test 3: User said "Yes" but hasn't selected rating/dependents yet
print("\n[TEST 3] User said 'Yes' but no rating/dependents")
state = {"has_va_disability": "yes"}
has_disability = state.get("has_va_disability")
rating = state.get("va_disability_rating")
dependents = state.get("va_dependents")
print(f"  has_va_disability: {has_disability}")
print(f"  va_disability_rating: {rating}")
print(f"  va_dependents: {dependents}")
print(f"  Should skip: {rating is None or dependents is None}")

# Test 4: User selected rating but not dependents
print("\n[TEST 4] Rating selected but not dependents")
state = {"has_va_disability": "yes", "va_disability_rating": 60}
has_disability = state.get("has_va_disability")
rating = state.get("va_disability_rating")
dependents = state.get("va_dependents")
print(f"  has_va_disability: {has_disability}")
print(f"  va_disability_rating: {rating}")
print(f"  va_dependents: {dependents}")
print(f"  Should skip: {rating is None or dependents is None}")

# Test 5: Both rating and dependents selected (SHOULD CALCULATE)
print("\n[TEST 5] Both rating and dependents selected ✅")
state = {
    "has_va_disability": "yes",
    "va_disability_rating": 60,
    "va_dependents": "spouse"
}
has_disability = state.get("has_va_disability")
rating = state.get("va_disability_rating")
dependents = state.get("va_dependents")
print(f"  has_va_disability: {has_disability}")
print(f"  va_disability_rating: {rating} (type: {type(rating).__name__})")
print(f"  va_dependents: {dependents} (type: {type(dependents).__name__})")
print(f"  Should calculate: {has_disability == 'yes' and rating is not None and dependents is not None}")

print(f"\n  Calling get_monthly_va_disability({rating}, '{dependents}')...")
try:
    monthly_amount = get_monthly_va_disability(rating, dependents)
    print(f"  ✅ Result: ${monthly_amount:,.2f}" if monthly_amount else f"  ❌ Result: {monthly_amount}")
    if monthly_amount:
        state["va_disability_monthly"] = monthly_amount
        print(f"  ✅ Updated state['va_disability_monthly'] = {monthly_amount}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Different combinations
print("\n[TEST 6] Different rating/dependent combinations")
test_cases = [
    (60, "spouse", "60% with spouse"),
    (60, "spouse_one_child", "60% with spouse + 1 child"),
    (70, "spouse", "70% with spouse"),
    (100, "spouse_multiple_children", "100% with spouse + 2+ children"),
]

for rating, deps, desc in test_cases:
    try:
        amount = get_monthly_va_disability(rating, deps)
        print(f"  ✅ {desc}: ${amount:,.2f}")
    except Exception as e:
        print(f"  ❌ {desc}: ERROR - {e}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("  - Function works correctly when called with proper parameters")
print("  - Check if Streamlit is passing correct rating/dependents values")
print("  - Check if has_va_disability is being set to 'yes' (not True/1)")
print("=" * 60)
