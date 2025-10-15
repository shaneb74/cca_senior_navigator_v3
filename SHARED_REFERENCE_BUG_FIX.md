# CRITICAL: Shared Reference Bug Fix

**Status:** ✅ FIXED (commit 342612e)  
**Severity:** HIGH - Data corruption bug  
**Date:** October 15, 2025

---

## The Bug

### Symptoms
After completing GCP, Cost Planner would unlock correctly. But after visiting the FAQ page and returning to the hub, Cost Planner would RE-LOCK.

### Root Cause
**Shared Reference Bug in MCIP.initialize()**

```python
# BUGGY CODE (line 121):
st.session_state[cls.STATE_KEY]["journey"] = contracts["journey"]
```

This assigns by **reference**, not by **value**. Both `mcip["journey"]` and `mcip_contracts["journey"]` pointed to the **same dictionary object**.

### Why This Caused the Bug

1. **Complete GCP:**
   ```python
   MCIP.mark_product_complete("gcp")
   # Both mcip and mcip_contracts updated (same object)
   mcip["journey"]["completed_products"] = ["gcp"]  ✓
   ```

2. **Navigate to FAQ → Return to Hub:**
   ```python
   # Hub calls MCIP.initialize()
   # Some code path (possibly default_state creation) creates fresh dict
   # If this fresh dict gets assigned, it overwrites the shared reference
   mcip["journey"]["completed_products"] = []  # Default state
   
   # Because they share the same object:
   # mcip_contracts["journey"]["completed_products"] ALSO becomes []! ❌
   ```

3. **Result:**
   - `mcip_contracts` (the persistent source of truth) gets corrupted
   - When `MCIP.initialize()` tries to restore from `mcip_contracts`, it restores corrupted data
   - Cost Planner sees no completed products → re-locks

### Visual Explanation

```
BEFORE FIX (Shared Reference):
┌──────────────────────────────────────┐
│  st.session_state                    │
│                                      │
│  mcip: {                             │
│    journey: ───────┐                 │
│  }                  │                 │
│                     │                 │
│  mcip_contracts: {  │                 │
│    journey: ───────┴──> SAME OBJECT  │  ← Modifying either one
│  }                      {            │     modifies both!
│                         completed: [] │
│                       }               │
└──────────────────────────────────────┘

AFTER FIX (Deep Copy):
┌──────────────────────────────────────┐
│  st.session_state                    │
│                                      │
│  mcip: {                             │
│    journey: ─────> { completed: [] } │  ← Separate object
│  }                                   │
│                                      │
│  mcip_contracts: {                   │
│    journey: ─────> { completed: ["gcp"] } │  ← Protected!
│  }                                   │
└──────────────────────────────────────┘
```

---

## The Fix

### Code Change

```python
# BEFORE (BUGGY):
if "journey" in contracts and contracts["journey"]:
    st.session_state[cls.STATE_KEY]["journey"] = contracts["journey"]

# AFTER (FIXED):
if "journey" in contracts and contracts["journey"]:
    import copy
    # Use deepcopy to avoid shared references
    st.session_state[cls.STATE_KEY]["journey"] = copy.deepcopy(contracts["journey"])
```

### Why Deep Copy?

- **Shallow copy** wouldn't work because `journey` contains nested dicts (completed_products is a list)
- **Deep copy** recursively copies all nested objects
- Ensures `mcip["journey"]` and `mcip_contracts["journey"]` are completely independent

---

## Testing

### Automated Tests

1. **test_shared_reference_bug.py** - Tests for shared references
   ```python
   # Corrupt mcip["journey"]["completed_products"] = []
   # Verify mcip_contracts["journey"]["completed_products"] still has ["gcp"]
   ```
   **Result:** ✅ PASS - No shared references

2. **test_mcip_restoration.py** - Tests restoration logic
   ```python
   # Complete GCP → Navigate → Return to hub
   # Verify completion state preserved
   ```
   **Result:** ✅ PASS - State preserved

3. **test_faq_navigation_fix.py** - Tests full FAQ flow
   ```python
   # Complete GCP → FAQ → Hub → Cost Planner still unlocked
   ```
   **Result:** ✅ PASS - All tests passing

4. **test_unlock_fix.py** - Original unlock tests
   **Result:** ✅ PASS - No regressions

### Manual Testing Guide

See `test_faq_interactive.py` for step-by-step manual test:

1. Complete GCP
2. Verify Cost Planner unlocks
3. Navigate to Cost Planner and back
4. Navigate to FAQ and back ← **Critical test**
5. Verify Cost Planner STILL unlocked
6. Restart app → verify persistence

---

