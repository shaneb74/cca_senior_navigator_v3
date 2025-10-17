# Phase 3 Expert Review - Testing Checklist

**Status:** Ready to Test  
**Branch:** `cp-refactor`  
**Local URL:** http://localhost:8501/?page=cost_v2

---

## 🚀 Quick Test Path

### 1. Navigate to Cost Planner
- Open browser to: http://localhost:8501/?page=cost_v2
- Or: Go to Concierge Hub → "Financial Planning"

### 2. Complete Intro & Triage
- [ ] Enter ZIP code (any valid ZIP, e.g., 90210)
- [ ] Select care type (e.g., "Assisted Living")
- [ ] Click "Continue to Financial Assessment"
- [ ] Sign in if needed (should auto-skip if authenticated)
- [ ] Answer triage questions if shown
- [ ] Click "Continue to Financial Assessment"

### 3. Complete Required Assessments

#### Income Assessment (Required)
- [ ] Click "Start →" on Income card
- [ ] Complete intro, click "Continue →"
- [ ] **Social Security:** Enter amount (e.g., $2,000)
- [ ] **Pension:** Enter amount or leave at $0
- [ ] **Employment:** Select status, enter amount if employed
- [ ] **Other Income:** Enter amount or leave at $0
- [ ] Click "View Results"
- [ ] Verify total calculates correctly
- [ ] Click "Back to Hub"
- [ ] Verify Income shows "✅ Complete"

#### Assets Assessment (Required)
- [ ] Click "Start →" or "Resume" on Assets card
- [ ] Complete intro, click "Continue →"
- [ ] **Checking & Savings:** Enter amount (e.g., $50,000)
- [ ] **Investment Accounts:** Enter amount (e.g., $100,000)
- [ ] **Primary Residence:** Enter value (e.g., $300,000)
- [ ] **Home Sale Interest:** Check or uncheck
- [ ] **Other Real Estate:** Enter amount or leave at $0
- [ ] **Other Resources:** Enter amount or leave at $0
- [ ] Click "View Results"
- [ ] Verify total calculates correctly
- [ ] Click "Back to Hub"
- [ ] Verify Assets shows "✅ Complete"

### 4. Access Expert Review

#### From Assessment Hub
- [ ] After completing Income + Assets, hub should show "Expert Review" option
- [ ] Click "Expert Review" button
- [ ] Should navigate to expert review page

---

## ✅ Expert Review Page - Clean UI Verification

### Navi Panel (Communication Layer)
- [ ] **Navi panel appears** at top with blue left border
- [ ] **Title adapts to coverage tier:**
  - Excellent: "Excellent Financial Position"
  - Good: "Strong Financial Foundation"
  - Moderate: "Strategic Planning Recommended"
  - Concerning: "Action Needed Soon"
  - Critical: "Immediate Planning Essential"
- [ ] **Reason text explains coverage** (e.g., "Your income covers X% of estimated costs")
- [ ] **Encouragement message appropriate:**
  - Icon: ✅ (excellent), 👍 (good), 📊 (moderate), ⚠️ (concerning), 🚨 (critical)
  - Text: Contextual guidance based on tier
  - Status: 'complete', 'active', or 'warning'
- [ ] **Context chips show runway** (if applicable):
  - Format: "X months coverage/runway/remaining"
  - Only shows if runway exists (gap > 0)

### Page Header
- [ ] **Page header renders:** "💰 Financial Review"
- [ ] Clean, minimal styling (no banner clutter)

### Coverage Summary (Large Display)
- [ ] **Coverage percentage displays:**
  - Large, centered (48px font)
  - Format: "XX%" or "999%+" if over 999%
  - Clean, professional typography
- [ ] **Label below:** "Income Coverage of Estimated Care Costs"

### 3-Column Breakdown
- [ ] **Column 1: Estimated Cost**
  - Label: "Estimated Cost"
  - Value: "$X,XXX/mo" (formatted with commas)
  - Clean card background
- [ ] **Column 2: Total Income**
  - Label: "Total Income"
  - Value: "$X,XXX/mo" (income + benefits)
  - Clean card background
