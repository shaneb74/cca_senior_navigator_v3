"""
Cost Calculator

Core calculation engine for Cost Planner v2.
Uses base costs + regional multipliers + care tier adjustments.

Base costs from config/cost_config.v3.json
Regional multipliers from RegionalDataProvider
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .regional_data import RegionalDataProvider


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
    breakdown: Dict[str, float]  # Component breakdown
    

class CostCalculator:
    """Cost calculation engine."""
    
    _base_costs: Optional[Dict[str, Any]] = None
    _config_path = "config/cost_config.v3.json"
    
    @classmethod
    def _load_base_costs(cls) -> Dict[str, Any]:
        """Load base costs once and cache."""
        if cls._base_costs is None:
            config_path = os.path.join(os.getcwd(), cls._config_path)
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    cls._base_costs = json.load(f)
            else:
                # Fallback to minimal config
                cls._base_costs = {
                    "care_tiers": {
                        "independent_living": {"monthly_base": 2500},
                        "assisted_living": {"monthly_base": 4500},
                        "memory_care": {"monthly_base": 6500},
                        "in_home_care": {"monthly_base": 3500}
                    }
                }
        return cls._base_costs
    
    @classmethod
    def calculate_quick_estimate(
        cls,
        care_tier: str,
        zip_code: Optional[str] = None,
        state: Optional[str] = None
    ) -> CostEstimate:
        """Calculate quick estimate for intro page.
        
        Uses base cost + regional multiplier only.
        No additional services or detailed breakdown.
        
        Args:
            care_tier: Care tier (independent_living, assisted_living, memory_care, in_home_care)
            zip_code: Optional ZIP code for regional adjustment
            state: Optional state code for regional adjustment
            
        Returns:
            CostEstimate with basic calculations
        """
        base_costs = cls._load_base_costs()
        
        # Get base cost for tier
        tier_config = base_costs.get("care_tiers", {}).get(care_tier, {})
        monthly_base = tier_config.get("monthly_base", 4000)
        
        # Get regional multiplier
        regional = RegionalDataProvider.get_multiplier(zip_code=zip_code, state=state)
        
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
            breakdown={"base_care": monthly_adjusted}
        )
    
    @classmethod
    def calculate_detailed_estimate(
        cls,
        care_tier: str,
        care_hours: Optional[int] = None,
        additional_services: Optional[Dict[str, bool]] = None,
        veteran_benefit: Optional[float] = None,
        insurance_coverage: Optional[float] = None,
        zip_code: Optional[str] = None,
        state: Optional[str] = None
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
        breakdown = {
            "base_care": monthly_base * regional.multiplier
        }
        
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
        monthly_adjusted = subtotal + breakdown.get("veteran_benefit", 0) + breakdown.get("insurance_coverage", 0)
        
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
            breakdown=breakdown
        )
