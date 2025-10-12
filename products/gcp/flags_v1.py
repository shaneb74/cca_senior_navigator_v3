from __future__ import annotations

from typing import Any, Dict, List, Tuple


def compute_flags(answers: Dict[str, Any]) -> Tuple[Dict[str, bool], List[str]]:
    flags: Dict[str, bool] = {
        "mobility_issue": False,
        "fall_risk": False,
        "meds_management_needed": False,
        "cognitive_risk": False,
        "emotional_followup": False,
        "isolation_high": False,
    }
    tags: List[str] = []

    mobility = (answers.get("mobility") or "").strip().lower()
    if "wheel" in mobility or "scooter" in mobility:
        flags["mobility_issue"] = True
        tags.append("mobility:wheelchair")
    elif "bed" in mobility:
        flags["mobility_issue"] = True
        tags.append("mobility:bedbound")

    falls = (answers.get("falls") or "").strip().lower()
    if falls.startswith("multiple"):
        flags["fall_risk"] = True
        tags.append("fall:multiple")

    meds = (answers.get("meds_complexity") or "").strip().lower()
    if "moderate" in meds:
        flags["meds_management_needed"] = True
        tags.append("meds:moderate")
    elif "complex" in meds:
        flags["meds_management_needed"] = True
        tags.append("meds:complex")

    cognition = (answers.get("memory_changes") or "").strip().lower()
    if "moderate" in cognition:
        flags["cognitive_risk"] = True
        tags.append("cognition:moderate")
    elif "severe" in cognition or "dementia" in cognition or "alzheimer" in cognition:
        flags["cognitive_risk"] = True
        tags.append("cognition:severe")

    mood = (answers.get("mood") or "").strip().lower()
    if mood.startswith("low"):
        flags["emotional_followup"] = True
        tags.append("mood:low")

    isolation = (answers.get("isolation") or "").strip().lower()
    if isolation.startswith("very"):
        flags["isolation_high"] = True
        tags.append("isolation:high")

    return flags, tags


__all__ = ["compute_flags"]
