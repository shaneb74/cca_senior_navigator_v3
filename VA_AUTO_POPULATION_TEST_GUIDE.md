# VA Auto-Population Testing Guide

## Overview
This guide walks through testing the VA disability auto-population feature that was just implemented. The feature automatically calculates monthly VA disability compensation based on the veteran's rating and dependents.

## Prerequisites
✅ App is running on port 8501 (confirmed: PIDs 2176, 2211)
✅ Debug logging is active (terminal + browser)
✅ Widget state management fixes applied
✅ Persistence keys corrected

## What We're Testing

### Primary Functionality
1. **Auto-calculation**: VA disability monthly amount auto-populates when rating + dependents are selected
2. **Single-click**: Dropdowns work on first click (no double-click needed)
3. **Persistence**: Data saves across page navigation and app restarts
4. **Summary integration**: Calculated amounts appear in summary section

### Test Scenarios

#### Test 1: Basic Auto-Population (60% + Spouse)
**Expected Result**: $1,523.93

1. **Navigate to VA Benefits Assessment**
   - In app, go to Cost Planner v2 → VA Benefits
   - You should see clean single-page layout

2. **Fill Section 1: VA Disability Status**
   - Click "Do you receive VA disability compensation?" dropdown
   - Select "Yes" (should work on FIRST click)
   - ⚠️ **Watch for**: Dropdown should register immediately, no second click needed

3. **Fill Section 2: Rating**
   - Click "VA disability rating" dropdown
   - Select "60%" (should work on FIRST click)

4. **Fill Section 3: Dependents**
   - Click "VA dependents status" dropdown
   - Select "Veteran with spouse" (should work on FIRST click)
   - 🎯 **Expected**: As soon as you select dependents, you should see:
     - Toast notification: "✅ Calculated VA benefit: $1,523.93/month"
     - Field "VA disability monthly amount" auto-fills with $1,523.93
     - Summary at bottom shows $1,523.93

5. **Check Terminal Output**
   Look for debug output like:
   ```
   ============================================================
   🔍 _auto_populate_va_disability() called
      State keys: [...]
      has_va_disability: 'yes' (type: str)
      va_disability_rating: '60' (type: str)
      va_dependents: 'spouse' (type: str)
      📞 Calling get_monthly_va_disability('60', 'spouse')...
      💰 Result: $1,523.93
      ✅ Updated state['va_disability_monthly'] = 1523.93
   ============================================================
   ```

#### Test 2: Higher Rating (70% + Spouse)
**Expected Result**: $1,908.95

1. Change rating to "70%"
2. Keep dependents as "Veteran with spouse"
3. **Expected**: Field auto-updates to $1,908.95
4. **Expected**: Toast shows new amount

#### Test 3: Complex Dependents (100% + Spouse + 2 Children)
**Expected Result**: $4,405.73

1. Change rating to "100%"
2. Change dependents to "Veteran with spouse and 2 or more children under 18"
3. **Expected**: Field auto-updates to $4,405.73
4. **Expected**: Summary shows $4,405.73

#### Test 4: No VA Disability
**Expected Result**: Fields hidden/disabled

1. Change "Do you receive VA disability compensation?" to "No"
2. **Expected**: Rating and dependents fields should be hidden or disabled
3. **Expected**: Monthly amount should clear or be $0.00

#### Test 5: Persistence Test

1. Complete VA Benefits assessment with 70% + spouse
2. Navigate to another assessment (e.g., Income)
3. Navigate back to VA Benefits
4. **Expected**: All fields retain values (70%, spouse, $1,908.95)

5. Restart the app:
   ```bash
   # Find and kill Streamlit processes
   kill -9 2176 2211
   
   # Restart
   cd /Users/shane/Desktop/cca_senior_navigator_v3
   streamlit run app.py
   ```

6. Navigate to VA Benefits again
7. **Expected**: All data persists (same UID in URL)

## What to Watch For

### ✅ Success Indicators
- ✅ Dropdowns work on **first click**
- ✅ Toast notification appears with calculated amount
- ✅ Field auto-fills immediately after selecting dependents
- ✅ Summary section shows correct total
- ✅ Terminal shows debug output with correct values
- ✅ No errors in terminal or browser console
- ✅ Data persists across navigation and restarts

### ❌ Failure Indicators
- ❌ Dropdown requires two clicks to register
- ❌ Field stays at $0.00 after selections
- ❌ No toast notification appears
- ❌ Summary doesn't update
- ❌ Terminal shows exceptions or "Skipping" messages
- ❌ Data disappears when navigating away
- ❌ TypeError or ValueError in terminal

## Troubleshooting

### Issue: Field Shows $0.00 After Selections

**Check Terminal Output:**
- Look for "Skipping" messages
- Check what values are being passed to get_monthly_va_disability()
- Verify state keys match expectations

**Possible Causes:**
- Widget state not updating (double-click issue not fixed)
- Auto-populate function not being called
- Calculation function returning None

**Debug Steps:**
1. Check terminal for "🔍 _auto_populate_va_disability() called" message
2. If not appearing: function not being invoked
3. If appearing but skipping: check has_va_disability value
4. If calculating but field not updating: state update not reflecting in UI

