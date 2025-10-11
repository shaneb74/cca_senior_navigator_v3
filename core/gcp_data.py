from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple


BASE = Path(__file__).resolve().parents[1] / "config" / "gcp"


def _load(name: str) -> dict:
    path = BASE / name
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing GCP config file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in GCP config file {path}: {exc}") from exc


@lru_cache(maxsize=None)
def load_schema() -> dict:
    path = Path(__file__).resolve().parents[1] / "config" / "gcp_schema.json"
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing GCP config file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in GCP config file {path}: {exc}") from exc


@lru_cache(maxsize=None)
def load_scoring() -> dict:
    return _load("scoring.json")


@lru_cache(maxsize=None)
def load_rules() -> dict:
    return _load("rules.json")


@lru_cache(maxsize=None)
def load_blurbs() -> dict:
    return _load("blurbs.json")


@lru_cache(maxsize=None)
def load_domains() -> dict:
    return _load("domains.json")


def _normalize_flag_tokens(raw: str) -> List[str]:
    if not raw:
        return []
    tokens = re.split(r"[,\s]+", raw.strip())
    return [tok for tok in tokens if tok]


def _match_from_mapping(question_text: str, answer_option: str, mapping: Mapping[str, Any]) -> bool:
    """
    Attempt to match a scoring row to an answer stored as a dict.

    The mapping may use any of the following key styles:
      * Full row question text (e.g., "BADLs — Bathing... assistance")
      * The trailing phrase after an em dash
      * The trailing phrase after a colon
      * For behavior rows ("Wandering — Present"), the portion before the dash
    """
    # Exact match on question text
    if question_text in mapping:
        return _value_matches(answer_option, mapping[question_text])

    variants: List[str] = []
    if "—" in question_text:
        variants.append(question_text.split("—", 1)[-1].strip())
    if ":" in question_text:
        variants.append(question_text.split(":", 1)[0].strip())
    if "—" in answer_option:
        variants.append(answer_option.split("—", 1)[0].strip())

    for key in variants:
        if key and key in mapping:
            if _value_matches(answer_option, mapping[key]):
                return True
    return False


def _value_matches(answer_option: str, value: Any) -> bool:
    """
    Evaluate whether a stored value represents the supplied answer option.
    """
    if isinstance(value, (list, tuple, set)):
        joined = {str(v).strip() for v in value}
        if answer_option in joined:
            return True
        # Allow matching on suffix (e.g., "Present")
        if "—" in answer_option:
            suffix = answer_option.split("—", 1)[1].strip().lower()
            return any(str(v).strip().lower() == suffix for v in value)
        return False

    if isinstance(value, dict):
        # Nested dictionaries (rare) -> recurse
        for sub in value.values():
            if _value_matches(answer_option, sub):
                return True
        return False

    if isinstance(value, bool):
        if "Present" in answer_option or "Yes" in answer_option:
            return bool(value)
        if "Not present" in answer_option or "No" in answer_option:
            return not value
        return False

    if isinstance(value, str):
        candidate = value.strip()
        if candidate == answer_option:
            return True
        if "—" in answer_option:
            suffix = answer_option.split("—", 1)[1].strip().lower()
            return candidate.lower() == suffix
        return candidate == answer_option

    return False


def _answer_matches(stored: Any, answer_option: str, question_text: str) -> bool:
    if stored is None:
        return False

    # Multi-select answers stored as iterable of options
    if isinstance(stored, (list, tuple, set)):
        values = {str(v) for v in stored}
        if answer_option in values:
            return True
        if "—" in answer_option:
            suffix = answer_option.split("—", 1)[1].strip().lower()
            return any(str(v).strip().lower() == suffix for v in stored)
        return False

    # Matrix answers stored as dicts
    if isinstance(stored, Mapping):
        return _match_from_mapping(question_text, answer_option, stored)

    # Scalar answers
    return _value_matches(answer_option, stored)


def _derive_counters(flags: Iterable[str]) -> Dict[str, int]:
    prefixes = {"chronic_present", "behavior_risk"}
    counters: Dict[str, int] = {}
    for flag in flags:
        for prefix in prefixes:
            if flag.startswith(prefix):
                counters[prefix] = counters.get(prefix, 0) + 1
    for prefix in prefixes:
        counters.setdefault(prefix, 0)
    return counters


