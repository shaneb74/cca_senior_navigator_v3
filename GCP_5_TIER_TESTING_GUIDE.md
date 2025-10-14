# GCP 5-Tier System - Testing Guide

**Date:** October 14, 2025  
**Commit:** 72c5f0c  
**Status:** Ready for Testing

---

## Quick Testing Checklist

### ✅ Pre-Test Setup
- [ ] App restarted with new code
- [ ] Clear session state (`Ctrl+R` in browser)
- [ ] Have Cost Planner V2 feature flag enabled

### ✅ Core GCP Tests

#### Test 1: No Care Needed (0-8 points)
**Goal:** Answer questions to get 0-8 total points

**Sample Answers:**
- Cognition: "No issues" (0 pts)
- Wandering: "Never happens" (0 pts)
- Falls: "None in past year" (0 pts)
- ADLs: "Independent in all" (0 pts)
- IADLs: "Independent in all" (0 pts)
- Medical: "No chronic conditions" (0 pts)
- Behavioral: "None" (0 pts)

**Expected Result:**
```
Based on 5 points, we recommend: No Care Needed

✓ No formal care is needed at this time. If circumstances 
  change, return to update your assessment.
```

**Verify:**
- [ ] Tier displays as "No Care Needed"
- [ ] Special message shown
- [ ] No errors in terminal
- [ ] MCIP shows "No Care Needed" in summary

---

#### Test 2: In-Home Care (9-16 points)
**Goal:** Answer questions to get 9-16 total points

**Sample Answers:**
- Cognition: "Minor forgetfulness" (2 pts)
- Falls: "1-2 in past year" (3 pts)
- ADLs: "Needs help with 1-2" (4 pts)
- IADLs: "Needs help with cooking" (3 pts)
- Medical: "1 chronic condition" (2 pts)

**Expected Result:**
```
Based on 14 points, we recommend: In-Home Care
```

**Verify:**
- [ ] Tier displays as "In-Home Care"
- [ ] Rationale makes sense for in-home needs
- [ ] No errors in terminal

---

#### Test 3: Assisted Living (17-24 points)
**Goal:** Answer questions to get 17-24 total points

**Sample Answers:**
- Cognition: "Moderate memory loss" (5 pts)
- Falls: "3+ in past year" (5 pts)
- ADLs: "Needs help with 3-4" (6 pts)
- IADLs: "Needs help with most" (5 pts)
- Medical: "2-3 chronic conditions" (4 pts)

**Expected Result:**
```
Based on 20 points, we recommend: Assisted Living
```

**Verify:**
- [ ] Tier displays as "Assisted Living"
- [ ] Rationale explains structured environment need
- [ ] No errors in terminal

---

#### Test 4: Memory Care (25-39 points)
**Goal:** Answer questions to get 25-39 total points

**Sample Answers:**
- Cognition: "Severe memory loss" (8 pts)
- Wandering: "Happens frequently" (8 pts)
- Falls: "3+ with injuries" (6 pts)
- ADLs: "Needs help with most" (8 pts)
- Behavioral: "Moderate agitation" (6 pts)
- Medical: "3+ chronic conditions" (5 pts)

**Expected Result:**
```
Based on 30 points, we recommend: Memory Care
```

**Verify:**
- [ ] Tier displays as "Memory Care"
- [ ] Rationale mentions cognitive decline
- [ ] No errors in terminal

---

#### Test 5: Memory Care (High Acuity) (40-100 points)
**Goal:** Answer questions to get 40+ total points

**Sample Answers:**
- Cognition: "Severe dementia" (10 pts)
- Wandering: "High risk, elopement attempts" (10 pts)
- Falls: "Frequent, multiple injuries" (8 pts)
- ADLs: "Fully dependent in all" (10 pts)
- Behavioral: "Severe aggression" (10 pts)
- Medical: "Complex medical needs" (8 pts)
- Incontinence: "Yes, frequent" (5 pts)

**Expected Result:**
```
Based on 45 points, we recommend: Memory Care (High Acuity)
```

**Verify:**
- [ ] Tier displays as "Memory Care (High Acuity)"
- [ ] Rationale explains intensive care needs
- [ ] No errors in terminal

---

### ✅ Boundary Testing

#### Boundary 1: 8 points → no_care_needed
- Answer to get exactly 8 points
- **Expected:** "No Care Needed"

#### Boundary 2: 9 points → in_home
- Answer to get exactly 9 points
- **Expected:** "In-Home Care"

#### Boundary 3: 16 points → in_home
- Answer to get exactly 16 points
- **Expected:** "In-Home Care"

#### Boundary 4: 17 points → assisted_living
- Answer to get exactly 17 points
- **Expected:** "Assisted Living"

