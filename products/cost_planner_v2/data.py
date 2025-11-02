"""
Cached data loaders for Cost Planner v2.

Loads heavy data files once and caches them in memory for fast O(1) lookups.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


def _get_project_root() -> Path:
    """Get project root by walking up to find config/nav.json or app.py."""
    cur = Path(__file__).resolve()
    for _ in range(8):
        if (cur / "config" / "nav.json").exists() or (cur / "app.py").exists():
            return cur
        cur = cur.parent
    # Fallback
    return Path(__file__).resolve().parents[5]


@st.cache_data(ttl=60 * 60, show_spinner=False)
def load_home_cost_index() -> dict[str, float]:
    """Load & normalize monthly median cost CSV once; return {zip: cost} dict.
    
    Cached for 1 hour. Provides O(1) lookup after first load.
    
    Returns:
        Dictionary mapping 5-digit ZIP codes to monthly median costs
    """
    csv_path = _get_project_root() / "data" / "app_data" / "monthly_median_cost.csv"
    
    if not csv_path.exists():
        print(f"[DATA_WARN] CSV not found: {csv_path}")
        return {}
    
    try:
        # Read CSV without column filtering first
        df = pd.read_csv(csv_path, dtype={"ZipCode": "string"})
        
        # Normalize column names
        df.columns = [col.lower().replace("_", "") for col in df.columns]
        
        # Find ZIP column
        zip_col = next((c for c in df.columns if "zip" in c), None)
        cost_col = next((c for c in df.columns if "median" in c or "cost" in c), None)
        
        if not zip_col or not cost_col:
            print(f"[DATA_WARN] Could not find ZIP or cost columns in {csv_path}")
            return {}
        
        # Normalize ZIPs to 5 digits and convert costs to float
        df[zip_col] = df[zip_col].astype(str).str.zfill(5)
        df[cost_col] = pd.to_numeric(df[cost_col], errors="coerce")
        
        # Drop NaN and create dict
        df = df.dropna(subset=[cost_col])
        index = dict(zip(df[zip_col], df[cost_col].astype(float)))
        
        print(f"[DATA_OK] Loaded home cost index: {len(index)} ZIP codes")
        return index
        
    except Exception as e:
        print(f"[DATA_ERR] Failed to load {csv_path}: {e}")
        return {}


def lookup_home_cost(zip_code: str | None) -> float | None:
    """Fast O(1) lookup of home cost by ZIP code.
    
    Args:
        zip_code: 5-digit ZIP code (or None)
        
    Returns:
        Monthly median cost or None if not found
    """
    if not zip_code:
        return None
    
    index = load_home_cost_index()
    normalized_zip = str(zip_code).strip().zfill(5)
    return index.get(normalized_zip)
