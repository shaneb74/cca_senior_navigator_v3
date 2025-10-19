#!/usr/bin/env python3
"""
Create Andy Assisted GCP Complete Demo Profile

This script generates a demo profile for testing:
- Complete GCP journey (Assisted Living tier)
- VA A&A eligibility flags
- Age 75-84 demographic
- Multiple health conditions (arthritis, diabetes, hypertension)
- Complete MCIP contracts and tiles

Output: data/users/demo/demo_andy_assisted_gcp_complete.json
"""

import json
from pathlib import Path
import time
from datetime import datetime

# Current timestamp for created_at/last_updated
TIMESTAMP = time.time()

# UID must be prefixed with "demo_" for protected demo loading
UID = "demo_andy_assisted_gcp_complete"

data = {
    # =========================================================================
    # IDENTITY & AUTH
    # =========================================================================
    "uid": UID,
    "created_at": TIMESTAMP,
    "last_updated": TIMESTAMP,
    
    # Auth block - required for authenticated demo user
    "auth": {
        "user_id": UID,
        "is_authenticated": True,
        "name": "Andy Assisted GCP Complete",
        "email": "andy@demo.test"
    },
    
    # =========================================================================
    # PROFILE & QUALIFIERS
    # =========================================================================
    "profile": {
        "name": "Andy",
        "age_range": "75-84",
        "location": "San Francisco, CA",
        "zip_code": "94102",
        "relationship": "self",
        "qualifiers": {
            "is_veteran": True,
            "service_connected_disability": False,
            "has_spouse": False,
            "spouse_needs_care": False
        }
    },
    
    # Duplicate qualifiers for Cost Planner compatibility
    "cost_v2_qualifiers": {
        "is_veteran": True,
        "service_connected_disability": False,
        "has_spouse": False,
        "spouse_needs_care": False
    },
    
    # =========================================================================
    # FEATURE FLAGS
    # =========================================================================
    "flags": {
        "is_veteran": True,
        "veteran_aanda_risk": True,
        "enable_cost_planner_v2": True
    },
    
    # =========================================================================
    # GCP CARE RECOMMENDATION
    # =========================================================================
    "gcp_care_recommendation": {
        "tier": "assisted_living",
        "tier_score": 18,
        "confidence": 0.73,
        "status": "complete",
        "progress": 100,
        "assessment": {
            "age_range": "75-84",
            "conditions": ["arthritis", "diabetes", "hypertension"],
            "adl_count": 2,
            "iadl_count": 3,
            "cognitive_decline": False,
            "wandering_risk": False,
            "safety_concerns": True,
            "living_situation": "alone",
            "primary_caregiver": "none",
            "caregiver_hours": 0,
            "professional_help": False
        },
        "flags": {
            "veteran_aanda_risk": True,
            "no_support": True,
            "safety_risk": True,
            "falls_risk": True,
            "medication_management": True,
            "nutrition_risk": True,
            "isolation_risk": True,
            "transportation_needs": True,
            "financial_stress": True,
            "housing_instability": False
        },
        "rationale": "Based on assessment, assisted living recommended due to ADL support needs, IADL assistance requirements, and lack of family support system. Safety concerns and living alone are contributing factors.",
        "next_step": "Review cost estimates and explore facility options in San Francisco area."
    },
    
    # Mark GCP as published
    "gcp_v4_published": True,
    
    # =========================================================================
    # MCIP CONTRACTS
    # =========================================================================
    "mcip_contracts": {
        # Care recommendation - mirrors gcp_care_recommendation
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
            "status": "complete",
            "flags": [
                {
                    "id": "veteran_aanda_risk",
                    "label": "VA A&A Eligible",
                    "description": "May qualify for VA Aid & Attendance benefits",
                    "tone": "success",
                    "priority": 1,
                    "cta": {
                        "label": "Check VA Benefits",
                        "route": "learning",
                        "filter": "va_benefits"
                    }
                },
                {
                    "id": "no_support",
                    "label": "Limited Support System",
                    "description": "Living alone with no regular caregiver support",
                    "tone": "warning",
                    "priority": 2,
                    "cta": {
                        "label": "Explore Care Options",
                        "route": "partners",
                        "filter": "assisted_living"
                    }
                },
                {
                    "id": "safety_risk",
                    "label": "Safety Concerns",
                    "description": "Multiple safety factors identified",
                    "tone": "warning",
                    "priority": 2,
                    "cta": {
                        "label": "Learn About Safety",
                        "route": "learning",
                        "filter": "safety"
                    }
                }
            ],
            "rationale": [
                "Assisted living recommended based on moderate ADL/IADL needs",
                "Lack of family support system increases care requirements",
                "Safety concerns warrant 24/7 staff availability",
                "VA benefits may help offset costs"
            ],
            "generated_at": datetime.now().isoformat(),
            "version": "4.0",
            "input_snapshot_id": f"andy_gcp_{int(TIMESTAMP)}",
            "rule_set": "gcp_v4_standard",
            "next_step": {
                "product": "cost_planner",
                "label": "Explore Costs",
                "reason": "Review budget and payment options"
            },
            "last_updated": datetime.now().isoformat(),
            "needs_refresh": False
        },
        
        # NO financial_profile - Andy hasn't done Cost Planner yet
        # This will be created when/if Andy completes Cost Planner
        
        # Journey tracking
        "journey": {
            "current_hub": "concierge",
            "completed_products": ["gcp"],
            "unlocked_products": ["cost_planner", "facility_finder"],
            "recommended_next": "cost_planner"
        },
        
        # Waiting room (for advisor appointments)
        "waiting_room": {
            "status": "available",
            "appointment_scheduled": False
        }
    },
    
    # =========================================================================
    # COST PLANNER V2 - QUICK ESTIMATE ONLY
    # =========================================================================
    "cost_v2_quick_estimate": {
        "location": "San Francisco, CA",
        "tier": "assisted_living",
        "tier_multiplier": 1.4,
        "base_cost": 5410,
        "adjusted_cost": 7574,
        "breakdown": {
            "room_board": 4500,
            "care_services": 1800,
            "medication_management": 450,
            "activities": 300,
            "transportation": 250,
            "personal_care": 274
        },
        "created_at": TIMESTAMP
    },
    
    # Cost Planner step - set to "exit" to show completed summary
    "cost_v2_step": "welcome",
    
    # Guest mode and triage - include even if empty
    "cost_v2_guest_mode": False,
    "cost_v2_triage": {},
    
    # Modules - empty for now (Andy only has quick estimate)
    "cost_v2_modules": {},
    
    # =========================================================================
    # TILES
    # =========================================================================
    "tiles": {
        "gcp_v4": {
            "status": "done",
            "progress": 100.0,
            "tier": "assisted_living",
            "confidence": 0.73,
            "tier_score": 18,
            "last_updated": TIMESTAMP
        },
        "cost_planner_v2": {
            "status": "not_started",
            "progress": 0,
            "last_updated": TIMESTAMP
        }
    },
    
    # Progress - empty unless using product-wide meters
    "progress": {},
    
    # Preferences - empty unless specific UI defaults needed
    "preferences": {}
}