#### Boundary 5: 24 points → assisted_living
- Answer to get exactly 24 points
- **Expected:** "Assisted Living"

#### Boundary 6: 25 points → memory_care
- Answer to get exactly 25 points
- **Expected:** "Memory Care"

#### Boundary 7: 39 points → memory_care
- Answer to get exactly 39 points
- **Expected:** "Memory Care"

#### Boundary 8: 40 points → memory_care_high_acuity
- Answer to get exactly 40 points
- **Expected:** "Memory Care (High Acuity)"

---

### ✅ Cost Planner Integration

#### Test 6: GCP → Cost Planner Flow
1. Complete GCP (any tier)
2. Navigate to Cost Planner
3. **Expected:** Tier pre-filled in "Coming from GCP" mode
4. Calculate cost
5. **Expected:** Pricing matches tier

**Verify Each Tier:**
- [ ] No Care Needed → ~$500/month base
- [ ] In-Home Care → ~$3,500/month base
- [ ] Assisted Living → ~$4,500/month base
- [ ] Memory Care → ~$6,500/month base
- [ ] Memory Care (High Acuity) → ~$9,000/month base

#### Test 7: Cost Planner Quick Estimate (No GCP)
1. Navigate to Cost Planner directly (not from GCP)
2. **Expected:** Dropdown shows all 5 care types
3. Select each tier and calculate cost
4. **Expected:** Pricing correct for each

**Verify Dropdown Options:**
- [ ] "No Care Needed" present
- [ ] "In-Home Care" present
- [ ] "Assisted Living" present
- [ ] "Memory Care" present
- [ ] "Memory Care (High Acuity)" present
- [ ] No "Independent Living" or "Skilled Nursing"

---

### ✅ Hub & MCIP Integration

#### Test 8: Hub Summary Display
1. Complete GCP (any tier)
2. Return to Hub (via "Back to Hub" or breadcrumbs)
3. Check GCP tile
4. **Expected:** Shows tier name correctly

**Verify:**
- [ ] No Care Needed → "No Care Needed"
- [ ] In-Home Care → "In-Home Care"
- [ ] Assisted Living → "Assisted Living"
- [ ] Memory Care → "Memory Care"
- [ ] Memory Care (High Acuity) → "Memory Care (High Acuity)"

#### Test 9: Concierge Hub Reason
1. Complete GCP with recommendation
2. Navigate to Concierge Hub
3. Check "Why you're here" section
4. **Expected:** Shows tier in personalized message

---

### ✅ Confidence Improvement Display

#### Test 10: View Confidence Improvement
1. Complete GCP (17 points → Assisted Living)
2. View results page
3. Look for "Improve Your Confidence" section
4. **Expected:** Shows tier boundaries correctly

**For 17 points (boundary case):**
- **Expected:** "Clarity: 0% - you're exactly at the boundary"
- **Next tier:** "17 points from Memory Care"

**For 20 points (mid-range):**
- **Expected:** "Clarity: 62.5% - moderate distance from boundaries"

---

### ✅ Navigation & Back Button

#### Test 11: Back Button Navigation
1. Start GCP
2. Go to second question
3. **Expected:** "← Back to Previous Question" button shown
4. Click back
5. **Expected:** Returns to first question
6. **Expected:** Previous answer preserved

**Verify:**
- [ ] No back button on intro page
- [ ] No back button on first question
- [ ] Back button appears on Q2+
- [ ] Back button works correctly
- [ ] Position: Above "Save & Continue Later"

---

### ✅ Navi Integration

#### Test 12: Navi Panel Context
1. Complete GCP (any tier)
2. Open Navi panel
3. **Expected:** Navi aware of care recommendation
4. Ask: "What care do I need?"
5. **Expected:** Navi responds with your tier

**Verify:**
- [ ] Navi uses correct tier name
- [ ] No "Independent Living" or "Skilled Nursing" in response

---

### ✅ Error Testing

#### Test 13: Validation Function
This is internal validation - if it fails, you'll see errors in terminal:

**Expected:** No errors like:
```
ValueError: Invalid tier 'skilled_nursing' - must be one of {...}
```

**If you see errors:**
- Check terminal output
- Look for stack trace
- Verify which function raised ValueError
- Report in GitHub issue

---

### ✅ Legacy Data Handling

#### Test 14: Old Tier Data (If Exists)
If you have old session data with tier="independent":

1. Navigate to Hub
2. Check GCP tile
3. **Expected:** Either:
   - Displays as "Independent" (fallback)
   - Or prompts to retake GCP

**Future Enhancement:** Add migration banner

---

## Regression Testing

