# How the App Loads Previous User Data

**Complete guide to the persistence and data loading system**

---

## Quick Answer

The app loads previous user data in 3 steps:

1. **Get User ID (UID)** from URL query param `?uid=anon_xxx` or generate new one
2. **Load user data** from `data/users/{uid}.json` file
3. **Merge into session_state** so all pages can access it

This happens **once per browser session** when the app first starts (before rendering any pages).

---

## The Complete Flow

### 1. App Startup (`app.py` lines 120-156)

```python
# Step 1: Get or generate session ID (browser-specific)
session_id = st.session_state.get("session_id") or generate_session_id()

# Step 2: Get User ID - CHECK URL FIRST!
uid_from_url = st.query_params.get("uid")

if uid_from_url:
    # User navigated with UID in URL (bookmark, link, tab)
    # Restore their previous session
    uid = uid_from_url
    
    if uid_from_url.startswith("anon_"):
        # Anonymous user
        st.session_state["anonymous_uid"] = uid_from_url
    else:
        # Authenticated user
        st.session_state["auth"]["user_id"] = uid_from_url
        st.session_state["auth"]["is_authenticated"] = True
else:
    # No UID in URL - generate new one or get from session
    uid = get_or_create_user_id(st.session_state)
    
    # Add UID to query params so future navigation preserves it
    st.query_params["uid"] = uid

# Step 3: Load data (ONLY on first run per browser session)
if "persistence_loaded" not in st.session_state:
    # Load session data (temporary, browser-specific)
    session_data = load_session(session_id)
    merge_into_state(st.session_state, session_data)
    
    # Load user data (persistent, cross-device)
    user_data = load_user(uid)
    merge_into_state(st.session_state, user_data)
    
    # Mark as loaded so we don't reload on every render
    st.session_state["persistence_loaded"] = True
```

### 2. User ID Generation (`core/session_store.py` lines 542-567)

```python
def get_or_create_user_id(state: dict[str, Any]) -> str:
    """Priority order:
    1. Authenticated user ID (from login system)
    2. Anonymous user ID (from session)
    3. Generate new anonymous ID
    """
    
    # Check for authenticated user
    auth = state.get("auth", {})
    if auth.get("is_authenticated") and auth.get("user_id"):
        return auth["user_id"]
    
    # Check for anonymous user ID
    if "anonymous_uid" in state:
        return state["anonymous_uid"]
    
    # Generate NEW anonymous ID (format: anon_{12-char-hash})
    anonymous_uid = f"anon_{uuid.uuid4().hex[:12]}"
    state["anonymous_uid"] = anonymous_uid
    return anonymous_uid
```

### 3. Loading User Data (`core/session_store.py` lines 348-390)

```python
def load_user(uid: str) -> dict[str, Any]:
    """Load user data from data/users/{uid}.json"""
    
    path = get_user_path(uid)  # data/users/{uid}.json
    
    with _file_lock(path):
        data = _safe_read(path)
    
    if data is None:
        # File doesn't exist - return empty default
        return {
            "uid": uid,
            "created_at": time.time(),
            "last_updated": time.time(),
            "profile": {},
            "progress": {},
            "mcip": {},
            "preferences": {},
            "tiles": {},
        }
    
    # File exists - return the data
    data["uid"] = uid
    data["last_updated"] = time.time()
    return data
```

### 4. Merging into Session State (`core/session_store.py` lines 526-535)

```python
def merge_into_state(state: dict[str, Any], loaded_data: dict[str, Any]) -> None:
    """Merge loaded data into st.session_state.
    
    Skips metadata keys like uid, created_at, etc.
    """
    for key, value in loaded_data.items():
        # Skip metadata
        if key not in ["uid", "session_id", "created_at", "last_updated", "last_accessed"]:
            state[key] = value
```

### 5. Saving Data (`app.py` lines 206-217)

```python
# AFTER rendering the page, save data

# Save session data (browser-specific, temporary)
session_state_to_save = extract_session_state(st.session_state)
if session_state_to_save:
    save_session(session_id, session_state_to_save)

# Save user data (persistent, cross-device)
user_state_to_save = extract_user_state(st.session_state)
if user_state_to_save:
    save_user(uid, user_state_to_save)
```

---

## What Gets Saved vs. What Gets Loaded

### USER_PERSIST_KEYS (Persistent, cross-device)

These keys are saved to `data/users/{uid}.json` and loaded when user returns:

