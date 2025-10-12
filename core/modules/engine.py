from __future__ import annotations

import importlib
import time
from dataclasses import asdict
from html import escape as H
from typing import Any, Dict, List, Mapping, Optional, Sequence

import streamlit as st

from core.events import log_event

from . import components as components
from .layout import actions, bottom_summary, header
from .schema import FieldDef, ModuleConfig, OutcomeContract, StepDef


def run_module(config: ModuleConfig) -> Dict[str, Any]:
    """Run a module flow defined by ModuleConfig. Returns updated module state."""
    state_key = config.state_key
    st.session_state.setdefault(state_key, {})
    state = st.session_state[state_key]

    total_steps = len(config.steps)
    step_index = int(st.session_state.get(f"{state_key}._step", 0))
    step_index = min(step_index, total_steps - 1)
    step = config.steps[step_index]

    header(step_index, total_steps, step.title, step.subtitle)

    new_values = _render_fields(step, state)
    if new_values:
        state.update(new_values)

    is_results = config.results_step_id and step.id == config.results_step_id
    if is_results:
        _ensure_outcomes(config, state)
        _render_results_view(state, config)
        return state

    progress = _update_progress(config, state, step, step_index)

    _render_summary(step, state)

    required_fields = _required_fields(step, state)
    missing = _required_missing(required_fields, state)

    next_clicked, skip_clicked = actions(step.next_label, step.skip_label)
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
    total = len(config.steps) or 1
    if config.results_step_id and step.id == config.results_step_id:
        progress = 1.0
    else:
        required = _required_fields(step, state)
        if required:
            completed = sum(1 for f in required if _has_value(state.get(f.write_key or f.key)))
            fraction = completed / len(required)
        else:
            fraction = 1.0
        progress = min(1.0, max(0.0, (step_index + fraction) / total))

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
    if step.show_bottom_bar and step.summary_keys:
        field_map = {f.write_key or f.key: f for f in step.fields}
        items = {
            key: _format_summary_value(state.get(key), field_map.get(key))
            for key in step.summary_keys
            if key in state
        }
        bottom_summary(items)


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

    if next_clicked and config.results_step_id and step.id == config.results_step_id:
        _emit(
            "product.completed",
            {"product": config.product, "state_key": config.state_key},
        )

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
                outcome = OutcomeContract(**result)
        except Exception:
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


def _get_recommendation(mod: Dict[str, Any]) -> Optional[str]:
    text = str(mod.get("recommendation_text", "")).strip()
    if text:
        if text.lower().startswith("based on your answers"):
            return text
        return f"Based on your answers, we recommend {text}."

    tier = str(mod.get("care_tier_label") or mod.get("care_tier") or "").strip()
    if not tier:
        return None
    mapping = {
        "stay_home": "Stay Home",
        "in_home": "In Home",
        "assisted_living": "Assisted Living",
        "memory_care": "Memory Care",
        "memory_care_high_acuity": "Memory Care (High Acuity)",
    }
    pretty = mapping.get(tier.lower(), tier.replace("_", " ").title())
    return f"Based on your answers, we recommend {pretty}."


def _render_results_view(mod: Dict[str, Any], config: ModuleConfig) -> None:
    recommendation = _get_recommendation(mod)
    if recommendation:
        st.markdown(f"<h3 class='h3 rec-line'>{H(recommendation)}</h3>", unsafe_allow_html=True)

    _render_results_summary(mod, config)
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


def _render_results_ctas_once(config: ModuleConfig) -> None:
    flag_key = f"{config.state_key}.__results_cta_once"
    if st.session_state.get(flag_key):
        return
    st.session_state[flag_key] = True
    st.markdown(
        """
        <div class="cta-rail">
          <a class="btn btn--primary" href="/product/cost">Continue to Cost Planner</a>
          <a class="btn btn--ghost" href="/hub/concierge">Return to Care Hub</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


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


__all__ = ["run_module"]
