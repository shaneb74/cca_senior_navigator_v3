from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

ALLOWED_TYPES = {"string", "number", "boolean", "date", "currency"}
ALLOWED_SELECT = {"single", "multi"}
ALLOWED_WIDGETS = {
    "chip",
    "radio",
    "multi_chip",
    "checkbox",
    "select",
    "text",
    "textarea",
    "number",
    "currency",
    "date",
}
ALLOWED_ACTIONS = {"next", "prev", "route", "save_exit", "restart", "submit"}


def _require(d: Dict[str, Any], key: str, where: str) -> None:
    if key not in d:
        raise ValueError(f"Manifest error: missing '{key}' in {where}.")


def _require_type(val: Any, typ, where: str, key: str) -> None:
    if not isinstance(val, typ):
        raise ValueError(f"Manifest error: '{key}' in {where} must be {typ.__name__}.")


def _validate_actions(actions: List[Dict[str, Any]], where: str) -> None:
    for i, action in enumerate(actions):
        action_where = f"{where}.actions[{i}]"
        _require(action, "label", action_where)
        _require(action, "action", action_where)
        act = action["action"]
        if act not in ALLOWED_ACTIONS:
            raise ValueError(
                f"Manifest error: invalid action '{act}' in {action_where}."
            )
        if act == "route":
            _require(action, "value", f"{action_where} (route requires 'value').")


def _validate_visible_if(visible_if: Dict[str, Any], where: str) -> None:
    allowed = {
        "eq",
        "neq",
        "in",
        "not_in",
        "lt",
        "lte",
        "gt",
        "gte",
        "all",
        "any",
        "len_gt",
        "len_gte",
        "len_lt",
        "len_lte",
    }
    if not any(key in visible_if for key in allowed):
        raise ValueError(
            f"Manifest error: unsupported visible_if in {where}. Use eq/neq/in/not_in/lt/lte/gt/gte/all/any/len_*."
        )


def validate_manifest(manifest: Dict[str, Any]) -> None:
    _require(manifest, "module", "manifest")
    _require(manifest, "sections", "manifest")
    _require_type(manifest["sections"], list, "manifest", "sections")

    module_meta = manifest["module"]
    for key in ("id", "name", "version"):
        _require(module_meta, key, "manifest.module")
        _require_type(module_meta[key], str, "manifest.module", key)
    _require(module_meta, "display", "manifest.module")
    display = module_meta["display"]
    for key in ("title", "subtitle", "estimated_time", "autosave", "progress_weight"):
        _require(display, key, "manifest.module.display")

    sections = manifest["sections"]
    if not sections:
        raise ValueError("Manifest error: 'sections' cannot be empty.")

    if any(section.get("type") == "results" for section in sections):
        if sections[-1].get("type") != "results":
            raise ValueError(
                "Manifest error: if a 'results' section exists, it must be the last section."
            )

    for idx, section in enumerate(sections):
        where = f"manifest.sections[{idx}]"
        _require(section, "id", where)
        _require_type(section["id"], str, where, "id")
        _require(section, "title", where)
        _require_type(section["title"], str, where, "title")
        section_type = section.get("type", "form")
        if section_type not in {"form", "info", "results"}:
            raise ValueError(
                f"Manifest error: invalid section 'type' in {where}; allowed: form|info|results."
            )

        if "actions" in section:
            _require_type(section["actions"], list, where, "actions")
            _validate_actions(section["actions"], where)

        if section_type != "form":
            continue

        questions = section.get("questions", [])
        _require_type(questions, list, where, "questions")
        if not questions:
            raise ValueError(
                f"Manifest error: {where} must contain at least one question or be type 'info'/'results'."
            )

        for q_idx, question in enumerate(questions):
            q_where = f"{where}.questions[{q_idx}]"
            for key in ("id", "type", "select", "label"):
                _require(question, key, q_where)
            if question["type"] not in ALLOWED_TYPES:
                raise ValueError(
                    f"Manifest error: invalid type '{question['type']}' in {q_where}."
                )
            if question["select"] not in ALLOWED_SELECT:
                raise ValueError(
                    f"Manifest error: invalid select '{question['select']}' in {q_where}."
                )
            if question["select"] in {"single", "multi"} and question["type"] == "string":
                options = question.get("options", [])
                _require_type(options, list, q_where, "options")
                for o_idx, option in enumerate(options):
                    opt_where = f"{q_where}.options[{o_idx}]"
                    _require(option, "label", opt_where)
                    _require(option, "value", opt_where)
            ui = question.get("ui", {})
            if ui:
                widget = ui.get("widget")
                if widget and widget not in ALLOWED_WIDGETS:
                    raise ValueError(
                        f"Manifest error: invalid ui.widget '{widget}' in {q_where}."
                    )
            if "visible_if" in question:
                _validate_visible_if(question["visible_if"], q_where)

    logic = manifest.get("logic")
    if not logic:
        return

    if "decision_tree" in logic:
        _require_type(logic["decision_tree"], list, "manifest.logic", "decision_tree")
        for i, node in enumerate(logic["decision_tree"]):
            node_where = f"manifest.logic.decision_tree[{i}]"
            _require(node, "if", node_where)
            _require(node, "recommendation", node_where)
            _require(node, "tier", node_where)

    if "scored_inputs" in logic:
        _require_type(logic["scored_inputs"], list, "manifest.logic", "scored_inputs")


# ---------------------------------------------------------------------------
# Legacy dataclasses (kept for compatibility with existing modules/components)
# ---------------------------------------------------------------------------


@dataclass
class FieldDef:
    key: str
    label: str
    type: str
    help: Optional[str] = None
    required: bool = False
    options: Optional[List[Dict[str, Any]]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    placeholder: Optional[str] = None
    default: Optional[Any] = None
    visible_if: Optional[Dict[str, Any]] = None
    write_key: Optional[str] = None
    a11y_hint: Optional[str] = None
    prefill_from: Optional[List[str]] = None
    ask_if_missing: bool = False
    ui: Optional[Dict[str, Any]] = None
    effects: Optional[List[Dict[str, Any]]] = None


@dataclass
class StepDef:
    id: str
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    fields: List[FieldDef] = field(default_factory=list)
    next_label: str = "Continue"
    skip_label: Optional[str] = None
    show_progress: bool = True
    show_bottom_bar: bool = True
    summary_keys: Optional[List[str]] = None


@dataclass
class ModuleConfig:
    product: str
    version: str
    steps: List[StepDef]
    state_key: str
    analytics_prefix: str = "module"
    autosave: bool = True
    theme_variant: Optional[str] = None
    outcomes_compute: Optional[str] = None
    results_step_id: Optional[str] = None


@dataclass
class OutcomeContract:
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    flags: Dict[str, bool] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    domain_scores: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    routing: Dict[str, Any] = field(default_factory=dict)
    audit: Dict[str, Any] = field(default_factory=dict)


FieldType = str  # legacy alias kept for backward compatibility


__all__ = [
    "validate_manifest",
    "FieldDef",
    "StepDef",
    "ModuleConfig",
    "OutcomeContract",
    "FieldType",
]
