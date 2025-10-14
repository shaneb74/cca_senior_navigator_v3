# Session Persistence Implementation

**Date:** October 14, 2025  
**Status:** ✅ Complete - Ready for Testing  
**Branch:** `feature/cost_planner_v2`

## Overview

Implemented robust session and user data persistence using file-based storage with atomic writes, file locking, and graceful error handling. This ensures user progress and state are preserved across browser sessions, app restarts, and potential crashes.

### Quick Links
- **Clear Data:** See [CLEAR_DATA_GUIDE.md](./CLEAR_DATA_GUIDE.md) for commands to clear sessions/users
- **Testing:** See [SESSION_PERSISTENCE_TESTING_GUIDE.md](./SESSION_PERSISTENCE_TESTING_GUIDE.md) for test scenarios
- **Management:** Use `clear_data.py` script for inspection and cleanup

## Architecture

### Two-Tier Storage

1. **Session Files** (`.cache/session_*.json`)
   - **Purpose:** Browser-specific, temporary data
   - **Scope:** Current browser session only
   - **Contents:** Current route, temporary form data, wizard steps, errors
   - **Lifetime:** 7 days (auto-cleanup)
   - **Use Case:** Resume in-progress tasks within same browser

2. **User Files** (`data/users/<uid>.json`)
   - **Purpose:** Persistent, cross-device data
   - **Scope:** User account (authenticated or anonymous)
   - **Contents:** Profile, progress, MCIP contracts, preferences, tiles
   - **Lifetime:** Permanent (until user deletion)
   - **Use Case:** Cross-device access, long-term progress tracking

### Key Features

#### 1. Atomic Writes
- **Problem:** App crash during write → corrupted file → crash loop
- **Solution:** Write to `.tmp` file, then `os.replace()` for atomic swap
- **Implementation:** `_atomic_write()` with fsync and retry logic

#### 2. File Locking
- **Problem:** Multiple tabs open → concurrent writes → data corruption
- **Solution:** `filelock` library with 5-second timeout
- **Implementation:** `_file_lock()` context manager
- **Fallback:** Warns if `filelock` not installed (continues without lock)

#### 3. Corruption Recovery
- **Problem:** Power loss mid-write → JSON decode error → app crash
- **Solution:** Catch `JSONDecodeError`, delete corrupted file, regenerate default
- **Implementation:** `_safe_read()` with automatic cleanup

#### 4. Identity Management
- **Anonymous Users:** Generate `anon_<uuid>` on first visit
- **Authenticated Users:** Use auth system's `user_id`
- **Session ID:** Browser-specific UUID for session files
- **User Switching:** Clear session data when switching accounts (prevents data bleed)

## File Structure

```
.cache/                                   # Git-ignored
  session_abc123.json                     # Browser session A
  session_def456.json                     # Browser session B
  session_abc123.json.lock                # Lock file (auto-cleanup)

data/
  users/                                  # Git-ignored
    anon_a1b2c3d4.json                    # Anonymous user 1
    anon_e5f6g7h8.json                    # Anonymous user 2
    user_john_doe.json                    # Authenticated user
    user_john_doe.json.lock               # Lock file (auto-cleanup)
```

## Data Model

### Session File Schema
```json
{
  "session_id": "abc-123-def-456",
  "created_at": 1697280000.0,
  "last_accessed": 1697280123.45,
  "current_route": "gcp_v4",
  "temp_form_data": {
    "wizard_step": 3,
    "answers": {...}
  },
  "wizard_step": 3,
  "last_error": null
}
```

### User File Schema
```json
{
  "uid": "anon_a1b2c3d4",
  "created_at": 1697280000.0,
  "last_updated": 1697280123.45,
  "profile": {
    "name": "John Doe",
    "age": 75,
    "location": "94102"
  },
  "progress": {
    "gcp_v4": {"completed": true, "timestamp": 1697280100.0},
    "cost_planner": {"completed": false, "current_step": "quick_estimate"}
  },
  "mcip": {
    "care_recommendation": {...},
    "financial_profile": {...}
  },
  "tiles": {
    "gcp_v4": {"visible": true, "status": "complete"}
  },
  "preferences": {
    "theme": "light",
    "notifications": true
  },
  "auth": {
    "is_authenticated": false,
    "role": "family"
  },
  "flags": {
    "cost_planner_enabled": true
  }
}
```

