"""VA Disability Rates - Robust loader with health logs."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional
import json

# -- CONFIG --------------------------------------------------------------

# Map visible dependent strings → internal keys used in the rates file.
DEP_MAP: Dict[str, str] = {
    "Veteran alone": "veteran_alone",
    "Veteran with spouse": "with_spouse",
    "Veteran with spouse and one child": "with_spouse_one_child",
    "Veteran with spouse and two children": "with_spouse_two_plus_children",
    "Veteran with spouse and 2+ children": "with_spouse_two_plus_children",
    "Veteran with one child": "children_only",
    "Veteran with child(ren) only": "children_only",
    "Veteran with parent": "veteran_alone",  # Fallback - base rate
    "Veteran with two parents": "veteran_alone",  # Fallback - base rate
    "Veteran with spouse, one parent": "with_spouse",  # Fallback - spouse rate
    "Veteran with spouse, two parents": "with_spouse",  # Fallback - spouse rate
    # Legacy keys (for backward compatibility)
    "none": "veteran_alone",
    "spouse": "with_spouse",
    "spouse_one_child": "with_spouse_one_child",
    "spouse_two_plus_children": "with_spouse_two_plus_children",
    "spouse_multiple_children": "with_spouse_two_plus_children",
    "children_only": "children_only",
}

# -- PATH RESOLUTION -----------------------------------------------------

def _project_root(start: Path) -> Path:
    """
    Walk up until 'config/nav.json' or 'app.py' is found; fallback 4 parents up.
    This makes the loader resilient to directory moves.
    """
    cur = start.resolve()
    for _ in range(8):
        if (cur / "config" / "nav.json").exists() or (cur / "app.py").exists():
            return cur
        cur = cur.parent
    return start.resolve().parents[4]

def _find_latest_rates_file(root: Path) -> Path | None:
    """
    Selects the newest 'config/va_disability_rates_*.json' by lexicographic order.
    """
    cfg = root / "config"
    candidates = sorted(cfg.glob("va_disability_rates_*.json"))
    return candidates[-1] if candidates else None

# -- LOADER & NORMALIZATION ---------------------------------------------

def load_va_rates() -> Dict[str, Any]:
    """Load VA disability rates from config with health logs."""
    root = _project_root(Path(__file__))
    rates_file = _find_latest_rates_file(root)
    if not rates_file:
        print("[VA_RATES_WARN] No rates file found under config/ (expected va_disability_rates_*.json)")
        return {}
    try:
        data = json.loads(rates_file.read_text())
        # Health log
        top = list(data.keys())[:5] if isinstance(data, dict) else f"type={type(data)}"
        print(f"[VA_RATES_OK] Loaded {rates_file.name}; top-level={top}")
        return data
    except Exception as e:
        print(f"[VA_RATES_ERR] Failed to read {rates_file}: {e}")
        return {}

def _norm_rating(rating_value: str | int | None) -> int:
    """Normalize rating to 0-100 integer."""
    if rating_value is None:
        return 0
    s = str(rating_value).strip()
    if s.endswith("%"):
        s = s[:-1]
    try:
        # clamp to 0..100, multiples of 10 are typical, but allow any int
        return max(0, min(100, int(float(s))))
    except Exception:
        return 0

def _norm_dep(dep_value: str | None) -> str:
    """Normalize dependent status to internal key."""
    if not dep_value:
        return ""
    key = DEP_MAP.get(dep_value.strip())
    if not key:
        print(f"[VA_RATES_WARN] Unknown dependent status: {dep_value!r}")
    return key or ""

# -- LOOKUP --------------------------------------------------------------

def compute_va_payment(rating_value, dep_value, rates: Dict[str, Any]) -> float:
    """
    Returns the monthly amount as float, or 0.0 if no match.
    Supports two common schemas:
      A) { "60": { "veteran_alone": XXXXX, ... }, "70": {...}, ... }
      B) { "ratings": { "60": {...}, "70": {...} } }
    """
    rating = _norm_rating(rating_value)
    dep_key = _norm_dep(dep_value)

    if not dep_key:
        return 0.0
    if not isinstance(rates, dict):
        print(f"[VA_RATES_ERR] Rates type unsupported: {type(rates)}")
        return 0.0

    # Try schema B first (has "rates" key)
    bucket = rates.get("rates", {}).get(str(rating))
    # Try schema A (direct rating key)
    if not bucket:
        bucket = rates.get(str(rating))

    if not bucket or not isinstance(bucket, dict):
        print(f"[VA_RATES_WARN] No bucket for rating={rating}; available={list(rates.get('rates', rates).keys())[:5]}")
        return 0.0

    amt = bucket.get(dep_key)
    if amt in (None, "", 0):
        print(f"[VA_RATES_WARN] No amount for rating={rating} dep={dep_key}; bucket_keys={list(bucket.keys())}")
        return 0.0

    try:
        val = float(amt)
        print(f"[VA_RATES_OK] rating={rating} dep={dep_key} amount={val}")
        return val
    except Exception as e:
        print(f"[VA_RATES_ERR] amount parse rating={rating} dep={dep_key}: {e} raw={amt!r}")
        return 0.0


# -- BACKWARD COMPATIBILITY ----------------------------------------------

def get_monthly_va_disability(rating: int, dependents: str = "none") -> float | None:
    """
    Legacy function for backward compatibility with existing code.
    
    Args:
        rating: Disability rating percentage (0, 10, 20, ..., 100)
        dependents: Dependents status (various formats supported)
    
    Returns:
        Monthly compensation amount in USD, or None if calculation fails
    """
    try:
        rates = load_va_rates()
        if not rates:
            return None
        
        amount = compute_va_payment(rating, dependents, rates)
        return amount if amount > 0 else None
    except Exception as e:
        print(f"[VA_RATES_ERR] Legacy function error: {e}")
        return None