```python
USER_PERSIST_KEYS = {
    "profile",              # User profile info
    "progress",             # Product completion status
    "mcip_contracts",       # MCIP contracts (care plans, etc.)
    "tiles",                # Legacy tile system
    "product_tiles_v2",     # New tile system (badges, trivia)
    "preferences",          # User settings
    "auth",                 # Authentication status
    "flags",                # Feature flags
    
    # Cost Planner v2 state (NEWLY ADDED)
    "cost_v2_step",
    "cost_v2_guest_mode",
    "cost_v2_triage",
    "cost_v2_qualifiers",
    "cost_v2_current_module",
    "cost_v2_modules",      # ← Main assessment data
    "cost_v2_income",
    "cost_v2_assets",
    "cost_v2_va_benefits",
    "cost_v2_health_insurance",
    "cost_v2_life_insurance",
    "cost_v2_medicaid_navigation",
    "cost_v2_advisor_notes",
    "cost_v2_schedule_advisor",
    "cost_v2_quick_estimate",
    "cost_planner_v2_published",
    "cost_planner_v2_complete",
}
```

### SESSION_PERSIST_KEYS (Temporary, browser-specific)

These keys are saved to `.cache/session_{id}.json` (temporary, not restored after app restart):

```python
SESSION_PERSIST_KEYS = {
    "current_route",    # Current page
    "temp_form_data",   # In-progress forms
    "wizard_step",      # Wizard progress
    "last_error",       # Error messages
}
```

---

## User Scenarios

### Scenario 1: New User, First Visit

1. User opens `http://localhost:8501/`
2. No `?uid=` in URL
3. `get_or_create_user_id()` generates: `anon_d2c42550e6a3`
4. `load_user("anon_d2c42550e6a3")` → file doesn't exist → returns empty defaults
5. App adds `?uid=anon_d2c42550e6a3` to URL
6. User fills out Cost Planner assessments
7. Data saved to `data/users/anon_d2c42550e6a3.json`

**Result:** New user with empty state

---

### Scenario 2: Same User, New Browser Tab

1. User clicks link in app → opens in new tab
2. URL includes `?uid=anon_d2c42550e6a3`
3. App reads UID from URL
4. `load_user("anon_d2c42550e6a3")` → file exists → loads all data
5. User sees their previous data

**Result:** Data restored from same UID

---

### Scenario 3: App Restart (No Bookmark)

1. User was using `http://localhost:8501/?uid=anon_d2c42550e6a3`
2. User stops app (Ctrl+C)
3. User restarts: `streamlit run app.py`
4. Browser opens `http://localhost:8501/` (NO UID!)
5. No UID in URL → generates NEW UID: `anon_9cb5f556f4fd`
6. Loads data for NEW UID → empty (different user)

**Result:** Data "lost" because different UID = different user

---

### Scenario 4: App Restart (With Bookmark)

1. User was using `http://localhost:8501/?uid=anon_d2c42550e6a3`
2. User bookmarks the URL
3. User stops app (Ctrl+C)
4. User restarts: `streamlit run app.py`
5. User navigates to bookmark: `http://localhost:8501/?uid=anon_d2c42550e6a3`
6. App reads UID from URL
7. Loads data for that UID → **all data restored!**

**Result:** Data restored because same UID maintained via URL

---

### Scenario 5: Multiple Browser Sessions

1. User A: `?uid=anon_d2c42550e6a3`
   - File: `data/users/anon_d2c42550e6a3.json`
2. User B: `?uid=anon_325a505188fa`
   - File: `data/users/anon_325a505188fa.json`
3. User C: `?uid=anon_784679f69d83`
   - File: `data/users/anon_784679f69d83.json`

Each UID has its own data file, completely separate.

**Result:** Multiple independent users

---

## The UID is the KEY

### Critical Understanding

**The UID is the ONLY thing that identifies a user.**

- Same UID = Same user = Same data
- Different UID = Different user = Different data
- UID in URL = Data can be restored
- No UID in URL = New UID generated = Appears as new user

### Why Multiple User Files?

You see multiple files because:
1. Each browser session (without UID in URL) = new UID
2. Each UID = separate user file
3. This is CORRECT behavior for anonymous users

To use same user across sessions:
- **Bookmark the URL with UID**
- Or implement UID persistence in browser localStorage
- Or implement authentication system (email/password login)

---

## File Structure

```
project/
├── data/
│   └── users/
│       ├── anon_d2c42550e6a3.json  ← User 1 (persistent)
│       ├── anon_325a505188fa.json  ← User 2 (persistent)
│       └── anon_784679f69d83.json  ← User 3 (persistent)
├── .cache/
│   └── session_abc123.json         ← Browser session (temporary)
```

### User File Contents (data/users/{uid}.json)

```json
{
  "uid": "anon_d2c42550e6a3",
  "created_at": 1729267200.0,
  "last_updated": 1729267800.0,
  "profile": { ... },
  "progress": { ... },
  "mcip_contracts": { ... },
  "cost_v2_modules": {
    "income": {
      "status": "completed",
      "progress": 100,
      "data": {
        "ss_monthly": 2000,
        "pension_monthly": 1500,
        ...
      }
    },
    ...
  },
  "cost_v2_quick_estimate": {
    "estimate": {
      "monthly_base": 4500,
      "monthly_adjusted": 5400,
      ...
    },
    "care_tier": "assisted_living",
    "zip_code": "94102"
  }
}
```