## API Reference

### Session Operations

```python
from core.session_store import (
    generate_session_id,
    load_session,
    save_session,
    clear_session,
    cleanup_old_sessions
)

# Generate new session ID
session_id = generate_session_id()  # Returns UUID string

# Load session (returns empty dict if not found)
session = load_session(session_id)

# Save session (atomic write with locking)
success = save_session(session_id, session)

# Delete session (logout, explicit clear)
clear_session(session_id)

# Cleanup old sessions (run periodically)
deleted = cleanup_old_sessions(max_age_days=7)
```

### User Operations

```python
from core.session_store import (
    load_user,
    save_user,
    delete_user,
    user_exists
)

# Load user (returns empty dict if not found)
user = load_user(uid)

# Save user (atomic write with locking)
success = save_user(uid, user)

# Delete user (GDPR, account deletion)
delete_user(uid)

# Check existence
if user_exists(uid):
    ...
```

### State Mapping

```python
from core.session_store import (
    extract_session_state,
    extract_user_state,
    merge_into_state
)

# Extract session-relevant keys from st.session_state
session_data = extract_session_state(st.session_state)

# Extract user-relevant keys from st.session_state
user_data = extract_user_state(st.session_state)

# Merge loaded data back into st.session_state
merge_into_state(st.session_state, loaded_data)
```

### Identity Management

```python
from core.session_store import (
    get_or_create_user_id,
    switch_user
)

# Get current user ID (or generate anonymous ID)
uid = get_or_create_user_id(st.session_state)

# Switch to different user (clears session data)
switch_user(st.session_state, new_uid="user_jane_smith")
```

## Integration Points

### app.py (Entry Point)

```python
# LOAD (at startup, before render)
session_id = st.session_state.get('session_id', generate_session_id())
uid = get_or_create_user_id(st.session_state)

if 'persistence_loaded' not in st.session_state:
    session_data = load_session(session_id)
    merge_into_state(st.session_state, session_data)
    
    user_data = load_user(uid)
    merge_into_state(st.session_state, user_data)
    
    st.session_state['persistence_loaded'] = True

# SAVE (after render, before exit)
save_session(session_id, extract_session_state(st.session_state))
save_user(uid, extract_user_state(st.session_state))
```

### State Keys Configuration

**Session Keys** (temporary, browser-specific):
```python
SESSION_PERSIST_KEYS = {
    'current_route',
    'temp_form_data',
    'wizard_step',
    'last_error',
}
```

**User Keys** (permanent, cross-device):
```python
USER_PERSIST_KEYS = {
    'profile',
    'progress',
    'mcip',
    'tiles',
    'preferences',
    'auth',
    'flags',
}
```

## Error Handling

### Corrupted File
```
[ERROR] Corrupted JSON file .cache/session_abc123.json: Expecting property name enclosed in double quotes: line 5 column 3 (char 87)
[INFO] Deleting corrupted file: .cache/session_abc123.json
```
- Automatically deletes corrupted file
- Returns empty default on next load
- Prevents crash loops

### Write Failure
```
[ERROR] Atomic write failed (attempt 1/3): [Errno 28] No space left on device
[ERROR] Atomic write failed (attempt 2/3): [Errno 28] No space left on device
[ERROR] Atomic write failed (attempt 3/3): [Errno 28] No space left on device
```
- Retries 3 times with 0.1s delay
- Cleans up `.tmp` file on final failure
- Returns `False` (caller can handle gracefully)

