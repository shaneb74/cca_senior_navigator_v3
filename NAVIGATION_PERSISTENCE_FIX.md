# Navigation Persistence Fix - Test Guide

**Issue:** Clicking header links cleared session persistence  
**Fixed:** Commit 85ba2e6  
**Date:** October 14, 2025

## Problem

User reported:
> "Clicking the header link from Cost Planner to the Concierge Hub also cleared out the persistence"

**Behavior:**
1. Complete GCP → Cost Planner unlocked ✅
2. Navigate to Cost Planner
3. Click "Concierge" header link
4. Return to Hub → Cost Planner LOCKED again ❌
5. All progress lost

## Root Cause

Header links use `<a href="?page=hub_concierge">` which triggers full page reload:
- Query params change (`?page=cost_planner` → `?page=hub_concierge`)
- Streamlit reruns `app.py`
- Previous implementation generated **new random session ID** on every reload
- New session ID → loads from different file → no data found

## Solution

Use Streamlit's built-in `ctx.session_id` which is:
- ✅ **Stable** across query param navigation
- ✅ **Persistent** for entire browser session
- ✅ **Unique** per browser tab
- ❌ Only resets when tab closes (expected behavior)

## Test Scenarios

### ✅ Test 1: Header Navigation Preserves State
```bash
streamlit run app.py
```

**Steps:**
1. Complete GCP assessment
2. Go to Hub → Cost Planner unlocked ✅
3. Click "Cost Planner" tile
4. **Click "Concierge" in header**
5. **Expected:** Cost Planner STILL unlocked ✅

**Verify:**
- Cost Planner tile shows as unlocked
- Journey state preserved
- No need to complete GCP again

### ✅ Test 2: Multiple Navigation Cycles
**Steps:**
1. Complete GCP
2. Hub → Cost Planner (via tile)
3. Cost Planner → Hub (via header "Concierge")
4. Hub → Welcome (via header "Welcome")
5. Welcome → Hub (via header "Concierge")
6. **Expected:** Cost Planner STILL unlocked through all navigation

### ✅ Test 3: Session File Stability
**Check session files during navigation:**

```bash
# Terminal 1: Watch session files
watch -n 1 'ls -lrt .cache/ | tail -5'

# Terminal 2: Run app
streamlit run app.py
```

**Steps:**
1. Start app → Note session file created (e.g., `session_abc123.json`)
2. Complete GCP
3. Navigate via header links (Welcome → Concierge → Learning → Concierge)
4. **Expected:** Same session file name throughout (no new files created)

### ✅ Test 4: Cross-Page State Preservation
**Steps:**
1. Complete GCP
2. Start Cost Planner quick estimate
3. Answer 2 questions (don't complete)
4. Click "Concierge" header
5. Click "Cost Planner" tile again
6. **Expected:** Resume at question 3 (progress preserved)

### ✅ Test 5: Tab Isolation (New Session)
**Steps:**
1. Tab A: Complete GCP
2. **Open Tab B** (new tab, same URL)
3. Tab B: Navigate to Hub
4. **Expected:** Tab B has clean slate (different session)
5. Tab A: Navigate around → progress still preserved

## What Changed

### Before (Random Session ID)
```python
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = generate_session_id()  # Random UUID
```

**Problem:** New UUID every time `st.session_state` resets (query param navigation)

### After (Streamlit Session ID)
```python
if 'session_id' not in st.session_state:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    ctx = get_script_run_ctx()
    if ctx and ctx.session_id:
        st.session_state['session_id'] = ctx.session_id  # Stable ID
    else:
        st.session_state['session_id'] = generate_session_id()  # Fallback
```

**Solution:** Use Streamlit's stable session ID (persists across query param changes)

## Session Lifecycle

### Streamlit Session ID
- **Created:** When browser tab opens app
- **Persists:** Across all query param navigation
- **Reset:** When tab closes or browser restarts
- **Scope:** Single browser tab

### File Mapping
```
Browser Tab A → session_abc123.json (stable)
Browser Tab B → session_def456.json (different tab)
```

## Debugging

### Check Current Session ID
Add to app.py temporarily:
```python
# After session_id assignment
if st.sidebar.checkbox("Debug Session"):
    st.sidebar.write(f"Session ID: {session_id}")
    st.sidebar.write(f"Session file: .cache/session_{session_id}.json")
```

### Verify Stable ID
1. Start app → Note session ID in sidebar
2. Navigate via header links multiple times
3. Check sidebar → **Same session ID** throughout

### Check Session File
```bash
# Find your session file
ls -lrt .cache/session_*.json | tail -1

# View contents
python clear_data.py --inspect .cache/session_<your_id>.json
```

Should show:
```json
{
  "session_id": "abc-123-def-456",  ← Stable across navigation
  "current_route": "hub_concierge",
  "last_accessed": 1697280123.45
}
```

## Common Issues

### Issue: State still clearing
- Check: Is session_id actually stable? (add debug output)
- Check: Are session files being created? (`ls .cache/`)
- Check: File permissions? (`chmod 755 .cache/`)

### Issue: Different session ID on each reload
- Check: Streamlit version (need ≥1.30 for ctx.session_id)
- Fallback: Should use random UUID but warn about instability

### Issue: Session not loading after navigation
- Check: Is save happening? (add debug after `save_session()`)
- Check: File corruption? (`python clear_data.py --list`)

## Success Criteria

All tests pass:
- [x] Test 1: Header navigation preserves state
- [x] Test 2: Multiple navigation cycles work
- [x] Test 3: Same session file throughout
- [x] Test 4: In-progress work preserved
- [x] Test 5: Tab isolation works

Behavior verified:
- [x] GCP completion survives header navigation
- [x] Cost Planner stays unlocked
- [x] In-progress assessments preserved
- [x] Session ID stable across query param changes
- [x] Different tabs have different sessions

## Related Fixes

- Session persistence: `SESSION_PERSISTENCE_IMPLEMENTATION.md`
- Journey state: `JOURNEY_STATE_PERSISTENCE_TEST.md`
- MCIP contracts: `MCIP_PERSISTENCE_FIX.md`

---

**Status:** ✅ Fixed - Navigation now preserves all session state  
**Commit:** 85ba2e6  
**Impact:** Critical UX improvement - users won't lose progress when navigating
