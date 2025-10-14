# Cost Planner Quick Estimate - Testing Guide

**Commit:** c4989c2  
**Date:** October 14, 2025  
**Status:** Ready for Testing

---

## Quick Test Flow (5 minutes)

### Test 1: Basic Flow (No GCP)
1. Navigate to Cost Planner (unauthenticated)
2. **Expected:** "Get a Quick Cost Estimate" page loads
3. **Expected:** Care type selector shows exactly 5 options:
   - No Care Recommended
   - In-Home Care
   - Assisted Living
   - Memory Care
   - Memory Care (High Acuity)
4. **Expected:** Single ZIP code field (NO State field)
5. Enter ZIP: `90210`
6. Select: "Assisted Living"
7. Click "🔍 Calculate Quick Estimate"
8. **Expected:** Line-item breakdown appears:
   - Base Cost (Assisted Living): $4,500/month
   - Regional Adjustment (ZIP 90210): +X%
   - = Adjusted Total: $Y,YYY/month
9. **Expected:** Reassurance copy: "We know these numbers can feel overwhelming..."
10. **Expected:** CTA button: "➡️ Continue to Full Assessment"

✅ **PASS if:** All expected elements present, no errors in terminal

---

### Test 2: GCP Recommendation Seeding
1. Complete GCP first → get recommendation (e.g., "Memory Care")
2. Navigate to Cost Planner
3. **Expected:** Caption shows: "💡 Based on your Guided Care Plan, we've pre-selected: Memory Care"
4. **Expected:** Dropdown pre-selected to "Memory Care"
5. Enter ZIP code
6. Click Calculate
7. **Expected:** Estimate shows for Memory Care

✅ **PASS if:** GCP recommendation pre-fills selector correctly

---

### Test 3: Condition-Based Add-Ons
**Setup:** Complete GCP with cognitive issues → should set `memory_support` flag

1. Navigate to Cost Planner
2. Enter ZIP code
3. Click Calculate
4. **Expected:** Breakdown shows:
   - Base Cost
   - Regional Adjustment
   - **+ Cognitive-related Adjustment: +20%**
   - = Adjusted Total

**Setup:** Complete GCP with mobility issues → should set `mobility_limited` flag

5. Recalculate
6. **Expected:** Breakdown shows:
   - Base Cost
   - Regional Adjustment
   - **+ Cognitive-related Adjustment: +20%**
   - **+ Mobility-related Adjustment: +15%**
   - = Adjusted Total

✅ **PASS if:** Add-ons appear only when flags are present

---

### Test 4: High-Acuity Add-On
1. Select care type: "Memory Care (High Acuity)"
2. Enter ZIP code
3. Click Calculate
4. **Expected:** Breakdown shows:
   - Base Cost (Memory Care High Acuity): $9,000/month
   - Regional Adjustment
   - **+ High-Acuity Adjustment: +25%**
   - = Adjusted Total

✅ **PASS if:** +25% add-on always appears for High Acuity tier

---

### Test 5: Scenario Switching
1. Complete GCP → get recommendation "Assisted Living"
2. Navigate to Cost Planner → pre-selected "Assisted Living"
3. Enter ZIP, Calculate → see estimate
4. Change dropdown to "In-Home Care"
5. Click Calculate again
6. **Expected:** New estimate for In-Home Care
7. Navigate away and back to Cost Planner
8. **Expected:** Still pre-selected "Assisted Living" (original GCP rec not overwritten)

✅ **PASS if:** User can preview different scenarios without losing GCP rec

---

### Test 6: ZIP Validation
1. Enter ZIP: `123` (too short)
2. Click Calculate
3. **Expected:** Error: "Please enter a valid 5-digit ZIP code, or leave it blank."
4. Clear ZIP (leave blank)
5. Click Calculate
6. **Expected:** Works with national average

✅ **PASS if:** Validation works, blank ZIP allowed

---

### Test 7: No Add-Ons Message
1. Complete GCP with no flags (low scores, no issues)
2. Navigate to Cost Planner
3. Select "In-Home Care"
4. Enter ZIP, Calculate
5. **Expected:** Breakdown shows:
   - Base Cost
   - Regional Adjustment
   - **ℹ️ No additional care adjustments applied for your area.**
   - = Adjusted Total

✅ **PASS if:** Message appears when no add-ons apply

---

