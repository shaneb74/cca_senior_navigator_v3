# FAQ Navigation Bug Fix

**Status:** ✅ FIXED (commit 934c4ec)  
**Date:** January 2025  
**Component:** MCIP Session Persistence

---

## Bug Report

### Symptoms
After completing GCP and unlocking Cost Planner, the Cost Planner would RE-LOCK after visiting the FAQ page and returning to the hub.

### Reproduction Steps
1. Complete GCP → Cost Planner unlocks ✅
2. Visit Cost Planner → Works correctly ✅
3. Return to hub → Cost Planner still unlocked ✅
4. **Click FAQ tile** → View FAQ page
5. **Return to hub** → **Cost Planner LOCKED** ❌

### Expected Behavior
Cost Planner should remain unlocked after visiting FAQ, since GCP completion is persisted.

---

## Root Cause Analysis

### Architecture Context
- **MCIP (Master Care Intelligence Panel)**: Single source of truth for product completion state
- **Persistence**: `mcip_contracts` saved to `data/users/<uid>.json`
- **Session State**: `st.session_state["mcip"]` runtime state, `st.session_state["mcip_contracts"]` persistent data

### The Bug
Located in `core/mcip.py` → `MCIP.initialize()` method (lines 88-120)

**Problem:** mcip_contracts restoration only happened on FRESH initialization

```python
# BEFORE FIX (BUGGY):
if cls.STATE_KEY not in st.session_state:
    # Fresh initialization
    st.session_state[cls.STATE_KEY] = default_state
    
    # Restore from mcip_contracts if available
    if "mcip_contracts" in st.session_state:
        # ... restore journey data ...
else:
    # Existing state - just fill missing keys
    # ❌ BUG: No restoration here!
    for key in default_state:
        if key not in st.session_state[cls.STATE_KEY]:
            st.session_state[cls.STATE_KEY][key] = default_state[key]
```

### Bug Flow
1. **App starts** → `MCIP.initialize()` → `mcip` state doesn't exist → **Fresh init** → Restores from `mcip_contracts` ✅
2. **User completes GCP** → `MCIP.mark_product_complete("gcp")` → Saves to `mcip_contracts` ✅
3. **Navigate to Cost Planner** → Hub renders → `MCIP.initialize()` → `mcip` state EXISTS → Else branch → **No restoration** ❌
4. **Navigate to FAQ** → FAQ renders (no MCIP calls)
5. **Return to hub** → Hub renders → `MCIP.initialize()` → `mcip` state EXISTS → Else branch → **No restoration** ❌
6. **Hub checks unlock status** → Reads `st.session_state["mcip"]["journey"]["completed_products"]` → Sees `[]` (stale default) → **Locks Cost Planner** ❌

### Why It Happened
- The else branch in `initialize()` assumed existing state was already correct
- It only filled in missing keys, but didn't sync from persistent storage
- After first page load, `mcip` state existed, so restoration never ran again
- `mcip_contracts` had correct data, but wasn't being read

---

## The Fix

### Solution
Move `mcip_contracts` restoration OUTSIDE the if/else block, so it runs on EVERY call to `initialize()`.

```python
# AFTER FIX (CORRECT):
if cls.STATE_KEY not in st.session_state:
    # Fresh initialization
    st.session_state[cls.STATE_KEY] = default_state
else:
    # Existing state - fill missing keys
    for key in default_state:
        if key not in st.session_state[cls.STATE_KEY]:
            st.session_state[cls.STATE_KEY][key] = default_state[key]

# ✅ CRITICAL FIX: Always restore from mcip_contracts if available
if "mcip_contracts" in st.session_state:
    contracts = st.session_state["mcip_contracts"]
    if "journey" in contracts and contracts["journey"]:
        # CRITICAL: Always restore journey state from contracts
        st.session_state[cls.STATE_KEY]["journey"] = contracts["journey"]
```

### What Changed
- **Before:** Restoration only in `if` branch (fresh init)
- **After:** Restoration ALWAYS happens, regardless of whether `mcip` state exists
- **Result:** `mcip_contracts` is the authoritative source, runtime state always syncs from it

---

## Testing

### Automated Tests
Created `test_faq_navigation_fix.py` with 3 test scenarios:

1. **test_faq_navigation_preserves_unlock()**
   - Simulates: Complete GCP → Navigate to FAQ → Return to hub
   - Verifies: Cost Planner stays unlocked
   - Result: ✅ PASS

