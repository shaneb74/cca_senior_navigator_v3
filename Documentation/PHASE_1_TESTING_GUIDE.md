# Phase 1 Complete: Testing Guide

**Date:** October 19, 2025  
**Branch:** feature/basic-advanced-mode-exploration  
**Status:** ✅ READY FOR TESTING

---

## What Was Completed

### Phase 1: Mode Engine Integration ✅
- ✅ Created `core/mode_engine.py` (471 lines) - JSON-driven mode rendering
- ✅ Enhanced `assets.json` with mode_config for 3 sections
- ✅ Integrated mode_engine into `core/assessment_engine.py` (multi-step flow)
- ✅ Integrated mode_engine into `products/cost_planner_v2/assessments.py` (single-page flow)

---

## What Changed

### Files Modified (This Session)
1. `core/mode_engine.py` (NEW) - Mode rendering engine
2. `core/assessment_engine.py` - Added mode support to multi-step flow
3. `products/cost_planner_v2/assessments.py` - Added mode support to single-page flow
4. `products/cost_planner_v2/modules/assessments/assets.json` - Enhanced 3 sections

### Sections with Mode Support (in assets.json)
1. **Liquid Assets** - Checking + Savings + Other
2. **Investments** - Mutual Funds/ETFs + Stocks/Bonds
3. **Retirement Accounts** - Traditional IRA/401(k) + Roth IRA

---

## How to Test

### Step 1: Start the App
```bash
cd /Users/shane/Desktop/cca_senior_navigator_v3
streamlit run app.py
```

### Step 2: Navigate to Assets Assessment
1. Go to Cost Planner v2
2. Click "Assessments" (or navigate to assessment hub)
3. Click "Assets & Resources" card

### Step 3: Look for Mode Toggle

#### What You Should See

**At the top of each enhanced section, you should see:**

```
┌─────────────────────────────────────────┐
│     ⚡ Basic        📊 Advanced ●       │  ← Radio button toggle
└─────────────────────────────────────────┘
```

**Followed by guidance box:**
```
┌─────────────────────────────────────────┐
│ 📊 Advanced Mode: Detailed breakdown   │
│ - Enter specific values for each       │
│ - Totals calculate automatically       │
│ - Better accuracy for complex finances │
└─────────────────────────────────────────┘
```

#### Sections That Should Have Mode Toggle
- 🏦 **Liquid Assets** (checking, savings, other)
- 📈 **Investments** (funds, stocks/bonds)
- 🏦 **Retirement Accounts** (traditional, roth)

#### Sections That Should NOT Have Mode Toggle
- 👥 **Household Context** (no mode_config)
- 🏠 **Real Estate & Other** (no mode_config)
- 💳 **Debts & Obligations** (no mode_config)

---

## Test Scenarios

### Test 1: Mode Toggle Visibility ✅
**Expected:**
- Mode toggle appears only in sections with `mode_config`
- Default mode is "Advanced" (right option selected)
- Toggle is responsive (radio buttons work)

**Steps:**
1. Open Assets assessment
2. Scroll to "Liquid Assets" section
3. Look for mode toggle above fields

**Pass Criteria:**
- ✅ Toggle visible
- ✅ "Advanced" selected by default
- ✅ Can click "Basic" option

---

### Test 2: Advanced Mode Display ✅
**Expected:**
- Detail fields visible (Checking, Savings/CDs, Other)
- Aggregate shows as calculated label (blue box)
- No input field for aggregate

**Steps:**
1. Ensure "Advanced" mode selected
2. Look at field layout

**Pass Criteria:**
- ✅ Three input fields visible (Checking, Savings, Other)
- ✅ Aggregate total displayed as label (not input)
- ✅ Aggregate updates when detail fields change

---

### Test 3: Basic Mode Input ✅
**Expected:**
- Single aggregate input field visible
- Detail fields hidden
- Distribution happens on input

**Steps:**
1. Click "Basic" mode toggle
2. Enter $100,000 in aggregate field
3. Switch back to "Advanced" mode
4. Check detail field values

**Pass Criteria:**
- ✅ Only one input field visible in Basic mode
- ✅ Value distributes evenly ($50k checking, $50k savings)
- ✅ Switching to Advanced shows distributed values

---

### Test 4: Unallocated Field Display ✅
**Expected:**
- Unallocated field appears when switching Basic → Advanced
- Shows difference between original estimate and allocated
- Action buttons present (Clear, Move to Other)

**Steps:**
1. Basic mode: Enter $100,000
2. Switch to Advanced
3. Detail fields show $50k, $50k (total $100k)
4. Edit checking to $30k
5. Look for Unallocated field

**Pass Criteria:**
- ✅ Unallocated shows $20,000 ($100k - $80k)
- ✅ Message explains it's not included in calculations
- ✅ "Clear Original" button visible
- ✅ "Move to Other" button visible

---

### Test 5: Mode Switching Feedback ✅
**Expected:**
- Success message when switching modes
- Guidance updates to reflect current mode

**Steps:**
1. Start in Advanced mode
2. Click "Basic" mode
3. Look for feedback message

