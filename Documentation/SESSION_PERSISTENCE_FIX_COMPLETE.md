# Session Persistence Fix - Complete ✅

**Date**: October 20, 2025  
**Branch**: `dev` (merged from `feature/visual-restyling`)  
**Status**: ✅ RESOLVED

---

## Problem Statement

When navigating between hubs (e.g., Concierge → Waiting Room → Concierge), session state was being lost:
- PFMA completion would disappear
- Advisor appointments would be forgotten
- In-session progress would reset to demo profile defaults
- Links would open in new browser tabs (unexpected behavior)

---

## Root Causes Identified

### 1. Demo Profile Reloading (CRITICAL)
**Location**: `core/session_store.py:417-422`

**Bug**: Demo profiles were being reloaded from `data/users/demo/` on EVERY page load, overwriting all session progress.

```python
# BEFORE (buggy):
# Always refresh working copy from demo source if it exists
if demo_path.exists():
    shutil.copy2(demo_path, path)  # ❌ Overwrites progress every time!
```

**Impact**: 
- User completes PFMA in Concierge
- Navigates to Waiting Room → Demo profile reloaded → Progress lost
- Navigates back to Concierge → PFMA shows as incomplete

**Fix**: Only copy demo profile on first load if working copy doesn't exist.

```python
# AFTER (fixed):
# Only copy demo profile if working copy doesn't exist yet
if demo_path.exists() and not path.exists():
    shutil.copy2(demo_path, path)  # ✅ Only on first load!
```

---

### 2. Skip Save Flag
**Location**: `app.py:159-162, 231-240`

**Bug**: When session data was loaded, `skip_save_this_render = True` was set to prevent overwriting freshly loaded data. However, this meant NO SAVE occurred after the first render, so subsequent navigation would load stale data.

**Fix**: Removed `skip_save_this_render` logic entirely. Now state is ALWAYS saved after every render, ensuring latest progress is persisted.

```python
# BEFORE (buggy):
if should_skip_save:
    st.session_state["skip_save_this_render"] = False
else:
    save_session(...)
    save_user(...)

# AFTER (fixed):
# Always save state after render
save_session(...)
save_user(...)
```

---

### 3. Links Opening New Tabs
**Location**: `ui/header_simple.py:64, 69, 208`

**Bug**: Header navigation links didn't have `target="_self"` attribute, causing some browsers to open links in new tabs.

**Fix**: Added `target="_self"` to all navigation links (nav items, login, logo).

```python
# BEFORE:
f'<a href="{href_with_uid}" class="nav-link">{label}</a>'

# AFTER:
f'<a href="{href_with_uid}" class="nav-link" target="_self">{label}</a>'
```

---

## Technical Details

### Session Persistence Flow (Now Working)

1. **User completes PFMA in Concierge Hub**
   - PFMA completion stored in `st.session_state["mcip"]["journey"]["completed_products"]`
   - `MCIP.mark_product_complete("pfma_v3")` called
   - `_save_contracts_for_persistence()` copies to `st.session_state["mcip_contracts"]`
   - End of render: `save_user(uid, user_state)` persists to disk ✅

2. **User navigates to Waiting Room**
   - href link → Browser navigates → Streamlit restarts app.py
   - `load_user(uid)` loads from `data/users/demo_mary_memory_care.json`
   - **CRITICAL**: Does NOT reload from demo source (working copy exists) ✅
   - `merge_into_state()` restores `mcip_contracts` to session state
   - `MCIP.initialize()` rebuilds `mcip` structure from `mcip_contracts` ✅
   - PFMA completion is preserved! ✅
   - End of render: State saved again (no skip) ✅

3. **User navigates back to Concierge**
   - Same load process
   - PFMA completion still in `mcip_contracts.journey.completed_products` ✅
   - Concierge Hub renders PFMA tile as complete ✅

### What Gets Persisted

**In `mcip_contracts` (saved to user file)**:
- `care_recommendation` (GCP data)
- `financial_profile` (Cost Planner data)
- `advisor_appointment` (PFMA booking details)
- `journey.completed_products` (["gcp", "cost_planner", "pfma_v3"])
- `journey.unlocked_products`
- `journey.recommended_next`
- `waiting_room.advisor_prep_status`
- `waiting_room.trivia_status`

**NOT persisted** (reconstructed on load):
- `mcip.events` (ephemeral event log)
- Internal MCIP state structure (rebuilt by `MCIP.initialize()`)

---

## Files Changed

1. **`core/session_store.py`**
   - Fixed demo profile loading logic (lines 417-422)
   - Only copies demo source on first load

