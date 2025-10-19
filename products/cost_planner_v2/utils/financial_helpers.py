"""
Financial helper utilities for Cost Planner v2.

Provides normalization and aggregation helpers that convert raw assessment
state dictionaries into consistent numeric structures used across the app.
"""

from __future__ import annotations

from typing import Any

# Income field metadata ------------------------------------------------------

INCOME_NUMERIC_FIELDS = [
    # Basic fields
    "ss_monthly",
    "pension_monthly",
    "employment_income",  # Fixed: was employment_monthly
    "other_income",  # Fixed: was other_monthly
    "partner_income_monthly",
    
    # Advanced fields (from income.json)
    "annuity_monthly",
    "retirement_distributions_monthly",  # Fixed: was retirement_withdrawals_monthly
    "dividends_interest_monthly",
    "rental_income_monthly",
    "alimony_support_monthly",
    "ltc_insurance_monthly",
    "family_support_monthly",
]

# Assets field metadata ------------------------------------------------------

# Basic total fields (mutually exclusive with advanced breakdowns)
ASSET_BASIC_FIELDS = [
    "cash_liquid_total",
    "brokerage_total",
    "retirement_total",
    "home_equity_estimate",
]

# Advanced breakdown fields (mutually exclusive with basic totals)
ASSET_ADVANCED_FIELDS = [
    "checking_balance",
    "savings_cds_balance",
    "brokerage_mf_etf",
    "brokerage_stocks_bonds",
    "retirement_traditional",
    "retirement_roth",
]

# Additional asset fields (included in both modes)
ASSET_OTHER_FIELDS = [
    "real_estate_other",
    "life_insurance_cash_value",
]

# Debt fields
ASSET_DEBT_FIELDS = [
    "primary_residence_mortgage",
    "other_real_estate_debt",
    "secured_loans",
    "unsecured_debt",
]

# Legacy field names (for backwards compatibility)
ASSET_NUMERIC_FIELDS = (
    ASSET_BASIC_FIELDS
    + ASSET_ADVANCED_FIELDS
    + ASSET_OTHER_FIELDS
    + ASSET_DEBT_FIELDS
)

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


