"""
Financial helper utilities for Cost Planner v2.

Provides normalization and aggregation helpers that convert raw assessment
state dictionaries into consistent numeric structures used across the app.
"""

from __future__ import annotations

from typing import Any, Dict


# Income field metadata ------------------------------------------------------

INCOME_NUMERIC_FIELDS = [
    "ss_monthly",
    "pension_monthly",
    "employment_monthly",
    "retirement_withdrawals_monthly",
    "rental_income_monthly",
    "ltc_insurance_monthly",
    "family_support_monthly",
    "other_monthly",
    "partner_income_monthly",
    "periodic_income_avg_monthly",
]

# Assets field metadata ------------------------------------------------------

ASSET_NUMERIC_FIELDS = [
    "checking_savings",
    "investment_accounts",
    "liquid_assets_loan_balance",
    "primary_residence_value",
    "primary_residence_mortgage_balance",
    "other_real_estate",
    "other_real_estate_debt_balance",
    "other_resources",
    "asset_secured_loans",
    "asset_other_debts",
]

ASSET_BOOL_FIELDS = [
    "liquid_assets_has_loan",
    "primary_residence_has_debt",
    "home_sale_interest",
    "other_real_estate_has_debt",
]


def _to_float(value: Any) -> float:
    """Convert a value to float with safe fallback."""
    if value in (None, "", False):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_str(value: Any, default: str = "") -> str:
    """Convert value to stripped string with default."""
    if value is None:
        return default
    return str(value)


def _to_bool(value: Any) -> bool:
    """Convert value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.lower() in {"true", "yes", "1", "on"}
    return bool(value)


# Income helpers -------------------------------------------------------------

def normalize_income_data(income_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized copy of the income assessment data."""
    normalized = dict(income_data or {})
    
    for key in INCOME_NUMERIC_FIELDS:
        normalized[key] = _to_float(normalized.get(key, 0.0))
    
    normalized["has_partner"] = normalized.get("has_partner") or "no_partner"
    normalized["shared_finance_notes"] = _to_str(normalized.get("shared_finance_notes", ""), "")
    normalized["employment_status"] = normalized.get("employment_status") or "not_employed"
    
    # Derived values for compatibility with legacy calculations
    normalized["other_income_monthly"] = (
        normalized.get("retirement_withdrawals_monthly", 0.0)
        + normalized.get("rental_income_monthly", 0.0)
        + normalized.get("ltc_insurance_monthly", 0.0)
        + normalized.get("family_support_monthly", 0.0)
        + normalized.get("other_monthly", 0.0)
        + normalized.get("partner_income_monthly", 0.0)
        + normalized.get("periodic_income_avg_monthly", 0.0)
    )
    
    # Legacy fields expected by existing analytics (investment_monthly)
    normalized["investment_monthly"] = (
        normalized.get("retirement_withdrawals_monthly", 0.0)
        + normalized.get("rental_income_monthly", 0.0)
    )
    
    normalized["total_monthly_income"] = calculate_total_monthly_income(normalized)
    
    return normalized


def calculate_total_monthly_income(income_data: Dict[str, Any]) -> float:
    """Calculate total monthly income from all sources."""
    normalized = dict(income_data or {})
    for key in INCOME_NUMERIC_FIELDS:
        normalized[key] = _to_float(normalized.get(key, 0.0))
    
    return sum([
        normalized.get("ss_monthly", 0.0),
        normalized.get("pension_monthly", 0.0),
        normalized.get("employment_monthly", 0.0),
        normalized.get("retirement_withdrawals_monthly", 0.0),
        normalized.get("rental_income_monthly", 0.0),
        normalized.get("ltc_insurance_monthly", 0.0),
        normalized.get("family_support_monthly", 0.0),
        normalized.get("partner_income_monthly", 0.0),
        normalized.get("periodic_income_avg_monthly", 0.0),
        normalized.get("other_monthly", 0.0),
    ])


