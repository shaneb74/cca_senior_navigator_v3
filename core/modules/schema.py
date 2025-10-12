from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, TypedDict

FieldType = Literal[
    "radio",
    "pill",
    "dropdown",
    "slider",
    "money",
    "integer",
    "text",
    "textarea",
    "date",
    "chip_multi",
    "switch",
    "yesno",
    "pill_list",
]


class EffectDef(TypedDict, total=False):
    when_value_in: List[str]
    set_flag: str
    flag_message: str


@dataclass
class FieldDef:
    key: str
    label: str
    type: FieldType
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
    ui: Optional[str] = None
    effects: Optional[List[EffectDef]] = None


@dataclass
class StepDef:
    id: str
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    fields: List[FieldDef] = field(default_factory=list)
    next_label: str = "Continue"
    skip_label: Optional[str] = "Skip"
    show_progress: bool = True
    show_bottom_bar: bool = True
    summary_keys: Optional[List[str]] = None


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


__all__ = ["FieldDef", "StepDef", "ModuleConfig", "OutcomeContract", "FieldType", "EffectDef"]
