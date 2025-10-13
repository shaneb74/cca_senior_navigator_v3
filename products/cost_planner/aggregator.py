"""Product-level outcome aggregation for Cost Planner.

This module combines outcomes from all calculation sub-modules into a
single product-level affordability assessment.
"""

from typing import Any, Dict
from core.modules.schema import OutcomeContract


def aggregate_product_outcomes(modules: Dict[str, Any]) -> OutcomeContract:
    """Aggregate all Cost Planner module outcomes into product-level result.
    
    Combines financial data from:
    - Income sources (monthly income)
    - Assets & savings (liquid assets)
    - Monthly care costs (estimated care cost)
    - Other modules as available
    
    Calculates:
    - Monthly surplus/deficit
    - Months until asset depletion
    - Affordability tier (affordable, at_risk, unsustainable)
    - Recommended actions via flags
    
    Args:
        modules: Dict of module states, each with "outcome" key containing
                module's OutcomeContract results
    
    Returns:
        OutcomeContract with product-level affordability recommendation
    """
    # Extract domain scores from completed modules
    income_outcome = modules.get("income_sources", {}).get("outcome", {})
    assets_outcome = modules.get("assets_savings", {}).get("outcome", {})
    costs_outcome = modules.get("monthly_care_costs", {}).get("outcome", {})
    va_outcome = modules.get("va_benefits", {}).get("outcome", {})
    
    # Get financial totals (default to 0 if module not completed)
    total_income = _get_score(income_outcome, "total_income", 0)
    liquid_assets = _get_score(assets_outcome, "liquid_assets", 0)
    monthly_care_cost = _get_score(costs_outcome, "monthly_care_cost", 0)
    va_monthly_benefit = _get_score(va_outcome, "va_monthly_amount", 0)
    
    # Adjust income with VA benefits
    total_income_with_benefits = total_income + va_monthly_benefit
    
    # Calculate monthly surplus/deficit
    monthly_deficit = max(0, monthly_care_cost - total_income_with_benefits)
    monthly_surplus = max(0, total_income_with_benefits - monthly_care_cost)
    
    # Calculate months until asset depletion
    if monthly_deficit == 0:
        months_until_depletion = 999  # Sustainable indefinitely
    elif liquid_assets <= 0:
        months_until_depletion = 0  # Immediate crisis
    else:
        months_until_depletion = liquid_assets / monthly_deficit
    
    # Determine affordability tier and flags
    recommendation, flags = _determine_affordability_tier(
        months_until_depletion,
        monthly_surplus,
        monthly_deficit,
        total_income_with_benefits,
        liquid_assets,
        modules
    )
    
    # Build product-level outcome
    return OutcomeContract(
        recommendation=recommendation,
        flags=flags,
        domain_scores={
            "total_income": total_income,
            "va_monthly_benefit": va_monthly_benefit,
            "total_income_with_benefits": total_income_with_benefits,
            "liquid_assets": liquid_assets,
            "monthly_care_cost": monthly_care_cost,
            "monthly_surplus": monthly_surplus,
            "monthly_deficit": monthly_deficit,
            "months_until_depletion": round(months_until_depletion, 1),
        },
        tags=["affordability_assessed", "multi_module_aggregation", "cost_planner"],
        audit={
            "aggregated_from_modules": list(modules.keys()),
            "calculation_version": "2025.10.1",
        },
    )


def _get_score(outcome: Dict[str, Any], key: str, default: float = 0) -> float:
    """Safely extract a domain score from a module outcome.
    
    Args:
        outcome: Module outcome dict
        key: Score key to extract
        default: Default value if not found
    
    Returns:
        Float value of the score
    """
    try:
        scores = outcome.get("domain_scores", {})
        value = scores.get(key, default)
        return float(value)
    except (ValueError, TypeError):
        return default


def _determine_affordability_tier(
    months: float,
    surplus: float,
    deficit: float,
    income: float,
    assets: float,
    modules: Dict[str, Any],
) -> tuple[str, Dict[str, bool]]:
    """Determine affordability tier and recommended action flags.
    
    Args:
        months: Months until asset depletion
        surplus: Monthly surplus (if income > costs)
        deficit: Monthly deficit (if costs > income)
        income: Total monthly income
        assets: Liquid assets
        modules: All module states (for context)
    
    Returns:
        Tuple of (recommendation tier, flags dict)
    """
    flags: Dict[str, bool] = {}
    
    # Critical situation: Assets depleted or will deplete within 12 months
    if months <= 12:
        recommendation = "unsustainable"
        flags["urgent_financial_planning"] = True
        flags["medicaid_eligible_check"] = True
        
        # Check if VA benefits could help
        va_outcome = modules.get("va_benefits", {}).get("outcome", {})
        if not _get_score(va_outcome, "va_monthly_amount", 0):
            flags["va_benefits_check"] = True
        
        # Low income suggests need for public assistance
        if income < 3000:
            flags["public_assistance_needed"] = True
        
        return recommendation, flags
    
    # At-risk situation: 12-60 months until depletion
    if months <= 60:
        recommendation = "at_risk"
        flags["financial_planning_needed"] = True
        
        # Encourage VA benefits exploration
        if income < 5000:
            flags["va_benefits_check"] = True
        
        # Consider asset optimization
        if assets > 100000:
            flags["asset_optimization_recommended"] = True
        
        return recommendation, flags
    
    # Comfortable situation: 60+ months or indefinitely sustainable
    recommendation = "affordable"
    
    # Even if affordable, suggest optimization for large assets
    if assets > 250000:
        flags["wealth_management_recommended"] = True
    
    # Suggest planning if borderline
    if months < 120:  # Less than 10 years
        flags["long_term_planning_recommended"] = True
    
    return recommendation, flags


def calculate_product_progress(modules: Dict[str, Any]) -> float:
    """Calculate product-level progress from module completion.
    
    Args:
        modules: Dict of module states with progress values
    
    Returns:
        Average progress across all modules (0-100)
    """
    # Define required modules for progress calculation
    REQUIRED_MODULES = [
        "income_sources",
        "assets_savings",
        "monthly_care_costs",
    ]
    
    # Optional modules (count if started)
    OPTIONAL_MODULES = [
        "home_ownership",
        "insurance_benefits",
        "va_benefits",
        "expense_adjustments",
    ]
    
    # Get progress for each module
    module_progress = []
    
    for module_key in REQUIRED_MODULES:
        progress = modules.get(module_key, {}).get("progress", 0)
        module_progress.append(float(progress))
    
    # Include optional modules if they have progress
    for module_key in OPTIONAL_MODULES:
        progress = modules.get(module_key, {}).get("progress", 0)
        if progress > 0:
            module_progress.append(float(progress))
    
    # Calculate average progress
    if not module_progress:
        return 0.0
    
    avg_progress = sum(module_progress) / len(module_progress)
    return round(avg_progress, 1)
