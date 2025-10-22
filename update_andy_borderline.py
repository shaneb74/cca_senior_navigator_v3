#!/usr/bin/env python3
"""
Update Andy Assisted GCP Complete Profile

Makes Andy a borderline Assisted Living case - close to Memory Care threshold
but with just enough independence to stay in Assisted Living tier.

Target Score: 23-24 points (upper end of Assisted Living 17-24 range)
Threshold: Memory Care starts at 25 points

Profile Updates:
- Score: 18 → 23 points (borderline, just below Memory Care)
- Location: San Francisco → Seattle (zip 98101)
- Added moderate cognitive decline (memory issues emerging)
- Increased ADL dependencies (3 → 3, but with bathing added)
- Increased IADL dependencies (3 → 4)
- Multiple falls (safety concern escalation)
- Still veteran with VA A&A eligibility

Borderline Factors:
+ Moderate memory concerns (pushing toward Memory Care)
+ Multiple falls (safety risk)
+ 3 ADLs + 4 IADLs (significant dependencies)
+ Lives alone, no family support
- BUT: Not severe cognitive decline (keeping in AL)
- BUT: No wandering/behavioral issues (keeping in AL)
- BUT: Can still participate in decisions (keeping in AL)

Usage:
    python3 update_andy_borderline.py

Prerequisites:
    - App must be stopped
    - Run from project root directory
"""

import json
import time
from datetime import datetime
from pathlib import Path

# Current timestamp
TIMESTAMP = time.time()

# UID remains the same
UID = "demo_andy_assisted_gcp_complete"

data = {
    "uid": UID,
    "created_at": TIMESTAMP,
    "last_updated": TIMESTAMP,
    "auth": {
        "user_id": UID,
        "is_authenticated": True,
        "name": "Andy Assisted GCP Complete",
        "email": "andy@demo.test"
    },
    "profile": {
        "name": "Andy",
        "age_range": "75-84",
        "location": "Seattle, WA",  # CHANGED from San Francisco
        "zip_code": "98101",  # CHANGED to Seattle downtown
        "relationship": "self",
        "qualifiers": {
            "is_veteran": True,
            "service_connected_disability": False,
            "has_spouse": False,
            "spouse_needs_care": False
        }
    },
    "cost_v2_qualifiers": {
        "is_veteran": True,
        "service_connected_disability": False,
        "has_spouse": False,
        "spouse_needs_care": False
    },
    "flags": {
        "is_veteran": True,
        "veteran_aanda_risk": True,
        "moderate_cognitive_decline": True,  # NEW - pushing toward Memory Care
        "enable_cost_planner_v2": True
    },

    # =========================================================================
    # GCP CARE RECOMMENDATION - BORDERLINE ASSISTED LIVING (23 points)
    # =========================================================================
    "gcp_care_recommendation": {
        "tier": "assisted_living",
        "tier_score": 23,  # INCREASED from 18 (borderline, just below Memory Care at 25)
        "confidence": 0.85,  # Higher confidence (more questions answered)
        "status": "complete",
        "progress": 100,
        "assessment": {
            "age_range": "75-84",
            "conditions": ["arthritis", "diabetes", "hypertension", "heart_disease"],  # Added condition
            "adl_count": 3,  # 3 ADLs (bathing, dressing, mobility)
            "iadl_count": 4,  # INCREASED: 4 IADLs (meal prep, shopping, finances, meds)
            "cognitive_decline": "moderate",  # CHANGED from false - moderate memory concerns
            "wandering_risk": False,  # Keeping false (would push to Memory Care)
            "behavioral_issues": False,  # Keeping false (would push to Memory Care)
            "safety_concerns": True,
            "living_situation": "alone",
            "primary_caregiver": "none",
            "caregiver_hours": 0,
            "professional_help": False
        },
        "flags": {
            "veteran_aanda_risk": True,
            "moderate_cognitive_decline": True,  # NEW - memory concerns
            "no_support": True,
            "safety_risk": True,
            "falls_multiple": True,  # CHANGED from falls_risk - multiple falls
            "medication_management": True,
            "nutrition_risk": True,
            "isolation_risk": True,
            "transportation_needs": True,
            "financial_stress": True,
            "moderate_dependence": True,  # Significant ADL/IADL needs
            "housing_instability": False
        },
        "rationale": "Borderline case: 23 points places Andy at the upper end of Assisted Living (17-24). He has moderate memory concerns and significant ADL/IADL dependencies, but lacks severe cognitive impairment or behavioral issues that would require Memory Care. Assisted living with enhanced services recommended.",
        "next_step": "Review costs for assisted living facilities with memory support programs."
    },

    # Mark GCP as published
    "gcp_v4_published": True,

    # =========================================================================
    # MCIP CONTRACTS
    # =========================================================================
    "mcip_contracts": {
        # Care recommendation - all 14 required fields
        "care_recommendation": {
            "tier": "assisted_living",
            "tier_score": 23.0,  # Borderline - just 2 points below Memory Care
            "tier_rankings": [
                ["memory_care_high_acuity", 70.0],
                ["memory_care", 25.0],  # Very close! Only 2 points away
                ["assisted_living", 23.0],  # Current recommendation
                ["in_home", 12.5],
                ["no_care_needed", 4.0]
            ],
            "confidence": 0.85,
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
                    "id": "moderate_cognitive_decline",
                    "label": "Moderate Memory Concerns",
                    "description": "Noticeable memory or thinking difficulties requiring support",
                    "tone": "warning",
                    "priority": 1,
                    "cta": {
                        "label": "Find Memory Support",
                        "route": "partners",
                        "filter": "memory_care"
                    }
                },
                {
                    "id": "falls_multiple",
                    "label": "Multiple Falls",
                    "description": "Multiple recent falls creating safety concerns",
                    "tone": "warning",
                    "priority": 2,
                    "cta": {
                        "label": "Learn About Fall Prevention",
                        "route": "learning",
                        "filter": "safety"
                    }
                },
                {
                    "id": "no_support",
                    "label": "No Family Support",
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
                    "id": "moderate_dependence",
                    "label": "Significant ADL/IADL Needs",
                    "description": "Needs regular assistance with 3 ADLs and 4 IADLs",
                    "tone": "info",
                    "priority": 3,
                    "cta": {
                        "label": "Learn About Personal Care",
                        "route": "learning",
                        "filter": "daily_living"
                    }
                }
            ],
            "rationale": [
                "Based on 23 points, we recommend: Assisted Living (borderline case)",
                "Borderline: Only 2 points below Memory Care threshold (25)",
                "Moderate memory concerns emerging - monitor for progression",
                "Significant ADL/IADL dependencies (3 ADLs + 4 IADLs)",
                "Multiple falls and safety risks",
                "Living alone with no family support",
                "Assisted living with enhanced memory support recommended",
                "VA benefits may help offset costs"
            ],
            "generated_at": datetime.now().isoformat(),
            "version": "4.0",
            "input_snapshot_id": f"andy_borderline_{int(TIMESTAMP)}",
            "rule_set": "gcp_v4_standard",
            "next_step": {
                "product": "cost_planner",
                "label": "Explore Costs",
                "reason": "Calculate costs for assisted living with memory support"
            },
            "last_updated": datetime.now().isoformat(),
            "needs_refresh": False
        },
        "journey": {
            "current_hub": "concierge",
            "completed_products": ["gcp"],
            "unlocked_products": ["cost_planner", "facility_finder"],
            "recommended_next": "cost_planner"
        },
        "waiting_room": {
            "status": "available",
            "appointment_scheduled": False
        }
    },

    # =========================================================================
    # COST PLANNER QUICK ESTIMATE (Seattle, not started)
    # =========================================================================
    "cost_v2_quick_estimate": {
        "estimate": {
            "monthly_base": 4500,
            "monthly_adjusted": 7200.0,  # Updated for Seattle + memory support
            "annual": 86400.0,
            "three_year": 259200.0,
            "five_year": 432000.0,
            "multiplier": 1.15,  # Seattle multiplier
            "region_name": "Seattle, WA (Downtown)",
            "care_tier": "assisted_living",
            "breakdown": {
                "base_cost": 4500,
                "regional_adjustment": 675.0,  # Seattle premium
                "memory_support_addon": 800.0,  # Enhanced memory program
                "moderate_adl_support_addon": 600.0,
                "medication_management_addon": 300.0,
                "falls_prevention_addon": 325.0
            }
        },
        "care_tier": "assisted_living",
        "zip_code": "98101"
    },

    # Cost Planner not started
    "cost_v2_step": "welcome",
    "cost_v2_guest_mode": False,
    "cost_v2_triage": {},
    "cost_v2_modules": {},

    # =========================================================================
    # TILES
    # =========================================================================
    "tiles": {
        "gcp_v4": {
            "status": "done",
            "progress": 100.0,
            "tier": "assisted_living",
            "confidence": 0.85,
            "tier_score": 23,
            "last_updated": TIMESTAMP
        },
        "cost_planner_v2": {
            "status": "not_started",
            "progress": 0,
            "last_updated": TIMESTAMP
        }
    },

    "progress": {},
    "preferences": {}
}