- [ ] **Column 3: Gap or Surplus**
  - Label: "Surplus" (if negative gap) or "Gap" (if positive gap)
  - Value: "$X,XXX/mo" (absolute value)
  - Color: Green for surplus, Red for gap
  - Clean card background

### Financial Details Section
- [ ] **Section header:** "Financial Details"
- [ ] **Monthly Income breakdown:**
  - Shows total: "$X,XXX"
  - Lists sources if > $0: Social Security, Pension, Employment, Other
  - Details shown in secondary color, smaller font
- [ ] **Monthly Benefits** (if any):
  - Shows total: "$X,XXX"
- [ ] **Liquid Assets** (if any):
  - Shows total: "$X,XXX"
  - Runway text: "Coverage runway: X years, Y months"
  - Only shows if runway exists

### Recommended Actions Section
- [ ] **Section header:** "Recommended Actions"
- [ ] **Primary recommendation:**
  - Bold text
  - Clear, actionable statement
- [ ] **Action items list:**
  - Numbered (1, 2, 3, etc.)
  - 3-5 items depending on scenario
  - Clear, specific actions
- [ ] **Helpful Resources** (if any):
  - Subheading: "Helpful Resources:"
  - Bulleted list
  - 3-5 resources with descriptions

### Navigation (Bottom)
- [ ] **3-column layout:**
  - Left: "← Back to Assessments" button
  - Middle: Empty
  - Right: "Exit Cost Planner →" button
- [ ] **Back to Assessments** returns to hub
- [ ] **Exit** navigates to exit step

---

## 🧪 Test Scenarios

### Scenario A: Excellent Coverage (100%+ Income)
**Setup:**
- Income: Social Security $2,000, Pension $2,000, Total = $4,000/mo
- Assets: $150,000 liquid
- Estimated Cost: ~$4,500/mo (for assisted living)

**Expected:**
- [ ] Coverage: ~89% (or adjust income to $4,500+ for 100%+)
- [ ] Navi title: "Excellent Financial Position" (if 100%+) or "Strong Financial Foundation" (if 80-99%)
- [ ] Green/positive messaging
- [ ] Recommendations focus on optimization
- [ ] No urgent action items

### Scenario B: Moderate Coverage (60-79% Income)
**Setup:**
- Income: Social Security $2,000, Total = $2,000/mo
- Assets: $200,000 liquid
- Estimated Cost: ~$4,500/mo

**Expected:**
- [ ] Coverage: ~44% (or adjust to 60-79% range)
- [ ] Navi title: "Moderate" or "Concerning"
- [ ] Blue/guidance messaging
- [ ] Recommendations focus on bridging gap
- [ ] Action items: Explore supplemental income, consider home equity, Medicaid, VA benefits

### Scenario C: Critical Coverage (<40% Income, Low Assets)
**Setup:**
- Income: Social Security $1,500, Total = $1,500/mo
- Assets: $20,000 liquid
- Estimated Cost: ~$4,500/mo

**Expected:**
- [ ] Coverage: ~33%
- [ ] Navi title: "Immediate Planning Essential"
- [ ] Warning messaging (calm but urgent)
- [ ] Gap: $3,000/mo
- [ ] Runway: ~7 months ($20,000 / $3,000)
- [ ] Recommendations focus on urgent actions
- [ ] Action items: Medicaid application, all benefit programs, Area Agency on Aging, care alternatives

---

## 🔧 Incomplete State Testing

### Test: Access Expert Review Before Completing Required Assessments
1. [ ] Clear session state (refresh page)
2. [ ] Navigate directly to expert review (if possible)
3. [ ] Or: Start Cost Planner, skip to assessments, try to access expert review

**Expected Behavior:**
- [ ] **Navi shows:** "Complete Required Assessments"
- [ ] **Navi reason:** "Please complete Income and Assets assessments to see your financial review"
- [ ] **Navi encouragement:**
  - Icon: 📋
  - Text: "These two assessments are essential for accurate cost analysis"
  - Status: 'active'
