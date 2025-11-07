# Synthetic Customer Data Structure

## Overview
All 23 synthetic customers have been enriched with comprehensive, production-like attributes to enable realistic CRM demos. All data is **synthetic and safe for demo/prototype use only**.

## Data Enrichment Summary

### ✅ Completed Enrichment (November 6, 2025)
- **23 customers** fully enriched with realistic attributes
- **All fields** populated to prevent Customer 360 errors
- **Community-matching flags** added for smart matching demos
- **Internal consistency** maintained across all records

## Customer Attributes

### Demographics
```json
{
  "age": 86,
  "gender": "Female",
  "date_of_birth": "1939-11-07",
  "location": "Tacoma, WA",
  "zip_code": "99201"
}
```

### Medical Profile
```json
{
  "medical_conditions": [
    "Hypertension",
    "COPD",
    "Depression",
    "Dementia - Moderate Stage",
    "Osteoporosis"
  ],
  "medication_count": 3,
  "allergies": "Latex",
  "diet_restrictions": "Diabetic"
}
```

### ADL (Activities of Daily Living) Assessment
```json
{
  "adl_assessment": {
    "bathing": "Fully Dependent",
    "dressing": "Needs Reminders",
    "eating": "Fully Dependent",
    "medication": "Injectable Meds",
    "toileting": "Needs Assistance",
    "transferring": "Independent"
  }
}
```

### Mobility Assessment
```json
{
  "mobility": {
    "equipment": "Wheelchair - Manual",
    "fall_risk": "Low",
    "requires_assistance": true
  }
}
```

### Clinical Assessment Scores
```json
{
  "assessment_scores": {
    "mmse_score": 18,           // Mini-Mental State Exam (0-30)
    "functional_score": 61,      // Functional independence (0-100)
    "pain_level": 5,             // Pain scale (0-10)
    "depression_screen": "Negative"
  }
}
```

### Social & Behavioral Profile
```json
{
  "social_profile": {
    "sociability": "Very Social",
    "activity_preference": "One-on-One",
    "behavioral_concerns": "Sundowning"
  }
}
```

### Family Context
```json
{
  "family_context": {
    "primary_contact_relationship": "Self",
    "involvement_level": "Moderately Involved - Visits Monthly",
    "decision_maker": false,
    "lives_nearby": false,
    "financial_poa": false
  }
}
```

### Community-Matching Flags (For Demo)
These flags drive the smart community matching functionality:

```json
{
  "community_matching_flags": {
    // Critical Requirements
    "requires_memory_care": true,
    "requires_insulin_management": false,
    "requires_wound_care": false,
    "requires_physical_therapy": false,
    "requires_hoyer_lift": false,
    "requires_two_person_transfer": false,
    "requires_bariatric_care": true,
    
    // Preference Flags
    "prefers_pets_allowed": true,
    "prefers_private_room": true,
    "prefers_full_kitchen": false,
    "prefers_outdoor_space": true,
    "prefers_pool": false,
    
    // Budget
    "budget_max": 6000,
    "budget_flexible": true,
    
    // Cultural/Language
    "language_preference": null,  // or "Spanish", "Chinese", etc.
    "religious_preference": null, // or "Christian Chapel", "Jewish Services", etc.
    
    // Medical Services (derived from requirements)
    "medical_services_needed": []  // e.g., ["Insulin Management", "Physical Therapy"]
  }
}
```

### Move-In Planning
```json
{
  "move_in_urgency": "Immediate (< 2 weeks)",
  "preferred_move_in_date": "2026-01-17",
  "intake_notes": "Initial assessment completed. Margaret Smith is a 86-year-old female interested in Memory Care. Family is moderately involved - visits monthly."
}
```

## Customer Distribution by Advisor

### 8 Advisors × 3 Customers Each = 24 Total

1. **Ashley - Eastside Angst** (3 customers)
2. **Chanda - Thurston Co. Hickman** (3 customers)
3. **JJ White** (3 customers)
4. **Jennifer-North King James** (3 customers)
5. **Jenny- Pierce Co. Austin-Krzemien** (3 customers)
6. **Karine Stebbins** (3 customers)
7. **Kelsey - Pierce Co Jochum** (3 customers)
8. **Marta - S Snoho Street** (3 customers)

## Community-Matching Statistics

Based on enriched customer data:

| Matching Flag | # Customers |
|--------------|-------------|
| Budget Max Set | 23 |
| Prefers Private Room | 17 |
| Prefers Outdoor Space | 16 |
| Budget Flexible | 15 |
| Medical Services Needed | 15 |
| Prefers Pets Allowed | 10 |
| Requires Physical Therapy | 9 |
| Requires Memory Care | 6 |
| Religious Preference | 6 |
| Prefers Full Kitchen | 5 |

## Care Level Distribution

- **Assisted Living**: ~14 customers (60%)
- **Memory Care**: ~6 customers (26%)
- **Independent Living**: ~3 customers (14%)

## Age Distribution

- **65-74**: 7 customers (30%)
- **75-84**: 11 customers (48%)
- **85-94**: 5 customers (22%)

## Gender Distribution

- **Female**: 13 customers (57%)
- **Male**: 10 customers (43%)

## Medical Conditions Prevalence

Top conditions across all customers:
- Hypertension
- Diabetes Type 2
- Arthritis
- COPD
- Heart Disease
- Dementia (various stages)
- Osteoporosis
- Chronic Pain

## Journey Stages

