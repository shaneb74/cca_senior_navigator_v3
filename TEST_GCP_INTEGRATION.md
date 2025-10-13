# GCP Integration Test Plan

## Bug Fix Verification
**Commit**: `b0657be` - Fix: GCP progress calculation and improve integration handling

## What Was Fixed
- **Root Cause**: Results step check was inside else block after StopIteration exception
- **Fix**: Moved check BEFORE try/except in `_update_progress()` (engine.py line 212)
- **Impact**: Progress now correctly set to 100.0 instead of 0.0 when on results page

## Test Procedure

### 1. Restart the App
```bash
v3r
```

### 2. Complete GCP Assessment
- Navigate to **Guided Care Plan** from Concierge hub
- Answer all questions through to the **Results** page
- Verify no errors in terminal

### 3. Verify Fix - Three Integration Points

#### ✅ **GCP Tile Display** (Concierge Hub)
**Expected**: 
- GCP tile shows green checkmark badge: "✓ COMPLETED"
- Recommendation displayed below title: e.g., "✓ In-Home Care"
- Progress bar shows 100%

**Terminal Check**:
```
[CONCIERGE] GCP tile rendering:
  gcp_prog=100.0
  recommendation='In-Home Care' (or appropriate tier)
```

#### ✅ **Cost Planner Gate Opens**
**Expected**:
- Cost Planner tile is **NOT** locked (no 🔒 icon)
- "Begin" button is clickable
- No "Complete Guided Care Plan first" message

**Terminal Check**:
```
[CONCIERGE] Cost Planner gate check:
  gcp_prog >= 100: True
  is_locked: False
```

#### ✅ **MCIP Advances to Cost Planner**
**Expected**:
- Return to Welcome hub
- MCIP "Your Journey" shows Cost Planner as next step
- Cost Planner card has gradient border (active state)
- Clicking Cost Planner opens the product

**Terminal Check**:
```
[MCIP] Next step after GCP: cost_planner
  gcp.progress: 100.0
  recommendation: 'In-Home Care'
```

## Expected Outcomes
All three symptoms should be **RESOLVED**:
1. ✅ GCP tile displays recommendation
2. ✅ Cost Planner is unlocked
3. ✅ MCIP shows Cost Planner as next step

## If Issues Persist
Check terminal output for:
- Any `[DEBUG]` lines (should be none - all removed)
- Error messages in `_ensure_outcomes()`
- Progress values in session state dumps

## Files Modified
- `core/modules/engine.py` - Bug fix + improvements
- `hubs/concierge.py` - Routing + PFMA badges

## Related Documentation
- `GCP_PROGRESS_BUG_FIX.md` - Complete bug analysis
- `test_complete_flow.py` - Validation test (7/7 passing)