- [ ] **Info box displays:** "Complete Income and Assets assessments to unlock your personalized financial review"
- [ ] **Single button:** "← Back to Assessments" (centered)
- [ ] **No financial data displayed**

---

## 🎨 Clean UI Verification

### No Clutter Checklist
- [ ] **NO warning banners** (Navi handles all warnings)
- [ ] **NO colored alert boxes** on page (except info box in incomplete state)
- [ ] **NO redundant messaging** (Navi is sole communication)
- [ ] **NO unnecessary visual elements** (just clean metrics)
- [ ] **Clean typography** (professional, readable)
- [ ] **Minimal navigation** (only essential buttons)
- [ ] **Whitespace** used effectively (not cramped)

### Professional Design Checklist
- [ ] **Consistent spacing** (margins/padding)
- [ ] **Clean color palette** (subtle backgrounds, no harsh colors)
- [ ] **Clear hierarchy** (headers, body text, labels distinct)
- [ ] **Readable fonts** (appropriate sizes)
- [ ] **Aligned elements** (columns, lists, buttons)
- [ ] **Responsive** (works on different screen sizes)

---

## 🐛 Issues to Watch For

### Common Problems
1. **Missing data:** If assessments not aggregated correctly
2. **Calculation errors:** If formulas return NaN or wrong values
3. **Missing Navi:** If Navi panel doesn't render
4. **Wrong tier:** If coverage tier classification incorrect
5. **Missing runway:** If runway_months should exist but doesn't
6. **Navigation broken:** If buttons don't route correctly
7. **Import errors:** If financial_profile or expert_formulas fail to import
8. **MCIP errors:** If publishing fails silently

### Debug Commands (Browser Console)
```javascript
// Check session state
Streamlit.getStreamlitState()

// Look for cost planner data
// (use Streamlit Dev Tools if installed)
```

### Python Debug (if errors occur)
```python
# Add to expert_review.py temporarily
import streamlit as st
st.write("Profile:", profile)
st.write("Analysis:", analysis)
```

---

## ✅ Success Criteria

Phase 3 Expert Review is successful when:

- [ ] **Navi communication works** (title, reason, encouragement adapt to tier)
- [ ] **Coverage % displays correctly** (large, centered, formatted)
- [ ] **3-column breakdown renders** (cost, income, gap with proper formatting)
- [ ] **Financial details show** (income breakdown, benefits, assets, runway)
- [ ] **Recommendations display** (primary rec, action items, resources)
- [ ] **Navigation works** (back to hub, exit)
- [ ] **Incomplete state handled** (clear message, back button, no data)
- [ ] **Clean UI throughout** (no clutter, Navi handles communication)
- [ ] **Professional design** (typography, spacing, colors)
- [ ] **MCIP publishing works** (financial profile saved to contracts)
- [ ] **No console errors** (check browser console)
- [ ] **No Python errors** (check terminal output)

---

## 📊 Test Results Template

### Test Summary
- **Tester:** [Your Name]
- **Date:** [Date]
- **Branch:** cp-refactor
- **Commit:** c6002d4 (or latest)

### Results
- [ ] All required assessments completable
- [ ] Expert review accessible after completion
- [ ] Navi communication clear and contextual
- [ ] Coverage summary displays correctly
- [ ] Financial details accurate
- [ ] Recommendations personalized and helpful
- [ ] Navigation smooth
- [ ] Clean UI (no clutter)
- [ ] Professional design
- [ ] No errors encountered

### Issues Found
1. [Issue description, if any]
2. [Issue description, if any]

### Overall Assessment
- [ ] ✅ **Phase 3 Ready** - All tests pass, no issues
- [ ] ⚠️ **Minor Issues** - Works but needs small fixes
- [ ] ❌ **Major Issues** - Blocking problems found

### Notes
[Any additional observations, suggestions, or feedback]

---

**Testing Time Estimate:** 15-20 minutes for comprehensive Phase 3 testing  
**Expected Result:** Clean, professional expert review with Navi-driven communication

🎉 **Ready to test Phase 3!**
