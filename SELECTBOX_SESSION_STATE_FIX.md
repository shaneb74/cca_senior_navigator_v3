# Selectbox Label-to-Value Conversion Fix

## Issue
Conditional fields (with `visible_if` conditions) were not appearing when users selected options in dropdown fields. For example, selecting "Yes" for "Do you receive VA Disability Compensation?" did not reveal the dependent fields (rating, number of dependents).

## Root Cause
Streamlit's `st.selectbox()` widget stores the **selected label** (e.g., "Yes") in `st.session_state[widget_key]`, but our JSON configuration files specify **values** (e.g., "yes") in `visible_if` conditions:

```json
{
  "id": "has_va_disability",
  "type": "select",
  "options": [
    {"value": "yes", "label": "Yes"},
    {"value": "no", "label": "No"}
  ]
}
```

```json
{
  "id": "va_disability_rating",
  "visible_if": {"field": "has_va_disability", "equals": "yes"}
}
```

The visibility check in `_is_field_visible()` was comparing:
- Widget session state = **"Yes"** (label, capitalized)
- `visible_if["equals"]` = **"yes"** (value, lowercase)

Case-sensitive comparison: `"Yes" == "yes"` → **False** → fields stay hidden

## Why We Can't Override Session State
Initial attempt to fix: store the converted value in `st.session_state[widget_key]` after label→value conversion.

**Problem**: Streamlit owns widget keys and throws an error if you try to manually set them:
```
StreamlitAPIException: Cannot set value for widget key 'field_has_va_disability' 
because it is controlled by a widget
```

## Solution
Instead of overriding session state, pass the **converted values** (`new_values` dict) to the visibility check function:

1. **During rendering**: As selectbox widgets render, we convert label→value and store in `new_values` dict
2. **Pass to visibility check**: Pass `new_values` to `_is_field_visible()` so it can check converted values
3. **Priority order**: Check `new_values` (current render) first, then fall back to `state` (persisted data)

### Code Changes

**`_render_fields()` - Render loop** (line ~351):
```python
for field in fields:
    # Pass new_values so visibility checks can see converted label→value mappings
    if not _should_show_field(field, view_mode, state, new_values):
        continue
    # ... render field and add to new_values ...
```

**`_should_show_field()` - Wrapper** (line ~285):
```python
def _should_show_field(field, view_mode, state, new_values=None):
    if not _is_field_visible(field, state, new_values):
        return False
    # ... level-based filtering ...
```

**`_is_field_visible()` - Core visibility logic** (line ~526):
```python
def _is_field_visible(field, state, new_values=None):
    visible_if = field.get("visible_if")
    if not visible_if:
        return True
    
    check_field = visible_if.get("field")
    
    # CRITICAL: Check new_values first (has converted label→value)
    if new_values and check_field in new_values:
        current_value = new_values[check_field]
    else:
        current_value = state.get(check_field)
    
    if "equals" in visible_if:
        return current_value == visible_if["equals"]
    # ... other conditions ...
```

## How It Works

### Render Cycle
1. User selects "Yes" in dropdown
2. Streamlit stores "Yes" in `st.session_state["field_has_va_disability"]`
3. Selectbox rendering code converts label→value:
   ```python
   selected_label = "Yes"  # From widget
   value = "yes"  # Converted value
   new_values["has_va_disability"] = "yes"
   ```
4. Next field checks visibility:
   ```python
   _is_field_visible(field, state, new_values)
   # Checks new_values["has_va_disability"] = "yes"
   # Compares with visible_if["equals"] = "yes"
   # ✅ Match! Field is visible
   ```

### Why This Works
- **Separation of concerns**: Widget session state remains unchanged (Streamlit controls it)
- **Data integrity**: Persisted state always has values (lowercase), never labels
- **Immediate visibility**: Dependent fields see converted values in same render cycle
- **No widget conflicts**: Never try to override Streamlit's internal widget state

## Files Changed
- `core/assessment_engine.py`:
  - Updated `_is_field_visible()` signature to accept `new_values`
  - Updated `_should_show_field()` signature to accept and pass `new_values`
  - Updated `_render_fields()` to pass `new_values` to `_should_show_field()`

## Testing
1. **Hard refresh** browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)
2. Navigate to Cost Planner v2 → Assets & Resources assessment
3. Test conditional visibility:
   - Select "No, assets are only in my name" → related fields should hide/appear
   - Select "Yes, we share assets" → related fields should appear
4. Navigate to VA Benefits assessment
5. Test conditional visibility:
   - Select "Yes" for VA disability → rating and dependents fields should appear **immediately**
   - Change rating → monthly payment field should appear **immediately**
   - Select "No" → dependent fields should hide **immediately**
6. Verify VA amount calculation still works correctly

## Expected Behavior
✅ All conditional fields appear on **first selection** when dependency is met
✅ Fields hide immediately when dependency is no longer met  
✅ No "double-click" required
✅ No Streamlit API exceptions
✅ VA auto-population continues to work

## Related Fixes
- VA Auto-Population Timing Fix (moved calculation before widget render)
- Dropdown Visibility Approach (check current render values, not just persisted state)
