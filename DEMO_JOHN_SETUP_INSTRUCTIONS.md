# Demo John Test Profile Setup Instructions

## Overview
This guide explains how to create a pre-configured "John Test" demo user with complete GCP (Guided Care Plan) and Cost Planner assessments.

## Profile Summary

**John Test** (`demo_john_cost_planner`)
- **Location:** Seattle, WA (ZIP: 98101)
- **Age:** 75-84 years old
- **Care Recommendation:** Assisted Living (21 points)
- **Veteran Status:** Navy veteran (1966-1970), 30% disability rating
- **GCP Status:** ✅ Complete (100%)
- **Cost Planner Status:** ✅ Complete (100%)
- **Next Product:** PFMA v3 (unlocked and ready)

## GCP Assessment Answers

### About You
- **Age Range:** 75-84
- **Living Situation:** Alone
- **Isolation:** Accessible (easily accessible)

### Medication & Mobility
- **Medication Complexity:** Complex (many meds or caregiver-managed)
- **Mobility:** Uses walker
- **Falls:** One fall in past six months
- **Chronic Conditions:** Diabetes, Hypertension, Arthritis

### Cognition & Mental Health
- **Memory Changes:** Occasional forgetfulness
- **Mood:** Mostly good
- **Behaviors:** Confusion

### Daily Living
- **Help Overall:** Daily help (needs daily assistance)
- **ADLs (Activities of Daily Living):** Bathing, Dressing, Transferring
- **IADLs (Instrumental ADLs):** Meal prep, Medication management
- **Hours per Day:** 4-8 hours
- **Primary Support:** Family

### Care Recommendation Result
- **Tier:** Assisted Living
- **Score:** 21 points (range: 17-24 for Assisted Living)
- **Confidence:** 85%

### Care Flags (6 total)
1. **Chronic Conditions** - Diabetes, hypertension, arthritis requiring management
2. **Moderate Mobility** - Uses walker, needs accessibility modifications
3. **Moderate Safety Concern** - One fall requiring attention
4. **Mild Cognitive Decline** - Occasional forgetfulness
5. **Moderate Dependence** - Needs regular help with daily activities
6. **Veteran A&A Eligible** - May qualify for VA Aid & Attendance benefits

## Cost Planner Assessments

### Income Module (Completed)
- **Social Security:** $2,200/month
- **Pension:** $1,800/month
- **Other Income:** $500/month (quarterly dividends)
- **Total Monthly Income:** $4,500

### Assets Module (Completed)
- **Checking/Savings:** $45,000
- **Investment Accounts:** $240,000
- **Primary Residence:** $650,000 (no mortgage)
- **Total Liquid Assets:** $285,000

### VA Benefits Module (Completed)
- **Veteran Status:** Yes
- **Service Branch:** Navy
- **Service Years:** 1966-1970
- **Disability Rating:** 30%
- **Interested in Benefits:** Yes

### Health Insurance Module (Completed)
- **Primary Coverage:** Medicare
- **Medigap:** Plan G ($185/month)

### Life Insurance Module (Completed)
- **Policy Type:** Term life
- **Premium:** $125/month

### Medicaid Navigation Module (Completed)
- **Currently on Medicaid:** No
- **Interested:** Yes
- **Planning Stage:** Researching

### Quick Estimate
- **Monthly Base Cost:** $5,400
- **Regional Adjustment:** 1.1x (Seattle, WA)
- **Monthly Adjusted Cost:** $5,940
- **Monthly Gap:** $1,440 (care cost minus income)
- **Runway:** 197.9 months (~16.5 years)

## Setup Instructions

### Step 1: Stop the Streamlit App
The app must be stopped to modify user data files:

```bash
# Find the running process
ps aux | grep streamlit | grep -v grep

# Kill the process (replace PID with actual process ID)
kill <PID>

# Or press Ctrl+C in the terminal running the app
```

### Step 2: Run the Creation Script
```bash
python3 create_demo_john.py
```

Expected output:
```
✅ John Test demo profile created successfully!

📄 File: data/users/demo_john_cost_planner.json
👤 UID: demo_john_cost_planner
📍 Location: Seattle, WA (ZIP: 98101)

🏥 Care Recommendation: ASSISTED LIVING
   Score: 21 points
   Confidence: 85%

🏷️  Care Flags (6):
   - Chronic Conditions
   - Mobility Assistance Needed
   - Safety Monitoring Needed
   - Mild Memory Changes
   - Regular Assistance Needed
   - Veteran A&A Eligible

📋 GCP Assessment Complete:
   Age: 75_84
   Mobility: walker
   Memory: occasional
   ADL Support: bathing, dressing, transferring
   IADL Support: meal_prep, med_management

💰 Financial Summary:
   Monthly Income: $4,500
   Liquid Assets: $285,000
   Veteran: True (Navy, 30% disability)
   Estimated Care Cost: $5,940/month (Seattle, WA)
   Monthly Gap: $1,440
   Runway: 197.9 months

✅ Both GCP and Cost Planner completed and published!
🎯 Next Step: PFMA (Personal Financial Management Assistant) ready

🚀 To use: Login as 'John Test' in the app
```

