"""
Configuration loader for GCP v4 care_recommendation module.

Loads module.json and converts to ModuleConfig for the module engine.
Converts sections-based schema to steps-based schema with content contract system.
"""

import json
from pathlib import Path
from typing import Any

    # Remove legacy imports that are no longer used
from core.modules.schema import FieldDef, ModuleConfig, StepDef


def get_config() -> ModuleConfig:
    """Load care_recommendation module configuration.

    Converts sections-based module.json to steps-based ModuleConfig.
    Content contract resolution happens at render time, not config load time.

    Returns:
        ModuleConfig object for module engine
    """
    # Load raw JSON without content contract resolution
    # Resolution will happen at render time when session state is available
    module_dir = Path(__file__).parent
    spec_file = module_dir / "module.json"
    
    with spec_file.open('r', encoding='utf-8') as f:
        raw_spec = json.load(f)
    
    # Extract raw data
    module_meta = raw_spec.get("module", {})
    sections = raw_spec.get("sections", [])

    # Convert sections to steps (content will be resolved at render time)
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
        outcomes_compute="products.concierge_hub.gcp_v4.modules.care_recommendation.logic:derive_outcome",
        results_step_id="results",
    )


def _convert_section_to_step(section: dict[str, Any]) -> StepDef:
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
    
    # Extract Navi guidance (already interpolated by content contract)
    navi_guidance = section.get("navi_guidance")

    # Handle info sections (intro pages)
    if section_type == "info":
        return StepDef(
            id=section_id,
            title=title,
            subtitle=description,
            icon=None,
            fields=[],  # No fields for info pages
            content=section.get("content"),  # Pass content array for rendering
            next_label="Start" if section_id == "intro" else "Continue",
            skip_label=None,
            show_progress=False,
            show_bottom_bar=True,
            summary_keys=None,
            navi_guidance=navi_guidance,  # Pass guidance to StepDef
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
            navi_guidance=navi_guidance,  # Pass guidance to StepDef
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
        navi_guidance=navi_guidance,  # Pass guidance to StepDef
    )


def _convert_question_to_field(question: dict[str, Any]) -> FieldDef:
    """Convert a question from module.json to a FieldDef.

    Args:
        question: Question dict from module.json

    Returns:
        FieldDef object for module engine
    """
    question_id = question["id"]
    question_type = question.get("type", "string")
    select_type = question.get("select", "single")
    ui_config = question.get("ui", {})

    # Build effects from option flags
    effects = _build_effects_from_options(question.get("options", []))

    # Handle visible_if condition
    visible_if = question.get("visible_if")
    
    # Extract label and help text (already interpolated by content contract)
    label = question.get("label", "")
    help_text = question.get("help") if question.get("help") else None

    return FieldDef(
        key=question_id,
        label=label,
        type=_convert_type(question_type, select_type, ui_config),
        help=help_text,
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


def _convert_type(question_type: str, select_type: str, ui: dict[str, Any] = None) -> str:
    """Convert module.json type to FieldDef type.

    Args:
        question_type: Type from module.json ("string", "number", etc.)
        select_type: Select type ("single", "multi")
        ui: UI configuration dict with widget preference

    Returns:
        FieldDef type string matching component renderer names
    """
    # Check if UI specifies a widget type
    widget = (ui or {}).get("widget", "")

    # Multi-select types
    if question_type == "string" and select_type == "multi":
        if widget == "multi_chip":
            return "chip_multi"
        return "multiselect"

    # Single-select types - use UI widget to determine renderer
    elif question_type == "string" and select_type == "single":
        if widget == "chip":
            return "pill"  # Chip widget uses pill renderer
        elif widget == "dropdown":
            return "dropdown"
        else:
            return "radio"  # Default to radio for single-select

    # Number types
    elif question_type == "number":
        return "number"

    # Boolean types
    elif question_type == "boolean":
        return "yesno"

    # Default to text
    else:
        return "text"


def _build_effects_from_options(options: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
                    effects.append(
                        {"when_value_in": [value], "set_flag": flag, "flag_message": None}
                    )

    return effects


def _load_module_json() -> dict[str, Any]:
    """Load module.json from disk.

    Returns:
        Module configuration dict
    """
    path = Path(__file__).with_name("module.json")
    with path.open() as fh:
        return json.load(fh)


__all__ = ["get_config"]
