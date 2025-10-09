from __future__ import annotations
import json
import pathlib
from typing import Any, Dict

import pandas as pd
import streamlit as st

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_CFG = _REPO_ROOT / "config"

SCHEMA_PATH = _CFG / "gcp_schema.json"
SCORING_PATH = _CFG / "gcp_v3_scoring.csv"
BLURBS_PATH = _CFG / "gcp_v3_conversational_blurbs.csv"


@st.cache_data(show_spinner=False)
def load_schema() -> Dict[str, Any]:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_scoring() -> pd.DataFrame:
    df = pd.read_csv(SCORING_PATH)
    required = {"question_id", "answer_value", "setting", "points"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"gcp_v3_scoring.csv missing columns: {missing}")
    df["points"] = df["points"].astype(float)
    return df


@st.cache_data(show_spinner=False)
def load_blurbs() -> Dict[str, str]:
    df = pd.read_csv(BLURBS_PATH)
    if not {"key", "text"}.issubset(df.columns):
        raise ValueError("gcp_v3_conversational_blurbs.csv must include columns: key, text")
    return dict(zip(df["key"].astype(str), df["text"].astype(str)))