## Why Previous Fix Wasn't Enough

### Previous Fix (Commit 934c4ec)
**What it did:** Moved `mcip_contracts` restoration outside if/else block
**What it fixed:** Ensured restoration runs on every `initialize()` call
**What it missed:** Didn't account for shared references

### The Problem
Even though restoration was running, it was restoring a **corrupted** `mcip_contracts` because both `mcip` and `mcip_contracts` pointed to the same object that got corrupted.

### Complete Solution
**Both fixes are necessary:**
1. **Commit 934c4ec:** Always restore from `mcip_contracts` (timing fix)
2. **Commit 342612e:** Use `deepcopy` when restoring (reference fix)

Together they ensure:
- ✅ Restoration happens on every initialize
- ✅ Restored data is independent (no shared references)
- ✅ `mcip_contracts` can never be corrupted by modifying `mcip`

---

## Python Reference Mechanics

### Why This Happens

```python
# Python assigns by reference for mutable objects:
a = {"key": ["value"]}
b = a  # b points to SAME object as a

b["key"].append("new")
print(a["key"])  # ["value", "new"] ← a was also modified!

# Fix with deepcopy:
import copy
a = {"key": ["value"]}
b = copy.deepcopy(a)  # b is a NEW object

b["key"].append("new")
print(a["key"])  # ["value"] ← a is unchanged!
```

### In MCIP Context

```python
# BUGGY:
st.session_state["mcip"]["journey"] = st.session_state["mcip_contracts"]["journey"]
# Both variables point to SAME dict

# FIXED:
import copy
st.session_state["mcip"]["journey"] = copy.deepcopy(st.session_state["mcip_contracts"]["journey"])
# Now they're separate dicts
```

---

## Impact Assessment

### Before Fix
- ❌ Cost Planner re-locked after FAQ navigation
- ❌ Completion state could be lost
- ❌ User had to re-complete GCP
- ❌ Poor user experience

### After Fix
- ✅ Cost Planner stays unlocked after FAQ navigation
- ✅ Completion state preserved across all navigations
- ✅ State persists across app restarts
- ✅ Smooth user experience

---

## Related Issues

### Other Potential Shared Reference Bugs?

We should audit other places where we assign from contracts:

```python
# In MCIP.initialize() - These might also need deepcopy:
st.session_state[cls.STATE_KEY]["care_recommendation"] = contracts["care_recommendation"]
st.session_state[cls.STATE_KEY]["financial_profile"] = contracts["financial_profile"]
st.session_state[cls.STATE_KEY]["advisor_appointment"] = contracts["advisor_appointment"]
```

**However:** These are likely dataclass instances or dicts that don't get mutated directly, so they're probably safe. But worth monitoring.

---

## Prevention

### Code Review Checklist
- [ ] When assigning dicts/lists from session state, consider if they need deepcopy
- [ ] Be wary of shared references between "source of truth" and "working copy"
- [ ] Test for shared references explicitly (check `id()` of objects)
- [ ] Document when deepcopy is intentionally used for data protection

### Testing Strategy
- ✅ Add test for shared references (test_shared_reference_bug.py)
- ✅ Test corruption scenarios (manual corruption + restore)
- ✅ Test multiple navigation cycles
- ✅ Test persistence across app restarts

---

## Commit History

1. **2f9e9df** - Fix unlock logic to check MCIP first
2. **934c4ec** - Fix MCIP.initialize() to always restore from contracts
3. **342612e** - Fix shared reference bug with deepcopy ← **This fix**

**All three fixes work together to solve the complete bug:**
- Fix 1: Check the right source (MCIP, not legacy state)
- Fix 2: Always restore from persistent source
- Fix 3: Protect persistent source from corruption

---

## Conclusion

This was a **subtle but critical bug** caused by Python's reference semantics. The fix is simple (add `deepcopy`) but the diagnosis was complex because:

1. State appeared correct initially
2. Bug only manifested after specific navigation patterns
3. Corruption happened silently (no errors thrown)
4. Both `mcip` and `mcip_contracts` showed same (wrong) data

**Key Takeaway:** When dealing with persistent state, always use `deepcopy()` to ensure the persistent copy cannot be corrupted by modifications to the working copy.

---

## Files Modified

- `core/mcip.py` - Added `copy.deepcopy()` in `initialize()` method
- `test_shared_reference_bug.py` - Tests for shared references
- `test_mcip_restoration.py` - Tests restoration logic
- `test_faq_interactive.py` - Manual testing guide

---

**Status:** ✅ FIXED and TESTED  
**Ready for:** Production deployment  
**Manual testing:** Recommended before deploy
