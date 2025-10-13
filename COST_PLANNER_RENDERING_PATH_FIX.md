# Cost Planner - Rendering Path Fix

**Issue:** Same URL (`?page=cost`) showing TWO different pages:
- ❌ **OLD (wrong):** Standard form rendering without purple GCP box
- ✅ **NEW (correct):** Custom rendering WITH purple GCP box + dynamic button

**Root Cause:** Quick Estimate step was sometimes using standard `run_module()` rendering instead of custom rendering.

---

## Fix Applied

### 1. Added Error Guard
Ensured that if `run_module()` somehow renders `quick_estimate`, it shows an error:

```python
# In _render_base_module() after run_module(config)
if step_id == "quick_estimate":
    st.error("❌ ERROR: quick_estimate using wrong rendering path!")
    st.stop()
```

### 2. Deprecated Old Footer Function
Renamed and disabled `_render_quick_estimate_footer()`:

```python
def _render_quick_estimate_footer_DEPRECATED(context: dict) -> None:
    """DEPRECATED - DO NOT USE."""
    st.error("❌ DEPRECATED FUNCTION CALLED")
    return  # Early exit
```

### 3. Added Debug Info
Shows in sidebar which rendering path is being used:

```python
st.sidebar.write(f"🔍 Debug: step_index={step_index}")
st.sidebar.write(f"🔍 Debug: step.id={step.id}")

if step.id == "quick_estimate":
    st.sidebar.success("✅ Using CUSTOM rendering")
```

---

## Expected Behavior

**When on Quick Estimate (step 1):**
- Sidebar shows: `step_index=1`, `step.id=quick_estimate`
- Sidebar shows: "✅ Using CUSTOM rendering for quick_estimate"
- Page shows: Purple GCP recommendation box
- Page shows: Radio button care type selector
- Page shows: "See My Estimate" blue button

**If you see the OLD page:**
- Sidebar will show error or wrong step ID
- This indicates step index is incorrect or config mismatch

---

## Testing

1. Navigate to: http://localhost:8501/?page=cost
2. Click Continue from Intro
3. **Check sidebar:** Should show step_index=1, step.id=quick_estimate, "✅ Using CUSTOM rendering"
4. **Check page:** Should show purple box with GCP recommendation
5. **If OLD page appears:** Check sidebar debug info and report values

---

## Files Modified

- `products/cost_planner/product.py` (lines 114-126: error guard, lines 260-271: deprecated footer)

---

**Status:** Ready for testing  
**Next:** Refresh browser and check sidebar debug output
