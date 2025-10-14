# 🚨 CRITICAL: Care Recommendation Module Authority

## Architectural Mandate

**The Care Recommendation module is the authoritative source of truth for user intelligence in the Senior Navigator application.**

### Non-Negotiable Rules

1. **DO NOT modify the questions, their order, sections, or scoring**
2. **DO NOT add, remove, or rename questions**  
3. **DO NOT change flag names or generation logic**
4. **DO NOT localize flags - they MUST be globally accessible**

---

## Module Purpose

The Care Recommendation module (`products/gcp_v4/modules/care_recommendation/`) exists to:

1. **Collect data** through a defined sequence of questions grouped into structured sections:
   - About You
   - Medication & Mobility  
   - Cognition & Mental Health
   - Daily Living

2. **Generate intelligence** using authoritative scoring and flag rules:
   - Calculate care recommendation (tier and type)
   - Generate flags representing specific risks or needs
   - Produce confidence scores

3. **Publish contract** to MCIP for system-wide use:
   - Care tier (independent | in_home | assisted_living | memory_care)
   - Care score (numeric confidence)
   - Flags (structured risk/need indicators)
   - Rationale (human-readable justification)

---

## Data Flow Architecture

```
┌─────────────────────────────────────┐
│  Care Recommendation Module         │
│  (module.json = Source of Truth)    │
│                                      │
│  • Questions (order, text, options) │
│  • Scoring (weights, points)        │
│  • Flags (triggers, names)          │
└─────────────┬───────────────────────┘
              │
              ▼ generates
┌─────────────────────────────────────┐
│  CareRecommendation Contract        │
│  (Published to MCIP)                │
│                                      │
│  • tier: string                     │
│  • score: number                    │
│  • flags: List[Dict]                │
│  • rationale: List[string]          │
└─────────────┬───────────────────────┘
              │
              ▼ drives
┌─────────────────────────────────────┐
│  Navi Intelligence Engine           │
│  (Reads from MCIP)                  │
│                                      │
│  • get_all_flags()                  │
│  • get_suggested_questions()        │
│  • get_additional_services()        │
└─────────────┬───────────────────────┘
              │
              ▼ informs
┌─────────────────────────────────────┐
│  Dependent Systems                  │
│                                      │
│  ├─ Additional Services (partners)  │
│  ├─ FAQ Dynamic Questions           │
│  ├─ Cost Planner (modifiers)        │
│  └─ Advisor Prep (context)          │
└─────────────────────────────────────┘
```

---

## Critical Implementation Details

### 1. Module.json is Authoritative

File: `products/gcp_v4/modules/care_recommendation/module.json`

**This file defines:**
- Every question (id, label, options, scoring)
- Every flag trigger (when options set which flags)
- Section order and grouping
- Required vs optional questions
- UI rendering hints

**The module engine (`core/modules/engine.py`) reads this file and:**
- Renders questions in exact order specified
- Applies flag logic via `_apply_effects()` function  
- Stores answers in session state
- Calls `outcomes_compute` function with answers

### 2. Flag Generation is Declarative

Flags are set **directly in module.json** via option properties:

```json
{
  "label": "Multiple falls",
  "value": "multiple",
  "score": 3,
  "flags": ["high_safety_concern", "falls_multiple"]
}
```

When user selects this option:
- Score of 3 is added to calculations
- Flags `high_safety_concern` and `falls_multiple` are set to True
- Module engine stores these in session state

**The logic.py file MUST NOT override or ignore these flags.**

### 3. Central Flag Storage

Flags are stored in: `st.session_state["{state_key}"]["flags"]`

For Care Recommendation module:
- State key: `gcp_care_recommendation`
- Flags location: `st.session_state["gcp_care_recommendation"]["flags"]`

**These flags persist beyond the module and are read by:**
- `core/flags.py:get_all_flags()` - aggregates from all products
- `core/navi.py:NaviOrchestrator` - uses for intelligence
- `core/additional_services.py` - filters partner services
- `pages/faq.py` - selects dynamic questions

