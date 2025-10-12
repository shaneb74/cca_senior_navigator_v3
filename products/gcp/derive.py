from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from core.modules.schema import OutcomeContract

from .flags_v1 import compute_flags
from .recommend_v1 import recommend_tier

VALUE_ALIASES: Dict[str, Dict[str, str]] = {
    "help_overall": {
        "none": "None – fully independent",
        "occasional": "Occasional – some help with a few tasks",
        "regular": "Regular – needs daily assistance",
        "extensive": "Extensive – needs full-time support",
    },
    "hours_per_day": {
        "lt1": "Less than 1 hour",
        "1_3": "1–3 hours",
        "4_8": "4–8 hours",
        "24h": "24-hour support",
    },
    "primary_support": {
        "family": "Family/friends",
        "paid": "Paid caregiver",
        "agency": "Community or agency",
        "none": "No regular support",
    },
    "memory_changes": {
        "none": "No concerns",
        "occasional": "Occasional forgetfulness",
        "moderate": "Moderate memory or thinking issues",
        "severe": "Severe memory issues or diagnosis like dementia or Alzheimer's",
    },
    "meds_complexity": {
        "none": "None",
        "simple": "Simple – a few meds",
        "moderate": "Moderate – daily meds, some complexity",
        "complex": "Complex – many meds or caregiver-managed",
    },
    "mobility": {
        "independent": "Walks independently",
        "device": "Uses cane or walker",
        "wheelchair": "Uses wheelchair or scooter",
        "bedbound": "Bed-bound or limited mobility",
    },
    "falls": {
        "none_6m": "No falls in past six months",
        "one": "One fall",
        "multiple": "Multiple falls",
    },
    "isolation": {
        "no": "No – easily accessible",
        "somewhat": "Somewhat isolated",
        "very": "Very isolated",
    },
}


def derive_outcomes_v1(answers: Dict[str, Any], context: Dict[str, Any]) -> OutcomeContract:
    scores = _score_domains(answers)
    flags, tags = compute_flags(answers)
    recommendation = recommend_tier(answers, flags)

    oc = OutcomeContract()
    oc.recommendation = recommendation
    oc.confidence = 0.7
    oc.flags = flags
    oc.tags = tags
    oc.domain_scores = scores

    name = context.get("person_a_name", "this person")
    bullets = _build_bullets(scores, name)
    oc.summary = {
        "bullets": bullets,
        "wrap_up": f"Based on your answers, {name} may be best served by {recommendation.replace('_', ' ').title()}.",
    }

    oc.routing = {
        "next": "cost_planner",
        "recommended_modules": _suggest_modules(recommendation, flags),
    }

    return oc


def _score_domains(answers: Dict[str, Any]) -> Dict[str, int]:
    scores = {
        "adl_iadl_burden": 0,
        "support_network": 0,
        "cognitive_function": 0,
        "meds_complexity": 0,
        "mobility_falls": 0,
        "chronic_health": 0,
        "geographic_isolation": 0,
    }

    for rule in _load_scoring_rules():
        domain = rule["domain"]
        key = rule["key"]
        match = rule["value_match"]
        raw_score = rule["score"]
        current = int(scores.get(domain, 0))

        normalized = match.replace(" ", "").lower()
        if normalized.startswith("count>="):
            threshold = int(normalized.split(">=")[1])
            count = _count_conditions(answers, key)
            if count >= threshold:
                scores[domain] = _clamp_score(max(current, int(raw_score)))
            continue

        if normalized == "anyselected":
            increment = _parse_increment(raw_score)
            if increment and current >= 2 and _has_behaviors(answers):
                scores[domain] = _clamp_score(current + increment)
            continue

        value = _canonical_value(key, answers.get(key))
        if isinstance(value, str):
            candidate = value.strip()
        else:
            candidate = value

        if isinstance(candidate, str) and candidate == match:
            scores[domain] = _clamp_score(max(current, int(raw_score)))

    return scores


def _count_conditions(answers: Dict[str, Any], key: str) -> int:
    values = answers.get(key)
    count = 0
    if isinstance(values, (list, tuple, set)):
        count = len(
            [str(v) for v in values if str(v).strip() and str(v).lower() != "none of these"]
        )
    elif values:
        count = 1
    additional = answers.get("additional_conditions")
    if isinstance(additional, str) and additional.strip():
        count += 1
    return count


def _has_behaviors(answers: Dict[str, Any]) -> bool:
    behaviors = answers.get("behaviors")
    if not behaviors:
        return False
    if isinstance(behaviors, str):
        normalized = behaviors.strip().lower()
        return bool(normalized) and normalized not in {"none", "none of these"}
    return any(
        str(b).strip() and str(b).strip().lower() not in {"none", "none of these"}
        for b in behaviors
    )


def _build_bullets(scores: Dict[str, int], name: str) -> List[str]:
    blurbs = _load_blurbs()
    ordered_domains = [
        "adl_iadl_burden",
        "support_network",
        "cognitive_function",
        "meds_complexity",
        "mobility_falls",
        "chronic_health",
        "geographic_isolation",
    ]
    bullets: List[str] = []
    for domain in ordered_domains:
        score = scores.get(domain, 0)
        text = _choose_blurb(blurbs.get(domain, {}), score)
        if text:
            bullets.append(text.format(name=name))
    return bullets


def _choose_blurb(mapping: Dict[int, str], score: int) -> str:
    if not mapping:
        return ""
    if score in mapping:
        return mapping[score]
    candidates = [mapping[s] for s in sorted(mapping.keys()) if s <= score]
    if candidates:
        return candidates[-1]
    return mapping.get(min(mapping.keys()), "")


def _suggest_modules(recommendation: str, flags: Dict[str, bool]) -> List[str]:
    modules: List[str] = []
    if recommendation in ("in_home", "stay_home") or flags.get("mobility_issue"):
        modules.append("home_mods")
    if flags.get("meds_management_needed"):
        modules.append("meds_costs")
    if flags.get("emotional_followup"):
        modules.append("caregiver_support")
    else:
        modules.append("caregiver_support")
    return modules


@lru_cache(maxsize=1)
def _load_scoring_rules() -> List[Dict[str, str]]:
    path = Path(__file__).with_name("scoring_v1.csv")
    with path.open() as fh:
        reader = csv.DictReader(fh)
        return [row for row in reader]


@lru_cache(maxsize=1)
def _load_blurbs() -> Dict[str, Dict[int, str]]:
    path = Path(__file__).with_name("blurbs_v1.csv")
    mapping: Dict[str, Dict[int, str]] = {}
    with path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            domain = row["domain"]
            rank = int(row["rank"])
            mapping.setdefault(domain, {})[rank] = row["blurb"].strip()
    return mapping


def _parse_increment(raw_value: str) -> int:
    digits = "".join(ch for ch in str(raw_value) if ch.isdigit())
    return int(digits) if digits else 0


def _clamp_score(value: int) -> int:
    return max(0, min(3, int(value)))


def _canonical_value(key: str, value: Any) -> Any:
    mapping = VALUE_ALIASES.get(key)
    if mapping and isinstance(value, str):
        return mapping.get(value, value)
    return value


__all__ = ["derive_outcomes_v1"]