2. **`app.py`**
   - Removed `skip_save_this_render` logic (lines 159-162, 231-240)
   - Now always saves state after render

3. **`ui/header_simple.py`**
   - Added `target="_self"` to all navigation links (lines 64, 69, 208)
   - Ensures same-tab navigation

---

## Testing Results

### ✅ All Tests Passing

**Test Case 1: PFMA Persistence**
1. Load Mary: `?uid=demo_mary_memory_care`
2. Navigate to Concierge Hub
3. Complete PFMA (Book Appointment)
4. Navigate to Waiting Room
5. Navigate back to Concierge
6. **RESULT**: ✅ PFMA shows as complete with appointment details

**Test Case 2: GCP/Cost Planner Persistence**
1. Load Mary (already has GCP/CP complete)
2. Navigate between hubs
3. **RESULT**: ✅ GCP and Cost Planner remain complete

**Test Case 3: Demo Source Protection**
1. Complete progress as Mary
2. Check `data/users/demo/demo_mary_memory_care.json`
3. **RESULT**: ✅ Demo source unchanged
4. Check `data/users/demo_mary_memory_care.json`
5. **RESULT**: ✅ Working copy has updated progress

**Test Case 4: Navigation Behavior**
1. Click header navigation links
2. **RESULT**: ✅ Navigates in same tab (not new tabs)

---

## Commits Included

1. **6acbdf1**: `fix: Demo profiles now persist session progress instead of reloading from source on every navigation`
   - The critical fix for demo profile reloading

2. **ef16e73**: `fix: Always save state after render to ensure href navigation preserves session progress`
   - Removed skip_save logic

3. **a92f8d4**: `fix: Add target='_self' to prevent new tabs + immediate save after load to fix session persistence`
   - Added target attribute to links

4. **a55839c**: `fix: Revert to working href navigation with UID preservation`
   - Simplified navigation approach

5. Plus earlier commits for review pages and MCIP orchestration

---

## Architecture Notes

### Demo User Workflow
- **Demo Source**: `data/users/demo/<uid>.json` (read-only, protected)
- **Working Copy**: `data/users/<uid>.json` (read-write, session-specific)
- **First Load**: Copy demo source → working copy
- **Subsequent Loads**: Use working copy (has session progress)
- **Session Progress**: Persists in working copy across navigation
- **Demo Reset**: Delete working copy to reload from demo source

### Session Persistence Keys
See `core/session_store.py:549-577` for full list.

**Key entries**:
- `mcip_contracts` ← Contains all MCIP state
- `progress` ← Legacy product completion (deprecated)
- `profile` ← User profile data
- `gcp_care_recommendation` ← GCP assessment answers
- `cost_planner_v2_*` ← Cost Planner assessment states

---

## Known Limitations

1. **Session State vs Persistence**
   - In-memory session state (`st.session_state`) is ephemeral
   - Only persisted keys are saved to disk
   - Non-persisted keys are lost on page reload

2. **Demo Profile Fresh Start**
   - To reset a demo user, delete working copy:
     ```bash
     rm data/users/demo_mary_memory_care.json
     ```
   - Next load will copy fresh from demo source

3. **Concurrent Sessions**
   - Multiple browser tabs share the same UID
   - File locking prevents corruption but doesn't merge state
   - Last save wins

---

## Migration Notes

**For Existing Demo Users**:
1. Delete all working copies in `data/users/`
2. Demo users will reload fresh from `data/users/demo/`
3. Session progress will persist going forward

**For Production**:
- Authenticated users were never affected (no demo logic)
- Anonymous users (`anon_*` UIDs) work as expected
- No migration needed

---

## Future Improvements

1. **Real-time State Sync**
   - Consider WebSocket or polling for multi-tab sync
   - Or lock to single tab per user

2. **Optimistic Saves**
   - Save state on every user interaction, not just render end
   - Reduces risk of data loss on unexpected navigation

3. **Demo Profile Versioning**
   - Track demo profile version in working copy
   - Auto-upgrade working copy if demo source changes

4. **Session Recovery**
   - Add "restore previous session" on crash/timeout
   - Store last successful save timestamp

---

## Conclusion

The root cause was **demo profiles being reloaded on every page load**, overwriting all session progress. Combined with the `skip_save` flag preventing persistence, this created a perfect storm where progress was never saved and always reset.

All three issues are now resolved:
- ✅ Demo profiles persist session progress
- ✅ State always saves after render
- ✅ Navigation stays in same tab

Session persistence now works as expected for demo users, matching the behavior of authenticated users.

---

**Status**: ✅ Complete and merged to `dev`  
**Next Steps**: Deploy to production and monitor for any edge cases