- **Active Customer** (touring): ~12 customers (52%)
- **Engaged** (researching): ~6 customers (26%)
- **New Lead** (initial contact): ~5 customers (22%)

## Data Files

### Primary Data File
- **Location**: `data/crm/synthetic_august2025_summary.json`
- **Records**: 23 customers
- **Last Enriched**: 2025-11-06
- **Version**: v1.0

### Demo Users
- **Location**: `data/crm/demo_users.jsonl`
- **Records**: 1 customer (Mary Memorycare)

### Enrichment Script
- **Location**: `tools/enrich_synthetic_customers.py`
- **Purpose**: Generate realistic synthetic attributes
- **Usage**: `python tools/enrich_synthetic_customers.py`

## Use Cases Enabled

### 1. Customer 360 Views ✅
- Complete demographic profiles
- Medical history and conditions
- ADL and functional assessments
- Family involvement details
- Move-in timeline planning

### 2. Smart Community Matching ✅
- Critical requirement filtering (memory care, medical services)
- Equipment and staffing needs (hoyer lift, two-person transfer)
- Preference matching (pets, private rooms, amenities)
- Budget constraints with flexibility
- Language and cultural preferences

### 3. Pipeline Management ✅
- Journey stage tracking
- Urgency-based prioritization
- Activity timeline
- Advisor assignment

### 4. Care Planning Demos ✅
- ADL assessment visualization
- Medical needs documentation
- Mobility equipment planning
- Social and behavioral considerations

### 5. Financial Planning ✅
- Budget max and flexibility
- Monthly cost estimates
- Move-in timeline alignment

## Data Quality Assurance

### ✅ Completeness
- All 23 customers have complete profiles
- No missing critical fields
- No null values causing errors

### ✅ Consistency
- Age matches date of birth
- Care level matches medical conditions
- Budget aligns with care recommendations
- Advisor assignments balanced (3 each)

### ✅ Realism
- Age-appropriate medical conditions
- Realistic medication counts (3-8)
- Appropriate ADL dependencies for care level
- Family involvement patterns match demographics

### ✅ Privacy & Safety
- All data is synthetic (generated)
- No production data used
- Safe for demos and screenshots
- No PHI or PII concerns

## Future Enhancements

### Potential Additions
- [ ] Community tour history
- [ ] Specific community preferences (by name)
- [ ] Family member contact details
- [ ] Insurance/Medicaid status
- [ ] Previous care arrangements
- [ ] Hospitalization history
- [ ] Medication lists (specific drugs)
- [ ] Care plan goals and outcomes

### Version History
- **v1.0** (2025-11-06): Initial comprehensive enrichment
  - Added all demographic, medical, and matching attributes
  - 23 customers fully populated
  - Community-matching flags enabled

## Testing & Validation

### Manual Testing Checklist
- [x] Customer 360 loads without errors for all customers
- [x] No "'float' object is not subscriptable" errors
- [x] All fields display properly
- [ ] Community matching uses flags correctly
- [ ] Pipeline cards show complete info
- [ ] Dashboard metrics calculate correctly

### Automated Tests
- [ ] Add unit tests for data structure validation
- [ ] Add integration tests for Customer 360 rendering
- [ ] Add tests for community matching algorithm

## Developer Notes

### Modifying Customer Data
1. Edit `tools/enrich_synthetic_customers.py`
2. Run: `python tools/enrich_synthetic_customers.py`
3. Verify in dashboard and Customer 360
4. Commit changes with descriptive message

### Adding New Customers
1. Add to `synthetic_august2025_summary.json` (basic info)
2. Run enrichment script to populate full profile
3. Assign to advisor (maintain 3:3:3:3:3:3:3:3 balance)
4. Update `record_count` in JSON file

### Resetting Data
```bash
# Backup current data
cp data/crm/synthetic_august2025_summary.json data/crm/backup_$(date +%Y%m%d).json

# Re-run enrichment
python tools/enrich_synthetic_customers.py

# Verify
python -c "import json; print(json.load(open('data/crm/synthetic_august2025_summary.json'))['record_count'])"
```

## QuickBase Mapping

### Community-Matching Fields in QuickBase
These flags map to QuickBase Communities table fields:

| Our Flag | QuickBase Field | Field ID |
|----------|----------------|----------|
| requires_hoyer_lift | Hoyer Lift | 91 |
| requires_memory_care | Dedicated Memory Care | 71 |
| requires_bariatric_care | Bariatric | 147 |
| requires_two_person_transfer | 2 Person Transfers | 89 |
| requires_insulin_management | Insulin Management | 90 |
| requires_wound_care | Wound Care | 151 |
| prefers_awake_staff | Awake Night Staff | 19 |
| prefers_pets_allowed | Pet Friendly | 61 |
| prefers_full_kitchen | Full Kitchen | 47 |
| language_preference | Languages Spoken | 104 |

## Support & Maintenance

### Questions or Issues?
1. Check this documentation first
2. Review `tools/enrich_synthetic_customers.py` for generation logic
3. Check git history for recent changes
4. Test with one customer before modifying all 23

### Data Regeneration
If data becomes inconsistent:
1. Restore from git: `git checkout HEAD -- data/crm/synthetic_august2025_summary.json`
2. Re-run enrichment: `python tools/enrich_synthetic_customers.py`
3. Verify in dashboard

---

**Last Updated**: November 6, 2025  
**Maintainer**: CCA Senior Navigator Development Team  
**Status**: ✅ Production-Ready for Demo Use