### Step 3: Restart the Streamlit App
```bash
streamlit run app.py
```

### Step 4: Login as John Test
1. Navigate to: `http://localhost:8501/`
2. Click "Demo/Test Login 🧪" button on welcome page
3. Click "John Test" button to load profile
4. You should see:
   - GCP tile showing "Complete" (100%)
   - Cost Planner tile showing "Complete" (100%)
   - PFMA tile showing "Ready" (unlocked)
   - Journey hub: Financial Hub (current)

## Testing Checklist

### GCP Verification
- [ ] Navigate to GCP product
- [ ] Verify "Results" page shows Assisted Living recommendation
- [ ] Verify 21 points score displayed
- [ ] Verify 6 care flags shown with descriptions
- [ ] Verify rationale shows scoring breakdown
- [ ] Verify suggested next step is "Cost Planner"

### Cost Planner Verification
- [ ] Navigate to Cost Planner
- [ ] Verify all 6 modules show "Completed" status
- [ ] Verify Income module shows $4,500 total
- [ ] Verify Assets module shows $285,000 liquid assets
- [ ] Verify VA Benefits module shows Navy veteran with 30% rating
- [ ] Verify Quick Estimate shows $5,940/month for Seattle
- [ ] Verify Expert Review calculates financial gap and runway

### Persistence Verification
- [ ] Review all data as John Test
- [ ] Restart the Streamlit app
- [ ] Login as John Test again
- [ ] Verify ALL data persists (GCP answers, Cost Planner modules, recommendations)
- [ ] Check tiles still show "Complete" status

## Troubleshooting

### "File already exists" error
The file was created by the app but is empty. Stop the app first, then run the script.

### "Operation not permitted" error
The Streamlit app has a file lock. You must stop the app before running the script.

### Data doesn't persist after restart
Check `core/session_store.py` - ensure these keys are in `USER_PERSIST_KEYS`:
- `gcp_care_recommendation`
- `gcp_v4_published`
- `gcp_v4_complete`
- All `cost_v2_*` keys

### GCP shows as incomplete
Verify the `tiles` section in the JSON has:
```json
"gcp_v4": {
  "status": "completed",
  "progress": 100.0,
  "saved_state": { ... all answers ... }
}
```

## File Structure

The demo user data is stored at:
```
data/users/demo_john_cost_planner.json
```

This file contains:
- Profile information (name, age, location, zip)
- Progress tracking (completed products)
- GCP assessment answers (`gcp_care_recommendation`)
- GCP care recommendation result (`mcip_contracts.care_recommendation`)
- Cost Planner module data (`cost_v2_modules`)
- Cost Planner quick estimate (`cost_v2_quick_estimate`)
- Tile states (`tiles`, `product_tiles_v2`)
- Journey tracking (`mcip_contracts.journey`)

## Scoring Logic (GCP)

The 21-point score breaks down as follows:

| Section | Points | Key Answers |
|---------|--------|-------------|
| Medication & Mobility | 8 | Complex meds (3), walker (1), one fall (1), 3 chronic conditions (3) |
| Cognition & Mental Health | 3 | Occasional forgetfulness (1), mostly good mood (1), confusion behavior (1) |
| Daily Living | 10 | Daily help (2), 3 ADLs (3), 2 IADLs (2), 4-8 hours support (2), family caregiver (1) |
| **Total** | **21** | **Assisted Living tier (17-24 range)** |

## Care Tier Thresholds

- **0-8 points:** No Care Needed
- **9-16 points:** In-Home Care
- **17-24 points:** Assisted Living ✅ (John scores 21)
- **25-39 points:** Memory Care
- **40+ points:** Memory Care (High Acuity)

## Related Documentation

- `HOW_PERSISTENCE_WORKS.md` - Explains persistence system
- `COST_PLANNER_ASSESSMENT_FIXES_SUMMARY.md` - Cost Planner data integrity fixes
- `DEMO_USER_LOGIN_GUIDE.md` - Demo user login system overview
- `create_demo_john.py` - Python script to create profile

## Notes

- The profile uses **Seattle, WA (98101)** instead of San Francisco to test different regional cost adjustments
- Veteran status is set to **True** to test VA benefits integration and Aid & Attendance eligibility
- All 6 Cost Planner modules are marked complete to enable Expert Review testing
- PFMA (Personal Financial Management Assistant) is unlocked as the next recommended product
- The profile demonstrates a realistic scenario: moderate care needs with financial capacity but monthly gap requiring planning
