# GCP Care Recommendation Module Update - Summary

**Date:** October 13, 2025  
**Module:** `products/gcp/modules/care_recommendation/`

## Overview

Updated the Guided Care Plan (GCP) module with new question structure, conditional visibility logic, updated flag system, and message rendering on results page.

---

## Files Modified

### 1. `module.json` (NEW - replaces module.json.OLD)

**Key Changes:**
- **New Questions Added:**
  - `help_overall` - Overall daily help assessment (triggers BADL/IADL visibility)
  - Reordered questions in Daily Living section
  
- **Updated Flag Structure:**
  - `isolation`: Now sets `low_access` (somewhat) and `very_low_access` + `geo_isolated` (very)
  - `mobility`: Sets `moderate_mobility` (walker) or `high_mobility_dependence` (wheelchair/bedbound)
  - `falls`: Sets `moderate_safety_concern` (one fall) or `high_safety_concern` + `falls_multiple` (multiple)
  - `chronic_conditions`: Stroke/Parkinson's now also set `moderate_cognitive_decline`
  - `additional_conditions`: Uses regex pattern matching to set `severe_cognitive_risk` for dementia/Alzheimer's
  - `memory_changes`: Sets `mild_cognitive_decline`, `moderate_cognitive_decline`, or `severe_cognitive_risk`
  - `behaviors`: All behaviors set `moderate_safety_concern`
  - `mood`: Sets `moderate_risk` (mostly good/okay) or `high_risk` + `mental_health_concern` (low)
  - `help_overall`: Sets `moderate_dependence` (some_help/daily_help) or `high_dependence` (full_support)
  - `badls`: Each selection sets both `moderate_dependence` and `veteran_aanda_risk`
  - `iadls`: Each selection sets both `moderate_dependence` and `veteran_aanda_risk`
  - `hours_per_day`: Sets `no_support` (<1h) or `limited_support` (1-3h)
  - `primary_support`: Sets `no_support` (none option)

- **Conditional Visibility:**
  - `badls` and `iadls` questions now only appear when specific risk conditions are met:
    - Age 85+
    - Living alone
    - Very isolated location
    - Wheelchair/bedbound mobility
    - Multiple falls
    - Any memory concerns
    - Parkinson's or stroke condition
    - 3+ chronic conditions
    - 3+ additional conditions

- **Question Order (Daily Living section):**
  1. `help_overall` (always visible)
  2. `badls` (conditional)
  3. `iadls` (conditional)
  4. `hours_per_day` (always visible)
  5. `primary_support` (always visible)

---

### 2. `logic.json` (NEW)

**Purpose:** Defines the scoring engine, flag mappings, decision thresholds, and messages.

**Structure:**
```json
{
  "logic": {
    "aggregate_method": "sum",
    "scoring": { ... },
    "flag_to_category_mapping": { ... },
    "decision_thresholds": { ... },
    "flags": {
      "flag_name": {
        "trigger": "condition",
        "priority": "high|medium|low",
        "message": "Human-readable message"
      }
    }
  }
}
```

**Key Features:**
- **28 Flags Defined** with priorities and messages
- **High-Priority Flags with Messages:**
  - `emo_concern`: Emotional well-being discussion
  - `veteran_aanda_risk`: VA Aid & Attendance qualification
  - `caregiver_burnout`: Unsustainable family caregiver burden
  - `medication_risk`: Complex meds in remote location
  - `cognition_risk_severe`: Severe cognitive issues need memory care
  - `fall_risk`: Multiple falls with limited mobility
  - `isolation_risk`: Isolation with no support
  - `safety_risk`: Critical ADL needs with behaviors
  - `mobility_support_risk`: Limited mobility with no support
  - `medication_adherence_risk`: Complex meds with management issues
  - `cognitive_safety_risk`: Moderate/severe cognition with minimal support

---

### 3. `logic.py` (MODIFIED)

**Updated Function:** `_generate_summary_points()`