### Test 8: Legacy Terms Removed
Search entire UI for these terms (should NOT appear):
- ❌ "Independent Living" (as a care tier option)
- ❌ "Skilled Nursing" (as a care tier option)

**Allowed references:**
- ✅ "skilled nursing" in Medicare context (e.g., "Medicare covers short-term skilled nursing")

✅ **PASS if:** No legacy tier names in Quick Estimate UI

---

### Test 9: Math Validation
**Example:** Memory Care, ZIP 90210 (15% regional), with cognitive (+20%) and mobility (+15%)

**Expected Calculation:**
```
Base: $6,500
After regional (15%): $6,500 × 1.15 = $7,475
After cognitive (+20%): $7,475 × 1.20 = $8,970
After mobility (+15%): $8,970 × 1.15 = $10,315.50
Total: $10,315.50/month
```

**Verify:**
- Base cost line: $6,500
- Regional line: +15% ($975)
- Cognitive line: +20% ($1,495)
- Mobility line: +15% ($1,345.50)
- **Total: $10,315.50**

✅ **PASS if:** Math is correct (cumulative add-ons)

---

### Test 10: CTA Navigation
1. Calculate estimate
2. Click "➡️ Continue to Full Assessment"
3. **Expected:** Navigates to authentication page (or Full Assessment if already logged in)
4. **Expected:** Context preserved (care type, ZIP)

✅ **PASS if:** CTA triggers correct workflow

---

## Terminal Checks

While testing, watch terminal for:

**❌ Bad (Report These):**
```
KeyError: 'memory_support'
AttributeError: 'NoneType' has no attribute 'flags'
ValueError: Invalid care tier
```

**✅ Good (Expected):**
```
[INFO] Cost Planner: Calculated estimate for memory_care
[INFO] MCIP: Retrieved care_recommendation with 2 flags
```

---

## Browser Console Checks

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

## Test Results Template

```markdown
## Test Results - [Date]

**Tester:** [Your Name]  
**Commit:** c4989c2  
**Environment:** Local / Dev / Prod

### Test 1: Basic Flow
- Status: ✅ PASS / ❌ FAIL
- Notes: [observations]

### Test 2: GCP Seeding
- Status: ✅ PASS / ❌ FAIL
- GCP Tier: [tier name]
- Pre-selected: [yes/no]
- Notes: [observations]

### Test 3: Condition Add-Ons
- Status: ✅ PASS / ❌ FAIL
- Flags Present: [list flags]
- Add-ons Shown: [list add-ons]
- Notes: [observations]

### Test 4: High-Acuity Add-On
- Status: ✅ PASS / ❌ FAIL
- +25% shown: [yes/no]
- Notes: [observations]

### Test 5: Scenario Switching
- Status: ✅ PASS / ❌ FAIL
- GCP rec preserved: [yes/no]
- Notes: [observations]

### Test 6: ZIP Validation
- Status: ✅ PASS / ❌ FAIL
- Validation works: [yes/no]
- Blank allowed: [yes/no]
- Notes: [observations]

### Test 7: No Add-Ons Message
- Status: ✅ PASS / ❌ FAIL
- Message shown: [yes/no]
- Notes: [observations]

### Test 8: Legacy Terms
- Status: ✅ PASS / ❌ FAIL
- Found any: [yes/no - list if yes]
- Notes: [observations]

### Test 9: Math Validation
- Status: ✅ PASS / ❌ FAIL
- Calculation correct: [yes/no]
- Expected: $X,XXX
- Actual: $Y,YYY
- Notes: [observations]

### Test 10: CTA Navigation
- Status: ✅ PASS / ❌ FAIL
- Navigates correctly: [yes/no]
- Context preserved: [yes/no]
- Notes: [observations]

### Issues Found
1. [Issue description]
   - Severity: High / Medium / Low
   - Steps to reproduce
   - Expected vs. actual

### Overall Assessment
- All tests passing: ✅ YES / ❌ NO
- Ready for production: ✅ YES / ❌ NO
- Blockers: [list any blockers]
```

---

## Quick Smoke Test (1 minute)

1. Go to Cost Planner
2. See 5 care types (no legacy types)
3. Enter ZIP
4. Calculate
5. See line-item breakdown
6. No errors in terminal

✅ **If all pass:** Ready for production

---

**Next:** Run through all 10 test cases and document results!

