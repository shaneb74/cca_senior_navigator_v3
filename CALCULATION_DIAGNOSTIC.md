# Expert Review Calculation Diagnostic

## Test Scenario: Mary
- **Care Type**: Memory Care
- **Monthly Cost**: $13,972
- **Monthly Income**: $6,000 (SS + pension + benefits)
- **Monthly Shortfall**: $7,972
- **Coverage from Income**: 43% (6000/13972 = 0.429)

### Assets:
- **Liquid Assets**: $950,000
- **Retirement Accounts**: $500,000  
- **Home Equity**: $450,000 (excluded for in-home/memory care)
- **Total Available Assets**: $1,450,000 ($950k + $500k)

### Debt (if any):
- **Total Asset Debt**: $0 (assumed, needs verification)

---

## Issue 1: Progress Bar Not Displaying (43%)

**Expected**: Bar should fill 43% of width with red color
**Actual**: Bar appears empty or minimal fill

**Diagnosis**:
The CSS uses `width: {coverage_pct}%` which should be `width: 43%`.
Need to verify `coverage_pct` calculation:
```python
coverage_pct = min(analysis.coverage_percentage, 100)  # Should be 43
```

**Potential Issues**:
1. CSS variable `--surface-secondary` might be same color as progress fill
2. Progress bar might be rendering but invisible due to color conflict
3. Border-radius on inner div might be clipping the fill at low percentages

**Fix**: Check CSS colors and add min-width to progress bar inner div

---

## Issue 2: Asset Selection Not Recalculating

**Expected Flow**:
1. User unchecks "Liquid Assets" checkbox
2. Session state updates: `expert_review_selected_assets["liquid_assets"] = False`
3. Page reruns with `st.rerun()`
4. Banner calls `calculate_extended_runway()` with new selections
5. Coverage duration updates to show only selected assets

**Current Behavior**: Unchecking boxes doesn't update coverage duration

**Diagnosis Points**:
```python
# In _render_financial_summary_banner:
selected_assets = st.session_state.get("expert_review_selected_assets", {})
extended_runway = calculate_extended_runway(
    analysis.monthly_gap if analysis.monthly_gap > 0 else 0,
    selected_assets,
    analysis.asset_categories,
)
```

**Potential Issues**:
1. `st.rerun()` not being called after checkbox change
2. Session state not persisting across reruns  
3. `calculate_extended_runway()` logic error
4. Asset categories dict not matching session state keys

**Test Calculation** (Mary, with $950k liquid + $500k retirement selected):
```
monthly_gap = $7,972
total_selected = $1,450,000
extended_runway = 1,450,000 / 7,972 = 181.9 months = 15 years, 2 months
```

**If only $950k liquid selected**:
```
extended_runway = 950,000 / 7,972 = 119.2 months = 9 years, 11 months ✅ (matches screenshot)
```

This suggests retirement accounts ($500k) are NOT being selected by default, which is correct behavior.

---

## Issue 3: Debt Not Displayed or Calculated

**Current State**:
- `FinancialProfile` has `total_asset_debt` field
- Debt is calculated in assessment phase
- Expert Review does NOT display debt or adjust asset values

**Expected Behavior**:
1. Show debt total in Financial Summary banner
2. Display: `Total Assets (Gross)` - `Debts Against Assets` = `Net Available Assets`
3. Use NET values in all calculations

**Proposed UI Addition**:
```
💰 FINANCIAL SUMMARY
────────────────────
Coverage Duration: 9 years, 11 months
Estimated Care Cost: $13,972/month

Monthly Income: $6,000/month
Monthly Shortfall: $7,972/month

Total Assets: $1,450,000
Less: Debts: $0
Net Available: $1,450,000

Coverage from Income: 43% [===········]
```

**Calculation Impact**:
If Mary had $50k in debts:
- Gross Assets: $1,450,000
- Less Debts: $50,000
- Net Assets: $1,400,000
- Extended Runway: 1,400,000 / 7,972 = 175.6 months = 14 years, 8 months

---

## Issue 4: Coverage Percentage Calculation Review

**Formula**:
```python
coverage_percentage = (total_monthly_income / estimated_monthly_cost) * 100
coverage_percentage = (6000 / 13972) * 100 = 42.94% ✅ Correct
```

**Displayed**: 43% (rounded) ✅

---

## Issue 5: Runway Months Calculation Review

**Formula**:
```python
if monthly_gap > 0:
    runway_months = total_liquid_assets / monthly_gap
else:
    runway_months = None  # Indefinite coverage
```

**Mary's Base Calculation** (without selected assets):
```python
monthly_gap = 13972 - 6000 = 7972
total_liquid_assets = 950000 (liquid only, not counting retirement/home)
runway_months = 950000 / 7972 = 119.2 months = 9 years, 11 months ✅
```

This matches the screenshot! So base calculation is CORRECT.

---

## Issue 6: Extended Runway with Selections

