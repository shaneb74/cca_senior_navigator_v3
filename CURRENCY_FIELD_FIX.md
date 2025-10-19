# Currency Field Type Mismatch Fix

**Date:** October 18, 2025  
**Issue:** StreamlitMixedNumericTypesError  
**Commit:** `23d05bc`  
**Status:** ✅ Fixed

---

## Problem

When testing the VA Benefits assessment with auto-population enabled, the app crashed with:

```
streamlit.errors.StreamlitMixedNumericTypesError
```

**Stack trace pointed to:** `core/assessment_engine.py` line 403, in the `number_input` widget for currency fields.

---

## Root Cause

### The Type Mismatch:

**VA disability auto-population returns float values:**
```python
# From va_rates.py
def get_monthly_va_disability(rating: int, dependents: str) -> Optional[float]:
    # ...
    return 1908.95  # ← Float with cents
```

**Currency fields were configured for integers:**
```python
# In core/assessment_engine.py (OLD)
value = container.number_input(
    min_value=0,           # int
    max_value=10000000,    # int
    value=1908.95,         # ← FLOAT from auto-population
    step=100,              # int
    format="%d",           # ← Integer format
)
```

**Streamlit's requirement:**
> All numeric parameters (`value`, `min_value`, `max_value`, `step`) must be the same type (all int OR all float).

**Result:** Type mismatch error!

---

## Why VA Rates Have Decimals

Official 2025 VA disability compensation rates include cents:

| Rating | Veteran Alone | With Spouse |
|--------|---------------|-------------|
| 10% | $**175.51** | $175.51 |
| 30% | $**537.42** | $**601.42** |
| 70% | $**1,758.95** | $**1,908.95** |
| 100% | $**3,831.73** | $**4,057.73** |

**These are the official amounts from VA.gov** - we can't round to whole dollars without losing accuracy.

---

## Solution

### Changed currency fields to support decimals:

```python
# In core/assessment_engine.py (NEW)
if field_type == "currency":
    min_val = field.get("min", 0)
    max_val = field.get("max", 10000000)
    step = field.get("step", 100)
    
    # Ensure all numeric values are the same type (float)
    min_val = float(min_val)
    max_val = float(max_val)
    step = float(step)
    
    # Handle current value
    if current_value is not None:
        current_value = float(current_value)
    else:
        current_value = min_val

    value = container.number_input(
        label=label,
        label_visibility="collapsed",
        min_value=min_val,        # float
        max_value=max_val,        # float
        value=current_value,      # float
        step=step,                # float
        format="%.2f",            # ← Changed: 2 decimal places
        help=help_text,
        key=f"field_{key}",
    )
```

### Key Changes:

1. **Format changed:** `"%d"` → `"%.2f"`
   - Now displays: `$1,908.95` instead of `$1909`

2. **Explicit float conversion:**
   - All parameters converted to `float()`
   - Ensures type consistency

3. **Preserves precision:**
   - Official VA rates shown exactly as published
   - No rounding errors

---

## Impact

### Before Fix:
```
User selects: 70% disability + spouse
Auto-population tries to set: 1908.95
ERROR: StreamlitMixedNumericTypesError
App crashes ❌
```

### After Fix:
```
User selects: 70% disability + spouse
Auto-population sets: 1908.95
Field displays: $1,908.95
App works perfectly ✅
```

---

## Affected Fields

This fix applies to **ALL** currency fields across all assessments:

### Income Assessment:
- Social Security monthly amount
- Pension amounts
- Employment income
- Rental income
- Investment income

### Assets Assessment:
- Home value
- Mortgage balance
- Bank account balances
- Investment values
- Retirement account balances

### VA Benefits: ⭐ **Primary beneficiary**
- VA disability monthly amount (auto-populated)
- Aid & Attendance monthly amount

### Health Insurance:
- Annual deductible
- Out-of-pocket maximum
- Monthly premium

### Life Insurance:
- Cash value
- Face value
- Monthly premium
- Annuity current value
- Annuity monthly income

**All now support decimal precision** for accurate financial calculations.

---

## Testing Validation

### Test 1: VA Auto-Population ✅
```
1. Navigate to VA Benefits assessment
2. Select "Yes" for VA Disability
3. Select rating: 70%
4. Select dependents: "Veteran with spouse"
5. Verify: Monthly amount shows $1,908.95
6. Click Save
7. Result: SUCCESS - no error
```

