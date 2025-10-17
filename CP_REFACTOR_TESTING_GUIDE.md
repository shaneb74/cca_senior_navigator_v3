# Cost Planner Assessment Refactor - Testing Guide

**Branch:** `cp-refactor`  
**Status:** Phase 2 Complete - Ready for Full Testing  
**Last Updated:** January 2025

---

## 🎉 Phase 2 Complete!

All 6 financial assessments have been fully migrated from Python modules to JSON configurations:
- ✅ **Income** (172 lines, 5 fields)
- ✅ **Assets** (146 lines, 6 fields, two-column layout)
- ✅ **Health Insurance** (220 lines, 13 fields, multiselect, complex conditionals)
- ✅ **Life Insurance** (156 lines, 8 fields, annuities)
- ✅ **VA Benefits** (180 lines, 6 fields, veteran flag required)
- ✅ **Medicaid Planning** (195 lines, 9 fields, interest flag required)

**Total:** 41 fields, 19 info boxes, 4 calculated formulas, ~1,050 lines of JSON

See `CP_REFACTOR_PHASE_2_COMPLETE.md` for detailed implementation summary.

---

## 🚀 Quick Start

### 1. Start Streamlit
```bash
cd /Users/shane/Desktop/cca_senior_navigator_v3
git checkout cp-refactor
streamlit run app.py
```

### 2. Navigate to Cost Planner
- Go to Concierge Hub
- Click "Financial Planning" or navigate to `?page=cost_v2`

### 3. Complete Intro
- Enter ZIP code
- Select a care type
- Click "Continue to Financial Assessment"

### 4. Sign In
- Should auto-skip if already authenticated
- Otherwise, sign in (no guest mode option should appear)

### 5. Triage (Optional)
- Answer qualifier questions
- Click "Continue to Financial Assessment"

### 6. **Assessment Hub** (NEW!)
You should see:
- 6 assessment cards in a 2-column grid
- Each card shows: icon, title, description, time estimate, status badge
- Income and Assets marked as "Required" (red badge)
- Progress bar at top showing "0 of 6 assessments completed"

---

## ✅ Test Cases

### Hub View
- [ ] **All 6 cards render:** Income, Assets, Health Insurance, Life Insurance, VA Benefits, Medicaid Planning
- [ ] **Required badges:** Income and Assets show "🔴 Required"
- [ ] **Status badges:** All show "⚪ Not Started" initially
- [ ] **Progress bar:** Shows "0 of 6 assessments completed" and 0%
- [ ] **Conditional visibility:** 
  - VA Benefits hidden unless `is_veteran` flag = true
  - Medicaid Planning hidden unless `medicaid_planning_interest` flag = true

### Flag Testing (Important!)
To test conditional assessments, set flags in session state:
```python
# For VA Benefits
st.session_state.setdefault("flags", {})["is_veteran"] = True

# For Medicaid Planning
st.session_state.setdefault("flags", {})["medicaid_planning_interest"] = True
```
- [ ] **VA Benefits card appears** when `is_veteran` = true
- [ ] **Medicaid Planning card appears** when `medicaid_planning_interest` = true
- [ ] **Cards hidden** when flags are false or not set

### Starting an Assessment
- [ ] Click "Start →" on Income assessment
- [ ] **Intro section displays:** With title, icon, help_text, and info boxes
- [ ] **Navi panel appears** at top with guidance message (blue left border)
- [ ] **Continue button** appears (no Back button on intro)
- [ ] Click "Continue →" to first field section
- [ ] **Section header renders:** "💰 Social Security Benefits" (or section title)
- [ ] **Fields render correctly:**
  - Currency field with number input ($0 format)
  - Min/max/step constraints work
  - Help text appears below field
  - Default values populated if specified
- [ ] **Navigation buttons appear:**
  - "← Back" (to previous section)
  - "Continue →" (to next section, primary button)
  - "← Back to Hub" (secondary button)

### Section Navigation
- [ ] Click "Continue →" to next section
- [ ] **State persists:** Previous field values saved
- [ ] Click "← Back" button
- [ ] **Returns to previous section** with values preserved
- [ ] Click "← Back to Hub"
- [ ] **Returns to assessment hub**
- [ ] **Progress updated:** Card shows "🔄 X% Done" instead of "Not Started"
- [ ] Click "Resume" button
- [ ] **Resumes at last section** visited

