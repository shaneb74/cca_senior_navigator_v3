from __future__ import annotations

import importlib
import time
from dataclasses import asdict
from html import escape as H
from typing import Any, Dict, List, Mapping, Optional, Sequence

import streamlit as st

from core.events import log_event
from core.nav import PRODUCTS
from core.session_store import safe_rerun

from . import components as components
from .layout import actions, bottom_summary, header
from .schema import FieldDef, ModuleConfig, OutcomeContract, StepDef


def run_module(config: ModuleConfig) -> Dict[str, Any]:
    """Run a module flow defined by ModuleConfig. Returns updated module state."""
    state_key = config.state_key
    st.session_state.setdefault(state_key, {})
    state = st.session_state[state_key]

    total_steps = len(config.steps)
    
    # Validate module configuration
    if total_steps == 0:
        st.error("⚠️ Module configuration error: No steps defined.")
        st.stop()
    
    # Check tile state for last saved step (resume functionality)
    tiles = st.session_state.setdefault("tiles", {})
    tile_state = tiles.setdefault(config.product, {})
    saved_step = tile_state.get("last_step")
    
    # Resume from saved step if exists, otherwise start at 0
    if saved_step is not None and saved_step >= 0:
        step_index = saved_step
    else:
        step_index = int(st.session_state.get(f"{state_key}._step", 0))
    
    # Clamp to valid range with additional safety check
    step_index = max(0, min(step_index, total_steps - 1))
    
    # Final bounds validation before array access
    if step_index < 0 or step_index >= total_steps:
        st.error(f"⚠️ Invalid step index: {step_index} (total steps: {total_steps}). Resetting to step 0.")
        step_index = 0
        st.session_state[f"{state_key}._step"] = 0
    
    # Store step index for internal navigation
    st.session_state[f"{state_key}._step"] = step_index
    
    step = config.steps[step_index]

    # Substitute {{name}} template in title
    title = _substitute_title(step.title, state)
    
    # Calculate progress BEFORE rendering header
    progress = _update_progress(config, state, step, step_index)
    
    # Calculate progress-eligible steps (exclude intro/results pages)
    progress_steps = [s for s in config.steps if s.show_progress]
    progress_total = len(progress_steps)
    
    # Check if current step should show progress indicators
    show_step_dots = step.show_progress
    
    # ========================================================================
    # NAVI PERSISTENT GUIDE BAR
    # Inject Navi's contextual guidance at the top of every module
    # ========================================================================
    # DISABLED: Now using main Navi panel (blue box) which shows step progress
    # The purple box was duplicate - main Navi panel at page top handles all guidance
    # _render_navi_guide_bar(config, step, state, step_index, progress_total)
    
    # Render header with actual progress
    # Note: Progress bar also disabled since Navi panel shows progress (X/Y steps)
    _render_header(step_index, total_steps, title, step.subtitle, progress, progress_total, show_step_dots, step.id == config.steps[0].id, config)

    # Render content array (for info-type pages)
    if step.content:
        _render_content(step.content)

    new_values = _render_fields(step, state)
    if new_values:
        state.update(new_values)

    is_results = config.results_step_id and step.id == config.results_step_id
    
    if is_results:
        _ensure_outcomes(config, state)
        _render_results_view(state, config)
        return state

    _render_summary(step, state)

    required_fields = _required_fields(step, state)
    missing = _required_missing(required_fields, state)

    # Render actions - get save_exit button state
    # Detect if this is the intro page (first step) - nothing to save yet
    is_intro_page = (step.id == config.steps[0].id)
    next_clicked, skip_clicked, save_exit_clicked, back_clicked, back_to_hub_clicked = actions(
        step.next_label, 
        step.skip_label, 
        is_intro=is_intro_page,
        show_back=(not is_intro_page and step_index > 0),
        step_index=step_index,
        config=config
    )
    
    # Handle Back button
    if back_clicked:
        prev_index = max(0, step_index - 1)
        st.session_state[f"{config.state_key}._step"] = prev_index
        
        # Update tile state for resume functionality
        tiles = st.session_state.setdefault("tiles", {})
        tile_state = tiles.setdefault(config.product, {})
        tile_state["last_step"] = prev_index
        
        safe_rerun()
    
    # Handle Back to Hub
    if back_to_hub_clicked:
        _handle_save_exit(config, state, step_index, total_steps, reason="back_to_hub")
        return state
    
    # Handle Save & Continue Later
    if save_exit_clicked:
        _handle_save_exit(config, state, step_index, total_steps, reason="save_exit")
        return state
    
    if next_clicked and missing:
        st.warning(f"Please complete the required fields: {', '.join(missing)}")
    allow_next = next_clicked and not missing
    if allow_next:
        _apply_step_effects(step, state)
    _handle_nav(config, step, step_index, total_steps, allow_next, skip_clicked)

    if config.results_step_id and step.id == config.results_step_id:
        _render_results_view(state, config)
        return state

    return state


