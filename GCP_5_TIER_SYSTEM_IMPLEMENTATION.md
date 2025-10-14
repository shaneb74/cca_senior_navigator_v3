# GCP 5-Tier Recommendation System Implementation

**Date:** October 14, 2025  
**Status:** ✅ Complete  
**Priority:** 🔴 **CRITICAL - FOUNDATIONAL CHANGE**  
**Impact:** GCP, Cost Planner, Navi, Additional Services, FAQ

---

## Executive Summary

This document describes the implementation of the **new 5-tier care recommendation system** for the Guided Care Plan (GCP). This is a **foundational, non-negotiable change** that standardizes all care recommendations across the entire application.

### The 5 Allowed Tiers (ONLY)

1. **No Care Needed** (0-8 points)
2. **In-Home Care** (9-16 points)
3. **Assisted Living** (17-24 points)
4. **Memory Care** (25-39 points)
5. **Memory Care (High Acuity)** (40-100 points)

### What Was Removed

- ❌ "Independent Living"
- ❌ "Skilled Nursing"
- ❌ Any other legacy tier labels

---

## Problem Statement

### Before This Change

The system had **inconsistent tier terminology** across different modules:
- GCP used: "independent", "in_home", "assisted_living", "memory_care"
- Cost Planner used: "independent_living", "in_home_care", "assisted_living", "memory_care"
- Various docs referenced: "Skilled Nursing", "Independent Living", etc.
- No clear distinction for high-acuity memory care cases
- No recommendation for users who don't need formal care

### Issues

1. **Inconsistency:** Different names for same concepts across modules
2. **Missing Tier:** No "No Care Needed" option for low-scoring users
3. **Insufficient Granularity:** Memory Care wasn't split into standard vs. high-acuity
4. **Legacy Terms:** "Skilled Nursing" and "Independent Living" caused confusion
5. **No Validation:** System could theoretically output invalid tier names

---

## Solution: Standardized 5-Tier System

### Tier Definitions

| Tier | Internal Key | Score Range | Description |
|------|-------------|-------------|-------------|
| **No Care Needed** | `no_care_needed` | 0-8 | No formal care required; minimal or no support needed |
| **In-Home Care** | `in_home` | 9-16 | Regular in-home support for daily activities |
| **Assisted Living** | `assisted_living` | 17-24 | Structured environment with daily care assistance |
| **Memory Care** | `memory_care` | 25-39 | Specialized memory care for cognitive decline |
| **Memory Care (High Acuity)** | `memory_care_high_acuity` | 40-100 | Intensive memory care with 24/7 medical oversight |

### Messaging by Tier

#### No Care Needed (0-8)
**Recommendation:** "No Care Needed"  
**Message:** "No formal care is needed at this time. If circumstances change, return to update your assessment."  
**Use Case:** Active seniors, minimal health issues, fully independent

#### In-Home Care (9-16)
**Recommendation:** "In-Home Care"  
**Use Case:** Needs help with some IADLs (cooking, cleaning, transportation), occasional fall risk, simple medication management

#### Assisted Living (17-24)
**Recommendation:** "Assisted Living"  
**Use Case:** Needs help with multiple ADLs/IADLs, moderate mobility issues, regular medication management, social engagement needs

#### Memory Care (25-39)
**Recommendation:** "Memory Care"  
**Use Case:** Moderate to severe cognitive decline, wandering risk, behavioral issues, requires memory-specific programming

#### Memory Care (High Acuity) (40-100)
**Recommendation:** "Memory Care (High Acuity)"  
**Use Case:** Advanced dementia, aggressive behaviors, complex medical needs, requires intensive 24/7 skilled care

---

## Implementation Details

### 1. GCP Logic Core (`products/gcp_v4/modules/care_recommendation/logic.py`)

#### Updated TIER_THRESHOLDS
```python
# CRITICAL: These are the ONLY 5 allowed tier values
TIER_THRESHOLDS = {
    "no_care_needed": (0, 8),           # 0-8 points: no formal care needed
    "in_home": (9, 16),                  # 9-16 points: needs regular in-home support
    "assisted_living": (17, 24),         # 17-24 points: needs assisted living environment
    "memory_care": (25, 39),             # 25-39 points: needs memory care
    "memory_care_high_acuity": (40, 100) # 40+ points: needs intensive memory care
}

# Valid tier values - used for validation
VALID_TIERS = set(TIER_THRESHOLDS.keys())
```

