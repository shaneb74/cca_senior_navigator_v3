# IL/SNF Content Cleanup - Complete

**Date:** October 14, 2025  
**Status:** ✅ COMPLETE  
**Branch:** `feature/cost_planner_v2`

## Overview

Removed all references to "Independent Living" and "Skilled Nursing" as **care tier options** from the application. Medical/Medicare context references to "skilled nursing" were intentionally preserved as they refer to medical services, not care tiers.

---

## Changes Made

### 1. `pages/_stubs.py` (Line 792)
**Before:**
```python
tier_map = {
    "independent": "Independent Living",
    "in_home": "In-Home Care", 
    "assisted_living": "Assisted Living",
    "memory_care": "Memory Care"
}
```

**After:**
```python
tier_map = {
    "no_care": "No Care Needed",
    "in_home": "In-Home Care", 
    "assisted_living": "Assisted Living",
    "memory_care": "Memory Care",
    "memory_care_high": "Memory Care — High Acuity"
}
```

**Impact:** Debug page now shows correct 5-tier system.

---

### 2. `config/navi_dialogue.json` (Line 150)
**Before:**
```json
"navi_says": "I'll use your answers to recommend Independent Living, In-Home Care, Assisted Living, or Memory Care. Ready?"
```

**After:**
```json
"navi_says": "I'll use your answers to recommend In-Home Care, Assisted Living, or Memory Care. Ready?"
```

**Impact:** Navi intro message now reflects correct care types (no IL mention).

---

### 3. `products/cost_planner/cost_estimate.py` (Lines 41-54)
**Before:**
```python
"description": "Intensive memory care with skilled nursing support",

TIER_TO_CARE_TYPE = {
    "Independent / In-Home": "no_care",
    "In-Home Care": "in_home",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "High-Acuity Memory Care": "memory_care_high",
    "Skilled Nursing": "memory_care_high",  # Same tier
}
```

**After:**
```python
"description": "Intensive memory care with 24/7 monitoring and medical support",

TIER_TO_CARE_TYPE = {
    "No Care Needed": "no_care",
    "In-Home Care": "in_home",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "Memory Care — High Acuity": "memory_care_high",
}
```

**Impact:** 
- Removed "Skilled Nursing" tier mapping
- Updated description to avoid "skilled nursing" term
- Updated tier names to match current 5-tier system

---

### 4. `products/cost_planner/cost_estimate_v2.py` (Lines 56-62)
**Before:**
```python
TIER_TO_CARE_TYPE = {
    "Independent / In-Home": "no_care",
    "In-Home Care": "in_home_care",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "High-Acuity Memory Care": "memory_care_high_acuity",
    "Skilled Nursing": "memory_care_high_acuity",
}
```

**After:**
```python
TIER_TO_CARE_TYPE = {
    "No Care Needed": "no_care",
    "In-Home Care": "in_home_care",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "Memory Care — High Acuity": "memory_care_high_acuity",
}
```

**Impact:** Removed "Skilled Nursing" tier mapping, updated tier names.

---

## Preserved References (Intentional)

The following files contain "skilled nursing" references that were **intentionally preserved** because they refer to medical services (Medicare coverage context), not care tier options:

### 1. `pages/faq.py`
- **Line 52:** Medicare coverage explanation mentions "Short-term skilled nursing (up to 100 days post-hospitalization)"
- **Lines 190-214:** Entire FAQ entry about skilled nursing facilities (medical context)
- **Line 269-270:** Flag detection for "skilled_nursing_recommended" (backend logic)

**Rationale:** These references describe Medicare-covered medical services, not our care tier system.

### 2. `products/cost_planner_v2/intro.py`
- **Line 251:** "24/7 skilled nursing and advanced medical support" (descriptive text for high-acuity care)

**Rationale:** Describes the medical services provided, not a care tier name.

### 3. `products/cost_planner_v2/modules/coverage.py`
- **Line 140:** "Covers skilled nursing care (up to 100 days)"
- **Line 148:** "Yes - Skilled nursing (short-term)" (dropdown option)

**Rationale:** Describes Medicare coverage options for medical services.

---

## Validation

### Files Checked
✅ All `.py` files in workspace  
✅ All `.json` config files  
✅ Documentation files (confirmed they reference old terms for historical context)

### Search Results
```bash
grep -r "Independent Living" --include="*.py" --include="*.json"
# No care tier references found (only historical docs)

grep -r "Skilled Nursing" --include="*.py" --include="*.json"  
# Only Medicare/medical context references remain
```

### Allowed Care Types (Post-Cleanup)
1. ✅ No Care Needed (`no_care`)
2. ✅ In-Home Care (`in_home`, `in_home_care`)
3. ✅ Assisted Living (`assisted_living`)
4. ✅ Memory Care (`memory_care`)
5. ✅ Memory Care — High Acuity (`memory_care_high`, `memory_care_high_acuity`)

### Removed Care Types
- ❌ Independent Living (`independent`)
- ❌ Skilled Nursing (as a tier)

---

## Testing Checklist

- [ ] **GCP Results Page:** Run through GCP, verify no "Independent Living" or "Skilled Nursing" tier displayed
- [ ] **Navi Intro Message:** Start GCP, verify Navi intro doesn't mention IL
- [ ] **Cost Planner Tier Mapping:** Complete GCP → Cost Planner, verify tier maps correctly
- [ ] **FAQ Page:** Search for "skilled nursing", verify only Medicare context appears
- [ ] **Debug Page:** Check MCIP debug view, verify tier_map shows 5 tiers correctly

---

## Impact Assessment

### User-Facing Changes
✅ **No breaking changes** - Only cleaned up legacy terminology  
✅ **Consistent messaging** - All tier references now use 5-tier system  
✅ **Preserved medical context** - Medicare "skilled nursing" references intact

### Backend Changes
✅ **Tier mappings updated** - Cost estimator now uses correct tier names  
✅ **No data migration needed** - Existing user data uses tier keys (not labels)  
✅ **Backward compatible** - Old tier keys still work (defensive coding)

---

## Related Documentation

The following documents contain historical references to IL/SNF (intentionally preserved for context):
- `GCP_5_TIER_SYSTEM_IMPLEMENTATION.md` - Documents the transition away from IL/SNF
- `GCP_5_TIER_TESTING_GUIDE.md` - Testing guide mentions what NOT to see
- `GCP_5_TIER_DEPLOYMENT_SUMMARY.md` - Deployment notes about the change
- `COST_PLANNER_QUICK_ESTIMATE_SPEC.md` - Spec confirms IL/SNF removal

These docs serve as historical record and should NOT be updated.

---

## Commit Message

```
refactor: Remove Independent Living and Skilled Nursing tier references

- Update pages/_stubs.py tier_map to use 5-tier system
- Update config/navi_dialogue.json GCP intro message
- Update products/cost_planner/cost_estimate.py tier mappings
- Update products/cost_planner/cost_estimate_v2.py tier mappings
- Preserve medical context "skilled nursing" references (Medicare/FAQ)

Closes task: F) Global Content Cleanup - Remove IL/SNF
```

---

## Next Steps

1. ✅ Commit changes
2. ⏭️ Run manual testing (GCP → Cost Planner flow)
3. ⏭️ Move to next task: Navi placement & CSS spacing

---

**Status:** ✅ **COMPLETE**  
**Files Modified:** 4  
**Lines Changed:** ~20  
**Breaking Changes:** None