def normalize_income_data(income_data: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized copy of the income assessment data."""
    normalized = dict(income_data or {})

    for key in INCOME_NUMERIC_FIELDS:
        normalized[key] = _to_float(normalized.get(key, 0.0))

    normalized["has_partner"] = normalized.get("has_partner") or "no_partner"
    normalized["shared_finance_notes"] = _to_str(normalized.get("shared_finance_notes", ""), "")
    normalized["employment_status"] = normalized.get("employment_status") or "not_employed"

    # Calculate total using corrected field names
    normalized["total_monthly_income"] = calculate_total_monthly_income(normalized)

    return normalized


def calculate_total_monthly_income(income_data: dict[str, Any]) -> float:
    """
    Calculate total monthly income from all sources.
    
    Uses field names from income.json config to match UI form fields.
    Includes both basic and advanced income sources.
    """
    normalized = dict(income_data or {})
    for key in INCOME_NUMERIC_FIELDS:
        normalized[key] = _to_float(normalized.get(key, 0.0))

    return sum(
        [
            # Basic income sources
            normalized.get("ss_monthly", 0.0),
            normalized.get("pension_monthly", 0.0),
            normalized.get("employment_income", 0.0),  # Fixed: was employment_monthly
            normalized.get("other_income", 0.0),  # Fixed: was other_monthly
            normalized.get("partner_income_monthly", 0.0),
            
            # Advanced income sources (from income.json)
            normalized.get("annuity_monthly", 0.0),  # Fixed: was missing
            normalized.get("retirement_distributions_monthly", 0.0),  # Fixed: was retirement_withdrawals_monthly
            normalized.get("dividends_interest_monthly", 0.0),  # Fixed: was missing
            normalized.get("rental_income_monthly", 0.0),
            normalized.get("alimony_support_monthly", 0.0),  # Fixed: was missing
            normalized.get("ltc_insurance_monthly", 0.0),
            normalized.get("family_support_monthly", 0.0),
        ]
    )


def income_breakdown(income_data: dict[str, Any]) -> dict[str, float]:
    """Return a categorized breakdown of monthly income sources."""
    data = normalize_income_data(income_data)

    breakdown = {
        "social_security": data.get("ss_monthly", 0.0),
        "pension": data.get("pension_monthly", 0.0),
        "employment": data.get("employment_income", 0.0),  # Fixed: was employment_monthly
        "annuity": data.get("annuity_monthly", 0.0),
        "retirement_distributions": data.get("retirement_distributions_monthly", 0.0),  # Fixed
        "dividends_interest": data.get("dividends_interest_monthly", 0.0),
        "rental_income": data.get("rental_income_monthly", 0.0),
        "alimony_support": data.get("alimony_support_monthly", 0.0),
        "insurance_benefits": data.get("ltc_insurance_monthly", 0.0),
        "family_support": data.get("family_support_monthly", 0.0),
        "partner_income": data.get("partner_income_monthly", 0.0),
        "other_income": data.get("other_income", 0.0),  # Fixed: was other_monthly
    }
    breakdown["total"] = sum(breakdown.values())
    breakdown["additional_sources"] = breakdown["total"] - (
        breakdown["social_security"] + breakdown["pension"] + breakdown["employment"]
    )

    return breakdown


# Asset helpers --------------------------------------------------------------


def normalize_asset_data(assets_data: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized copy of the assets assessment data."""
    normalized = dict(assets_data or {})

    for key in ASSET_NUMERIC_FIELDS:
        normalized[key] = _to_float(normalized.get(key, 0.0))

    for key in ASSET_BOOL_FIELDS:
        normalized[key] = _to_bool(normalized.get(key, False))

    normalized["asset_has_partner"] = normalized.get("asset_has_partner") or "no_partner"
    normalized["asset_legal_restrictions"] = _to_str(
        normalized.get("asset_legal_restrictions", ""), ""
    )
    normalized["asset_debt_notes"] = _to_str(normalized.get("asset_debt_notes", ""), "")
    normalized["asset_liquidity_concerns"] = (
        normalized.get("asset_liquidity_concerns") or "no_concerns"
    )
    normalized["asset_liquidity_notes"] = _to_str(normalized.get("asset_liquidity_notes", ""), "")
    normalized["primary_residence_liquidity_window"] = (
        normalized.get("primary_residence_liquidity_window") or "under_6_months"
    )

    normalized["total_asset_value"] = calculate_total_asset_value(normalized)
    normalized["total_asset_debt"] = calculate_total_asset_debt(normalized)
    normalized["net_asset_value"] = max(
        normalized["total_asset_value"] - normalized["total_asset_debt"], 0.0
    )

    return normalized


def calculate_total_asset_value(assets_data: dict[str, Any]) -> float:
    """
    Calculate gross asset value before debts.
    
    Uses smart detection to avoid double-counting when both basic totals
    and advanced breakdowns are present. Prioritizes whichever has data.
    """
    data = dict(assets_data or {})
    for key in ASSET_NUMERIC_FIELDS:
        data[key] = _to_float(data.get(key, 0.0))

    # Detect which mode has data (basic totals vs advanced breakdowns)
    basic_total = sum(data.get(field, 0.0) for field in ASSET_BASIC_FIELDS)
    advanced_total = sum(data.get(field, 0.0) for field in ASSET_ADVANCED_FIELDS)
    
    # If both modes have data, prioritize advanced (more detailed)
    # If only one mode has data, use that mode
    # This prevents double-counting
    if advanced_total > 0:
        # Use advanced breakdown mode
        liquid_assets = (
            data.get("checking_balance", 0.0)
            + data.get("savings_cds_balance", 0.0)
        )
        investments = (
            data.get("brokerage_mf_etf", 0.0)
            + data.get("brokerage_stocks_bonds", 0.0)
        )
        retirement = (
            data.get("retirement_traditional", 0.0)
            + data.get("retirement_roth", 0.0)
        )
        # Note: home_equity_estimate is net (no separate home_value field in advanced mode)
        home_value = data.get("home_equity_estimate", 0.0)
    else:
        # Use basic total mode
        liquid_assets = data.get("cash_liquid_total", 0.0)
        investments = data.get("brokerage_total", 0.0)
        retirement = data.get("retirement_total", 0.0)
        home_value = data.get("home_equity_estimate", 0.0)
    
    # Add other assets (included in both modes)
    other_real_estate = data.get("real_estate_other", 0.0)
    life_insurance = data.get("life_insurance_cash_value", 0.0)
    
    return sum([
        liquid_assets,
        investments,
        retirement,
        home_value,
        other_real_estate,
        life_insurance,
    ])


def calculate_total_asset_debt(assets_data: dict[str, Any]) -> float:
    """
    Calculate total debts tied to assets.
    
    Uses field names from assets.json config.
    """
    data = dict(assets_data or {})
    for key in ASSET_NUMERIC_FIELDS:
        data[key] = _to_float(data.get(key, 0.0))

    return sum(
        [
            data.get("primary_residence_mortgage", 0.0),
            data.get("other_real_estate_debt", 0.0),
            data.get("secured_loans", 0.0),
            data.get("unsecured_debt", 0.0),
        ]
    )


def asset_breakdown(assets_data: dict[str, Any]) -> dict[str, float]:
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
    breakdown["net_assets"] = data.get(
        "net_asset_value", breakdown["total"] - breakdown["total_debt"]
    )

    return breakdown