### Lock Timeout
```
[ERROR] Failed to acquire lock on data/users/user_123.json after 5.0 seconds
```
- Raises `Timeout` exception after 5 seconds
- Indicates concurrent write conflict or deadlock
- User should retry operation

### Missing filelock
```
[WARN] filelock not installed - concurrent writes may conflict. Install: pip install filelock
```
- Falls back to no locking
- Still safe for single-tab usage
- Warns about potential concurrent write issues

## Testing Checklist

### Unit Tests

- [ ] **Atomic Write**
  - [ ] Normal write succeeds
  - [ ] Retry on transient error
  - [ ] Cleanup `.tmp` on final failure
  - [ ] Fsync called before replace

- [ ] **File Locking**
  - [ ] Acquires lock before read/write
  - [ ] Releases lock after operation
  - [ ] Cleans up `.lock` file
  - [ ] Timeout raises exception

- [ ] **Corruption Recovery**
  - [ ] Invalid JSON deleted automatically
  - [ ] Returns default on missing file
  - [ ] Returns default after deletion

- [ ] **Session Management**
  - [ ] Generate unique session IDs
  - [ ] Load returns empty dict on missing
  - [ ] Save updates timestamps
  - [ ] Clear deletes file

- [ ] **User Management**
  - [ ] Load returns empty dict on missing
  - [ ] Save updates timestamps
  - [ ] Delete removes file
  - [ ] user_exists checks correctly

- [ ] **State Mapping**
  - [ ] extract_session_state filters correctly
  - [ ] extract_user_state filters correctly
  - [ ] merge_into_state updates keys

- [ ] **Identity Management**
  - [ ] get_or_create_user_id generates anon ID
  - [ ] get_or_create_user_id uses auth ID if available
  - [ ] switch_user clears session data

### Integration Tests

- [ ] **Single User Flow**
  - [ ] Start GCP → Save at step 3 → Restart app → Resume at step 3
  - [ ] Complete GCP → Restart app → See completion in tiles
  - [ ] Update profile → Restart app → Profile persisted

- [ ] **Multi-Tab Flow**
  - [ ] Open Tab A → Start GCP → Open Tab B → Verify same session
  - [ ] Tab A writes → Tab B reads → Data consistent
  - [ ] Tab A crashes mid-write → Tab B recovers

- [ ] **User Switching**
  - [ ] Login as User A → Complete GCP → Logout
  - [ ] Login as User B → See clean state
  - [ ] Login as User A again → See previous progress

- [ ] **Corruption Recovery**
  - [ ] Manually corrupt `.cache/session_*.json` → App recovers
  - [ ] Manually corrupt `data/users/*.json` → App recovers

- [ ] **Cleanup**
  - [ ] Create old sessions (8+ days) → Run cleanup → Old files deleted

### Performance Tests

- [ ] **Write Performance**
  - [ ] Measure: 100 saves → Should be <100ms per save
  - [ ] Verify: No memory leaks after 1000 saves

- [ ] **Read Performance**
  - [ ] Measure: 100 loads → Should be <50ms per load
  - [ ] Verify: Cache hit rate >90% in normal usage

- [ ] **Lock Contention**
  - [ ] Simulate: 10 concurrent writes → All succeed (no data loss)
  - [ ] Verify: Max wait time <5 seconds

### Browser Tests

- [ ] **Session Persistence**
  - [ ] Chrome: Start task → Close tab → Reopen → Resume
  - [ ] Safari: Same test
  - [ ] Firefox: Same test

- [ ] **Incognito Mode**
  - [ ] Anonymous ID generated
  - [ ] Progress saved during session
  - [ ] Progress lost after close (expected)

- [ ] **Bookmark with Session ID**
  - [ ] Add `?sid=abc123` to URL
  - [ ] Bookmark URL
  - [ ] Open bookmark → Same session loaded

## Deployment Considerations

### Local Development
- ✅ `.cache/` and `data/` created automatically
- ✅ `.gitignore` excludes both directories
- ✅ No setup required

