"""
Session and User Data Persistence

Provides atomic file operations with locking for session and user data.
Prevents data corruption from concurrent writes or app crashes.

Architecture:
- .cache/session.json: Per-browser session state (route, temp data)
- data/users/<uid>.json: Persistent user profile and progress
- Atomic writes: Write to .tmp file, then os.replace()
- File locking: Prevents concurrent write conflicts
- Auto-cleanup: Handles corrupted files gracefully

Usage:
    # Session (browser-specific, temporary)
    session = load_session(session_id)
    session['current_route'] = 'gcp_v4'
    save_session(session_id, session)

    # User (persistent, cross-device if authenticated)
    user = load_user(uid)
    user['profile']['name'] = 'John Doe'
    save_user(uid, user)
"""

import json
import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional, Dict
from typing import Any

try:
    import filelock

    HAS_FILELOCK = True
except ImportError:
    HAS_FILELOCK = False
    print(
        "[WARN] filelock not installed - concurrent writes may conflict. Install: pip install filelock"
    )


# ====================================================================
# CONFIGURATION
# ====================================================================

# Cache directory for session files (browser-specific, temporary)
CACHE_DIR = Path(".cache")

# Data directory for user profiles (persistent, cross-device)
DATA_DIR = Path("data/users")

# Demo profiles directory (read-only, protected from overwrite)
DEMO_DIR = Path("data/users/demo")

# Session file name pattern
SESSION_FILE_PATTERN = "session_{session_id}.json"

# User file name pattern
USER_FILE_PATTERN = "{uid}.json"

# Lock timeout (seconds) - how long to wait for file lock
LOCK_TIMEOUT = 5

# Max retry attempts for atomic writes
MAX_RETRIES = 3

# Retry delay (seconds)
RETRY_DELAY = 0.1


# ====================================================================
# INITIALIZATION
# ====================================================================


def _ensure_directories() -> None:
    """Create cache and data directories if they don't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DEMO_DIR.mkdir(parents=True, exist_ok=True)


_ensure_directories()


# ====================================================================
# FILE LOCKING
# ====================================================================


@contextmanager
def _file_lock(path: Path, timeout: float = LOCK_TIMEOUT):
    """Context manager for file locking.

    If filelock is installed, uses FileLock.
    Otherwise, falls back to no locking (with warning).

    Args:
        path: File path to lock
        timeout: Timeout in seconds

    Yields:
        None
    """
    if HAS_FILELOCK:
        lock_path = path.with_suffix(path.suffix + ".lock")
        lock = filelock.FileLock(str(lock_path), timeout=timeout)
        try:
            with lock:
                yield
        finally:
            # Clean up lock file if it exists
            if lock_path.exists():
                try:
                    lock_path.unlink()
                except OSError:
                    pass
    else:
        # No locking - just yield
        yield


# ====================================================================
# ATOMIC FILE OPERATIONS
# ====================================================================


def _atomic_write(path: Path, data: dict[str, Any], retries: int = MAX_RETRIES) -> bool:
    """Write data to file atomically.

    Writes to a temporary file first, then uses os.replace() for atomic swap.
    This prevents corruption if the app crashes or is restarted mid-write.

    Args:
        path: Target file path
        data: Data to write (must be JSON-serializable)
        retries: Number of retry attempts

    Returns:
        True if successful, False otherwise
    """
    tmp_path = path.with_suffix(".tmp")

    for attempt in range(retries):
        try:
            # Write to temporary file
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Atomic replace
            os.replace(str(tmp_path), str(path))
            return True

        except Exception as e:
            print(f"[ERROR] Atomic write failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
            else:
                # Clean up temp file on final failure
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except OSError:
                        pass
                return False

    return False


def _safe_read(path: Path) -> Optional[Dict[str, Any]]:
    """Read JSON file safely with error handling.

    If file is corrupted or doesn't exist, returns None.
    Corrupted files are automatically deleted to prevent crash loops.

    Args:
        path: File path to read

    Returns:
        Parsed JSON data or None if error
    """
    if not path.exists():
        return None

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Corrupted JSON file {path}: {e}")
        print(f"[INFO] Deleting corrupted file: {path}")
        try:
            path.unlink()
        except OSError:
            pass
        return None
    except Exception as e:
        print(f"[ERROR] Failed to read {path}: {e}")
        return None


# ====================================================================
# SESSION MANAGEMENT (Browser-specific, temporary)
# ====================================================================


def generate_session_id() -> str:
    """Generate a unique session ID.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def get_session_path(session_id: str) -> Path:
    """Get path to session file.

    Args:
        session_id: Session identifier

    Returns:
        Path to session JSON file
    """
    filename = SESSION_FILE_PATTERN.format(session_id=session_id)
    return CACHE_DIR / filename


