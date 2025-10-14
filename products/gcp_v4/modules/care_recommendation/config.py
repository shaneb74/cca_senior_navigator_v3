"""
Configuration loader for GCP v4 care_recommendation module.

Loads module.json and converts to ModuleConfig for the module engine.
Converts sections-based schema to steps-based schema.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List
from core.modules.schema import FieldDef, ModuleConfig, StepDef


def get_config() -> ModuleConfig:
    """Load care_recommendation module configuration.
    
    Converts sections-based module.json to steps-based ModuleConfig.
    
    Returns:
        ModuleConfig object for module engine
    """
    raw = _load_module_json()
    module_meta = raw.get("module", {})
    sections = raw.get("sections", [])
    
    # Convert sections to steps
    steps = []
    for section in sections:
        step = _convert_section_to_step(section)
        if step:
            steps.append(step)
    
    return ModuleConfig(
        product="gcp_v4",
        version=module_meta.get("version", "v2025.10"),
        steps=steps,
        state_key="gcp_care_recommendation",  # Must match module.id
        outcomes_compute="products.gcp_v4.modules.care_recommendation.logic:derive_outcome",
        results_step_id="results",
    )


def _convert_section_to_step(section: Dict[str, Any]) -> StepDef:
    """Convert a section from module.json to a StepDef.
    
    module.json sections can be:
    - "info" type: intro/outro pages
    - Question sections: contain questions array
    - "results" type: final results page
    
    Args:
        section: Section dict from module.json
    
    Returns:
        StepDef object for module engine
    """
    section_type = section.get("type", "questions")
    section_id = section["id"]
    title = section.get("title", "")
    description = section.get("description", "")
    
    # Handle info sections (intro pages)
    if section_type == "info":
        return StepDef(
            id=section_id,
            title=title,
            subtitle=description,
            icon=None,
            fields=[],  # No fields for info pages
            next_label="Start" if section_id == "intro" else "Continue",
            skip_label=None,
            show_progress=False,
            show_bottom_bar=True,
            summary_keys=None,
        )
    
    # Handle results section
    if section_type == "results":
        return StepDef(
            id=section_id,
            title=title,
            subtitle=description,
            icon="🎯",
            fields=[],  # Results computed by outcomes_compute
            next_label="Continue",
            skip_label=None,
            show_progress=True,
            show_bottom_bar=True,
            summary_keys=None,
        )
    
    # Handle question sections
    questions = section.get("questions", [])
    fields = [_convert_question_to_field(q) for q in questions]
    
    return StepDef(
        id=section_id,
        title=title,
        subtitle=description,
        icon=None,
        fields=fields,
        next_label="Continue",
        skip_label=None,
        show_progress=True,
        show_bottom_bar=True,
        summary_keys=None,
    )


def _convert_question_to_field(question: Dict[str, Any]) -> FieldDef:
    """Convert a question from module.json to a FieldDef.
    
    Args:
        question: Question dict from module.json
    
    Returns:
        FieldDef object for module engine
    """
    question_id = question["id"]
    question_type = question.get("type", "string")
    select_type = question.get("select", "single")
    
    # Build effects from option flags
    effects = _build_effects_from_options(question.get("options", []))
    
    # Handle visible_if condition
    visible_if = question.get("visible_if")
    
    return FieldDef(
        key=question_id,
        label=question.get("label", ""),
        type=_convert_type(question_type, select_type),
        help=question.get("help"),
        required=question.get("required", False),
        options=question.get("options", []),
        min=question.get("min"),
        max=question.get("max"),
        step=question.get("step"),
        placeholder=question.get("placeholder"),
        default=question.get("default"),
        visible_if=visible_if,
        write_key=None,
        a11y_hint=None,
        prefill_from=None,
        ask_if_missing=False,
        ui=question.get("ui", {}),
        effects=effects,
    )


def _convert_type(question_type: str, select_type: str) -> str:
    """Convert module.json type to FieldDef type.
    
    Args:
        question_type: Type from module.json ("string", "number", etc.)
        select_type: Select type ("single", "multi")
    
    Returns:
        FieldDef type string
    """
    if question_type == "string" and select_type == "multi":
        return "multiselect"
    elif question_type == "string" and select_type == "single":
        return "select"
    elif question_type == "number":
        return "number"
    elif question_type == "boolean":
        return "boolean"
    else:
        return "text"


def _build_effects_from_options(options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build effects array from option flags.
    
    Converts flags in options to effects that the module engine can process.
    
    Args:
        options: List of option dicts from module.json
    
    Returns:
        List of effect dicts
    """
    effects = []
    
    for option in options:
        flags = option.get("flags", [])
        if flags:
            value = option.get("value")
            if value:
                # Create effect for each flag
                for flag in flags:
                    effects.append({
                        "when_value_in": [value],
                        "set_flag": flag,
                        "flag_message": None
                    })
    
    return effects




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
