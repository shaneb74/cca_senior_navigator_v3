"""
Lightweight performance tracing for Senior Navigator.

Enable with PERF_TRACE=1 (default on for dev).
Set PERF_THRESH_MS to control logging threshold (default: 25ms).
"""

import contextlib
import os
import time

# Enable with PERF_TRACE=1 (default on for dev). Set PERF_THRESH_MS to control logging threshold.
PERF_ON = os.getenv("PERF_TRACE", "1") == "1"
THRESH_MS = float(os.getenv("PERF_THRESH_MS", "25"))  # log blocks > 25 ms by default


@contextlib.contextmanager
def perf(tag: str):
    """Context manager for performance timing.
    
    Usage:
        with perf("operation_name"):
            expensive_operation()
    
    Logs if operation exceeds PERF_THRESH_MS milliseconds.
    """
    if not PERF_ON:
        yield
        return
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = (time.perf_counter() - t0) * 1000.0
        if dt >= THRESH_MS:
            print(f"[PERF] {tag} {dt:.1f} ms")