def load_session(session_id: str) -> dict[str, Any]:
    """Load session data from disk.

    Session data includes:
    - current_route: Current page route
    - temp_data: Temporary working data (forms, in-progress assessments)
    - last_accessed: Timestamp of last access

    Args:
        session_id: Session identifier

    Returns:
        Session data dict (empty if not found or corrupted)
    """
    path = get_session_path(session_id)

    with _file_lock(path):
        data = _safe_read(path)

    if data is None:
        # Return default empty session
        return {
            "session_id": session_id,
            "created_at": time.time(),
            "last_accessed": time.time(),
            "current_route": None,
            "temp_data": {},
        }

    # Update last accessed timestamp
    data["last_accessed"] = time.time()
    return data


def save_session(session_id: str, data: dict[str, Any]) -> bool:
    """Save session data to disk atomically.

    Args:
        session_id: Session identifier
        data: Session data to save

    Returns:
        True if successful, False otherwise
    """
    path = get_session_path(session_id)

    # Update metadata
    data["session_id"] = session_id
    data["last_accessed"] = time.time()
    if "created_at" not in data:
        data["created_at"] = time.time()

    with _file_lock(path):
        return _atomic_write(path, data)


def clear_session(session_id: str) -> bool:
    """Delete session file.

    Use when user logs out or explicitly clears session.

    Args:
        session_id: Session identifier

    Returns:
        True if deleted, False if error
    """
    path = get_session_path(session_id)

    try:
        if path.exists():
            path.unlink()
        return True
    except OSError as e:
        print(f"[ERROR] Failed to delete session {session_id}: {e}")
        return False


def cleanup_old_sessions(max_age_days: int = 7) -> int:
    """Delete session files older than max_age_days.

    Args:
        max_age_days: Maximum age in days

    Returns:
        Number of sessions deleted
    """
    cutoff = time.time() - (max_age_days * 86400)
    deleted = 0

    for path in CACHE_DIR.glob("session_*.json"):
        try:
            # Check last modified time
            if path.stat().st_mtime < cutoff:
                path.unlink()
                deleted += 1
        except OSError:
            pass

    return deleted


# ====================================================================
# USER MANAGEMENT (Persistent, cross-device)
# ====================================================================


def is_demo_user(uid: str) -> bool:
    """Check if user ID is a demo user.
    
    Demo users have UIDs starting with 'demo_'.
    
    Args:
        uid: User identifier
        
    Returns:
        True if demo user, False otherwise
    """
    return uid.startswith("demo_")


def get_demo_path(uid: str) -> Path:
    """Get path to demo profile file (read-only source).
    
    Args:
        uid: User identifier
        
    Returns:
        Path to demo profile JSON file
    """
    filename = USER_FILE_PATTERN.format(uid=uid)
    return DEMO_DIR / filename


def get_user_path(uid: str) -> Path:
    """Get path to user profile file.

    Args:
        uid: User identifier

    Returns:
        Path to user JSON file
    """
    filename = USER_FILE_PATTERN.format(uid=uid)
    return DATA_DIR / filename


def load_user(uid: str) -> dict[str, Any]:
    """Load user profile and progress from disk.
    
    For demo users (UIDs starting with 'demo_'):
    - First checks if demo profile exists in data/users/demo/
    - If found, copies it to data/users/ for this session (fresh slate)
    - If working copy exists in data/users/, uses that instead
    - Demo profile in demo/ directory is never modified (protected)
    
    For regular users:
    - Loads from data/users/ as normal

    User data includes:
    - profile: Name, age, location, etc.
    - progress: Product completion status
    - mcip: MCIP contracts (care recommendation, financial profile, etc.)
    - preferences: User settings

    Args:
        uid: User identifier

    Returns:
        User data dict (empty default if not found)
    """
    path = get_user_path(uid)
    
    # Check if this is a demo user
    if is_demo_user(uid):
        demo_path = get_demo_path(uid)
        
        # Always refresh working copy from demo source if it exists
        # This ensures demo users always start with clean, complete data
        if demo_path.exists():
            try:
                import shutil
                # Force overwrite even if working copy exists
                shutil.copy2(demo_path, path)
            except Exception as e:
                print(f"[ERROR] Failed to copy demo profile: {e}")

    with _file_lock(path):
        data = _safe_read(path)

    if data is None:
        # Return default empty user
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

    return data
    data["uid"] = uid
    data["last_updated"] = time.time()
    return data