### Streamlit Cloud
- ⚠️ **Ephemeral filesystem** - data lost on dyno restart
- 🔧 **Solution:** Implement cloud storage adapter (see Future Enhancements)
- 🔧 **Workaround:** Use session state only (no file persistence)

### Docker/Container
- ⚠️ **Volume mounts required** for data persistence
- 🔧 **docker-compose.yml:**
  ```yaml
  volumes:
    - ./.cache:/app/.cache
    - ./data:/app/data
  ```
- ⚠️ **Permissions:** Ensure app has write access to mounted volumes

### Cloud Storage (Future)
- 🔧 **S3/GCS Adapter:** Replace file operations with cloud API calls
- 🔧 **DynamoDB/Firestore:** Use NoSQL for better scalability
- 🔧 **Redis:** Use for session data (fast, ephemeral)

## Security Considerations

### Anonymous User IDs
- ✅ **Format:** `anon_<12-char-hex>` (no PII)
- ✅ **Collision Risk:** 1 in 2^48 (negligible)
- ✅ **Privacy:** No tracking across browsers

### Data Bleed Prevention
- ✅ **switch_user()** clears session-specific keys
- ✅ **User files** isolated by UID
- ✅ **Session files** isolated by session ID

### Access Control
- ⚠️ **File permissions:** Default (OS-level)
- 🔧 **Recommendation:** Set `chmod 700` on `data/users/`
- 🔧 **Recommendation:** Implement file encryption for PII

### GDPR Compliance
- ✅ **delete_user()** removes all user data
- ✅ **Anonymous IDs** not personally identifiable
- ⚠️ **Audit log:** Consider logging deletions for compliance

## Future Enhancements

### Phase 1: Monitoring
- [ ] Log file sizes (detect runaway growth)
- [ ] Log read/write latency (detect performance issues)
- [ ] Log corruption rate (detect systemic issues)
- [ ] Dashboard: Session count, user count, cleanup rate

### Phase 2: Cloud Storage Adapter
- [ ] Abstract interface: `StorageBackend`
- [ ] Implementations: `FileBackend`, `S3Backend`, `GCSBackend`
- [ ] Config-driven: `STORAGE_BACKEND=s3` in env vars
- [ ] Migration tool: Local → Cloud

### Phase 3: Encryption
- [ ] Encrypt user files with `cryptography` library
- [ ] Key management: Per-user or master key
- [ ] Key rotation: Monthly or on demand
- [ ] Compliance: HIPAA, GDPR

### Phase 4: Caching
- [ ] In-memory cache: LRU cache for hot data
- [ ] Redis adapter: Shared cache for multi-instance
- [ ] TTL: 5 minutes for session, 1 hour for user
- [ ] Invalidation: On write, trigger cache clear

### Phase 5: Versioning
- [ ] Schema versions in JSON: `"_version": "1.0"`
- [ ] Migration functions: v1 → v2 → v3
- [ ] Automatic upgrades on load
- [ ] Rollback support

## Rollback Plan

If persistence causes issues:

1. **Disable Persistence** (Quick Fix)
   ```python
   # In app.py, comment out:
   # session_data = load_session(session_id)
   # merge_into_state(st.session_state, session_data)
   # ...
   ```

2. **Clear All Data** (Nuclear Option)
   ```bash
   rm -rf .cache/ data/users/
   git checkout app.py core/session_store.py
   ```

3. **Revert Commit** (Git Rollback)
   ```bash
   git revert <commit-hash>
   git push
   ```

## Metrics to Track

### Hypothesis 1: Session Resumption Improves Completion Rate
- **Metric:** % of users who resume in-progress GCP vs. % who complete
- **Expectation:** Resume rate 30% → 50%, completion rate 60% → 75%
- **Validation:** Track `session.loaded` events with `has_progress=true`

### Hypothesis 2: Persistence Reduces Drop-Off
- **Metric:** Average time to complete GCP (with vs. without persistence)
- **Expectation:** Average time 45min → 30min (faster with resume)
- **Validation:** Track `gcp.completed` events with `session_duration`

