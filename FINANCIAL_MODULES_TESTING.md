# Financial Modules - Quick Testing Guide

## 🚀 Quick Start Testing

### 1. Run the App
```bash
cd /Users/shane/Desktop/cca_senior_navigator_v3
streamlit run app.py
```

### 2. Navigate to Cost Planner
- From welcome page → Select "Cost Planner V2" or navigate to Concierge Hub
- Should see **6 new module tiles**

## 📋 Module Testing Checklist

### Module 1: Income Sources 💰
**Expected time:** 2-3 minutes
- [ ] Social Security input works
- [ ] Pension input works
- [ ] Employment status dropdown shows 4 options
- [ ] Employment income only appears when status != "not_employed"
- [ ] Investment income input works
- [ ] Other income input works
- [ ] **Total Monthly Income** metric displays and calculates correctly
- [ ] Save & Continue works, marks module complete

### Module 2: Assets & Resources 🏦
**Expected time:** 3-4 minutes
- [ ] Checking & Savings input works (two-column layout)
- [ ] CDs & Money Market input works
- [ ] Total Liquid Assets calculates
- [ ] IRA inputs work (Traditional, Roth)
- [ ] 401k/403b and Other Retirement inputs work
- [ ] Total Retirement Accounts calculates
- [ ] Stocks & Bonds, Mutual Funds inputs work
- [ ] Total Investments calculates
- [ ] Primary Residence Value and Mortgage inputs work
- [ ] **Home Equity** calculates (value - mortgage)
- [ ] Investment Property input works
- [ ] Business Value and Other Assets inputs work
- [ ] **Total Available Assets** calculates correctly
- [ ] Percentage breakdown displays in info box
- [ ] Save & Continue works, marks module complete

### Module 3: VA Benefits 🎖️
**Expected time:** 3-5 minutes
- [ ] "Are you a veteran?" checkbox works
- [ ] Veteran relationship dropdown appears when checked
- [ ] Service era dropdown appears and works
- [ ] "Receive VA Disability?" checkbox works
- [ ] Disability rating dropdown appears (10%-100%)
- [ ] Monthly VA Disability input appears
- [ ] "Receive Aid & Attendance?" checkbox works
- [ ] A&A monthly input appears when checked
- [ ] "Interested in A&A?" checkbox appears when not receiving
- [ ] **Success message with 2025 benefit amounts** appears when interested:
  - Veteran alone: $2,379
  - Veteran with spouse: $2,829
  - Surviving spouse: $1,537
- [ ] **Total VA Benefits** metric calculates
- [ ] Save & Continue works, marks module complete

### Module 4: Health Insurance 🏥
**Expected time:** 4-6 minutes
- [ ] "Enrolled in Medicare?" checkbox works
- [ ] Medicare Parts multiselect appears (A, B, D)
- [ ] Medicare Advantage checkbox appears
- [ ] Medigap checkbox appears
- [ ] Medicare monthly premium input appears
- [ ] **Info box** displays: "Medicare does NOT cover long-term care in assisted living"
- [ ] "Enrolled in Medicaid?" checkbox works
- [ ] Medicaid status dropdown appears (enrolled, pending, planning, not eligible)
- [ ] "Medicaid covers LTC?" checkbox appears when enrolled
- [ ] Medicaid monthly coverage input appears
- [ ] Medicaid planning success message appears when not enrolled
- [ ] "Have LTC insurance?" checkbox works
- [ ] LTC provider text input appears
- [ ] LTC daily benefit input appears
- [ ] **LTC Monthly Benefit** auto-calculates (daily × 30)
- [ ] Elimination period dropdown appears
- [ ] Benefit period dropdown appears
- [ ] LTC monthly premium input appears
- [ ] "Have private insurance?" checkbox works
- [ ] Insurance type dropdown appears (employer, marketplace, private)
- [ ] Private premium input appears
- [ ] **Summary metrics** display:
  - Monthly Coverage
  - Monthly Premiums
  - Net Monthly Benefit (coverage - premiums)
- [ ] Save & Continue works, marks module complete

### Module 5: Life Insurance 🛡️
**Expected time:** 2-3 minutes
- [ ] "Have life insurance?" checkbox works
- [ ] Policy count dropdown appears (1, 2, 3+ policies)
- [ ] Policy type dropdown appears (Term, Whole, Universal, Variable, Not sure)
- [ ] Death benefit input works
- [ ] "Has cash value?" checkbox appears for non-term policies
- [ ] Cash value input appears when checked
- [ ] Monthly premium input works
- [ ] "Accelerated Death Benefit rider?" checkbox works
- [ ] "LTC rider?" checkbox works
- [ ] "Consider life settlement?" checkbox works
- [ ] **Info box** displays explaining care funding options
- [ ] **Summary metrics** display:
  - Death Benefit
  - Cash Value (if applicable)
  - Monthly Premium
