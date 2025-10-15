# Flag Architecture Analysis

## Current State Assessment

### 1. **Central Flag Registry** ✅ EXISTS
**Location:** `core/flags.py`

**Purpose:** 
- Single source of truth for reading flags across the app
- Aggregates flags from GCP, Cost Planner, PFMA
- Used by Navi and Additional Services

**Functions:**
- `get_all_flags()` - Returns dict of all active flags
- `get_flag(name)` - Gets single flag value
- `has_any_flags(list)` - Check if any flag is true
- `has_all_flags(list)` - Check if all flags are true

**Status:** ✅ Working correctly as flag aggregator

---

### 2. **GCP Care Recommendation Flags** ⚠️ TWO-TIER SYSTEM

#### Tier 1: High-Level Flag Schema (Display Layer)
**Location:** `products/gcp_v4/modules/care_recommendation/flags.py`

**Contains:** 10 standardized flags with rich metadata for UI display:

| Flag ID | Label | Tone | Priority | CTA Route |
|---------|-------|------|----------|-----------|
| `falls_risk` | High Fall Risk | warning | 1 | learning/fall_prevention |
| `memory_support` | Memory Care Needed | critical | 0 | partners/memory_care |
| `behavioral_concerns` | Behavioral Support Required | critical | 0 | partners/behavioral_support |
| `medication_management` | Medication Management Needed | warning | 2 | learning/medication |
| `isolation_risk` | Social Isolation Risk | info | 3 | learning/social_engagement |
| `adl_support_high` | Extensive ADL Support | warning | 2 | learning/daily_living_support |
| `mobility_limited` | Limited Mobility | warning | 2 | partners/wheelchair_accessible |
| `chronic_conditions` | Multiple Chronic Conditions | warning | 2 | learning/health_management |
| `safety_concerns` | Safety Concerns | warning | 1 | learning/safety |
| `caregiver_stress` | Caregiver Burden | info | 3 | learning/caregiver_support |

**Purpose:**
- Display in MCIP panels and action cards
- Provide user-facing labels and descriptions
- Define routing to resources (Learning Center, Partners)
- Set visual tone (critical/warning/info) and priority

#### Tier 2: Granular Assessment Flags (Data Layer)
**Location:** `products/gcp_v4/modules/care_recommendation/module.json`

**Contains:** 50+ granular flags set by specific user responses:

| Category | Example Flags | Set When |
|----------|---------------|----------|
| **Mobility** | `moderate_mobility`, `high_mobility_dependence` | Uses walker, wheelchair, bedbound |
| **Falls** | `moderate_safety_concern`, `high_safety_concern`, `falls_multiple` | One fall, multiple falls |
| **Chronic Conditions** | `chronic_present` | Any chronic disease selected |
| **Cognitive** | `mild_cognitive_decline`, `moderate_cognitive_decline`, `severe_cognitive_risk` | Memory issues by severity |
| **Mental Health** | `moderate_risk`, `high_risk`, `mental_health_concern` | Emotional wellbeing responses |
| **Behaviors** | `moderate_safety_concern` | Wandering, aggression, confusion, etc. |
| **ADL Dependence** | `moderate_dependence`, `high_dependence`, `veteran_aanda_risk` | Needs help with ADLs |
| **Support System** | `no_support`, `limited_support` | Caregiver availability |
| **Geographic** | `low_access`, `very_low_access`, `geo_isolated` | Rural/isolated location |

**Purpose:**
- Capture specific user responses with high fidelity
- Enable detailed analytics and reporting
- Support future feature flags or granular routing
- Maintain audit trail of assessment responses

---

### 3. **The Missing Link** 🔴 CRITICAL ISSUE

**Problem:** `logic.py` does NOT map granular flags → high-level flags!

**Current Flow:**
```
User answers questions
    ↓
module.json sets granular flags (e.g., "severe_cognitive_risk")
    ↓
logic.py extracts flags from answers
    ↓
FLAGS_SCHEMA builds display metadata
    ↓
⚠️ NO MAPPING OCCURS ⚠️
    ↓
MCIP receives raw granular flags
    ↓
Additional Services look for high-level flags (e.g., "memory_support")
    ↓
🔴 FLAGS DON'T MATCH - Services don't trigger!
```

