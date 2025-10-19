# VA Auto-Population Infinite Loop Fix

## Issue Identified
**Symptoms:**
- ✅ Terminal shows correct calculated values ($1,523.93, etc.)
- ✅ Dropdowns work on first click
- ❌ Values not showing in the form field
- ❌ Terminal output "twitching" - continuously updating
- **Root Cause**: Infinite rerun loop

## Root Cause Analysis

### The Infinite Loop Mechanism

```
1. User selects rating/dependents
   ↓
2. new_values contains change → state.update(new_values)
   ↓
3. _auto_populate_va_disability(state) calculates amount
   ↓
4. state["va_disability_monthly"] = 1523.93
   ↓
5. safe_rerun() called → triggers full re-render
   ↓
6. On re-render, line 727 calls _auto_populate_va_disability(state) AGAIN
   ↓
7. State updated again (even with same value)
   ↓
8. Widget sees state "change" and returns it in new_values
   ↓
9. Loop back to step 2 → INFINITE LOOP
```

### Why Values Didn't Show in Form

The issue was **two-tier state management**:
1. **State dict** (`state["va_disability_monthly"]`) - updated by auto-populate function
2. **Widget session state** (`st.session_state["field_va_disability_monthly"]`) - what the widget displays

When we updated the state dict, the widget was already rendered with the OLD value from widget session state. The widget's `value=current_value` parameter uses `state.get(key)`, but this only applies on initial render. Once the widget exists, Streamlit manages its value in `st.session_state[widget_key]`.

## Fixes Applied

### Fix 1: Remove `safe_rerun()` Call
**Location**: `products/cost_planner_v2/assessments.py` lines ~742-747

**Before:**
```python
_auto_populate_va_disability(state)
st.success(f"🔍 DEBUG: Calculated amount: ${state.get('va_disability_monthly', 0):,.2f}")
_persist_assessment_state(product_key, assessment_key, state)
# Trigger rerun to update the UI with auto-populated value
st.warning("🔍 DEBUG: About to call safe_rerun()...")
safe_rerun()
return
```

**After:**
```python
_auto_populate_va_disability(state)
st.success(f"🔍 DEBUG: Calculated amount: ${state.get('va_disability_monthly', 0):,.2f}")
# Note: Removed safe_rerun() to prevent infinite loop
# The field will pick up the updated value on next interaction
```

**Why**: `safe_rerun()` caused the infinite loop. Let Streamlit's natural update cycle handle reruns.

### Fix 2: Update Widget Session State Directly
**Location**: `products/cost_planner_v2/assessments.py` lines ~850-854 (_auto_populate_va_disability function)

**Before:**
```python
if monthly_amount is not None:
    # Update state with calculated amount
    state["va_disability_monthly"] = monthly_amount
    print(f"   ✅ Updated state['va_disability_monthly'] = {monthly_amount}")
    st.toast(f"✅ Calculated VA benefit: ${monthly_amount:,.2f}/month", icon="💰")
```

**After:**
```python
if monthly_amount is not None:
    # Update state dict with calculated amount
    state["va_disability_monthly"] = monthly_amount
    print(f"   ✅ Updated state['va_disability_monthly'] = {monthly_amount}")
    
    # CRITICAL: Also update the widget's session state value
    # This ensures the number_input widget displays the calculated value
    widget_key = "field_va_disability_monthly"
    st.session_state[widget_key] = monthly_amount
    print(f"   ✅ Updated st.session_state['{widget_key}'] = {monthly_amount}")
    
    st.toast(f"✅ Calculated VA benefit: ${monthly_amount:,.2f}/month", icon="💰")
```

**Why**: Updating `st.session_state[widget_key]` tells Streamlit the widget's value has changed, so it will display the new value on the next render.

### Fix 3: Only Auto-Populate When Necessary
**Location**: `products/cost_planner_v2/assessments.py` lines ~727-739

**Before:**
```python
# Auto-populate VA disability amount if this is the VA disability section
if assessment_key == "va_benefits" and section.get("id") == "va_disability":
    _auto_populate_va_disability(state)
    # DEBUG: Show what we calculated
    if state.get("va_disability_monthly"):
        st.info(f"🔍 DEBUG: Auto-calculated VA disability: ${state.get('va_disability_monthly'):,.2f}")
```