def save_user(uid: str, data: dict[str, Any]) -> bool:
    """Save user profile and progress to disk atomically.

    Args:
        uid: User identifier
        data: User data to save

    Returns:
        True if successful, False otherwise
    """
    path = get_user_path(uid)

    # Update metadata
    data["uid"] = uid
    data["last_updated"] = time.time()
    if "created_at" not in data:
        data["created_at"] = time.time()

    with _file_lock(path):
        return _atomic_write(path, data)


def delete_user(uid: str) -> bool:
    """Delete user profile file.

    Use when user requests account deletion.

    Args:
        uid: User identifier

    Returns:
        True if deleted, False if error
    """
    path = get_user_path(uid)

    try:
        if path.exists():
            path.unlink()
        return True
    except OSError as e:
        print(f"[ERROR] Failed to delete user {uid}: {e}")
        return False


def user_exists(uid: str) -> bool:
    """Check if user profile file exists.

    Args:
        uid: User identifier

    Returns:
        True if user file exists
    """
    return get_user_path(uid).exists()


def reset_demo_user(uid: str) -> bool:
    """Reset a demo user back to the original demo profile.
    
    This deletes the working copy in data/users/ so the next load
    will copy a fresh version from data/users/demo/.
    
    Only works for demo users (UIDs starting with 'demo_').
    
    Args:
        uid: User identifier
        
    Returns:
        True if reset successful, False otherwise
    """
    if not is_demo_user(uid):
        print(f"[ERROR] Cannot reset non-demo user: {uid}")
        return False
    
    demo_path = get_demo_path(uid)
    if not demo_path.exists():
        print(f"[ERROR] Demo profile not found: {demo_path}")
        return False
    
    user_path = get_user_path(uid)
    if user_path.exists():
        try:
            user_path.unlink()
            print(f"[INFO] Reset demo user: {uid}")
            return True
        except OSError as e:
            print(f"[ERROR] Failed to delete user copy: {e}")
            return False
    else:
        print(f"[INFO] Demo user already at clean state: {uid}")
        return True


# ====================================================================
# SESSION ↔ STATE MAPPING
# ====================================================================

# Keys to persist in session file (browser-specific, temporary)
SESSION_PERSIST_KEYS = {
    "current_route",
    "temp_form_data",
    "wizard_step",
    "last_error",
}

# Keys to persist in user file (cross-device, permanent)
USER_PERSIST_KEYS = {
    "profile",
    "progress",
    "mcip_contracts",  # MCIP contracts (care_recommendation, financial_profile, etc.)
    # Note: 'mcip' itself is NOT persisted - MCIP.initialize() reconstructs
    # the full state structure and journey tracking from contracts + progress
    "tiles",
    "product_tiles_v2",  # New tile system (includes trivia badges, etc.)
    "preferences",
    "auth",
    "flags",
    # Cost Planner v2 state keys
    "cost_v2_step",
    "cost_v2_guest_mode",
    "cost_v2_triage",
    "cost_v2_qualifiers",
    "cost_v2_current_module",
    "cost_v2_modules",  # Main assessment data
    "cost_v2_advisor_notes",
    "cost_v2_schedule_advisor",
    "cost_v2_quick_estimate",
    "cost_planner_v2_published",
    "cost_planner_v2_complete",
    # Cost Planner v2 assessment state keys (CORRECTED naming)
    "cost_planner_v2_income",  # Income assessment state
    "cost_planner_v2_assets",  # Assets assessment state
    "cost_planner_v2_va_benefits",  # VA benefits assessment state
    "cost_planner_v2_health_insurance",  # Health insurance assessment state
    "cost_planner_v2_life_insurance",  # Life insurance assessment state
    "cost_planner_v2_medicaid_navigation",  # Medicaid navigation assessment state
    # GCP v4 answer data
    "gcp_care_recommendation",  # All GCP assessment answers
    "gcp_v4_published",
    "gcp_v4_complete",
}