def main():
    """Update Andy's profile to borderline Assisted Living."""
    # Ensure demo directory exists
    demo_dir = Path("data/users/demo")
    demo_dir.mkdir(parents=True, exist_ok=True)

    # Output file path (in protected demo directory)
    output_file = demo_dir / f"{UID}.json"

    # Check if file exists
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

        print("\n" + "=" * 70)
        print("✅ Andy Borderline Profile Updated Successfully!")
        print("=" * 70)
        print(f"\n📄 File: {output_file}")
        print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"📝 Lines: {line_count:,}")
        print(f"\n👤 UID: {data['uid']}")
        print(f"📍 Location: {data['profile']['location']} (ZIP: {data['profile']['zip_code']})")
        print(f"👴 Age Range: {data['profile']['age_range']}")
        print("\n🏥 Care Recommendation: Assisted Living (BORDERLINE)")
        print(f"   Score: {data['gcp_care_recommendation']['tier_score']} points")
        print("   Memory Care Threshold: 25 points (only 2 points away!)")
        print("   Range: 17-24 (Assisted Living)")
        print(f"   Confidence: {data['gcp_care_recommendation']['confidence']:.0%}")
        print(f"   Status: {data['gcp_care_recommendation']['status']}")
        print("\n🎯 Borderline Factors:")
        print("   ✓ Moderate memory concerns (pushing toward Memory Care)")
        print("   ✓ 3 ADLs + 4 IADLs (significant dependencies)")
        print("   ✓ Multiple falls (safety concerns)")
        print("   ✓ Lives alone, no family support")
        print("   ✓ Veteran - VA A&A eligible")
        print("   ✗ No severe cognitive impairment (keeping in AL)")
        print("   ✗ No wandering/behavioral issues (keeping in AL)")
        print("\n💰 Quick Estimate:")
        print(f"   Seattle Assisted Living: ${data['cost_v2_quick_estimate']['estimate']['monthly_adjusted']:,.0f}/month")
        print("   Includes: Memory support program, fall prevention")
        print("\n📋 Next: Cost Planner (not started)")
        print("\n" + "=" * 70 + "\n")

    except PermissionError:
        print("❌ ERROR: Could not write file. Is the app running?")
        print("   Stop the app first: pkill -9 streamlit")
        return
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return


if __name__ == "__main__":
    main()
