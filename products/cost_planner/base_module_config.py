"""Base/home module configuration for Cost Planner.

This module serves as the landing page and module dashboard for the Cost Planner product.
It does not require authentication and provides navigation to sub-modules.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from core.modules.schema import FieldDef, ModuleConfig, StepDef


def _build_field(data: Dict[str, Any]) -> FieldDef:
    """Convert JSON field definition to FieldDef schema.
    
    Args:
        data: Field definition from JSON config
    
    Returns:
        FieldDef instance
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
    )


@lru_cache(maxsize=1)
def _load_config_payload() -> Dict[str, Any]:
    """Load base_module_config.json from disk.
    
    Returns:
        Dict with module configuration
    """
    path = Path(__file__).with_name("base_module_config.json")
    with path.open() as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def get_base_config() -> ModuleConfig:
    """Load Cost Planner base/home module configuration.
    
    The base module includes:
    - Intro/welcome page
    - Path selection (quick vs full assessment)
    - Module dashboard (rendered dynamically)
    
    Returns:
        ModuleConfig for base module
    """
    payload = _load_config_payload()
    
    steps: List[StepDef] = []
    for step_data in payload.get("steps", []):
        fields = [_build_field(f) for f in step_data.get("fields", [])]
        
        steps.append(
            StepDef(
                id=step_data["id"],
                title=step_data["title"],
                subtitle=step_data.get("subtitle"),
                fields=fields,
                show_progress=step_data.get("show_progress", True),
                next_label=step_data.get("next_label", "Continue"),
                skip_label=step_data.get("skip_label"),
            )
        )
    
    return ModuleConfig(
        product="cost_planner",
        state_key="cost.base",
        version=payload["version"],
        steps=steps,
        results_step_id=None,  # Base module doesn't have results page
        outcomes_compute=None,  # No outcomes calculation for base module
    )