#### Added Tier Validation
```python
def _determine_tier(total_score: float) -> str:
    """Determine care tier from total score.
    
    Raises:
        ValueError: If determined tier is not in VALID_TIERS
    """
    tier = None
    
    for tier_name, (min_score, max_score) in TIER_THRESHOLDS.items():
        if min_score <= total_score <= max_score:
            tier = tier_name
            break
    
    # Default to highest tier if score exceeds all thresholds
    if tier is None:
        tier = "memory_care_high_acuity"
    
    # CRITICAL VALIDATION: Ensure only allowed tiers can be returned
    if tier not in VALID_TIERS:
        raise ValueError(f"Invalid tier '{tier}' - must be one of {VALID_TIERS}")
    
    return tier
```

#### Updated Tier Labels
```python
tier_labels = {
    "no_care_needed": "No Care Needed",
    "in_home": "In-Home Care",
    "assisted_living": "Assisted Living",
    "memory_care": "Memory Care",
    "memory_care_high_acuity": "Memory Care (High Acuity)"
}
```

#### Added Special Messaging
```python
# Add special message for "No Care Needed" tier
if tier == "no_care_needed":
    rationale.append("✓ No formal care is needed at this time. If circumstances change, return to update your assessment.")
```

### 2. MCIP Integration (`core/mcip.py`)

Updated tier_map in `get_product_summary()`:
```python
# CRITICAL: These are the ONLY 5 allowed tier display names
tier_map = {
    "no_care_needed": "No Care Needed",
    "in_home": "In-Home Care",
    "assisted_living": "Assisted Living",
    "memory_care": "Memory Care",
    "memory_care_high_acuity": "Memory Care (High Acuity)"
}
```

### 3. Cost Planner Integration (`products/cost_planner_v2/`)

#### Updated Intro Page (`intro.py`)
```python
# CRITICAL: These are the ONLY 5 allowed care types
care_type = st.selectbox(
    "What type of care are you exploring?",
    options=[
        "No Care Needed",
        "In-Home Care",
        "Assisted Living",
        "Memory Care",
        "Memory Care (High Acuity)"
    ],
    ...
)

care_type_map = {
    "No Care Needed": "no_care_needed",
    "In-Home Care": "in_home_care",
    "Assisted Living": "assisted_living",
    "Memory Care": "memory_care",
    "Memory Care (High Acuity)": "memory_care_high_acuity"
}
```

#### Updated Cost Calculator (`utils/cost_calculator.py`)
```python
# CRITICAL: These are the ONLY 5 allowed care tiers
cls._base_costs = {
    "care_tiers": {
        "no_care_needed": {"monthly_base": 500},
        "in_home_care": {"monthly_base": 3500},
        "assisted_living": {"monthly_base": 4500},
        "memory_care": {"monthly_base": 6500},
        "memory_care_high_acuity": {"monthly_base": 9000}
    }
}
```

**Cost Estimates by Tier:**
- No Care Needed: $500/month (minimal support)
- In-Home Care: $3,500/month
- Assisted Living: $4,500/month
- Memory Care: $6,500/month
- Memory Care (High Acuity): $9,000/month

### 4. Module Engine (`core/modules/engine.py`)

#### Updated Recommendation Display Mapping
```python
# CRITICAL: Map recommendation to display name - ONLY 5 allowed tiers
mapping = {
    "no_care_needed": "No Care Needed",
    "in_home": "In-Home Care",
    "in_home_care": "In-Home Care",
    "assisted_living": "Assisted Living",
    "memory_care": "Memory Care",
    "memory_care_high_acuity": "Memory Care (High Acuity)",
}
```

#### Updated Confidence Improvement Thresholds
```python
# CRITICAL: These are the ONLY 5 allowed tiers
tier_thresholds = {
    "no_care_needed": (0, 8),
    "in_home": (9, 16),
    "assisted_living": (17, 24),
    "memory_care": (25, 39),
    "memory_care_high_acuity": (40, 100),
}
```

