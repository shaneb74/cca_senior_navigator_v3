# Cost Planner Assessment Refactor - Testing Guide

**Branch:** `cp-refactor`  
**Status:** Phase 1 Complete - Ready for Testing

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
- [ ] **All 6 cards render:** Income, Assets, VA Benefits, Health Insurance, Life Insurance, Medicaid Planning
- [ ] **Required badges:** Income and Assets show "🔴 Required"
- [ ] **Status badges:** All show "⚪ Not Started" initially
- [ ] **Progress bar:** Shows "0 of 6 assessments completed" and 0%
- [ ] **Conditional visibility:** VA Benefits and Medicaid hidden (unless flags set)

### Starting an Assessment
- [ ] Click "Start →" on Income assessment
- [ ] **Navi panel appears** at top with guidance message
- [ ] **Section header renders:** "💰 Income Assessment" or "🏛️ Social Security Benefits"
- [ ] **Fields render correctly:**
  - Currency field with number input
  - Min/max/step constraints work
  - Help text appears
- [ ] **Navigation buttons appear:**
  - "Continue →" (primary button)
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
- [ ] Click "View Results" on last section
- [ ] **Results page renders:**
  - Summary calculation shows (e.g., "Total Monthly Income: $1,234")
  - All responses listed by section
  - Currency values formatted correctly
- [ ] **Status updated:** Card shows "✅ Complete" back on hub
- [ ] **Progress bar updates:** "1 of 6 assessments completed"

### State Persistence
- [ ] Complete Income assessment partially
- [ ] Navigate to different product (e.g., GCP)
- [ ] Return to Cost Planner → Financial Assessment
- [ ] **Progress preserved:** Income shows "Resume" button and percentage
- [ ] Click "Resume"
- [ ] **Returns to exact section** where you left off
- [ ] **All answers preserved**

### Field Types
Test different field widgets:
- [ ] **Currency:** Number input with step increments
- [ ] **Select:** Dropdown with options
- [ ] **Checkbox:** Boolean toggle
- [ ] **Multiselect:** Multiple selection
- [ ] **Text:** Text input
- [ ] **Date:** Date picker

### Two-Column Layout
- [ ] Assets assessment uses two-column layout
- [ ] Fields render in correct columns
- [ ] Responsive on narrow screens (stacks vertically)

### Conditional Visibility
- [ ] Set `is_veteran` flag in session state:
  ```python
  st.session_state.setdefault("flags", {})["is_veteran"] = True
  ```
- [ ] **VA Benefits card appears** in hub
- [ ] **Medicaid Planning card appears** if `medicaid_eligible` flag set

### Required Field Validation
- [ ] Leave a required field empty
- [ ] Click "Continue"
- [ ] **Warning appears:** "Please complete required fields: [field name]"
- [ ] **Navigation blocked** until field completed

### Navi Panel
- [ ] Navi panel appears on all assessment pages
- [ ] **Variant is "module":** Blue left border style
- [ ] **Contextual messages:** Different guidance per section
- [ ] **Progress chip:** Shows "Step X of Y"
- [ ] **No Navi on results page** (assessment handles its own messaging)

---

## 🐛 Known Issues to Watch For

### Potential Issues
1. **Missing imports:** If assessment engine or hub imports fail
2. **JSON parsing errors:** If stub configs have syntax errors
3. **State key conflicts:** If old module state interferes
4. **Routing loops:** If step transitions don't rerun correctly

### Debug Commands
```python
# Check current step
print(st.session_state.get("cost_v2_step"))

# Check current assessment
print(st.session_state.get("cost_planner_v2_current_assessment"))

# Check assessment state
print(st.session_state.get("cost_planner_v2_income"))

# Check tile state
print(st.session_state.get("tiles", {}).get("cost_planner_v2"))
```

---

## 📊 Success Criteria

### Phase 1 Complete When:
- ✅ Assessment hub renders with 6 cards
- ✅ Can start any assessment
- ✅ Navi panel appears with guidance
- ✅ Fields render based on JSON config
- ✅ Navigation works (Continue, Back, Back to Hub)
- ✅ State persists across sections
- ✅ Results view shows summary
- ✅ Progress tracking works on hub
- ✅ Resume functionality works
- ✅ Required field validation works

### Ready for Phase 2 When:
- All test cases above pass
- No compile errors
- No runtime errors in console
- State management works correctly
- Navigation flow is smooth

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

After testing Phase 1:
1. Report any bugs or issues
2. Verify all test cases pass
3. Move to Phase 2: Full config population
4. Migrate all fields from `cost_planner_v2_modules.json`
5. Add calculations and conditional logic
6. Integrate with Expert Review

---

**Testing Time Estimate:** ~30 minutes for full test suite  
**Expected Result:** All core functionality works, ready for Phase 2
