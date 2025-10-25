"""
VA Disability Rates Calculator

Loads official 2025 VA disability compensation rates and provides
calculation utilities for auto-populating benefit amounts.

NOTE: Rates are stored in static JSON config file (not fetched dynamically).
VA disability rates update annually on December 1st based on Social Security COLA.
Update config/va_disability_rates_2025.json when new rates are published.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def load_va_rates() -> dict:
    """
    Load VA disability compensation rates from config.
    
    Returns:
        dict: Rate configuration with effective_date, rates, and metadata
        
    Raises:
        FileNotFoundError: If rates config file is missing
        json.JSONDecodeError: If config file has invalid JSON
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "va_disability_rates_2025.json"

    try:
        with open(config_path) as f:
            rates = json.load(f)

        # Check if rates might be stale (optional warning)
        effective_date = rates.get("effective_date", "")
        if effective_date:
            try:
                effective_dt = datetime.strptime(effective_date, "%Y-%m-%d")
                current_dt = datetime.now()
                days_old = (current_dt - effective_dt).days

                # Warn if rates are over 400 days old (should update annually)
                if days_old > 400:
                    logger.warning(
                        f"VA disability rates may be outdated. "
                        f"Effective date: {effective_date}, {days_old} days old. "
                        f"Check VA.gov for updated rates published each December 1st."
                    )
            except ValueError:
                pass  # Invalid date format, skip check

        return rates
    except FileNotFoundError:
        logger.error(f"VA rates config file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in VA rates config: {e}")
        raise


def get_monthly_va_disability(
    rating: int,
    dependents: str = "none"
) -> float | None:
    """
    Calculate monthly VA disability compensation based on rating and dependents.
    
    Uses static rate table from config (not fetched from internet).
    Returns None if calculation fails - UI will allow manual entry.
    
    Args:
        rating: Disability rating percentage (0, 10, 20, ..., 100)
        dependents: Dependents status - one of:
            - "none" (veteran alone)
            - "spouse" (veteran with spouse)
            - "spouse_one_child" (veteran with spouse and one child)
            - "spouse_multiple_children" / "spouse_two_plus_children" (veteran with spouse and 2+ children)
            - "children_only" (veteran with child(ren) only)
    
    Returns:
        Monthly compensation amount in USD, or None if:
        - Invalid rating/dependents
        - Rates file missing
        - Calculation error
    """
    try:
        rates = load_va_rates()

        # Normalize rating to string
        rating_str = str(int(rating))

        # Normalize dependents key (handle both naming conventions)
        if dependents == "spouse_multiple_children":
            dependents = "spouse_two_plus_children"

        # Look up rate in mapping
        rate_mapping = rates.get("dependents_mapping", {})
        rate_key = rate_mapping.get(dependents)

        if not rate_key:
            logger.warning(f"Invalid dependents value: {dependents}")
            return None

        # Get monthly amount
        rating_data = rates.get("rates", {}).get(rating_str, {})
        monthly_amount = rating_data.get(rate_key)

        if monthly_amount is None:
            logger.warning(f"No rate found for rating={rating}, dependents={dependents}")

        return monthly_amount
    except Exception as e:
        # Catch all errors (file not found, JSON parse, key errors, etc.)
        logger.error(f"Error calculating VA disability amount: {e}")
        return None


def format_va_disability_info(rating: int, dependents: str) -> str:
    """
    Format VA disability information for display.
    
    Returns a human-readable string describing the rate calculation.
    """
    amount = get_monthly_va_disability(rating, dependents)
    if amount is None:
        return "Unable to calculate rate"

    dependents_display = {
        "none": "Veteran only (no dependents)",
        "spouse": "Veteran with spouse",
        "spouse_one_child": "Veteran with spouse and 1 child",
        "spouse_two_plus_children": "Veteran with spouse and 2+ children",
        "spouse_multiple_children": "Veteran with spouse and 2+ children",
        "children_only": "Veteran with child(ren) only"
    }.get(dependents, dependents)

    return f"{rating}% disability, {dependents_display}: ${amount:,.2f}/month (2025 rate)"
