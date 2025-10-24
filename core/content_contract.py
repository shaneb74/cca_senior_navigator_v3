"""
Content Contract System - Centralized token interpolation and content resolution.

This module provides a single pipeline for processing JSON content with token
interpolation, validation, and optional overrides. Replaces scattered string
replacement code throughout the application.

Key principles:
- JSON is the source of truth for copy
- No runtime mutation of JSON
- All personalization happens at render-time through interpolation
- Immutable view-models for UI consumption
- Support for editor-friendly overrides
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

import streamlit as st

logger = logging.getLogger(__name__)

# Token specification v1
ALLOWED_TOKENS = {
    "NAME": "First name of care recipient; fallback 'you'",
    "NAME_POS": "Possessive form (James's); fallback 'your'", 
    "ZIP": "5-digit ZIP if present; else 'your area'",
    "TIER": "Recommended tier label if present",
    "HOURS": "Integer hours if present",
    "STATE": "Two-letter state if present",
    "RELATION": "'you' if self, else 'your loved one'"
}


@dataclass
class TokenContext:
    """Context for token interpolation containing all available replacement values."""
    
    # Core person information
    name: str = "you"
    name_possessive: str = "your"
    
    # Location information
    zip_code: str = "your area"
    state: str = ""
    
    # Care information
    tier: str = ""
    hours: str = ""
    
    # Relationship context
    relation: str = "you"
    
    # Truncation settings
    truncate_names_in_headers: bool = True
    max_header_name_length: int = 20


def first_name(full_name: str) -> str:
    """Extract first name from full name string.
    
    Args:
        full_name: Full name string (e.g., "Mary Jo Smith")
        
    Returns:
        First name only (e.g., "Mary")
    """
    if not full_name or not full_name.strip():
        return ""
    
    return full_name.strip().split()[0]


def possessive(name: str, ap_style: bool = False) -> str:
    """Convert name to possessive form.
    
    Args:
        name: Name to convert (e.g., "James", "Mary")
        ap_style: If True, use AP style (James' vs James's)
        
    Returns:
        Possessive form (e.g., "James's" or "Mary's")
    """
    if not name or not name.strip():
        return "your"
    
    name = name.strip()
    
    if ap_style and name.lower().endswith('s'):
        return f"{name}'"
    else:
        return f"{name}'s"


def build_token_context(session_state: Dict[str, Any], snapshot: Dict[str, Any] | None = None) -> TokenContext:
    """Build token context from session state and optional snapshot.
    
    Args:
        session_state: Streamlit session state or equivalent dict
        snapshot: Optional user data snapshot
        
    Returns:
        TokenContext with all available token values
    """
    # Extract person name
    person_name = (
        session_state.get("person_a_name") or 
        session_state.get("planning_for_name") or
        session_state.get("person_name") or
        ""
    )
    
    # Determine relationship context
    relationship_type = session_state.get("relationship_type", "")
    planning_for_relationship = session_state.get("planning_for_relationship", "")
    
    # Build name tokens
    if person_name:
        name = first_name(person_name)
        name_pos = possessive(name)
    else:
        name = "you"
        name_pos = "your"
    
    # Build relation token
    if relationship_type == "Myself" or planning_for_relationship == "self":
        relation = "you"
    else:
        relation = "your loved one"
    
    # Extract location information
    zip_code = session_state.get("zip_code", "")
    if not zip_code and snapshot:
        zip_code = snapshot.get("zip_code", "")
    if not zip_code:
        zip_code = "your area"
    
    state = session_state.get("state", "")
    if not state and snapshot:
        state = snapshot.get("state", "")
    
    # Extract care information
    tier = ""
    hours = ""
    
    # Try to get tier from various sources
    care_rec = session_state.get("gcp_care_recommendation", {})
    if care_rec and care_rec.get("recommendation"):
        tier = care_rec["recommendation"]
    
    # Try to get hours from cost planner or other sources
    cost_state = session_state.get("cost_planner_v2", {})
    if cost_state and cost_state.get("hours"):
        hours = str(cost_state["hours"])
    
    return TokenContext(
        name=name,
        name_possessive=name_pos,
        zip_code=zip_code,
        state=state,
        tier=tier,
        hours=hours,
        relation=relation
    )


def interpolate(value: Any, context: TokenContext, is_header: bool = False) -> Any:
    """Interpolate tokens in content without mutating input.
    
    Args:
        value: Content to interpolate (str, list, dict, or other)
        context: Token context with replacement values
        is_header: If True, truncate long names for headers
        
    Returns:
        New object with tokens replaced (same shape as input)
    """
    if isinstance(value, str):
        return _interpolate_string(value, context, is_header)
    elif isinstance(value, list):
        return [interpolate(item, context, is_header) for item in value]
    elif isinstance(value, dict):
        return {k: interpolate(v, context, is_header) for k, v in value.items()}
    else:
        # Return other types unchanged
        return value


def _interpolate_string(text: str, context: TokenContext, is_header: bool = False) -> str:
    """Interpolate tokens in a string.
    
    Args:
        text: String to process
        context: Token context
        is_header: If True, truncate long names
        
    Returns:
        String with tokens replaced
    """
    if not text or "{" not in text:
        return text
    
    result = text
    
    # Get name values (possibly truncated for headers)
    name = context.name
    name_pos = context.name_possessive
    
    if is_header and context.truncate_names_in_headers and len(name) > context.max_header_name_length:
        name = name[:context.max_header_name_length] + "..."
        name_pos = possessive(name)
    
    # Token replacements
    replacements = {
        "{NAME}": name,
        "{NAME_POS}": name_pos,
        "{ZIP}": context.zip_code,
        "{TIER}": context.tier,
        "{HOURS}": context.hours,
        "{STATE}": context.state,
        "{RELATION}": context.relation,
    }
    
    # Apply replacements
    for token, replacement in replacements.items():
        if token in result:
            result = result.replace(token, replacement)
    
    # Check for unknown tokens and warn
    _check_unknown_tokens(result, text)
    
    return result


def _check_unknown_tokens(result: str, original: str) -> None:
    """Check for unknown tokens and log warnings."""
    if "{" in result and "}" in result:
        # Find remaining tokens
        import re
        remaining_tokens = re.findall(r'\{([^}]+)\}', result)
        unknown_tokens = [token for token in remaining_tokens if token not in ALLOWED_TOKENS]
        
        if unknown_tokens:
            logger.warning(
                f"Unknown tokens found in content: {unknown_tokens}. "
                f"Allowed tokens: {list(ALLOWED_TOKENS.keys())}. "
                f"Original text: '{original}'"
            )


def resolve_content(
    spec: Dict[str, Any], 
    overrides: Dict[str, Any] | None = None, 
    context: TokenContext | None = None
) -> Dict[str, Any]:
    """Resolve content spec with validation, overrides, and interpolation.
    
    Args:
        spec: Base content specification (loaded JSON)
        overrides: Optional overrides dict  
        context: Token context for interpolation
        
    Returns:
        Resolved content dict with interpolated tokens
    """
    if context is None:
        context = build_token_context(st.session_state if 'st' in globals() else {})
    
    # Start with base spec (create copy to avoid mutation)
    resolved = _deep_copy(spec)
    
    # Apply overrides if provided
    if overrides:
        resolved = _merge_overrides(resolved, overrides)
    
    # Validate structure (basic checks)
    _validate_content_spec(resolved)
    
    # Interpolate all content
    resolved = interpolate(resolved, context)
    
    return resolved


def _deep_copy(obj: Any) -> Any:
    """Create a deep copy of object without mutating original."""
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(item) for item in obj]
    else:
        return obj


def _merge_overrides(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Merge overrides into base content.
    
    Overrides are applied by matching keys. For nested dicts, merge recursively.
    For other values, override completely replaces base value.
    """
    result = _deep_copy(base)
    
    for key, override_value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(override_value, dict):
            # Recursive merge for nested dicts
            result[key] = _merge_overrides(result[key], override_value)
        else:
            # Direct replacement for other types
            result[key] = _deep_copy(override_value)
    
    return result


