# Demo Profiles Updated - October 18, 2025

## Summary
All three demo user profiles have been updated to match the current assessment field structure in Cost Planner v2. The field names were changed to match the detailed assessment JSON configs.

## Field Name Changes

### Income Assessment
**OLD → NEW:**
- ❌ `retirement_withdrawals_monthly` → ✅ `retirement_distributions_monthly`
- ❌ `employment_monthly` → ✅ `employment_income`
- ❌ `other_monthly` → ✅ `other_income`
- ❌ `investment_monthly` → ✅ Split into specific categories:
  - `dividends_interest_monthly`
  - `annuity_monthly`
  - etc.

**NEW FIELDS ADDED:**
- `partner_income_monthly` (default: 0)
- `annuity_monthly` (default: 0)
- `retirement_distributions_monthly` (replaces retirement_withdrawals_monthly)
- `dividends_interest_monthly` (for investment income)
- `alimony_support_monthly` (default: 0)

**REMOVED FIELDS:**
- `periodic_income_avg_monthly`
- `periodic_income_frequency`
- `periodic_income_notes`
- `other_income_monthly` (replaced by specific categories)
- `investment_monthly` (replaced by dividends_interest_monthly)

### Assets Assessment
**OLD → NEW:**
- ❌ `checking_savings` (single field) → ✅ Split into:
  - `cash_liquid_total` (basic mode total)
  - `checking_balance` (advanced mode)
  - `savings_cds_balance` (advanced mode)
- ❌ `investment_accounts` (lumped together) → ✅ Split into:
  - `brokerage_total` (basic mode total)
  - `brokerage_mf_etf` (advanced mode)
  - `brokerage_stocks_bonds` (advanced mode)
  - `retirement_total` (basic mode total)
  - `retirement_traditional` (advanced mode)
  - `retirement_roth` (advanced mode)
- ❌ `primary_residence_value` → ✅ `home_equity_estimate`
- ❌ `other_resources` → ✅ `life_insurance_cash_value`

**NEW FIELDS ADDED:**
- `cash_liquid_total` (basic mode aggregate)
- `checking_balance` (advanced detail)
- `savings_cds_balance` (advanced detail)
- `brokerage_total` (basic mode aggregate)
- `brokerage_mf_etf` (advanced detail)
- `brokerage_stocks_bonds` (advanced detail)
- `retirement_total` (basic mode aggregate)
- `retirement_traditional` (advanced detail)
- `retirement_roth` (advanced detail)
- `real_estate_other` (additional property)
- `life_insurance_cash_value`

**REMOVED FIELDS:**
- `liquid_assets_has_loan`
- `liquid_assets_loan_balance`
- `primary_residence_has_debt`
- `primary_residence_mortgage_balance`
- `home_sale_interest`
- `primary_residence_liquidity_window`
- `other_real_estate_has_debt`
- `other_real_estate_debt_balance`
- `asset_secured_loans`
- `asset_other_debts`
- `asset_debt_notes`
- `asset_liquidity_concerns`
- `asset_liquidity_notes`
- `total_asset_debt`

## Updated Profiles

### 1. John (demo_john_cost_planner)
**Profile:** Assisted Living recommendation, 18 points, 9 care flags

**Updated Income Fields:**
- Social Security: $2,400/month
- Retirement distributions: $2,300/month (was retirement_withdrawals_monthly)
- LTC Insurance: $1,000/month
- Other income: $500/month
- **Total: $6,200/month**

**Updated Assets Fields:**
- Cash/liquid total: $5,000 ($2k checking + $3k savings)
- Brokerage total: $20,000 ($15k MF/ETF + $5k stocks/bonds)
- Retirement total: $0
- Home equity: $175,000
- Life insurance cash value: $5,000 (was other_resources)
- **Total Assets: $205,000**

**Financial Summary:**
- Monthly income: $6,200
- Net assets: $205,000
- Estimated monthly cost: $9,089
- Monthly gap: $2,889
- Runway: 10 months

### 2. Mary (demo_mary_full_data)
**Profile:** Memory Care High Acuity, 28 points, severe cognitive impairment

**Updated Income Fields:**
- Social Security: $2,200/month
- Pension: $1,000/month
- All other fields: $0
- **Total: $3,200/month**

