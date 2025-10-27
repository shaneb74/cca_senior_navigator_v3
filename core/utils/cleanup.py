"""
Throttled file cleanup for Senior Navigator.

Prevents per-rerun cleanup spam by enforcing a global throttle.
Only runs on explicit navigation or after timeout interval.
"""

import logging
import os
import time

log = logging.getLogger("app")

# Global state (module-level to persist across Streamlit reruns)
_CLEANUP_INTERVAL_S = int(os.getenv("CLEANUP_INTERVAL_S", "60"))
_last_cleanup_ts = 0.0


def maybe_cleanup_files(force: bool = False) -> None:
    """Run expensive cleanup at most once per minute, or when forced on navigation.
    
    Global throttle prevents per-rerun spam while ensuring orphans are removed periodically.
    
    Args:
        force: If True, run immediately regardless of throttle (used for navigation)
    
    Usage:
        # In navigation/CTA handlers only:
        maybe_cleanup_files(force=True)
        
        # Optional: Add heartbeat at end of render (will throttle):
        maybe_cleanup_files(force=False)
    """
    global _last_cleanup_ts
    
    now = time.time()
    
    # Check throttle (skip if not forced and interval not elapsed)
    if not force and (now - _last_cleanup_ts) < _CLEANUP_INTERVAL_S:
        return
    
    log.info("[CLEANUP] running")
    
    try:
        # Import cleanup function lazily to avoid circular dependencies
        from core.session_store import cleanup_orphaned_user_files
        cleanup_orphaned_user_files()
    except ImportError:
        log.warning("[CLEANUP] cleanup_orphaned_user_files not available")
    except Exception as e:
        log.error(f"[CLEANUP] failed: {e}")
    finally:
        _last_cleanup_ts = now