def _render_header(step_index: int, total: int, title: str, subtitle: str | None, progress: float, progress_total: int, show_step_dots: bool = True, is_intro: bool = False, config: ModuleConfig | None = None) -> None:
    """Render module header without progress bar (Navi panel handles progress)."""
    from html import escape as _escape
    
    # Progress bar removed - Navi panel at top now shows step progress (X/Y)
    
    subtitle_html = ""
    if subtitle:
        # Convert newlines to <br> tags and wrap paragraphs
        lines = subtitle.split('\n')
        formatted_lines = []
        first_line = True
        for line in lines:
            stripped = line.strip()
            if stripped:
                # First line gets emphasized styling (h3)
                if first_line and stripped.endswith(':'):
                    formatted_lines.append(f"<h3 class='h3' style='margin-top: 1.5rem; margin-bottom: 1rem;'>{_escape(stripped)}</h3>")
                    first_line = False
                else:
                    # Escape the line but preserve emoji and special chars
                    formatted_lines.append(f"<p>{_escape(stripped)}</p>")
            elif formatted_lines:  # Add spacing between paragraphs
                formatted_lines.append("<br/>")
        subtitle_html = f"<div class='lead'>{''.join(formatted_lines)}</div>"
    
    # Header without back button (back button moved to actions section)
    st.markdown(
        f"""
        <div class="mod-head">
          <div class="mod-head-row">
            <h2 class="h2">{_escape(title)}</h2>
          </div>
          {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _substitute_title(title: str, state: Mapping[str, Any]) -> str:
    """Replace {{name}} with person's name from state or session."""
    if "{{name}}" not in title:
        return title
    
    # Try to get name from module state first
    name = state.get("recipient_name") or state.get("person_name")
    
    # Fall back to session state
    if not name:
        profile = st.session_state.get("profile", {})
        name = profile.get("recipient_name") or profile.get("person_name")
    
    # Default to generic text
    if not name:
        name = "This Person"
    
    return title.replace("{{name}}", name)


def _render_content(content: list[str]) -> None:
    """Render content array for info-type pages.
    
    Args:
        content: List of content lines with markdown support.
                 Empty strings create spacing.
    """
    for line in content:
        if line.strip():
            # Render non-empty lines with markdown
            st.markdown(line)
        else:
            # Empty lines add spacing
            st.markdown("<br/>", unsafe_allow_html=True)


def _render_fields(step: StepDef, state: Mapping[str, Any]) -> Dict[str, Any]:
    new_values: Dict[str, Any] = {}
    for field in step.fields:
        if not _is_visible(field, state):
            continue
        renderer = components.RENDERERS.get(field.type)
        if not renderer:
            continue
        store_key = field.write_key or field.key
        current_value = state.get(store_key, field.default)
        value = renderer(field, current_value)
        new_values[store_key] = value
    return new_values


def _update_progress(
    config: ModuleConfig, state: Dict[str, Any], step: StepDef, step_index: int
) -> float:
    # Only count steps that have show_progress=True (exclude intro)
    progress_steps = [s for s in config.steps if s.show_progress]
    total = len(progress_steps) or 1
    
    # Check if we're on results page FIRST - that's always 100%
    if config.results_step_id and step.id == config.results_step_id:
        progress = 1.0
    else:
        # Find the current step's index among progress-eligible steps
        try:
            progress_index = next(i for i, s in enumerate(progress_steps) if s.id == step.id)
        except StopIteration:
            # Current step doesn't count toward progress (like intro page)
            progress = 0.0
        else:
            # Calculate fractional progress within current step
            required = _required_fields(step, state)
            if required:
                completed = sum(1 for f in required if _has_value(state.get(f.write_key or f.key)))
                fraction = completed / len(required)
            else:
                fraction = 1.0
            
            # Progress is (completed steps + fraction of current) / total
            progress = (progress_index + fraction) / total

    progress_pct = round(progress * 100, 1)
    state["progress"] = progress_pct
    
    if progress >= 1.0:
        state["status"] = "done"
    elif progress > 0:
        state["status"] = "doing"
    else:
        state["status"] = "new"

    tiles = st.session_state.setdefault("tiles", {})
    tile_state = tiles.setdefault(config.product, {})
    tile_state["progress"] = progress_pct
    # NOTE: Do NOT update last_step here - it should only update on navigation
    # to avoid overwriting the step before user clicks Continue
    
    if progress >= 1.0:
        tile_state["status"] = "done"
    elif progress > 0:
        tile_state["status"] = "doing"
    else:
        tile_state["status"] = "new"

    _emit(
        "product.progress",
        {
            "product": config.product,
            "state_key": config.state_key,
            "progress": progress_pct,
        },
    )

    return progress


def _render_summary(step: StepDef, state: Mapping[str, Any]) -> None:
    """Render developer info in sidebar for debugging."""
    if step.show_bottom_bar and step.summary_keys:
        field_map = {f.write_key or f.key: f for f in step.fields}
        items = {
            key: _format_summary_value(state.get(key), field_map.get(key))
            for key in step.summary_keys
            if key in state
        }
        # Render in sidebar instead of bottom of main content
        with st.sidebar:
            st.markdown("### 🔧 Developer Info")
            for key, value in items.items():
                st.markdown(f"**{key}**")
                st.code(value, language="text")


def _handle_nav(
    config: ModuleConfig,
    step: StepDef,
    step_index: int,
    total_steps: int,
    next_clicked: bool,
    skip_clicked: bool,
) -> None:
    if not (next_clicked or skip_clicked):
        return

    next_index = min(step_index + 1, total_steps - 1)
    st.session_state[f"{config.state_key}._step"] = next_index
    
    # Update tile state with new step for resume functionality
    tiles = st.session_state.setdefault("tiles", {})
    tile_state = tiles.setdefault(config.product, {})
    tile_state["last_step"] = next_index

    if next_clicked and config.results_step_id and step.id == config.results_step_id:
        _emit(
            "product.completed",
            {"product": config.product, "state_key": config.state_key},
        )

    _rerun_app()


def _hub_route_for_product(product_key: str) -> str:
    """Resolve hub route key for a given product key."""
    fallback_map = {
        "gcp_v4": "gcp",
        "cost_v2": "cost_planner",
        "pfma_v2": "pfma",
    }
    candidates = [product_key]
    mapped = fallback_map.get(product_key)
    if mapped:
        candidates.append(mapped)
    if "_" in product_key:
        base_key = product_key.split("_", 1)[0]
        candidates.append(base_key)
    for key in candidates:
        if not key:
            continue
        info = PRODUCTS.get(key)
        if not info:
            continue
        hub_id = info.get("hub") or "concierge"
        return hub_id if hub_id.startswith("hub_") else f"hub_{hub_id}"
    return "hub_concierge"


def _handle_save_exit(
    config: ModuleConfig,
    state: Dict[str, Any],
    step_index: int,
    total_steps: int,
    reason: str = "save_exit",
) -> None:
    """Handle Save & Continue Later button - saves progress and returns to hub."""
    # Progress is already auto-saved in state
    progress_pct = state.get("progress", 0)
    
    # Calculate readable step info
    progress_steps = [s for s in config.steps if s.show_progress]
    completed_progress_steps = min(step_index, len(progress_steps))
    
    # Store exit info for hub message
    state["last_exit_step"] = step_index
    state["last_exit_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    state["last_exit_reason"] = reason
    
    # Update tile state with current step for resume functionality
    tiles = st.session_state.setdefault("tiles", {})
    tile_state = tiles.setdefault(config.product, {})
    tile_state["last_step"] = step_index
    
    hub_route = _hub_route_for_product(config.product)

    # Set a session flag to show completion message
    st.session_state["_show_save_message"] = {
        "product": config.product,
        "progress": progress_pct,
        "step": completed_progress_steps + 1,
        "total": len(progress_steps),
        "reason": reason,
        "hub_route": hub_route,
    }
    
    event_name = "product.saved_exit" if reason == "save_exit" else "product.back_to_hub"
    payload = {
        "product": config.product,
        "state_key": config.state_key,
        "progress": progress_pct,
        "step_index": step_index,
        "hub_route": hub_route,
        "reason": reason,
    }
    _emit(event_name, payload)
    
    # Navigate to concierge hub
    st.query_params.clear()
    st.query_params["page"] = hub_route
    _rerun_app()



def _ensure_outcomes(config: ModuleConfig, answers: Dict[str, Any]) -> None:
    state_key = config.state_key
    outcome_key = f"{state_key}._outcomes"
    
    if st.session_state.get(outcome_key):
        return

    context = _compute_context(config)
    outcome = OutcomeContract()
    if config.outcomes_compute:
        fn = _resolve_callable(config.outcomes_compute)
        try:
            result = fn(answers=answers, context=context)
            if isinstance(result, OutcomeContract):
                outcome = result
            elif isinstance(result, dict):
                # Don't wrap in OutcomeContract - store dict directly
                # This allows product-specific schemas (e.g., GCP's tier/tier_score)
                st.session_state[outcome_key] = result
                
                # Still handle legacy handoff for backward compatibility
                handoff = st.session_state.setdefault("handoff", {})
                handoff[state_key] = result
                
                _emit(
                    "module.outcomes.ready",
                    {"state_key": state_key, "outcome": str(result.get("tier") or result.get("recommendation", ""))}
                )
                return  # Early return - we're done
        except Exception as e:
            import traceback
            st.error(f"❌ Error computing outcomes: {type(e).__name__}: {str(e)}")
            st.text(traceback.format_exc())
            outcome = OutcomeContract()

    audit = dict(outcome.audit)
    audit.update(
        {
            "version": config.version,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    )
    outcome.audit = audit

    st.session_state[outcome_key] = asdict(outcome)

    handoff = st.session_state.setdefault("handoff", {})
    handoff[state_key] = {
        "recommendation": outcome.recommendation,
        "flags": dict(outcome.flags),
        "tags": list(outcome.tags),
        "domain_scores": dict(outcome.domain_scores),
    }

    if outcome.recommendation:
        answers["care_tier"] = outcome.recommendation
        answers["status"] = "done"
        answers["progress"] = 100.0

        person_name = context.get("person_a_name", "This person")
        reason = (
            f"{person_name}'s care plan suggests {outcome.recommendation.replace('_', ' ').title()}"
        )
        nudges: List[str] = []
        if outcome.flags.get("emotional_followup"):
            nudges.append("Emotional wellbeing may need an advisor check-in.")
        if outcome.flags.get("fall_risk"):
            nudges.append("Fall prevention should be part of your next step.")

        concierge_panel = {
            "reason": reason,
            "next_step": "cost",
        }
        if nudges:
            concierge_panel["nudges"] = nudges

        st.session_state.setdefault("mcip", {})["concierge"] = concierge_panel

    _emit(
        "module.outcomes.ready",
        {"state_key": state_key, "recommendation": outcome.recommendation},
    )


def _resolve_callable(path: str):
    module_path, attr = path.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, attr)


def _compute_context(config: ModuleConfig) -> Dict[str, Any]:
    state = st.session_state.get(config.state_key, {})
    profile = st.session_state.get("profile", {})
    auth = st.session_state.get("auth", {})
    return {
        "product": config.product,
        "version": config.version,
        "person_a_name": state.get("recipient_name") or "this person",
        "geo": profile.get("state"),
        "auth": bool(auth.get("is_authenticated")),
    }


def _emit(event: str, payload: Optional[Dict[str, Any]] = None) -> None:
    try:
        log_event(event, payload or {})
    except Exception:
        pass


def _is_visible(field: FieldDef, state: Mapping[str, Any]) -> bool:
    cond = field.visible_if
    if not cond:
        return True
    key = cond.get("key")
    if key is None or key not in state:
        return False
    if "eq" in cond:
        return state.get(key) == cond["eq"]
    if "in" in cond:
        values = cond.get("in")
        return state.get(key) in values if isinstance(values, (list, tuple, set)) else False
    return True


def _format_summary_value(value: Any, field: Optional[FieldDef] = None) -> str:
    if field:
        return _display_value(field, value)
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        return f"{value:,.0f}" if abs(value) >= 1000 else f"{value}"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(v) for v in value if str(v))
    return str(value)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return True
    if isinstance(value, (list, tuple, set)):
        return len(value) > 0
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _required_fields(step: StepDef, state: Mapping[str, Any]) -> List[FieldDef]:
    fields: List[FieldDef] = []
    for field in step.fields:
        if not field.required:
            continue
        if not _is_visible(field, state):
            continue
        store_key = field.write_key or field.key
        if field.ask_if_missing and _has_value(state.get(store_key)):
            continue
        fields.append(field)
    return fields


def _required_missing(required_fields: Sequence[FieldDef], state: Mapping[str, Any]) -> List[str]:
    missing: List[str] = []
    for field in required_fields:
        store_key = field.write_key or field.key
        value = state.get(store_key)
        if not _has_value(value):
            missing.append(field.label)
    return missing


def _apply_step_effects(step: StepDef, state: Dict[str, Any]) -> None:
    if not step.fields:
        return
    flags = state.setdefault("flags", {})
    for field in step.fields:
        if not field.effects:
            continue
        store_key = field.write_key or field.key
        value = state.get(store_key)
        _apply_effects(field, value, flags)


def _apply_effects(field: FieldDef, value: Any, flags: Dict[str, Any]) -> None:
    if not field.effects:
        return
    values: List[str] = []
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = [str(v) for v in value]
    elif value is not None:
        values = [str(value)]
    for effect in field.effects:
        triggers = effect.get("when_value_in", [])
        if not triggers:
            continue
        if _effect_triggered(values, triggers):
            flag_key = effect.get("set_flag")
            if flag_key:
                flags[flag_key] = True
                message = effect.get("flag_message")
                if message:
                    flags[f"{flag_key}_message"] = message


def _display_value(field: FieldDef, value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, tuple, set)):
        if field.options:
            mapping = {
                str(opt.get("value", opt.get("label"))): str(opt.get("label", opt.get("value")))
                for opt in (field.options or [])
            }
            return ", ".join(mapping.get(str(v), str(v)) for v in value if str(v))
        return ", ".join(str(v) for v in value if str(v))
    if field.options:
        lookup = {
            str(opt.get("value", opt.get("label"))): str(opt.get("label", opt.get("value")))
            for opt in (field.options or [])
        }
        return lookup.get(str(value), str(value))
    return str(value)


