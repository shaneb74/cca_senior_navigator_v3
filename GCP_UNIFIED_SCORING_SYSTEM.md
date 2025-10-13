# GCP Unified Scoring System

**Date:** October 13, 2025  
**Status:** ✅ COMPLETE

---

## Overview

Completely rebuilt the GCP recommendation scoring system to use **ONE unified source of truth**: the new `module.json` and `logic.json` files. Eliminated the dependency on `module.json.OLD` to prevent confusion from having two similar files with different question orders.

---

## Architecture

### Data Files (Single Source of Truth)
1. **`module.json`** - Question structure, UI rendering, section ordering
2. **`logic.json`** - Scoring rules, flags, decision thresholds

### Code Files
1. **`logic.py`** - New scoring engine that interprets logic.json
2. **`engine.py`** - Results view displays recommendations and summary points
3. **`product.py`** - Loads module.json for UI rendering

---

## New Scoring System

### Flag-Based Scoring (Not Question Weights)

**OLD System (module.json.OLD):**
- Each question had a `score` attribute
- Questions had `weight` values
- Used `decision_tree` with score thresholds
- Total weighted score determined tier

**NEW System (logic.json):**
- Flags are evaluated from answer values
- Flags map to **categories** (care_burden, cognitive_function, etc.)
- Categories have different weights for **in_home** vs **assisted_living** scores
- Decision thresholds compare aggregate scores and flag combinations

### Scoring Flow

```
Answers → Evaluate Flags → Map to Categories → Calculate Scores → Match Thresholds → Recommendation
```

#### Step 1: Evaluate Flags
```json
{
  "severe_cognitive_risk": {
    "trigger": "memory_changes == 'severe' || additional_conditions matches '(?i)dementia|alzheimer'",
    "priority": "high",
    "message": "..."
  }
}
```

Evaluates triggers using:
- `==` equality checks
- `in [...]` list membership
- `.length >` array length
- `includes [...]` array contains
- `matches` regex patterns
- `||` logical OR

#### Step 2: Map to Categories
```json
{
  "flag_to_category_mapping": {
    "severe_cognitive_risk": "cognitive_function",
    "high_dependence": "care_burden",
    "fall_risk": "home_safety"
  }
}
```

Each active flag contributes +1 to its category count.

#### Step 3: Calculate Aggregate Scores
```json
{
  "scoring": {
    "in_home": {
      "care_burden": 1,
      "cognitive_function": 1,
      "home_safety": 1
    },
    "assisted_living": {
      "care_burden": 3,
      "cognitive_function": 2,
      "home_safety": 2
    }
  }
}
```

For each category:
- `in_home_score += category_count * in_home_weight`
- `assisted_living_score += category_count * assisted_living_weight`

**Example:**
- 3 care_burden flags active
- in_home_score += 3 × 1 = 3
- assisted_living_score += 3 × 3 = 9

#### Step 4: Evaluate Decision Thresholds
```json
{
  "memory_care_override": {
    "criteria": "Always trigger if severe_cognitive_risk && no_support",
    "recommendation": "Memory Care"
  },
  "assisted_living": {
    "criteria": "assisted_living_score >= 6",
    "recommendation": "Assisted Living"
  }
}
```

Thresholds evaluated in priority order:
1. memory_care_override (highest priority)
2. no_care_needed
3. assisted_living
4. moderate_needs_assisted_living
5. in_home_with_support (and variants)

First matching threshold wins.

---

## Code Changes

### `logic.py` - Rewritten `derive_outcome()` Function

**New Implementation:**
```python
def derive_outcome(answers: Dict[str, Any], context: Dict[str, Any]) -> OutcomeContract:
    # Load module.json + logic.json (NOT module.json.OLD)
    # Evaluate all flags from logic.json
    # Map flags to categories
    # Calculate in_home_score and assisted_living_score
    # Evaluate decision thresholds
    # Generate summary points
    # Return OutcomeContract with recommendation
```

**Helper Functions Added:**
- `_evaluate_trigger(trigger, answers)` - Parses and evaluates flag trigger conditions
- `_evaluate_criteria(criteria, ctx)` - Evaluates decision threshold criteria

**Trigger Evaluation:**
Supports complex expressions:
- `"mood == 'low'"` → Equality
- `"mobility in ['wheelchair', 'bedbound']"` → List membership
- `"badls.length > 0"` → Array length
- `"chronic_conditions includes ['parkinsons', 'stroke']"` → Array contains
- `"additional_conditions matches '(?i)dementia'"` → Regex
- `"condition1 || condition2"` → Logical OR

