from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json

import streamlit as st

from core.modules.base import load_module_manifest
from core.modules.engine import run_module
from core.modules.schema import ModuleConfig, StepDef, FieldDef
from layout import render_shell_end, render_shell_start


def _load_care_recommendation_config() -> ModuleConfig:
    """Load the care_recommendation module manifest and convert to ModuleConfig."""
    manifest = load_module_manifest("gcp", "care_recommendation")
    
    # Extract module metadata
    module_meta = manifest.get("module", {})
    display = module_meta.get("display", {})
    
    # Convert sections to steps
    steps = []
    for section in manifest.get("sections", []):
        section_id = section.get("id")
        section_type = section.get("type", "form")
        
        # Skip intro section - it's shown differently by the engine
        # Include results section - engine needs it for navigation
        if section_type == "info":
            continue
            
        # Convert questions to fields
        fields = []
        for q in section.get("questions", []):
            # Determine the field type for the renderer
            field_type = _determine_field_type(q)
            
            # Normalize effects to always be a list
            effects = _normalize_effects(q.get("effects"))
            
            fields.append(FieldDef(
                key=q.get("id"),
                label=q.get("label", ""),
                type=field_type,
                help=q.get("help"),
                required=q.get("required", False),
                options=q.get("options"),
                min=q.get("min"),
                max=q.get("max"),
                step=q.get("step"),
                placeholder=q.get("placeholder"),
                default=q.get("default"),
                visible_if=q.get("visible_if"),
                write_key=q.get("write_key"),
                a11y_hint=q.get("a11y_hint"),
                prefill_from=q.get("prefill_from"),
                ask_if_missing=q.get("ask_if_missing", False),
                ui=q.get("ui"),
                effects=effects,
            ))
        
        # Results sections shouldn't show progress or bottom bar
        is_results = section_type == "results"
        
        steps.append(StepDef(
            id=section_id,
            title=section.get("title", ""),
            subtitle=section.get("description"),
            icon=section.get("icon"),
            fields=fields,
            next_label="Continue",
            skip_label=None,
            show_progress=not is_results,
            show_bottom_bar=not is_results,
            summary_keys=None,
        ))
    
    return ModuleConfig(
        product="gcp",
        version=module_meta.get("version", "v2025.10"),
        steps=steps,
        state_key="gcp",
        outcomes_compute="products.gcp.modules.care_recommendation.logic:derive_outcome",
        results_step_id="results",
    )


def _normalize_effects(effects: Any) -> Optional[List[Dict[str, Any]]]:
    """Normalize effects to always be a list of effect objects.
    
    Handles two formats from module.json:
    1. Array format: [{ "condition": "...", "flags": [...] }, ...]
    2. Object format: { "effect_name": { "condition": "...", "message": "..." }, ... }
    """
    if effects is None:
        return None
    
    # If already a list, return as-is
    if isinstance(effects, list):
        return effects
    
    # If it's a dict, convert named effects to list format
    if isinstance(effects, dict):
        effect_list = []
        for effect_name, effect_data in effects.items():
            # Create a normalized effect object
            normalized = {"name": effect_name}
            normalized.update(effect_data)
            effect_list.append(normalized)
        return effect_list
    
    # Unknown format, return None
    return None


def _determine_field_type(question: Dict[str, Any]) -> str:
    """Determine the renderer type based on question structure."""
    q_type = question.get("type", "string")
    select_type = question.get("select")
    ui = question.get("ui", {})
    widget = ui.get("widget")
    
    # If widget is explicitly specified, use it
    if widget == "chip":
        return "chip_multi" if select_type == "multi" else "pill"
    if widget == "multi_chip":
        return "chip_multi"
    if widget == "pill":
        return "pill"
    if widget == "dropdown":
        return "multi_dropdown" if select_type == "multi" else "dropdown"
    if widget == "slider":
        return "slider"
    if widget == "textarea":
        return "textarea"
    
    # Infer from select type if no widget specified
    if select_type == "single":
        return "radio"  # Default for single select
    if select_type == "multi":
        return "chip_multi"  # Default for multi select
    
    # Handle other types
    if q_type == "number":
        return "slider"
    if q_type == "boolean":
        return "yesno"
    
    # Default to text input
    return "text"


def render() -> None:
    """Render the Guided Care Plan product using the new module engine."""
    config = _load_care_recommendation_config()
    
    # Don't show page-level title - module intro has its own title
    render_shell_start("", active_route="gcp")
    
    # Run the module with the new engine
    module_state = run_module(config)
    
    render_shell_end()


def register() -> Dict[str, Any]:
    return {
        "routes": {"product/gcp": render},
        "tile": {
            "key": "gcp",
            "title": "Guided Care Plan",
            "meta": ["≈2 min • Auto-saves"],
            "progress_key": "gcp.progress",
            "unlock_condition": lambda _ss: True,
        },
    }
