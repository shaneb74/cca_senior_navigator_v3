from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import streamlit as st

from core.forms import chip_group


def _pairs(opts: Sequence[Dict[str, Any]]) -> List[Tuple[str, Any]]:
    return [(opt.get("label", ""), opt.get("value")) for opt in (opts or [])]


def render_input(q: Dict[str, Any], *, current: Optional[Any]) -> Any:
    t = q.get("type", "string")
    sel = q.get("select", "single")
    ui = q.get("ui", {}) or {}
    widget = ui.get("widget", "chip")
    label = q.get("label", "")
    help_text = q.get("help")
    options = q.get("options", [])
    key = f"{st.session_state.get('_module_slug','mod')}.{q['key']}"

    # prepare value/label maps once
    values: List[Any] = []
    v2l: Dict[Any, str] = {}
    for opt in options:
        val = opt.get("value", opt.get("label"))
        values.append(val)
        v2l[val] = opt.get("label", str(val))

    # SINGLE SELECT
    if sel == "single":
        if widget in ("chip", "radio"):
            pairs = [
                (opt.get("label", str(opt.get("value"))), opt.get("value", opt.get("label")))
                for opt in options
            ]
            return chip_group(key, pairs, label=label, help_text=help_text)

        if widget == "select":
            if not values:
                return current
            cur = current if current in values else None
            index = values.index(cur) if cur in values else 0
            return st.selectbox(
                label,
                values,
                index=index,
                format_func=lambda v: v2l.get(v, v),
                help=help_text,
                key=key,
            )

        if widget == "date":
            dt = st.date_input(label, help=help_text, key=key)
            return str(dt) if dt else None

        if widget == "currency":
            val = st.number_input(label, value=float(current or 0), step=100.0, help=help_text, key=key)
            return round(val, 2)

        if widget == "number":
            kwargs: Dict[str, Any] = {}
            if "min" in ui:
                kwargs["min_value"] = ui["min"]
            if "max" in ui:
                kwargs["max_value"] = ui["max"]
            if "step" in ui:
                kwargs["step"] = ui["step"]
            return st.number_input(label, value=current or 0, help=help_text, key=key, **kwargs)

        if widget in ("text","textarea"):
            fn = st.text_area if widget == "textarea" else st.text_input
            return fn(label, value=current or "", help=help_text, key=key)

        # fallback to chip single
        pairs = [
            (opt.get("label", str(opt.get("value"))), opt.get("value", opt.get("label")))
            for opt in options
        ]
        return chip_group(key, pairs, label=label, help_text=help_text)

    # MULTI SELECT
    if sel == "multi":
        if not values:
            return []
        if current is None:
            current_list: List[Any] = []
        elif isinstance(current, list):
            current_list = current
        else:
            current_list = [current]
        defaults = [v for v in current_list if v in values]
        return st.multiselect(
            label,
            values,
            default=defaults,
            format_func=lambda v: v2l.get(v, v),
            help=help_text,
            key=key,
        )

    # BOOLEAN
    if t == "boolean" or widget == "checkbox":
        return st.checkbox(label, value=bool(current), help=help_text, key=key)

    # fallback
    return current