**Expected Flow:**
```
User answers questions
    ↓
module.json sets granular flags
    ↓
logic.py extracts granular flags
    ↓
✅ MAPPING LOGIC converts granular → high-level ✅
    ↓
FLAGS_SCHEMA builds display metadata for high-level flags
    ↓
MCIP receives high-level flags
    ↓
Additional Services match on high-level flags
    ↓
✅ Services trigger correctly!
```

---

## Evidence of the Problem

### Example 1: Memory Support Flag
**Granular flags set by module.json:**
- `mild_cognitive_decline`
- `moderate_cognitive_decline`
- `severe_cognitive_risk`

**High-level flag expected by services:**
- `memory_support`

**Current Result:** ❌ `memory_support` is NEVER set, so SeniorLife AI never triggers!

**Fix Needed:** Map `moderate_cognitive_decline` OR `severe_cognitive_risk` → `memory_support`

---

### Example 2: Medication Management Flag
**Granular flags set by module.json:**
- `moderate_dependence` (when "Medication management" IADL is selected)
- `veteran_aanda_risk` (same trigger)

**High-level flag expected by services:**
- `medication_management`

**Current Result:** ❌ `medication_management` is NEVER set, so OMCARE never triggers!

**Fix Needed:** Add logic to detect complex med scenarios and set `medication_management`

---

### Example 3: Falls Risk Flag
**Granular flags set by module.json:**
- `moderate_safety_concern` (one fall)
- `high_safety_concern` (multiple falls)
- `falls_multiple` (multiple falls)

**High-level flag expected by services:**
- `falls_risk` ✅ (note the 's')

**Current Result:** ⚠️ Need to verify if `falls_risk` is being set by logic.py

**Fix Needed:** Map `falls_multiple` OR `high_safety_concern` → `falls_risk`

---

## Recommended Solution

### Option A: Add Mapping Logic to `logic.py` ⭐ RECOMMENDED

**Location:** `products/gcp_v4/modules/care_recommendation/logic.py`

**Add new function after `_extract_flags_from_answers()`:**

```python
def _map_granular_to_high_level_flags(granular_flags: List[str]) -> List[str]:
    """Map granular assessment flags to high-level display flags.
    
    This bridges the gap between:
    - Granular flags: Set by specific user responses in module.json
    - High-level flags: Used for service routing and display in FLAGS_SCHEMA
    
    Args:
        granular_flags: Raw flags from user's assessment responses
    
    Returns:
        List of high-level flag IDs matching FLAGS_SCHEMA
    """
    high_level = []
    granular_set = set(granular_flags)
    
    # FALLS RISK - 2+ falls or high safety concern
    if "falls_multiple" in granular_set or "high_safety_concern" in granular_set:
        high_level.append("falls_risk")
    
    # MEMORY SUPPORT - Moderate to severe cognitive decline
    if "moderate_cognitive_decline" in granular_set or "severe_cognitive_risk" in granular_set:
        high_level.append("memory_support")
    
    # BEHAVIORAL CONCERNS - Any behavioral flags from multi-select
    behavioral_indicators = {
        "wandering", "aggression", "elopement", "confusion",
        "sundowning", "repetitive", "judgment", "hoarding"
    }
    if granular_set & behavioral_indicators:  # Set intersection
        high_level.append("behavioral_concerns")
    
    # MEDICATION MANAGEMENT - Complex med needs (will need scoring logic)
    # TODO: Add med complexity logic based on number of meds + IADL needs
    if "med_management" in granular_set:  # If IADL med management selected
        high_level.append("medication_management")
    
    # ISOLATION RISK - Geographic or social isolation
    if "very_low_access" in granular_set or "geo_isolated" in granular_set:
        high_level.append("isolation_risk")
    
    # ADL SUPPORT HIGH - Extensive ADL needs
    if "high_dependence" in granular_set:
        high_level.append("adl_support_high")
    
    # MOBILITY LIMITED - High mobility dependence (wheelchair/bedbound)
    if "high_mobility_dependence" in granular_set:
        high_level.append("mobility_limited")
    
    # CHRONIC CONDITIONS - Multiple chronic diseases
    if "chronic_present" in granular_set:
        # TODO: Count how many chronic conditions selected
        high_level.append("chronic_conditions")
    
    # SAFETY CONCERNS - High safety risk from multiple factors
    if granular_set & {"high_safety_concern", "moderate_safety_concern"}:
        high_level.append("safety_concerns")
    
    # CAREGIVER STRESS - Limited or no support
    if "no_support" in granular_set or "limited_support" in granular_set:
        high_level.append("caregiver_stress")
    
    return high_level
```

