#!/usr/bin/env python3
"""
Enrich Synthetic Customers with Realistic Demo Data

Adds production-like attributes to all synthetic customers including:
- Demographics (age, gender, location)
- Medical conditions and care needs
- Community preferences and requirements
- Financial information
- Assessment scores and recommendations
- Community-matching flags for demo purposes

All data is synthetic and safe for demo use.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Realistic names matched to existing records
CUSTOMER_PROFILES = {
    "Richard Jackson": {"gender": "Male", "age": 78},
    "Joan Williams": {"gender": "Female", "age": 82},
    "Nancy Wilson": {"gender": "Female", "age": 80},
    "Dorothy Thomas": {"gender": "Female", "age": 71},
    "Robert Williams": {"gender": "Male", "age": 81},
    "Robert Thomas": {"gender": "Male", "age": 83},
    "James Moore": {"gender": "Male", "age": 88},
    "Robert Johnson": {"gender": "Male", "age": 69},
    "Joan Moore": {"gender": "Female", "age": 89},
    "Robert Wilson": {"gender": "Male", "age": 79},
    "Patricia Anderson": {"gender": "Female", "age": 76},
    "Michael Taylor": {"gender": "Male", "age": 73},
    "Susan Martinez": {"gender": "Female", "age": 77},
    "David Garcia": {"gender": "Male", "age": 74},
    "Barbara Rodriguez": {"gender": "Female", "age": 81},
    "Christopher Miller": {"gender": "Male", "age": 72},
    "Linda Davis": {"gender": "Female", "age": 85},
    "Matthew Lopez": {"gender": "Male", "age": 70},
    "Elizabeth Gonzalez": {"gender": "Female", "age": 79},
    "Daniel Hernandez": {"gender": "Male", "age": 82},
    "Margaret Smith": {"gender": "Female", "age": 86},
    "Joseph Brown": {"gender": "Male", "age": 75},
    "Jennifer Lee": {"gender": "Female", "age": 68},
}

# Medical conditions for realistic scenarios
MEDICAL_CONDITIONS = [
    "Diabetes Type 2", "Hypertension", "Arthritis", "COPD",
    "Heart Disease", "Osteoporosis", "Mild Cognitive Impairment",
    "Dementia - Early Stage", "Dementia - Moderate Stage",
    "Parkinson's Disease", "Chronic Pain", "Vision Impairment",
    "Hearing Loss", "Depression", "Anxiety", "Stroke History"
]

# ADL (Activities of Daily Living) needs
ADL_CATEGORIES = {
    "bathing": ["Independent", "Needs Reminders", "Needs Assistance", "Fully Dependent"],
    "dressing": ["Independent", "Needs Reminders", "Needs Assistance", "Fully Dependent"],
    "toileting": ["Independent", "Needs Reminders", "Needs Assistance", "Fully Dependent"],
    "transferring": ["Independent", "Needs Assistance", "Requires Equipment", "Two Person Transfer"],
    "eating": ["Independent", "Needs Setup", "Needs Feeding Assistance", "Fully Dependent"],
    "medication": ["Independent", "Needs Reminders", "Needs Administration", "Injectable Meds"]
}

# Community preferences
AMENITY_PREFERENCES = [
    "Pet Friendly", "Private Room", "Shared Room OK", "Full Kitchen",
    "Pool Access", "Garden/Outdoor Space", "Fitness Center",
    "Chapel/Spiritual Space", "Beauty Salon", "Library",
    "Movie Theater", "Restaurant-Style Dining", "Transportation Services"
]

# Medical service requirements
MEDICAL_SERVICES = [
    "Insulin Management", "Wound Care", "Physical Therapy",
    "Occupational Therapy", "Speech Therapy", "Memory Care Program",
    "Hospice Care", "24-Hour Nursing", "On-Site Doctor",
    "Medication Management", "Incontinence Care"
]

# Mobility equipment
MOBILITY_EQUIPMENT = [
    "None", "Cane", "Walker", "Wheelchair - Manual",
    "Wheelchair - Power", "Hoyer Lift Required", "Transfer Equipment"
]

def generate_adl_assessment():
    """Generate realistic ADL assessment"""
    assessment = {}
    for category, options in ADL_CATEGORIES.items():
        # Weight towards higher independence for AL, lower for memory care
        if random.random() < 0.6:  # 60% independent or minimal help
            assessment[category] = random.choice(options[:2])
        else:
            assessment[category] = random.choice(options[2:])
    return assessment

def generate_medical_profile(age, care_level):
    """Generate realistic medical conditions and needs"""
    # Older age = more conditions
    num_conditions = min(random.randint(1, 4) + (age - 70) // 10, 6)
    conditions = random.sample(MEDICAL_CONDITIONS, num_conditions)
    
    # Memory care customers have memory-related conditions
    if care_level == "memory_care":
        if "Dementia - Early Stage" not in conditions and "Dementia - Moderate Stage" not in conditions:
            conditions.append(random.choice(["Dementia - Early Stage", "Dementia - Moderate Stage"]))
    
    return {
        "conditions": conditions,
        "medications": random.randint(3, 8),
        "allergies": random.choice([None, "Penicillin", "Sulfa Drugs", "Latex", "None Known"]),
        "diet_restrictions": random.choice([None, "Diabetic", "Low Sodium", "Pureed", "Thickened Liquids"])
    }

def generate_community_matching_flags(care_level):
    """Generate community-matching requirements for demo"""
    flags = {
        # Critical needs (these drive matching)
        "requires_memory_care": care_level == "memory_care",
        "requires_insulin_management": random.random() < 0.3,
        "requires_wound_care": random.random() < 0.2,
        "requires_physical_therapy": random.random() < 0.4,
        "requires_hoyer_lift": random.random() < 0.15,
        "requires_two_person_transfer": random.random() < 0.2,
        "requires_bariatric_care": random.random() < 0.1,
        
        # Preferences (nice to have)
        "prefers_pets_allowed": random.random() < 0.35,
        "prefers_private_room": random.random() < 0.7,
        "prefers_full_kitchen": random.random() < 0.25,
        "prefers_outdoor_space": random.random() < 0.6,
        "prefers_pool": random.random() < 0.2,
        
        # Language needs
        "language_preference": random.choice([None, "Spanish", "Chinese", "Russian", "Vietnamese"]) if random.random() < 0.15 else None,
        
        # Religious/cultural
        "religious_preference": random.choice([None, "Christian Chapel", "Jewish Services", "Non-denominational"]) if random.random() < 0.3 else None,
        
        # Budget constraints
        "budget_max": random.choice([4500, 5000, 6000, 7000, 8000, 9000, 10000]),
        "budget_flexible": random.random() < 0.6,
    }
    
    # Add specific medical services needed
    flags["medical_services_needed"] = []
    if flags["requires_insulin_management"]:
        flags["medical_services_needed"].append("Insulin Management")
    if flags["requires_wound_care"]:
        flags["medical_services_needed"].append("Wound Care")
    if flags["requires_physical_therapy"]:
        flags["medical_services_needed"].append("Physical Therapy")
    
    return flags

def generate_family_context():
    """Generate family involvement details"""
    relationship_types = [
        "Adult Daughter", "Adult Son", "Spouse", "Niece/Nephew",
        "Grandchild", "Friend/Neighbor", "Professional Guardian", "Self"
    ]
    
    involvement_levels = [
        "Very Involved - Visits Weekly",
        "Moderately Involved - Visits Monthly",
        "Limited Involvement - Out of State",
        "Minimal Contact",
        "Primary Decision Maker - Local"
    ]
    
    return {
        "primary_contact_relationship": random.choice(relationship_types),
        "involvement_level": random.choice(involvement_levels),
        "decision_maker": random.choice([True, False]),
        "lives_nearby": random.random() < 0.6,
        "financial_poa": random.random() < 0.4
    }

def enrich_customer(customer):
    """Add comprehensive realistic demo data to a customer"""
    
    name = customer.get('person_name', 'Unknown')
    profile = CUSTOMER_PROFILES.get(name, {"gender": "Unknown", "age": 75})
    
    age = profile["age"]
    gender = profile["gender"]
    care_level = customer.get('care_level', 'assisted_living')
    
    # Generate ADL assessment
    adl_assessment = generate_adl_assessment()
    
    # Generate medical profile
    medical_profile = generate_medical_profile(age, care_level)
    
    # Generate community matching flags
    matching_flags = generate_community_matching_flags(care_level)
    
    # Generate family context
    family_context = generate_family_context()
    
    # Mobility assessment
    mobility = {
        "equipment": random.choice(MOBILITY_EQUIPMENT),
        "fall_risk": random.choice(["Low", "Moderate", "High"]),
        "requires_assistance": random.random() < 0.5
    }
    
    # Social/behavioral
    social_profile = {
        "sociability": random.choice(["Very Social", "Moderately Social", "Prefers Quiet", "Withdrawn"]),
        "activity_preference": random.choice(["Group Activities", "One-on-One", "Independent", "Varies"]),
        "behavioral_concerns": random.choice([None, "Wandering Risk", "Agitation", "Sundowning", "None"]),
    }
    
    # Assessment scores (realistic ranges)
    assessment_scores = {
        "mmse_score": random.randint(15, 30) if care_level != "memory_care" else random.randint(10, 22),
        "functional_score": random.randint(50, 95),
        "pain_level": random.randint(0, 7),
        "depression_screen": random.choice(["Negative", "Mild", "Moderate", "Not Assessed"])
    }
    
    # Move-in timeline
    urgency = random.choice(["Immediate (< 2 weeks)", "Soon (2-4 weeks)", "Planning (1-3 months)", "Exploring (3+ months)"])
    
    # Enriched data structure
    enrichment = {
        # Demographics
        "age": age,
        "gender": gender,
        "date_of_birth": (datetime.now() - timedelta(days=age*365.25)).strftime('%Y-%m-%d'),
        
        # Medical
        "medical_conditions": medical_profile["conditions"],
        "medication_count": medical_profile["medications"],
        "allergies": medical_profile["allergies"],
        "diet_restrictions": medical_profile["diet_restrictions"],
        
        # Functional Assessment
        "adl_assessment": adl_assessment,
        "mobility": mobility,
        "assessment_scores": assessment_scores,
        
        # Social/Behavioral
        "social_profile": social_profile,
        
        # Family
        "family_context": family_context,
        
        # Community Matching (for demo)
        "community_matching_flags": matching_flags,
        
        # Move-in timeline
        "move_in_urgency": urgency,
        "preferred_move_in_date": (datetime.now() + timedelta(days=random.randint(14, 90))).strftime('%Y-%m-%d'),
        
        # Notes
        "intake_notes": f"Initial assessment completed. {name} is a {age}-year-old {gender.lower()} interested in {customer.get('care_recommendation', 'senior living')}. Family is {family_context['involvement_level'].lower()}.",
        
        # Last updated
        "enriched_at": datetime.now().isoformat(),
    }
    
    # Merge into customer record
    customer.update(enrichment)
    
    return customer

def main():
    """Main enrichment process"""
    print("=" * 80)
    print("ENRICHING SYNTHETIC CUSTOMERS WITH REALISTIC DEMO DATA")
    print("=" * 80)
    print()
    
    # Load existing customers
    data_file = Path("data/crm/synthetic_august2025_summary.json")
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    customers = data['customers']
    print(f"Found {len(customers)} customers to enrich\n")
    
    # Enrich each customer
    enriched_count = 0
    for customer in customers:
        name = customer.get('person_name', 'Unknown')
        print(f"Enriching: {name}")
        
        try:
            enrich_customer(customer)
            enriched_count += 1
            print(f"  ✅ Added demographics, medical profile, ADL assessment, matching flags")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Update metadata
    data['enriched_at'] = datetime.now().isoformat()
    data['enrichment_version'] = "v1.0"
    
    # Save back
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 80)
    print(f"✅ Successfully enriched {enriched_count}/{len(customers)} customers")
    print("=" * 80)
    print()
    
    # Show sample
    print("Sample Enriched Customer:")
    print("-" * 80)
    sample = customers[0]
    print(f"Name: {sample['person_name']}")
    print(f"Age: {sample['age']} ({sample['gender']})")
    print(f"Conditions: {', '.join(sample['medical_conditions'][:3])}")
    print(f"Care Level: {sample['care_recommendation']}")
    print(f"Matching Flags: {sum(1 for v in sample['community_matching_flags'].values() if v == True)} requirements")
    print(f"Budget Max: ${sample['community_matching_flags']['budget_max']:,}/month")
    print()
    
    print("Community Matching Flags Summary:")
    print("-" * 80)
    flag_counts = {}
    for customer in customers:
        flags = customer.get('community_matching_flags', {})
        for key, value in flags.items():
            if value is True or (value and value != "None"):
                flag_counts[key] = flag_counts.get(key, 0) + 1
    
    for flag, count in sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {flag:40} {count:2} customers")
    
    print()
    print("🎉 All customers now have production-like demo data!")
    print("   - Ready for Customer 360 viewing")
    print("   - Ready for community matching demos")
    print("   - All data is synthetic and safe for demo use")

if __name__ == "__main__":
    main()