def _validate_content_spec(spec: Dict[str, Any]) -> None:
    """Validate content specification structure.
    
    Performs basic validation to catch common issues early.
    """
    # Check for required top-level structure
    if not isinstance(spec, dict):
        logger.warning("Content spec should be a dictionary")
        return
    
    # Validate copy section if present
    if "copy" in spec:
        copy_section = spec["copy"]
        if not isinstance(copy_section, dict):
            logger.warning("'copy' section should be a dictionary")
        else:
            # Check that copy values are strings or lists of strings
            for key, value in copy_section.items():
                if not _is_valid_copy_value(value):
                    logger.warning(f"Copy key '{key}' should contain strings or lists of strings")
    
    # Validate view section if present  
    if "view" in spec:
        view_section = spec["view"]
        if not isinstance(view_section, dict):
            logger.warning("'view' section should be a dictionary")
    
    # Check for unknown top-level keys (warning only)
    known_keys = {"id", "copy", "view", "module", "sections", "inputs"}  # Add common keys
    unknown_keys = set(spec.keys()) - known_keys
    if unknown_keys:
        logger.debug(f"Unknown top-level keys in content spec: {unknown_keys}")


def _is_valid_copy_value(value: Any) -> bool:
    """Check if a value is valid for copy content (string or list of strings)."""
    if isinstance(value, str):
        return True
    elif isinstance(value, list):
        return all(isinstance(item, str) for item in value)
    elif isinstance(value, dict):
        # Allow nested dicts (like navi_guidance)
        return all(_is_valid_copy_value(v) for v in value.values())
    else:
        return False


def load_json_if_exists(file_path: str | Path) -> Dict[str, Any] | None:
    """Load JSON file if it exists, return None otherwise."""
    path = Path(file_path)
    if path.exists():
        try:
            with path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load JSON from {path}: {e}")
            return None
    return None


# Convenience function for common usage pattern
def resolve_module_content(module_dir: str | Path, context: TokenContext | None = None) -> Dict[str, Any]:
    """Resolve content for a module directory with optional overrides.
    
    Args:
        module_dir: Path to module directory containing module.json
        context: Optional token context (will build from session if None)
        
    Returns:
        Resolved content dict
    """
    module_path = Path(module_dir)
    
    # Load base spec
    spec_file = module_path / "module.json"
    if not spec_file.exists():
        raise FileNotFoundError(f"Module spec not found: {spec_file}")
    
    with spec_file.open('r', encoding='utf-8') as f:
        spec = json.load(f)
    
    # Load optional overrides
    overrides_file = module_path / "module.overrides.json"
    overrides = load_json_if_exists(overrides_file)
    
    return resolve_content(spec, overrides, context)