### 4. Logic.py Role

File: `products/gcp_v4/modules/care_recommendation/logic.py`

**Responsibilities:**
- Receive `answers` dict from module engine
- Calculate `tier` using scoring algorithm
- Calculate `confidence` based on completeness
- Build `tier_rankings` showing all tier scores
- Generate `rationale` explaining recommendation
- Return dict matching `CareRecommendation` schema

**MUST NOT:**
- Modify answers
- Override flags from module.json
- Change tier mappings arbitrarily
- Ignore scoring weights

**Current Issue:**
The logic.py currently wraps GCP v3 logic which may not respect module.json flags. This needs verification/correction.

### 5. MCIP Publication

File: `products/gcp_v4/product.py`

After module completes, the product publishes to MCIP:

```python
MCIP.publish_care_recommendation(CareRecommendation(
    tier=outcome["tier"],
    tier_score=outcome["tier_score"],
    flags=outcome["flags"],  # From module.json + logic.py
    rationale=outcome["rationale"],
    ...
))
```

This makes the contract available to all downstream systems via:
```python
care_rec = MCIP.get_care_recommendation()
```

---

## Verification Checklist

### ✅ Module.json Compliance

- [ ] All questions present and in correct order
- [ ] All sections match specification  
- [ ] All flag names match those in module.json
- [ ] No questions added or removed
- [ ] No scoring weights modified

### ✅ Logic.py Compliance

- [ ] Reads answers from module engine (not hardcoded)
- [ ] Respects flags set by module.json options
- [ ] Does not override or ignore declarative flags
- [ ] Scoring algorithm matches module.json weights
- [ ] Returns complete CareRecommendation contract

### ✅ Flag Aggregation Compliance

- [ ] `core/flags.py` reads from MCIP correctly
- [ ] Handles both dict and list-of-dicts formats
- [ ] Does not filter or modify flag values
- [ ] Aggregates across all products properly

### ✅ Navi Intelligence Compliance

- [ ] `core/navi.py` uses actual flag names from module.json
- [ ] Question mapping matches flag triggers
- [ ] Service mapping uses correct flag names
- [ ] No hardcoded logic that bypasses flags

### ✅ System Integration Compliance

- [ ] Additional Services reads flags correctly
- [ ] FAQ dynamic questions use flag-based logic
- [ ] Cost Planner references care_recommendation
- [ ] All systems read from MCIP (single source)

---

## Acceptance Criteria

**Before any code change to Care Recommendation system:**

1. ✅ Verify module.json remains authoritative
2. ✅ Confirm flag names match specification  
3. ✅ Test that flags persist globally
4. ✅ Validate downstream systems receive flags
5. ✅ Document any necessary schema changes

**After any code change:**

1. ✅ Run full GCP module (intro → results)
2. ✅ Verify flags appear in session state
3. ✅ Check Navi shows correct questions
4. ✅ Confirm Additional Services update
5. ✅ Test FAQ dynamic questions load
6. ✅ Validate Cost Planner receives tier

---

## Emergency Contact

**If you need to modify the Care Recommendation module:**

1. **STOP** - Read this document completely
2. **Document** - Why the change is needed
3. **Verify** - Impact on all downstream systems
4. **Test** - Full integration suite
5. **Commit** - With detailed explanation

**This module is load-bearing infrastructure. Changes ripple through the entire application.**

---

## Related Documentation

- `GCP_FLAG_MAPPING.md` - Flag → Question/Service mappings
- `NAVI_SINGLE_INTELLIGENCE_LAYER.md` - Navi architecture
- `NEW_PRODUCT_QUICKSTART.md` - MCIP integration pattern
- `products/gcp_v4/modules/care_recommendation/module.json` - Source of truth

---

**Last Updated:** 2025-10-14  
**Status:** ACTIVE - ENFORCE STRICTLY
