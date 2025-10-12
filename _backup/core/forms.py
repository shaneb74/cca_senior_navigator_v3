from __future__ import annotations

from typing import Optional

import streamlit as st


def _ensure_container(label: str):
    if label:
        st.markdown(f"<p><strong>{label}</strong></p>", unsafe_allow_html=True)


def pill_row(
    key: str,
    options: list[str],
    value: Optional[str] = None,
    label_to_value: Optional[dict] = None,
):
    st.markdown('<div class="choice-pills">', unsafe_allow_html=True)
    current = st.session_state.get(key, value or "")
    current_label = next(
        (k for k, v in (label_to_value or {}).items() if v == current), current
    )
    for opt in options:
        selected_class = " is-selected" if current_label == opt else ""
        st.markdown(
            f'<div class="pill{selected_class}" style="display: inline-block; margin-right: 5px;">',
            unsafe_allow_html=True,
        )
        if st.button(opt, key=f"{key}::{opt}"):
            st.session_state[key] = opt
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    selected = st.session_state.get(key, value or "")
    if label_to_value:
        st.session_state[key] = label_to_value.get(selected, selected)
    return selected


def pills(key: str, options: list[str], label_to_value: Optional[dict] = None):
    stored_value = st.session_state.get(key)
    default_label = next(
        (k for k, v in (label_to_value or {}).items() if v == stored_value), None
    )
    return pill_row(key, options, value=default_label, label_to_value=label_to_value)


def text(key: str, placeholder: str = ""):
    return st.text_input("", placeholder=placeholder, key=key)


def multiselect(key: str, options: list[str], default: list = None):
    if default is not None and key not in st.session_state:
        st.session_state[key] = default
    return st.multiselect("Select options", options, key=key)


def render_question(q: dict):
    q_type = q["type"]
    label = q.get("label", "")
    _ensure_container(label)
    options = q.get("options", [])
    # Normalize options to list of strings (labels)
    normalized_options = []
    label_to_value = {}
    for opt in options:
        if isinstance(opt, dict):
            opt_label = opt.get("label", "")
            opt_value = opt.get("value", opt_label)
            normalized_options.append(opt_label)
            label_to_value[opt_label] = opt_value
        else:
            opt_str = str(opt)
            normalized_options.append(opt_str)
            label_to_value[opt_str] = opt_str
    if q_type == "single":
        stored_value = st.session_state.get(q["key"])
        default_label = next(
            (k for k, v in label_to_value.items() if v == stored_value), None
        )
        index = (
            normalized_options.index(default_label)
            if default_label in normalized_options
            else 0
        )
        selected_label = st.radio(
            " ",
            normalized_options,
            index=index,
            key=q["key"],
            label_visibility="collapsed",
        )
        return label_to_value.get(selected_label, selected_label)
    if q_type == "pills":
        selected_label = pills(q["key"], normalized_options, label_to_value)
        return label_to_value.get(selected_label, selected_label)
    if q_type == "text":
        return text(q["key"], q.get("placeholder", ""))
    if q_type == "multiselect":
        stored_values = st.session_state.get(q["key"], [])
        default_labels = [k for k, v in label_to_value.items() if v in stored_values]
        selected_labels = st.multiselect(
            " ",
            normalized_options,
            default=default_labels,
            key=q["key"],
            label_visibility="collapsed",
        )
        return [label_to_value.get(l, l) for l in selected_labels]
    if q_type == "slider":
        return st.slider(
            "",
            q["min"],
            q["max"],
            q.get("default", q["min"]),
            key=q["key"],
            label_visibility="collapsed",
        )
    if q_type == "matrix":
        st.write("Matrix questions not yet implemented")
        return {}


def render_form(schema: list[dict]):
    answers = {}
    for q in schema:
        val = render_question(q)
        answers[q["id"]] = val
        st.markdown('<div class="helper"></div>', unsafe_allow_html=True)
    return answers
