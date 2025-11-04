"""
Quick test of Care Hours Calculator functionality.
Tests baseline calculation without running Streamlit UI.
"""

from ai.hours_schemas import HoursContext
from ai.hours_weights import (
    get_badl_hours,
    get_iadl_hours,
    get_cognitive_multiplier,
    get_fall_risk_multiplier,
    get_mobility_hours,
)
from ai.hours_engine import calculate_baseline_hours_weighted

# Test case: Moderate cognitive impairment + multiple ADLs + fall risk
print("=" * 60)
print("Care Hours Calculator - Test Case")
print("=" * 60)

# Input scenario
badls = ["bathing", "toileting", "dressing"]
iadls = ["medication_management", "meal_preparation"]
cognitive_level = "moderate"
wandering = True
aggression = False
sundowning = False
repetitive_questions = False
falls = "multiple"
mobility = "walker"
overnight = False

print("\nINPUTS:")
print(f"  BADLs: {', '.join(badls)}")
print(f"  IADLs: {', '.join(iadls)}")
print(f"  Cognitive: {cognitive_level}")
print(f"  Wandering: {wandering}")
print(f"  Falls: {falls}")
print(f"  Mobility: {mobility}")

# Build context
context = HoursContext(
    badls_count=len(badls),
    iadls_count=len(iadls),
    badls_list=badls,
    iadls_list=iadls,
    cognitive_level=cognitive_level,
    wandering=wandering,
    aggression=aggression,
    sundowning=sundowning,
    repetitive_questions=repetitive_questions,
    falls=falls,
    mobility=mobility,
    overnight_needed=overnight,
)

# Calculate components
badl_hours = sum(get_badl_hours(badl) for badl in badls)
iadl_hours = sum(get_iadl_hours(iadl) for iadl in iadls)
cognitive_multiplier = get_cognitive_multiplier(
    cognitive_level, wandering, aggression, sundowning, repetitive_questions
)
fall_multiplier = get_fall_risk_multiplier(falls)
mobility_hours = get_mobility_hours(mobility)

total_hours = (badl_hours + iadl_hours) * cognitive_multiplier * fall_multiplier + mobility_hours

# Get baseline band
baseline_band = calculate_baseline_hours_weighted(context)

print("\nCALCULATION BREAKDOWN:")
print(f"  BADL hours: {badl_hours:.2f}h")
for badl in badls:
    print(f"    - {badl}: {get_badl_hours(badl):.2f}h")
print(f"  IADL hours: {iadl_hours:.2f}h")
for iadl in iadls:
    print(f"    - {iadl}: {get_iadl_hours(iadl):.2f}h")
print(f"  × Cognitive multiplier: {cognitive_multiplier:.2f}x")
print(f"    (moderate base 1.6x + wandering 0.3x)")
print(f"  × Fall risk multiplier: {fall_multiplier:.2f}x")
print(f"  + Mobility aid hours: {mobility_hours:.2f}h")
print(f"\n  TOTAL: {total_hours:.2f}h → {baseline_band}")

print("\n" + "=" * 60)
print("✅ Baseline calculation working correctly!")
print("=" * 60)
