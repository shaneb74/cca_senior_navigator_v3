# Cost Planner Phase 1 - Testing Checklist

**Date:** October 12, 2025  
**Streamlit URL:** http://localhost:8501/?page=cost

---

## Test 1: Base Module Loads ✓

**URL:** `http://localhost:8501/?page=cost`

**Expected Behavior:**
- ✅ Page loads without errors
- ✅ Title: "Cost Planner"
- ✅ Subtitle with 5 bullet points about features
- ✅ Blue progress bar at top (0 segments filled)
- ✅ "Get Started" button at bottom

**What to Check:**
- [ ] No errors in browser console (F12)
- [ ] No errors in Streamlit terminal
- [ ] Page layout looks correct
- [ ] Back button says "← Back" (should go to hub_concierge)

---

## Test 2: Mock Authentication Controls ✓

**Location:** Sidebar (left panel)

**Expected Behavior:**
- ✅ Section titled "🔧 Dev Tools"
- ✅ Status shows "Not authenticated" with info icon
- ✅ Button: "🔒 Mock Login"
- ✅ Caption: "*Mock authentication for development*"

**Actions to Test:**
1. Click "🔒 Mock Login" button
   - Expected: Button changes to "🔓 Mock Logout"
   - Expected: Status changes to "✓ Authenticated"
   - Expected: Shows "*Logged in as: dev@example.com*"

2. Click "🔓 Mock Logout" button
   - Expected: Returns to "Not authenticated" state
   - Expected: Button changes back to "🔒 Mock Login"

**Checklist:**
- [ ] Mock Login button works
- [ ] Status updates correctly
- [ ] Mock Logout button works
- [ ] State persists when navigating

---

## Test 3: Intro Page Navigation ✓

**Starting Point:** Intro page (`?page=cost`)

**Action:** Click "Get Started" button

**Expected Behavior:**
- ✅ Navigates to Step 2: "Choose Your Assessment Path"
- ✅ Progress bar updates (1/2 segments filled)
- ✅ Title changes to "Choose Your Assessment Path"
- ✅ Shows subtitle about assessment detail
- ✅ Radio button options visible:
  - "📊 Quick Estimate" (with help text)
  - "📈 Full Assessment" (with help text)
- ✅ "Continue" button at bottom
- ✅ "Full Assessment" is pre-selected (default)

**Checklist:**
- [ ] Navigation works
- [ ] Progress bar updates
- [ ] Radio buttons render correctly
- [ ] Default selection is set
- [ ] Continue button is enabled

---

## Test 4: Path Selection ✓

**Starting Point:** Step 2 (Path Selection)

**Test A: Select Quick Estimate**
1. Click "📊 Quick Estimate" radio button
2. Click "Continue" button

**Expected:**
- State saved: `assessment_path = "quick"`
- Navigates to Step 3: "Financial Assessment Modules"

**Test B: Select Full Assessment**
1. Use browser back button to return to Step 2
2. Click "📈 Full Assessment" radio button
3. Click "Continue" button

**Expected:**
- State saved: `assessment_path = "full"`
- Navigates to Step 3: "Financial Assessment Modules"

**Checklist:**
- [ ] Quick Estimate selection works
- [ ] Full Assessment selection works
- [ ] Selection saved in state
- [ ] Continue button navigates correctly
- [ ] Browser back button works

---

## Test 5: Module Dashboard (Empty) ✓

**Starting Point:** Step 3 (Module Dashboard)

**Expected Behavior:**
- ✅ Title: "Financial Assessment Modules"
- ✅ Subtitle with instructions about completing modules
- ✅ Progress bar shows 2/2 segments filled (100%)
- ✅ No module tiles displayed (Phase 2 feature)
- ✅ No Continue/Next button (end of base module)

**What to Check:**
- [ ] Dashboard page renders
- [ ] Progress shows 100% (base module complete)
- [ ] No errors about missing tiles
- [ ] Instructions are clear

**Note:** Module tiles will be added in Phase 2. This is expected behavior.

---

## Test 6: Authentication Gate (Protected Route) ✓

**Objective:** Verify auth gate blocks access to protected modules

**Setup:**
1. Ensure you are logged OUT (click Mock Logout if needed)
2. Navigate to fake protected module

**URL to Test:** `http://localhost:8501/?page=cost&cost_module=income_sources`

**Expected Behavior:**
- ✅ Page title: "Cost Planner"
- ✅ Warning box: "🔒 **Authentication Required**"
- ✅ Message about login requirement (save progress, personalized calculations, secure data)
- ✅ Button: "🔓 Mock Login" (primary blue button)
- ✅ Caption: "*Real authentication will be integrated in production*"
- ✅ NO module content displayed (blocked by auth gate)

