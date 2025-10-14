"""
Flag definitions for GCP v4 care recommendation module.

Flags represent risk factors or support needs that route to specific resources.
Each flag includes metadata for rendering in MCIP panels and action cards.
"""

from typing import Dict, Any


FLAGS_SCHEMA = {
    "falls_risk": {
        "id": "falls_risk",
        "label": "High Fall Risk",
        "description": "2+ falls in the past year or significant mobility challenges requiring safety interventions",
        "tone": "warning",
        "priority": 1,
        "cta": {
            "label": "See Fall Prevention Resources",
            "route": "learning",
            "filter": "fall_prevention"
        }
    },
    
    "memory_support": {
        "id": "memory_support",
        "label": "Memory Care Needed",
        "description": "Alzheimer's or dementia diagnosis requiring specialized memory care environment",
        "tone": "critical",
        "priority": 0,
        "cta": {
            "label": "Find Memory Care Facilities",
            "route": "partners",
            "filter": "memory_care"
        }
    },
    
    "behavioral_concerns": {
        "id": "behavioral_concerns",
        "label": "Behavioral Support Required",
        "description": "Wandering, aggression, or other behaviors requiring specialized behavioral care",
        "tone": "critical",
        "priority": 0,
        "cta": {
            "label": "Find Specialized Facilities",
            "route": "partners",
            "filter": "behavioral_support"
        }
    },
    
    "medication_management": {
        "id": "medication_management",
        "label": "Medication Management Needed",
        "description": "Complex medication regimen requiring professional oversight and administration",
        "tone": "warning",
        "priority": 2,
        "cta": {
            "label": "Learn About Med Management",
            "route": "learning",
            "filter": "medication"
        }
    },
    
    "isolation_risk": {
        "id": "isolation_risk",
        "label": "Social Isolation Risk",
        "description": "Living alone with limited social interaction, increasing health risks",
        "tone": "info",
        "priority": 3,
        "cta": {
            "label": "Explore Social Programs",
            "route": "learning",
            "filter": "social_engagement"
        }
    },
    
    "adl_support_high": {
        "id": "adl_support_high",
        "label": "Extensive ADL Support",
        "description": "Needs help with multiple activities of daily living (bathing, dressing, eating, etc.)",
        "tone": "warning",
        "priority": 2,
        "cta": {
            "label": "Learn About Care Options",
            "route": "learning",
            "filter": "daily_living_support"
        }
    },
    
    "mobility_limited": {
        "id": "mobility_limited",
        "label": "Limited Mobility",
        "description": "Wheelchair or bedbound status requiring accessible environment",
        "tone": "warning",
        "priority": 2,
        "cta": {
            "label": "Find Accessible Facilities",
            "route": "partners",
            "filter": "wheelchair_accessible"
        }
    },
    
    "chronic_conditions": {
        "id": "chronic_conditions",
        "label": "Multiple Chronic Conditions",
        "description": "Multiple health conditions requiring coordinated medical oversight",
        "tone": "warning",
        "priority": 2,
        "cta": {
            "label": "Learn About Health Management",
            "route": "learning",
            "filter": "health_management"
        }
    },
    
    "safety_concerns": {
        "id": "safety_concerns",
        "label": "Safety Concerns",
        "description": "Living situation poses safety risks requiring environmental modifications or supervision",
        "tone": "warning",
        "priority": 1,
        "cta": {
            "label": "See Safety Resources",
            "route": "learning",
            "filter": "safety"
        }
    },
    
    "caregiver_stress": {
        "id": "caregiver_stress",
        "label": "Caregiver Burden",
        "description": "Primary caregiver experiencing high stress or burnout",
        "tone": "info",
        "priority": 3,
        "cta": {
            "label": "Caregiver Support Resources",
            "route": "learning",
            "filter": "caregiver_support"
        }
    }
}


def build_flag(flag_id: str) -> Dict[str, Any]:
    """Build a flag object from schema.
    
    Args:
        flag_id: Flag identifier (e.g., "falls_risk")
    
    Returns:
        Flag dict with all metadata for rendering
    """
    return FLAGS_SCHEMA.get(flag_id, {
        "id": flag_id,
        "label": flag_id.replace("_", " ").title(),
        "description": f"Flag: {flag_id}",
        "tone": "info",
        "priority": 99,
        "cta": None
    })


def build_flags(flag_ids: list) -> list:
    """Build multiple flag objects from IDs.
    
    Args:
        flag_ids: List of flag identifiers
    
    Returns:
        List of flag dicts
    """
    return [build_flag(flag_id) for flag_id in flag_ids]