### Issue: Dropdowns Require Two Clicks

**This indicates widget state management issue not fully resolved.**

**Check:**
1. Verify browser cache is cleared (hard refresh: Cmd+Shift+R)
2. Check core/assessment_engine.py uses widget_key correctly
3. Look for st.session_state pre-initialization attempts

**Quick Fix:**
```python
# In core/assessment_engine.py, ensure pattern is:
widget_key = f"field_{key}"
value = st.selectbox(..., key=widget_key)  # NOT pre-initializing st.session_state
```

### Issue: Data Doesn't Persist

**Check Persistence Keys:**
- Verify core/session_store.py line 571 has `"cost_planner_v2_va_benefits"`
- NOT `"cost_v2_va_benefits"`

**Check Session:**
- Verify UID in URL stays consistent
- Check if session_id changes between visits

## Browser Testing Tips

### Clear Cache First
```
Chrome: Cmd+Shift+R (hard refresh)
Safari: Cmd+Option+E (clear cache) then Cmd+R
Firefox: Cmd+Shift+R
```

### Check Browser Console
1. Open Developer Tools (Cmd+Option+I)
2. Go to Console tab
3. Look for JavaScript errors
4. Watch for Streamlit connection messages

### Monitor Network Tab
1. Open Developer Tools → Network tab
2. Watch for WebSocket connections
3. Check for failed requests

## Terminal Monitoring

### What to Watch
Open terminal where Streamlit is running and watch for:

1. **Page Load**:
   ```
   Section 1 render complete
   🔍 VA Benefits Section VA Disability Status rendered
   ```

2. **Dropdown Changes**:
   ```
   Field updated: has_va_disability = 'yes'
   Field updated: va_disability_rating = '60'
   Field updated: va_dependents = 'spouse'
   ```

3. **Auto-Population Trigger**:
   ```
   ============================================================
   🔍 _auto_populate_va_disability() called
   ...
   💰 Result: $1,523.93
   ✅ Updated state['va_disability_monthly'] = 1523.93
   ============================================================
   ```

### Terminal Commands

**View last 50 lines of output**:
```bash
# Terminal is already running, just scroll up to see debug output
```

**Restart app with visible output**:
```bash
cd /Users/shane/Desktop/cca_senior_navigator_v3
streamlit run app.py
```

## Expected Test Results Summary

| Test | Rating | Dependents | Expected Amount |
|------|--------|------------|-----------------|
| 1 | 60% | Spouse | $1,523.93 |
| 2 | 70% | Spouse | $1,908.95 |
| 3 | 100% | Spouse + 2 children | $4,405.73 |
| 4 | 60% | Spouse + 1 child | $1,621.93 |
| 5 | 30% | No dependents | $524.31 |

## Next Steps After Testing

### If All Tests Pass ✅
1. Update todo list to mark test complete
2. Remove debug logging code:
   - Terminal print statements in assessments.py
   - st.info/warning/success debug messages
   - st.toast notifications (or keep as user feedback)
3. Test remaining assessments (Health, Life, Medicaid)
4. Proceed to Expert Review integration testing

### If Tests Fail ❌
1. Document which specific test(s) failed
2. Capture terminal output showing the failure
3. Note exact user actions that caused failure
4. Check browser console for JavaScript errors
5. Report findings with context for debugging

## Test Report Template

Copy this template and fill it out after testing:

```
# VA Auto-Population Test Report
Date: 2025-10-18
Tester: [Your Name]
Branch: assessment-updates
Commit: [Current commit hash]

## Test Results

### Test 1: Basic (60% + Spouse)
- [ ] Dropdowns work on first click
- [ ] Amount auto-populates: $1,523.93
- [ ] Toast notification appears
- [ ] Summary shows correct total
- [ ] Terminal debug output correct
Notes: 

### Test 2: Higher Rating (70% + Spouse)
- [ ] Amount updates to $1,908.95
- [ ] No errors in terminal
Notes:

### Test 3: Complex (100% + Spouse + 2 Children)
- [ ] Amount updates to $4,405.73
- [ ] All fields work correctly
Notes:

### Test 4: No VA Disability
- [ ] Fields hide/disable appropriately
- [ ] Amount clears correctly
Notes:

### Test 5: Persistence
- [ ] Data persists across navigation
- [ ] Data persists after app restart
Notes:

## Overall Status
- [ ] All tests passed
- [ ] Some tests failed (see notes above)
- [ ] Blocked by [issue]

## Issues Encountered
[List any issues, with terminal output and steps to reproduce]

## Terminal Output Sample
[Paste relevant terminal output showing debug messages]

## Next Actions
[What needs to happen next]
```

---

## Quick Start

**Ready to test? Follow these steps:**

1. **Open browser**: http://localhost:8501
2. **Clear cache**: Cmd+Shift+R (hard refresh)
3. **Navigate**: Cost Planner v2 → VA Benefits
4. **Test**: Follow Test 1 above
5. **Watch**: Terminal output for debug messages
6. **Verify**: Field shows $1,523.93 after selecting dependents
7. **Report**: Fill out test report template above

**Good luck! 🎯**
