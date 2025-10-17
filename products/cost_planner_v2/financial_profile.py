"""
Financial Profile Aggregator for Cost Planner v2

Collects and aggregates data from all financial assessments into a unified
FinancialProfile structure for expert review and cost analysis.

Pattern: Data aggregation layer between assessments and expert review
Input: Individual assessment states from session_state
Output: Unified FinancialProfile ready for MCIP publishing and analysis
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import streamlit as st


@dataclass
class FinancialProfile:
    """
    Unified financial profile aggregating all assessment data.
    
    This structure represents the complete financial picture of a user,
    collected from 6 financial assessments, ready for expert review analysis.
    """
    
    # ==== INCOME SOURCES ====
    ss_monthly: float = 0.0
    pension_monthly: float = 0.0
    employment_status: str = "not_employed"
    employment_monthly: float = 0.0
    other_income_monthly: float = 0.0
    total_monthly_income: float = 0.0
    
    # ==== ASSETS & RESOURCES ====
    checking_savings: float = 0.0
    investment_accounts: float = 0.0
    primary_residence_value: float = 0.0
    home_sale_interest: bool = False
    other_real_estate: float = 0.0
    other_resources: float = 0.0
    total_asset_value: float = 0.0
    
    # ==== HEALTH INSURANCE ====
    has_medicare: bool = False
    medicare_parts: list = field(default_factory=list)
    has_medicare_advantage: bool = False
    has_medicare_supplement: bool = False
    medicare_premium_monthly: float = 0.0
    
    has_medicaid: bool = False
    medicaid_covers_ltc: bool = False
    
    has_ltc_insurance: bool = False
    ltc_daily_benefit: float = 0.0
    ltc_benefit_period_months: int = 0
    ltc_elimination_days: int = 0
    
    has_private_insurance: bool = False
    private_insurance_premium_monthly: float = 0.0
    
    # ==== LIFE INSURANCE ====
    has_life_insurance: str = "no"
    life_insurance_type: Optional[str] = None
    life_insurance_face_value: float = 0.0
    life_insurance_cash_value: float = 0.0
    life_insurance_premium_monthly: float = 0.0
    
    has_annuities: str = "no"
    annuity_current_value: float = 0.0
    annuity_monthly_income: float = 0.0
    
    total_accessible_life_value: float = 0.0
    
    # ==== VA BENEFITS ====
    has_va_benefits: str = "no"
    va_disability_rating: int = 0
    va_disability_monthly: float = 0.0
    va_pension_monthly: float = 0.0
    
    has_aid_attendance: str = "no"
    aid_attendance_monthly: float = 0.0
    
    total_va_benefits_monthly: float = 0.0
    
    # ==== MEDICAID PLANNING ====
    medicaid_status: str = "not_enrolled"
    interested_in_spend_down: bool = False
    spend_down_timeline: Optional[str] = None
    has_estate_plan: list = field(default_factory=list)
    
    # ==== METADATA ====
    completeness_percentage: float = 0.0
    required_assessments_complete: bool = False
    optional_assessments_complete: dict = field(default_factory=dict)
    last_updated: Optional[str] = None


def build_financial_profile(
    product_key: str = "cost_planner_v2"
) -> FinancialProfile:
    """
    Aggregate all assessment data into a unified FinancialProfile.
    
    Args:
        product_key: Product key for state management
        
    Returns:
        FinancialProfile with all collected data
    """
    profile = FinancialProfile()
    
    # Get tiles state (persistent assessment storage)
    tiles = st.session_state.get("tiles", {})
    product_tiles = tiles.get(product_key, {})
    assessments_state = product_tiles.get("assessments", {})
    
    # ==== INCOME ASSESSMENT ====
    income_data = assessments_state.get("income", {})
    if income_data:
        profile.ss_monthly = float(income_data.get("ss_monthly", 0))
        profile.pension_monthly = float(income_data.get("pension_monthly", 0))
        profile.employment_status = income_data.get("employment_status", "not_employed")
        profile.employment_monthly = float(income_data.get("employment_monthly", 0))
        profile.other_income_monthly = float(income_data.get("other_monthly", 0))
        profile.total_monthly_income = (
            profile.ss_monthly + 
            profile.pension_monthly + 
            profile.employment_monthly + 
            profile.other_income_monthly
        )
    
    # ==== ASSETS ASSESSMENT ====
    assets_data = assessments_state.get("assets", {})
    if assets_data:
        profile.checking_savings = float(assets_data.get("checking_savings", 0))
        profile.investment_accounts = float(assets_data.get("investment_accounts", 0))
        profile.primary_residence_value = float(assets_data.get("primary_residence_value", 0))
        profile.home_sale_interest = bool(assets_data.get("home_sale_interest", False))
        profile.other_real_estate = float(assets_data.get("other_real_estate", 0))
        profile.other_resources = float(assets_data.get("other_resources", 0))
        profile.total_asset_value = (
            profile.checking_savings +
            profile.investment_accounts +
            profile.primary_residence_value +
            profile.other_real_estate +
            profile.other_resources
        )
    
    # ==== HEALTH INSURANCE ASSESSMENT ====
    health_data = assessments_state.get("health_insurance", {})
    if health_data:
        profile.has_medicare = bool(health_data.get("has_medicare", False))
        profile.medicare_parts = health_data.get("medicare_parts", [])
        profile.has_medicare_advantage = bool(health_data.get("has_medicare_advantage", False))
        profile.has_medicare_supplement = bool(health_data.get("has_medicare_supplement", False))
        profile.medicare_premium_monthly = float(health_data.get("medicare_premium_monthly", 0))
        
        profile.has_medicaid = bool(health_data.get("has_medicaid", False))
        profile.medicaid_covers_ltc = bool(health_data.get("medicaid_covers_ltc", False))
        
        profile.has_ltc_insurance = bool(health_data.get("has_ltc_insurance", False))
        profile.ltc_daily_benefit = float(health_data.get("ltc_daily_benefit", 0))
        profile.ltc_benefit_period_months = int(health_data.get("ltc_benefit_period_months", 0))
        profile.ltc_elimination_days = int(health_data.get("ltc_elimination_days", 0))
        
        profile.has_private_insurance = bool(health_data.get("has_private_insurance", False))
        profile.private_insurance_premium_monthly = float(health_data.get("private_insurance_premium_monthly", 0))
    
    # ==== LIFE INSURANCE ASSESSMENT ====
    life_data = assessments_state.get("life_insurance", {})
    if life_data:
        profile.has_life_insurance = life_data.get("has_life_insurance", "no")
        profile.life_insurance_type = life_data.get("life_insurance_type")
        profile.life_insurance_face_value = float(life_data.get("life_insurance_face_value", 0))
        profile.life_insurance_cash_value = float(life_data.get("life_insurance_cash_value", 0))
        profile.life_insurance_premium_monthly = float(life_data.get("life_insurance_premium_monthly", 0))
        
        profile.has_annuities = life_data.get("has_annuities", "no")
        profile.annuity_current_value = float(life_data.get("annuity_current_value", 0))
        profile.annuity_monthly_income = float(life_data.get("annuity_monthly_income", 0))
        
        profile.total_accessible_life_value = (
            profile.life_insurance_cash_value +
            profile.annuity_current_value
        )
    
    # ==== VA BENEFITS ASSESSMENT (optional - flag-gated) ====
    va_data = assessments_state.get("va_benefits", {})
    if va_data:
        profile.has_va_benefits = va_data.get("has_va_benefits", "no")
        
        # Parse VA disability rating (comes as string like "50%" or "100%")
        rating_str = va_data.get("va_disability_rating", "0")
        try:
            # Remove '%' if present and convert to int
            profile.va_disability_rating = int(rating_str.replace("%", "")) if rating_str else 0
        except (ValueError, AttributeError):
            profile.va_disability_rating = 0
        
        profile.va_disability_monthly = float(va_data.get("va_disability_monthly", 0))
        profile.va_pension_monthly = float(va_data.get("va_pension_monthly", 0))
        
        profile.has_aid_attendance = va_data.get("has_aid_attendance", "no")
        profile.aid_attendance_monthly = float(va_data.get("aid_attendance_monthly", 0))
        
        profile.total_va_benefits_monthly = (
            profile.va_disability_monthly +
            profile.va_pension_monthly +
            profile.aid_attendance_monthly
        )
    
    # ==== MEDICAID PLANNING ASSESSMENT (optional - flag-gated) ====
    medicaid_data = assessments_state.get("medicaid_navigation", {})
    if medicaid_data:
        profile.medicaid_status = medicaid_data.get("medicaid_status", "not_enrolled")
        profile.interested_in_spend_down = bool(medicaid_data.get("interested_in_spend_down", False))
        profile.spend_down_timeline = medicaid_data.get("spend_down_timeline")
        profile.has_estate_plan = medicaid_data.get("has_estate_plan", [])
    
    # ==== CALCULATE METADATA ====
    profile.completeness_percentage = _calculate_completeness(assessments_state)
    profile.required_assessments_complete = _check_required_complete(assessments_state)
    profile.optional_assessments_complete = {
        "va_benefits": bool(va_data),
        "medicaid_planning": bool(medicaid_data)
    }
    
    import datetime
    profile.last_updated = datetime.datetime.now().isoformat()
    
    return profile


def _calculate_completeness(assessments_state: Dict[str, Any]) -> float:
    """
    Calculate overall completeness percentage based on completed assessments.
    
    Required assessments (Income, Assets) count more heavily.
    """
    # Required assessments (50% weight each = 100% total)
    required_complete = 0
    if assessments_state.get("income"):
        required_complete += 50
    if assessments_state.get("assets"):
        required_complete += 50
    
    # Optional assessments (split remaining weight)
    optional_complete = 0
    optional_assessments = ["health_insurance", "life_insurance", "va_benefits", "medicaid_navigation"]
    completed_optional = sum(1 for key in optional_assessments if assessments_state.get(key))
    
    # If any optional completed, they don't add to base score but show engagement
    # Keep it simple: required = 100%, optional enhances but doesn't count toward completion
    
    return float(required_complete)


def _check_required_complete(assessments_state: Dict[str, Any]) -> bool:
    """Check if both required assessments (Income, Assets) are complete."""
    return bool(
        assessments_state.get("income") and 
        assessments_state.get("assets")
    )


def get_financial_profile(product_key: str = "cost_planner_v2") -> Optional[FinancialProfile]:
    """
    Get cached financial profile or build new one.
    
    This is the primary entry point for accessing financial data.
    """
    # Check if we have a cached profile
    cache_key = f"{product_key}_financial_profile"
    
    # For now, always rebuild (later we can add caching logic)
    profile = build_financial_profile(product_key)
    
    # Cache it
    st.session_state[cache_key] = profile
    
    return profile


def publish_to_mcip(analysis, profile: FinancialProfile) -> bool:
    """
    Publish financial analysis summary to MCIP contracts.
    
    Creates MCIP FinancialProfile contract with summary data from expert analysis.
    
    Args:
        analysis: ExpertReviewAnalysis with calculated metrics
        profile: FinancialProfile with assessment data (for metadata)
    
    Returns:
        True if publish succeeded, False otherwise
    """
    try:
        from core.mcip import MCIP, FinancialProfile as MCIPFinancialProfile
        from datetime import datetime
        
        # Create MCIP contract with summary metrics
        mcip_profile = MCIPFinancialProfile(
            estimated_monthly_cost=analysis.estimated_monthly_cost,
            coverage_percentage=analysis.coverage_percentage,
            gap_amount=analysis.monthly_gap,
            runway_months=int(analysis.runway_months) if analysis.runway_months else 0,
            confidence=profile.completeness_percentage / 100.0,  # Convert to 0.0-1.0
            generated_at=datetime.now().isoformat(),
            status="complete" if profile.required_assessments_complete else "in_progress"
        )
        
        # Publish to MCIP
        MCIP.publish_financial_profile(mcip_profile)
        
        return True
    
    except Exception as e:
        st.error(f"Failed to publish financial profile to MCIP: {e}")
        return False