**Actions:**
1. Click "🔓 Mock Login" button
   - Expected: Page reloads
   - Expected: Shows error "❌ Module 'income_sources' not found" (expected - not built yet)
   - Expected: "← Back to Cost Planner Home" button appears

2. Click "← Back to Cost Planner Home" button
   - Expected: Returns to base module intro (`?page=cost`)

**Checklist:**
- [ ] Auth gate shows for protected module
- [ ] Login button works
- [ ] After login, shows "module not found" error (expected)
- [ ] Back button returns to base module
- [ ] Auth state persists

---

## Test 7: Public Module Access ✓

**Objective:** Verify base module is accessible without authentication

**Setup:**
1. Ensure you are logged OUT
2. Navigate to base module

**URL to Test:** `http://localhost:8501/?page=cost` or `?page=cost&cost_module=base`

**Expected Behavior:**
- ✅ Page loads successfully
- ✅ No auth gate appears
- ✅ Can navigate through all 3 steps
- ✅ Authentication status in sidebar shows "Not authenticated"

**Checklist:**
- [ ] Base module accessible without login
- [ ] All steps work without auth
- [ ] No auth gate blocking content

---

## Test 8: State Persistence ✓

**Objective:** Verify state is saved across page refreshes

**Actions:**
1. Navigate through base module to Step 2 (Path Selection)
2. Select "Full Assessment"
3. Click Continue to reach Dashboard
4. Press F5 or refresh browser
5. Use browser back button to return to Step 2

**Expected Behavior:**
- ✅ After refresh: Returns to last page (Dashboard)
- ✅ After back button: Previous selection ("Full Assessment") is still selected
- ✅ Progress bar reflects correct position

**Checklist:**
- [ ] State persists after refresh
- [ ] Selections are remembered
- [ ] Progress tracking works

---

## Test 9: Terminal Output (No Errors) ✓

**Check Streamlit Terminal for Errors**

**Expected Output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

**Should NOT see:**
- ❌ ImportError
- ❌ ModuleNotFoundError
- ❌ AttributeError
- ❌ TypeError
- ❌ Any stack traces

**Checklist:**
- [ ] No import errors
- [ ] No runtime errors
- [ ] Clean terminal output

---

## Test 10: Browser Console (No Errors) ✓

**Check Browser Console (F12 → Console tab)**

**Should NOT see:**
- ❌ JavaScript errors
- ❌ 404 errors
- ❌ Network errors
- ❌ CORS errors

**Checklist:**
- [ ] No JavaScript errors
- [ ] No network errors
- [ ] Clean console

---

## Test 11: Session State Inspection ✓

**Optional: Advanced Testing**

**Add to base module config for debugging:**

In `products/cost_planner/base_module_config.py`, temporarily add:
```python
import streamlit as st
st.sidebar.markdown("### 🔍 State Inspector")
st.sidebar.json(st.session_state.get("cost.base", {}))
st.sidebar.json(st.session_state.get("auth", {}))
```

**Expected State Structure:**
```json
{
  "cost.base": {
    "progress": 100,
    "assessment_path": "full",
    "_step": 2
  },
  "auth": {
    "is_authenticated": true
  }
}
```

**Checklist:**
- [ ] State structure matches expected
- [ ] Values update correctly
- [ ] No unexpected keys

---

## Summary: Phase 1 Test Results

### Critical Tests (Must Pass)
- [ ] Base module loads without errors
- [ ] All 3 steps navigate correctly
- [ ] Mock authentication works (login/logout)
- [ ] Auth gate blocks protected routes
- [ ] Public module accessible without auth

### Nice-to-Have Tests (Should Pass)
- [ ] Progress bar updates correctly
- [ ] State persists across refreshes
- [ ] Browser back button works
- [ ] No console errors
- [ ] No terminal errors

---

## Issues Found

**List any issues discovered during testing:**

1. Issue: _______________________________________________
   - Expected: _________________________________________
   - Actual: ___________________________________________
   - Fix needed: _______________________________________

2. Issue: _______________________________________________
   - Expected: _________________________________________
   - Actual: ___________________________________________
   - Fix needed: _______________________________________

---

## Phase 1 Test Status

**Overall Result:** 
- [ ] ✅ PASS - Ready for Phase 2
- [ ] ⚠️ MINOR ISSUES - Document and proceed
- [ ] ❌ FAIL - Fix issues before Phase 2

**Tested By:** _______________________  
**Date:** October 12, 2025  
**Time:** _______________________

---

## Next Steps

### If Tests Pass ✅
1. Commit Phase 1 to Git
2. Proceed to Phase 2: Build income_sources module
3. Update COST_PLANNER_PHASE1_STATUS.md with test results

### If Tests Fail ❌
1. Document issues in this file
2. Fix critical issues
3. Re-run tests
4. Update code as needed

---

**Testing Instructions:** Work through tests 1-10 in order, checking each item as you go.