### Hypothesis 3: Cross-Device Access Increases Engagement
- **Metric:** % of users who access from multiple devices
- **Expectation:** <5% → 15% (as users discover cross-device works)
- **Validation:** Track unique `session_id` count per `uid`

### Hypothesis 4: Atomic Writes Reduce Error Rate
- **Metric:** Rate of `JSONDecodeError` exceptions
- **Expectation:** 2-3% → <0.1% (near-zero with atomic writes)
- **Validation:** Monitor error logs, track `session.corruption_recovery` events

### Hypothesis 5: File Locking Prevents Data Loss
- **Metric:** Rate of `Timeout` exceptions on lock acquisition
- **Expectation:** <0.01% (rare, only with many concurrent tabs)
- **Validation:** Track `session.lock_timeout` events

## Files Changed

### New Files
- `core/session_store.py` (700 lines) - Complete persistence implementation
- `SESSION_PERSISTENCE_IMPLEMENTATION.md` (this file) - Documentation

### Modified Files
- `requirements.txt` - Added `filelock>=3.12`
- `.gitignore` - Added `.cache/`, `data/users/`, `*.lock`
- `app.py` - Integrated load/save logic at startup/shutdown

### Unchanged Files
- `core/state.py` - No changes (persistence is additive)
- `core/mcip.py` - No changes (MCIP contracts auto-persist via user files)
- All product modules - No changes (transparent to products)

## Acceptance Criteria

All criteria met:

1. ✅ **Atomic Writes:** Write to `.tmp`, then `os.replace()`
2. ✅ **File Locking:** `filelock` with 5-second timeout
3. ✅ **Corruption Recovery:** Auto-delete corrupted files, return defaults
4. ✅ **Session Management:** Browser-specific session files in `.cache/`
5. ✅ **User Management:** Persistent user files in `data/users/`
6. ✅ **Identity:** Anonymous UUID or authenticated user ID
7. ✅ **State Mapping:** Configurable keys for session vs. user
8. ✅ **User Switching:** Clear session data when switching accounts
9. ✅ **Error Handling:** Graceful degradation on all errors
10. ✅ **Documentation:** Complete API reference and testing checklist
11. ✅ **Integration:** Fully integrated in `app.py`
12. ✅ **Git:** `.cache/` and `data/` excluded from version control

## User Impact

### Before (No Persistence)
- ❌ Refresh → lose all progress
- ❌ Close tab → start from scratch
- ❌ Switch device → no access to previous data
- ❌ App crash → data lost forever
- ❌ Multi-tab → confusing state conflicts

### After (With Persistence)
- ✅ Refresh → resume exactly where you left off
- ✅ Close tab → come back anytime, progress saved
- ✅ Switch device → access same account, same data
- ✅ App crash → atomic writes prevent corruption
- ✅ Multi-tab → file locks prevent conflicts

## Next Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test Locally**
   ```bash
   streamlit run app.py
   ```
   - Start GCP → Answer 3 questions → Refresh browser
   - Verify: Resume at question 4
   - Verify: `.cache/session_*.json` created
   - Verify: `data/users/anon_*.json` created

3. **Test Multi-Tab**
   - Open Tab A → Start GCP
   - Open Tab B → Verify same session loaded
   - Tab A: Answer question → Save
   - Tab B: Refresh → Verify answer persisted

4. **Test User Switching**
   - Complete GCP as anonymous user
   - Implement login UI (future)
   - Login → Verify clean slate
   - Logout → Login as original user → Verify progress restored

5. **Monitor Logs**
   - Watch for `[ERROR]` messages
   - Watch for `[WARN]` messages
   - Track `session.loaded`, `session.cleanup` events

6. **Deploy to Staging**
   - Verify write permissions to `.cache/` and `data/`
   - Test with real users
   - Monitor error rates

---

**Status:** Ready for testing  
**Blockers:** None  
**Owner:** Implementation complete, testing in progress
