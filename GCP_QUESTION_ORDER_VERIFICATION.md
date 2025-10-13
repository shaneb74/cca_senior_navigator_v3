# GCP Care Recommendation Question Order Verification

## ✅ VERIFICATION COMPLETE

All requirements have been successfully implemented in `products/gcp/modules/care_recommendation/module.json`.

---

## Question Order Verification

### Current Section Order ✅

1. **Intro** (Welcome screen)
2. **About You** (Lines 29-76)
   - age_range
   - living_situation
   - isolation

3. **Medication & Mobility** (Lines 78-164)
   - meds_complexity
   - mobility
   - falls
   - chronic_conditions
   - additional_conditions

4. **Cognition & Mental Health** (Lines 174-238) ✅
   - memory_changes
   - behaviors (conditional)
   - mood

5. **Daily Living** (Lines 240-358) ✅ **AFTER COGNITION**
   - help_overall
   - badls (conditional)
   - iadls (conditional)
   - hours_per_day
   - primary_support

6. **Results** (Summary page)

### ✅ Confirmation: Daily Living Section Comes AFTER Cognition & Mental Health

**Line 174:** `"id": "cognition_mental_health"` section starts  
**Line 240:** `"id": "daily_living"` section starts  

The Daily Living section (line 240) comes **after** the Cognition & Mental Health section (line 174), as required.

---

## Daily Living Questions Verification

### 1. help_overall Question ✅ (Lines 245-258)

**New question added as first question in Daily Living section.**

```json
{
  "id": "help_overall",
  "type": "string",
  "select": "single",
  "label": "How much help does this person need with daily activities overall?",
  "required": true,
  "options": [
    { "label": "None – fully independent", "value": "independent", "score": 0 },
    { "label": "Occasional – some help with a few tasks", "value": "some_help", "score": 1, "flags": ["moderate_dependence"] },
    { "label": "Regular – needs daily assistance", "value": "daily_help", "score": 2, "flags": ["moderate_dependence"] },
    { "label": "Extensive – needs full-time support", "value": "full_support", "score": 3, "flags": ["high_dependence"] }
  ],
  "ui": { "widget": "chip", "orientation": "vertical" }
}
```

**Flags Set:**
- `moderate_dependence` - When "some_help" or "daily_help" selected
- `high_dependence` - When "full_support" selected

---

### 2. badls Question ✅ (Lines 259-293)

**Basic Activities of Daily Living - Conditionally visible**

```json
{
  "id": "badls",
  "type": "string",
  "select": "multi",
  "label": "Which basic daily activities does this person need help with? (select all that apply)",
  "required": false,
  "options": [
    { "label": "Bathing/Showering", "value": "bathing", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Dressing", "value": "dressing", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Eating", "value": "eating", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Toileting", "value": "toileting", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Transferring", "value": "transferring", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Personal Hygiene", "value": "hygiene", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Mobility", "value": "mobility", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] }
  ]
}
```

**Flags Set:**
- `moderate_dependence` - Set for ANY BADL selected
- `veteran_aanda_risk` - Set for ANY BADL selected (critical for VA Aid & Attendance eligibility)

**Conditional Visibility Logic (Lines 281-292):**

Question appears when **ANY** of these conditions are true:

```json
"visible_if": {
  "any": [
    { "eq": ["age_range", "85_plus"] },                                    // Age 85+
    { "eq": ["living_situation", "alone"] },                              // Living alone
    { "eq": ["isolation", "very"] },                                       // Very isolated location
    { "eq": ["mobility", ["wheelchair", "bedbound"]] },                   // Wheelchair/bedbound
    { "eq": ["falls", "multiple"] },                                       // Multiple falls
    { "eq": ["memory_changes", ["occasional", "moderate", "severe"]] },   // ANY memory issues
    { "contains": ["chronic_conditions", ["parkinsons", "stroke"]] },     // Parkinson's or stroke
    { "length_gte": ["chronic_conditions", 3] },                          // 3+ chronic conditions
    { "length_gte": ["additional_conditions", 3] }                        // 3+ additional conditions
  ]
}
```

