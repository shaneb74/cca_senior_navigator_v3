from __future__ import annotations

from typing import Any, Mapping, Optional


def _get_flag(name: str, default: str = "off") -> str:
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


def log_event(event: str, data: Optional[Mapping[str, Any]] = None) -> None:
    """Best-effort event logger: gated prints, small rolling buffer."""
    try:
        import json
        import time
        
        DEBUG_EVENTS = (_get_flag("DEBUG_EVENTS", "off") in {"on", "true", "1", "yes"})
        BUFFER_ON = (_get_flag("EVENT_BUFFER", "on") in {"on", "true", "1", "yes"})
        MAX_BUF = int((_get_flag("EVENT_BUFFER_MAX", "500")) or "500")

        payload = {
            "ts": int(time.time()),
            "event": event,
            "data": dict(data) if data else {},
        }
        
        # Only print when explicitly enabled
        if DEBUG_EVENTS:
            print(f"[EVENT] {json.dumps(payload, default=str)}")

        # Optional rolling buffer in session_state
        if BUFFER_ON:
            try:
                import streamlit as st
                buf = st.session_state.setdefault("_events", [])
                buf.append(payload)
                if MAX_BUF and len(buf) > MAX_BUF:
                    del buf[:-MAX_BUF // 2]  # trim to half
            except Exception:
                pass
    except Exception as e:
        try:
            print(f"[EVENT_WARN] {event}: {e}")
        except Exception:
            pass
