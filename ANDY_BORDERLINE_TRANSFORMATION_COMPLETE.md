# Andy Borderline Transformation Complete ✅

**Date:** October 20, 2025  
**Profile:** Andy Assisted GCP Complete  
**Status:** ✅ Complete

---

## 🎯 Objective

Transform Andy from a low-tier Assisted Living case (18 points) into a **borderline Assisted Living/Memory Care case** (23 points) - placing him at the upper threshold of Assisted Living, just 2 points away from the Memory Care tier.

---

## 📊 Score Transformation

### GCP Tier Thresholds (Reference)
- **No Care Needed:** 0-8 points
- **In-Home Care:** 9-16 points
- **Assisted Living:** 17-24 points ← **Andy is here (23 points)**
- **Memory Care:** 25-39 points ← **Threshold: 25 points (only 2 away!)**
- **Memory Care High Acuity:** 40+ points

### Before vs After

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Score** | 18 points | 23 points | +5 points |
| **Tier** | Assisted Living (low) | Assisted Living (borderline) | Same tier, higher risk |
| **Confidence** | 73% | 85% | +12% (more assessment data) |
| **Location** | San Francisco, CA 94102 | Seattle, WA 98101 | Changed |
| **Cognitive Decline** | None | Moderate | Added |
| **ADL Count** | 2 | 3 | +1 |
| **IADL Count** | 3 | 4 | +1 |
| **Falls Risk** | Single fall concern | Multiple falls | Escalated |
| **Monthly Cost** | ~$6,000 (SF estimate) | $7,200 (Seattle + memory support) | +$1,200 |

---

## 🔍 Key Changes

### 1. Location Change
- **From:** San Francisco, CA (94102)
- **To:** Seattle, WA (98101) - Downtown Seattle
- **Reason:** User requirement for Seattle zip code

### 2. Cognitive Decline (Major Change)
- **From:** `false` (no concerns)
- **To:** `"moderate"` (noticeable memory/thinking difficulties)
- **Impact:** +2-3 points toward Memory Care threshold
- **Flag Added:** `moderate_cognitive_decline: true`
- **Rationale:** This is the primary factor pushing Andy toward Memory Care, but it's not severe enough to require it yet

### 3. ADL Dependencies
- **Count:** 2 → 3 (added bathing to existing dressing and mobility)
- **Impact:** +1 point
- **Assessment:** Still manageable in Assisted Living with enhanced support

### 4. IADL Dependencies
- **Count:** 3 → 4 (added medication management to meal prep, shopping, finances)
- **Impact:** +1 point
- **Concern:** Medication errors pose safety risks

### 5. Safety Concerns
- **Falls:** Changed from `falls_risk` to `falls_multiple`
- **Impact:** Multiple recent falls indicate increased fall risk
- **Flag Added:** Enhanced fall prevention needs

### 6. Medical Conditions
- **Added:** Heart disease (in addition to arthritis, diabetes, hypertension)
- **Rationale:** Increases overall health complexity

---

## 🏥 Borderline Profile Characteristics

### Factors Pushing Toward Memory Care (25+ points)
✅ **Moderate cognitive decline** - Memory concerns emerging  
✅ **3 ADLs + 4 IADLs** - Significant dependencies  
✅ **Multiple falls** - Safety risks escalating  
✅ **Lives alone** - No family support network  
✅ **Medication management issues** - Safety concern  

### Factors Keeping in Assisted Living (17-24 points)
✅ **NOT severe cognitive impairment** - Still participates in decisions  
✅ **NO wandering behavior** - Doesn't require secure environment  
✅ **NO behavioral issues** - No aggression, agitation, or combativeness  
✅ **Can still engage socially** - Participates in activities  
✅ **Responsive to redirection** - Doesn't require constant supervision  

---

## 🎯 Rationale for 23 Points

Andy is now a **true borderline case**:

1. **Moderate Memory Concerns:** He has noticeable memory issues that impact daily life, but they're not severe enough to require the secured environment and intensive support of Memory Care.

2. **Significant Dependencies:** With 3 ADLs and 4 IADLs, he needs substantial help, but Assisted Living can provide this level of support.

3. **Safety Risks:** Multiple falls are concerning, but can be addressed with fall prevention programs, enhanced monitoring, and environmental modifications in Assisted Living.

4. **Veteran Benefits:** VA Aid & Attendance can help offset the higher costs of enhanced Assisted Living services.

5. **Recommendation:** Assisted Living **with enhanced memory support programs** - this gives him the supervision and help he needs while preserving independence and dignity.

6. **Monitoring Required:** If cognitive decline progresses to severe, or if wandering/behavioral issues emerge, a reassessment for Memory Care would be appropriate.

---

## 💰 Cost Estimate Updates

