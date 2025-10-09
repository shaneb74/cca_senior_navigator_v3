from __future__ import annotations
import json
import pathlib
from typing import Any, Dict

import pandas as pd
import streamlit as st

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_CFG = _REPO_ROOT / "config"

SCHEMA_PATH = _CFG / "gcp_schema.json"
SCORING_JSON = _CFG / "gcp_scoring.json"
BLURBS_JSON = _CFG / "gcp_blurbs.json"


@st.cache_data(show_spinner=False)
def load_schema() -> Dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_scoring() -> pd.DataFrame:
    if not SCORING_JSON.exists():
        raise FileNotFoundError(
            "Missing config/gcp_scoring.json (run the CSV→JSON converter)."
        )
    with SCORING_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    required = {"question_id", "answer_value", "setting", "points"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"gcp_scoring.json missing columns: {missing}")
    df["points"] = df["points"].astype(float)
    return df


@st.cache_data(show_spinner=False)
def load_blurbs() -> Dict[str, str]:
    if not BLURBS_JSON.exists():
        return {}
    with BLURBS_JSON.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    return {str(k): str(v) for k, v in obj.items()}