**After:**
```python
# Auto-populate VA disability amount if this is the VA disability section
# Only run on initial render (when no widget interactions yet)
if assessment_key == "va_benefits" and section.get("id") == "va_disability":
    # Check if this is initial calculation or if we should recalculate
    should_calculate = (
        state.get("has_va_disability") == "yes" and
        state.get("va_disability_rating") is not None and
        state.get("va_dependents") is not None and
        state.get("va_disability_monthly") is None  # Only if not already set
    )
    if should_calculate:
        print("🔵 Initial VA disability auto-population")
        _auto_populate_va_disability(state)
    # DEBUG: Show what we have in state
    if state.get("va_disability_monthly"):
        st.info(f"🔍 DEBUG: VA disability in state: ${state.get('va_disability_monthly'):,.2f}")
```

**Why**: Only auto-populate on initial render when amount is None. Prevents recalculating on every single rerun.

## How It Works Now

### Correct Flow

```
1. User loads VA Benefits assessment
   ↓
2. If has_disability='yes', rating set, dependents set, amount=None
   ↓ (initial calculation only)
3. _auto_populate_va_disability() calculates amount
   ↓
4. Updates BOTH:
   - state["va_disability_monthly"] = 1523.93
   - st.session_state["field_va_disability_monthly"] = 1523.93
   ↓
5. Widget renders with value from session state
   ↓
6. User changes rating/dependents
   ↓ (recalculation triggered by new_values)
7. _auto_populate_va_disability() called again
   ↓
8. Updates both state locations again
   ↓
9. NO safe_rerun() → no infinite loop
   ↓
10. Next natural interaction/rerun shows updated value
```

### Key Points

1. **No safe_rerun()**: Let Streamlit handle reruns naturally
2. **Widget state updated directly**: `st.session_state[widget_key]` updated alongside state dict
3. **Conditional auto-populate**: Only on initial render if amount is None
4. **Recalculate on change**: When rating/dependents change in new_values

## Testing Instructions

### What Should Happen Now

1. **Load VA Benefits page** → terminal shows initial calculation (if conditions met)
2. **Select rating** (e.g., 60%) → dropdown works on first click
3. **Select dependents** (e.g., "Veteran with spouse") → dropdown works on first click
4. **After both selections** → terminal shows recalculation with correct values
5. **Field updates** → shows $1,523.93 (or appropriate amount)
6. **Terminal stops twitching** → no infinite loop
7. **No continuous reruns** → stable state

### Verification Checklist

- [ ] Terminal shows "🔵 Initial VA disability auto-population" ONCE on page load
- [ ] Terminal shows calculation when rating/dependents change
- [ ] Terminal does NOT continuously repeat the same calculations
- [ ] Field shows calculated amount after selections
- [ ] Toast notification appears: "✅ Calculated VA benefit: $X,XXX.XX/month"
- [ ] Summary section shows correct total
- [ ] No "twitching" or rapid terminal updates
- [ ] Browser remains responsive

### Debug Output to Watch

**Good (one-time calculation):**
```
============================================================
🔍 _auto_populate_va_disability() called
   State keys: [...]
   has_va_disability: 'yes' (type: str)
   va_disability_rating: '60' (type: str)
   va_dependents: 'spouse' (type: str)
   📞 Calling get_monthly_va_disability('60', 'spouse')...
   💰 Result: $1,523.93
   ✅ Updated state['va_disability_monthly'] = 1523.93
   ✅ Updated st.session_state['field_va_disability_monthly'] = 1523.93
============================================================
```

**Bad (infinite loop - should NOT see this):**
```
============================================================
🔍 _auto_populate_va_disability() called
   ...
============================================================
============================================================
🔍 _auto_populate_va_disability() called
   ...
============================================================
============================================================
🔍 _auto_populate_va_disability() called
   ...
============================================================
[repeating continuously...]
```

## What Changed vs. Original Implementation

| Aspect | Original | Fixed |
|--------|----------|-------|
| Rerun trigger | `safe_rerun()` called | No forced rerun |
| State update | State dict only | State dict + widget session state |
| Auto-populate frequency | Every render | Only when needed |
| Loop prevention | None | Conditional calculation |

## Next Steps

1. **Refresh browser** (Cmd+Shift+R) to clear cache
2. **Navigate to VA Benefits** assessment
3. **Watch terminal** for single calculation (not continuous)
4. **Test selections** and verify field updates
5. **Report results** - does field show correct value?

## If Issues Persist

### Field Still Shows $0.00
- Check if widget_key matches: `"field_va_disability_monthly"`
- Verify st.session_state is being updated (check terminal output)
- Check if widget is rendering AFTER state update

### Terminal Still Twitching
- Check for other rerun triggers
- Verify safe_rerun() is completely removed
- Look for other st.rerun() or st.experimental_rerun() calls

### Values Change But Don't Display
- Widget may be caching old value
- Try clearing browser cache completely
- Check if widget key is stable across reruns