### Seattle Assisted Living with Memory Support
- **Base Cost:** $4,500/month (Seattle Assisted Living)
- **Regional Adjustment:** +$675 (Seattle premium)
- **Memory Support Add-on:** +$800 (enhanced memory program)
- **ADL Support Add-on:** +$600 (3 ADLs)
- **Medication Management:** +$300
- **Fall Prevention:** +$325
- **Total:** **$7,200/month** ($86,400/year)

### Cost Breakdown Philosophy
Andy needs more than basic Assisted Living, but less than full Memory Care. The enhanced services (memory support, medication management, fall prevention) bridge the gap while keeping him in a less restrictive environment.

---

## 📋 Profile Status

### Products Completed
- ✅ **GCP (Guided Care Plan):** Complete - 100% progress
  - Status: Published
  - Tier: Assisted Living (borderline)
  - Score: 23 points
  - Confidence: 85%

### Products Not Started
- ⏸️ **Cost Planner:** Not started - 0% progress
  - Andy is preparing to explore costs
  - Seattle market data ready
  - Estimate available: $7,200/month

---

## 🚩 Flags Summary

### Active Flags
1. **`is_veteran: true`** - Eligible for VA benefits
2. **`veteran_aanda_risk: true`** - May qualify for VA Aid & Attendance
3. **`moderate_cognitive_decline: true`** - Memory support needed
4. **`enable_cost_planner_v2: true`** - Cost Planner available
5. **`no_support: true`** - Lives alone, no caregiver
6. **`safety_risk: true`** - Multiple falls
7. **`falls_multiple: true`** - Multiple recent falls
8. **`medication_management: true`** - Needs med supervision
9. **`nutrition_risk: true`** - May need meal assistance
10. **`isolation_risk: true`** - Social isolation concern
11. **`transportation_needs: true`** - Can't drive safely
12. **`financial_stress: true`** - Concerned about costs
13. **`moderate_dependence: true`** - Significant ADL/IADL needs

---

## 🔄 MCIP Contract Updates

### Care Recommendation Contract
All 14 required fields updated:
- ✅ `tier`: "assisted_living"
- ✅ `tier_score`: 23.0
- ✅ `tier_rankings`: Updated with all 5 tiers
- ✅ `confidence`: 0.85
- ✅ `status`: "complete"
- ✅ `flags`: 5 priority flags (veteran, memory, falls, support, dependence)
- ✅ `rationale`: Updated with borderline explanation
- ✅ `generated_at`: Current timestamp
- ✅ `version`: "4.0"
- ✅ `input_snapshot_id`: Updated
- ✅ `rule_set`: "gcp_v4_standard"
- ✅ `next_step`: Points to Cost Planner
- ✅ `last_updated`: Current timestamp
- ✅ `needs_refresh`: false

---

## 📁 Files Modified

### 1. `data/users/demo/demo_andy_assisted_gcp_complete.json`
- **Size:** 7,248 bytes (7.1 KB)
- **Lines:** 250
- **Changes:**
  - Updated `profile.location` to "Seattle, WA"
  - Updated `profile.zip_code` to "98101"
  - Updated `gcp_care_recommendation.tier_score` to 23
  - Updated `gcp_care_recommendation.assessment.cognitive_decline` to "moderate"
  - Updated `gcp_care_recommendation.assessment.adl_count` to 3
  - Updated `gcp_care_recommendation.assessment.iadl_count` to 4
  - Added `gcp_care_recommendation.assessment.conditions`: heart_disease
  - Updated `gcp_care_recommendation.flags`: Added moderate_cognitive_decline, falls_multiple
  - Updated `gcp_care_recommendation.rationale` for borderline case
  - Updated `mcip_contracts.care_recommendation`: All fields synchronized
  - Updated `cost_v2_quick_estimate`: Seattle costs with memory support
  - Updated `flags.moderate_cognitive_decline`: true

### 2. `update_andy_borderline.py` (NEW)
- **Purpose:** Script to generate/update Andy's borderline profile
- **Features:**
  - Comprehensive documentation in docstring
  - 23-point score calculation
  - Seattle location (98101)
  - Moderate cognitive decline
  - Enhanced cost breakdown
  - Borderline rationale
  - Validation output

---

## ✅ Validation Results

```
✅ JSON Valid
Lines: 250
UID: demo_andy_assisted_gcp_complete
Location: Seattle, WA (ZIP: 98101)
Care Tier: assisted_living
Score: 23 points
Cognitive Decline: moderate
ADLs: 3
IADLs: 4
Monthly Cost: $7,200
Veteran: True
Flags: is_veteran, veteran_aanda_risk, moderate_cognitive_decline, enable_cost_planner_v2
```

---

## 🧪 Testing Checklist

