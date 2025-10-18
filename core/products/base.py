from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import streamlit as st

from core.forms import progress_rail, progress_steps
from core.modules.base import load_module_manifest, render_module_inputs
from core.nav import route_to
from core.products.contract import set_module_outcome, set_outcome, set_progress


@dataclass
class ModuleSpec:
    slug: str
    plugin: str
    func: str = "derive"


ICON_MAP = {
    "person": "👤",
    "medication": "💊",
    "mobility": "🦽",
    "home": "🏠",
    "brain": "🧠",
    "check": "✅",
}


class BaseProduct:
    def __init__(
        self,
        product: str,
        modules: list[ModuleSpec],
        aggregator: Callable[[dict[str, Any]], dict[str, Any]],
        *,
        title: str = "",
    ):
        self.product = product
        self.modules = modules
        self.aggregator = aggregator
        self.title = title or "Product"
        st.session_state.setdefault(
            product,
            {"progress": 0, "outcome": {}, "modules": {}, "step": 0},
        )

    @property
    def state(self) -> dict[str, Any]:
        return st.session_state[self.product]

    def render(self) -> None:
        self._update_progress()
        step = self.state.get("step", 0)
        total_steps = len(self.modules) + 1

        render_shell_start(self.title, active_route=self.product)

        # Calculate actual progress including current section fraction
        steps = len(self.modules)
        completed = min(step, steps)
        fraction = 0.0

        if step >= steps:
            # On summary page - show 100%
            actual_progress = float(steps)
        elif completed < steps and self.modules:
            # In a module - calculate fractional progress
            current_spec = self.modules[completed]
            mod_state = self.state.get("modules", {}).get(current_spec.slug, {})
            progress = mod_state.get("progress", {})
            fraction = float(progress.get("fraction", 0.0))
            actual_progress = completed + fraction
        else:
            # Fallback
            actual_progress = float(completed)

        # Progress bar fills based on module completion (summary = 100%)
        # total_steps includes summary, so we divide by module count, not total_steps
        progress_rail(actual_progress, steps)

        if step < len(self.modules):
            self._render_module(self.modules[step])
        else:
            self._render_summary()

        render_shell_end()

    def _render_module(self, spec: ModuleSpec) -> None:
        manifest = load_module_manifest(self.product, spec.slug)
        sections = manifest.get("sections") or []
        if not sections:
            sections = [
                {
                    "id": "_default",
                    "title": manifest.get("module", {}).get("display", {}).get("title", "Module"),
                    "type": "form",
                    "questions": manifest.get("inputs", []),
                }
            ]

        total_sections = max(1, len(sections))
        mod_state = self.state["modules"].setdefault(
            spec.slug,
            {
                "answers": {},
                "outcome": {},
                "section_index": 0,
                "progress": {"current": 0, "total": total_sections, "fraction": 0.0},
            },
        )
        mod_state.setdefault("section_index", 0)
        mod_state.setdefault("progress", {"current": 0, "total": total_sections, "fraction": 0.0})

        index = max(0, min(mod_state.get("section_index", 0), total_sections - 1))
        section = sections[index]
        section_type = section.get("type", "form")

        progress_steps(index, total_sections)

        inputs = section.get("questions", []) if section_type == "form" else []
        answers, required_visible, stats = render_module_inputs(
            self.product,
            spec.slug,
            manifest,
            mod_state.get("answers", {}),
            inputs=inputs,
        )
        mod_state["answers"] = answers

        # Calculate section progress (how far through current section based on answered questions)
        section_completion = 0.0
        if section_type == "form":
            section_total = float(stats.get("section_total", 0))
            section_answered = float(stats.get("section_answered", 0))
            if section_total > 0:
                section_completion = section_answered / section_total
        else:
            # Non-form sections (info, results) are considered complete when viewed
            section_completion = 1.0

        # Calculate overall module progress
        # fraction = (completed_sections + current_section_progress) / total_sections
        fraction = (index + section_completion) / total_sections if total_sections else 0.0

        mod_state["progress"] = {
            "current": index,
            "total": total_sections,
            "fraction": fraction,
            "section_completion": section_completion,
        }
        mod_state["stats"] = stats

        title = section.get("title")
        subtitle = section.get("subtitle")
        if title:
            st.markdown(f"#### {title}")
        if subtitle:
            st.caption(subtitle)

        if section_type == "info":
            body = section.get("body")
            if isinstance(body, list):
                for block in body:
                    st.markdown(block)
            elif isinstance(body, str):
                st.markdown(body)
        elif section_type == "results":
            body = section.get("body")
            if body:
                if isinstance(body, list):
                    for block in body:
                        st.markdown(block)
                else:
                    st.markdown(body)

        required_complete = all(_has_response(answers.get(key)) for key in required_visible)

        actions = section.get("actions") or []
        if not actions:
            actions = [{"label": "Continue", "action": "next"}]
            if index > 0:
                actions.append({"label": "Back", "action": "prev"})

        pending_next = st.session_state.pop("_next_section", False)
        action: tuple[str, Any] | None = None
        if pending_next:
            if required_complete:
                action = ("_next_section", None)
            else:
                st.warning("Please complete the required fields before continuing.")

        button_action = self._render_actions(
            spec.slug, index, actions, disabled_next=not required_complete
        )
        if action is None:
            action = button_action

        if action:
            command, value = action
            if command == "_next_section":
                if not required_complete:
                    st.warning("Please complete the required fields before continuing.")
                else:
                    mod_state["section_index"] = index + 1
                    if mod_state["section_index"] >= total_sections:
                        outcome = self._normalize_module_result(
                            self._invoke_module(spec, manifest, answers)
                        )
                        mod_state["outcome"] = outcome
                        set_module_outcome(self.product, spec.slug, outcome)
                        mod_state["progress"] = {
                            "current": total_sections,
                            "total": total_sections,
                            "fraction": 1.0,
                        }
                        self.state["step"] += 1
                    else:
                        mod_state["progress"] = {
                            "current": mod_state["section_index"],
                            "total": total_sections,
                            "fraction": mod_state["section_index"] / total_sections,
                        }
                    self._update_progress()
                    st.rerun()
            elif command == "_prev_section":
                mod_state["section_index"] = max(0, index - 1)
                self._update_progress()
                st.rerun()
            elif command == "_nav_route" and value:
                route_to(str(value))
            elif command == "_restart":
                mod_state["section_index"] = 0
                mod_state["answers"] = {}
                mod_state["outcome"] = {}
                mod_state["progress"] = {"current": 0, "total": total_sections, "fraction": 0.0}
                self._update_progress()
                st.rerun()
            elif command == "_save_exit":
                self.state["step"] = len(self.modules)
                self._update_progress()
                st.rerun()
            elif command == "_submit":
                if not required_complete:
                    st.warning("Please complete the required fields before submitting.")
                else:
                    mod_state["section_index"] = total_sections
                    outcome = self._normalize_module_result(
                        self._invoke_module(spec, manifest, answers)
                    )
                    mod_state["outcome"] = outcome
                    set_module_outcome(self.product, spec.slug, outcome)
                    mod_state["progress"] = {
                        "current": total_sections,
                        "total": total_sections,
                        "fraction": 1.0,
                    }
                    self.state["step"] += 1
                    self._update_progress()
                    st.rerun()

        self._update_progress()

    def _render_summary(self) -> None:
        outcome = self._normalize_module_result(self.aggregator(self.state.get("modules", {})))
        set_outcome(self.product, outcome)
        set_progress(self.product, 100)
        st.markdown("## Summary")
        tier = outcome.get("tier")
        if tier:
            st.markdown(f"**Recommendation: {tier}**")
        for point in outcome.get("points", []):
            st.markdown(f"- {point}")

    def _invoke_module(
        self, spec: ModuleSpec, manifest: dict[str, Any], answers: dict[str, Any]
    ) -> dict[str, Any]:
        module = importlib.import_module(spec.plugin)
        fn = getattr(module, spec.func)
        return fn(manifest, answers, {"product": self.product})

    def _render_actions(
        self,
        slug: str,
        section_index: int,
        actions: list[dict[str, Any]],
        *,
        disabled_next: bool,
    ) -> tuple[str, Any] | None:
        if not actions:
            return None
        cols = st.columns(len(actions))
        triggered: tuple[str, Any] | None = None
        for idx, action in enumerate(actions):
            label = action.get("label", "Continue")
            act_type = action.get("action", "next")
            command = self.ACTION_COMMANDS.get(act_type, act_type)
            disabled = False
            if command in {"_next_section", "_submit"} and disabled_next:
                disabled = True
            if command == "_prev_section" and section_index == 0:
                disabled = True
            key = f"{slug}_action_{section_index}_{idx}"
            with cols[idx]:
                if st.button(label, key=key, disabled=disabled):
                    triggered = (command, action.get("value"))
        return triggered

    def _update_progress(self) -> None:
        steps = len(self.modules)
        if steps <= 0:
            set_progress(self.product, 0)
            return

        completed = min(self.state.get("step", 0), steps)
        fraction = 0.0
        if completed < steps:
            current_spec = self.modules[completed]
            mod_state = self.state.get("modules", {}).get(current_spec.slug, {})
            progress = mod_state.get("progress", {})
            fraction = float(progress.get("fraction", 0.0))

        raw = int(round(100 * ((completed + fraction) / steps)))
        capped = min(99, max(0, raw))
        set_progress(self.product, capped)

    @staticmethod
    def _normalize_module_result(result: Any) -> dict[str, Any]:
        if not isinstance(result, dict):
            return {"tier": "N/A", "score": 0, "points": [str(result)]}
        tier = str(result.get("tier", "N/A"))
        score = result.get("score", 0)
        try:
            score = float(score)
        except Exception:
            score = 0
        points = result.get("points") or []
        if isinstance(points, str):
            points = [points]
        elif not isinstance(points, list):
            points = [str(points)]
        normalized = {"tier": tier, "score": score, "points": points}
        if "payload" in result:
            normalized["payload"] = result["payload"]
        return normalized

    ACTION_COMMANDS = {
        "next": "_next_section",
        "prev": "_prev_section",
        "route": "_nav_route",
        "save_exit": "_save_exit",
        "restart": "_restart",
        "submit": "_submit",
    }


def _has_response(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, tuple, set, dict)):
        return (
            any(_has_response(v) for v in value)
            if isinstance(value, (list, tuple))
            else bool(value)
        )
    return True
