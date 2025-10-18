from __future__ import annotations

from typing import Any

import streamlit as st


def _bucket(product: str) -> dict[str, Any]:
    return st.session_state.setdefault(
        product,
        {
            "progress": 0,
            "outcome": {},
            "modules": {},
        },
    )


def set_progress(product: str, value: int) -> None:
    _bucket(product)["progress"] = max(0, min(100, int(value)))


def set_outcome(product: str, outcome: dict[str, Any]) -> None:
    _bucket(product)["outcome"] = dict(outcome or {})


def set_module_outcome(product: str, module: str, outcome: dict[str, Any]) -> None:
    bucket = _bucket(product)
    bucket["modules"].setdefault(module, {})["outcome"] = dict(outcome or {})