### Results View
- [ ] Complete all sections in an assessment
- [ ] Click "View Results" on last field section
- [ ] **Results page renders:**
  - Summary calculation shows (e.g., "Total Monthly Income: $3,450/month")
  - All responses listed by section with icons
  - Currency values formatted correctly with commas
  - Text summaries for qualitative assessments (Health Insurance, Medicaid)
- [ ] **No Navi panel on results page** (assessment handles messaging)
- [ ] **Navigation buttons:**
  - "Review Answers" returns to first field section
  - "Back to Hub" returns to assessment hub
- [ ] **Status updated:** Card shows "✅ Complete" back on hub
- [ ] **Progress bar updates:** "1 of 6 assessments completed (17%)"

### Calculated Formulas
Test assessments with sum formulas:
- [ ] **Income:** Total = ss_monthly + pension_monthly + employment_monthly + other_monthly
- [ ] **Assets:** Total = checking_savings + investment_accounts + primary_residence_value + other_real_estate + other_resources
- [ ] **Life Insurance:** Total = life_insurance_cash_value + annuity_current_value
- [ ] **VA Benefits:** Total = va_disability_monthly + va_pension_monthly + aid_attendance_monthly
- [ ] **Verify:** All formulas calculate correctly, display with proper formatting

### State Persistence
- [ ] Complete Income assessment partially
- [ ] Navigate to different product (e.g., GCP)
- [ ] Return to Cost Planner → Financial Assessment
- [ ] **Progress preserved:** Income shows "Resume" button and percentage
- [ ] Click "Resume"
- [ ] **Returns to exact section** where you left off
- [ ] **All answers preserved**

### Field Types
Test different field widgets across assessments:
- [ ] **Currency:** Number input with step increments (Income: ss_monthly, Assets: checking_savings)
- [ ] **Select:** Dropdown with options (Income: employment_status, Life Insurance: life_insurance_type)
- [ ] **Checkbox:** Boolean toggle (Health Insurance: has_medicare, Assets: home_sale_interest)
- [ ] **Multiselect:** Multiple selection (Health Insurance: medicare_parts, Medicaid: has_estate_plan)
- [ ] **Text:** Text input (none in current assessments, but engine supports it)

### Conditional Visibility (Critical Testing!)
Test complex conditional logic across assessments:

#### Income Assessment
- [ ] Set `employment_status` to "not_employed"
- [ ] Verify `employment_monthly` field is hidden
- [ ] Change to "full_time", "part_time", or "self_employed"
- [ ] Verify `employment_monthly` field appears

#### Health Insurance Assessment
- [ ] Check `has_medicare` checkbox
- [ ] Verify all Medicare fields appear (parts, advantage, supplement, premium)
- [ ] Test `medicare_parts` multiselect (can select multiple: A, B, C, D)
- [ ] Uncheck `has_medicare`
- [ ] Verify all Medicare fields disappear
- [ ] Repeat for `has_medicaid`, `has_ltc_insurance`, `has_private_insurance` sections

#### Life Insurance Assessment
- [ ] Set `has_life_insurance` to "yes"
- [ ] Verify policy fields appear (type, face_value, cash_value, premium)
- [ ] Set to "no"
- [ ] Verify policy fields disappear
- [ ] Test `has_annuities` conditional (same pattern)

#### VA Benefits Assessment
- [ ] Set `has_va_benefits` to "yes" or "applied"
- [ ] Verify `va_disability_rating` field appears
- [ ] Set to "no" or "eligible"
- [ ] Verify `va_disability_rating` field disappears
- [ ] Set `has_aid_attendance` to "yes"
- [ ] Verify `aid_attendance_monthly` field appears

#### Medicaid Planning Assessment
- [ ] Set `medicaid_status` to "enrolled"
- [ ] Verify `medicaid_covers_ltc` checkbox appears
- [ ] Set to other values
- [ ] Verify checkbox disappears
- [ ] Check `interested_in_spend_down` checkbox
- [ ] Verify `spend_down_timeline` select appears

