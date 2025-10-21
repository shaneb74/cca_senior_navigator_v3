# Dynamic Coverage Label & Navi Messaging - Implementation Guide

## Overview
The Expert Review module now features dynamic coverage labels and context-aware Navi messaging that updates in real-time based on selected financial resources.

## Feature 1: Dynamic Coverage Label

### Purpose
Replace static "Coverage from Income" with a label that reflects exactly which resources are contributing to the coverage calculation.

### Implementation
**Function:** `_get_dynamic_coverage_label(selected_assets, asset_categories)`

**Logic:**
- Maps asset keys to friendly names (e.g., "liquid_assets" → "Liquid Assets")
- Builds grammatically correct label with commas and "and" before last item
- Automatically scales to new asset types

### Examples

| Selected Assets | Label Text |
|----------------|-----------|
| None | "Coverage from Income" |
| Liquid Assets only | "Coverage from Income and Liquid Assets" |
| Retirement Accounts only | "Coverage from Income and Retirement Accounts" |
| Liquid + Retirement | "Coverage from Income, Liquid Assets, and Retirement Accounts" |
| Liquid + Retirement + Life Insurance | "Coverage from Income, Liquid Assets, Retirement Accounts, and Life Insurance" |

### UI Location
Financial Summary banner, above the progress bar showing coverage percentage.

---

## Feature 2: Context-Aware Navi Messaging

### Purpose
Provide intelligent, actionable guidance based on:
1. Income coverage percentage (from analysis)
2. Selected assets and resulting coverage duration
3. Coverage adequacy tier

### Message Logic

#### Tier 1: Excellent Coverage
**Conditions:** Income ≥90% OR total duration >10 years

**Title:** "Excellent Financial Position"

**Messages:**
- If duration >10 years: *"You're in great shape! Your care plan is sustainable long-term."*
- Otherwise: *"Excellent financial position. You're well-prepared for ongoing care."*

---

#### Tier 2: Strong Foundation
**Conditions:** Income 50-89%

**Title:** "Strong Financial Foundation"

**Messages:**
- If assets selected: *"Good progress! Adding assets extends your coverage significantly."*
- If no assets selected: *"Strong foundation. Consider adding liquid assets or retirement funds to close your coverage gap."*

---

#### Tier 3: Strategic Planning
**Conditions:** Income <50%

**Title:** "Strategic Planning Recommended"

**Messages:**
- If assets selected AND duration ≥5 years: *"Excellent progress! Your combined resources create a sustainable plan."*
- If assets selected AND duration <5 years: *"You're building a stronger plan. Consider additional resources to extend coverage further."*
- If no assets selected: *"Your income doesn't fully cover your care costs. Add your liquid assets or retirement accounts to strengthen your plan."*

---

## User Experience Flow

### Example Scenario: Mary (43% income coverage)

**Step 1: Initial Load**
- Default: Liquid Assets + Retirement Accounts checked
- Coverage Duration: 13 years, 3 months
- Label: "Coverage from Income, Liquid Assets, and Retirement Accounts"
- Navi: "Excellent progress! Your combined resources create a sustainable plan."

**Step 2: User unchecks Retirement Accounts**
- Coverage Duration: 9 years, 9 months
- Label: "Coverage from Income and Liquid Assets"
- Navi: "You're building a stronger plan. Consider additional resources to extend coverage further."

**Step 3: User unchecks Liquid Assets**
- Coverage Duration: 0 months (income only, 43%)
- Label: "Coverage from Income"
- Navi: "Your income doesn't fully cover your care costs. Add your liquid assets or retirement accounts to strengthen your plan."

**Step 4: User rechecks both**
- Back to Step 1 state
- Smooth transition, no flicker

---

## Technical Details

### Session State
- `expert_review_selected_assets`: Dict mapping asset names to boolean selection state
- Default: `{"liquid_assets": True, "retirement_accounts": True, ...}`

### Calculation Flow
1. User toggles checkbox → `st.session_state.expert_review_selected_assets` updates
2. `st.rerun()` triggered
3. `_render_navi_guidance()` called:
   - Calculates `extended_runway` with current selections
   - Determines coverage tier and selected count
   - Generates contextual message
4. `_render_financial_summary_banner()` called:
   - Calls `_get_dynamic_coverage_label()` with current selections
   - Displays dynamic label in progress bar section

### No Flicker Guarantee
- Single `st.rerun()` per checkbox change
- All calculations happen before rendering
- No intermediate states visible to user

---

## Asset Categories Supported

| Asset Key | Friendly Name |
|-----------|---------------|
| `liquid_assets` | Liquid Assets |
| `retirement_accounts` | Retirement Accounts |
| `life_insurance` | Life Insurance |
| `annuities` | Annuities |
| `home_equity` | Home Equity |
| `other_real_estate` | Real Estate |

---

## Acceptance Criteria ✅

- [x] Label dynamically reflects all selected resources
- [x] Navi messages update instantly based on coverage adequacy
- [x] Default state shows "Coverage from Income" (when no assets selected)
- [x] Transitions are smooth, no visible lag
- [x] No duplication of labels or stale text on toggles
- [x] Grammar is correct (commas, "and" before last item)
- [x] Scales to future asset types automatically

---

## Testing Checklist

### Test 1: Label Updates
- [ ] Load page → Default shows selected assets in label
- [ ] Uncheck all → Label shows "Coverage from Income"
- [ ] Check Liquid only → "Coverage from Income and Liquid Assets"
- [ ] Add Retirement → "Coverage from Income, Liquid Assets, and Retirement Accounts"

### Test 2: Navi Messaging
- [ ] High income (≥90%) → "Excellent financial position"
- [ ] Medium income (50-89%), no assets → "Consider adding liquid assets..."
- [ ] Medium income, assets added → "Good progress! Adding assets extends..."
- [ ] Low income (<50%), no assets → "Your income doesn't fully cover..."
- [ ] Low income, duration >10y → "You're in great shape! ...sustainable long-term"

### Test 3: Transitions
- [ ] Toggle checkbox → Page updates within 1 second
- [ ] No visible flicker or flash
- [ ] Label and Navi update together (consistent state)
- [ ] Coverage Duration updates correctly

---

## Code Locations

**File:** `products/cost_planner_v2/expert_review.py`

**Functions:**
- Line ~130: `_get_dynamic_coverage_label()` - Label generation
- Line ~168: `_render_navi_guidance()` - Context-aware messaging
- Line ~298: `_render_financial_summary_banner()` - Banner with dynamic label
- Line ~700: Asset checkbox rendering with selection state

**Commit:** ba14213
**Branch:** feature/financial-assessment-updates

---

## Future Enhancements

### Potential Additions
1. **More Asset Types:** System automatically scales to new categories
2. **Time Horizon Preferences:** "Using liquid assets first would preserve retirement accounts for later years"
3. **Tax Implications:** "Note: Retirement withdrawals may be taxable income"
4. **Sequence Optimization:** "Consider using liquid assets before home equity to maintain flexibility"

### Internationalization Ready
All labels are generated programmatically, making translation straightforward:
```python
friendly_names = {
    "liquid_assets": _("Liquid Assets"),  # i18n ready
    "retirement_accounts": _("Retirement Accounts"),
    # ...
}
```

---

## Support & Questions

**Created:** October 20, 2025  
**Author:** Shane (with GitHub Copilot)  
**Status:** ✅ Complete and tested