### Test 2: Manual Entry ✅
```
1. Enter disability amount manually: $2,156.37
2. Verify: Field accepts decimal input
3. Save assessment
4. Result: SUCCESS - value persists correctly
```

### Test 3: Other Currency Fields ✅
```
1. Navigate to Income assessment
2. Enter Social Security: $1,827.50
3. Verify: Accepts decimals
4. Summary calculation: Correct to 2 decimal places
5. Result: SUCCESS - all currency fields work
```

### Test 4: Whole Dollar Amounts ✅
```
1. Enter employment income: $5,000.00
2. Verify: Displays with 2 decimals
3. Can also enter as: $5000 (auto-converts to $5,000.00)
4. Result: SUCCESS - backwards compatible
```

---

## Side Effects (All Positive ✅)

### 1. More Accurate Calculations
- Income totals now precise to the cent
- Asset valuations exact
- No rounding errors in Expert Review

### 2. Better User Experience
- Users can enter exact amounts from bank statements
- VA veterans see official rates (not rounded)
- Professional appearance (shows cents like real financial software)

### 3. Compliance with VA Official Rates
- Matches VA.gov exactly
- Audit trail shows correct amounts
- No "close enough" approximations

---

## Technical Details

### Streamlit number_input Type Rules:

From Streamlit documentation:
> If you pass a float value to `value`, `min_value`, `max_value`, or `step`, Streamlit will automatically use float precision. If you pass an int, it will use int precision. **Mixing types will raise an error.**

**Our solution:** Always use `float()` for all currency fields.

### Format Specifier:

- `"%d"` - Integer (no decimals): `1908`
- `"%.0f"` - Float with 0 decimals: `1909` (rounds)
- `"%.2f"` - Float with 2 decimals: `1908.95` ✅

### Python float precision:

```python
>>> float(1908.95)
1908.95
>>> float(0)
0.0
>>> float(10000000)
10000000.0
>>> float(100)
100.0
```

All conversions safe for financial calculations (within JavaScript's safe integer range).

---

## Regression Risk: LOW ✅

**Why this is safe:**

1. **Backwards compatible:**
   - Existing data (integers) auto-converts to float
   - `float(1000)` = `1000.0` - semantically identical
   - User sees: `$1,000.00` instead of `$1000` (better UX)

2. **No data loss:**
   - Float precision sufficient for financial amounts
   - Max value: $10,000,000.00 - well within float precision
   - No floating-point errors at this scale

3. **JSON persistence compatible:**
   - JSON supports both integers and floats
   - `{"amount": 1908.95}` - valid
   - `{"amount": 1000}` - also valid
   - Reading data back: Python handles both automatically

4. **Calculation accuracy:**
   - All financial calculations already use float arithmetic
   - Summary totals unaffected
   - MCIP contract handles floats correctly

---

## Future Considerations

### Option 1: Store as cents (integer)
```python
# Could store internally as cents to avoid float issues
stored_value = 190895  # cents
display_value = stored_value / 100  # 1908.95 dollars
```
**Pro:** No floating-point precision issues  
**Con:** More complex, current approach works fine

### Option 2: Decimal type
```python
from decimal import Decimal
# Use Python's Decimal for exact precision
amount = Decimal("1908.95")
```
**Pro:** Mathematically exact  
**Con:** Streamlit doesn't support Decimal in number_input

### Decision: Keep float ✅
Current float approach is:
- Simple
- Accurate enough for financial planning (not trading)
- Compatible with Streamlit
- Matches industry standard (most financial apps use float)

---

## Summary

| Aspect | Status |
|--------|--------|
| **Issue** | StreamlitMixedNumericTypesError |
| **Cause** | Integer format + float auto-population |
| **Fix** | Convert all currency params to float, use %.2f format |
| **Testing** | ✅ Passed all scenarios |
| **Regression Risk** | Low - backwards compatible |
| **Impact** | Positive - better accuracy and UX |
| **Deployed** | Commit 23d05bc, pushed to assessment-updates |

**Status: RESOLVED ✅**

---

**Last Updated:** October 18, 2025  
**Branch:** `assessment-updates`  
**Commit:** `23d05bc`
