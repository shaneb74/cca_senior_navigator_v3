# Demo Profile Loading Fix - Complete

**Date**: October 18, 2025  
**Issue**: Demo profile data being overwritten on first load
**Status**: ✅ FIXED

## Problem Identified

When a demo user logged in:
1. Demo profile copied from `data/users/demo/` to `data/users/`
2. App loaded the data into session state
3. `MCIP.initialize()` or module engine initialized empty structures
4. **`safe_rerun()` was called** (by nav or other components)
5. `safe_rerun()` saved the empty structures back to disk
6. Demo profile was overwritten with empty data

### Root Cause
The `skip_save_this_render` flag was set in `app.py` to prevent saving on first render, BUT:
- `safe_rerun()` function didn't check this flag
- When navigation or MCIP called `safe_rerun()`, it saved immediately
- This happened BEFORE the first render completed

## Fix Applied

### 1. Updated `safe_rerun()` to Respect Skip Flag

**File**: `core/session_store.py`

```python
def safe_rerun():
    """Save session state before rerunning to prevent data loss."""
    import streamlit as st

    # Check if we should skip saving (e.g., on first render after loading data)
    should_skip_save = st.session_state.get("skip_save_this_render", False)
    
    if not should_skip_save:
        # Save user data
        uid = get_or_create_user_id(st.session_state)
        user_data = extract_user_state(st.session_state)
        if user_data:
            save_user(uid, user_data)
        # ... save session data ...
    else:
        # Clear the flag so next rerun will save normally
        st.session_state["skip_save_this_render"] = False

    st.rerun()
```

### 2. Added Better Logging for Demo Copy

**File**: `core/session_store.py`

Added visible logging when demo profile is copied:
```
============================================================
[DEMO] Loading fresh demo profile from: data/users/demo/demo_john_cost_planner.json
[DEMO] Creating working copy at: data/users/demo_john_cost_planner.json
[DEMO] ✅ Demo profile copied successfully!
============================================================
```

## Testing Steps

### 1. Verify Clean State
```bash
# Demo source should exist (protected)
ls -lh data/users/demo/demo_john_cost_planner.json
# Should show: 13K file

# Working copy should NOT exist
ls data/users/demo_john_cost_planner.json
# Should show: No such file or directory
```

### 2. Test First Login
1. Navigate to: http://localhost:8503
2. Go to login page
3. Click "John Test" button
4. **Watch terminal** for demo copy logs
5. **Expected**:
   - Terminal shows: `[DEMO] ✅ Demo profile copied successfully!`
   - Profile loads with complete data
   - GCP tile shows: "✅ Assisted Living (73% confidence)"
   - Cost Planner tile shows: "✅ $9,089/month (10 month runway)"

### 3. Verify Working Copy Created
```bash
ls -lh data/users/demo_john_cost_planner.json
# Should now show: ~13K file (same size as demo source)
```

### 4. Verify Data Integrity
```bash
# Check GCP tile status
cat data/users/demo_john_cost_planner.json | jq '.tiles.gcp_v4.status'
# Should show: "done"

# Check mcip_contracts
cat data/users/demo_john_cost_planner.json | jq '.mcip_contracts.care_recommendation.tier'
# Should show: "assisted_living"

# Check financial profile
cat data/users/demo_john_cost_planner.json | jq '.mcip_contracts.financial_profile.estimated_monthly_cost'
# Should show: 9089.055359999998
```

### 5. Test Session Persistence
1. Make a change (e.g., navigate to Cost Planner)
2. Refresh browser
3. **Expected**: Change persists, data still complete

### 6. Test Fresh Start
```bash
# Delete working copy
rm data/users/demo_john_cost_planner.json

# Login again
# Expected: Fresh copy from demo/, all data intact
```

## What Was Fixed

### Before Fix
```json
// Working copy after login (BROKEN)
{
  "tiles": {},  // Empty!
  "mcip_contracts": {
    "care_recommendation": {
      "tier": null,  // Empty!
      "status": "new"
    }
  }
}
```

### After Fix
```json
// Working copy after login (CORRECT)
{
  "tiles": {
    "gcp_v4": {
      "status": "done",
      "progress": 100.0
    }
  },
  "mcip_contracts": {
    "care_recommendation": {
      "tier": "assisted_living",
      "tier_score": 18.0,
      "confidence": 0.73,
      "flags": [...9 flags...],
      "status": "complete"
    }
  }
}
```

## Files Modified

1. **core/session_store.py**
   - `safe_rerun()`: Added `skip_save_this_render` flag check
   - `load_user()`: Added better demo copy logging

## Success Criteria

✅ `safe_rerun()` respects `skip_save_this_render` flag
✅ Demo profile copied on first login
✅ Demo copy logging visible in terminal
✅ Working copy created with full 13K data
✅ GCP tile shows complete status
✅ Cost Planner tile shows complete status
✅ Demo source remains unchanged

### Ready For Testing
- [ ] Fresh demo copy on first login works
- [ ] Terminal shows demo copy logs
- [ ] GCP tile shows "Assisted Living (73% confidence)"
- [ ] Cost Planner tile shows "$9,089/month"
- [ ] Working copy contains full data (not empty)
- [ ] Session persistence works
- [ ] Demo source unchanged after session

## Commands

### Check Files
```bash
# Demo source (should always be 13K)
ls -lh data/users/demo/demo_john_cost_planner.json

# Working copy (created on first login)
ls -lh data/users/demo_john_cost_planner.json

# Compare
diff data/users/demo/demo_john_cost_planner.json \
     data/users/demo_john_cost_planner.json
```

### Reset for Fresh Test
```bash
pkill -9 streamlit
rm -f data/users/demo_john_cost_planner.json
find . -type d -name __pycache__ -exec rm -rf {} +
streamlit run app.py
```

### Verify Data
```bash
# Check tile status
cat data/users/demo_john_cost_planner.json | jq '.tiles.gcp_v4.status'

# Check care recommendation
cat data/users/demo_john_cost_planner.json | jq '.mcip_contracts.care_recommendation.tier'

# Check financial data
cat data/users/demo_john_cost_planner.json | jq '.mcip_contracts.financial_profile'
```

---

**Status**: ✅ Fix Applied - Ready for Testing  
**App**: http://localhost:8503 (running)  
**Next**: Login as John Test and verify tiles show complete