**Pass Criteria:**
- ✅ Green success box appears
- ✅ Message says "Switched to Basic Mode"
- ✅ Guidance box updates (⚡ Basic Mode text)

---

### Test 6: Calculations Ignore Unallocated ✅ CRITICAL
**Expected:**
- Net Assets uses only detail fields
- Unallocated does NOT inflate total

**Steps:**
1. Basic mode: Enter $100,000
2. Switch to Advanced
3. Edit checking to $30k, savings to $40k (total $70k)
4. Unallocated shows $30k
5. Scroll to bottom, check "NET ASSETS" summary

**Pass Criteria:**
- ✅ NET ASSETS = $70,000 (NOT $100,000)
- ✅ Unallocated field visible but not in calculation
- ✅ Summary uses detail fields only

---

## Known Issues / Expected Behavior

### UI Rendering
- **Mode toggle at section level** - Each section has its own toggle
- **Mode state is per-section** - Can mix Basic/Advanced across sections
- **Distribution is even split** - Basic mode splits equally (proportional not yet implemented)

### State Management
- **Mode preference not persisted** - Resets to Advanced on page reload (future enhancement)
- **Unallocated requires switching** - Only appears after Basic → Advanced transition

### Styling
- **mode_engine uses default Streamlit widgets** - Not yet styled to match custom theme
- **Aggregate label is inline HTML** - May need CSS adjustments for consistency

---

## Troubleshooting

### Issue: Mode toggle doesn't appear
**Possible causes:**
- Section doesn't have `mode_config` in JSON
- JSON syntax error (check console)
- Caching issue (restart Streamlit)

**Fix:**
1. Check `assets.json` for `mode_config` block
2. Verify `supports_basic_advanced: true`
3. Restart app: Ctrl+C, then `streamlit run app.py`

---

### Issue: Fields don't filter by mode
**Possible causes:**
- `visible_in_modes` not set on fields
- Field keys don't match `advanced_mode_fields` list

**Fix:**
1. Check each field has `"visible_in_modes": ["advanced"]`
2. Verify field keys match exactly in mode_config

---

### Issue: Unallocated field doesn't appear
**Possible causes:**
- Haven't switched from Basic to Advanced yet
- No `_entered` value stored (need to enter value in Basic first)

**Expected behavior:**
- Only shows after entering value in Basic mode, then switching to Advanced

---

### Issue: Aggregate shows as input instead of label
**Possible causes:**
- Field type is `display_currency_aggregate` instead of `aggregate_input`
- Mode is "basic" (should show input)

**Fix:**
- Change field type to `"type": "aggregate_input"` in JSON
- Verify mode_behavior config exists

---

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Mode toggle visible in enhanced sections
- ✅ Basic mode shows single input
- ✅ Advanced mode shows detail fields
- ✅ Distribution works (even split)
- ✅ Calculations use detail fields only

### Nice to Have (Future)
- ⏳ Mode preference persistence
- ⏳ Proportional distribution strategy
- ⏳ Manual distribution modal
- ⏳ Custom styling for mode toggle
- ⏳ Animation on mode switch

---

## Next Steps After Testing

### If Tests Pass ✅
1. Enhance remaining sections (Real Estate, Debts, etc.)
2. Add mode support to Income assessment
3. Test with real user data
4. Merge to dev branch

### If Issues Found ❌
1. Document specific issues
2. Create bug fix commits
3. Re-test
4. Iterate

---

## Git Commands for Testing

### Create Test Branch
```bash
git checkout -b test/mode-toggle-validation
```

### Reset to Clean State (if needed)
```bash
git checkout feature/basic-advanced-mode-exploration
git reset --hard 9f609c8
```

### View Changes
```bash
git diff dev..feature/basic-advanced-mode-exploration
```

---

## Commit History (This Session)

```
9f609c8 feat: Add mode support to single-page assessments (Phase 1 Complete)
8ee9a73 feat: Integrate mode_engine into assessment_engine (Phase 1)
dee8c09 docs: Add JSON-driven mode implementation summary
9a55c2c feat: Implement JSON-driven mode architecture (POC)
b673662 docs: Add comprehensive Unallocated field design decision doc
70bfdb7 docs: Finalize Unallocated field architecture (10/10 solution)
559939e docs: Add comprehensive Basic/Advanced mode exploration plan
```

---

## Questions to Answer During Testing

1. **Does the mode toggle appear?** (Yes/No)
2. **Does Basic mode show single input?** (Yes/No)
3. **Does Advanced mode show detail fields?** (Yes/No)
4. **Does distribution work correctly?** (Even split? Values correct?)
5. **Does Unallocated field appear after switching?** (Yes/No)
6. **Do calculations ignore Unallocated?** (NET ASSETS correct?)
7. **Is the UI intuitive?** (User-friendly? Confusing?)
8. **Any errors in console?** (Check browser console and terminal)

---

## Contact/Feedback

After testing, please report:
- ✅ What worked well
- ❌ What didn't work
- 💡 Ideas for improvement
- 🐛 Bugs found

---

**Ready to test!** 🚀

Run `streamlit run app.py` and navigate to Assets & Resources to see the mode toggle in action!