### Test 15: Core Features Still Work
- [ ] GCP intro page loads
- [ ] Questions display correctly
- [ ] Progress bar works
- [ ] Save & Continue Later works
- [ ] Results page renders
- [ ] Rationale sections show
- [ ] Regional data loads (if enabled)
- [ ] Cost Planner launches
- [ ] Navi panel works
- [ ] Hub tile updates

---

## Performance Testing

### Test 16: Load Times
- [ ] GCP intro: < 1s
- [ ] Question pages: < 0.5s
- [ ] Results calculation: < 2s
- [ ] Cost Planner: < 1s
- [ ] Hub refresh: < 0.5s

---

## Terminal Checks

### Test 17: No Errors in Console
While testing, watch terminal for:

**❌ Bad (Report These):**
```
ValueError: Invalid tier 'skilled_nursing'
KeyError: 'independent_living'
AttributeError: 'NoneType' object has no attribute 'tier'
```

**✅ Good (Expected):**
```
[INFO] GCP: Calculated tier 'memory_care' from score 30
[INFO] MCIP: Updated care_recommendation with tier
[INFO] Cost Planner: Using tier 'memory_care' for estimates
```

---

## Browser Console Checks

### Test 18: No JS Errors
Open browser console (F12) and check for:

**❌ Bad:**
```
Uncaught TypeError: Cannot read property 'tier'
404 errors for static assets
```

**✅ Good:**
```
Streamlit connected
No console errors
```

---

## Documentation Verification

### Test 19: Check User-Facing Text
Search UI for any remaining legacy terms:

**❌ Should NOT appear:**
- "Independent Living" (as a care tier)
- "Skilled Nursing" (as a care tier)

**✅ Should appear:**
- "No Care Needed"
- "In-Home Care"
- "Assisted Living"
- "Memory Care"
- "Memory Care (High Acuity)"

**Note:** "skilled nursing" in FAQ about Medicare is OK (that's about Medicare coverage, not our tier system)

---

## Test Results Template

```markdown
## Test Results - [Date]

### Environment
- Commit: 72c5f0c
- Branch: feature/cost_planner_v2
- Python: 3.11.x
- Streamlit: 1.x.x

### Test 1: No Care Needed (0-8 points)
- Status: ✅ PASS / ❌ FAIL
- Score: X points
- Tier: "No Care Needed"
- Special Message: Shown
- Notes: [any observations]

### Test 2: In-Home Care (9-16 points)
- Status: ✅ PASS / ❌ FAIL
- Score: X points
- Tier: "In-Home Care"
- Notes: [any observations]

[... continue for all tests ...]

### Issues Found
1. [Issue description]
   - Severity: High / Medium / Low
   - Steps to reproduce
   - Expected vs. actual behavior

### Overall Assessment
- Core functionality: ✅ Working / ❌ Broken
- Tier accuracy: ✅ Correct / ❌ Issues
- Integration: ✅ Smooth / ❌ Problems
- Ready for production: ✅ YES / ❌ NO
```

---

## Known Issues / Expected Behaviors

### OK to See:
1. **FAQ references "skilled nursing"** in Medicare context
   - This is about Medicare coverage, not our tier system
   - OK to keep

2. **Old Cost Planner (v1)** may have legacy tier names
   - Located in `products/cost_planner/` (not v2)
   - Not actively used
   - Can be archived later

3. **Documentation files** (.md) may reference old tiers
   - These are historical records
   - Can be updated or archived
   - Not user-facing

### NOT OK to See:
1. **GCP results** showing "Independent Living" or "Skilled Nursing"
2. **Cost Planner dropdown** with legacy tier names
3. **Hub tile** with legacy tier names
4. **Navi responses** with legacy tier names
5. **Terminal errors** about invalid tiers

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Update this document with test results
2. Create production deployment plan
3. Update user-facing documentation
4. Plan data migration for legacy users
5. Monitor production logs for issues

### If Tests Fail ❌
1. Document exact failures
2. Check terminal and browser console for errors
3. Review code changes for missed mappings
4. Fix issues and re-test
5. Do NOT deploy until all tests pass

---

## Emergency Rollback Plan

If critical issues found in production:

1. **Immediate:** Revert commit 72c5f0c
   ```bash
   git revert 72c5f0c
   git push origin feature/cost_planner_v2
   ```

2. **Restart app** with reverted code

3. **Investigate** what went wrong

4. **Fix** in separate branch

5. **Re-test** thoroughly before re-deploying

---

**Status:** Ready for Testing ✅  
**Tester:** [Your Name]  
**Date:** [Test Date]  
**Duration:** [Estimated 30-45 minutes for full test suite]