**New Behavior:**
- Accepts `flag_messages` parameter (list of high-priority messages)
- Renders flag messages **at the top** of results, above standard summary
- Standard summary now shows:
  ```
  Independence snapshot: {badls or help_overall} [+ iadls]
  Cognitive notes: {memory_changes} [; behaviors: {behaviors}]
  Medication complexity: {meds_complexity}
  Caregiver hours/day: {hours_per_day}
  Location/access: {isolation}
  ```

**Updated Function:** `derive()`

**New Behavior:**
- Extracts high-priority flag messages after flag evaluation
- Passes messages to `_generate_summary_points()` for rendering
- Messages appear in results **before** standard summary bullets

**Example Results Output:**
```
It might help to discuss emotional well-being with a professional...
Severe cognitive issues require significant supervision...

Independence snapshot: Regular – needs daily assistance
Cognitive notes: Moderate memory or thinking issues
Medication complexity: Moderate – daily meds, some complexity
Caregiver hours/day: Less than 1 hour
Location/access: Somewhat isolated
```

---

## Flag System Architecture

### Flag Categories (for scoring):
- `care_burden` - Daily living needs, mobility, ADL/IADL dependencies
- `social_isolation` - Mood, emotional support
- `mental_health_concern` - Depression, low mood, emotional risks
- `home_safety` - Falls, behaviors, safety concerns
- `geographic_access` - Isolation, location barriers
- `cognitive_function` - Memory, cognition, dementia risk
- `health_management` - Chronic conditions, medication complexity
- `caregiver_support` - Support hours, caregiver burnout

### Priority Levels:
- **High:** Urgent safety or care concerns requiring immediate attention
- **Medium:** Moderate concerns that affect care planning
- **Low:** Minor concerns for monitoring

---

## Care Recommendations (unchanged):
1. **Stay Home** - Independent, no support needed
2. **In-Home Care** - Support at home with assistance
3. **Assisted Living** - Community-based living with care
4. **Memory Care** - Specialized cognitive support
5. **Memory Care (High Acuity)** - Advanced cognitive/behavioral needs

---

## Testing Recommendations

### 1. **Conditional Visibility Testing**
- Test that BADL/IADL questions only appear when conditions met
- Verify questions hide when conditions not met

### 2. **Flag Setting Testing**
- Verify each answer option sets correct flags
- Check multi-select fields set flags for each selection
- Test regex pattern matching for additional_conditions

### 3. **Message Rendering Testing**
- Verify high-priority messages appear at top of results
- Test multiple messages display correctly
- Ensure messages don't duplicate standard summary

### 4. **Scoring Engine Testing**
- Verify flags map to correct categories
- Test decision threshold logic
- Validate care recommendations match expectations

---

## Migration Notes

**Old Module:** `module.json.OLD` (preserved for reference)  
**New Module:** `module.json` (active)  
**Logic File:** `logic.json` (new, defines scoring engine)  
**Python Logic:** `logic.py` (updated to support messages)

**Backward Compatibility:**
- `logic.py` still uses OLD manifest for `derive()` function
- `derive_outcome()` loads `module.json.OLD` for scoring
- New module.json is for UI/question flow only
- Scoring logic unchanged (maintains compatibility)

---

## Files Summary

```
products/gcp/modules/care_recommendation/
├── module.json              # NEW - Updated questions, flags, conditional visibility
├── module.json.OLD          # Preserved for scoring logic reference
├── logic.json               # NEW - Scoring rules, flags, messages
└── logic.py                 # MODIFIED - Message rendering support
```

All files validated:
- ✅ `module.json` - Valid JSON
- ✅ `logic.json` - Valid JSON  
- ✅ `logic.py` - Compiles successfully

---

## Next Steps

1. **Await scoring engine update** (user mentioned coming next)
2. **Update `logic.py` to use new logic.json** (if needed for scoring)
3. **Test complete GCP flow** with new questions and flags
4. **Verify Cost Planner** recognizes new flags
5. **Test message rendering** on results page