**Criteria Evaluation:**
Converts logic.json criteria to Python expressions:
- `"in_home_score >= 3"` → Compare scores
- `"high_dependence && no_support"` → Check multiple flags
- `"assisted_living_score >= 6 && !severe_cognitive_risk"` → Complex logic

### `engine.py` - Enhanced Results View

**Updated `_render_results_view()`:**
```python
def _render_results_view(mod: Dict[str, Any], config: ModuleConfig) -> None:
    # Display recommendation
    recommendation = _get_recommendation(mod, config)
    
    # Get summary points from outcomes (from derive_outcome)
    outcomes = st.session_state.get(f"{config.state_key}._outcomes", {})
    points = outcomes.get("summary", {}).get("points", [])
    
    if points:
        # Use detailed summary from logic.py
        st.markdown(f"<ul>{items}</ul>")
    else:
        # Fallback to basic summary
        _render_results_summary(mod, config)
```

Now displays the rich summary points generated by the scoring logic instead of building generic bullets.

---

## Benefits

### ✅ Single Source of Truth
- Only `module.json` for questions
- Only `logic.json` for scoring
- No confusion from duplicate files
- Section order consistent across UI and logic

### ✅ More Sophisticated Scoring
- Flag-based instead of simple question weights
- Category-based aggregation
- Different weights for different care settings
- Priority-ordered decision thresholds

### ✅ Flexible Flag System
- Complex trigger conditions (regex, array operations, logical OR)
- Priority levels (high/medium/low)
- Custom messages for high-priority flags
- Merge with field-level flags from questions

### ✅ Better Recommendations
- Handles edge cases (memory_care_override)
- Considers multiple factors simultaneously
- Confidence scoring based on data completeness
- Detailed audit trail in outcomes

---

## Testing Checklist

### Basic Flow ✅
1. Complete all GCP questions
2. Click Continue on Daily Living section
3. Verify Results/Summary page loads
4. Check recommendation displays

### Recommendation Logic
1. **Independent** - No significant flags, low scores
2. **In-Home with Support** - Moderate flags, in_home_score >= 3
3. **Assisted Living** - High flags, assisted_living_score >= 6
4. **Memory Care** - severe_cognitive_risk + no_support (override)

### Flag Testing
- Moderate memory_changes → cog_moderate flag
- Severe memory_changes → cog_severe, severe_cognitive_risk flags
- Multiple falls → falls_multiple, high_safety_concern flags
- Low mood → emo_concern, mental_health_concern flags
- BADL selections → moderate_dependence, veteran_aanda_risk flags

### Summary Points
- High-priority flag messages appear FIRST
- Independence snapshot (from help_overall or badls)
- Cognitive notes (memory_changes + behaviors)
- Medication complexity
- Caregiver hours
- Location/access

### Handoff Integration
- Flags stored in `handoff["gcp"]["flags"]`
- cognitive_risk convenience flag set
- meds_management_needed flag set
- Services in Concierge Hub filter based on flags

---

## Files Modified

1. **`products/gcp/modules/care_recommendation/logic.py`**
   - Rewrote `derive_outcome()` function
   - Added `_evaluate_trigger()` helper
   - Added `_evaluate_criteria()` helper
   - Now uses module.json + logic.json (not module.json.OLD)

2. **`core/modules/engine.py`**
   - Updated `_render_results_view()` to use outcome summary points
   - Falls back to basic summary if points not available

---

## Migration Notes

### What Changed
- ❌ **REMOVED:** Dependency on `module.json.OLD`
- ✅ **NEW:** Flag-based scoring from `logic.json`
- ✅ **NEW:** Category-based aggregation
- ✅ **NEW:** Complex trigger evaluation
- ✅ **NEW:** Priority-ordered decision thresholds

### Backward Compatibility
- OutcomeContract structure unchanged
- Handoff format unchanged
- Flag names preserved where possible
- Summary points still use same format

### Future Enhancements
- Could add more decision thresholds
- Could create new flag triggers
- Could adjust category weights
- Could add tier-based modifiers
- All changes in logic.json (no code changes needed!)

---

## Status: ✅ READY FOR TESTING

- ✅ Code compiles successfully
- ✅ Streamlit restarted
- ✅ Single source of truth (module.json + logic.json)
- ✅ New scoring system implemented
- ✅ Results view displays recommendations
- ⏳ **NEEDS TESTING:** Complete GCP flow with various answer combinations

**Next Step:** Test the complete flow and verify recommendations are accurate!