def _find_field(config: ModuleConfig, key: str) -> Optional[FieldDef]:
    for step in config.steps:
        for field in step.fields:
            if (field.write_key or field.key) == key:
                return field
    return None


def _get_recommendation(mod: Dict[str, Any], config: ModuleConfig) -> Optional[str]:
    """Get recommendation text from outcomes or module state."""
    # Try to get from outcomes first (preferred)
    outcome_key = f"{config.state_key}._outcomes"
    outcomes = st.session_state.get(outcome_key, {})
    
    # GCP v4 uses "tier" field (new system)
    tier = outcomes.get("tier")
    if tier:
        # Special handling for independent tier - more helpful message
        if tier.lower() == "independent":
            return "Good for now! If things change, consider In-Home Care."
        
        mapping = {
            "in_home": "In-Home Care with Support",
            "assisted_living": "Assisted Living",
            "memory_care": "Memory Care",
        }
        pretty = mapping.get(tier.lower(), tier.replace("_", " ").title())
        return f"Based on your answers, we recommend {pretty}."
    
    # Legacy modules use "recommendation" field
    recommendation = outcomes.get("recommendation")
    if recommendation:
        # If the recommendation is already properly formatted (contains capitals or special chars),
        # use it as-is (this is the case for new logic_v3 output)
        if any(c.isupper() for c in recommendation) or "/" in recommendation or "-" in recommendation:
            return f"Based on your answers, we recommend {recommendation}."
        
        # Otherwise, normalize the recommendation key for backward compatibility
        rec_key = recommendation.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        
        # CRITICAL: Map recommendation to display name - ONLY 5 allowed tiers
        mapping = {
            "no_care_needed": "No Care Needed",
            "in_home": "In-Home Care",
            "in_home_care": "In-Home Care",
            "assisted_living": "Assisted Living",
            "memory_care": "Memory Care",
            "memory_care_high_acuity": "Memory Care (High Acuity)",
        }
        
        pretty = mapping.get(rec_key)
        if not pretty:
            # Fallback: title case the recommendation
            pretty = recommendation.replace("_", " ").replace("/", " / ").title()
        
        return f"Based on your answers, we recommend {pretty}."
    
    # Fallback: try module state
    text = str(mod.get("recommendation_text", "")).strip()
    if text:
        if text.lower().startswith("based on your answers"):
            return text
        return f"Based on your answers, we recommend {text}."

    tier = str(mod.get("care_tier_label") or mod.get("care_tier") or "").strip()
    if not tier:
        return None
    # CRITICAL: Map tier to display name - ONLY 5 allowed tiers
    mapping = {
        "no_care_needed": "No Care Needed",
        "in_home": "In-Home Care",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)",
    }
    pretty = mapping.get(tier.lower(), tier.replace("_", " ").title())
    return f"Based on your answers, we recommend {pretty}."


