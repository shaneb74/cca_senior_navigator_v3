"""Lightweight logging helpers with feature flag gating."""

from __future__ import annotations


def get_flag(name: str, default: str = "off") -> str:
    """Get flag from secrets first, then env, with stripped quotes."""
    import os
    try:
        import streamlit as st
        s = getattr(st, "secrets", None)
        if s:
            v = s.get(name)
            if v is not None:
                return str(v).strip().strip('"').lower()
    except Exception:
        pass
    return str(os.getenv(name, default)).strip().strip('"').lower()


def get_logger(name: str = "app"):
    """Get logger with level gated by DEBUG_FILES or DEBUG_NAVI flags."""
    import logging
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
        h.setFormatter(fmt)
        logger.addHandler(h)
    debug_on = get_flag("DEBUG_FILES", "off") in {"on", "true", "1", "yes"} or \
               get_flag("DEBUG_NAVI", "off") in {"on", "true", "1", "yes"}
    logger.setLevel(logging.DEBUG if debug_on else logging.WARNING)
    return logger