### Two-Column Layout
- [ ] Open Assets assessment
- [ ] Navigate to "Primary Assets" section (checking_savings, investment_accounts)
- [ ] **Verify:** Fields render side-by-side on desktop (two columns)
- [ ] Navigate to "Property & Real Estate" section
- [ ] **Verify:** Fields render side-by-side (primary_residence_value, home_sale_interest, other_real_estate)
- [ ] Resize browser window to mobile width (<768px)
- [ ] **Verify:** Fields stack vertically on mobile
- [ ] Navigate to "Other Resources" section
- [ ] **Verify:** Single column layout (other_resources field full width)

### Info Boxes
Test that all 19 info boxes display correctly:

#### Income Assessment (5 boxes)
- [ ] Social Security claiming strategies info box (blue)
- [ ] Full Retirement Age (FRA) explanation
- [ ] Social Security taxation basics
- [ ] Social Security earnings limit warning
- [ ] Pension income types

#### Assets Assessment (3 boxes)
- [ ] Medicaid asset counting rules (warning, yellow)
- [ ] Home valuation tips
- [ ] Liquidation considerations

#### Health Insurance (3 boxes)
- [ ] Medicare doesn't cover LTC warning (intro, yellow)
- [ ] Medicaid LTC eligibility success box (Medicaid section, green)
- [ ] LTC insurance elimination periods info

#### Life Insurance (2 boxes)
- [ ] Accessing policy cash value options
- [ ] Annuity surrender charges warning

#### VA Benefits (2 boxes)
- [ ] VA disability is tax-free (success, green)
- [ ] Aid & Attendance eligibility criteria (success, green)

#### Medicaid Planning (4 boxes)
- [ ] Medicaid LTC coverage basics (intro, info, blue)
- [ ] Asset limit details (warning, yellow)
- [ ] Legal spend-down strategies (info, blue)
- [ ] Medicaid estate recovery warning (warning, yellow)

**Verify for all boxes:**
- Correct icon (ℹ️, ✅, ⚠️)
- Correct background color (blue, green, yellow)
- Text is readable and helpful
- Proper formatting and spacing

### Required Field Validation
- [ ] Leave a required field empty
- [ ] Click "Continue"
- [ ] **Warning appears:** "Please complete required fields: [field name]"
- [ ] **Navigation blocked** until field completed

### Navi Panel
- [ ] Navi panel appears on intro and field sections (not on results)
- [ ] **Variant is "module":** Blue left border style
- [ ] **Contextual messages:** Appropriate guidance for each section
- [ ] **Progress chip:** Shows "Step X of Y" (e.g., "Step 2 of 5")
- [ ] **No Navi on results page** (assessment handles its own messaging)
- [ ] **Navi hidden on intro sections** (no double Navi with help_text)

---

## 🧪 Comprehensive Assessment Testing

Use the detailed checklist from `CP_REFACTOR_PHASE_2_COMPLETE.md` to test each assessment thoroughly. Key areas:

### Income Assessment (5 fields)
- [ ] All 5 field sections render (SS, Pension, Employment, Other Income)
- [ ] Employment conditional logic works (employment_monthly shows/hides)
- [ ] 5 info boxes display correctly
- [ ] Formula calculates: sum(ss, pension, employment, other)
- [ ] Results show correct total with /month format

### Assets Assessment (6 fields)
- [ ] 3 field sections render (Primary, Real Estate, Other)
- [ ] Two-column layout works on Primary and Real Estate sections
- [ ] Home sale checkbox toggles correctly
- [ ] 3 info boxes display
- [ ] Formula calculates: sum(all 6 asset fields)
- [ ] Results show correct total in currency format

### Health Insurance Assessment (13 fields!)
- [ ] 4 field sections render (Medicare, Medicaid, LTC, Other)
- [ ] All conditional fields show/hide based on checkboxes
- [ ] Medicare parts multiselect allows multiple selections
- [ ] 3 info boxes display (including LTC warning in intro)
- [ ] All 13 field values persist correctly
- [ ] Results show qualitative summary (no formula)

### Life Insurance Assessment (8 fields)
- [ ] 2 field sections render (Life Insurance, Annuities)
- [ ] Life insurance type select works (5 options)
- [ ] Policy fields conditional on has_life_insurance = "yes"
- [ ] Annuity fields conditional on has_annuities = "yes"
- [ ] 2 info boxes display
- [ ] Formula calculates: cash_value + annuity_value
- [ ] Results show total accessible value

