# GCP Scoring V3 Implementation Summary

**Date:** October 13, 2025  
**Status:** 🟡 In Progress - Core logic implemented, fine-tuning needed

---

## 🎯 Objective

Rebuild the GCP care recommendation scoring logic using the proven clinical model from `gcp_v3_scoring.csv` instead of the broken flag-counting system in the current `logic.py`.

---

## 📊 Approach: Hybrid Scoring System

Combined the CSV's clinical decision rules with the current `module.json` question structure:

### **CSV Scoring Model**
- **Domain-weighted scoring**: Each question domain (ADL/IADL, Cognitive, Support, etc.) has a weight (1-3)
- **Override rules**: High-priority clinical decisions (e.g., severe cognitive + no support → Memory Care)
- **Modifier rules**: Adjustments based on context (e.g., strong support reduces tier)
- **Clear tier boundaries**: 0=Independent, 1=In-Home, 2=Assisted Living, 3=Memory Care, 4=High-Acuity Memory Care

### **Implementation**
Created `products/gcp/modules/care_recommendation/logic_v3.py`:

```python
# Domain weights from CSV
DOMAIN_WEIGHTS = {
    "adl_iadl": 3,          # Critical for daily function
    "cognitive": 3,         # Critical for safety
    "support": 2,           # Important but not critical
    "mobility": 2,          # Important for safety
    "medication": 2,        # Important for health
    "health": 2,            # Important for stability
    "mood": 1,              # Secondary factor
    "isolation": 1          # Modifier only
}

# Scoring flow:
# 1. Score each answer (0-3 raw points)
# 2. Sum by domain
# 3. Apply domain weights
# 4. Calculate base tier from total score
# 5. Apply CSV OVERRIDE rules (memory care, high-acuity, etc.)
# 6. Apply CSV MODIFIER rules (support, isolation adjustments)
```

---

## ✅ What's Working

### **Tests Passing (3/7)**

1. ✅ **High-Acuity Memory Care Override**
   - Severe cognitive + no support → Tier 4
   - Override rule correctly escalates to highest tier

2. ✅ **Independent Senior - No Care Needed**
   - No cognitive issues, fully independent → Tier 0
   - Correctly identifies low-need scenarios

3. ✅ **Assisted Living - Falls + No Support Override**
   - Multiple falls + no support → Tier 2 (Assisted Living)
   - Override rule correctly escalates for safety

### **Key Fixes**

1. **Normalization Bug Fixed**
   - Issue: "None – fully independent" was matching "full" keyword → scored as "full_support"
   - Fix: Check for "independent" BEFORE checking for "full" in string matching

2. **Flag Naming Consistency**
   - Standardized flag names to match CSV expectations (`no_support` not `support_none`)

3. **Domain Weight Application**
   - Fixed: Was applying weights per item in multi-select (badls × 3 per item)
   - Correct: Sum raw scores per domain, THEN apply weight to domain total

---

## 🚧 What Needs Fine-Tuning

### **Tests Failing (4/7)**

4. ❌ **Assisted Living - Moderate Needs**
   - Expected: Tier 2 (Assisted Living)
   - Actual: Tier 3 (Memory Care)
   - Issue: Scores are too high (~39 points pushes into Memory Care range)

5. ❌ **Memory Care - Moderate Cognitive + Behaviors**
   - Expected: Tier 3 (Memory Care)
   - Actual: Tier 2 (Assisted Living) - reduced by strong support modifier
   - Issue: Strong support modifier is too aggressive in reducing tier

6. ❌ **In-Home with Support**
   - Expected: Tier 1 (In-Home Support)
   - Actual: Tier 2 (Assisted Living)
   - Issue: Scores ~27 points, above Tier 1 threshold

7. ❌ **Strong Support Reduces Tier**
   - Expected: Tier 1 (In-Home Support)
   - Actual: Tier 2 (Assisted Living)
   - Issue: Base score too high before modifier applies

---

## 🎚️ Tier Threshold Tuning Needed

Current thresholds:
```python
TIER_THRESHOLDS = {
    0: (0, 8),       # Independent: 0-8 points  
    1: (9, 18),      # In-Home Support: 9-18 points
    2: (19, 30),     # Assisted Living: 19-30 points
    3: (31, 999)     # Memory Care: 31+ points
}
```

### **Recommendations**

Based on test results, suggest:
```python
TIER_THRESHOLDS = {
    0: (0, 6),       # Independent: 0-6 points  
    1: (7, 16),      # In-Home Support: 7-16 points
    2: (17, 28),     # Assisted Living: 17-28 points
    3: (29, 999)     # Memory Care: 29+ points
}
```

**Rationale:**
- Test 4 scores 39 → should be Tier 2, but that's way over even adjusted threshold
- Test 6 scores 27 → should be Tier 1, fits in adjusted 7-16 range if we lower scores
- May also need to adjust individual question weights (not just thresholds)

---

## 📁 Files Created/Modified

