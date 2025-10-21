# VA Disability Payment Read-Only Display Fix

**Date:** October 19, 2025  
**Issue:** VA Disability Monthly Payment field shows as editable textbox instead of read-only display  
**Branch:** `bugfix/gcp-issues`  
**Status:** ✅ Fixed

---

## Problem Summary

In the VA Benefits assessment, the "Monthly VA Disability Payment" field was showing as an editable `number_input` textbox, even though:
- ✅ The value auto-calculates correctly based on rating + dependents
- ✅ The value displays correctly in the summary at bottom of page
- ❌ Users could manually edit the calculated value (confusing)
- ❌ Appeared as if user needed to enter it manually

### User Impact

- Confusing UX - auto-calculated field looked like it needed manual entry
- Users might override the correct calculation
- Inconsistent with help text that says "automatically calculated"
- Unclear that the field is informational, not input

---

## Expected Behavior

The "Monthly VA Disability Payment" field should:
1. ✅ Display the auto-calculated amount based on rating + dependents
2. ✅ Be **read-only** (disabled) - no manual editing needed
3. ✅ Show $ formatted value with cents (e.g., $1,622.44)
4. ✅ Update automatically when rating or dependents change
5. ✅ Still contribute to summary calculation at bottom

---

## The Fix

### Solution Approach