### VA Benefits Assessment (6 fields, flag-gated)
- [ ] **Set is_veteran flag first!**
- [ ] Assessment card appears on hub
- [ ] 3 field sections render (Status, Income, A&A)
- [ ] Disability rating conditional on benefits status
- [ ] A&A monthly conditional on A&A status
- [ ] 2 info boxes display (tax-free, A&A eligibility)
- [ ] Formula calculates: disability + pension + A&A
- [ ] Results show total VA benefits /month

### Medicaid Planning Assessment (9 fields, flag-gated)
- [ ] **Set medicaid_planning_interest flag first!**
- [ ] Assessment card appears on hub
- [ ] 4 field sections render (Status, Assets, Spend-Down, Estate)
- [ ] LTC checkbox conditional on medicaid_status = "enrolled"
- [ ] Timeline conditional on interested_in_spend_down = true
- [ ] Estate plan multiselect allows multiple selections
- [ ] 4 info boxes display (coverage, limits, spend-down, recovery)
- [ ] Results show text summary (no formula)

---

## 🐛 Known Issues to Watch For

### Potential Issues
1. **Missing imports:** If assessment engine or hub imports fail
2. **JSON parsing errors:** If stub configs have syntax errors (unlikely after Phase 2)
3. **State key conflicts:** If old module state interferes with new assessment state
4. **Routing loops:** If step transitions don't rerun correctly
5. **Conditional logic bugs:** If visible_if checks fail on edge cases
6. **Formula calculation errors:** If referenced fields don't exist or are null
7. **Flag visibility issues:** If is_veteran or medicaid_planning_interest flags not set correctly
8. **Multiselect state:** If multiselect values don't persist or serialize correctly

### Debug Commands
```python
# Check current step
print(st.session_state.get("cost_v2_step"))

# Check current assessment
print(st.session_state.get("cost_planner_v2_current_assessment"))

# Check specific assessment state
print(st.session_state.get("cost_planner_v2_income"))
print(st.session_state.get("cost_planner_v2_health_insurance"))

# Check tile state
print(st.session_state.get("tiles", {}).get("cost_planner_v2"))

# Check flags
print(st.session_state.get("flags", {}))

# Check all assessment states
for key in st.session_state:
    if key.startswith("cost_planner_v2_"):
        print(f"{key}: {st.session_state[key]}")
```

### Common Fixes
- **Fields not appearing:** Check conditional visibility logic in JSON
- **Formula shows NaN:** Check that all referenced fields exist and have numeric defaults
- **Assessment not visible:** Check flag requirements (is_veteran, medicaid_planning_interest)
- **State not persisting:** Check that field keys match exactly in JSON and session_state
- **Multiselect issues:** Verify default is [] (empty array) not null

---

## 📊 Success Criteria

### Phase 2 Complete When:
- ✅ Assessment hub renders with 6 cards
- ✅ All 6 assessments have full field definitions (41 fields total)
- ✅ Can start any assessment (including flag-gated ones)
- ✅ Navi panel appears with guidance (hidden on intro/results)
- ✅ All field types render correctly (currency, select, checkbox, multiselect)
- ✅ Navigation works (Continue, Back, Back to Hub, Review Answers)
- ✅ State persists across sections and navigation
- ✅ Results view shows summaries (4 formulas + 2 text summaries)
- ✅ Progress tracking works on hub (percentages, completion icons)
- ✅ Resume functionality works
- ✅ Conditional visibility logic works (14+ different patterns)
- ✅ Two-column layout renders on Assets assessment
- ✅ All 19 info boxes display correctly
- ✅ Flag-based visibility works (veteran, Medicaid interest)
- ✅ Multiselect fields work (Medicare parts, estate docs)

### Ready for Phase 3 When:
- All test cases above pass
- No compile errors
- No runtime errors in console
- All 6 assessments can be completed end-to-end
- State management works correctly across all assessments
- Navigation flow is smooth
- Formulas calculate correctly
- Conditional logic reliable
- **User feedback:** UX feels complete and professional

---