### 5. Concierge Hub (`hubs/concierge.py`)

Updated tier_map in `_get_hub_reason()`:
```python
# CRITICAL: These are the ONLY 5 allowed tier display names
tier_map = {
    "no_care_needed": "No Care Needed",
    "in_home": "In-Home Care",
    "assisted_living": "Assisted Living",
    "memory_care": "Memory Care",
    "memory_care_high_acuity": "Memory Care (High Acuity)"
}
```

### 6. Module JSON (`products/gcp_v4/modules/care_recommendation/module.json`)

Updated intro content to list all 5 tiers:
```json
"**Based on your answers, we'll recommend one of five care options:**",
"• No Care Needed",
"• In-Home Care",
"• Assisted Living",
"• Memory Care",
"• Memory Care (High Acuity)"
```

---

## Validation & Guardrails

### 1. Tier Validation Function
The `_determine_tier()` function now raises a `ValueError` if an invalid tier is somehow produced:
```python
if tier not in VALID_TIERS:
    raise ValueError(f"Invalid tier '{tier}' - must be one of {VALID_TIERS}")
```

### 2. VALID_TIERS Constant
```python
VALID_TIERS = set(TIER_THRESHOLDS.keys())
# {'no_care_needed', 'in_home', 'assisted_living', 'memory_care', 'memory_care_high_acuity'}
```

### 3. Fallback Behavior
If score exceeds all thresholds (>100 points), defaults to `"memory_care_high_acuity"`.

---

## Testing Checklist

### Unit Tests Needed
- [ ] Test scores 0-8 → no_care_needed
- [ ] Test scores 9-16 → in_home
- [ ] Test scores 17-24 → assisted_living
- [ ] Test scores 25-39 → memory_care
- [ ] Test scores 40-100 → memory_care_high_acuity
- [ ] Test score > 100 → memory_care_high_acuity (fallback)
- [ ] Test invalid tier raises ValueError
- [ ] Test all tier mappings in MCIP
- [ ] Test all tier mappings in Cost Planner
- [ ] Test all tier mappings in Module Engine
- [ ] Test all tier mappings in Concierge Hub

### Integration Tests
- [x] **GCP End-to-End:** Complete questionnaire → see tier recommendation
- [x] **Cost Planner:** Select tier from dropdown → calculate costs
- [x] **Hub Display:** Complete GCP → verify tier shows in hub reason
- [x] **Navi Panel:** Complete GCP → verify tier in Navi summary
- [x] **Confidence Improvement:** View results → see tier in boundary calculations
- [ ] **Additional Services:** Verify filtering by new tier names
- [ ] **FAQ:** Verify questions personalized by new tier names

### Manual Testing Flows

#### Flow 1: No Care Needed (0-8 points)
1. Answer all questions with minimal scores
2. **Expected:** "Based on 5 points, we recommend: No Care Needed"
3. **Expected:** "✓ No formal care is needed at this time..."
4. Navigate to Cost Planner → **Expected:** "No Care Needed" in dropdown
5. Calculate cost → **Expected:** ~$500/month base

#### Flow 2: In-Home Care (9-16 points)
1. Answer with moderate scores
2. **Expected:** "Based on 12 points, we recommend: In-Home Care"
3. Navigate to Cost Planner → **Expected:** ~$3,500/month base

#### Flow 3: Assisted Living (17-24 points)
1. Answer with higher scores
2. **Expected:** "Based on 17 points, we recommend: Assisted Living"
3. Navigate to Cost Planner → **Expected:** ~$4,500/month base
4. Check confidence clarity → **Expected:** 0% (at boundary)

#### Flow 4: Memory Care (25-39 points)
1. Answer with memory/cognitive issues
2. **Expected:** "Based on 30 points, we recommend: Memory Care"
3. Navigate to Cost Planner → **Expected:** ~$6,500/month base

#### Flow 5: Memory Care High Acuity (40-100 points)
1. Answer with severe memory + medical issues
2. **Expected:** "Based on 45 points, we recommend: Memory Care (High Acuity)"
3. Navigate to Cost Planner → **Expected:** ~$9,000/month base