def evaluate(answers: Dict[str, Any]) -> Dict[str, Any]:
    scoring_rows = load_scoring().get("scoring", [])
    domains_cfg = {d["id"]: d for d in load_domains().get("domains", [])}
    blurbs_payload = load_blurbs()
    system_cfg = blurbs_payload.get("system", {}) if isinstance(blurbs_payload, Mapping) else {}
    advisory_map = system_cfg.get("advisories", {}) if isinstance(system_cfg, Mapping) else {}

    domain_totals: Dict[str, float] = {}
    contributions: List[Tuple[str, str, str, float]] = []
    ordered_flags: List[str] = []
    seen_flags: set[str] = set()

    def _append_flag(flag: str) -> None:
        if flag not in seen_flags:
            seen_flags.add(flag)
            ordered_flags.append(flag)

    def _add(domain: str, value: float, weight_override: Any) -> float:
        weight = (
            float(weight_override)
            if weight_override is not None
            else float(domains_cfg.get(domain, {}).get("weightDefault", 1))
        )
        contribution = value * weight
        domain_totals[domain] = domain_totals.get(domain, 0.0) + contribution
        return contribution

    for row in scoring_rows:
        qid = row["QuestionID"]
        answer = answers.get(qid)
        if answer is None:
            continue

        if not _answer_matches(answer, row["AnswerOption"], row["Question"]):
            continue

        score_value = row.get("ScoreValue")
        contribution = 0.0
        if isinstance(score_value, (int, float)):
            contribution = _add(row["Domain"], float(score_value), row.get("DomainWeight"))
            if contribution != 0:
                contributions.append((qid, row["AnswerOption"], row["Domain"], contribution))

        for flag in _normalize_flag_tokens(row.get("FlagsEmitted", "")):
            _append_flag(flag)

    # Cap domains
    for domain, cfg in domains_cfg.items():
        cap = cfg.get("cap")
        if cap is not None and domain in domain_totals:
            domain_totals[domain] = min(domain_totals[domain], float(cap))

    counters = _derive_counters(ordered_flags)

    base_total = sum(domain_totals.values())
    if base_total >= 12:
        base_tier = 3
    elif base_total >= 6:
        base_tier = 2
    elif base_total >= 2:
        base_tier = 1
    else:
        base_tier = 0

    tier_index, rule_flags, rule_advisories = apply_rules(base_tier, ordered_flags, counters)
    for flag in rule_flags:
        _append_flag(flag)

    tier_map = {
        0: "In-Home Care",
        1: "In-Home Care",
        2: "Assisted Living",
        3: "Memory Care",
        4: "Memory Care High Acuity",
    }
    tier_name = tier_map.get(tier_index, "In-Home Care")

    drivers = sorted(contributions, key=lambda item: abs(item[3]), reverse=True)[:3]
    driver_payload = [(qid, answer, round(points, 2)) for qid, answer, _domain, points in drivers]

    advisories: List[str] = []
    for flag in ordered_flags:
        note = advisory_map.get(flag)
        if note and note not in advisories:
            advisories.append(note)
    for adv in rule_advisories:
        if adv and adv not in advisories:
            advisories.append(adv)

    return {
        "tier": tier_name,
        "scores": domain_totals,
        "flags": ordered_flags,
        "advisories": advisories,
        "drivers": driver_payload,
    }


def apply_rules(
    base_tier: int, flags: List[str], counters: Dict[str, int]
) -> Tuple[int, List[str], List[str]]:
    ruleset = load_rules()
    env = set(flags)
    emitted_flags: List[str] = []
    advisories: List[str] = []

    def _replace_counters(expr: str) -> str:
        def repl(match: re.Match[str]) -> str:
            key = match.group("key")
            op = match.group("op")
            value = int(match.group("value"))
            current = counters.get(key, 0)
            if op == ">=":
                return str(current >= value)
            if op == ">":
                return str(current > value)
            if op == "<=":
                return str(current <= value)
            if op == "<":
                return str(current < value)
            if op == "==":
                return str(current == value)
            return "False"

        pattern = r"(?P<key>[A-Za-z0-9_]+)\s*(?P<op>>=|>|<=|<|==)\s*(?P<value>\d+)"
        return re.sub(pattern, repl, expr)

    def _eval(expr: str) -> bool:
        expr = _replace_counters(expr)
        tokens = re.split(r"(\bAND\b|\bOR\b|\bNOT\b|\(|\))", expr)
        converted: List[str] = []
        for token in tokens:
            stripped = token.strip()
            if not stripped:
                continue
            if stripped in {"AND", "OR", "NOT"}:
                converted.append(stripped.lower())
            elif stripped in {"(", ")"}:
                converted.append(stripped)
            elif stripped in {"True", "False"}:
                converted.append(stripped)
            else:
                converted.append("True" if stripped in env else "False")
        safe_expr = " ".join(converted)
        if not safe_expr:
            return False
        return bool(eval(safe_expr))

    tier = base_tier
    for key in ruleset.get("order", []):
        rule = ruleset["rules"][key]
        condition = rule.get("when", "")
        if condition and not _eval(condition):
            continue
        kind = rule.get("kind")
        if kind == "override":
            tier = rule.get("setTier", tier)
        elif kind == "floor":
            tier = max(tier, rule.get("minTier", tier))
        elif kind == "modifier":
            tier += rule.get("delta", 0)
            if "minTier" in rule:
                tier = max(rule["minTier"], tier)
            if "maxTier" in rule:
                tier = min(rule["maxTier"], tier)
        for field in ("emit", "flags"):
            tokens = rule.get(field)
            if not tokens:
                continue
            if isinstance(tokens, str):
                tokens = [tokens]
            for token in tokens:
                if token and token not in emitted_flags:
                    emitted_flags.append(token)
        notes = rule.get("advisory") or rule.get("advisories") or []
        if isinstance(notes, str):
            notes = [notes]
        for note in notes:
            if note and note not in advisories:
                advisories.append(note)

    final_tier = max(0, min(4, tier))
    return final_tier, emitted_flags, advisories