- [ ] **Life settlement estimate** appears when considering (15% of death benefit)
- [ ] Save & Continue works, marks module complete

### Module 6: Medicaid Navigation 🧭
**Expected time:** 5-7 minutes
- [ ] Interest level dropdown works (5 options)
- [ ] State input appears when interest != "not_interested"
- [ ] Marital status dropdown appears (single, married, widowed, divorced)
- [ ] Countable assets input works
- [ ] Monthly income input works
- [ ] **Preliminary eligibility calculation** works:
  - ✅ Green success if assets <= $2,000 (single) / $3,000 (married) AND income <= $2,829
  - ⚠️ Yellow warning if over limits, with planning strategies listed
- [ ] Timeline dropdown appears (immediate to 2+ years)
- [ ] "Transferred assets in past 5 years?" checkbox works
- [ ] Transfer amount input appears when checked
- [ ] **5-year lookback warning** appears when transfers checked
- [ ] "Connect with Medicaid attorney?" checkbox works
- [ ] "Need application help?" checkbox works
- [ ] "Protect spouse?" checkbox appears when married
- [ ] **Summary metrics** display:
  - Interest Level
  - Timeline
  - Preliminary Eligible (Yes/No)
- [ ] Save & Continue works, marks module complete

## 🔄 Navigation Testing
- [ ] "Back to Hub" button returns to Cost Planner Hub
- [ ] "Back to Modules" button works (if applicable)
- [ ] "Save & Continue" saves data to session state
- [ ] Module completion status visible on hub tiles
- [ ] Can navigate between modules without losing data
- [ ] Completed modules show checkmark or "completed" status

## 💾 Data Persistence Testing
- [ ] Fill out Income module → Save → Return to hub
- [ ] Navigate to Assets module → Save → Return to hub
- [ ] Go back to Income module → Previous data still there
- [ ] Refresh browser → Session data persists (if session management configured)

## 📊 Summary/Results Testing
After completing modules:
- [ ] Can view aggregated financial summary
- [ ] Total monthly income from all sources accurate
- [ ] Total available assets accurate
- [ ] VA benefits properly counted
- [ ] Insurance net benefits calculated correctly
- [ ] Medicaid eligibility status clear

## 🐛 Known Limitations
- Cost estimates/recommendations may not be updated yet (depends on aggregation logic)
- Some old module references may need cleanup
- Session state structure may need adjustment for new module keys

## ✅ Success Criteria
**Minimum for merge to dev:**
- [ ] All 6 modules appear as tiles in Cost Planner Hub
- [ ] Each module form renders without errors
- [ ] Data entry works for all field types
- [ ] Conditional fields show/hide correctly
- [ ] Summary calculations work
- [ ] Save & Continue marks modules complete
- [ ] Navigation works (hub ↔ modules)
- [ ] No console errors

**Nice to have:**
- [ ] Module completion progress indicator
- [ ] Data export functionality
- [ ] Visual breakdown charts
- [ ] Recommendation engine integration

## 🚨 Troubleshooting

### If modules don't appear:
1. Check `config/cost_planner_v2_modules.json` loaded correctly
2. Verify module registry in `products/cost_planner_v2/modules/__init__.py`
3. Check Cost Planner Hub rendering logic for module loading

### If conditional fields don't work:
1. Check `visible_if` logic in JSON config
2. Verify field keys match exactly (case-sensitive)
3. Test with browser console open for JS errors

### If calculations are wrong:
1. Verify formula in JSON config
2. Check Python calculation logic in module .py files
3. Test with simple values first

### If data doesn't persist:
1. Check session state keys match module keys
2. Verify `st.session_state.cost_v2_modules[module_key]` structure
3. Look for session state clearing/reset logic

## 📝 Git Status
**Branch:** `financial-modules`
**Commit:** `e31a83c` - feat: Implement 6 comprehensive Financial Assessment modules
**Status:** ✅ All changes committed

**Ready for:** Testing → Merge to dev → Test in dev environment → Merge to main/apzumi

---

**Questions or issues?** Refer to `FINANCIAL_MODULES_IMPLEMENTATION.md` for comprehensive documentation.
