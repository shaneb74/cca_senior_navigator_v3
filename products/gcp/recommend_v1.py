from __future__ import annotations

from typing import Any, Dict


def recommend_tier(answers: Dict[str, Any], flags: Dict[str, bool]) -> str:
    help_overall = (answers.get("help_overall") or "").strip().lower()
    hours = (answers.get("hours_per_day") or "").strip().lower()

    if flags.get("cognitive_risk"):
        return "memory_care"

    if "regular" in help_overall or "extensive" in help_overall or hours.startswith("24"):
        return "assisted_living"

    if flags.get("mobility_issue") or flags.get("meds_management_needed"):
        return "in_home"

    return "stay_home"


__all__ = ["recommend_tier"]
