# GCP Module Section Order Fix

## Issue Resolved
**Problem:** Daily Living section was appearing BEFORE Cognition & Mental Health section in the UI, preventing cognitive flags from being set before BADL/IADL conditional visibility logic evaluated.

**Impact:** BADL/IADL questions could not properly check for `memory_changes` flag in their `visible_if` conditions since cognitive questions hadn't been answered yet.

---

## Root Cause

The conditional visibility logic for BADL/IADL questions includes:
```json
"visible_if": {
  "any": [
    { "eq": ["memory_changes", ["occasional", "moderate", "severe"]] }
    // ... other conditions
  ]
}
```

If Daily Living section appears BEFORE Cognition section:
- ❌ `memory_changes` question hasn't been asked yet
- ❌ Cognitive flags haven't been set
- ❌ BADL/IADL questions can't evaluate memory-based visibility
- ❌ Only non-cognitive triggers (age, mobility, falls) would work

---

## Solution Implemented

### 1. Created Fresh module.json
- Backed up existing file with timestamp: `module.json.backup_YYYYMMDD_HHMMSS`
- Created new file from user's exact specification
- Ensured strict section ordering

### 2. Verified Section Order

**Correct Order (as required):**
```
1. intro                    - Welcome to the Guided Care Plan
2. about_you               - About You
3. medication_mobility     - Medication & Mobility
4. cognition_mental_health - Cognition & Mental Health  ← BEFORE Daily Living
5. daily_living            - Daily Living                ← AFTER Cognition
6. results                 - Your Guided Care Plan Summary
```

### 3. Flow Logic Verification

**Question Flow with Flags:**

**Step 1: Cognition & Mental Health Section**
- Q: `memory_changes` → Sets flags:
  - `mild_cognitive_decline` (occasional)
  - `moderate_cognitive_decline` (moderate)
  - `severe_cognitive_risk` (severe)
- Q: `behaviors` (conditional on moderate/severe memory)
- Q: `mood` → Sets flags: `moderate_risk`, `high_risk`, `mental_health_concern`

**Step 2: Daily Living Section** (cognitive flags NOW available)
- Q: `help_overall` → Always shown
- Q: `badls` → Conditional visibility can NOW check:
  ```json
  { "eq": ["memory_changes", ["occasional", "moderate", "severe"]] }
  ```
  ✅ `memory_changes` value exists and can be evaluated
  
- Q: `iadls` → Same conditional logic as badls
- Q: `hours_per_day` → Always shown
- Q: `primary_support` → Always shown

---

## BADL/IADL Conditional Visibility Logic

Both questions appear when **ANY** condition is true:

### 9 Trigger Conditions

1. **Age-Based:** `{ "eq": ["age_range", "85_plus"] }`
2. **Living Situation:** `{ "eq": ["living_situation", "alone"] }`
3. **Geographic Isolation:** `{ "eq": ["isolation", "very"] }`
4. **Mobility Impairment:** `{ "eq": ["mobility", ["wheelchair", "bedbound"]] }`
5. **Fall Risk:** `{ "eq": ["falls", "multiple"] }`
6. **Cognitive Risk:** `{ "eq": ["memory_changes", ["occasional", "moderate", "severe"]] }` ⭐
7. **Neurological Conditions:** `{ "contains": ["chronic_conditions", ["parkinsons", "stroke"]] }`
8. **High Chronic Burden:** `{ "length_gte": ["chronic_conditions", 3] }`
9. **Additional Conditions:** `{ "length_gte": ["additional_conditions", 3] }`

**⭐ Critical:** Condition #6 requires `memory_changes` to be answered FIRST, which is why Cognition section MUST come before Daily Living.

---

## Testing Requirements

### Test Case 1: Cognitive Trigger
**Setup:**
1. Start fresh GCP assessment
2. Complete About You section
3. Complete Medication & Mobility section
4. **Cognition Section:** Answer `memory_changes` = "Occasional forgetfulness"
5. Complete mood question
6. Proceed to Daily Living section

**Expected Result:**
- ✅ BADL question appears (triggered by memory_changes = "occasional")
- ✅ IADL question appears (triggered by memory_changes = "occasional")
- ✅ Can select BADL/IADL options
- ✅ `veteran_aanda_risk` flag set when any BADL/IADL selected

**Previous Behavior (BROKEN):**
- ❌ Daily Living appeared before Cognition
- ❌ `memory_changes` wasn't answered yet
- ❌ BADL/IADL trigger condition failed to evaluate
- ❌ Questions didn't appear for cognitive risk users

---

### Test Case 2: Multiple Memory Levels

Test each memory level triggers BADL/IADL:

**A. Occasional Forgetfulness:**
- Answer: memory_changes = "occasional"
- Expected: BADL/IADL appear ✅

**B. Moderate Memory Issues:**
- Answer: memory_changes = "moderate"
- Expected: BADL/IADL appear ✅
- Expected: `behaviors` question also appears ✅

**C. Severe Memory / Dementia:**
- Answer: memory_changes = "severe"
- Expected: BADL/IADL appear ✅
- Expected: `behaviors` question also appears ✅

**D. No Concerns:**
- Answer: memory_changes = "no_concerns"
- Expected: BADL/IADL do NOT appear (unless other triggers met) ✅

---

### Test Case 3: Non-Cognitive Triggers Still Work