def income_breakdown(income_data: Dict[str, Any]) -> Dict[str, float]:
    """Return a categorized breakdown of monthly income sources."""
    data = normalize_income_data(income_data)
    
    breakdown = {
        "social_security": data.get("ss_monthly", 0.0),
        "pension": data.get("pension_monthly", 0.0),
        "employment": data.get("employment_monthly", 0.0),
        "retirement_withdrawals": data.get("retirement_withdrawals_monthly", 0.0),
        "rental_income": data.get("rental_income_monthly", 0.0),
        "insurance_benefits": data.get("ltc_insurance_monthly", 0.0),
        "family_support": data.get("family_support_monthly", 0.0),
        "partner_income": data.get("partner_income_monthly", 0.0),
        "periodic_income": data.get("periodic_income_avg_monthly", 0.0),
        "other_income": data.get("other_monthly", 0.0),
    }
    breakdown["total"] = sum(breakdown.values())
    breakdown["additional_sources"] = breakdown["total"] - (
        breakdown["social_security"] + breakdown["pension"] + breakdown["employment"]
    )
    
    return breakdown


# Asset helpers --------------------------------------------------------------

def normalize_asset_data(assets_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized copy of the assets assessment data."""
    normalized = dict(assets_data or {})
    
    for key in ASSET_NUMERIC_FIELDS:
        normalized[key] = _to_float(normalized.get(key, 0.0))
    
    for key in ASSET_BOOL_FIELDS:
        normalized[key] = _to_bool(normalized.get(key, False))
    
    normalized["asset_has_partner"] = normalized.get("asset_has_partner") or "no_partner"
    normalized["asset_legal_restrictions"] = _to_str(normalized.get("asset_legal_restrictions", ""), "")
    normalized["asset_debt_notes"] = _to_str(normalized.get("asset_debt_notes", ""), "")
    normalized["asset_liquidity_concerns"] = normalized.get("asset_liquidity_concerns") or "no_concerns"
    normalized["asset_liquidity_notes"] = _to_str(normalized.get("asset_liquidity_notes", ""), "")
    normalized["primary_residence_liquidity_window"] = normalized.get("primary_residence_liquidity_window") or "under_6_months"
    
    normalized["total_asset_value"] = calculate_total_asset_value(normalized)
    normalized["total_asset_debt"] = calculate_total_asset_debt(normalized)
    normalized["net_asset_value"] = max(normalized["total_asset_value"] - normalized["total_asset_debt"], 0.0)
    
    return normalized


def calculate_total_asset_value(assets_data: Dict[str, Any]) -> float:
    """Calculate gross asset value before debts."""
    data = dict(assets_data or {})
    for key in ASSET_NUMERIC_FIELDS:
        data[key] = _to_float(data.get(key, 0.0))
    
    return sum([
        data.get("checking_savings", 0.0),
        data.get("investment_accounts", 0.0),
        data.get("primary_residence_value", 0.0),
        data.get("other_real_estate", 0.0),
        data.get("other_resources", 0.0),
    ])


def calculate_total_asset_debt(assets_data: Dict[str, Any]) -> float:
    """Calculate total debts tied to assets."""
    data = dict(assets_data or {})
    for key in ASSET_NUMERIC_FIELDS:
        data[key] = _to_float(data.get(key, 0.0))
    
    return sum([
        data.get("liquid_assets_loan_balance", 0.0),
        data.get("primary_residence_mortgage_balance", 0.0),
        data.get("other_real_estate_debt_balance", 0.0),
        data.get("asset_secured_loans", 0.0),
        data.get("asset_other_debts", 0.0),
    ])


def asset_breakdown(assets_data: Dict[str, Any]) -> Dict[str, float]:
    """Return categorical breakdown of assets and debts."""
    data = normalize_asset_data(assets_data)
    
    breakdown = {
        "liquid_assets": data.get("checking_savings", 0.0),
        "investment_accounts": data.get("investment_accounts", 0.0),
        "primary_residence": data.get("primary_residence_value", 0.0),
        "other_real_estate": data.get("other_real_estate", 0.0),
        "other_resources": data.get("other_resources", 0.0),
    }
    breakdown["total"] = sum(breakdown.values())
    breakdown["total_debt"] = data.get("total_asset_debt", 0.0)
    breakdown["net_assets"] = data.get("net_asset_value", breakdown["total"] - breakdown["total_debt"])
    
    return breakdown