---

## When Does Data Load?

### Load Timing

```python
if "persistence_loaded" not in st.session_state:
    # THIS RUNS ONLY ONCE per browser session
    user_data = load_user(uid)
    merge_into_state(st.session_state, user_data)
    st.session_state["persistence_loaded"] = True
```

**Loads exactly ONCE:**
- When browser session starts (first render)
- When app restarts (if UID maintained via URL)

**Does NOT reload:**
- On every page render
- On navigation between pages
- On form submissions

Once loaded, data lives in `st.session_state` for the entire browser session.

---

## When Does Data Save?

### Save Timing

```python
# app.py - AFTER rendering page

user_state_to_save = extract_user_state(st.session_state)
if user_state_to_save:
    save_user(uid, user_state_to_save)
```

**Saves on EVERY render:**
- After every page load
- After every form submission
- After every navigation
- After every user interaction

This ensures data is always up-to-date on disk.

---

## How to Maintain UID Across Restarts

### Option 1: Bookmark URL (Current System)

```
http://localhost:8501/?uid=anon_d2c42550e6a3
```

✅ Simple, no code changes
❌ Users must manually bookmark

### Option 2: Browser LocalStorage (Future Enhancement)

```javascript
// Store UID in browser
localStorage.setItem('senior_nav_uid', 'anon_d2c42550e6a3');

// Retrieve on app load
const uid = localStorage.getItem('senior_nav_uid');
```

✅ Automatic persistence
✅ Survives app restarts
❌ Requires custom JS component

### Option 3: Authentication System (Full Solution)

```python
# User logs in with email/password
# UID = user database ID or email
# Always same UID for that user
```

✅ True multi-device sync
✅ Secure
❌ Requires backend, auth system

---

## Common Issues & Solutions

### Issue 1: "Data disappeared after restart"

**Cause:** Different UID (new browser session, no UID in URL)

**Solution:** Bookmark URL with UID parameter

**Verify:**
```bash
# Check what UIDs you have
ls data/users/

# See which one has your data
cat data/users/anon_xxx.json | jq '.cost_v2_modules'
```

---

### Issue 2: "Multiple user files created"

**Cause:** Each browser session without UID in URL creates new UID

**Solution:** This is CORRECT behavior. To reuse same user:
- Bookmark the URL with UID
- Or implement localStorage UID persistence

---

### Issue 3: "Data not saving"

**Cause 1:** Keys not in `USER_PERSIST_KEYS`
**Solution:** Add to `USER_PERSIST_KEYS` in `core/session_store.py`

**Cause 2:** Non-serializable objects (dataclasses, functions, etc.)
**Solution:** Convert to dict before storing (like `CostEstimate.to_dict()`)

**Verify:**
```bash
# Check if data actually saved
cat data/users/anon_xxx.json | jq '.cost_v2_modules'

# Should show your assessment data
```

---

## Testing Data Persistence

### Test 1: Does data save?

```bash
# 1. Start app
streamlit run app.py

# 2. Fill out Cost Planner assessment
# 3. Note UID from URL: ?uid=anon_xxx

# 4. Check file exists and has data
cat data/users/anon_xxx.json | jq '.cost_v2_modules'
```

✅ Should show assessment data

---

### Test 2: Does data load?

```bash
# 1. Note current UID from URL: ?uid=anon_xxx
# 2. Stop app (Ctrl+C)
# 3. Restart app: streamlit run app.py
# 4. Navigate to: http://localhost:8501/?uid=anon_xxx
# 5. Go to Cost Planner
```

✅ Should see previous data

---

### Test 3: Different UID = different data?

```bash
# 1. Fill out data for UID: anon_aaa
# 2. Navigate to: http://localhost:8501/?uid=anon_bbb
# 3. Check Cost Planner
```

✅ Should be empty (different user)

---

## Summary

### The Three Keys to Persistence

1. **UID in URL** - Identifies which user's data to load
2. **USER_PERSIST_KEYS** - Defines what gets saved
3. **JSON Serialization** - Data must be JSON-serializable

### The Data Flow

```
Browser Request
    ↓
Extract UID from URL (?uid=anon_xxx)
    ↓
Load data/users/anon_xxx.json
    ↓
Merge into st.session_state
    ↓
Render page (user sees their data)
    ↓
User makes changes
    ↓
Save st.session_state → data/users/anon_xxx.json
    ↓
Next request: Load same file again
```

### Best Practice

**For Development:**
- Bookmark: `http://localhost:8501/?uid=anon_dev_test`
- Always use same UID for testing

**For Production:**
- Implement localStorage UID persistence
- Or implement authentication system
- Or educate users to bookmark URLs