def _render_confidence_improvement(outcomes: Dict[str, Any], config: ModuleConfig, state: Dict[str, Any]) -> None:
    """Render confidence improvement guidance on results page.
    
    Redesigned as split cards showing progress and clarity with actionable guidance.
    
    Args:
        outcomes: Outcome data with confidence and scoring details
        config: Module configuration
        state: Module state with user answers
    """
    confidence = outcomes.get("confidence", 1.0)
    confidence_pct = int(confidence * 100)
    
    # Only show improvement guidance if confidence < 100%
    if confidence_pct >= 100:
        return
    
    # Get scoring details
    tier_score = outcomes.get("tier_score", 0)
    tier = outcomes.get("tier", "")
    
    # Calculate completeness
    answered_count = 0
    total_count = 0
    unanswered_questions = []
    
    for step in config.steps:
        if not step.fields:  # Skip intro/results pages
            continue
        for field in step.fields:
            if field.required:
                total_count += 1
                value = state.get(field.key)
                if value is not None and value != "" and value != []:
                    answered_count += 1
                else:
                    unanswered_questions.append({
                        'label': field.label,
                        'step_id': step.id,
                        'step_title': step.title
                    })
    
    completeness = answered_count / total_count if total_count > 0 else 1.0
    completeness_pct = int(completeness * 100)
    
    # Determine tier boundaries for clarity
    tier_thresholds = {
        "no_care_needed": (0, 8),
        "in_home": (9, 16),
        "assisted_living": (17, 24),
        "memory_care": (25, 39),
        "memory_care_high_acuity": (40, 100),
    }
    
    boundary_clarity = 100  # Default
    clarity_message = "Clear"
    if tier in tier_thresholds:
        min_score, max_score = tier_thresholds[tier]
        distance_from_min = tier_score - min_score
        distance_from_max = max_score - tier_score
        distance_from_boundary = min(distance_from_min, distance_from_max)
        boundary_clarity = min(int((distance_from_boundary / 3.0) * 100), 100)
        
        if boundary_clarity >= 80:
            clarity_message = "Strong — well within tier"
        elif boundary_clarity >= 50:
            clarity_message = "Moderate — some distance from boundary"
        else:
            clarity_message = "Near boundary — consider reviewing"
    
    st.markdown("### 💡 Improve Your Confidence")
    
    st.markdown("""
    <p style="font-size: 14px; color: #64748b; margin-bottom: 20px;">
        Your confidence score is based on how complete your answers are and how clear your tier placement is.
    </p>
    """, unsafe_allow_html=True)
    
    # Split into two horizontal cards
    col1, col2 = st.columns(2)
    
    with col1:
        # Progress card
        completeness_color = "#22c55e" if completeness_pct >= 90 else "#f59e0b" if completeness_pct >= 70 else "#ef4444"
        
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            height: 100%;
        ">
            <div style="font-size: 12px; color: #64748b; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 12px;">
                QUESTION COMPLETENESS
            </div>
            <div style="font-size: 32px; font-weight: 600; color: {completeness_color}; margin-bottom: 8px;">
                {completeness_pct}%
            </div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 12px;">
                {answered_count} of {total_count} questions answered
            </div>
            <div style="
                background: #f1f5f9;
                height: 8px;
                border-radius: 4px;
                overflow: hidden;
            ">
                <div style="
                    background: {completeness_color};
                    height: 100%;
                    width: {completeness_pct}%;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Clarity card
        clarity_color = "#22c55e" if boundary_clarity >= 80 else "#f59e0b" if boundary_clarity >= 50 else "#ef4444"
        
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            height: 100%;
        ">
            <div style="font-size: 12px; color: #64748b; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 12px;">
                RECOMMENDATION CLARITY
            </div>
            <div style="font-size: 32px; font-weight: 600; color: {clarity_color}; margin-bottom: 8px;">
                {boundary_clarity}%
            </div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 12px;">
                {clarity_message}
            </div>
            <div style="
                background: #f1f5f9;
                height: 8px;
                border-radius: 4px;
                overflow: hidden;
            ">
                <div style="
                    background: {clarity_color};
                    height: 100%;
                    width: {boundary_clarity}%;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Guidance section below both cards
    if completeness_pct < 100 or boundary_clarity < 80:
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        with st.expander("🔍 How to Improve Your Confidence", expanded=(completeness_pct < 90)):
            if completeness_pct < 100 and unanswered_questions:
                st.markdown("**📝 Complete Unanswered Questions**")
                st.markdown(f"You have {len(unanswered_questions)} unanswered question(s). Answering them will improve your confidence score.")
                
                if len(unanswered_questions) <= 5:
                    for q in unanswered_questions:
                        st.markdown(f"- {q['label']}")
            
            if boundary_clarity < 80 and tier in tier_thresholds:
                st.markdown("**📊 Your Score is Near a Tier Boundary**")
                min_score, max_score = tier_thresholds[tier]
                st.markdown(f"""
                Your current score is **{tier_score} points**, which places you in the **{tier.replace('_', ' ').title()}** tier (range: {min_score}-{max_score} points).
                
                You're close to a tier boundary, which means small changes in your answers could affect your recommendation. Consider reviewing your responses for accuracy.
                """)
            
            # Go back button
            st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
            if st.button("← Review Your Answers", type="secondary", use_container_width=True):
                # Go back to first question step
                for idx, step in enumerate(config.steps):
                    if step.fields and not step.id.startswith("intro"):
                        st.session_state[f"{config.state_key}._step"] = idx
                        _rerun_app()
                        break



