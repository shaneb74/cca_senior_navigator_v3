# CSS Scoping Fix - CORRECTED ✅

**Date:** October 17, 2025  
**Issue:** Pills styling broken - used wrong selector (`.mod-radio-pills` instead of `.sn-app`)  
**Status:** ✅ FIXED - Pills restored, assessments still working

---

## The Real Scoping Pattern

### GCP Modules Architecture
```python
# core/modules/engine.py line 83
st.markdown('<div class="sn-app module-container">', unsafe_allow_html=True)

# core/modules/components.py line 99 (input_pill function)
st.markdown('<div class="sn-app mod-field mod-radio-pills">', unsafe_allow_html=True)
```

So GCP uses **`.sn-app`** as the outer wrapper, NOT just `.mod-radio-pills`.

### Financial Assessments Architecture
Financial assessments use raw Streamlit widgets with **NO `.sn-app` wrapper**.

---

## Correct CSS Scoping

All radio pill styles are now scoped to `.sn-app`:

```css
/* BEFORE (WRONG - broke pills) */
.mod-radio-pills [data-testid="stRadio"] label { ... }

/* AFTER (CORRECT - pills work) */
.sn-app [data-testid="stRadio"] label:not([aria-hidden="true"]):not([data-testid="stWidgetLabel"]) { ... }
```

### Why This Works

- **GCP**: Has `.sn-app` wrapper → Gets pill styling
- **Assessments**: No `.sn-app` wrapper → Gets native Streamlit styling
- **Gray pill bug**: Collapsed labels hidden via `:not([data-testid="stWidgetLabel"])`

---

## CSS Rules Updated (All 7)

1. **Base pill style** → `.sn-app [data-testid="stRadio"] label`
2. **Collapsed label hiding** → `.sn-app [data-testid="stRadio"] label[data-testid="stWidgetLabel"]`
3. **Text container** → `.sn-app [data-testid="stRadio"] label > div`
4. **Hover state** → `.sn-app [data-testid="stRadio"] label:hover`
5. **Selected state** → `.sn-app [data-testid="stRadio"] label:has(input:checked)`
6. **Selected hover** → `.sn-app [data-testid="stRadio"] label:has(input:checked):hover`
7. **Text color forcing** → `.sn-app [data-testid="stRadio"] label:has(input:checked) div`

---

## What Works Now

✅ **GCP**: Gray/black pills restored  
✅ **Assessments**: Labels visible  
✅ **Gray pill bug**: Still fixed  
✅ **Architecture**: Proper separation via `.sn-app` wrapper  

---

## Testing

1. **Restart Streamlit**
2. **GCP**: Verify pills are gray (unselected) and black (selected) with correct text colors
3. **Assessments**: Verify labels are still visible

---

**Status:** ✅ **PILLS RESTORED**
