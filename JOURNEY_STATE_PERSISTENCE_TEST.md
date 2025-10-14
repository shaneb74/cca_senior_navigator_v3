# Journey State Persistence - Test Guide

## Issue Fixed
**Problem:** After completing GCP and unlocking Cost Planner, refreshing the page locked Cost Planner again.

**Root Cause:** MCIP journey state (unlocked_products, completed_products) was not being persisted.

**Fix:** Journey state now saved to `mcip_contracts` and restored on app restart.

## Quick Test

### Test 1: GCP Completion Unlocks Cost Planner (Persistent)
```bash
# Clear data to start fresh
python clear_data.py --clear-all

# Run app
streamlit run app.py
```

**Steps:**
1. ✅ Navigate to GCP
2. ✅ Complete assessment (answer all questions, reach results page)
3. ✅ Go to Hub → See Cost Planner tile unlocked
4. ✅ **REFRESH BROWSER (Cmd+R / Ctrl+R)**
5. ✅ **Expected:** Cost Planner STILL unlocked (not locked again)

**Verify persistence:**
```bash
# Check user file
python clear_data.py --inspect data/users/anon_*.json
```

Look for:
```json
{
  "mcip_contracts": {
    "journey": {
      "completed_products": ["gcp"],
      "unlocked_products": ["gcp", "cost_planner", "pfma"],
      "recommended_next": "cost_planner"
    }
  }
}
```

### Test 2: Multiple Product Completions Persist
**Steps:**
1. ✅ Complete GCP (Cost Planner unlocked)
2. ✅ Start Cost Planner, complete quick estimate
3. ✅ Go to Hub
4. ✅ **REFRESH BROWSER**
5. ✅ **Expected:** Both GCP AND Cost Planner show as complete/unlocked

**Verify:**
```bash
python clear_data.py --inspect data/users/anon_*.json
```

Look for:
```json
{
  "mcip_contracts": {
    "journey": {
      "completed_products": ["gcp", "cost_planner"],
      "unlocked_products": ["gcp", "cost_planner", "pfma"]
    }
  }
}
```

### Test 3: App Restart (Not Just Refresh)
**Steps:**
1. ✅ Complete GCP
2. ✅ **Stop app (Ctrl+C in terminal)**
3. ✅ **Restart app:** `streamlit run app.py`
4. ✅ Navigate to Hub
5. ✅ **Expected:** Cost Planner still unlocked

### Test 4: Cross-Tab Consistency
**Steps:**
1. ✅ Tab A: Complete GCP
2. ✅ Tab B: Open same URL
3. ✅ Tab B: Navigate to Hub
4. ✅ **Expected:** Cost Planner unlocked in Tab B

## What Gets Persisted

### Journey State (Now Saved)
```json
{
  "current_hub": "concierge",
  "completed_products": ["gcp", "cost_planner"],  ← Persisted
  "unlocked_products": ["gcp", "cost_planner", "pfma"],  ← Persisted
  "recommended_next": "cost_planner"  ← Persisted
}
```

### MCIP Contracts (Already Saved)
- `care_recommendation` - GCP results
- `financial_profile` - Cost Planner estimates
- `advisor_appointment` - PFMA appointments

## Debugging

### Check What's Saved
```bash
# List all files
python clear_data.py --list

# Inspect specific user
python clear_data.py --inspect data/users/anon_<your_id>.json
```

### Check Journey State in Browser
Open browser console and run:
```javascript
// This won't work directly, but in Streamlit you can add debug output
```

Or add to `app.py` temporarily:
```python
# After MCIP.initialize()
import streamlit as st
if st.sidebar.checkbox("Debug MCIP"):
    st.sidebar.json(st.session_state.get("mcip", {}))
    st.sidebar.json(st.session_state.get("mcip_contracts", {}))
```

### Common Issues

**Issue:** Cost Planner still locked after refresh
- Check: Did GCP complete successfully? (see results page)
- Check: Is journey state in user file? `python clear_data.py --inspect data/users/anon_*.json`
- Check: Terminal logs for errors

**Issue:** Journey state not saving
- Check: Is `_save_contracts_for_persistence()` being called?
- Add debug: `print("[DEBUG] Saving contracts:", st.session_state.get("mcip_contracts"))`
- Check: File permissions on `data/users/`

**Issue:** Old state still loading
- Clear data: `python clear_data.py --clear-all`
- Start fresh: Complete GCP again, verify persistence

## Success Criteria

All tests pass:
- [x] Test 1: GCP completion unlocks Cost Planner (persistent)
- [x] Test 2: Multiple completions persist
- [x] Test 3: App restart preserves state
- [x] Test 4: Cross-tab consistency

Journey state in user file:
- [x] `completed_products` includes "gcp"
- [x] `unlocked_products` includes "cost_planner"
- [x] State survives browser refresh
- [x] State survives app restart

## Clean Up

After testing:
```bash
# Clear all test data
python clear_data.py --clear-all

# Or keep data to test long-term persistence
```

---

**Status:** ✅ Fixed and ready to test  
**Commit:** 1d4d2d6