Added support for `readonly` flag on field definitions. When `readonly: true`:
- Field renders as `disabled=True` in Streamlit
- Shows grayed-out appearance (visual indication it's read-only)
- Value still accessible programmatically
- Still included in form submission/state

### Code Changes

#### 1. VA Benefits Config (`va_benefits.json`)

**File:** `products/cost_planner_v2/modules/assessments/va_benefits.json`  
**Line:** ~137

```json
// BEFORE:
{
  "key": "va_disability_monthly",
  "label": "Monthly VA Disability Payment",
  "type": "currency",
  "required": false,
  "min": 0,
  "max": 10000,
  "step": 10,
  "default": 0,
  "help": "This amount is automatically calculated based on your disability rating and dependents using 2025 official VA rates. You can adjust manually if needed.",  // ❌ Misleading
  "visible_if": {
    "field": "has_va_disability",
    "equals": "yes"
  }
}

// AFTER:
{
  "key": "va_disability_monthly",
  "label": "Monthly VA Disability Payment",
  "type": "currency",
  "required": false,
  "min": 0,
  "max": 10000,
  "step": 10,
  "default": 0,
  "readonly": true,  // ✅ New flag - makes field read-only
  "help": "This amount is automatically calculated based on your disability rating and dependents using 2025 official VA rates.",  // ✅ Accurate
  "visible_if": {
    "field": "has_va_disability",
    "equals": "yes"
  }
}
```

**Changes:**
- Added `"readonly": true` flag
- Updated help text to remove "You can adjust manually if needed" (no longer true)

#### 2. Assessment Engine (`assessment_engine.py`)

**File:** `core/assessment_engine.py`  
**Function:** `_render_fields()` - currency field rendering (line ~403)

```python
# BEFORE:
if field_type == "currency":
    min_val = field.get("min", 0)
    max_val = field.get("max", 10000000)
    step = field.get("step", 100)
    # ... type conversions ...
    
    value = container.number_input(
        label=label,
        label_visibility="collapsed",
        min_value=min_val,
        max_value=max_val,
        value=current_value,
        step=step,
        format="%.2f",
        help=help_text,
        key=widget_key,
        # ❌ No disabled parameter
    )
    new_values[key] = value

# AFTER:
if field_type == "currency":
    min_val = field.get("min", 0)
    max_val = field.get("max", 10000000)
    step = field.get("step", 100)
    readonly = field.get("readonly", False)  # ✅ Get readonly flag
    # ... type conversions ...
    
    value = container.number_input(
        label=label,
        label_visibility="collapsed",
        min_value=min_val,
        max_value=max_val,
        value=current_value,
        step=step,
        format="%.2f",
        help=help_text,
        key=widget_key,
        disabled=readonly,  # ✅ Make read-only if specified
    )
    new_values[key] = value
```

**Changes:**
- Added `readonly = field.get("readonly", False)` to read flag from config
- Added `disabled=readonly` parameter to `st.number_input()`
- When `readonly=True`, Streamlit renders field as disabled (grayed out, uneditable)

---

## How It Works

### Visual Behavior

**Before Fix:**
```
Monthly VA Disability Payment
[1622.44] ← White textbox, cursor appears, user can edit
```

**After Fix:**
```
Monthly VA Disability Payment
[1622.44] ← Grayed out textbox, no cursor, cannot edit ✅
```

### Data Flow (Unchanged)

```
1. User selects rating: "60%"
2. User selects dependents: "Veteran with spouse and one child"
3. _auto_populate_va_disability() calculates: $1,622.44
4. Updates state: state["va_disability_monthly"] = 1622.44
5. safe_rerun() triggers page refresh
6. Field renders with value=1622.44, disabled=True ✅
7. User sees grayed-out field with $1,622.44
8. Summary shows: $1,622/month ✅
9. Both match ✅
```

**Key:** The auto-population logic is unchanged - only the display changes from editable to read-only.

---

## Testing Verification

### Test Cases

#### Test 1: Field Appears Read-Only ✅
```
1. Navigate to VA Benefits assessment
2. Select "Yes" for VA Disability
3. Select rating "60%"
4. Select dependents "Veteran with spouse and one child"
   Expected: Field shows $1,622.44 and is grayed out ✅
   Actual: Field shows $1,622.44 and is grayed out ✅
```

#### Test 2: Cannot Edit Field ✅
```
1. With field showing $1,622.44
2. Click on field
   Expected: No cursor, cannot edit ✅
   Actual: No cursor, cannot edit ✅
3. Try to type
   Expected: No change ✅
   Actual: No change ✅
```

#### Test 3: Auto-Calculation Still Works ✅
```
1. Field shows $1,622.44 (60%, spouse + 1 child)
2. Change rating to "70%"
   Expected: Field updates to $2,019.95 ✅
   Actual: Field updates to $2,019.95 ✅
3. Change dependents to "Veteran with spouse"
   Expected: Field updates to $1,908.95 ✅
   Actual: Field updates to $1,908.95 ✅
```

#### Test 4: Summary Still Correct ✅
```
1. VA Disability shows: $1,908.95 (read-only)
2. Summary at bottom shows: $1,909/month
   Expected: Both match (rounded) ✅
   Actual: Both match ✅
```

#### Test 5: Help Text Accurate ✅
```
Hover over help icon (?)
Expected: "This amount is automatically calculated based on your disability rating and dependents using 2025 official VA rates."
Actual: Same text, no mention of manual adjustment ✅
```

---

## Edge Cases Handled

### 1. No Value Yet
```
Scenario: User hasn't selected rating/dependents yet
Behavior:
- Field shows $0.00 (min value)
- Still read-only (grayed out)
- Updates when rating/dependents selected
✅ Correct
```

### 2. Rating Changed Multiple Times
```
Scenario: User changes rating 3 times
Behavior:
- Each change triggers auto-calculation
- Field updates each time
- Always read-only
- User never tempted to manually edit
✅ Correct
```

### 3. Save and Reload
```
Scenario: User saves assessment, then reopens later
Behavior:
- Saved value loads into field
- Field still read-only
- If user changes rating, recalculates
✅ Correct
```

### 4. Validation
```
Scenario: User tries to save without selecting rating
Behavior:
- Field shows $0.00 (read-only)
- Validation allows save (field not required)
- No manual entry needed
✅ Correct
```

---

## Benefits of Read-Only Approach

### User Experience
- ✅ **Clear intent:** Grayed-out field signals "calculated, don't touch"
- ✅ **No confusion:** Users know they don't need to enter it manually
- ✅ **Trust:** Shows system is handling calculation automatically
- ✅ **Prevents errors:** Can't accidentally override correct calculation

### Technical
- ✅ **Simple implementation:** Just add `disabled=True`
- ✅ **No data flow changes:** Value still in state, still in submission
- ✅ **Backward compatible:** Other currency fields unaffected
- ✅ **Reusable pattern:** Can apply `readonly` flag to any field type

### Accessibility
- ✅ **Screen readers:** Announce as "disabled" or "read-only"
- ✅ **Keyboard users:** Can tab past field without stopping
- ✅ **Visual indication:** Gray color universally understood as disabled

---

## Related Code

### Other Fields That Could Use This

**Potential candidates for `readonly: true` flag:**

1. **Calculated summary fields** - Any field that shows a sum/total
2. **Auto-populated fields** - Fields filled by system logic
3. **Display-only information** - Reference data user needs to see but not edit

**Example: Total Monthly Income**
```json
{
  "key": "total_monthly_income",
  "label": "Total Monthly Income",
  "type": "currency",
  "readonly": true,
  "help": "Calculated from all income sources above"
}
```

### Field Types That Support `readonly`

Currently implemented:
- ✅ `currency` - number_input with disabled parameter

Could be extended to:
- ⏳ `text` - text_input with disabled parameter
- ⏳ `textarea` - text_area with disabled parameter
- ⏳ `select` - selectbox with disabled parameter
- ⏳ `date` - date_input with disabled parameter

**Note:** For now, only `currency` fields support `readonly` since that's what VA Benefits needed.

---

## Performance

**No performance impact:**
- Same widget rendering
- Same state updates
- Just adds one boolean parameter
- No extra reruns

---

## Accessibility

**Improved accessibility:**
- ✅ Visual affordance (gray = disabled)
- ✅ Screen reader support (announced as disabled)
- ✅ Keyboard navigation (skip over disabled fields)
- ✅ ARIA attributes handled by Streamlit

---

## Commit Message

```
fix(va-benefits): Make VA disability payment field read-only

The "Monthly VA Disability Payment" field was showing as an editable
textbox even though it auto-calculates from rating + dependents. This
confused users who thought they needed to enter it manually.

Changes:
- va_benefits.json: Added "readonly": true flag to field definition
- assessment_engine.py: Added readonly support for currency fields
- When readonly=true, renders as disabled=True (grayed out)

User Experience:
- Field now appears grayed out (visual cue) ✅
- Cannot be edited (prevents override of calculation) ✅
- Still shows calculated value ($1,622.44 etc.) ✅
- Still contributes to summary at bottom ✅
- Help text updated to remove "adjust manually" mention ✅

Auto-calculation logic unchanged - field just displays result
as read-only instead of editable.

Affects: VA Benefits assessment only
```

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Field Appearance** | White textbox (editable) ❌ | Grayed textbox (read-only) ✅ |
| **User Can Edit** | Yes (confusing) ❌ | No (correct) ✅ |
| **Auto-Calculation** | Works ✅ | Works ✅ |
| **Summary Calculation** | Works ✅ | Works ✅ |
| **Help Text** | "You can adjust manually" ❌ | "Automatically calculated" ✅ |
| **Visual Clarity** | Unclear ❌ | Clear (disabled look) ✅ |

**Status: FULLY RESOLVED** ✅

---

**Last Updated:** October 19, 2025  
**Branch:** `bugfix/gcp-issues`  
**Files Modified:**
- `products/cost_planner_v2/modules/assessments/va_benefits.json` (added readonly flag)
- `core/assessment_engine.py` (added readonly support for currency fields)

**Related Docs:**
- VA_FIELD_AUTO_POPULATION_FIX.md (auto-calculation implementation)
- CURRENCY_FIELD_FIX.md (currency field type fixes)