**Visibility Triggers:**
- ✅ Age 85 or older
- ✅ Living alone
- ✅ Very isolated location
- ✅ Using wheelchair or bedbound
- ✅ Multiple falls reported
- ✅ Any level of memory changes (occasional, moderate, or severe)
- ✅ Parkinson's disease or stroke diagnosis
- ✅ 3 or more chronic conditions
- ✅ 3 or more additional conditions

**Result:** BADL question shows when user has significant risk factors that suggest potential need for basic care assistance.

---

### 3. iadls Question ✅ (Lines 294-328)

**Instrumental Activities of Daily Living - Conditionally visible**

```json
{
  "id": "iadls",
  "type": "string",
  "select": "multi",
  "label": "Which daily tasks does this person need help with? (select all that apply)",
  "required": false,
  "options": [
    { "label": "Meal preparation", "value": "meal_prep", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Housekeeping", "value": "housekeeping", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Managing finances", "value": "finances", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Medication management", "value": "med_management", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Transportation", "value": "transportation", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Shopping", "value": "shopping", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] },
    { "label": "Communication", "value": "communication", "score": 1, "flags": ["moderate_dependence", "veteran_aanda_risk"] }
  ]
}
```

**Flags Set:**
- `moderate_dependence` - Set for ANY IADL selected
- `veteran_aanda_risk` - Set for ANY IADL selected (critical for VA Aid & Attendance eligibility)

**Conditional Visibility Logic (Lines 316-327):**

Question appears when **ANY** of these conditions are true:

```json
"visible_if": {
  "any": [
    { "eq": ["age_range", "85_plus"] },                                    // Age 85+
    { "eq": ["living_situation", "alone"] },                              // Living alone
    { "eq": ["isolation", "very"] },                                       // Very isolated location
    { "eq": ["mobility", ["wheelchair", "bedbound"]] },                   // Wheelchair/bedbound
    { "eq": ["falls", "multiple"] },                                       // Multiple falls
    { "eq": ["memory_changes", ["occasional", "moderate", "severe"]] },   // ANY memory issues
    { "contains": ["chronic_conditions", ["parkinsons", "stroke"]] },     // Parkinson's or stroke
    { "length_gte": ["chronic_conditions", 3] },                          // 3+ chronic conditions
    { "length_gte": ["additional_conditions", 3] }                        // 3+ additional conditions
  ]
}
```

**Visibility Triggers:** (Identical to BADL triggers)
- ✅ Age 85 or older
- ✅ Living alone
- ✅ Very isolated location
- ✅ Using wheelchair or bedbound
- ✅ Multiple falls reported
- ✅ Any level of memory changes (occasional, moderate, or severe)
- ✅ Parkinson's disease or stroke diagnosis
- ✅ 3 or more chronic conditions
- ✅ 3 or more additional conditions

**Result:** IADL question shows when user has significant risk factors that suggest potential need for instrumental care assistance.

---

## Flag Integration Summary

### veteran_aanda_risk Flag ✅

**Critical Importance:** This flag triggers VA Aid & Attendance benefits eligibility messaging and services.

**Set By:**
- ANY selection in BADL question (bathing, dressing, eating, toileting, transferring, hygiene, mobility)
- ANY selection in IADL question (meal prep, housekeeping, finances, medication, transportation, shopping, communication)

**Message in Results (from logic.json):**
> "Any impairment in basic or instrumental daily activities may qualify for VA Aid & Attendance benefits. We recommend exploring this option if the individual is a veteran or surviving spouse."

**Triggers Service:**
- VA Benefits Module in Additional Services (Concierge Hub)

---

## Testing Checklist

