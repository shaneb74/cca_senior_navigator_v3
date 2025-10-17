# Cost Planner Assessment Refactor - Phase 2 Implementation Plan

**Branch:** `cp-refactor`  
**Status:** Phase 1 Complete ✅ → Starting Phase 2  
**Date:** October 16, 2025

---

## 🎯 Phase 2 Objectives

Populate all 6 assessment stub configs with full field definitions, calculations, and conditional logic from the existing `cost_planner_v2_modules.json`.

---

## 📋 Source Material

**File:** `config/cost_planner_v2/cost_planner_v2_modules.json`

This file contains the complete field definitions for all financial assessments:
- Income sections (Social Security, Pension, Employment, Investment, Other)
- Assets sections (Liquid, Retirement, Real Estate, Life Insurance)
- VA Benefits sections
- Health Insurance sections (Medicare, Medicaid, Supplemental)
- Life Insurance sections
- Medicaid Planning sections

---

## 🏗️ Implementation Strategy

### Step 1: Income Assessment (income.json)
**Sections to add:**
1. ✅ Intro (already exists)
2. 🔄 Social Security Benefits (expand from stub)
3. ➕ Pension Income
4. ➕ Employment Income
5. ➕ Investment Income
6. ➕ Other Income Sources
7. ✅ Results (already exists)

**Summary calculation:** Sum all income sources for total monthly income

**Estimated time:** 15-20 minutes

---

### Step 2: Assets Assessment (assets.json)
**Sections to add:**
1. ✅ Intro (already exists)
2. 🔄 Liquid Assets (expand from stub)
3. ➕ Retirement Accounts
4. ➕ Real Estate
5. ➕ Life Insurance Cash Value
6. ✅ Results (already exists)

**Layout:** Two-column layout for all field sections (already configured)

**Summary calculation:** Sum all asset categories for total assets

**Estimated time:** 15-20 minutes

---

### Step 3: VA Benefits Assessment (va_benefits.json)
**Sections to add:**
1. ✅ Intro (already exists)
2. 🔄 VA Status (expand from stub)
3. ➕ Monthly VA Benefits
4. ➕ Aid & Attendance
5. ➕ Special Programs
6. ✅ Results (already exists)

**Conditional visibility:** Only visible if `is_veteran` flag is true

**Summary calculation:** Sum VA benefit amounts

**Estimated time:** 10-15 minutes

---

### Step 4: Health Insurance Assessment (health_insurance.json)
**Sections to add:**
1. ✅ Intro (already exists)
2. 🔄 Medicare Coverage (expand from stub)
3. ➕ Medicare Part Details (A, B, D)
4. ➕ Medicare Supplement
5. ➕ Medicaid Enrollment
6. ➕ Other Coverage
7. ✅ Results (already exists)

**Summary:** Text-based summary of coverage status

**Estimated time:** 15-20 minutes

---

### Step 5: Life Insurance Assessment (life_insurance.json)
**Sections to add:**
1. ✅ Intro (already exists)
2. 🔄 Life Insurance Policies (expand from stub)
3. ➕ Policy Details (type, face value, cash value)
4. ➕ Annuities
5. ➕ Long-Term Care Insurance
6. ✅ Results (already exists)

**Summary calculation:** Sum total face value and cash value

**Estimated time:** 10-15 minutes

---

### Step 6: Medicaid Planning Assessment (medicaid_navigation.json)
**Sections to add:**
1. ✅ Intro (already exists)
2. 🔄 Medicaid Status (expand from stub)
3. ➕ Asset Limits & Eligibility
4. ➕ Spend-Down Strategies
5. ➕ Estate Planning Considerations
6. ✅ Results (already exists)

**Conditional visibility:** Only visible if `medicaid_eligible` flag is true

**Summary:** Text-based eligibility summary

**Estimated time:** 10-15 minutes

---

## 📊 Field Type Mapping

| Module JSON Type | Assessment Engine Type | Widget |
|-----------------|----------------------|--------|
| `number` | `currency` | number_input |
| `select` | `select` | selectbox |
| `multiselect` | `multiselect` | multiselect |
| `checkbox` | `checkbox` | checkbox |
| `text` | `text` | text_input |
| `date` | `date` | date_input |

---

## 🔧 Additional Features to Add

### Info Boxes
Add contextual guidance from module JSON:
```json
{
  "info_boxes": [
    {
      "type": "info",
      "message": "Social Security benefits are adjusted annually for cost of living."
    }
  ]
}
```

### Conditional Visibility
Implement field-level `visible_if` logic:
```json
{
  "key": "pension_amount",
  "visible_if": {
    "field": "has_pension",
    "equals": "yes"
  }
}
```

### Calculations
Implement formula evaluation:
```json
{
  "summary": {
    "type": "calculated",
    "label": "Total Monthly Income",
    "formula": "sum(ss_monthly, pension_monthly, employment_monthly, investment_monthly, other_monthly)",
    "display_format": "${:,.0f}/month"
  }
}
```

---

## ✅ Success Criteria

**Phase 2 Complete When:**
- [ ] All 6 assessments have full section definitions
- [ ] All fields migrated from cost_planner_v2_modules.json
- [ ] Summary calculations work correctly
- [ ] Conditional visibility logic works
- [ ] Info boxes display contextual guidance
- [ ] Two-column layouts render properly
- [ ] Required field validation works
- [ ] State persistence works across all fields
- [ ] Progress tracking reflects actual completion
- [ ] End-to-end testing passes for all assessments

---

## 🚀 Implementation Order

1. **Income** (most complex, sets pattern)
2. **Assets** (second most complex, tests two-column layout)
3. **Health Insurance** (medium complexity)
4. **Life Insurance** (medium complexity)
5. **VA Benefits** (conditional visibility testing)
6. **Medicaid Planning** (conditional visibility testing)

---

## 📝 Testing Checklist (Per Assessment)

- [ ] All sections render correctly
- [ ] All field types display properly
- [ ] Required fields validated
- [ ] Conditional fields show/hide correctly
- [ ] Summary calculations accurate
- [ ] Info boxes appear in right places
- [ ] Two-column layout works (if applicable)
- [ ] State persists across navigation
- [ ] Results page shows all data
- [ ] Progress tracking accurate

---

## 🔗 Next Steps After Phase 2

**Phase 3: Integration**
- Connect assessments to expert_review.py
- Publish FinancialProfile to MCIP
- Add care flag modifiers (fall_risk, emotional_followup)
- Implement expert review formulas

**Phase 4: Cleanup**
- Delete legacy files (hub.py, modules/*.py)
- Update documentation
- Full end-to-end testing
- Merge to main branch

---

**Estimated Total Time:** 90-120 minutes  
**Target Completion:** Today (October 16, 2025)
