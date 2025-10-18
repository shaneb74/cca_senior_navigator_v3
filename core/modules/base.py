from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from core.modules.inputs import render_input
from core.modules.schema import validate_manifest


def load_module_manifest(product: str, module: str) -> dict[str, Any]:
    manifest_path = Path("products") / product / "modules" / module / "module.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_manifest(manifest)
        return manifest
    except Exception as exc:  # pragma: no cover - defensive UI layer
        st.error(
            "This module's configuration appears to be invalid. Please contact your admin.\n\n"
            f"Details: {exc}"
        )
        st.caption(str(manifest_path.resolve()))
        st.stop()


def _visible(question: dict[str, Any], answers: dict[str, Any]) -> bool:
    cond = question.get("visible_if")
    if not cond:
        return True

    def _check(rule: dict[str, Any]) -> bool:
        if "eq" in rule:
            key, value = rule["eq"]
            return answers.get(key) == value
        if "neq" in rule:
            key, value = rule["neq"]
            return answers.get(key) != value
        if "in" in rule:
            key, values = rule["in"]
            return answers.get(key) in (values or [])
        if "not_in" in rule:
            key, values = rule["not_in"]
            return answers.get(key) not in (values or [])
        if "lt" in rule:
            key, value = rule["lt"]
            try:
                return float(answers.get(key, 0)) < float(value)
            except Exception:
                return False
        if "lte" in rule:
            key, value = rule["lte"]
            try:
                return float(answers.get(key, 0)) <= float(value)
            except Exception:
                return False
        if "gt" in rule:
            key, value = rule["gt"]
            try:
                return float(answers.get(key, 0)) > float(value)
            except Exception:
                return False
        if "gte" in rule:
            key, value = rule["gte"]
            try:
                return float(answers.get(key, 0)) >= float(value)
            except Exception:
                return False
        if "len_gt" in rule:
            key, value = rule["len_gt"]
            return len(answers.get(key) or []) > int(value)
        if "len_gte" in rule:
            key, value = rule["len_gte"]
            return len(answers.get(key) or []) >= int(value)
        if "len_lt" in rule:
            key, value = rule["len_lt"]
            return len(answers.get(key) or []) < int(value)
        if "len_lte" in rule:
            key, value = rule["len_lte"]
            return len(answers.get(key) or []) <= int(value)
        return True

    if "all" in cond:
        return all(_check(rule) for rule in cond["all"])
    if "any" in cond:
        return any(_check(rule) for rule in cond["any"])
    return True


def render_module_inputs(
    product: str,
    module: str,
    manifest: dict[str, Any],
    previous_answers: dict[str, Any],
    *,
    inputs: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    st.session_state["_module_slug"] = f"{product}.{module}"
    answers = dict(previous_answers or {})
    required_visible: list[str] = []
    completion_entries: list[dict[str, Any]] = []
    section_answered = 0.0
    section_total = 0.0

    title = manifest.get("title")
    if not title and manifest.get("module"):
        title = manifest.get("module", {}).get("display", {}).get("title")
    if title:
        st.markdown(f"### {title}")

    input_list = inputs
    if input_list is None:
        input_list = manifest.get("inputs")
        if not input_list and manifest.get("sections"):
            input_list = []
            for section in manifest.get("sections", []):
                input_list.extend(section.get("questions", []))

    for raw_question in input_list or []:
        key = raw_question.get("key") or raw_question.get("id")
        if not key:
            continue
        question = dict(raw_question)
        question.setdefault("key", key)
        if not _visible(question, answers):
            continue
        value = render_input(question, current=answers.get(key))
        if value is not None:
            answers[key] = value
        if question.get("required"):
            required_visible.append(key)

        if question.get("count_in_completion", True):
            weight = float(question.get("completion_weight", 1) or 0)
            if weight < 0:
                weight = 0.0
            section_total += weight
            answered = _has_response(answers.get(key))
            if answered:
                section_answered += weight
            completion_entries.append({"key": key, "weight": weight, "answered": answered})

    st.session_state["_module_slug"] = None
    stats = {
        "section_answered": section_answered,
        "section_total": section_total,
        "entries": completion_entries,
    }
    return answers, required_visible, stats


def _has_response(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True