Verify other 8 triggers work independently:

**Setup:** Answer memory_changes = "no_concerns" (no cognitive trigger)

**Then test each:**
- Age 85+ → BADL/IADL appear ✅
- Living alone → BADL/IADL appear ✅
- Very isolated → BADL/IADL appear ✅
- Wheelchair/bedbound → BADL/IADL appear ✅
- Multiple falls → BADL/IADL appear ✅
- Parkinson's/stroke → BADL/IADL appear ✅
- 3+ chronic conditions → BADL/IADL appear ✅
- 3+ additional conditions → BADL/IADL appear ✅

---

## Files Changed

### Primary Change
**File:** `products/gcp/modules/care_recommendation/module.json`  
**Action:** Complete recreation with correct section ordering  
**Backup:** `products/gcp/modules/care_recommendation/module.json.backup_YYYYMMDD_HHMMSS`

### Verification
```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('products/gcp/modules/care_recommendation/module.json')); print('✅ Valid JSON')"

# Verify section order
python3 -c "
import json
with open('products/gcp/modules/care_recommendation/module.json', 'r') as f:
    data = json.load(f)
    sections = data['sections']
    print('Section Order:')
    for i, section in enumerate(sections, 1):
        print(f'{i}. {section[\"id\"]} - {section.get(\"title\", \"N/A\")}')"
```

### Output
```
✅ Valid JSON

Section Order:
1. intro - Welcome to the Guided Care Plan
2. about_you - About You
3. medication_mobility - Medication & Mobility
4. cognition_mental_health - Cognition & Mental Health
5. daily_living - Daily Living
6. results - Your Guided Care Plan Summary
```

---

## Architecture Notes

### Why Order Matters

**Conditional Visibility Evaluation:**
The module engine evaluates `visible_if` conditions using the current state of answered questions. If a condition references a question that hasn't been answered yet:
- Value is `undefined` or empty
- Equality checks fail
- Conditional questions don't appear

**Flag-Based vs Value-Based Conditions:**
- **Value-based:** `{ "eq": ["memory_changes", "severe"] }` - checks answer VALUE
- **Flag-based:** Would check if flag exists in state

BADL/IADL use **value-based** conditions, so they need the actual answer value from `memory_changes` question.

### Session State Flow

1. User answers `memory_changes` in Cognition section
2. Answer stored: `state["answers"]["memory_changes"] = "occasional"`
3. Field flag set: `state["flags"]["mild_cognitive_decline"] = True`
4. User proceeds to Daily Living section
5. Module engine evaluates BADL `visible_if` condition:
   ```python
   if state["answers"]["memory_changes"] in ["occasional", "moderate", "severe"]:
       show_badls = True
   ```
6. ✅ BADL question appears
7. User selects BADL option (e.g., "Bathing/Showering")
8. Flags set: `veteran_aanda_risk = True`, `moderate_dependence = True`

---

## Integration Impact

### Downstream Systems Affected

**1. Additional Services** (`core/additional_services.py`)
- Reads flags from `handoff["gcp"]["flags"]`
- Services that check cognitive + BADL flags:
  - Memory Care: `cognitive_risk` AND (`moderate_dependence` OR `high_dependence`)
  - VA Benefits: `veteran_aanda_risk` (requires BADL/IADL selection)

**2. Cost Planner** (`products/cost_planner/cost_estimate_v2.py`)
- Reads `handoff["gcp"]["recommendation"]`
- Recommendation influenced by dependency flags from BADL/IADL

**3. FAQ/AI Advisor** (`pages/faq.py`)
- Filters questions based on flags
- Cognitive + veteran questions require both flag sets

**4. MCIP Panel** (Concierge Hub)
- Displays recommendations with nudges
- Combination of cognitive + dependency flags creates targeted messaging

---

## Rollback Procedure

If issues occur, restore previous version:

```bash
# List backups
ls -la products/gcp/modules/care_recommendation/module.json.backup_*

# Restore specific backup
cp products/gcp/modules/care_recommendation/module.json.backup_YYYYMMDD_HHMMSS \
   products/gcp/modules/care_recommendation/module.json

# Restart Streamlit
pkill -f "streamlit" && sleep 2 && streamlit run app.py
```

---

## Deployment Checklist

- [x] Created backup of existing module.json
- [x] Created new module.json with correct section order
- [x] Validated JSON syntax
- [x] Verified section order programmatically
- [x] Restarted Streamlit application
- [ ] **MANUAL TESTING REQUIRED:**
  - [ ] Test cognitive trigger for BADL/IADL
  - [ ] Test all 9 trigger conditions
  - [ ] Verify veteran_aanda_risk flag setting
  - [ ] Check VA Benefits Module appears in hub
  - [ ] Verify flag integration across all products

---

## Related Documentation

- [GCP Question Order Verification](./GCP_QUESTION_ORDER_VERIFICATION.md) - Complete question structure
- [GCP Flag Integration Verification](./GCP_FLAG_INTEGRATION_VERIFICATION.md) - Complete flag system
- [FAQ Handoff Integration Fix](./FAQ_HANDOFF_INTEGRATION_FIX.md) - Context-aware questions

---

**Fixed:** October 13, 2025  
**Priority:** CRITICAL - Enables cognitive-based BADL/IADL visibility logic  
**Status:** DEPLOYED - Requires manual testing verification