def main():
    """Create the Andy demo profile file."""
    # Ensure demo directory exists
    demo_dir = Path("data/users/demo")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # Output file path (in protected demo directory)
    output_file = demo_dir / f"{UID}.json"
    
    # Check if app is running (file might be locked)
    if output_file.exists():
        print(f"⚠️  Profile file already exists: {output_file}")
        response = input("Overwrite? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("❌ Aborted.")
            return
    
    # Write profile to file
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Get file size
        file_size = output_file.stat().st_size
        line_count = len(output_file.read_text().splitlines())
        
        print(f"✅ Profile created successfully!")
        print(f"   File: {output_file}")
        print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"   Lines: {line_count:,}")
        print()
        print(f"👤 UID: {data['uid']}")
        print(f"📍 Location: {data['profile']['location']} (ZIP: {data['profile']['zip_code']})")
        print()
        print(f"🏥 Care Recommendation: {data['mcip_contracts']['care_recommendation']['tier'].upper().replace('_', ' ')}")
        print(f"   Score: {data['mcip_contracts']['care_recommendation']['tier_score']} points")
        print(f"   Confidence: {data['mcip_contracts']['care_recommendation']['confidence']:.0%}")
        print(f"   Status: {data['mcip_contracts']['care_recommendation']['status']}")
        print()
        print(f"💰 Quick Estimate: ${data['cost_v2_quick_estimate']['adjusted_cost']:,}/month")
        print(f"   Location multiplier: {data['cost_v2_quick_estimate']['tier_multiplier']}x")
        print()
        print(f"🏁 Journey Status:")
        print(f"   Completed: {', '.join(data['mcip_contracts']['journey']['completed_products'])}")
        print(f"   Unlocked: {', '.join(data['mcip_contracts']['journey']['unlocked_products'])}")
        print()
        print("🚩 Key Flags:")
        for flag in data['mcip_contracts']['care_recommendation']['flags']:
            print(f"   ✓ {flag['label']} ({flag['id']})")
        print()
        print("=" * 60)
        print()
        print("📋 NEXT STEPS:")
        print()
        print("1. Add to login page (if not already done):")
        print("   Edit: pages/login.py")
        print("   Add to DEMO_USERS dict:")
        print(f'''
    "demo_andy": {{
        "name": "Andy Assisted GCP Complete",
        "email": "andy@demo.test",
        "uid": "{UID}",
        "description": "Assisted Living - GCP complete with VA A&A eligibility flag",
    }},
''')
        print()
        print("2. Delete any existing working copy:")
        print(f"   rm -f data/users/{UID}.json")
        print()
        print("3. Test login:")
        print("   - Restart Streamlit")
        print("   - Navigate to login page")
        print("   - Click 'Andy Assisted GCP Complete' button")
        print("   - Verify GCP tile shows: '✅ Assisted Living (73% confidence)'")
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error writing profile: {e}")
        return


if __name__ == "__main__":
    main()