def _render_results_view(mod: Dict[str, Any], config: ModuleConfig) -> None:
    """Render results as guided narrative: outcome → why → how to improve → next steps."""
    
    # Get data
    outcome_key = f"{config.state_key}._outcomes"
    outcomes = st.session_state.get(outcome_key, {})
    recommendation = _get_recommendation(mod, config)
    confidence = outcomes.get("confidence", 1.0)
    confidence_pct = int(confidence * 100)
    tier = outcomes.get("tier", "")
    tier_score = outcomes.get("tier_score", 0)
    
    # ========================================
    # 1. TOP SECTION - "Your Recommendation" (Hero Card)
    # ========================================
    
    # Determine confidence badge
    if confidence_pct >= 90:
        confidence_label = "Strong"
        confidence_color = "#22c55e"  # Green
    elif confidence_pct >= 70:
        confidence_label = "Moderate"
        confidence_color = "#f59e0b"  # Amber
    else:
        confidence_label = "Building"
        confidence_color = "#ef4444"  # Red
    
    # Extract recommendation text (clean)
    if recommendation and "recommend" in recommendation.lower():
        rec_text = recommendation.split("recommend")[-1].strip().rstrip(".")
    elif recommendation:
        rec_text = recommendation
    else:
        rec_text = "Your Guided Care Plan"
    
    # Add CSS classes for spacing control
    st.markdown(f"""
    <div class="gcp-rec-card" style="
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 32px;
        margin: 14px 0 20px 0;
        text-align: center;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
    ">
        <div style="font-size: 14px; color: #64748b; font-weight: 500; letter-spacing: 0.5px; margin-bottom: 12px;">
            YOUR CARE RECOMMENDATION
        </div>
        <div style="font-size: 28px; font-weight: 600; color: #1e293b; margin-bottom: 16px; line-height: 1.3;">
            {H(rec_text)}
        </div>
        <div style="display: flex; align-items: center; justify-content: center; gap: 24px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 13px; color: #64748b;">Confidence:</span>
                <span style="
                    background: {confidence_color}15;
                    color: {confidence_color};
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 14px;
                ">{confidence_pct}% • {confidence_label}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================
    # 2. REASSURANCE SECTION (moved up - directly under recommendation)
    # ========================================
    
    st.markdown("""
    <div class="gcp-reassure" style="
        background: #fff8e1;
        border: 1px solid #fde68a;
        border-radius: 10px;
        padding: 10px 12px;
        margin: 12px 0 24px 0;
        color: #92400e;
        display: flex;
        gap: 0.6rem;
        align-items: flex-start;
    ">
        <span style="font-size: 1.1rem;">💬</span>
        <span style="font-size: 14px; line-height: 1.6;">
            Your care plan can evolve as your needs change. 
            You can retake the assessment anytime to get an updated recommendation.
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================
    # 3. DETAILS SECTION - "Why You Got This Recommendation"
    # ========================================
    
    st.markdown("### 🔍 Why You Got This Recommendation")
    
    summary_data = outcomes.get("summary", {})
    points = summary_data.get("points", [])
    
    if points:
        # Use detailed summary points from derive() function
        # Group them visually with icons
        _render_recommendation_details(points)
    else:
        # Fallback to basic summary
        _render_results_summary(mod, config)
    
    st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)
    
    # ========================================
    # 4. INSIGHTS SECTION - "Improve Your Confidence"
    # ========================================
    
    if confidence_pct < 100:
        _render_confidence_improvement(outcomes, config, mod)
        st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)
    
    # ========================================
    # 5. NEXT ACTIONS SECTION - "What Happens Next"
    # ========================================
    
    st.markdown("""
    <div class="gcp-next">
        <div class="gcp-next__title" style="font-weight: 700; margin: 10px 0 6px; color: #0f172a; font-size: 1.05rem;">
            What Happens Next
        </div>
        <p style="font-size: 14px; color: #64748b; margin-bottom: 20px; line-height: 1.6;">
            Now that you have a recommendation, the next step is the Cost Planner. 
            You'll get a quick estimate of monthly care costs, adjusted for your ZIP code 
            and any care needs in your plan.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    _render_results_ctas_once(config)


def _render_results_summary(state: Dict[str, Any], config: ModuleConfig) -> None:
    bullets: List[str] = []

    def add_bullet(prefix: str, field_key: str, join: bool = False) -> None:
        field = _find_field(config, field_key)
        if not field:
            return
        value = state.get(field_key)
        if not _has_value(value):
            return
        text = _display_value(field, value)
        if join and isinstance(value, (list, tuple, set)):
            text = ", ".join(str(v) for v in value if str(v))
        bullets.append(f"{prefix} {text}")

    add_bullet("Independence snapshot:", "help_overall")
    add_bullet("Cognitive notes:", "memory_changes")
    add_bullet("Medication complexity:", "meds_complexity")

    chronic_chunks: List[str] = []
    chronic_field = _find_field(config, "chronic_conditions")
    chronic_value = state.get("chronic_conditions")
    if chronic_field and _has_value(chronic_value):
        chronic_chunks.append(_display_value(chronic_field, chronic_value))

    additional_value = state.get("additional_conditions")
    if isinstance(additional_value, (list, tuple, set)):
        chronic_chunks.extend(str(v) for v in additional_value if str(v))
    elif additional_value:
        chronic_chunks.append(str(additional_value))

    if chronic_chunks:
        bullets.append(f"Chronic conditions: {', '.join(chronic_chunks)}")

    flags = state.get("flags", {})
    if isinstance(flags, dict) and flags.get("emotional_followup"):
        message = (
            flags.get("emotional_followup_message")
            or "Emotional well-being: follow-up recommended."
        )
        bullets.append(message)

    add_bullet("Caregiver hours/day:", "hours_per_day")
    add_bullet("Location/access:", "isolation")

    if not bullets:
        return

    items = "".join(f"<li>{H(b)}</li>" for b in bullets)
    st.markdown(f"<ul>{items}</ul>", unsafe_allow_html=True)


def _render_recommendation_details(points: List[str]) -> None:
    """Render recommendation details in a clean, icon-based grid.
    
    Groups summary points by category with visual icons.
    """
    # Categorize points by keyword detection
    categories = {
        "cognitive": {"icon": "🧠", "label": "Cognitive Health", "points": []},
        "medication": {"icon": "💊", "label": "Medications", "points": []},
        "mobility": {"icon": "🦽", "label": "Mobility & Safety", "points": []},
        "health": {"icon": "❤️", "label": "Health Conditions", "points": []},
        "daily": {"icon": "🏠", "label": "Daily Living", "points": []},
        "social": {"icon": "👥", "label": "Social & Support", "points": []},
    }
    
    # Categorize each point
    for point in points:
        point_lower = point.lower()
        categorized = False
        
        # Cognitive
        if any(word in point_lower for word in ["memory", "cognitive", "confusion", "dementia", "alzheimer"]):
            categories["cognitive"]["points"].append(point)
            categorized = True
        
        # Medication
        if any(word in point_lower for word in ["medication", "prescription", "med", "drug"]):
            categories["medication"]["points"].append(point)
            categorized = True
        
        # Mobility
        if any(word in point_lower for word in ["mobility", "fall", "walk", "wheelchair", "transfer", "balance"]):
            categories["mobility"]["points"].append(point)
            categorized = True
        
        # Health conditions
        if any(word in point_lower for word in ["chronic", "condition", "disease", "illness", "diabetes", "heart"]):
            categories["health"]["points"].append(point)
            categorized = True
        
        # Daily living
        if any(word in point_lower for word in ["adl", "bathing", "dressing", "eating", "toileting", "grooming", "hygiene"]):
            categories["daily"]["points"].append(point)
            categorized = True
        
        # Social
        if any(word in point_lower for word in ["social", "isolation", "alone", "caregiver", "family", "support"]):
            categories["social"]["points"].append(point)
            categorized = True
        
        # If not categorized, add to daily living as default
        if not categorized:
            categories["daily"]["points"].append(point)
    
    # Render only categories that have points
    active_categories = [cat for cat in categories.values() if cat["points"]]
    
    if not active_categories:
        return
    
    # Determine grid columns based on count
    num_cols = min(len(active_categories), 3)
    cols = st.columns(num_cols)
    
    for idx, category in enumerate(active_categories):
        with cols[idx % num_cols]:
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                min-height: 120px;
            ">
                <div style="
                    font-size: 24px;
                    margin-bottom: 8px;
                ">{category["icon"]}</div>
                <div style="
                    font-size: 12px;
                    font-weight: 600;
                    color: #64748b;
                    letter-spacing: 0.5px;
                    margin-bottom: 12px;
                ">{category["label"].upper()}</div>
                <div style="font-size: 13px; color: #475569; line-height: 1.5;">
                    {"<br>".join([f"• {H(p)}" for p in category["points"]])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Add collapsible "View More Details" if there are many points
    if len(points) > 6:
        with st.expander("📋 View Full Details", expanded=False):
            items = "".join(f"<li style='margin-bottom: 8px;'>{H(p)}</li>" for p in points)
            st.markdown(f"<ul style='line-height: 1.6;'>{items}</ul>", unsafe_allow_html=True)


def _render_results_ctas_once(config: ModuleConfig) -> None:
    """Render action buttons on results page."""
    state_key = config.state_key
    
    st.markdown('<div class="sn-app mod-actions">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Review Answers button - navigate back to first question
        if st.button(
            "← Review Your Answers",
            key="_results_review",
            type="secondary",
            use_container_width=True,
            help="Go back to review or update your answers"
        ):
            # Navigate back to first question (step 0)
            st.session_state[f"{state_key}._step"] = 0
            
            # Update tile state
            tiles = st.session_state.setdefault("tiles", {})
            tile_state = tiles.setdefault(config.product, {})
            tile_state["last_step"] = 0
            
            safe_rerun()
    
    with col2:
        # Back to Hub button
        if st.button(
            "← Back to Hub",
            key="_results_back_hub",
            type="secondary",
            use_container_width=True,
            help="Return to the main hub"
        ):
            from core.nav import route_to
            route_to("hub_concierge")
    
    st.markdown('</div>', unsafe_allow_html=True)


def _effect_triggered(values: Sequence[str], triggers: Sequence[str]) -> bool:
    normalized_values = [v.strip().lower() for v in values if str(v).strip()]
    normalized_triggers = [t.strip().lower() for t in triggers if str(t).strip()]
    for trigger in normalized_triggers:
        for current in normalized_values:
            if current == trigger or trigger in current:
                return True
    return False


def _rerun_app() -> None:
    rerun = getattr(st, "rerun", None)
    if callable(rerun):
        rerun()
        return
    legacy_rerun = getattr(st, "experimental_rerun", None)
    if callable(legacy_rerun):
        legacy_rerun()
        return
    raise RuntimeError("Streamlit rerun is unavailable in this environment.")


def _render_navi_guide_bar(
    config: ModuleConfig,
    step: StepDef,
    state: Dict[str, Any],
    step_index: int,
    progress_total: int
) -> None:
    """Render Navi's persistent guide bar at top of module.
    
    PRIORITY: Use step.navi_guidance if embedded in module JSON.
    FALLBACK: Use navi_dialogue.json for legacy modules.
    
    Args:
        config: Module configuration
        step: Current step definition
        state: Module state
        step_index: Current step index
        progress_total: Total progress-eligible steps
    """
    try:
        from core.ui import render_navi_guide_bar
        from core.mcip import MCIP
        
        # Check if step has embedded navi_guidance (new system)
        if step.navi_guidance:
            message = step.navi_guidance
        # Check if module has intro/outro guidance
        elif step_index == 0 and config.navi_intro:
            message = config.navi_intro
        elif (step_index == len(config.steps) - 1 or 
              (config.results_step_id and step.id == config.results_step_id)) and config.navi_outro:
            message = config.navi_outro
        else:
            # Fallback to dialogue JSON (legacy system)
            from core.navi_dialogue import NaviDialogue
            
            # Map product key to dialogue key
            product_to_dialogue = {
                "gcp_v4": "gcp",
                "cost_v2": "cost_planner",
                "pfma_v2": "pfma"
            }
            
            dialogue_product = product_to_dialogue.get(config.product, config.product)
            
            # Determine module key from step
            is_first_step = (step_index == 0)
            is_last_step = (step_index == len(config.steps) - 1)
            is_results = config.results_step_id and step.id == config.results_step_id
            
            if is_first_step:
                module_key = "intro"
            elif is_results or is_last_step:
                module_key = "complete"
            else:
                module_key = step.id if step.id else "intro"
            
            # Build context from MCIP
            context = {}
            try:
                care_rec = MCIP.get_care_recommendation()
                if care_rec:
                    context["tier"] = care_rec.tier
                    context["confidence"] = int(care_rec.confidence * 100)
            except:
                pass
            
            try:
                financial = MCIP.get_financial_profile()
                if financial:
                    context["monthly_cost"] = f"${financial.estimated_monthly_cost:,.0f}"
                    context["runway_months"] = financial.runway_months
            except:
                pass
            
            # Get message from dialogue JSON
            message = NaviDialogue.get_module_message(dialogue_product, module_key, context)
        
        if not message:
            return
        
        # Calculate current progress step
        progress_steps = [s for s in config.steps if s.show_progress]
        current_progress = sum(1 for s in progress_steps if config.steps.index(s) < step_index) + (1 if step.show_progress else 0)
        
        # Determine if we should show progress
        is_first_step = (step_index == 0)
        is_results = config.results_step_id and step.id == config.results_step_id
        show_progress_bar = (progress_total > 0 and not is_first_step and not is_results)
        
        # Get color from message or use default
        color = message.get("color", "#8b5cf6")
        
        render_navi_guide_bar(
            text=message.get("text", ""),
            subtext=message.get("subtext"),
            icon=message.get("icon", "🤖"),
            show_progress=show_progress_bar,
            current_step=current_progress if current_progress > 0 else None,
            total_steps=progress_total if progress_total > 0 else None,
            color=color
        )
    except Exception as e:
        # Silently fail if Navi can't render (don't break module flow)
        import sys
        print(f"[WARN] Navi guide bar failed: {e}", file=sys.stderr)


__all__ = ["run_module"]
