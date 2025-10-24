"""
Hours suggestion disagreement logger.

Appends hours cases to data/training/hours_cases.jsonl for offline analysis.
Captures user selection vs baseline vs LLM suggestion for training data.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def log_hours_case(
    context: Any,
    base_band: str,
    llm_band: str | None,
    llm_conf: float | None,
    mode: str
) -> None:
    """Log a hours suggestion case for offline analysis.
    
    Appends a single row to data/training/hours_cases.jsonl with:
    - All context signals (badls_count, iadls_count, falls, mobility, etc.)
    - User's current selection (if any)
    - Baseline suggestion
    - LLM suggestion (if available)
    - Confidence score
    - Timestamp
    
    Args:
        context: HoursContext instance with all input signals
        base_band: Baseline suggestion (e.g., "4-8h")
        llm_band: LLM suggestion (e.g., "1-3h") or None if failed
        llm_conf: LLM confidence score (0.0-1.0) or None
        mode: Feature mode ("shadow" or "assist")
    """
    try:
        # Ensure data/training directory exists
        log_dir = Path(__file__).parent.parent / "data" / "training"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "hours_cases.jsonl"

        # Build row dict (extract fields from HoursContext)
        row = {
            "ts": datetime.utcnow().isoformat(),
            "mode": mode,
            "badls_count": getattr(context, "badls_count", 0),
            "iadls_count": getattr(context, "iadls_count", 0),
            "falls": getattr(context, "falls", None),
            "mobility": getattr(context, "mobility", None),
            "risky_behaviors": getattr(context, "risky_behaviors", False),
            "meds_complexity": getattr(context, "meds_complexity", None),
            "primary_support": getattr(context, "primary_support", None),
            "overnight_needed": getattr(context, "overnight_needed", False),
            "user_band": getattr(context, "current_hours", None),
            "base_band": base_band,
            "llm_band": llm_band,
            "llm_conf": llm_conf,
        }

        # Append to JSONL
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    except Exception as e:
        # Never fail the main flow - just log error
        print(f"[HOURS_LOG_ERROR] Failed to log hours case: {e}")
