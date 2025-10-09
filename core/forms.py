from __future__ import annotations
from typing import Any, Dict, Optional, Sequence, Tuple

import streamlit as st


def subject_name() -> str:
    return (
        st.session_state.get("subject_name")
        or st.session_state.get("who_name")
        or "they"
    )


def section_header(title: str, blurb: Optional[str] = None) -> None:
    st.markdown(f'<h2 class="h2">{title}</h2>', unsafe_allow_html=True)
    if blurb:
        st.markdown(f'<p class="lead">{blurb}</p>', unsafe_allow_html=True)


def _normalise_options(
    options: Sequence[Tuple[str, str]] | Sequence[Dict[str, Any]]
) -> Tuple[Tuple[str, str], ...]:
    normalised: list[Tuple[str, str]] = []
    for opt in options:
        if isinstance(opt, dict):
            label = opt.get("label") or opt.get("title") or opt.get("value")
            value = opt.get("value") or label
        else:
            label, value = opt  # type: ignore[misc]
        normalised.append((str(label), str(value)))
    return tuple(normalised)


def choice_pills(
    key: str,
    options: Sequence[Tuple[str, str]] | Sequence[Dict[str, Any]],
    value: Optional[str] = None,
    allow_none: bool = True,
) -> Optional[str]:
    opts = _normalise_options(options)
    if not opts:
        return None

    current = st.session_state.get(key, value)
    labels = [label for label, _ in opts]
    values = [val for _, val in opts]

    radio_labels = labels
    radio_values = values
    if allow_none:
        radio_labels = ["Select"] + radio_labels
        radio_values = [None] + radio_values

    idx = 0
    if current in radio_values:
        idx = radio_values.index(current)

    selected_label = st.radio(
        " ",
        radio_labels,
        index=idx,
        horizontal=True,
        label_visibility="collapsed",
        key=f"{key}__radio",
    )
    selected_value = radio_values[radio_labels.index(selected_label)]
    st.session_state[key] = selected_value
    return selected_value if selected_value is not None else None