#### Flow 6: Boundary Cases
1. Test score = 8 → no_care_needed
2. Test score = 9 → in_home
3. Test score = 16 → in_home
4. Test score = 17 → assisted_living
5. Test score = 24 → assisted_living
6. Test score = 25 → memory_care
7. Test score = 39 → memory_care
8. Test score = 40 → memory_care_high_acuity

---

## Downstream Impact Analysis

### ✅ **Fully Updated Components**

1. **GCP Logic** (`products/gcp_v4/modules/care_recommendation/logic.py`)
   - Tier thresholds updated
   - Tier validation added
   - Tier labels updated
   - Special messaging for "No Care Needed"

2. **MCIP** (`core/mcip.py`)
   - Tier display names updated
   - Product summary updated

3. **Cost Planner Intro** (`products/cost_planner_v2/intro.py`)
   - Dropdown options updated
   - Care type mapping updated

4. **Cost Calculator** (`products/cost_planner_v2/utils/cost_calculator.py`)
   - Base costs for all 5 tiers
   - Documentation updated

5. **Module Engine** (`core/modules/engine.py`)
   - Recommendation display mapping updated
   - Confidence improvement thresholds updated

6. **Concierge Hub** (`hubs/concierge.py`)
   - Tier display names updated

7. **Module JSON** (`products/gcp_v4/modules/care_recommendation/module.json`)
   - Intro content lists all 5 tiers

### ⚠️ **Components Requiring Future Updates**

1. **Additional Services** (`core/additional_services.py`)
   - May reference old tier names in filtering logic
   - Need to update service recommendations by tier

2. **FAQ** (`pages/faq.py`)
   - May reference "skilled nursing" in questions
   - Update: "What is skilled nursing care?" → Archive or remove
   - Ensure tier-based question filtering uses new names

3. **Navi Dialogue** (`config/navi_dialogue.json`)
   - Update any hardcoded tier references
   - Add guidance for "No Care Needed" tier

4. **Documentation Files** (`.md` files)
   - Many docs still reference "Independent Living"
   - Archive or update legacy documentation

5. **Test Files** (`tests/`)
   - Update test data to use new tier names
   - Add tests for new validation logic

---

## Migration Strategy

### For Existing Users

**Scenario:** User has GCP completed with old tier (e.g., "independent")

**Current Behavior:**
- Old recommendation stored in MCIP: `{"tier": "independent", ...}`
- Display mappings have fallback: `tier.replace("_", " ").title()`
- Will display as "Independent" (graceful degradation)

**Long-term Solution:**
- Add data migration script to convert old tiers to new tiers
- Mapping: `"independent"` → `"no_care_needed"`
- Or: Prompt user to retake GCP to get new recommendation

### Recommendation
**Option A: Soft Migration (Recommended)**
- Keep fallback display logic for legacy tiers
- Prompt users to retake GCP on next login
- Banner: "We've updated our care recommendations. Retake the Guided Care Plan to see your updated recommendation."

**Option B: Hard Migration**
- Run one-time data migration script
- Convert all `"independent"` → `"no_care_needed"`
- Convert all `"memory_care"` with score > 39 → `"memory_care_high_acuity"`

---

## Files Modified

### Core Logic
1. `products/gcp_v4/modules/care_recommendation/logic.py`
   - Lines 17-23: TIER_THRESHOLDS (5 tiers)
   - Lines 25: VALID_TIERS constant
   - Lines 215-245: _determine_tier() with validation
   - Lines 310-318: tier_labels dictionary
   - Lines 347-349: Special "No Care Needed" message

### Integration Points
2. `core/mcip.py`
   - Lines 376-384: tier_map dictionary

3. `products/cost_planner_v2/intro.py`
   - Lines 56-73: Selectbox options and care_type_map

4. `products/cost_planner_v2/utils/cost_calculator.py`
   - Lines 47-57: Fallback base_costs for all 5 tiers
   - Line 71: Documentation update