### **New Files**
- `products/gcp/modules/care_recommendation/logic_v3.py` - New hybrid scoring implementation
- `products/gcp/modules/care_recommendation/test_logic_v3.py` - Test suite with 7 scenarios
- `GCP_SCORING_V3_IMPLEMENTATION.md` - This document

### **To Be Modified**
- `products/gcp/modules/care_recommendation/logic.py` - Replace with logic_v3.py
- `products/gcp/modules/care_recommendation/logic.json` - Simplify to flags-only (remove scoring)
- `products/gcp/product.py` - Update outcomes_compute path if needed

---

## 🔍 Scoring Breakdown Example

**Test Case: Moderate Needs**
```
Answers:
- help_overall: "Regular – needs daily assistance" → 2 raw points
- badls: ["Bathing/Showering"] → 1 raw point
- iadls: ["Meal preparation", "Housekeeping"] → 2 raw points
- memory_changes: "Occasional forgetfulness" → 1 raw point
- mobility: "Uses cane or walker" → 1 raw point
- falls: "One fall" → 1 raw point
- meds_complexity: "Moderate" → 2 raw points
- chronic_conditions: ["Diabetes", "Hypertension"] → 2 raw points
- hours_per_day: "4–8 hours" → 2 raw points
- primary_support: "Family/friends" → 1 raw point
- mood: "Mostly good" → 1 raw point

Domain Totals (raw):
- adl_iadl: 2 + 1 + 2 = 5 → × 3 weight = 15
- cognitive: 1 → × 3 weight = 3
- support: 2 + 1 = 3 → × 2 weight = 6
- mobility: 1 + 1 = 2 → × 2 weight = 4
- medication: 2 → × 2 weight = 4
- health: 2 → × 2 weight = 4
- mood: 1 → × 1 weight = 1

Total Score: 15 + 3 + 6 + 4 + 4 + 4 + 1 = 37 points
Base Tier: 3 (exceeds 31 threshold)
After Overrides: 3 (no overrides)
Final Tier: 3 (no modifiers)
Expected: Tier 2 ❌
```

**Problem:** Even moderate needs are scoring too high due to cumulative domain weighting.

---

## 🚀 Next Steps

1. **Adjust domain weights or tier thresholds**
   - Option A: Lower tier thresholds (8/18/30 → 6/14/24)
   - Option B: Reduce domain weights (adl_iadl: 3 → 2, cognitive: 3 → 2.5)
   - Option C: Cap more domains (currently only cognitive and health capped)

2. **Review BADLs/IADLs scoring**
   - Each selected item adds 1 point, but CSV shows individual questions with 0-3 scale
   - May need to score based on # of items: 1-2=1pt, 3-4=2pts, 5+=3pts

3. **Test with real-world scenarios**
   - Get example cases from CSV or clinical team
   - Validate tier assignments make sense

4. **Integration**
   - Replace `logic.py` with `logic_v3.py`
   - Update imports in `product.py`
   - Run existing test suite (`tests/test_care_recommendation.py`)

5. **Documentation**
   - Update `README.md` in care_recommendation module
   - Document scoring algorithm for clinical review

---

## 💡 Key Insights

1. **Flag-based scoring was fundamentally flawed**
   - Counting flags (1 point each) doesn't capture severity
   - "High mobility dependence" and "mild cognitive decline" both counted as +1

2. **Domain weighting is powerful but sensitive**
   - Multiplying by 2-3× can quickly push scores into higher tiers
   - Need careful calibration with real-world data

3. **Override rules work well**
   - High-acuity memory care override (severe cog + no support) correctly identifies critical cases
   - Falls + no support override appropriately escalates safety concerns

4. **Modifier rules need refinement**
   - Strong support modifier reducing tier by 1 works for some cases
   - But can incorrectly lower Memory Care → Assisted Living for complex needs

---

## 📊 Testing Matrix

| Test Scenario | Expected Tier | Actual Tier | Status | Issue |
|--------------|--------------|-------------|--------|-------|
| High-Acuity Memory Care | 4 | 4 | ✅ PASS | - |
| Independent Senior | 0 | 0 | ✅ PASS | - |
| Assisted Living - Moderate | 2 | 3 | ❌ FAIL | Score too high (39) |
| Memory Care - High Burden | 3 | 2 | ❌ FAIL | Modifier too aggressive |
| In-Home Support | 1 | 2 | ❌ FAIL | Score too high (27) |
| Assisted Living - Falls Override | 2 | 2 | ✅ PASS | - |
| Strong Support Reduces Tier | 1 | 2 | ❌ FAIL | Base score too high |

**Pass Rate: 43% (3/7 tests)**

---

## 🔗 Related Documents

- `gcp_v3_scoring.csv` - Original clinical scoring model
- `GCP_UNIFIED_SCORING_SYSTEM.md` - Previous scoring attempt (flag-based)
- `GCP_MODULE_UPDATE_SUMMARY.md` - Module structure documentation

---

**Next Review:** After tier threshold adjustments
**Owner:** AI Agent + Shane
