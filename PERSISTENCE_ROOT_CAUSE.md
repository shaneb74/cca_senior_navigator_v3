# Persistence Layer Debug - Root Cause Analysis

## Problem
User reports:
- No tiles showing complete
- No module progress visible
- Progress lost when navigating away from pages

User's saved file shows:
```json
{
  "progress": {},
  "preferences": {},
  "profile": {},
  "tiles": {},
  "uid": "anon_6611127117e7",
  "last_updated": 1760505231.842378,
  "created_at": 1760505231.842379
}
```

## Root Cause

The persistence system IS working correctly - directories exist, files are being saved. The problem is **the data is never getting into the keys that persistence is looking for**.

### What's Happening:

1. **Module Engine Updates tiles** ✅
   - `core/modules/engine.py` line 280: `tiles = st.session_state.setdefault("tiles", {})`
   - `tile_state["progress"] = progress_pct`
   - `tile_state["status"] = "done"/"doing"/"new"`
   - This DOES work - tiles are being updated in session_state

2. **Persistence Tries to Save tiles** ✅
   - `app.py` line 172: Calls `save_user(uid, user_state_to_save)`
   - `extract_user_state()` looks for keys in `USER_PERSIST_KEYS`
   - USER_PERSIST_KEYS includes `'tiles'`
   
3. **But tiles is EMPTY** ❌
   - When `extract_user_state()` runs, `st.session_state["tiles"]` exists but is `{}`
   - Module updates tiles during render
   - BUT those updates happen AFTER the page render is complete
   - By the time persistence saves, the tiles dict is empty again

### The Timing Issue:

```
1. Page loads → persistence restores empty tiles
2. Module engine runs → updates tiles with progress
3. User clicks button → Streamlit reruns
4. [RERUN CLEARS SESSION STATE]  ← THIS IS THE PROBLEM
5. Persistence tries to save → tiles is empty again
```

**Streamlit reruns clear session_state updates made during the previous run!**

### Why MCIP Works (Sometimes):

MCIP explicitly calls `_save_contracts_for_persistence()` which creates a SEPARATE key `mcip_contracts` that persistence saves. But even this might not survive reruns if not done carefully.

## The Real Issue

**Streamlit's rerun behavior:** When you call `st.rerun()`, Streamlit starts fresh. Any changes to `st.session_state` made during the render are preserved ONLY if:
1. They're made BEFORE the rerun
2. OR they're in persistent storage (database, file)

But our pattern is:
1. Module engine updates `tiles`
2. User clicks Next → `st.rerun()`
3. **Session state is cleared/reset**
4. Persistence saves **empty tiles**

## Solution Options

### Option 1: Immediate Persistence (Best)
Save tiles immediately after updating them, don't wait for end of render:

```python
# In core/modules/engine.py _update_progress()
tiles = st.session_state.setdefault("tiles", {})
tile_state = tiles.setdefault(config.product, {})
tile_state["progress"] = progress_pct
tile_state["status"] = "done" if progress >= 1.0 else "doing" if progress > 0 else "new"

# NEW: Save immediately
from core.session_store import save_user, get_or_create_user_id
uid = get_or_create_user_id(st.session_state)
save_user(uid, {"tiles": tiles})
```

**Pros:**
- Guarantees tiles are saved before rerun
- No data loss
- Simple fix

**Cons:**
- Multiple file writes per render (performance hit)
- Couples module engine to persistence layer

### Option 2: Pre-Rerun Hook
Save state immediately before calling `st.rerun()`:

```python
# In core/modules/engine.py before st.rerun()
def _save_before_rerun():
    from core.session_store import save_user, get_or_create_user_id, extract_user_state
    uid = get_or_create_user_id(st.session_state)
    user_data = extract_user_state(st.session_state)
    if user_data:
        save_user(uid, user_data)

# Then call before every st.rerun()
_save_before_rerun()
st.rerun()
```

**Pros:**
- Saves all user data at once
- Minimal performance impact (once per rerun)
- Clean separation

**Cons:**
- Need to wrap every `st.rerun()` call
- Easy to forget

### Option 3: Session State Callback
Use Streamlit's session_state callbacks to save on change:

```python
# NOT VIABLE: Streamlit doesn't have global session_state change callbacks
```

### Option 4: Persistent Session State Wrapper
Create a wrapper that auto-saves on write:

```python
class PersistentDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        # Auto-save to disk
        _save_to_disk()
```

**Pros:**
- Transparent persistence
- No code changes needed

**Cons:**
- Complex implementation
- Performance overhead
- May not work with Streamlit's internal state management

## Recommended Solution

**Use Option 2 with a centralized rerun helper:**

1. Create `core/nav.py:safe_rerun()` function
2. Always use `safe_rerun()` instead of `st.rerun()`
3. This function saves state before rerunning

Implementation:

```python
# core/nav.py or core/session_store.py

def safe_rerun():
    """Save session state then rerun. ALWAYS use this instead of st.rerun()."""
    import streamlit as st
    from core.session_store import save_user, save_session, get_or_create_user_id, extract_user_state, extract_session_state
    
    # Save user data
    uid = get_or_create_user_id(st.session_state)
    user_data = extract_user_state(st.session_state)
    if user_data:
        save_user(uid, user_data)
    
    # Save session data
    if 'session_id' in st.session_state:
        session_data = extract_session_state(st.session_state)
        if session_data:
            save_session(st.session_state['session_id'], session_data)
    
    # Now rerun
    st.rerun()
```

Then update all `st.rerun()` calls:

```python
# Replace all instances:
st.rerun()

# With:
from core.nav import safe_rerun
safe_rerun()
```

## Files to Update

1. **core/nav.py** or **core/session_store.py**
   - Add `safe_rerun()` function

2. **core/modules/engine.py**
   - Replace 6 instances of `st.rerun()` with `safe_rerun()`
   - Lines: ~120, ~341, ~421, ~730, ~1124, ~1354

3. **products/gcp_v4/product.py**
   - Replace st.rerun() if any

4. **All other product files**
   - Search for `st.rerun()` and replace

5. **Hub files**
   - Search for `st.rerun()` and replace

## Testing Plan

1. Clear user data: `rm data/users/*.json`
2. Start fresh session
3. Complete first GCP question
4. Check `data/users/anon_*.json` → Should have tiles with progress
5. Navigate away and back
6. Check tiles still show progress
7. Complete full GCP
8. Verify tiles shows "done" status
9. Close browser and reopen
10. Verify progress persists

## Alternative: Database-Backed Session State

If file-based persistence continues to have issues, consider:
- Redis for session state
- SQLite for user data
- Streamlit Cloud's built-in persistence (if deploying there)

But for local development and small deployments, fixing the rerun timing should be sufficient.

## Status

❌ **BROKEN** - Progress not persisting due to rerun timing
🔧 **FIX READY** - Implement `safe_rerun()` wrapper
✅ **QUICK WIN** - Should take <30 minutes to implement and test
