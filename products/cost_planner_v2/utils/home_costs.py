"""
Home carry cost lookup by ZIP code.

Loads monthly median housing costs from CSV and provides ZIP-based prefill
for Cost Planner intro home carry cost field.
"""

from pathlib import Path
from typing import Optional

import pandas as pd

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


# Module-level cache (fallback if no Streamlit)
_HOME_COSTS_CACHE: Optional[pd.DataFrame] = None


def load_home_costs() -> pd.DataFrame:
    """Load home costs CSV (cached).
    
    Returns:
        DataFrame with columns: zip (str), amount (float), kind (str)
    """
    global _HOME_COSTS_CACHE
    
    # Use Streamlit cache if available
    if HAS_STREAMLIT:
        return _load_with_streamlit_cache()
    
    # Module-level cache
    if _HOME_COSTS_CACHE is not None:
        return _HOME_COSTS_CACHE
    
    _HOME_COSTS_CACHE = _load_csv()
    return _HOME_COSTS_CACHE


@st.cache_data
def _load_with_streamlit_cache() -> pd.DataFrame:
    """Load CSV with Streamlit cache."""
    return _load_csv()


def _load_csv() -> pd.DataFrame:
    """Load and normalize CSV data.
    
    Returns:
        DataFrame with normalized columns
    """
    # Find CSV path
    csv_path = Path(__file__).resolve().parents[3] / "data" / "app_data" / "monthly_median_cost.csv"
    
    if not csv_path.exists():
        print(f"[HOME_COST_WARN] CSV not found at {csv_path}")
        return pd.DataFrame(columns=["zip", "amount", "kind"])
    
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Detect ZIP column (case-insensitive, with variants)
    zip_col = None
    zip_variants = ["zipcode", "zip", "postal", "zip_code", "postalcode"]
    
    for col in df.columns:
        if col.lower().replace(" ", "_") in zip_variants:
            zip_col = col
            break
    
    if zip_col is None:
        print(f"[HOME_COST_WARN] No ZIP column found in CSV. Columns: {list(df.columns)}")
        return pd.DataFrame(columns=["zip", "amount", "kind"])
    
    # Detect value column (owner/renter variants)
    owner_variants = ["owner_monthly", "owner_carry", "owner_cost", "owner_avg", "median_owner", "medianmonthlycost", "median_monthly_cost"]
    renter_variants = ["renter_monthly", "renter_carry", "renter_cost", "renter_avg", "median_renter"]
    
    owner_col = None
    renter_col = None
    
    for col in df.columns:
        col_norm = col.lower().replace(" ", "_")
        if col_norm in owner_variants:
            owner_col = col
        if col_norm in renter_variants:
            renter_col = col
    
    # Build normalized dataframe
    rows = []
    
    # Process owner costs
    if owner_col:
        for _, row in df.iterrows():
            zip_code = str(row[zip_col]).strip().zfill(5)
            
            # Try to convert to float, handle '-' and other non-numeric values
            try:
                amount = float(row[owner_col])
            except (ValueError, TypeError):
                continue  # Skip non-numeric values
            
            # Skip negative or zero amounts
            if amount <= 0:
                continue
            
            rows.append({
                "zip": zip_code,
                "amount": amount,
                "kind": "owner",
            })
    
    # Process renter costs (if separate column exists)
    if renter_col:
        for _, row in df.iterrows():
            zip_code = str(row[zip_col]).strip().zfill(5)
            
            # Try to convert to float, handle '-' and other non-numeric values
            try:
                amount = float(row[renter_col])
            except (ValueError, TypeError):
                continue  # Skip non-numeric values
            
            # Skip negative or zero amounts
            if amount <= 0:
                continue
            
            rows.append({
                "zip": zip_code,
                "amount": amount,
                "kind": "renter",
            })
    
    result_df = pd.DataFrame(rows)
    
    print(f"[HOME_COST] Loaded {len(result_df)} records from {csv_path.name}")
    print(f"[HOME_COST] Columns detected: ZIP={zip_col}, OWNER={owner_col}, RENTER={renter_col}")
    
    return result_df


def lookup_zip(zip_code: str, kind: str = "owner") -> Optional[dict]:
    """Look up home carry cost by ZIP code.
    
    Tries:
    1. Exact ZIP match (confidence 1.0)
    2. ZIP3 bucket (first 3 digits, confidence 0.7)
    3. None (user must enter manually)
    
    Args:
        zip_code: 5-digit ZIP code
        kind: "owner" or "renter"
    
    Returns:
        Dict with amount, source, confidence, kind or None
    """
    # Normalize ZIP
    zip_code = str(zip_code).strip().zfill(5)[:5]
    
    # Load data
    df = load_home_costs()
    
    if df.empty:
        return None
    
    # Filter by kind
    df_kind = df[df["kind"] == kind]
    
    # Try exact match
    exact = df_kind[df_kind["zip"] == zip_code]
    
    if not exact.empty:
        amount = float(exact.iloc[0]["amount"])
        return {
            "amount": amount,
            "source": "ZIP exact match",
            "confidence": 1.0,
            "kind": kind,
        }
    
    # Try ZIP3 bucket (average of all ZIPs in same 3-digit prefix)
    zip3 = zip_code[:3]
    zip3_matches = df_kind[df_kind["zip"].str.startswith(zip3)]
    
    if not zip3_matches.empty:
        amount = float(zip3_matches["amount"].median())
        return {
            "amount": amount,
            "source": f"ZIP3 bucket ({zip3}xx)",
            "confidence": 0.7,
            "kind": kind,
        }
    
    # No match
    return None