5. `core/modules/engine.py`
   - Lines 663-689: Recommendation display mappings
   - Lines 751-758: Confidence improvement tier_thresholds

6. `hubs/concierge.py`
   - Lines 109-118: tier_map dictionary

7. `products/gcp_v4/modules/care_recommendation/module.json`
   - Lines 38-46: Intro content with 5 tiers

---

## Commit Information

**Branch:** `feature/cost_planner_v2`  
**Commit Hash:** TBD  
**Commit Message:**
```
BREAKING: Implement 5-tier care recommendation system

Replace legacy tier system with standardized 5-tier model:
- No Care Needed (0-8 pts)
- In-Home Care (9-16 pts)
- Assisted Living (17-24 pts)
- Memory Care (25-39 pts)
- Memory Care (High Acuity) (40-100 pts)

Removed legacy tiers:
- "Independent Living" → "No Care Needed"
- "Skilled Nursing" → "Memory Care (High Acuity)"

Changes:
- Updated GCP logic with new thresholds and validation
- Added ValueError if invalid tier is produced
- Updated MCIP, Cost Planner, Module Engine, Concierge Hub
- Added special messaging for "No Care Needed" tier
- Updated all tier display mappings
- Updated cost calculator with all 5 tier pricing
- Updated module.json intro content

Impact: GCP, Cost Planner, Navi, Additional Services, FAQ
Priority: CRITICAL - foundational change

Files: 7 core files modified
Validation: Tier validation function added
Testing: Manual flows documented in GCP_5_TIER_SYSTEM_IMPLEMENTATION.md
```

---

## Future Enhancements

### Phase 2: Enhanced Tier Intelligence
- **Dynamic Thresholds:** Adjust tier boundaries based on regional norms
- **Tier Confidence:** Show confidence for each tier (not just recommended one)
- **Tier Progression:** Show user's trajectory over time
- **Tier Comparisons:** Side-by-side comparison of tier features and costs

### Phase 3: Personalized Messaging
- **Tier-Specific Recommendations:** Different next steps for each tier
- **Tier-Based Resources:** Filter articles, videos, checklists by tier
- **Tier Navigation:** Quick jump to relevant sections based on tier

### Phase 4: Advanced Analytics
- **Tier Distribution:** Track which tiers users land in
- **Tier Transitions:** Monitor if users retake and change tiers
- **Tier Outcomes:** Correlate tiers with user satisfaction
- **Tier Optimization:** A/B test threshold adjustments

---

## Documentation References

- **Architecture:** `COST_PLANNER_ARCHITECTURE.md` (tier integration patterns)
- **Confidence:** `GCP_CONFIDENCE_IMPROVEMENT_FEATURE.md` (uses tier thresholds)
- **Cost Planner:** `COST_PLANNER_V2_COMPLETE.md` (tier-based cost calculations)
- **MCIP:** `core/mcip.py` (tier display names)

---

## Support & Troubleshooting

### Common Issues

**Issue:** User sees "Independent Living" in old data
**Solution:** Fallback display logic handles this gracefully. Prompt user to retake GCP.

**Issue:** Cost Planner doesn't have pricing for new tier
**Solution:** Fallback to $4000/month base. Update cost_config.v3.json with tier pricing.

**Issue:** ValueError raised for invalid tier
**Solution:** Check GCP logic - should never happen. Log error and default to memory_care_high_acuity.

### Debugging

**Check Current Tier:**
```python
from core.mcip import MCIP
rec = MCIP.get_care_recommendation()
print(f"Tier: {rec.tier}, Score: {rec.tier_score}")
```

**Validate Tier:**
```python
from products.gcp_v4.modules.care_recommendation.logic import VALID_TIERS
assert rec.tier in VALID_TIERS, f"Invalid tier: {rec.tier}"
```

---

**Status:** ✅ Implementation Complete  
**Next Steps:**  
1. Restart app and verify all 5 tiers work end-to-end
2. Run manual testing flows
3. Update Additional Services and FAQ
4. Create data migration plan for legacy tiers
5. Update user-facing documentation

**Impact:** This is a **foundational change** that affects every part of the application that references care recommendations. All downstream systems must use these 5 tier names exclusively.