**What SHOULD happen** when user checks retirement accounts:
```python
selected_assets = {"liquid_assets": True, "retirement_accounts": True}
total_selected = 950000 + 500000 = 1,450,000
extended_runway = 1,450,000 / 7,972 = 181.9 months = 15 years, 2 months
```

**Banner should show**:
- Coverage Duration: **15 years, 2 months** (not 9 years, 11 months)
- With note: "+ Assets: $1,450,000"

**If this is NOT happening**, the issue is in:
1. Checkbox state not updating
2. `st.rerun()` not triggering
3. Banner not reading updated session state

---

## Recommended Fixes:

### 1. Progress Bar Fix
```python
# Add minimum visibility and contrast
progress_html = f"""
<div style="width: 100%; background: #e0e0e0; border-radius: 12px; height: 32px; position: relative; overflow: hidden; box-shadow: inset 0 2px 6px rgba(0,0,0,0.1);">
<div style="width: {max(coverage_pct, 2)}%; background: linear-gradient(90deg, {progress_color} 0%, {progress_color}dd 100%); min-width: 40px; height: 100%; border-radius: 12px; ...">
```

### 2. Asset Selection Debug
Add logging to track session state:
```python
if new_selection != current_selection:
    st.session_state.expert_review_selected_assets[cat_name] = new_selection
    print(f"DEBUG: Updated {cat_name} = {new_selection}")
    print(f"DEBUG: Full state = {st.session_state.expert_review_selected_assets}")
    st.rerun()
```

### 3. Add Debt Display
In `_render_financial_summary_banner`:
```python
# After coverage duration section, add:
if profile.total_asset_debt > 0:
    debt_section = f"""
    <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border-secondary);">
    <div style="display: flex; justify-content: space-between;">
    <span>Total Assets (Gross)</span>
    <span>${total_assets_gross:,.0f}</span>
    </div>
    <div style="display: flex; justify-content: space-between; color: var(--error-fg);">
    <span>Less: Debts Against Assets</span>
    <span>-${profile.total_asset_debt:,.0f}</span>
    </div>
    <div style="display: flex; justify-content: space-between; font-weight: 700; margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border-secondary);">
    <span>Net Available Assets</span>
    <span>${net_assets:,.0f}</span>
    </div>
    </div>
    """
```

### 4. Calculation Audit Checklist
- ✅ Coverage percentage: (income/cost) * 100 = 43%
- ✅ Monthly gap: cost - income = $7,972
- ✅ Base runway: liquid_assets / gap = 119 months
- ⚠️ Extended runway: selected_assets / gap (needs testing)
- ❌ Debt adjustment: currently not applied
- ❌ Progress bar visibility: CSS issue

---

## Next Steps:
1. ✅ Fix progress bar CSS (min-width, background color)
2. ✅ Add debt display section to banner
3. ✅ CRITICAL BUG FOUND: Asset category mismatch between base and extended calculations
4. ⚠️ Test checkbox behavior with new default selections
5. ⚠️ Verify calculations match expectations

---

## CRITICAL BUG DISCOVERED

**Root Cause**: Mismatch between base `runway_months` and `extended_runway` calculations

### Base Calculation (`analysis.runway_months`):
```python
total_liquid_assets = (
    profile.checking_savings
    + profile.investment_accounts
    + profile.other_real_estate          # ← INCLUDED!
    + profile.other_resources
    + profile.total_accessible_life_value
)
runway_months = total_liquid_assets / monthly_gap
```

### Asset Categories ("Liquid Assets" checkbox):
```python
liquid_balance = profile.checking_savings + profile.investment_accounts
# ← Does NOT include other_real_estate!
```

**Problem**: `analysis.runway_months` (9y 11m) includes MORE assets than just "Liquid Assets" checkbox.

**Fix Applied**:
1. Changed banner to ALWAYS use `extended_runway` (checkbox-based calculation)
2. Removed fallback to `analysis.runway_months` (inconsistent definition)
3. Default selections: Liquid Assets + Retirement Accounts checked
4. This makes the calculation transparent: duration = selected assets / gap

**Expected Behavior After Fix**:
- Page loads: Liquid + Retirement checked → Duration shows combined value
- Uncheck Liquid: Duration decreases (only retirement counted)
- Uncheck Retirement: Duration decreases further (only liquid counted)
- Check both: Duration increases (both counted)

**Test Scenario** (Mary):
- Monthly Gap: $7,972
- Liquid Assets: $950,000 × 0.98 = $931,000
- Retirement: $500,000 × 0.68 = $340,000
- Combined: $1,271,000
- Expected Duration: 1,271,000 / 7,972 = 159.4 months = **13 years, 3 months**

If only Liquid checked:
- 931,000 / 7,972 = 116.8 months = **9 years, 9 months**

If only Retirement checked:
- 340,000 / 7,972 = 42.7 months = **3 years, 7 months**