**Then update `derive_outcome()` to use this mapping:**

```python
def derive_outcome(answers: Dict[str, Any], context: Dict[str, Any] = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
    # ... existing code ...
    
    # Extract granular flags from answers
    granular_flag_ids = _extract_flags_from_state(answers)
    if not granular_flag_ids:
        granular_flag_ids = _extract_flags_from_answers(answers, module_data)
    
    # ✅ ADD THIS: Map granular flags to high-level flags
    high_level_flag_ids = _map_granular_to_high_level_flags(granular_flag_ids)
    
    # Build flag objects with display metadata
    flags = build_flags(high_level_flag_ids)
    
    # ... rest of function ...
```

**Benefits:**
- ✅ Keeps granular flags for analytics
- ✅ Produces high-level flags for UI/routing
- ✅ Maintains single source of truth (FLAGS_SCHEMA)
- ✅ Easy to maintain and extend
- ✅ No breaking changes to other systems

---

### Option B: Flatten Everything to High-Level Flags Only ❌ NOT RECOMMENDED

**Change:** Remove all granular flags from module.json, only set high-level flags

**Problems:**
- ❌ Loss of granular data for analytics
- ❌ Can't distinguish between "one fall" vs "multiple falls"
- ❌ Can't track specific ADL dependencies
- ❌ Large refactor of module.json (500+ lines)
- ❌ Breaks existing analytics/reporting

---

### Option C: Add Aliases to FLAGS_SCHEMA ⚠️ PARTIAL SOLUTION

**Change:** Add multiple IDs for same flag (e.g., `falls_risk`, `falls_multiple`)

**Problems:**
- ⚠️ Doesn't solve the mapping problem
- ⚠️ Still need logic to set the right flags
- ⚠️ Bloats FLAGS_SCHEMA with 50+ entries
- ⚠️ Confuses which flags are "canonical"

---

## Implementation Checklist

### Phase 1: Add Mapping Function ✅ RECOMMENDED NEXT STEP
- [ ] Add `_map_granular_to_high_level_flags()` to `logic.py`
- [ ] Update `derive_outcome()` to call mapping function
- [ ] Add unit tests for mapping logic
- [ ] Test with completed GCP → verify flags appear in MCIP

### Phase 2: Refine Mapping Rules
- [ ] Add medication complexity logic (need answer to "How many medications?")
- [ ] Add chronic condition counting (2+ conditions → `chronic_conditions`)
- [ ] Add scoring thresholds (e.g., only set `memory_support` if score > X)
- [ ] Test edge cases (mild symptoms shouldn't trigger high-acuity flags)

### Phase 3: Verify Service Triggering
- [ ] Test OMCARE triggers on `medication_management`
- [ ] Test SeniorLife AI triggers on `memory_support` + `falls_risk`
- [ ] Test Fall Prevention triggers on `falls_risk`
- [ ] Test Memory Care triggers on `memory_support`
- [ ] Verify "Navi Recommended" labels appear correctly

### Phase 4: Documentation
- [ ] Update FLAG_ARCHITECTURE_ANALYSIS.md with final mapping logic
- [ ] Document which granular flags map to which high-level flags
- [ ] Update NAVI_COST_FEATURES_IMPLEMENTED.md with correct flag names
- [ ] Add inline comments to module.json explaining flag purpose

---

## Summary

**The Problem:**
- GCP has TWO flag systems that don't talk to each other
- Granular flags (50+) capture detailed assessment data
- High-level flags (10) drive UI and service routing
- **NO MAPPING EXISTS** between them

**The Solution:**
- Add mapping logic to `logic.py` (Option A)
- Convert granular flags → high-level flags after assessment
- Publish high-level flags to MCIP
- Services and Additional Services will work correctly

**The Quick Fix:**
- I already updated `additional_services.py` to use correct high-level flag names
- Now we need `logic.py` to actually SET those high-level flags!

**Next Step:**
- Implement `_map_granular_to_high_level_flags()` in logic.py
- This will fix OMCARE, SeniorLife AI, and all other flag-triggered services
