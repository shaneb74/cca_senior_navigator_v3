# Dropdown Conditional Visibility Fix

## Issue
Dropdowns require **two clicks** to reveal the next part of the question. When a user selects a value that should make dependent fields visible (via `visible_if` conditions), the fields don't appear until the user clicks again.

## Root Cause
The visibility check was only looking at the `state` dict, which gets updated AFTER all widgets are rendered. Here's the broken flow:

```
RENDER CYCLE 1:
1. User selects "Yes" in dropdown
2. Dropdown widget updates st.session_state["field_has_va_disability"] = "yes"
3. Visibility check for rating field: checks state.get("has_va_disability")
4. ❌ state["has_va_disability"] still has old value (not yet updated)
5. Rating field remains hidden
6. After render: state.update(new_values) updates state["has_va_disability"] = "yes"

RENDER CYCLE 2 (user clicks anything):
7. Visibility check: state.get("has_va_disability") = "yes"
8. ✅ Rating field becomes visible
```

**Problem**: The state dict lags one render cycle behind the widget session state.

## The Fix

### Location: `core/assessment_engine.py`

### Function: `_is_field_visible()`

**Before:**
```python
def _is_field_visible(field: dict[str, Any], state: dict[str, Any]) -> bool:
    """Check if field should be visible based on visible_if condition."""
    visible_if = field.get("visible_if")
    if not visible_if:
        return True

    check_field = visible_if.get("field")
    if not check_field:
        return True

    current_value = state.get(check_field)  # ❌ Lags one render behind

    # Check conditions...
```

**After:**
```python
def _is_field_visible(field: dict[str, Any], state: dict[str, Any]) -> bool:
    """Check if field should be visible based on visible_if condition."""
    visible_if = field.get("visible_if")
    if not visible_if:
        return True

    check_field = visible_if.get("field")
    if not check_field:
        return True

    # CRITICAL FIX: Check widget session state first (has current user selection)
    # If user just changed a dropdown, the new value is in st.session_state[widget_key]
    # but not yet in the state dict. We need to check session state to show/hide
    # dependent fields immediately on the next render.
    widget_key = f"field_{check_field}"
    if widget_key in st.session_state:
        current_value = st.session_state[widget_key]  # ✅ Current value
    else:
        current_value = state.get(check_field)  # Fallback for first render

    # Check conditions...
```

## How It Works Now

```
RENDER CYCLE 1:
1. User selects "Yes" in dropdown
2. Dropdown widget updates st.session_state["field_has_va_disability"] = "yes"
3. (App re-renders immediately - Streamlit auto-rerun)

RENDER CYCLE 2 (automatic):
4. Visibility check for rating field:
   - Looks for st.session_state["field_has_va_disability"] first
   - ✅ Finds "yes" (just set by dropdown)
   - Rating field becomes visible immediately!
5. User sees rating dropdown appear
6. After render: state.update(new_values) syncs state dict
```

**Result**: Dependent fields appear after ONE click, not two.

## Examples

### VA Benefits Assessment

**User Action**: Select "Yes" for "Do you receive VA Disability Compensation?"

**Expected Behavior** (now working):
- ✅ Disability Rating Percentage dropdown appears immediately
- ✅ Dependents Status dropdown appears immediately
- ✅ Monthly VA Disability Payment field appears immediately (when rating/dependents selected)

**Previous Behavior** (broken):
- ❌ User had to click something else first
- ❌ Fields appeared on second render only

### Aid & Attendance Section

**User Action**: Select "Yes" for "Do you receive VA Aid & Attendance benefits?"

**Expected Behavior** (now working):
- ✅ Monthly Aid & Attendance Payment field appears immediately
- ✅ Household Status dropdown appears immediately
- ✅ Eligibility Notes field appears immediately

## Configuration Pattern

This fix applies to ALL fields with `visible_if` conditions:

```json
{
  "key": "dependent_field",
  "label": "This field depends on another",
  "type": "select",
  "visible_if": {
    "field": "parent_field",
    "equals": "yes"
  }
}
```

Or with "in" condition:

```json
{
  "key": "dependent_field",
  "label": "Shows for multiple parent values",
  "type": "currency",
  "visible_if": {
    "field": "parent_field",
    "in": ["yes", "applied"]
  }
}
```

## Testing Instructions

### Test Case 1: VA Disability Section
1. Navigate to VA Benefits assessment
2. **Select "Yes"** for "Do you receive VA Disability Compensation?"
3. **Verify**: Rating and Dependents dropdowns appear immediately (no second click)

### Test Case 2: Rating Field
1. Select "Applied" for VA Disability
2. **Verify**: Rating and Dependents dropdowns appear immediately

### Test Case 3: Aid & Attendance
1. Select "Yes" for "Do you receive VA Aid & Attendance benefits?"
2. **Verify**: Payment field, Household Status, and Notes field appear immediately

### Test Case 4: Monthly Payment Field
1. Ensure "Yes" is selected for VA Disability
2. Select rating and dependents
3. **Verify**: Monthly VA Disability Payment field is visible (should show calculated amount)

## Verification Checklist

- [ ] VA Disability: "Yes" → shows rating/dependents immediately
- [ ] VA Disability: "Applied" → shows rating/dependents immediately  
- [ ] VA Disability: "No" → hides all dependent fields
- [ ] VA Disability: "Considering" → hides rating/dependents
- [ ] Aid & Attendance: "Yes" → shows payment field immediately
- [ ] Aid & Attendance: "Applied" → shows household status immediately
- [ ] Aid & Attendance: "No" → hides all A&A fields
- [ ] No "ghost" fields or flashing
- [ ] No need for extra clicks or interactions

## Technical Details

### Streamlit Widget State Management

Streamlit manages widget values in two places:
1. **`st.session_state[widget_key]`**: The live widget value (updated immediately on interaction)
2. **Custom state dict**: Application state (updated after render in `state.update(new_values)`)

The visibility function now checks **both** sources, prioritizing the live widget value.

### Widget Key Pattern

All widgets use this key format:
```python
widget_key = f"field_{field_key}"
```

Example:
- Field key: `has_va_disability`
- Widget key: `field_has_va_disability`
- Session state location: `st.session_state["field_has_va_disability"]`

### Fallback Logic

If the widget hasn't been rendered yet (first load), `st.session_state[widget_key]` won't exist. The function falls back to the state dict:

```python
if widget_key in st.session_state:
    current_value = st.session_state[widget_key]  # Use live value
else:
    current_value = state.get(check_field)  # Use persisted value
```

This ensures:
- ✅ Immediate visibility updates on interaction
- ✅ Correct visibility on initial page load
- ✅ Correct visibility when restoring from persistence

## Related Fixes

This fix works together with:
- **VA Widget Timing Fix** (`VA_WIDGET_TIMING_FIX.md`): VA disability auto-population before render
- **Widget State Management Fix**: Consistent widget key pattern across all field types

## Benefits

1. **Better UX**: Fields appear immediately when conditions are met
2. **Fewer clicks**: User doesn't need to interact twice
3. **More intuitive**: Form behaves as users expect
4. **Works everywhere**: Applies to all assessments with `visible_if` conditions

## Next Steps

1. **Hard refresh browser** (Cmd+Shift+R) to load updated code
2. **Test all conditional fields** in VA Benefits assessment
3. **Test other assessments** that use `visible_if` (Income, Assets, etc.)
4. **Verify persistence**: Check that hidden fields don't lose their values