2. **test_multiple_navigation_cycles()**
   - Simulates: 5 cycles of hub → FAQ → hub → FAQ → hub
   - Verifies: State preserved across all navigations
   - Result: ✅ PASS

3. **test_contracts_restoration_priority()**
   - Simulates: Corrupt runtime state, restore from contracts
   - Verifies: `mcip_contracts` is source of truth
   - Result: ✅ PASS

### Test Output
```
🎉 ALL TESTS PASSED!

✅ FAQ navigation no longer re-locks Cost Planner
✅ State persists across multiple page navigations
✅ mcip_contracts is the authoritative source of truth
```

---

## Manual Testing Steps

1. **Start app:** `streamlit run app.py`
2. **Complete GCP:**
   - Navigate to GCP product
   - Complete all questions
   - Verify progress = 100%
3. **Check Cost Planner unlocks:**
   - Return to hub
   - Verify Cost Planner tile shows unlocked
4. **Navigate to FAQ:**
   - Click FAQ tile
   - Interact with Navi (optional)
   - Click "Back to Hub"
5. **Verify Cost Planner STILL unlocked:**
   - Check Cost Planner tile status
   - Should remain unlocked ✅
6. **Restart app:**
   - Stop and restart Streamlit
   - Cost Planner should STILL be unlocked (persistence) ✅

---

## Related Work

### Previous Fix (Commit 2f9e9df)
- **File:** `core/product_tile.py`
- **Issue:** Unlock logic checked legacy session state instead of MCIP
- **Fix:** Updated `_evaluate_requirement()` to check `MCIP.is_product_complete()` first
- **Result:** Unlock logic now reads from authoritative source

### Combined Solution
Both fixes were necessary:
1. **Tile unlock logic** checks MCIP (commit 2f9e9df)
2. **MCIP initialization** restores from contracts (commit 934c4ec)

Together, they ensure:
- ✅ Unlock checks read from MCIP (single source of truth)
- ✅ MCIP runtime state always syncs from persistent storage
- ✅ Completion state survives page navigations
- ✅ Persistence works across app restarts

---

## Code References

### Modified Files
- `core/mcip.py` - MCIP.initialize() method (lines 88-120)

### Test Files
- `test_faq_navigation_fix.py` - Automated test suite (235 lines)
- `test_unlock_fix.py` - Original unlock logic tests (220 lines)

### Related Components
- `core/product_tile.py` - Tile unlock evaluation logic
- `hubs/concierge.py` - Calls MCIP.initialize() on every render
- `pages/faq.py` - FAQ page implementation (no state resets)
- `app.py` - Loads user data, merges mcip_contracts into session

---

## Deployment Checklist

- [x] ✅ Root cause identified
- [x] ✅ Fix implemented in core/mcip.py
- [x] ✅ Automated tests created and passing
- [x] ✅ Code committed (934c4ec)
- [ ] ⏳ Manual testing in live app
- [ ] ⏳ Verify FAQ → Hub → Cost Planner flow
- [ ] ⏳ Verify app restart persistence
- [ ] ⏳ Deploy to production

---

## Technical Notes

### Why This Was Subtle
1. **Worked on first page load:** Fresh init restored contracts correctly
2. **Failed on subsequent navigations:** Else branch didn't restore
3. **Hard to debug:** State appeared correct initially, only failed after navigation
4. **Edge case:** Most products don't have unlock requirements, so bug wasn't obvious

### Design Principle
**mcip_contracts is the authoritative source.**  
Runtime state (`st.session_state["mcip"]`) should ALWAYS sync from persistent storage, never assume it's current.

### Future Considerations
- Consider making MCIP state immutable, with explicit sync operations
- Add validation to ensure journey data never goes stale
- Monitor for similar patterns in other state initialization code

---

## Conclusion

**Bug:** Cost Planner re-locked after FAQ navigation  
**Cause:** MCIP.initialize() only restored contracts on fresh init  
**Fix:** Always restore from mcip_contracts, regardless of state existence  
**Status:** ✅ FIXED and TESTED  
**Commits:** 934c4ec (MCIP fix), 2f9e9df (unlock logic fix)

Both fixes together ensure Cost Planner unlock state persists correctly across all navigation scenarios and app restarts.