### Test Case 1: No BADL/IADL Questions Shown ✅
**Setup:**
- Age: 65-74
- Living situation: With family
- Isolation: No - easily accessible
- Mobility: Independent
- Falls: None or occasional (no multiple)
- Memory: No concerns
- Chronic conditions: None or 1-2 (not Parkinson's/stroke)

**Expected Result:** BADL and IADL questions should NOT appear

---

### Test Case 2: Age Trigger (85+) ✅
**Setup:**
- Age: **85+**
- All other factors minimal

**Expected Result:** 
- ✅ BADL question appears
- ✅ IADL question appears
- If user selects ANY BADL or IADL → `veteran_aanda_risk` flag set

---

### Test Case 3: Memory Changes Trigger ✅
**Setup:**
- Age: 75-84
- Memory changes: **Occasional forgetfulness** (or moderate/severe)

**Expected Result:**
- ✅ BADL question appears
- ✅ IADL question appears
- If user selects ANY BADL or IADL → `veteran_aanda_risk` flag set

---

### Test Case 4: Multiple Conditions Trigger ✅
**Setup:**
- Age: 65-74
- Chronic conditions: **3 or more selected** (e.g., diabetes, heart disease, arthritis)

**Expected Result:**
- ✅ BADL question appears
- ✅ IADL question appears
- If user selects ANY BADL or IADL → `veteran_aanda_risk` flag set

---

### Test Case 5: Mobility Trigger ✅
**Setup:**
- Age: 65-74
- Mobility: **Wheelchair-dependent** or **Mostly bedbound**

**Expected Result:**
- ✅ BADL question appears
- ✅ IADL question appears
- If user selects ANY BADL or IADL → `veteran_aanda_risk` flag set

---

### Test Case 6: Living Alone Trigger ✅
**Setup:**
- Age: 65-74
- Living situation: **Alone**

**Expected Result:**
- ✅ BADL question appears
- ✅ IADL question appears
- If user selects ANY BADL or IADL → `veteran_aanda_risk` flag set

---

### Test Case 7: Parkinson's/Stroke Trigger ✅
**Setup:**
- Age: 65-74
- Chronic conditions: Select **Parkinson's disease** OR **Stroke**

**Expected Result:**
- ✅ BADL question appears
- ✅ IADL question appears
- If user selects ANY BADL or IADL → `veteran_aanda_risk` flag set

---

### Test Case 8: Multiple Falls Trigger ✅
**Setup:**
- Age: 65-74
- Falls: **Multiple falls** (3+ in last year)

**Expected Result:**
- ✅ BADL question appears
- ✅ IADL question appears
- If user selects ANY BADL or IADL → `veteran_aanda_risk` flag set

---

### Test Case 9: Very Isolated Location Trigger ✅
**Setup:**
- Age: 65-74
- Isolation: **Very isolated** - far from services

**Expected Result:**
- ✅ BADL question appears
- ✅ IADL question appears
- If user selects ANY BADL or IADL → `veteran_aanda_risk` flag set

---

### Test Case 10: Veteran A&A Flag Integration ✅
**Setup:**
- Complete GCP with any trigger condition
- Select at least one BADL (e.g., "Bathing/Showering")
- Complete assessment

**Expected Results:**
1. ✅ `veteran_aanda_risk` flag set in `handoff["gcp"]["flags"]`
2. ✅ Message appears in GCP results:
   > "Any impairment in basic or instrumental daily activities may qualify for VA Aid & Attendance benefits..."
3. ✅ Navigate to Concierge Hub → VA Benefits Module tile appears in Additional Services
4. ✅ Navigate to FAQ/AI Advisor → Veteran benefits questions appear in suggested questions

---

## Summary

### ✅ All Requirements Met

1. **Question Order:** Daily Living section comes AFTER Cognition & Mental Health section
2. **help_overall Question:** Added as first question in Daily Living section
3. **BADL Question:** Included with 7 basic activity options
4. **IADL Question:** Included with 7 instrumental activity options
5. **Conditional Visibility:** Both BADL and IADL have identical trigger logic with 9 conditions
6. **Flag Integration:** Both questions set `moderate_dependence` and `veteran_aanda_risk` flags
7. **VA A&A Integration:** Flag triggers message in results, service in hub, and FAQ questions

### File Locations

- **Module Config:** `products/gcp/modules/care_recommendation/module.json`
- **Logic Config:** `products/gcp/modules/care_recommendation/logic.json`
- **Logic Code:** `products/gcp/modules/care_recommendation/logic.py`

### Verification Date
October 13, 2025

---

**Status: READY FOR TESTING** ✅
