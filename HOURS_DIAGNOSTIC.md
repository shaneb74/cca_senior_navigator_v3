# Hours Recommendation Diagnostic

## Issue
User seeing max 4.0 hours recommendation despite expecting much higher based on care needs.

## Root Cause Analysis

### From Logs:
```
[HOURS_PARSE] gcp_keys=[...] band=None result=None
[HOURS_CHECK] llm_high=None
[CARE_CONTEXT] Extracted from GCP: adl=0 iadl=0 cognition=None behaviors=0 falls=None
[HOURS_CHECK] fallback_llm_high=4.0 band=2-4h/day
```

### Problems Identified:

1. **No GCP hours data** (`band=None`)
2. **No care context** (`adl=0 iadl=0 cognition=None`)
3. **Fallback heuristic maxes at 4 hours**

### Why This Happens:

#### Scenario 1: FEATURE_GCP_HOURS is "off"
- Location: `.streamlit/secrets.toml` or environment variable
- Effect: Weighted hours calculation never runs
- Fallback: Heuristic in `ui_helpers.py` line 310-323 (max 12h but defaults to 4h)

#### Scenario 2: Facility recommendation + no comparison mode
- Recommendation: `assisted_living` 
- Hours cleared: Lines 480-494 in `logic.py`
- Effect: No hours stored when primary recommendation is facility

#### Scenario 3: Hours calculation runs but data not persisted
- Calculation happens in `ensure_summary_ready()` 
- Storage: Lines 1267-1271 store to `gcp` state
- But: Only if `need_hours=True` (line 1218)
- `need_hours` requires: in_home tier OR `cost.compare_inhome=True`

## Solutions

### Immediate Fix: Enable FEATURE_GCP_HOURS

Add to `.streamlit/secrets.toml`:
```toml
FEATURE_GCP_HOURS = "assist"
```

Or set environment variable:
```bash
export FEATURE_GCP_HOURS=assist
```

Valid values:
- `"off"` - No hours calculation (uses 4h fallback)
- `"shadow"` - Calculates but logs only
- `"assist"` - Full weighted calculation with LLM refinement

### Recommended: Always Calculate Hours for Comparisons

Even when primary recommendation is facility (AL/MC), users should be able to compare with in-home. The hours calculation should run when:
1. Recommendation is in_home, OR
2. User is viewing in-home comparison tab

Currently this logic exists (line 1217-1218) but may not be triggering properly.

### Alternative: Pre-compute Hours for All Cases

Calculate hours during GCP assessment regardless of final recommendation. This ensures hours are always available when user switches to comparison view.

## Testing Steps

1. **Check current flag value:**
   - Look in `.streamlit/secrets.toml` for `FEATURE_GCP_HOURS`
   - Or check environment: `echo $FEATURE_GCP_HOURS`

2. **Enable hours calculation:**
   ```toml
   # .streamlit/secrets.toml
   FEATURE_GCP_HOURS = "assist"
   ```

3. **Restart Streamlit app**

4. **Re-run GCP assessment** with high care needs:
   - Multiple BADLs (especially toileting)
   - Cognitive impairment (moderate/severe)
   - Behavioral issues (wandering, aggression)
   - Fall history (multiple/frequent)
   - Mobility aids (wheelchair/bedbound)

5. **Check logs for:**
   ```
   [HOURS_WEIGHTED] BADL hours: X.Xh from [...]
   [HOURS_WEIGHTED] Cognitive multiplier: X.Xx for moderate
   [HOURS_WEIGHTED] Total weighted hours: XX.Xh
   [GCP_HOURS_PERSIST] user=XXh llm=XXh
   ```

6. **Verify in Cost Planner:**
   - Should see higher hours recommendation
   - Slider should reflect weighted calculation
   - Advisory button should show if significantly different

## Expected Behavior After Fix

**Complex care case:**
- All 6 BADLs + All 8 IADLs: 11.9h base
- × Severe dementia (2.2x): 26.2h
- + Behaviors (wandering, aggression, sundowning): +0.9h = 27.1h  
- × Frequent falls (1.5x): 40.6h
- + Bedbound mobility: +2.0h = **42.6h**
- **Band: "24h"** (≥12h triggers 24h band)

**Moderate care case:**
- 3 BADLs (toileting, bathing, dressing): 3.1h
- × Moderate dementia (1.6x): 5.0h
- + Wandering: +0.3h = 5.3h
- **Band: "4-8h"**

**Light care case:**
- 1 BADL (bathing): 0.5h
- No cognitive issues
- **Band: "<1h"** or **"1-3h"** (depending on IADLs)

## Files to Review

1. `products/gcp_v4/modules/care_recommendation/logic.py`
   - Line 49: `gcp_hours_mode()` - check flag
   - Line 1217: `need_hours` gate
   - Line 1242: `calculate_baseline_hours_weighted()` call ✅ FIXED
   - Line 1267: Hours persistence to GCP state

2. `products/cost_planner_v2/ui_helpers.py`
   - Line 73: `get_llm_hours_high_end_from_gcp()` - reads from GCP state
   - Line 310: Fallback heuristic (4h max without real calculation)

3. `ai/hours_engine.py`
   - Line 29: `calculate_baseline_hours_weighted()` - weighted system ✅ IMPLEMENTED

## Commits

- `01e0436` - Implemented Phase 1 weighted hours system
- `60a31d7` - Fixed GCP logic to call weighted function (not old baseline)

## Next Steps

1. **User Action:** Enable `FEATURE_GCP_HOURS = "assist"`
2. **Re-test:** Run GCP with complex care scenario
3. **Verify:** Check logs for weighted calculation output
4. **Confirm:** See higher hours in Cost Planner (up to 24h possible)
