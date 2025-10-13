# GCP Recommendation & Cost Planner Integration - Issue Resolution

## Issues Reported

1. ❌ **Cost Planner is still gated** even though GCP is complete
2. ❌ **Recommendation not showing on GCP tile** after completion

## Root Cause Analysis

### Issue 1: Cost Planner Gate Check
**Location:** `/products/cost_planner/product.py` lines 41-60

The Cost Planner checks if GCP is complete by looking at:
```python
gcp_progress = float(st.session_state.get("gcp", {}).get("progress", 0))

if gcp_progress < 100:
    # Block access - show "GCP Required" message
```

**Problem:** The check is CORRECT, but the progress might not be getting set to 100 because:
1. User didn't reach the results step
2. `_ensure_outcomes()` wasn't called
3. An error occurred during outcomes computation

### Issue 2: Recommendation Not Displaying
**Location:** `/core/modules/engine.py` line 655 (`_render_results_view`)

The results page gets the recommendation from:
```python
recommendation = _get_recommendation(mod, config)
```

Which looks in:
```python
outcome_key = f"{config.state_key}._outcomes"
outcomes = st.session_state.get(outcome_key, {})
recommendation = outcomes.get("recommendation")
```

**Problem:** If `recommendation` is None or empty, nothing displays!

## Diagnostic Steps

### Step 1: Add Debug Page to Nav

Add this to `config/nav.json` under the "app_utilities" group:

```json
{
  "key": "debug_gcp",
  "label": "🔍 Debug GCP",
  "module": "pages.debug_gcp:render"
}
```

### Step 2: Run the App and Check Debug Page

```bash
streamlit run app.py
```

Navigate to the Debug GCP page and check:

1. **GCP State:**
   - `progress`: Should be 100.0 after completing GCP
   - `status`: Should be "done"
   - `care_tier`: Should have the recommendation (e.g., "Assisted Living")
   - `_outcomes`: Should exist with recommendation data

2. **Handoff Data:**
   - `handoff['gcp']['recommendation']`: Should have the tier name
   - `handoff['gcp']['flags']`: Should have flags dict
   - Should show "✅ Recommendation ready for Cost Planner"

3. **Cost Planner Gate Check:**
   - Should show "✅ GATE CHECK PASSES"
   - If blocked, use the "⚡ Force GCP to 100% Complete" button (dev only)

### Step 3: Check Console Output

Look for `[DEBUG]` lines in your terminal:

```
[DEBUG] Outcomes computed successfully:
  Recommendation: Assisted Living
  Tier: 2
  Score: 31
  Flags: 6 flags

[DEBUG] Handoff data set for 'gcp':
  recommendation: Assisted Living
  flags: 6 flags
  domain_scores: 8 domains

[DEBUG] _render_results_view called:
  outcomes exists: True
  recommendation from outcomes: Assisted Living
  formatted recommendation: Based on your answers, we recommend Assisted Living.
```

**If you DON'T see these lines:**
- Outcomes aren't being computed
- Results step isn't being reached
- An error is happening silently

## Likely Scenarios & Fixes

### Scenario A: User Skipped Questions
**Symptom:** Progress < 100, no outcomes

**Fix:** Complete all required questions in GCP assessment

**How to check:**
```python
# On debug page, check:
gcp_state.get("progress", 0)  # Should be 100.0
gcp_state.get("_outcomes")    # Should exist
```

### Scenario B: Outcomes Error (Silent Failure)
**Symptom:** Progress might be high, but no outcomes or recommendation

**Fix:** Check for errors in Streamlit UI or console

**What to look for:**
- Red error boxes on GCP results page
- Traceback in terminal
- Missing required answers causing derive_outcome() to fail

### Scenario C: Results Step Not Reached
**Symptom:** Progress stops before 100

**Fix:** Click through to the final results page

**How to check:**
```python
gcp_state.get("_step")  # Should be at results step index (usually 4 or 5)
```

### Scenario D: Navigation Configuration Mismatch
**Symptom:** Outcomes computed but not displayed

**Fix:** Verify `results_step_id` in product.py matches module.json

**Check:**
```python
# In products/gcp/product.py
return ModuleConfig(
    ...
    results_step_id="results",  # Must match section.id in module.json
)
```

## Testing Checklist

- [ ] Complete GCP assessment from start to results page
- [ ] Check debug page shows:
  - [ ] `gcp.progress = 100.0`
  - [ ] `gcp.status = "done"`
  - [ ] `gcp._outcomes` exists
  - [ ] `handoff['gcp']['recommendation']` set
- [ ] Check terminal shows `[DEBUG]` output for:
  - [ ] Outcomes computation
  - [ ] Handoff data set
  - [ ] Results view rendering
- [ ] Navigate to Cost Planner
  - [ ] Should NOT show "GCP Required" message
  - [ ] Should proceed to landing page
- [ ] Check GCP results page
  - [ ] Should show: "Based on your answers, we recommend [Tier]."
  - [ ] Should show summary points
  - [ ] Should NOT show "Your Guided Care Plan Summary" (generic fallback)

## Quick Commands

### Run App with Debug
```bash
streamlit run app.py
```

### Check Integration Test
```bash
python products/gcp/modules/care_recommendation/test_integration.py
```

### View Session State Structure
```bash
python debug_gcp_state.py
```

## Files Modified for Debugging

1. **`/core/modules/engine.py`**
   - Added debug output in `_ensure_outcomes()` lines 377-387
   - Added debug output in `_render_results_view()` lines 666-672
   - Updated `_get_recommendation()` to handle properly-formatted strings lines 605-616

2. **`/pages/debug_gcp.py`** (NEW)
   - Diagnostic page to check session state
   - Shows GCP progress, handoff data, gate checks
   - Quick fix button to force completion (dev only)

3. **`/debug_gcp_state.py`** (NEW)
   - CLI script to show expected session state structure
   - Helps understand what should be set

## Next Steps

1. **Add debug page to nav.json**
2. **Run the app and complete GCP**
3. **Check the debug page** - it will tell you exactly what's wrong
4. **Look at terminal console** for [DEBUG] output
5. **Report findings:**
   - What does the debug page show?
   - Do you see [DEBUG] output in terminal?
   - What's the value of `gcp.progress`?
   - Does `gcp._outcomes` exist?
   - What's in `handoff['gcp']`?

## Expected Behavior

### After GCP Completion:
```python
# Session State
st.session_state["gcp"] = {
    "progress": 100.0,
    "status": "done",
    "care_tier": "Assisted Living",  # or other tier
    "_step": 5,  # results step
    "_outcomes": {
        "recommendation": "Assisted Living",
        "confidence": 0.85,
        "flags": {...},
        "tags": [...],
        "domain_scores": {...},
        "summary": {...},
        "routing": {...},
        "audit": {...}
    }
}

st.session_state["handoff"] = {
    "gcp": {
        "recommendation": "Assisted Living",
        "flags": {...},
        "tags": [...],
        "domain_scores": {...}
    }
}
```

### GCP Results Page Should Show:
```
Based on your answers, we recommend Assisted Living.

• [Summary points from scoring logic...]
• ...
```

### Cost Planner Should:
- NOT show "⚠️ **Guided Care Plan Required**" message
- Proceed directly to landing/quick estimate page
- Use handoff data to pre-populate care type

---

**Status:** Diagnostic tools ready. Please run the app and check the debug page to identify the specific issue.

**Next Action:** Add debug page to nav.json, run app, complete GCP, check debug page output.
