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
    # Liquid Assets (3 fields)
    "checking_balance",
    "savings_cds_balance",
    "cash_on_hand",
    # Investments (3 fields)
    "brokerage_stocks_bonds",
    "brokerage_mf_etf",
    "brokerage_other",
    # Retirement (3 fields)
    "retirement_traditional",
    "retirement_roth",
    "retirement_pension_value",
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

    # NEW: Aggregate detailed fields into simplified fields for FinancialProfile
    # This allows FinancialProfile to access aggregated values directly
    normalized["checking_savings"] = (
        normalized.get("checking_balance", 0.0)
        + normalized.get("savings_cds_balance", 0.0)
        + normalized.get("cash_on_hand", 0.0)
    )
    
    normalized["investment_accounts"] = (
        normalized.get("brokerage_stocks_bonds", 0.0)
        + normalized.get("brokerage_mf_etf", 0.0)
        + normalized.get("brokerage_other", 0.0)
    )
    
    # Primary residence uses home_equity_estimate from assessment
    normalized["primary_residence_value"] = normalized.get("home_equity_estimate", 0.0)
    
    # Other real estate
    normalized["other_real_estate"] = normalized.get("real_estate_other", 0.0)
    
    # Life insurance cash value (already a single field)
    # normalized["life_insurance_cash_value"] already exists
    
    # Retirement accounts total (for reference, though not currently in FinancialProfile)
    normalized["retirement_accounts_total"] = (
        normalized.get("retirement_traditional", 0.0)
        + normalized.get("retirement_roth", 0.0)
        + normalized.get("retirement_pension_value", 0.0)
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
    
    Uses all detailed breakdown fields from restored asset sections:
    - Liquid Assets: checking_balance, savings_cds_balance, cash_on_hand
    - Investments: brokerage_stocks_bonds, brokerage_mf_etf, brokerage_other
    - Retirement: retirement_traditional, retirement_roth, retirement_pension_value
    - Real Estate: home_equity_estimate, real_estate_other
    - Other: life_insurance_cash_value
    """
    data = dict(assets_data or {})
    for key in ASSET_NUMERIC_FIELDS:
        data[key] = _to_float(data.get(key, 0.0))

    # Liquid Assets (3 fields)
    liquid_assets = (
        data.get("checking_balance", 0.0)
        + data.get("savings_cds_balance", 0.0)
        + data.get("cash_on_hand", 0.0)
    )
    
    # Investments (3 fields)
    investments = (
        data.get("brokerage_stocks_bonds", 0.0)
        + data.get("brokerage_mf_etf", 0.0)
        + data.get("brokerage_other", 0.0)
    )
    
    # Retirement Accounts (3 fields)
    retirement = (
        data.get("retirement_traditional", 0.0)
        + data.get("retirement_roth", 0.0)
        + data.get("retirement_pension_value", 0.0)
    )
    
    # Real Estate (from Real Estate section - mode toggle enabled)
    home_value = data.get("home_equity_estimate", 0.0)
    other_real_estate = data.get("real_estate_other", 0.0)
    
    # Other Assets
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
    """
    Return categorical breakdown of assets and debts for display in Financial Review.
    
    Uses restored field structure:
    - liquid_assets: checking + savings + cash_on_hand
    - investment_accounts: stocks/bonds + mutual funds + other
    - retirement_accounts: traditional + roth + pension
    - real_estate: home equity + other property
    - life_insurance: cash value
    """
    data = normalize_asset_data(assets_data)

    # Calculate subcategories from detailed fields
    liquid_assets = (
        data.get("checking_balance", 0.0)
        + data.get("savings_cds_balance", 0.0)
        + data.get("cash_on_hand", 0.0)
    )
    
    investment_accounts = (
        data.get("brokerage_stocks_bonds", 0.0)
        + data.get("brokerage_mf_etf", 0.0)
        + data.get("brokerage_other", 0.0)
    )
    
    retirement_accounts = (
        data.get("retirement_traditional", 0.0)
        + data.get("retirement_roth", 0.0)
        + data.get("retirement_pension_value", 0.0)
    )
    
    real_estate = (
        data.get("home_equity_estimate", 0.0)
        + data.get("real_estate_other", 0.0)
    )
    
    life_insurance = data.get("life_insurance_cash_value", 0.0)

    breakdown = {
        "liquid_assets": liquid_assets,
        "investment_accounts": investment_accounts,
        "retirement_accounts": retirement_accounts,
        "real_estate": real_estate,
        "life_insurance": life_insurance,
    }
    breakdown["total"] = sum(breakdown.values())
    breakdown["total_debt"] = data.get("total_asset_debt", 0.0)
    breakdown["net_assets"] = data.get(
        "net_asset_value", breakdown["total"] - breakdown["total_debt"]
    )

    return breakdown