def extract_session_state(full_state: dict[str, Any]) -> dict[str, Any]:
    """Extract session-relevant keys from full state.

    Args:
        full_state: Full st.session_state dict

    Returns:
        Filtered dict with only session-relevant keys
    """
    session_data = {}

    for key in SESSION_PERSIST_KEYS:
        if key in full_state:
            session_data[key] = full_state[key]

    return session_data


def extract_user_state(full_state: dict[str, Any]) -> dict[str, Any]:
    """Extract user-relevant keys from full state.

    Args:
        full_state: Full st.session_state dict

    Returns:
        Filtered dict with only user-relevant keys
    """
    user_data = {}

    for key in USER_PERSIST_KEYS:
        if key in full_state:
            user_data[key] = full_state[key]

    return user_data


def merge_into_state(state: dict[str, Any], loaded_data: dict[str, Any]) -> None:
    """Merge loaded data into st.session_state.

    Args:
        state: st.session_state dict to update
        loaded_data: Data to merge in
    """
    for key, value in loaded_data.items():
        if key not in ["uid", "session_id", "created_at", "last_updated", "last_accessed"]:
            state[key] = value


# ====================================================================
# IDENTITY MANAGEMENT
# ====================================================================


def get_or_create_user_id(state: dict[str, Any]) -> str:
    """Get or create a user ID from session state.

    Priority:
    1. Authenticated user ID (from auth system)
    2. Anonymous user ID (generated UUID, stored in session)

    Args:
        state: st.session_state dict

    Returns:
        User ID string
    """
    # Check for authenticated user
    auth = state.get("auth", {})
    if auth.get("is_authenticated") and auth.get("user_id"):
        return auth["user_id"]

    # Check for anonymous user ID in session
    if "anonymous_uid" in state:
        return state["anonymous_uid"]

    # Generate new anonymous ID
    anonymous_uid = f"anon_{uuid.uuid4().hex[:12]}"
    state["anonymous_uid"] = anonymous_uid
    return anonymous_uid


def switch_user(state: dict[str, Any], new_uid: str) -> None:
    """Switch to a different user.

    Clears current session data and loads new user's data.
    Use when user logs in/out or switches accounts.

    Args:
        state: st.session_state dict
        new_uid: New user identifier
    """
    # Clear session-specific data to prevent bleed
    for key in list(state.keys()):
        if key in SESSION_PERSIST_KEYS:
            del state[key]

    # Update user ID
    if new_uid.startswith("anon_"):
        state["anonymous_uid"] = new_uid
        if "auth" in state:
            state["auth"]["is_authenticated"] = False
    else:
        state["auth"] = state.get("auth", {})
        state["auth"]["user_id"] = new_uid
        state["auth"]["is_authenticated"] = True

    # Load new user's data
    user_data = load_user(new_uid)
    merge_into_state(state, user_data)


# ====================================================================
# PUBLIC API
# ====================================================================


def safe_rerun():
    """
    Save session state before rerunning to prevent data loss.

    ALWAYS use this instead of st.rerun() to ensure persistence works correctly.

    Streamlit's st.rerun() clears session_state changes made during the render,
    so we must save to disk before rerunning.
    """
    import streamlit as st

    # Check if we should skip saving (e.g., on first render after loading data)
    should_skip_save = st.session_state.get("skip_save_this_render", False)
    
    if not should_skip_save:
        # Save user data (persistent across sessions)
        uid = get_or_create_user_id(st.session_state)
        user_data = extract_user_state(st.session_state)
        if user_data:
            save_user(uid, user_data)

        # Save session data (browser-specific, temporary)
        if "session_id" in st.session_state:
            session_data = extract_session_state(st.session_state)
            if session_data:
                save_session(st.session_state["session_id"], session_data)
    else:
        # Clear the flag so next rerun will save normally
        st.session_state["skip_save_this_render"] = False

    # Now safe to rerun
    st.rerun()


__all__ = [
    # Session operations
    "generate_session_id",
    "load_session",
    "save_session",
    "clear_session",
    "cleanup_old_sessions",
    # User operations
    "load_user",
    "save_user",
    "delete_user",
    "user_exists",
    # State mapping
    "extract_session_state",
    "extract_user_state",
    "merge_into_state",
    # Identity
    "get_or_create_user_id",
    "switch_user",
    # Rerun helper
    "safe_rerun",
]
