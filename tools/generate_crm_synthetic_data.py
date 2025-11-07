#!/usr/bin/env python3
"""
CRM Synthetic Data Generator - August 2025 Move-Ins

Generates realistic senior living customer records for CRM testing.
Creates 10 synthetic customers with complete Navigator journey data.
Safe for development use - no real customer PII.

Usage:
    python3 tools/generate_crm_synthetic_data.py

Output:
    - data/users/synthetic_aug2025_*.json (individual customer files)
    - data/crm/synthetic_august2025_summary.json (CRM summary data)
"""

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Ensure reproducible results
random.seed(20250805)  # August 5, 2025

class SyntheticCRMDataGenerator:
    """Generate realistic synthetic senior living customer data"""
    
    def __init__(self):
        self.base_date = datetime(2025, 8, 1)
        self.advisors = [
            "Sarah Johnson", "Mike Chen", "Lisa Rodriguez", "David Kim", 
            "Jennifer Williams", "Robert Davis", "Amanda Wilson", "James Martinez"
        ]
        
        # Realistic senior living communities in Pacific Northwest
        self.communities = [
            "Sunrise Manor Senior Living", "Evergreen Assisted Living", 
            "Pacific Crest Memory Care", "Harbor View Senior Community",
            "Cascade Gardens Assisted Living", "Olympic Heights Senior Care",
            "Puget Sound Senior Living", "Emerald Hills Care Community"
        ]
        
        # Realistic first/last name combinations for seniors
        self.first_names = [
            "Dorothy", "Robert", "Helen", "William", "Betty", "James",
            "Patricia", "Richard", "Joan", "Charles", "Nancy", "David"
        ]
        
        self.last_names = [
            "Johnson", "Williams", "Brown", "Davis", "Miller", "Wilson",
            "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White"
        ]
        
        # Care level distribution (realistic for move-ins)
        self.care_levels = {
            "assisted_living": 0.6,     # 60% assisted living
            "memory_care": 0.25,        # 25% memory care  
            "in_home": 0.15            # 15% chose in-home instead
        }
        
        # Cost ranges by care level (Pacific Northwest 2025)
        self.cost_ranges = {
            "assisted_living": (4200, 6800),
            "memory_care": (6000, 9500),
            "in_home": (2800, 5200)
        }

    def generate_synthetic_customers(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate specified number of synthetic customers"""
        customers = []
        
        for i in range(count):
            customer = self._generate_single_customer(i + 1)
            customers.append(customer)
            
        return customers
    
    def _generate_single_customer(self, customer_num: int) -> Dict[str, Any]:
        """Generate a single comprehensive customer record"""
        
        # Basic customer info
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        full_name = f"{first_name} {last_name}"
        user_id = f"synthetic_aug2025_{customer_num:03d}"
        
        # Care level selection (weighted random)
        care_level = self._weighted_choice(self.care_levels)
        
        # Timeline calculation
        move_in_date = self.base_date + timedelta(days=random.randint(1, 31))
        intake_date = move_in_date - timedelta(days=random.randint(45, 120))
        gcp_complete_date = intake_date + timedelta(days=random.randint(7, 21))
        cost_complete_date = gcp_complete_date + timedelta(days=random.randint(3, 14))
        
        # Journey completion status
        days_since_intake = (datetime.now() - intake_date).days
        has_gcp = days_since_intake >= 14  # Most complete GCP within 2 weeks
        has_cost = has_gcp and days_since_intake >= 21  # Cost planning after GCP
        
        # Generate realistic assessment data
        assessment_data = self._generate_assessment_data(care_level, first_name)
        cost_data = self._generate_cost_data(care_level) if has_cost else None
        
        # Community and advisor assignment
        community = random.choice(self.communities)
        advisor = random.choice(self.advisors)
        
        # Calculate customer metrics
        last_activity_days = self._calculate_activity_days(move_in_date)
        
        # Build comprehensive customer record
        customer = {
            "user_id": user_id,
            "person_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{first_name.lower()}.{last_name.lower()}@synthetic.test",
            "phone": self._generate_phone(),
            
            # Journey status
            "has_gcp_assessment": has_gcp,
            "has_cost_plan": has_cost,
            "journey_stage": self._determine_journey_stage(has_gcp, has_cost, move_in_date),
            "last_activity": intake_date.strftime("%Y-%m-%d"),
            "last_activity_days": last_activity_days,
            
            # Care information
            "care_recommendation": care_level.replace('_', ' ').title(),
            "care_level": care_level,
            "assessment_summary": assessment_data["summary"],
            "assessment_confidence": assessment_data["confidence"],
            
            # Cost information
            "cost_summary": cost_data["summary"] if cost_data else "Not started",
            "monthly_cost_estimate": cost_data["monthly_cost"] if cost_data else None,
            
            # Move-in details
            "move_in_date": move_in_date.strftime("%Y-%m-%d"),
            "intake_date": intake_date.strftime("%Y-%m-%d"),
            "community_name": community,
            "assigned_advisor": advisor,
            
            # Demographics
            "age_range": random.choice(["65-74", "75-84", "85-94"]),
            "location": random.choice(["Seattle, WA", "Portland, OR", "Tacoma, WA", "Spokane, WA"]),
            "zip_code": random.choice(["98101", "97201", "98402", "99201"]),
            
            # Status tracking
            "status": "moved_in" if move_in_date <= datetime.now() else "pending_move_in",
            "created_at": time.time(),
            "data_source": "synthetic_generator_aug2025"
        }
        
        return customer
    
    def _weighted_choice(self, choices: Dict[str, float]) -> str:
        """Select item based on weighted probabilities"""
        items = list(choices.keys())
        weights = list(choices.values())
        return random.choices(items, weights=weights)[0]
    
    def _generate_assessment_data(self, care_level: str, first_name: str) -> Dict[str, Any]:
        """Generate realistic GCP assessment data"""
        
        # Care level specific patterns
        assessment_patterns = {
            "assisted_living": {
                "confidence": random.randint(75, 90),
                "summary": f"{first_name} shows moderate care needs with assistance required for daily activities. Independent with supervision."
            },
            "memory_care": {
                "confidence": random.randint(85, 95),
                "summary": f"{first_name} has significant memory-related challenges requiring specialized care and secure environment."
            },
            "in_home": {
                "confidence": random.randint(70, 85),
                "summary": f"{first_name} demonstrates ability to remain at home with appropriate support services and family assistance."
            }
        }
        
        return assessment_patterns.get(care_level, assessment_patterns["assisted_living"])
    
    def _generate_cost_data(self, care_level: str) -> Dict[str, Any]:
        """Generate realistic cost planning data"""
        min_cost, max_cost = self.cost_ranges[care_level]
        monthly_cost = random.randint(min_cost, max_cost)
        
        return {
            "monthly_cost": monthly_cost,
            "summary": f"${monthly_cost:,}/month estimated cost including care services and accommodation."
        }
    
    def _determine_journey_stage(self, has_gcp: bool, has_cost: bool, move_in_date: datetime) -> str:
        """Determine customer's current journey stage"""
        if move_in_date <= datetime.now():
            return "Moved In - Success!"
        elif has_gcp and has_cost:
            return "Ready for Recommendations"
        elif has_gcp:
            return "Cost Planning In Progress"
        else:
            return "Care Assessment In Progress"
    
    def _calculate_activity_days(self, move_in_date: datetime) -> int:
        """Calculate realistic activity days"""
        if move_in_date <= datetime.now():
            # Recently moved in customers have recent activity
            return random.randint(1, 5)
        else:
            # Future move-ins have more varied activity
            return random.randint(2, 14)
    
    def _generate_phone(self) -> str:
        """Generate realistic phone number"""
        area_codes = ["206", "253", "425", "360"]  # WA area codes
        area = random.choice(area_codes)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"({area}) {exchange}-{number}"
    
    def _generate_care_flags(self, care_level: str) -> List[Dict[str, Any]]:
        """Generate realistic care flags based on care level"""
        base_flags = [
            {"id": "has_partner", "label": "Has partner", "value": random.choice([True, False])},
            {"id": "moderate_dependence", "label": "Moderate dependence", "value": True}
        ]
        
        if care_level == "memory_care":
            base_flags.extend([
                {"id": "severe_cognitive_risk", "label": "Severe cognitive risk", "value": True},
                {"id": "memory_support", "label": "Memory support needed", "value": True}
            ])
        elif care_level == "assisted_living":
            base_flags.extend([
                {"id": "moderate_mobility", "label": "Moderate mobility issues", "value": True},
                {"id": "chronic_present", "label": "Chronic conditions present", "value": True}
            ])
        
        return base_flags
    
    def _get_completed_products(self, has_gcp: bool, has_cost: bool) -> List[str]:
        """Get list of completed products based on journey progress"""
        completed = []
        if has_gcp:
            completed.append("gcp")
        if has_cost:
            completed.append("cost_planner")
        return completed

def main():
    """Generate synthetic CRM data and save to files"""
    
    print("🔄 Generating synthetic CRM customer data...")
    
    generator = SyntheticCRMDataGenerator()
    customers = generator.generate_synthetic_customers(count=10)
    
    # Create output directories
    data_dir = Path("data")
    users_dir = data_dir / "users"
    crm_dir = data_dir / "crm"
    
    users_dir.mkdir(exist_ok=True)
    crm_dir.mkdir(exist_ok=True)
    
    # Save individual customer files (for Navigator integration)
    individual_files = []
    for customer in customers:
        user_id = customer["user_id"]
        filename = f"{user_id}.json"
        filepath = users_dir / filename
        
        # Create Navigator-compatible structure
        navigator_data = {
            "uid": user_id,
            "created_at": customer["created_at"],
            "last_updated": customer["created_at"],
            "auth": {
                "user_id": user_id,
                "is_authenticated": True,
                "name": customer["person_name"],
                "email": customer["email"]
            },
            "profile": {
                "name": customer["first_name"],
                "age_range": customer["age_range"],
                "location": customer["location"],
                "zip_code": customer["zip_code"],
                "phone": customer["phone"]
            },
            # Add MCIP structure for proper NavigatorDataReader integration
            "mcip_contracts": {
                "care_recommendation": {
                    "tier": customer["care_level"],
                    "tier_score": customer["assessment_confidence"] / 10.0,  # Convert to 0-10 scale
                    "tier_rankings": [customer["care_level"]],
                    "confidence": customer["assessment_confidence"] / 100.0,  # Convert to 0-1 scale
                    "flags": generator._generate_care_flags(customer["care_level"]),
                    "rationale": [customer["assessment_summary"]],
                    "generated_at": customer["created_at"],
                    "status": "complete" if customer["has_gcp_assessment"] else "new",
                    "last_updated": customer["created_at"],
                    "needs_refresh": False
                },
                "financial_profile": {
                    "monthly_cost": customer["monthly_cost_estimate"] if customer["has_cost_plan"] else None,
                    "cost_summary": customer["cost_summary"] if customer["has_cost_plan"] else None,
                    "status": "complete" if customer["has_cost_plan"] else "new"
                } if customer["has_cost_plan"] else None,
                "cost_planner": {
                    "status": "complete" if customer["has_cost_plan"] else "new",
                    "monthly_estimate": customer["monthly_cost_estimate"] if customer["has_cost_plan"] else None
                } if customer["has_cost_plan"] else None,
                "journey": {
                    "current_hub": "hub",
                    "completed_products": generator._get_completed_products(customer["has_gcp_assessment"], customer["has_cost_plan"]),
                    "unlocked_products": ["gcp", "cost_planner", "pfma"]
                }
            },
            # Keep synthetic metadata for identification
            "synthetic_metadata": {
                "data_source": "synthetic_generator_aug2025",
                "care_level": customer["care_level"],
                "move_in_date": customer["move_in_date"],
                "advisor": customer["assigned_advisor"],
                "community": customer["community_name"]
            },
            # Add Navigator data fields
            "person_name": customer["person_name"],
            "relationship_type": "self",
            "last_activity": customer["last_activity"],
            # Add top-level fields that NavigatorDataReader expects
            "estimated_monthly_cost": customer["monthly_cost_estimate"] if customer["has_cost_plan"] else None,
            "gcp_care_recommendation": customer["care_level"] if customer["has_gcp_assessment"] else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(navigator_data, f, indent=2)
        
        individual_files.append(str(filepath))
    
    # Save CRM summary data
    crm_summary = {
        "generated_at": datetime.now().isoformat(),
        "record_count": len(customers),
        "data_source": "synthetic_generator_aug2025",
        "description": "Synthetic August 2025 move-in customers for CRM testing",
        "customers": customers
    }
    
    crm_summary_path = crm_dir / "synthetic_august2025_summary.json"
    with open(crm_summary_path, 'w') as f:
        json.dump(crm_summary, f, indent=2)
    
    # Generate summary report
    print("\n" + "="*60)
    print("✅ SYNTHETIC CRM DATA GENERATION COMPLETE")
    print("="*60)
    print(f"📊 Generated: {len(customers)} synthetic customers")
    print(f"📅 Move-in period: August 2025")
    print(f"📁 Individual files: data/users/ ({len(individual_files)} files)")
    print(f"📁 CRM summary: {crm_summary_path}")
    
    print("\n📋 CUSTOMER BREAKDOWN:")
    care_level_counts = {}
    advisor_counts = {}
    journey_stage_counts = {}
    
    for customer in customers:
        care_level = customer["care_level"]
        advisor = customer["assigned_advisor"]
        stage = customer["journey_stage"]
        
        care_level_counts[care_level] = care_level_counts.get(care_level, 0) + 1
        advisor_counts[advisor] = advisor_counts.get(advisor, 0) + 1
        journey_stage_counts[stage] = journey_stage_counts.get(stage, 0) + 1
    
    print(f"   Care Levels: {dict(care_level_counts)}")
    print(f"   Advisors: {dict(advisor_counts)}")
    print(f"   Journey Stages: {dict(journey_stage_counts)}")
    
    print(f"\n💰 COST ESTIMATES:")
    costs = [c["monthly_cost_estimate"] for c in customers if c["monthly_cost_estimate"]]
    if costs:
        print(f"   Range: ${min(costs):,} - ${max(costs):,}/month")
        print(f"   Average: ${sum(costs)//len(costs):,}/month")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Restart CRM app: streamlit run crm_app.py --server.port=8502")
    print(f"   2. Navigate to Customers page")
    print(f"   3. Verify all 10 synthetic customers display correctly")
    print(f"   4. Test Customer 360° views with realistic data")
    print(f"   5. Check AI Next Steps recommendations")
    
    print(f"\n🔒 SECURITY NOTE:")
    print(f"   ✅ All data is synthetic - safe for development use")
    print(f"   ✅ No real customer PII included")
    print(f"   ✅ Generated patterns match production data structure")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()