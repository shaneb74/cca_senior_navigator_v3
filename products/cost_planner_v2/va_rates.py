"""
VA Disability Rates Calculator

Loads official 2025 VA disability compensation rates and provides
calculation utilities for auto-populating benefit amounts.
"""
import json
from pathlib import Path
from typing import Optional


def load_va_rates() -> dict:
    """Load 2025 VA disability compensation rates from config."""
    config_path = Path(__file__).parent.parent.parent / "config" / "va_disability_rates_2025.json"
    with open(config_path, "r") as f:
        return json.load(f)


def get_monthly_va_disability(
    rating: int,
    dependents: str = "none"
) -> Optional[float]:
    """
    Calculate monthly VA disability compensation based on rating and dependents.
    
    Args:
        rating: Disability rating percentage (0, 10, 20, ..., 100)
        dependents: Dependents status - one of:
            - "none" (veteran alone)
            - "spouse" (veteran with spouse)
            - "spouse_one_child" (veteran with spouse and one child)
            - "spouse_multiple_children" / "spouse_two_plus_children" (veteran with spouse and 2+ children)
            - "children_only" (veteran with child(ren) only)
    
    Returns:
        Monthly compensation amount in USD, or None if invalid inputs
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
            return None
        
        # Get monthly amount
        rating_data = rates.get("rates", {}).get(rating_str, {})
        monthly_amount = rating_data.get(rate_key)
        
        return monthly_amount
    except Exception:
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
