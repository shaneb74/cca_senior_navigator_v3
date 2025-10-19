#!/usr/bin/env python3
"""
Create Veteran Vic Demo Profile

Demonstrates a veteran with:
- Mobility issues
- Mild cognitive impairment
- Borderline between assisted living and in-home care
- GCP complete, Cost Planner not started

Output: data/users/demo/demo_vic_veteran_borderline.json
"""

import json
from pathlib import Path
import time
from datetime import datetime

# Current timestamp for created_at/last_updated
TIMESTAMP = time.time()

# UID must be prefixed with "demo_" for protected demo loading
UID = "demo_vic_veteran_borderline"

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
        "name": "Veteran Vic",
        "email": "vic@demo.test"
    },
    
    # =========================================================================
    # PROFILE & QUALIFIERS
    # =========================================================================
    "profile": {
        "name": "Vic",
        "age_range": "75-84",
        "location": "Phoenix, AZ",
        "zip_code": "85001",
        "relationship": "self",
        "qualifiers": {
            "is_veteran": True,
            "service_connected_disability": True,
            "has_spouse": False,
            "spouse_needs_care": False
        }
    },
    
    # Duplicate qualifiers for Cost Planner compatibility
    "cost_v2_qualifiers": {
        "is_veteran": True,
        "service_connected_disability": True,
        "has_spouse": False,
        "spouse_needs_care": False
    },
    
    # =========================================================================
    # FEATURE FLAGS
    # =========================================================================
    "flags": {
        "is_veteran": True,
        "veteran_service_connected": True,
        "enable_cost_planner_v2": True
    },
    
    # =========================================================================
    # GCP CARE RECOMMENDATION
    # =========================================================================
    "gcp_care_recommendation": {
        "tier": "in_home",  # Borderline, but in-home slightly ahead
        "tier_score": 15.5,
        "confidence": 0.78,
        "status": "complete",
        "progress": 100,
        "assessment": {
            "age_range": "75-84",
            "conditions": ["mobility_issues", "mild_cognitive_impairment", "arthritis"],
            "adl_count": 1,
            "iadl_count": 2,
            "cognitive_decline": True,
            "wandering_risk": False,
            "safety_concerns": True,
            "living_situation": "alone",
            "primary_caregiver": "family_visits",
            "caregiver_hours": 10,
            "professional_help": False
        },
        "flags": {
            "veteran_benefits": True,
            "mobility_issues": True,
            "cognitive_decline_mild": True,
            "falls_risk": True,
            "medication_management": True,
            "transportation_needs": True,
            "part_time_support": True
        },
        "rationale": "Borderline case between in-home care and assisted living. Mobility and mild cognitive issues suggest need for support, but family involvement and part-time help may be sufficient for in-home care.",
        "next_step": "Explore both in-home care options and assisted living facilities to compare."
    },
    
    # Mark GCP as published
    "gcp_v4_published": True,
    
    # =========================================================================
    # MCIP CONTRACTS
    # =========================================================================
    "mcip_contracts": {
        # Care recommendation - all 14 required fields
        "care_recommendation": {
            "tier": "in_home",
            "tier_score": 15.5,
            "tier_rankings": [
                ["memory_care_high_acuity", 65.0],
                ["memory_care", 28.0],
                ["assisted_living", 15.0],  # Very close to in_home
                ["in_home", 15.5],           # Slightly ahead
                ["no_care_needed", 5.0]
            ],
            "confidence": 0.78,
            "status": "complete",
            "flags": [
                {
                    "id": "veteran_service_connected",
                    "label": "Service-Connected Veteran",
                    "description": "Eligible for enhanced VA benefits due to service-connected disability",
                    "tone": "success",
                    "priority": 1,
                    "cta": {
                        "label": "Check VA Benefits",
                        "route": "learning",
                        "filter": "va_benefits"
                    }
                },
                {
                    "id": "mobility_issues",
                    "label": "Mobility Challenges",
                    "description": "Limited mobility requiring assistance with movement",
                    "tone": "warning",
                    "priority": 2,
                    "cta": {
                        "label": "Explore Mobility Support",
                        "route": "learning",
                        "filter": "mobility_support"
                    }
                },
                {
                    "id": "cognitive_decline_mild",
                    "label": "Mild Cognitive Impairment",
                    "description": "Early cognitive changes requiring monitoring",
                    "tone": "info",
                    "priority": 2,
                    "cta": {
                        "label": "Learn About Memory Support",
                        "route": "learning",
                        "filter": "cognitive_support"
                    }
                },
                {
                    "id": "borderline_case",
                    "label": "Borderline Care Level",
                    "description": "Needs assessment suggests options in both in-home and assisted living",
                    "tone": "info",
                    "priority": 3,
                    "cta": {
                        "label": "Compare Care Options",
                        "route": "learning",
                        "filter": "care_options"
                    }
                }
            ],
            "rationale": [
                "Borderline case between in-home care and assisted living",
                "Mobility issues and mild cognitive impairment suggest need for support",
                "Family involvement (10 hrs/week) may enable in-home care",
                "Service-connected veteran status provides enhanced VA benefits",
                "Consider both options based on family capacity and budget"
            ],
            "generated_at": datetime.now().isoformat(),
            "version": "4.0",
            "input_snapshot_id": f"vic_gcp_{int(TIMESTAMP)}",
            "rule_set": "gcp_v4_standard",
            "next_step": {
                "product": "cost_planner",
                "label": "Compare Costs",
                "reason": "Evaluate cost difference between in-home care and assisted living"
            },
            "last_updated": datetime.now().isoformat(),
            "needs_refresh": False
        },
        
        # NO financial_profile - Vic hasn't done Cost Planner yet
        
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
        "estimate": {
            "monthly_base": 4200,
            "monthly_adjusted": 4620.0,
            "annual": 55440.0,
            "three_year": 166320.0,
            "five_year": 277200.0,
            "multiplier": 1.1,
            "region_name": "Phoenix, AZ",
            "care_tier": "in_home",
            "breakdown": {
                "base_cost": 4200,
                "regional_adjustment": 420.0,
                "caregiver_hours_addon": 0,
                "medication_management_addon": 0,
                "transportation_addon": 0
            }
        },
        "care_tier": "in_home",
        "zip_code": "85001"
    },
    
    # Cost Planner step - set to "welcome" (not started)
    "cost_v2_step": "welcome",
    
    # Guest mode and triage - include even if empty
    "cost_v2_guest_mode": False,
    "cost_v2_triage": {},
    
    # Modules - empty (Vic hasn't started Cost Planner)
    "cost_v2_modules": {},
    
    # =========================================================================
    # TILES
    # =========================================================================
    "tiles": {
        "gcp_v4": {
            "status": "done",
            "progress": 100.0,
            "tier": "in_home",
            "confidence": 0.78,
            "tier_score": 15.5,
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
    """Create the Veteran Vic demo profile file."""
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
        print(f"🎖️  Veteran: Service-connected disability")
        print()
        print(f"🏥 Care Recommendation: {data['mcip_contracts']['care_recommendation']['tier'].upper().replace('_', ' ')}")
        print(f"   Score: {data['mcip_contracts']['care_recommendation']['tier_score']} points")
        print(f"   Confidence: {data['mcip_contracts']['care_recommendation']['confidence']:.0%}")
        print(f"   Status: {data['mcip_contracts']['care_recommendation']['status']}")
        print(f"   Note: Borderline case - Assisted Living scored {15.0}, In-Home scored {15.5}")
        print()
        print(f"💰 Quick Estimate: ${data['cost_v2_quick_estimate']['estimate']['monthly_adjusted']:,}/month")
        print(f"   Location multiplier: {data['cost_v2_quick_estimate']['estimate']['multiplier']}x")
        print()
        print(f"🏁 Journey Status:")
        print(f"   Completed: {', '.join(data['mcip_contracts']['journey']['completed_products'])}")
        print(f"   Unlocked: {', '.join(data['mcip_contracts']['journey']['unlocked_products'])}")
        print()
        print(f"🚩 Key Flags:")
        for flag in data['mcip_contracts']['care_recommendation']['flags']:
            print(f"   ✓ {flag['label']} ({flag['id']})")
        print()
        print("=" * 60)
        print()
        print("📋 NEXT STEPS:")
        print()
        print("1. Add to login page:")
        print("   Edit: pages/login.py")
        print("   Add to DEMO_USERS dict:")
        print(f'''
    "demo_vic": {{
        "name": "Veteran Vic",
        "email": "vic@demo.test",
        "uid": "{UID}",
        "description": "Borderline In-Home/Assisted Living - Service-connected veteran",
    }},
''')
        print()
        print("2. Delete any existing working copy:")
        print(f"   rm -f data/users/{UID}.json")
        print()
        print("3. Test login:")
        print("   - Restart Streamlit")
        print("   - Navigate to login page")
        print("   - Click 'Veteran Vic' button")
        print("   - Verify GCP tile shows: '✅ In-Home Care (78% confidence)'")
        print("   - Note borderline scoring in care recommendation")
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error writing profile: {e}")
        return


if __name__ == "__main__":
    main()
