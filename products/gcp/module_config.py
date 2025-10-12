from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from core.modules.schema import FieldDef, ModuleConfig, StepDef


def get_config() -> ModuleConfig:
    raw = _load_config_payload()
    steps = [_build_step(step) for step in raw.get("steps", [])]

    return ModuleConfig(
        product=raw.get("product", "gcp"),
        version=raw.get("version", "v1.0"),
        steps=steps,
        state_key=raw.get("state_key", "gcp"),
        outcomes_compute="products.gcp.derive:derive_outcomes_v1",
        results_step_id="results",
    )


def _build_step(data: Dict[str, Any]) -> StepDef:
    fields = [_build_field(field) for field in data.get("fields", [])]
    return StepDef(
        id=data["id"],
        title=data["title"],
        subtitle=data.get("subtitle"),
        icon=data.get("icon"),
        fields=fields,
        next_label=data.get("next_label", "Continue"),
        skip_label=data.get("skip_label"),
        show_progress=data.get("show_progress", True),
        show_bottom_bar=data.get("show_bottom_bar", True),
        summary_keys=data.get("summary_keys"),
    )


def _build_field(data: Dict[str, Any]) -> FieldDef:
    return FieldDef(
        key=data["key"],
        label=data["label"],
        type=data["type"],
        help=data.get("help"),
        required=data.get("required", False),
        options=data.get("options"),
        min=data.get("min"),
        max=data.get("max"),
        step=data.get("step"),
        placeholder=data.get("placeholder"),
        default=data.get("default"),
        visible_if=data.get("visible_if"),
        write_key=data.get("write_key"),
        a11y_hint=data.get("a11y_hint"),
        prefill_from=data.get("prefill_from"),
        ask_if_missing=data.get("ask_if_missing", False),
        ui=data.get("ui"),
        effects=data.get("effects"),
    )


@lru_cache(maxsize=1)
def _load_config_payload() -> Dict[str, Any]:
    path = Path(__file__).with_name("module_config.json")
    with path.open() as fh:
        return json.load(fh)


__all__ = ["get_config"]