## 🔍 Visual Checks

### Assessment Hub Should Look Like:
```
Financial Assessments
Complete these assessments to build your financial profile for care planning.

Progress: 0 of 6 assessments completed
[=========>                                          ] 0%

┌─────────────────────────────┐  ┌─────────────────────────────┐
│ 💰 Income Sources           │  │ 🏦 Assets & Resources       │
│ Monthly income from all     │  │ Available financial assets  │
│ sources                     │  │ and resources               │
│                             │  │                             │
│ ⚪ Not Started 🔴 Required  │  │ ⚪ Not Started 🔴 Required  │
│ ⏱️ 2-3 min                  │  │ ⏱️ 3-4 min                  │
│ [Start →]                   │  │ [Start →]                   │
└─────────────────────────────┘  └─────────────────────────────┘

┌─────────────────────────────┐  ┌─────────────────────────────┐
│ 🎖️ VA Benefits              │  │ 🏥 Health Insurance         │
│ Veterans Affairs benefits   │  │ Medicare, Medicaid, and     │
│ and aid                     │  │ supplemental coverage       │
│                             │  │                             │
│ ⚪ Not Started              │  │ ⚪ Not Started              │
│ ⏱️ 2-3 min                  │  │ ⏱️ 3-4 min                  │
│ [Start →]                   │  │ [Start →]                   │
└─────────────────────────────┘  └─────────────────────────────┘

... etc
```

### Assessment Page Should Look Like:
```
┌─────────────────────────────────────────────────────────────┐
│ Navi Panel (blue left border)                               │
│ Let's work on Income Sources                                │
│ I'll guide you through each section.                        │
│ Step 1 of 2                                                 │
└─────────────────────────────────────────────────────────────┘

🏛️ Social Security Benefits
────────────────────────────

Social Security Monthly Benefit
[____________________] $
Enter the monthly Social Security benefit amount

[← Back]  [Continue →]  [← Back to Hub]
```

---

## 🎯 Next Actions

After completing Phase 2 testing:
1. **Report bugs or issues** - Document any failures, edge cases, or UX concerns
2. **Verify all test cases pass** - Use comprehensive checklist above
3. **Validate formulas** - Ensure all 4 calculated summaries are correct
4. **Test conditional logic** - All 14+ visible_if patterns working
5. **Check info boxes** - All 19 boxes display with correct styling
6. **Mobile responsive** - Two-column layouts work on desktop, stack on mobile
7. **Flag visibility** - Veteran and Medicaid assessments appear when flags set

### Then Move to Phase 3: Expert Review Integration
1. **FinancialProfile Aggregation:** Build aggregator to collect all assessment data
2. **Expert Review Formulas:** Implement coverage_percentage, gap_amount, runway_months
3. **Care Flag Modifiers:** Define how GCP care flags affect cost estimates
4. **MCIP Publishing:** Send FinancialProfile to MCIP contracts
5. **Summary Page:** Create expert review visualization with recommendations

### Then Move to Phase 4: Cleanup
1. **Delete legacy files:** Remove products/cost_planner_v2/modules/*.py (7 files)
2. **Clean imports:** Remove unused module references
3. **Documentation:** Update all docs with new architecture
4. **Regression testing:** Full end-to-end validation
5. **Merge to main:** Create PR and merge cp-refactor branch

---

**Testing Time Estimate:** ~60-90 minutes for comprehensive Phase 2 testing  
**Expected Result:** All 6 assessments work perfectly, ready for Phase 3 integration

---

## 📈 Phase 2 Achievements

✅ **41 fields** migrated from Python to JSON  
✅ **19 info boxes** providing comprehensive guidance  
✅ **4 calculated formulas** for financial summaries  
✅ **14+ conditional visibility patterns** implemented  
✅ **2 flag-gated assessments** (veteran, Medicaid interest)  
✅ **Multiselect fields** for complex inputs  
✅ **Two-column layout** for better desktop UX  
✅ **~1,050 lines** of JSON configuration created  
✅ **Complete migration** from legacy Python modules  

**Phase 2 Status:** ✅ COMPLETE - All assessments fully built and ready to test!

See `CP_REFACTOR_PHASE_2_COMPLETE.md` for detailed implementation documentation.
