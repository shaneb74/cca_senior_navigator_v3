from __future__ import annotations
import json
import pathlib
from typing import Any, Dict

import pandas as pd
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = ROOT / "config"

SCHEMA_JSON = CFG / "gcp_schema.json"
SCORING_JSON = CFG / "gcp_scoring.json"
BLURBS_JSON = CFG / "gcp_blurbs.json"

SCORING_CSV = CFG / "gcp_v3_scoring.csv"
BLURBS_CSV = CFG / "gcp_v3_conversational_blurbs.csv"


@st.cache_data(show_spinner=False)
def load_schema() -> Dict[str, Any]:
    with SCHEMA_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_scoring() -> Dict[str, Dict[str, Dict[str, float]]]:
    if SCORING_JSON.exists():
        with SCORING_JSON.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        if isinstance(payload, dict):
            return payload
        return _rows_to_mapping(payload)

    if SCORING_CSV.exists():
        df = pd.read_csv(SCORING_CSV)
        required = {"question_id", "answer_value", "setting", "points"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"gcp_v3_scoring.csv missing columns: {missing}")
        rows = [
            {
                "question_id": str(row["question_id"]),
                "answer_value": str(row["answer_value"]),
                "setting": str(row["setting"]),
                "points": float(row["points"]),
            }
            for _, row in df.iterrows()
        ]
        return _rows_to_mapping(rows)

    return {}


def _rows_to_mapping(rows: Any) -> Dict[str, Dict[str, Dict[str, float]]]:
    mapping: Dict[str, Dict[str, Dict[str, float]]] = {}
    for row in rows:
        q = str(row["question_id"])
        a = str(row["answer_value"])
        setting = str(row["setting"])
        points = float(row["points"])
        mapping.setdefault(q, {}).setdefault(a, {})[setting] = points
    return mapping


@st.cache_data(show_spinner=False)
def load_blurbs() -> Dict[str, str]:
    if BLURBS_JSON.exists():
        with BLURBS_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    if BLURBS_CSV.exists():
        df = pd.read_csv(BLURBS_CSV)
        if not {"key", "text"}.issubset(df.columns):
            raise ValueError("gcp_v3_conversational_blurbs.csv must include columns: key, text")
        return dict(zip(df["key"].astype(str), df["text"].astype(str)))
    return {}
