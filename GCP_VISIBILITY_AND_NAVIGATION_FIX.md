# GCP Module Visibility & Navigation Fix

**Date:** October 13, 2025  
**Issues Fixed:** 
1. Behaviors pill list not rendering
2. Continue button on Daily Living not advancing to Results

---

## Issue #1: Behaviors Question Not Appearing

### Root Cause
The `behaviors` question had a visibility condition that was incompatible with the engine:

**Module.json format (incompatible):**
```json
"visible_if": { "all": [{ "eq": ["memory_changes", ["moderate", "severe"]] }] }
```

**Engine expected format:**
```json
"visible_if": { "key": "memory_changes", "in": ["moderate", "severe"] }
```

The engine's `_is_visible()` function in `core/modules/engine.py` only supports:
- `{ "key": "field_name", "eq": "value" }` - exact match
- `{ "key": "field_name", "in": ["value1", "value2"] }` - value in list

It does NOT support:
- `"all"` / `"any"` boolean logic
- `"contains"` / `"length_gte"` advanced operators
- Nested condition arrays

### Fix Applied
Updated three visibility conditions in `module.json`:

1. **behaviors** - Changed to simple "in" format ✅
2. **badls** - Removed visibility condition (made always visible) ✅
3. **iadls** - Removed visibility condition (made always visible) ✅

The BADL/IADL questions had complex 9-condition "any" logic that cannot be expressed with the current engine's simple visibility system. Since these questions are important for the veteran A&A risk flag, they are now always visible.

---

## Issue #2: Continue Button Not Advancing to Results

### Root Cause
The product loader was filtering out BOTH "info" and "results" sections:

```python
# Old code (WRONG)
if section_type in ("info", "results"):
    continue  # Skip both intro and results
```

The engine navigation uses `next_index = min(step_index + 1, total_steps - 1)` to advance. When the results step wasn't in `config.steps`, clicking Continue on the last form section (Daily Living) had nowhere to go - it just stayed on Daily Living.

The engine also checks `if config.results_step_id and step.id == config.results_step_id` to render the results view, so the results step MUST exist in the steps array.

### Fix Applied
Changed product.py to include the results section:

```python
# New code (CORRECT)
if section_type == "info":
    continue  # Only skip intro - include results!

# ...later when creating StepDef...
is_results = section_type == "results"

steps.append(StepDef(
    # ...
    show_progress=not is_results,      # Don't count results in progress
    show_bottom_bar=not is_results,    # Don't show nav buttons on results
    # ...
))
```

Now the step sequence is:
1. about_you (form) - Progress 1/4
2. medication_mobility (form) - Progress 2/4
3. cognition_mental_health (form) - Progress 3/4
4. daily_living (form) - Progress 4/4
5. **results (results)** - ✅ NOW INCLUDED - Shows summary view

---

## Files Modified

### 1. `products/gcp/modules/care_recommendation/module.json`
- Removed incompatible effects from `additional_conditions` and `mood` questions
- Fixed `behaviors` visibility condition: `{ "key": "memory_changes", "in": ["moderate", "severe"] }`
- Removed complex visibility conditions from `badls` and `iadls` (now always visible)

### 2. `products/gcp/product.py`
- Added imports: `List`, `Optional` from typing
- Created `_normalize_effects()` helper function (handles dict/list formats)
- Updated `_determine_field_type()` to map question types to renderers
- **Fixed section filtering:** Only skip "info", include "results" 
- **Fixed results step properties:** `show_progress=False`, `show_bottom_bar=False`

---

## Testing Checklist

### Behaviors Question Visibility ✅
1. Navigate to GCP → Start module
2. Go through sections: About You → Medication & Mobility → **Cognition & Mental Health**
3. On "Cognitive health or memory changes" question:
   - Select "No concerns" → behaviors question should NOT appear
   - Select "Occasional forgetfulness" → behaviors question should NOT appear
   - Select "Moderate memory or thinking issues" → **behaviors question SHOULD appear** ✅
   - Select "Severe memory issues..." → **behaviors question SHOULD appear** ✅
4. Verify behaviors renders as multi-chip widget with 9 options (Wandering, Aggression, etc.)

### Continue to Results ✅
1. Complete all 4 form sections
2. On Daily Living (last section), fill in required questions
3. Click **Continue** button
4. Should advance to **Results/Summary** view ✅
5. Verify results view shows:
   - GCP recommendations
   - Flag-based messages
   - Care level summary
   - Next steps

### BADL/IADL Always Visible ✅
1. Navigate to Daily Living section
2. Verify "Which basic daily activities..." (BADL) question appears
3. Verify "Which daily tasks..." (IADL) question appears
4. These should be visible regardless of previous answers
5. Selecting any BADL/IADL options should set `veteran_aanda_risk` flag

---

## Technical Notes

### Visibility System Limitations
The current engine (`core/modules/engine.py`) has a simple visibility system that only supports:
- Key-value equality: `{ "key": "field", "eq": "value" }`
- Key-value in list: `{ "key": "field", "in": ["val1", "val2"] }`

To implement the original 9-condition BADL/IADL visibility logic, the engine would need enhancement to support:
- Boolean operators: `"all"`, `"any"`, `"not"`
- Advanced operators: `"contains"`, `"length_gte"`, `"matches"` (regex)
- Nested condition evaluation

For now, BADL/IADL are always visible, which is acceptable since:
1. They're optional questions (not required)
2. Users can skip if not applicable
3. The veteran_aanda_risk flag logic still works correctly

### Effects System Removed
The module.json had effects with `"condition"` and `"flags"` keys, but the engine expected `"when_value_in"` and `"set_flag"` keys. Since all flag logic is already handled by `logic.py`, the effects were redundant and removed.

---

## Status: ✅ COMPLETE

Both issues resolved:
- ✅ Behaviors question now appears when memory_changes is moderate/severe
- ✅ Continue button on Daily Living advances to Results view
- ✅ Progress tracking shows correct 4 steps (form sections only)
- ✅ Results step included but doesn't count toward progress
- ✅ All JSON validated and compiles successfully
- ✅ Streamlit restarted with all fixes applied