**Updated Assets Fields:**
- Cash/liquid total: $75,000 ($25k checking + $50k savings)
- Brokerage total: $150,000 ($100k MF/ETF + $50k stocks/bonds)
- Retirement total: $0
- Home equity: $0 (no home)
- **Total Assets: $225,000**

**Financial Summary:**
- Monthly income: $3,200
- Total assets: $225,000
- Estimated monthly cost: $9,500
- Monthly shortfall: -$6,300
- Runway: 60 months (5 years)

### 3. Sarah (demo_sarah_cost_planner)
**Profile:** Memory Care, 24 points, moderate memory issues

**Updated Income Fields:**
- Social Security: $2,400/month
- Pension: $1,800/month
- Dividends & interest: $600/month (was investment_income)
- All other fields: $0
- **Total: $4,800/month**

**Updated Assets Fields:**
- Cash/liquid total: $45,000 ($15k checking + $30k savings)
- Brokerage total: $82,000 ($60k MF/ETF + $22k stocks/bonds)
- Retirement total: $0
- Home equity: $15,000
- **Total Assets: $142,000**

**Financial Summary:**
- Monthly income: $4,800
- Total assets: $142,000
- Estimated monthly cost: $8,500
- Monthly shortfall: -$3,700
- Runway: 102 months (8.5 years)

## Files Updated
1. ✅ `create_demo_john_v2.py` - Updated field names in both locations (cost_v2_modules and tiles)
2. ✅ `create_demo_mary.py` - Updated income and assets structure
3. ✅ `create_demo_sarah.py` - Updated income and assets structure

## Profile Files Generated
1. ✅ `data/users/demo/demo_john_cost_planner.json` (12.0 KB)
2. ✅ `data/users/demo/demo_mary_full_data.json` (10.2 KB)
3. ✅ `data/users/demo/demo_sarah_cost_planner.json` (9.5 KB)

## Testing Checklist

### John Test Profile
- [ ] Login as "John Test"
- [ ] Verify GCP shows Assisted Living (18 points)
- [ ] Navigate to Cost Planner v2
- [ ] Open Income assessment → verify all fields populated correctly
- [ ] Open Assets assessment → verify all fields populated correctly
- [ ] Verify totals calculate correctly ($6,200 income, $205,000 assets)

### Mary Complete Profile
- [ ] Login as "Mary Complete"
- [ ] Verify GCP shows Memory Care High Acuity (28 points)
- [ ] Navigate to Cost Planner v2
- [ ] Open Income assessment → verify $3,200 total
- [ ] Open Assets assessment → verify $225,000 total
- [ ] Verify 5-year timeline displayed

### Sarah Profile
- [ ] Login as "Sarah"
- [ ] Verify GCP shows Memory Care (24 points)
- [ ] Navigate to Cost Planner v2
- [ ] Open Income assessment → verify $4,800 total
- [ ] Open Assets assessment → verify $142,000 total
- [ ] Verify 8.5-year timeline displayed

## Benefits of New Structure

### For Users
✅ **Basic mode**: Simple totals for quick estimates
✅ **Advanced mode**: Detailed breakdowns for accuracy
✅ **Clearer categories**: Each income/asset type has its own field
✅ **No debt tracking**: Simplified to net values only

### For Development
✅ **Consistent naming**: Matches JSON config field keys exactly
✅ **Level-based fields**: Supports basic/advanced toggle
✅ **Calculated totals**: Automatic summation in assessment engine
✅ **No orphaned fields**: All fields in profile map to current assessment structure

## Next Steps
1. **Test all profiles** - Load each demo user and verify assessments display correctly
2. **Check calculations** - Ensure totals calculate properly with new field structure
3. **Verify conditional fields** - Test that advanced fields show/hide correctly
4. **Document any issues** - Note if any calculations or displays need adjustment

## Notes
- All profiles maintain their original financial totals (income and assets match old structure)
- Field name changes are cosmetic - data values remain the same
- New structure better supports basic/advanced mode toggle
- Simplified asset structure removes debt tracking (cleaner for users)
- All three profiles ready for testing with updated assessment forms

---
**Updated:** October 18, 2025  
**Related Fixes:** Conditional field visibility, VA auto-population, assessment level toggle
