"""User persistence layer - append-only snapshots to disk.

Writes CarePlan and CostPlan snapshots to data/users/{user_id}/ for:
- Training data collection
- User history tracking
- Debugging flow issues

All writes are best-effort and non-blocking (never crash the app).
"""

import datetime as dt
import json
import os
from typing import Any

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def get_current_user_id() -> str:
    """Get current user ID from session state.
    
    Returns:
        User ID string, or 'anon_default' if not available
    
    Note: Uses session_store.get_or_create_user_id() for consistency
    with app.py initialization. Priority:
    1. Authenticated user ID (auth.user_id)
    2. Anonymous user ID (anonymous_uid)
    3. Fallback to 'anon_default'
    """
    if not (HAS_STREAMLIT and hasattr(st, "session_state")):
        return "anon_default"

    # Check for authenticated user
    auth = st.session_state.get("auth", {})
    if auth.get("is_authenticated") and auth.get("user_id"):
        return auth["user_id"]

    # Check for anonymous user ID
    if "anonymous_uid" in st.session_state:
        return st.session_state["anonymous_uid"]

    return "anon_default"


def _user_dir(user_id: str) -> str:
    """Get or create user data directory.
    
    Args:
        user_id: User identifier
        
    Returns:
        Absolute path to user directory
    """
    base = os.path.join("data", "users", user_id)
    os.makedirs(base, exist_ok=True)
    return base


def _write_json(user_id: str, subdir: str, payload: dict[str, Any]) -> str | None:
    """Write JSON payload to timestamped file.
    
    Args:
        user_id: User identifier
        subdir: Subdirectory (careplan, costplan)
        payload: Data to write
        
    Returns:
        Path to written file, or None if failed
    """
    try:
        base = _user_dir(user_id)
        folder = os.path.join(base, subdir)
        os.makedirs(folder, exist_ok=True)

        ts = dt.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
        path = os.path.join(folder, f"{ts}_{subdir}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        print(f"[USER_PERSIST] wrote {path}")
        return path

    except Exception as e:
        print(f"[USER_PERSIST_ERR] Failed to write {subdir}: {e}")
        return None


def persist_careplan(user_id: str, payload: dict[str, Any]) -> None:
    """Persist CarePlan snapshot to disk.
    
    Non-blocking - will not raise exceptions.
    
    Args:
        user_id: User identifier
        payload: CarePlan data (published_tier, allowed_tiers, flags, etc.)
    """
    if not user_id:
        print("[USER_PERSIST_ERR] No user_id provided for careplan")
        return

    try:
        payload.setdefault("schema_version", 2)
        payload.setdefault("timestamp", dt.datetime.utcnow().isoformat() + "Z")
        _write_json(user_id, "careplan", payload)
    except Exception as e:
        print(f"[USER_PERSIST_ERR] persist_careplan failed: {e}")


def persist_costplan(user_id: str, payload: dict[str, Any]) -> None:
    """Persist CostPlan snapshot to disk.
    
    Non-blocking - will not raise exceptions.
    
    Args:
        user_id: User identifier  
        payload: CostPlan data (event, zip, assessment, totals, etc.)
    """
    if not user_id:
        print("[USER_PERSIST_ERR] No user_id provided for costplan")
        return

    try:
        payload.setdefault("schema_version", 2)
        payload.setdefault("timestamp", dt.datetime.utcnow().isoformat() + "Z")
        _write_json(user_id, "costplan", payload)
    except Exception as e:
        print(f"[USER_PERSIST_ERR] persist_costplan failed: {e}")
