"""
Customer Preferences System - CRM Matching Enhancement

Collects and manages customer preferences for enhanced community matching.
Integrates with MCIP for persistence and CRM QuickBase integration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st


@dataclass
class CustomerPreferences:
    """Customer preferences for community matching and advisor preparation."""

    # Geographic & Location Preferences
    preferred_regions: List[str] = field(default_factory=list)  # ["bellevue_area", "seattle", "eastside"]
    max_distance_miles: Optional[int] = None  # Maximum distance from current location or family
    transportation_access: str = "flexible"  # "public_transit", "family_visits", "driving", "flexible"
    
    # Care Level & Services
    care_environment_preference: str = "assisted_living"  # "independent", "assisted_living", "memory_care", "in_home"
    specific_care_services: List[str] = field(default_factory=list)  # ["medication_mgmt", "mobility_help", "diabetes_care"]
    medical_specializations: List[str] = field(default_factory=list)  # ["physical_therapy", "diabetes", "alzheimers"]
    
    # Financial Preferences
    budget_comfort_level: str = "moderate"  # "tight", "moderate", "comfortable", "luxury"
    payment_preference: List[str] = field(default_factory=list)  # ["private_pay", "va_benefits", "insurance"]
    priority_vs_budget: str = "balanced"  # "essential_only", "balanced", "prefer_amenities"
    
    # Social & Lifestyle
    activity_preferences: List[str] = field(default_factory=list)  # ["fitness", "arts", "social", "quiet", "outdoors"]
    dining_preferences: List[str] = field(default_factory=list)  # ["dietary_restrictions", "flexible_timing", "social_dining"]
    pet_requirements: str = "none"  # "none", "current_pets", "pet_friendly_preferred"
    visitor_importance: str = "moderate"  # "low", "moderate", "high", "critical"
    
    # Timeline & Urgency
    move_timeline: str = "exploring"  # "immediate", "2_4_weeks", "2_3_months", "exploring", "future_planning"
    current_situation_stability: str = "stable"  # "urgent", "declining", "stable", "planned"
    move_triggers: List[str] = field(default_factory=list)  # ["safety_concern", "family_worry", "planned_transition"]
    
    # Family & Support Context
    primary_family_contact: str = ""  # Name of main decision maker/contact
    family_location: str = "nearby"  # "nearby", "distant", "out_of_state", "none"
    current_support_level: str = "independent"  # "independent", "family_help", "hired_care", "minimal"
    
    # Metadata
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"  # Schema version for future compatibility
    completion_status: str = "partial"  # "partial", "complete", "needs_update"


class PreferencesManager:
    """Manages customer preferences persistence and integration with MCIP."""
    
    @classmethod
    def get_preferences(cls) -> CustomerPreferences | None:
        """Get current customer preferences from MCIP contracts.
        
        Returns:
            CustomerPreferences object or None if not collected yet
        """
        # Check MCIP contracts first
        contracts = st.session_state.get("mcip_contracts", {})
        pref_data = contracts.get("customer_preferences")
        
        if pref_data:
            return CustomerPreferences(**pref_data)
        
        # Fallback to session state (temporary storage)
        pref_data = st.session_state.get("customer_preferences")
        if pref_data:
            return CustomerPreferences(**pref_data)
        
        return None
    
    @classmethod
    def save_preferences(cls, preferences: CustomerPreferences) -> None:
        """Save customer preferences to MCIP contracts for persistence.
        
        Args:
            preferences: CustomerPreferences object to save
        """
        from dataclasses import asdict
        
        # Update timestamp
        preferences.updated_at = datetime.now().isoformat()
        
        # Save to MCIP contracts (persistent across sessions)
        if "mcip_contracts" not in st.session_state:
            st.session_state["mcip_contracts"] = {}
        
        st.session_state["mcip_contracts"]["customer_preferences"] = asdict(preferences)
        
        # Also save to session state for immediate access
        st.session_state["customer_preferences"] = asdict(preferences)
        
        # Log event for tracking
        from core.events import log_event
        log_event(
            "preferences.updated",
            {
                "completion_status": preferences.completion_status,
                "move_timeline": preferences.move_timeline,
                "care_environment": preferences.care_environment_preference,
                "regions_count": len(preferences.preferred_regions),
            }
        )
    
    @classmethod
    def create_default_preferences(cls, care_recommendation: str = None) -> CustomerPreferences:
        """Create default preferences based on care recommendation.
        
        Args:
            care_recommendation: Care tier from GCP assessment
            
        Returns:
            CustomerPreferences with smart defaults
        """
        # Set care environment based on GCP recommendation
        care_env = "assisted_living"  # Default
        if care_recommendation:
            care_env = care_recommendation
        
        # Set default regions based on location (if available)
        default_regions = []
        profile = st.session_state.get("profile", {})
        location = profile.get("location", "").lower()
        if "bellevue" in location or "seattle" in location:
            default_regions = ["bellevue_area", "eastside"]
        elif "wa" in location or "washington" in location:
            default_regions = ["washington_state"]
        
        return CustomerPreferences(
            care_environment_preference=care_env,
            preferred_regions=default_regions,
            completion_status="partial",
        )
    
    @classmethod
    def get_crm_matching_data(cls) -> Dict[str, Any]:
        """Extract preferences data for CRM community matching.
        
        Returns:
            Dict with key-value pairs for CRM matching algorithm
        """
        preferences = cls.get_preferences()
        if not preferences:
            return {}
        
        return {
            # Geographic matching
            "preferred_regions": preferences.preferred_regions,
            "max_distance_miles": preferences.max_distance_miles,
            "transportation_needs": preferences.transportation_access,
            
            # Care level matching
            "care_environment": preferences.care_environment_preference,
            "required_services": preferences.specific_care_services,
            "medical_specializations": preferences.medical_specializations,
            
            # Urgency for vacancy matching
            "timeline": preferences.move_timeline,
            "urgency_level": preferences.current_situation_stability,
            
            # Budget considerations
            "budget_level": preferences.budget_comfort_level,
            "payment_methods": preferences.payment_preference,
            
            # Lifestyle matching
            "activity_preferences": preferences.activity_preferences,
            "pet_requirements": preferences.pet_requirements,
            "visitor_importance": preferences.visitor_importance,
            
            # Family context
            "family_proximity": preferences.family_location,
            "support_level": preferences.current_support_level,
            
            # Metadata
            "preferences_complete": preferences.completion_status == "complete",
            "last_updated": preferences.updated_at,
        }
    
    @classmethod
    def get_completion_percentage(cls) -> int:
        """Calculate completion percentage of preferences collection.
        
        Returns:
            Percentage (0-100) of preferences completed
        """
        preferences = cls.get_preferences()
        if not preferences:
            return 0
        
        # Count completed sections
        completed = 0
        total = 7  # Total number of preference sections
        
        # Geographic preferences
        if preferences.preferred_regions or preferences.max_distance_miles:
            completed += 1
        
        # Care preferences  
        if preferences.care_environment_preference != "assisted_living" or preferences.specific_care_services:
            completed += 1
        
        # Financial preferences
        if preferences.budget_comfort_level != "moderate" or preferences.payment_preference:
            completed += 1
        
        # Lifestyle preferences
        if preferences.activity_preferences or preferences.dining_preferences:
            completed += 1
        
        # Timeline preferences
        if preferences.move_timeline != "exploring":
            completed += 1
        
        # Family context
        if preferences.primary_family_contact or preferences.family_location != "nearby":
            completed += 1
        
        # Support context
        if preferences.current_support_level != "independent":
            completed += 1
        
        return int((completed / total) * 100)


# Integration functions for other modules
def get_preferences_for_crm() -> Dict[str, Any]:
    """Get preferences data formatted for CRM matching.
    
    Returns:
        Dictionary suitable for CRM community matching algorithms
    """
    return PreferencesManager.get_crm_matching_data()


def is_preferences_collection_complete() -> bool:
    """Check if customer has completed preferences collection.
    
    Returns:
        True if preferences are marked as complete
    """
    preferences = PreferencesManager.get_preferences()
    return preferences and preferences.completion_status == "complete"


def get_preferences_completion_percentage() -> int:
    """Get completion percentage for UI progress indicators.
    
    Returns:
        Percentage (0-100) of preferences completed
    """
    return PreferencesManager.get_completion_percentage()