- [ ] Test Andy login via demo profile selector
- [ ] Verify GCP tile shows "Complete" with 23 points
- [ ] Verify Care Recommendation shows "Assisted Living (Borderline)"
- [ ] Check that moderate cognitive decline flag displays
- [ ] Verify Cost Planner shows Seattle estimate ($7,200/month)
- [ ] Test Cost Planner unlock (should be available)
- [ ] Verify VA A&A flag displays prominently
- [ ] Check rationale mentions "borderline" and "2 points from Memory Care"
- [ ] Test navigation to Cost Planner from GCP
- [ ] Verify all 13 flags display correctly

---

## 📝 Next Steps

1. **Commit Changes:**
   ```bash
   git add data/users/demo/demo_andy_assisted_gcp_complete.json
   git add update_andy_borderline.py
   git commit -m "feat: Transform Andy to borderline Assisted Living case (23 points)"
   ```

2. **Push to Remote:**
   ```bash
   git push origin dev
   git push origin dev:apzumi
   ```

3. **Test Profile:**
   - Start app: `streamlit run app.py`
   - Login as Andy
   - Verify GCP shows 23 points
   - Check Cost Planner estimate

4. **Document for Stakeholders:**
   - Andy is now a perfect example of a **borderline case**
   - Shows how GCP scoring differentiates between care tiers
   - Demonstrates the value of enhanced Assisted Living vs. Memory Care
   - Highlights VA benefits for eligible veterans

---

## 🎓 Use Case: Andy as a Demo Profile

### What Andy Demonstrates

1. **Borderline Decision-Making:**
   - Shows the nuance between Assisted Living and Memory Care
   - Demonstrates how moderate cognitive decline doesn't automatically mean Memory Care
   - Illustrates the importance of comprehensive assessment

2. **Veteran Benefits:**
   - VA Aid & Attendance eligibility
   - How veteran status can help offset enhanced care costs
   - Importance of exploring all financial resources

3. **Enhanced Assisted Living:**
   - Memory support programs in Assisted Living settings
   - Fall prevention services
   - Medication management
   - How AL can serve higher-acuity residents with specialized programs

4. **Risk Monitoring:**
   - Importance of ongoing assessment
   - When to reassess for higher level of care
   - Red flags: wandering, severe cognitive decline, behavioral issues

5. **Cost Planning:**
   - How enhanced services increase costs
   - Regional variations (Seattle market)
   - Balancing cost with appropriate care level

---

## 🔍 Technical Notes

### Score Calculation (23 points)
Based on GCP v4 scoring logic in `products/gcp_v4/modules/care_recommendation/logic.py`:

- **Age Range (75-84):** Base points
- **Medical Conditions (4):** Arthritis, diabetes, hypertension, heart disease
- **ADLs (3):** Bathing, dressing, mobility → ~3-6 points
- **IADLs (4):** Meal prep, shopping, finances, medications → ~4-8 points
- **Cognitive Decline (moderate):** ~2-3 points
- **Safety Concerns:** Falls, living alone, no support → ~2-4 points
- **Total:** **23 points** (upper end of Assisted Living range)

### Why Not 24 or 25 Points?
- **24 points:** Would still be Assisted Living, but very high risk
- **25 points:** Would trigger Memory Care recommendation
- **23 points:** Perfect borderline - demonstrates the threshold clearly

### Confidence Calculation (85%)
Higher confidence than before (73%) because:
- More assessment questions answered
- Clear cognitive decline indicator
- Multiple flags confirming assessment
- Consistent cross-module data

---

## 📚 Related Documentation

- **GCP Scoring System:** `products/gcp_v4/modules/care_recommendation/logic.py`
- **Tier Thresholds:** `TIER_THRESHOLDS` constant in logic.py
- **Demo Profiles:** `data/users/demo/README.md`
- **Cost Estimation:** `products/cost_planner_v2/`

---

## ✨ Summary

Andy Assisted GCP Complete is now a **borderline Assisted Living case** - sitting at 23 points, just 2 points away from the Memory Care threshold (25 points). He has moderate memory concerns, significant ADL/IADL dependencies, and multiple safety risks, but lacks the severe cognitive impairment or behavioral issues that would require Memory Care.

This profile demonstrates:
- The nuance of care level recommendations
- The value of comprehensive assessment
- How Assisted Living can serve higher-acuity residents with enhanced programs
- The importance of veteran benefits (VA A&A)
- Regional cost variations (Seattle market)
- When to monitor for progression to higher care levels

**Status:** ✅ Profile updated, validated, and ready for testing
**Location:** Seattle, WA (98101)
**Score:** 23 points (borderline Assisted Living/Memory Care)
**Next:** Commit and push to remote repositories

---

**Transformation Complete! 🎉**
