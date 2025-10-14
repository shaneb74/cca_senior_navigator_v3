"""
Configuration loader for GCP v4 care_recommendation module.

Loads module.json and converts to ModuleConfig for the module engine.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict
from core.modules.schema import FieldDef, ModuleConfig, StepDef


def get_config() -> ModuleConfig:
    """Load care_recommendation module configuration.
    
    Returns:
        ModuleConfig object for module engine
    """
    raw = _load_module_json()
    steps = [_build_step(step) for step in raw.get("steps", [])]

    return ModuleConfig(
        product="gcp_v4",
        version=raw.get("version", "4.0.0"),
        steps=steps,
        state_key="gcp_v4",
        outcomes_compute="products.gcp_v4.modules.care_recommendation.logic:derive_outcome",
        results_step_id="results",
    )


def _build_step(data: Dict[str, Any]) -> StepDef:
    """Build StepDef from step data.
    
    Args:
        data: Step definition dict from module.json
    
    Returns:
        StepDef object
    """
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
    """Build FieldDef from field data.
    
    Args:
        data: Field definition dict from module.json
    
    Returns:
        FieldDef object
    """
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
def _load_module_json() -> Dict[str, Any]:
    """Load module.json from disk.
    
    Returns:
        Module configuration dict
    """
    path = Path(__file__).with_name("module.json")
    with path.open() as fh:
        return json.load(fh)


__all__ = ["get_config"]
