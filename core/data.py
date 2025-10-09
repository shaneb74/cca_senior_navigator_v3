from __future__ import annotations
import json
import pathlib
from typing import Any, Dict

import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = ROOT / "config"

SCHEMA_JSON = CFG / "gcp_schema.json"
SCORING_JSON = CFG / "gcp_scoring.json"
BLURBS_JSON = CFG / "gcp_blurbs.json"


def _require(path: pathlib.Path) -> pathlib.Path:
    if not path.exists():
        raise FileNotFoundError(f"Missing required config file: {path}")
    return path


@st.cache_data(show_spinner=False)
def load_schema() -> Dict[str, Any]:
    with _require(SCHEMA_JSON).open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_scoring() -> Dict[str, Dict[str, Dict[str, float]]]:
    with _require(SCORING_JSON).open("r", encoding="utf-8") as f:
        data = json.load(f)

    mapping: Dict[str, Dict[str, Dict[str, float]]] = {}
    rows = data if isinstance(data, list) else data.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("gcp_scoring.json must contain a list of rows")

    for row in rows:
        qid = str(row["question_id"])
        ans = str(row["answer_value"])
        setting = str(row["setting"])
        pts = float(row["points"])
        mapping.setdefault(qid, {}).setdefault(ans, {})[setting] = pts
    return mapping


@st.cache_data(show_spinner=False)
def load_blurbs() -> Dict[str, str]:
    with _require(BLURBS_JSON).open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {str(k): str(v) for k, v in data.items()}
