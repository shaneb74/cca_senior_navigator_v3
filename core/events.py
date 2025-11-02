from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from datetime import datetime


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


def log_event(event: str, data: Mapping[str, Any] | None = None) -> None:
    """Best-effort event logger: gated prints, small rolling buffer, disk persistence."""
    try:
        import json
        import time
        import os

        DEBUG_EVENTS = (_get_flag("DEBUG_EVENTS", "off") in {"on", "true", "1", "yes"})
        BUFFER_ON = (_get_flag("EVENT_BUFFER", "on") in {"on", "true", "1", "yes"})
        MAX_BUF = int((_get_flag("EVENT_BUFFER_MAX", "500")) or "500")
        FILE_LOG = (_get_flag("EVENT_FILE_LOG", "on") in {"on", "true", "1", "yes"})
        LOG_PATH = os.getenv("APP_EVENT_LOG", "data/events.log")

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

        # Write to disk log (for admin metrics)
        if FILE_LOG:
            try:
                os.makedirs(os.path.dirname(LOG_PATH) or ".", exist_ok=True)
                with open(LOG_PATH, "a") as f:
                    f.write(json.dumps(payload, default=str) + "\n")
            except Exception as e_file:
                if DEBUG_EVENTS:
                    print(f"[EVENT_FILE_WARN] {event}: {e_file}")
    except Exception as e:
        try:
            print(f"[EVENT_WARN] {event}: {e}")
        except Exception:
            pass


def mark_product_complete(user_ctx: dict, product_key: str) -> dict:
    """DEPRECATED: Use MCIP.mark_product_complete() instead.
    
    This function is maintained for backward compatibility only.
    All new code should use core.mcip.MCIP.mark_product_complete().
    
    Legacy function that marks a product complete in user_ctx structure.
    
    Args:
        user_ctx: User context dictionary (legacy)
        product_key: Product identifier
    
    Returns:
        Updated user context
        
    Migration:
        # Old way (deprecated)
        from core.events import mark_product_complete
        user_ctx = mark_product_complete(user_ctx, "gcp_v4")
        st.session_state["user_ctx"] = user_ctx
        
        # New way (correct)
        from core.mcip import MCIP
        MCIP.mark_product_complete("gcp")
    
    Note:
        Phase Post-CSS: This was the original completion consolidation logic.
        Now superseded by MCIP coordination system.
    """
    import warnings
    warnings.warn(
        "mark_product_complete() is deprecated. Use MCIP.mark_product_complete() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Keep original implementation for backward compatibility
    journeys = user_ctx.setdefault("journeys", {})

    for journey_key, journey_data in journeys.items():
        products = journey_data.get("products", {})
        if product_key in products:
            products[product_key]["completed"] = True
            journey_data["updated_at"] = datetime.utcnow().isoformat()

            # If all products are now complete, mark journey complete
            if all(p.get("completed") for p in products.values()):
                journey_data["completed"] = True
                journey_data["status"] = "completed"
            break

    return user_ctx

