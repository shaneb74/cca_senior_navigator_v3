"""
Lightweight debug helpers for gating noisy logs and training traces.

Priority for toggles: Streamlit secrets → environment variables → default.

Toggles:
- DEBUG_NAVI: Controls verbose diagnostics. Values: on|off (default: off)
- FEATURE_TRAIN_LOG_ALL: If on, logs alignments too (not just disagreements).
"""

from __future__ import annotations

import os
from typing import Optional


def _get_secret(name: str) -> Optional[str]:
    """Best-effort read from Streamlit secrets without import-time failure."""
    try:
        import streamlit as st
        v = st.secrets.get(name)
        if v is None:
            return None
        return str(v)
    except Exception:
        return None


def _on(val: Optional[str]) -> bool:
    if val is None:
        return False
    return str(val).strip().strip('"').lower() in {"on", "true", "1", "yes"}


def debug_enabled() -> bool:
    """Return True if DEBUG_NAVI is enabled via secrets or env."""
    v = _get_secret("DEBUG_NAVI")
    if v is not None:
        return _on(v)
    return _on(os.getenv("DEBUG_NAVI"))


def train_log_all() -> bool:
    """Return True if FEATURE_TRAIN_LOG_ALL is enabled.

    When enabled, we log both alignments and disagreements; otherwise we
    log only disagreements to keep noise low.
    """
    v = _get_secret("FEATURE_TRAIN_LOG_ALL")
    if v is not None:
        return _on(v)
    return _on(os.getenv("FEATURE_TRAIN_LOG_ALL"))


__all__ = [
    "debug_enabled",
    "train_log_all",
]
