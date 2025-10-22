#!/usr/bin/env python3
"""Update Andy's demo profile with new data."""

import json
from pathlib import Path

# New profile data
new_data = {
  "progress": {},
  "cost_v2_step": "triage",
  "gcp_v4_published": True,
  "mcip_contracts": {
    "care_recommendation": {
      "tier": "assisted_living",
      "tier_score": 18.0,
      "tier_rankings": [
        ["memory_care_high_acuity", 70.0],
        ["memory_care", 32.0],
        ["assisted_living", 18.0],
        ["in_home", 12.5],
        ["no_care_needed", 4.0]
      ],
      "confidence": 0.73,
      "flags": [
        {"id": "low_access", "label": "Limited Service Access", "description": "Somewhat isolated location with limited healthcare access", "tone": "info", "priority": 3, "cta": {"label": "See Available Services", "route": "partners", "filter": "home_care"}},
        {"id": "moderate_dependence", "label": "Regular Assistance Needed", "description": "Needs regular help with daily activities", "tone": "warning", "priority": 2, "cta": {"label": "Learn About Care Options", "route": "learning", "filter": "daily_living_support"}},
        {"id": "moderate_mobility", "label": "Mobility Assistance Needed", "description": "Uses cane or walker, may need accessibility modifications", "tone": "info", "priority": 3, "cta": {"label": "Learn About Mobility Support", "route": "learning", "filter": "mobility_support"}},
        {"id": "moderate_safety_concern", "label": "Safety Monitoring Needed", "description": "One fall or safety concerns that warrant attention", "tone": "warning", "priority": 2, "cta": {"label": "See Safety Resources", "route": "learning", "filter": "safety"}},
        {"id": "chronic_present", "label": "Chronic Conditions", "description": "One or more chronic health conditions requiring management", "tone": "info", "priority": 2, "cta": {"label": "Learn About Health Management", "route": "learning", "filter": "health_management"}},
        {"id": "mild_cognitive_decline", "label": "Mild Memory Changes", "description": "Occasional forgetfulness that may benefit from monitoring", "tone": "info", "priority": 3, "cta": {"label": "Learn About Memory Support", "route": "learning", "filter": "memory_care"}},
        {"id": "moderate_risk", "label": "Emotional Support Helpful", "description": "Emotional ups and downs that could benefit from support", "tone": "info", "priority": 3, "cta": {"label": "Explore Wellness Resources", "route": "learning", "filter": "mental_health"}},
        {"id": "veteran_aanda_risk", "label": "Veteran A&A Eligible", "description": "May qualify for VA Aid & Attendance benefits", "tone": "info", "priority": 3, "cta": {"label": "Learn About VA Benefits", "route": "learning", "filter": "veteran_benefits"}},
        {"id": "limited_support", "label": "Limited Caregiver Availability", "description": "Limited caregiver support may not be sufficient", "tone": "info", "priority": 2, "cta": {"label": "Explore Support Options", "route": "learning", "filter": "caregiver_support"}},
        {"id": "no_support", "label": "No Caregiver Support", "description": "No regular caregiver available, increasing care needs", "tone": "warning", "priority": 1, "cta": {"label": "Find Caregiver Resources", "route": "partners", "filter": "caregiver_support"}}
      ],
      "rationale": [
        "Based on 18 points, we recommend: Assisted Living",
        "Daily Living: 8 points",
        "  • No regular support",
        "Medication Mobility: 7 points",
        "  • Moderate – daily meds, some complexity",
        "Cognition Mental Health: 2 points"
      ],
      "generated_at": "2025-10-19T15:44:14.625165Z",
      "version": "4.0.0",
      "input_snapshot_id": "gcp_v4_anon_20251019_154414",
      "rule_set": "standard_2025_q4",
      "next_step": {
        "product": "cost_planner",
        "route": "cost_v2",
        "label": "Calculate Costs",
        "reason": "Calculate financial impact of Assisted Living care"
      },
      "status": "complete",
      "last_updated": "2025-10-19T15:44:14.625199Z",
      "needs_refresh": False
    },
    "financial_profile": None,
    "advisor_appointment": None,
    "journey": {
      "current_hub": "concierge",
      "completed_products": ["gcp"],
      "unlocked_products": ["gcp", "cost_planner", "pfma"],
      "recommended_next": "cost_planner"
    },
    "waiting_room": {
      "advisor_prep_status": "not_started",
      "trivia_status": "not_started",
      "current_focus": "advisor_prep"
    }
  },
  "cost_v2_qualifiers": {
    "is_on_medicaid": False,
    "is_veteran": True,
    "is_homeowner": False
  },
  "gcp_care_recommendation": {
    "progress": 100.0,
    "status": "done",
    "age_range": "75_84",
    "living_situation": "alone",
    "isolation": "somewhat",
    "flags": {
      "low_access": True,
      "moderate_dependence": True,
      "moderate_mobility": True,
      "moderate_safety_concern": True,
      "chronic_present": True,
      "mild_cognitive_decline": True,
      "moderate_risk": True,
      "veteran_aanda_risk": True,
      "limited_support": True,
      "no_support": True
    },
    "meds_complexity": "moderate",
    "mobility": "walker",
    "falls": "one",
    "chronic_conditions": ["arthritis", "diabetes", "hypertension"],
    "additional_conditions": [],
    "memory_changes": "occasional",
    "mood": "mostly_good",
    "help_overall": "some_help",
    "badls": ["mobility"],
    "iadls": ["finances", "med_management"],
    "hours_per_day": "1-3h",
    "primary_support": "none"
  },
  "profile": {
    "qualifiers": {
      "is_on_medicaid": False,
      "is_veteran": True,
      "is_homeowner": False
    }
  },
  "auth": {
    "user_id": "demo_andy_assisted_gcp_complete",
    "is_authenticated": True
  },
  "flags": {
    "is_veteran": True,
    "medicaid_planning_interest": False
  },
  "tiles": {
    "gcp_v4": {
      "progress": 100.0,
      "status": "done",
      "last_step": 5,
      "saved_state": {
        "progress": 80.0,
        "status": "doing",
        "age_range": "75_84",
        "living_situation": "alone",
        "isolation": "somewhat",
        "flags": {
          "low_access": True,
          "moderate_dependence": True,
          "moderate_mobility": True,
          "moderate_safety_concern": True,
          "chronic_present": True,
          "mild_cognitive_decline": True,
          "moderate_risk": True,
          "veteran_aanda_risk": True,
          "limited_support": True,
          "no_support": True
        },
        "meds_complexity": "moderate",
        "mobility": "walker",
        "falls": "one",
        "chronic_conditions": ["arthritis", "diabetes", "hypertension"],
        "additional_conditions": [],
        "memory_changes": "occasional",
        "mood": "mostly_good",
        "help_overall": "some_help",
        "badls": ["mobility"],
        "iadls": ["finances", "med_management"],
        "hours_per_day": "1-3h",
        "primary_support": "none"
      }
    }
  },
  "cost_v2_quick_estimate": {
    "estimate": {
      "monthly_base": 4500,
      "monthly_adjusted": 7574.212799999999,
      "annual": 90890.55359999998,
      "three_year": 272671.66079999995,
      "five_year": 454452.7679999999,
      "multiplier": 1.15,
      "region_name": "Seattle (Downtown/Core)",
      "care_tier": "assisted_living",
      "breakdown": {
        "base_cost": 4500,
        "regional_adjustment": 674.9999999999995,
        "high_adl_support_addon": 517.5,
        "medication_management_addon": 455.40000000000003,
        "behavioral_care_addon": 737.7479999999999,
        "chronic_conditions_addon": 688.5648
      }
    },
    "care_tier": "assisted_living",
    "zip_code": "98101"
  },
  "preferences": {},
  "uid": "demo_andy_assisted_gcp_complete",
  "last_updated": 1729354438.932980,
  "created_at": 1729354438.932941
}

# Write to file
output_path = Path("data/users/demo/andy_assisted_gcp_complete.json")

print(f"Writing updated profile to: {output_path}")

with open(output_path, 'w') as f:
    json.dump(new_data, f, indent=2)

print("✅ Profile updated successfully!")

# Verify it's valid JSON
with open(output_path) as f:
    verified = json.load(f)

print(f"✅ Verified: Profile has {len(verified)} top-level keys")
print(f"✅ GCP status: {verified['mcip_contracts']['care_recommendation']['status']}")
print(f"✅ GCP tier: {verified['mcip_contracts']['care_recommendation']['tier']}")
print(f"✅ Tiles GCP status: {verified['tiles']['gcp_v4']['status']}")
