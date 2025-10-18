"""
Cost Calculator

Core calculation engine for Cost Planner v2.
Uses base costs + regional multipliers + care tier adjustments.

Base costs from config/cost_config.v3.json
Regional multipliers from RegionalDataProvider
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Optional, Dict, List

from .regional_data import RegionalDataProvider

# Import flag manager for validation
try:
    from core import flag_manager
    from core.flags import COST_MODEL_FLAGS

    FLAG_MANAGER_AVAILABLE = True
except ImportError:
    FLAG_MANAGER_AVAILABLE = False
    COST_MODEL_FLAGS = []


# COST ADJUSTMENTS MAPPING
# Maps GCP flags to cost adjustment percentages and rationale
COST_ADJUSTMENTS = {
    "memory_support": {
        "percentage": 0.20,
        "label": "Severe Cognitive Impairment",
        "rationale": "Alzheimer's/dementia requiring specialized memory care and trained staff",
    },
    "mobility_limited": {
        "percentage": 0.15,
        "label": "Serious Mobility/Transferring Issues",
        "rationale": "Wheelchair/bedbound requiring lifting assistance and adaptive equipment",
    },
    "adl_support_high": {
        "percentage": 0.10,
        "label": "High-Level ADL Support",
        "rationale": "Extensive help with bathing, dressing, eating, toileting",
    },
    "medication_management": {
        "percentage": 0.08,
        "label": "Complex Medication Management",
        "rationale": "Multiple prescriptions requiring professional oversight and administration",
    },
    "behavioral_concerns": {
        "percentage": 0.12,
        "label": "Behavioral/Psychiatric Care",
        "rationale": "Wandering, aggression requiring specialized behavioral support",
    },
    "falls_risk": {
        "percentage": 0.08,
        "label": "Fall Risk/Safety Monitoring",
        "rationale": "2+ falls/year requiring enhanced supervision and safety measures",
    },
    "chronic_conditions": {
        "percentage": 0.10,
        "label": "Multiple Chronic Conditions",
        "rationale": "Multiple health conditions requiring coordinated medical care",
    },
}


# FLAG MAPPING: GCP flags → Cost Planner flags
# Maps the flags from care recommendation to cost adjustment flags
FLAG_MAPPINGS = {
    # Cognitive/Memory flags
    "severe_cognitive_risk": "memory_support",
    "moderate_cognitive_decline": "memory_support",
    # Mobility flags
    "high_mobility_dependence": "mobility_limited",
    # ADL/Dependence flags
    "high_dependence": "adl_support_high",
    "moderate_dependence": "adl_support_high",  # Treat moderate as high for cost purposes
    # Behavioral flags
    "mental_health_concern": "behavioral_concerns",
    "high_risk": "behavioral_concerns",
    "moderate_risk": "behavioral_concerns",
    # Fall/Safety flags
    "falls_multiple": "falls_risk",
    "high_safety_concern": "falls_risk",
    "moderate_safety_concern": "safety_concerns",
    # Chronic conditions
    "chronic_present": "chronic_conditions",
}


def _normalize_flags(gcp_flags: list[str]) -> list[str]:
    """Normalize GCP flags to cost planner flag names.

    Args:
        gcp_flags: List of flag IDs from GCP care recommendation

    Returns:
        List of normalized cost planner flag IDs
    """
    normalized = set()

    for flag in gcp_flags:
        # Direct match (cost planner flags)
        if flag in COST_ADJUSTMENTS:
            normalized.add(flag)
        # Mapped GCP flag
        elif flag in FLAG_MAPPINGS:
            normalized.add(FLAG_MAPPINGS[flag])

    return list(normalized)


@dataclass
class CostEstimate:
    """Single cost estimate result."""

    monthly_base: float
    monthly_adjusted: float
    annual: float
    three_year: float
    five_year: float
    multiplier: float
    region_name: str
    care_tier: str
    breakdown: dict[str, float]  # Component breakdown

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict for persistence."""
        return {
            "monthly_base": self.monthly_base,
            "monthly_adjusted": self.monthly_adjusted,
            "annual": self.annual,
            "three_year": self.three_year,
            "five_year": self.five_year,
            "multiplier": self.multiplier,
            "region_name": self.region_name,
            "care_tier": self.care_tier,
            "breakdown": self.breakdown,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CostEstimate":
        """Reconstruct from dict loaded from persistence."""
        return cls(
            monthly_base=data["monthly_base"],
            monthly_adjusted=data["monthly_adjusted"],
            annual=data["annual"],
            three_year=data["three_year"],
            five_year=data["five_year"],
            multiplier=data["multiplier"],
            region_name=data["region_name"],
            care_tier=data["care_tier"],
            breakdown=data["breakdown"],
        )


class CostCalculator:
    """Cost calculation engine."""

    _base_costs: Optional[dict[str, Any]] = None
    _config_path = "config/cost_config.v3.json"

    @classmethod
    def _load_base_costs(cls) -> dict[str, Any]:
        """Load base costs once and cache."""
        if cls._base_costs is None:
            config_path = os.path.join(os.getcwd(), cls._config_path)
            if os.path.exists(config_path):
                with open(config_path) as f:
                    cls._base_costs = json.load(f)
            else:
                # Fallback to minimal config with all 5 tiers
                # CRITICAL: These are the ONLY 5 allowed care tiers
                cls._base_costs = {
                    "care_tiers": {
                        "no_care_needed": {"monthly_base": 500},
                        "in_home_care": {"monthly_base": 3500},
                        "assisted_living": {"monthly_base": 4500},
                        "memory_care": {"monthly_base": 6500},
                        "memory_care_high_acuity": {"monthly_base": 9000},
                    }
                }
        return cls._base_costs

    @classmethod
    def get_active_adjustments(
        cls, flags: list[str], care_tier: str, base_amount: float
    ) -> list[dict[str, Any]]:
        """Get list of active cost adjustments for display in UI table.

        Args:
            flags: List of GCP flag IDs from MCIP
            care_tier: Care tier (for high-acuity check)
            base_amount: Starting amount (base + regional) before adjustments

        Returns:
            List of dicts with: flag_id, label, percentage, amount, rationale
        """
        active = []
        running_total = base_amount

        # Check each flag-based adjustment (cumulative application order)
        for flag_id in [
            "memory_support",
            "mobility_limited",
            "adl_support_high",
            "medication_management",
            "behavioral_concerns",
            "falls_risk",
            "chronic_conditions",
        ]:
            if flag_id in flags and flag_id in COST_ADJUSTMENTS:
                adjustment = COST_ADJUSTMENTS[flag_id]
                amount = running_total * adjustment["percentage"]
                active.append(
                    {
                        "flag_id": flag_id,
                        "label": adjustment["label"],
                        "percentage": adjustment["percentage"]
                        * 100,  # Convert to percentage for display
                        "amount": amount,
                        "rationale": adjustment["rationale"],
                    }
                )
                running_total += amount  # Cumulative

        # High-acuity tier adjustment (always applied for memory_care_high_acuity)
        if care_tier == "memory_care_high_acuity":
            amount = running_total * 0.25
            active.append(
                {
                    "flag_id": "high_acuity_tier",
                    "label": "High-Acuity Intensive Care",
                    "percentage": 25.0,
                    "amount": amount,
                    "rationale": "Intensive 24/7 skilled care for advanced dementia or medical complexity",
                }
            )

        return active

    @classmethod
    def calculate_quick_estimate_with_breakdown(
        cls, care_tier: str, zip_code: Optional[str] = None
    ) -> CostEstimate:
        """Calculate quick estimate with line-item breakdown for intro page.

        Implements spec requirements:
        - Base cost for care tier
        - Regional adjustment (ZIP→ZIP3→state→default precedence)
        - Cognitive-related add-on (+20% if memory_support flag present)
        - Mobility-related add-on (+15% if mobility_limited flag present)
        - High-acuity add-on (+25% if care_tier is memory_care_high_acuity)

        Args:
            care_tier: Care tier (no_care_needed, in_home_care, assisted_living, memory_care, memory_care_high_acuity)
            zip_code: Optional ZIP code for regional adjustment

        Returns:
            CostEstimate with detailed breakdown
        """
        from core.mcip import MCIP

        base_costs = cls._load_base_costs()

        # Get base cost for tier
        tier_config = base_costs.get("care_tiers", {}).get(care_tier, {})
        monthly_base = tier_config.get("monthly_base", 4000)

        # Get regional multiplier (ZIP→ZIP3→state→default)
        regional = RegionalDataProvider.get_multiplier(zip_code=zip_code)

        # Initialize breakdown
        breakdown = {"base_cost": monthly_base}

        # Apply regional adjustment
        regional_adjustment = monthly_base * (regional.multiplier - 1.0)
        if abs(regional_adjustment) > 0.01:  # Only show if non-zero
            breakdown["regional_adjustment"] = regional_adjustment

        # Start with base + regional
        running_total = monthly_base * regional.multiplier

        # Check for condition-based add-ons from MCIP/GCP flags
        gcp_rec = MCIP.get_care_recommendation()
        flags = []
        if gcp_rec and hasattr(gcp_rec, "flags"):
            # Extract flag IDs from flag objects
            raw_flags = [f.get("id") if isinstance(f, dict) else f for f in gcp_rec.flags]
            # Normalize GCP flags to cost planner flags
            flags = _normalize_flags(raw_flags)

        # Check for medication complexity from GCP state
        # If meds_complexity is "moderate" or "complex", add medication_management flag
        if gcp_rec:
            import streamlit as st

            gcp_state = st.session_state.get("gcp_care_recommendation", {})
            meds_complexity = gcp_state.get("meds_complexity")
            if meds_complexity in ["moderate", "complex"]:
                if "medication_management" not in flags:
                    flags.append("medication_management")

        # Validate cost flags (CHECKPOINT 2 integration - defense in depth)
        if FLAG_MANAGER_AVAILABLE and flags:
            cost_flags = [f for f in flags if f in COST_MODEL_FLAGS]
            try:
                invalid = flag_manager.validate_flags(cost_flags, context="cost_planner.estimate")
                if invalid:
                    # Filter out invalid flags (already logged by validator)
                    flags = [f for f in flags if f not in invalid]
            except Exception as e:
                # Don't fail estimate if validation has issues
                print(f"⚠️  Warning: Flag validation error: {e}")

        # CARE MULTIPLIERS (applied cumulatively to running total)

        # 1. Severe Cognitive Impairment (+20%)
        # Triggered by: memory_support flag (Alzheimer's/dementia requiring specialized care)
        if "memory_support" in flags:
            cognitive_addon = running_total * 0.20
            breakdown["severe_cognitive_addon"] = cognitive_addon
            running_total += cognitive_addon

        # 2. Serious Mobility/Transferring Issues (+15%)
        # Triggered by: mobility_limited flag (wheelchair/bedbound requiring lifting assistance)
        if "mobility_limited" in flags:
            mobility_addon = running_total * 0.15
            breakdown["mobility_transferring_addon"] = mobility_addon
            running_total += mobility_addon

        # 3. High-Level ADL Support (+10%)
        # Triggered by: adl_support_high flag (extensive help with bathing, dressing, eating, toileting)
        if "adl_support_high" in flags:
            adl_addon = running_total * 0.10
            breakdown["high_adl_support_addon"] = adl_addon
            running_total += adl_addon

        # 4. Complex Medication Management (+8%)
        # Triggered by: medication_management flag (multiple prescriptions requiring professional oversight)
        if "medication_management" in flags:
            med_addon = running_total * 0.08
            breakdown["medication_management_addon"] = med_addon
            running_total += med_addon

        # 5. Behavioral/Psychiatric Care (+12%)
        # Triggered by: behavioral_concerns flag (wandering, aggression, requires specialized behavioral support)
        if "behavioral_concerns" in flags:
            behavioral_addon = running_total * 0.12
            breakdown["behavioral_care_addon"] = behavioral_addon
            running_total += behavioral_addon

        # 6. Fall Risk/Safety Monitoring (+8%)
        # Triggered by: falls_risk flag (2+ falls/year requiring enhanced supervision and safety measures)
        if "falls_risk" in flags:
            falls_addon = running_total * 0.08
            breakdown["fall_risk_monitoring_addon"] = falls_addon
            running_total += falls_addon

        # 7. Multiple Chronic Conditions (+10%)
        # Triggered by: chronic_conditions flag (multiple health conditions requiring coordinated medical care)
        if "chronic_conditions" in flags:
            chronic_addon = running_total * 0.10
            breakdown["chronic_conditions_addon"] = chronic_addon
            running_total += chronic_addon

        # 8. High-Acuity Care (+25%)
        # Always applied for memory_care_high_acuity tier (intensive 24/7 skilled care)
        if care_tier == "memory_care_high_acuity":
            high_acuity_addon = running_total * 0.25
            breakdown["high_acuity_intensive_addon"] = high_acuity_addon
            running_total += high_acuity_addon

        # Final monthly adjusted
        monthly_adjusted = running_total

        # Calculate projections
        annual = monthly_adjusted * 12
        three_year = annual * 3
        five_year = annual * 5

        return CostEstimate(
            monthly_base=monthly_base,
            monthly_adjusted=monthly_adjusted,
            annual=annual,
            three_year=three_year,
            five_year=five_year,
            multiplier=regional.multiplier,
            region_name=regional.region_name,
            care_tier=care_tier,
            breakdown=breakdown,
        )

    @classmethod
    def calculate_quick_estimate(
        cls, care_tier: str, zip_code: Optional[str] = None, state: Optional[str] = None
    ) -> CostEstimate:
        """Calculate quick estimate for intro page (LEGACY - use calculate_quick_estimate_with_breakdown).

        Uses base cost + regional multiplier only.
        No additional services or detailed breakdown.

        Args:
            care_tier: Care tier (no_care_needed, in_home_care, assisted_living, memory_care, memory_care_high_acuity)
            zip_code: Optional ZIP code for regional adjustment
            state: Optional state code for regional adjustment (ignored - uses ZIP precedence)

        Returns:
            CostEstimate with basic calculations
        """
        base_costs = cls._load_base_costs()

        # Get base cost for tier
        tier_config = base_costs.get("care_tiers", {}).get(care_tier, {})
        monthly_base = tier_config.get("monthly_base", 4000)

        # Get regional multiplier (ZIP precedence, state ignored)
        regional = RegionalDataProvider.get_multiplier(zip_code=zip_code)

        # Calculate adjusted costs
        monthly_adjusted = monthly_base * regional.multiplier
        annual = monthly_adjusted * 12
        three_year = annual * 3
        five_year = annual * 5

        return CostEstimate(
            monthly_base=monthly_base,
            monthly_adjusted=monthly_adjusted,
            annual=annual,
            three_year=three_year,
            five_year=five_year,
            multiplier=regional.multiplier,
            region_name=regional.region_name,
            care_tier=care_tier,
            breakdown={"base_care": monthly_adjusted},
        )

    @classmethod
    def calculate_detailed_estimate(
        cls,
        care_tier: str,
        care_hours: Optional[int] = None,
        additional_services: Optional[dict[str, bool]] = None,
        veteran_benefit: Optional[float] = None,
        insurance_coverage: Optional[float] = None,
        zip_code: Optional[str] = None,
        state: Optional[str] = None,
    ) -> CostEstimate:
        """Calculate detailed estimate with all modules.

        Includes:
        - Base care costs
        - Care hours (if applicable)
        - Additional services
        - Veteran benefits reduction
        - Insurance coverage reduction

        Args:
            care_tier: Care tier
            care_hours: Weekly care hours (in-home only)
            additional_services: Dict of service name → enabled
            veteran_benefit: Monthly VA benefit amount
            insurance_coverage: Monthly insurance coverage amount
            zip_code: ZIP code for regional adjustment
            state: State code for regional adjustment

        Returns:
            CostEstimate with full breakdown
        """
        base_costs = cls._load_base_costs()
        tier_config = base_costs.get("care_tiers", {}).get(care_tier, {})

        # Start with base cost
        monthly_base = tier_config.get("monthly_base", 4000)

        # Get regional multiplier
        regional = RegionalDataProvider.get_multiplier(zip_code=zip_code, state=state)

        # Initialize breakdown
        breakdown = {"base_care": monthly_base * regional.multiplier}

        # Add care hours (in-home care only)
        if care_tier == "in_home_care" and care_hours:
            hourly_rate = tier_config.get("hourly_rate", 25) * regional.multiplier
            monthly_hours = care_hours * 4.33  # weeks per month
            breakdown["care_hours"] = hourly_rate * monthly_hours

        # Add additional services
        if additional_services:
            services_config = base_costs.get("additional_services", {})
            for service_key, enabled in additional_services.items():
                if enabled and service_key in services_config:
                    service_cost = services_config[service_key].get("monthly_cost", 0)
                    breakdown[service_key] = service_cost * regional.multiplier

        # Calculate subtotal
        subtotal = sum(breakdown.values())

        # Apply benefits/coverage reductions
        if veteran_benefit:
            breakdown["veteran_benefit"] = -veteran_benefit
        if insurance_coverage:
            breakdown["insurance_coverage"] = -insurance_coverage

        # Calculate final monthly adjusted
        monthly_adjusted = (
            subtotal + breakdown.get("veteran_benefit", 0) + breakdown.get("insurance_coverage", 0)
        )

        # Calculate projections
        annual = monthly_adjusted * 12
        three_year = annual * 3
        five_year = annual * 5

        return CostEstimate(
            monthly_base=monthly_base,
            monthly_adjusted=monthly_adjusted,
            annual=annual,
            three_year=three_year,
            five_year=five_year,
            multiplier=regional.multiplier,
            region_name=regional.region_name,
            care_tier=care_tier,
            breakdown=breakdown,
        )
