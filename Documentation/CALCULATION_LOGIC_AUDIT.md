# Financial Assessment Calculation Logic Audit

**Date:** October 19, 2025  
**Branch:** `feature/calculation-verification`  
**Purpose:** Verify all income, asset, debt, and benefit calculations are correctly summed

---

## Executive Summary

### ✅ FINDINGS: Calculation Issues Identified

After comprehensive code review, I've identified **critical gaps** in the calculation logic:

1. **Income Assessment**: Missing several advanced income fields in total calculation
2. **Assets Assessment**: Duplicated summation between basic/advanced fields (double-counting)
3. **VA Benefits**: Correctly calculated and added to total income ✅
4. **Asset/Debt Balance**: Core logic is correct but uses wrong field names

---

## Detailed Analysis

### 1. Income Assessment Calculation

#### Configuration (income.json)

**Summary Formula:**
```json
"formula": "sum(ss_monthly, pension_monthly, employment_income, other_income, annuity_monthly, retirement_distributions_monthly, dividends_interest_monthly, rental_income_monthly, alimony_support_monthly, ltc_insurance_monthly, family_support_monthly, partner_income_monthly)"
```

#### Calculation Function (`financial_helpers.py`)

**Function:** `calculate_total_monthly_income()`

```python
return sum([
    normalized.get("ss_monthly", 0.0),
    normalized.get("pension_monthly", 0.0),
    normalized.get("employment_monthly", 0.0),
    normalized.get("retirement_withdrawals_monthly", 0.0),
    normalized.get("rental_income_monthly", 0.0),
    normalized.get("ltc_insurance_monthly", 0.0),
    normalized.get("family_support_monthly", 0.0),
    normalized.get("partner_income_monthly", 0.0),
    normalized.get("periodic_income_avg_monthly", 0.0),
    normalized.get("other_monthly", 0.0),
])
```

#### ❌ ISSUE #1: Field Name Mismatches

The JSON config and calculation function use **different field names**:

| JSON Config Field | Calculation Function Field | Status |
|------------------|---------------------------|--------|
| `employment_income` | `employment_monthly` | ❌ MISMATCH |
| `other_income` | `other_monthly` | ❌ MISMATCH |
| `annuity_monthly` | ❌ MISSING | ❌ NOT INCLUDED |
| `retirement_distributions_monthly` | `retirement_withdrawals_monthly` | ❌ MISMATCH |
| `dividends_interest_monthly` | ❌ MISSING | ❌ NOT INCLUDED |
| `alimony_support_monthly` | ❌ MISSING | ❌ NOT INCLUDED |
| N/A | `periodic_income_avg_monthly` | ⚠️ EXTRA (not in JSON) |

**Impact:**
- Users entering income in advanced fields (annuity, dividends, alimony) will see **incorrect totals**
- Income summary on assessment page will be **wrong**
- Expert review total monthly income will be **understated**
- Financial gap analysis will show **incorrect funding shortfall**

**Root Cause:**
The JSON field definitions don't match the calculation logic in `financial_helpers.py`. The calculation function expects different field names than what the UI widgets create.

---

### 2. Assets Assessment Calculation

#### Configuration (assets.json)

**Summary Formula:**
```json
"formula": "sum(cash_liquid_total, brokerage_total, retirement_total, home_equity_estimate, checking_balance, savings_cds_balance, brokerage_mf_etf, brokerage_stocks_bonds, retirement_traditional, retirement_roth, real_estate_other, life_insurance_cash_value)"
```

#### Calculation Function (`financial_helpers.py`)

**Function:** `calculate_total_asset_value()`

```python
return sum([
    data.get("checking_savings", 0.0),
    data.get("investment_accounts", 0.0),
    data.get("primary_residence_value", 0.0),
    data.get("other_real_estate", 0.0),
    data.get("other_resources", 0.0),
])
```

#### ❌ ISSUE #2: Complete Disconnect Between Config and Calculation

The JSON config and calculation function use **entirely different field sets**:

| JSON Config Fields | Calculation Function Fields | Problem |
|-------------------|----------------------------|---------|
| `cash_liquid_total` | `checking_savings` | ❌ Different names |
| `checking_balance` | ❌ IGNORED | ❌ Not used |
| `savings_cds_balance` | ❌ IGNORED | ❌ Not used |
| `brokerage_total` | `investment_accounts` | ❌ Different names |
| `brokerage_mf_etf` | ❌ IGNORED | ❌ Not used |
| `brokerage_stocks_bonds` | ❌ IGNORED | ❌ Not used |
| `retirement_total` | ❌ IGNORED | ❌ Not used |
| `retirement_traditional` | ❌ IGNORED | ❌ Not used |
| `retirement_roth` | ❌ IGNORED | ❌ Not used |
| `home_equity_estimate` | `primary_residence_value` | ❌ Different names |
| `real_estate_other` | `other_real_estate` | ✅ MATCH |
| `life_insurance_cash_value` | `other_resources` | ⚠️ Possible mismatch |
| N/A | `primary_residence_value` | ⚠️ Extra field |

#### ❌ ISSUE #3: Duplicate Summation (Double-Counting)

The JSON formula includes **BOTH basic and advanced fields**:

**Basic Fields (Total):**
- `cash_liquid_total` (sum of checking + savings)
- `brokerage_total` (sum of funds + stocks)
- `retirement_total` (sum of traditional + roth)
- `home_equity_estimate`

**Advanced Fields (Breakdown):**
- `checking_balance`
- `savings_cds_balance`
- `brokerage_mf_etf`
- `brokerage_stocks_bonds`
- `retirement_traditional`
- `retirement_roth`

**Problem:**
If a user enters both basic totals AND advanced breakdowns, the formula will **double-count** these values.

Example:
```
User enters:
- cash_liquid_total = $50,000 (basic)
- checking_balance = $30,000 (advanced)
- savings_cds_balance = $20,000 (advanced)

Formula sums: $50,000 + $30,000 + $20,000 = $100,000 ❌
Actual assets: $50,000 ✅
```

**Impact:**
- Asset totals will be **massively inflated** if users fill out advanced fields
- Medicaid eligibility calculations will be **wrong**
- Net worth calculations will be **incorrect**
- Financial recommendations will be **based on false data**

---

### 3. Asset Debt Calculation

#### Calculation Function (`financial_helpers.py`)

**Function:** `calculate_total_asset_debt()`

```python
return sum([
    data.get("liquid_assets_loan_balance", 0.0),
    data.get("primary_residence_mortgage_balance", 0.0),
    data.get("other_real_estate_debt_balance", 0.0),
    data.get("asset_secured_loans", 0.0),
    data.get("asset_other_debts", 0.0),
])
```

#### ⚠️ ISSUE #4: Field Names Don't Exist in JSON Config

**Assets JSON has NO debt fields defined!**

The calculation expects:
- `liquid_assets_loan_balance` - ❌ NOT IN CONFIG
- `primary_residence_mortgage_balance` - ❌ NOT IN CONFIG
- `other_real_estate_debt_balance` - ❌ NOT IN CONFIG
- `asset_secured_loans` - ❌ NOT IN CONFIG
- `asset_other_debts` - ❌ NOT IN CONFIG

The JSON only has:
- `home_equity_estimate` (already net of mortgage)
- No dedicated debt fields

**Impact:**
- Asset debt will **always be $0**
- Net asset calculation will **equal gross assets** (incorrect if user has debts)
- Balance sheet will be **wrong**

---

### 4. VA Benefits Calculation ✅

#### Auto-Calculation Logic (`assessments.py`)

```python
def _auto_populate_va_disability(state: dict[str, Any]) -> None:
    has_disability = state.get("has_va_disability")
    if has_disability != "yes":
        return
    
    rating = state.get("va_disability_rating")
    dependents = state.get("va_dependents")
    
    if rating is None or dependents is None:
        return
    
    monthly_amount = get_monthly_va_disability(rating, dependents)
    
    if monthly_amount is not None:
        state["va_disability_monthly"] = monthly_amount
```

#### Inclusion in Total Income (`exit.py`)

```python
va_monthly_benefit = 0.0
if va_data:
    va_monthly_benefit = (
        va_data.get("va_disability_monthly", 0.0)
        + va_data.get("aid_attendance_monthly", 0.0)
        + va_data.get("va_pension_monthly", 0.0)  # ⚠️ Field doesn't exist in config
    )

total_monthly_income = base_monthly_income  # ❌ VA benefits NOT added!
```

#### ❌ ISSUE #5: VA Benefits Not Added to Total Income

**Critical Bug:** VA benefits are calculated but **NOT added** to `total_monthly_income`!

```python
total_monthly_income = base_monthly_income  # Should be: base_monthly_income + va_monthly_benefit
```

**Impact:**
- VA disability and A&A benefits are **excluded from total income**
- Monthly gap calculation will be **incorrect**
- Veterans will appear to have **less income than they actually have**
- Financial recommendations will be **wrong**

**Correct Logic:**
```python
total_monthly_income = base_monthly_income + va_monthly_benefit
```

---

## Summary of Issues

### Critical Issues (Must Fix)

| Issue | Severity | Component | Impact |
|-------|----------|-----------|--------|
| #1: Income field name mismatches | 🔴 CRITICAL | Income Assessment | Advanced income fields ignored, totals wrong |
| #2: Assets field disconnect | 🔴 CRITICAL | Assets Assessment | Calculation uses wrong field names |
| #3: Asset double-counting | 🔴 CRITICAL | Assets Assessment | Inflated asset values if advanced fields used |
| #4: Missing debt fields | 🔴 CRITICAL | Assets Assessment | Debts not captured, net worth incorrect |
| #5: VA benefits not added | 🔴 CRITICAL | Expert Review | VA income excluded from total |

### Field Name Mapping Issues

**Income Assessment:**
```
JSON Field                          → Expected by Calculation
-----------------------------------------------------------
employment_income                   → employment_monthly ❌
other_income                        → other_monthly ❌
annuity_monthly                     → (missing) ❌
retirement_distributions_monthly    → retirement_withdrawals_monthly ❌
dividends_interest_monthly          → (missing) ❌
alimony_support_monthly            → (missing) ❌
```

**Assets Assessment:**
```
JSON Field                          → Expected by Calculation
-----------------------------------------------------------
cash_liquid_total                   → checking_savings ❌
brokerage_total                     → investment_accounts ❌
retirement_total                    → (missing) ❌
home_equity_estimate                → primary_residence_value ❌
```

---

## Recommended Fixes

### Fix #1: Align Income Fields

**Option A:** Update JSON config to match calculation logic
- Rename fields in `income.json` to match `calculate_total_monthly_income()`
- Update all UI labels accordingly

**Option B:** Update calculation logic to match JSON config ✅ RECOMMENDED
- Modify `calculate_total_monthly_income()` to use exact JSON field names
- Add missing fields (annuity, dividends, alimony)
- Remove phantom field (`periodic_income_avg_monthly`)

### Fix #2: Redesign Assets Assessment

**Critical decision needed:**
Should assets use **basic totals** OR **advanced breakdowns**?

**Option A:** Basic totals only (simpler)
- Remove advanced breakdown fields
- Keep only: cash_liquid_total, brokerage_total, retirement_total, home_equity_estimate
- Update calculation to use these fields

**Option B:** Advanced breakdowns only (more detailed)
- Remove basic total fields
- Keep only breakdown fields (checking, savings, funds, stocks, etc.)
- Update calculation to sum breakdown fields

**Option C:** Smart toggle (current design intent) ✅ RECOMMENDED
- Keep both basic and advanced fields
- Use visibility rules: show basic OR advanced (never both)
- Calculation sums whichever set is visible/filled
- Add logic to detect which mode user is in

### Fix #3: Add Debt Fields to Assets

**Add debt section to assets.json:**
```json
{
  "id": "debts_obligations",
  "title": "Debts & Obligations",
  "icon": "💳",
  "fields": [
    {
      "key": "primary_residence_mortgage",
      "label": "Primary Residence Mortgage Balance",
      "type": "currency",
      "level": "basic"
    },
    {
      "key": "other_real_estate_debt",
      "label": "Other Real Estate Debt",
      "type": "currency",
      "level": "basic"
    },
    {
      "key": "secured_loans",
      "label": "Secured Loans (Auto, etc.)",
      "type": "currency",
      "level": "advanced"
    },
    {
      "key": "unsecured_debt",
      "label": "Unsecured Debt (Credit cards, etc.)",
      "type": "currency",
      "level": "advanced"
    }
  ]
}
```

### Fix #4: Add VA Benefits to Total Income

**Update exit.py line 157:**
```python
# BEFORE
total_monthly_income = base_monthly_income

# AFTER
total_monthly_income = base_monthly_income + va_monthly_benefit
```

### Fix #5: Remove Phantom VA Pension Field

**In exit.py, remove non-existent field:**
```python
# BEFORE
va_monthly_benefit = (
    va_data.get("va_disability_monthly", 0.0)
    + va_data.get("aid_attendance_monthly", 0.0)
    + va_data.get("va_pension_monthly", 0.0)  # ❌ Doesn't exist
)

# AFTER
va_monthly_benefit = (
    va_data.get("va_disability_monthly", 0.0)
    + va_data.get("aid_attendance_monthly", 0.0)
)
```

---

## Testing Checklist

After fixes are applied, verify:

### Income Assessment
- [ ] Enter Social Security: $2,000 → Shows in total ✅
- [ ] Enter Pension: $1,500 → Shows in total ✅
- [ ] Enter Employment: $3,000 → Shows in total ✅
- [ ] Switch to Advanced mode
- [ ] Enter Annuity: $500 → Shows in total ✅
- [ ] Enter IRA Distributions: $1,000 → Shows in total ✅
- [ ] Enter Dividends: $200 → Shows in total ✅
- [ ] Enter Rental Income: $1,200 → Shows in total ✅
- [ ] Enter Alimony: $800 → Shows in total ✅
- [ ] Enter LTC Insurance: $3,000 → Shows in total ✅
- [ ] Enter Family Support: $500 → Shows in total ✅
- [ ] Total should be: $13,700/month ✅

### Assets Assessment
- [ ] **Basic Mode:**
  - [ ] Enter Cash/Liquid: $50,000
  - [ ] Enter Brokerage: $200,000
  - [ ] Enter Retirement: $300,000
  - [ ] Enter Home Equity: $150,000
  - [ ] Total: $700,000 ✅
- [ ] **Advanced Mode:**
  - [ ] Enter Checking: $10,000
  - [ ] Enter Savings: $40,000
  - [ ] Enter Mutual Funds: $150,000
  - [ ] Enter Stocks: $50,000
  - [ ] Enter Traditional IRA: $250,000
  - [ ] Enter Roth IRA: $50,000
  - [ ] Enter Home Value: $400,000 (separate from equity)
  - [ ] Enter Mortgage: $250,000
  - [ ] Total Assets: $950,000 ✅
  - [ ] Total Debt: $250,000 ✅
  - [ ] Net Assets: $700,000 ✅
- [ ] Verify **NO double-counting** when switching modes

### VA Benefits
- [ ] Select "Yes" for VA Disability
- [ ] Select Rating: 60%
- [ ] Select Dependents: Veteran with spouse
- [ ] Auto-calculated amount: $1,622.44 ✅
- [ ] Enter Aid & Attendance: $1,000
- [ ] Total VA Benefits: $2,622.44/month ✅
- [ ] Verify VA benefits show in Expert Review total income ✅

### Expert Review / Financial Gap
- [ ] Income total includes ALL income sources ✅
- [ ] Income total includes VA benefits ✅
- [ ] Assets total shows correct gross value ✅
- [ ] Net assets = gross assets - debts ✅
- [ ] Monthly gap = (income + coverage) - care cost ✅

---

## Current Status

**Branch:** `feature/calculation-verification`  
**Code Changes:** None (audit only)  
**Next Step:** Await approval to implement fixes

**Estimated Effort:**
- Fix #1 (Income fields): 30 minutes
- Fix #2 (Assets redesign): 2-3 hours (requires design decision)
- Fix #3 (Add debt fields): 1 hour
- Fix #4 (VA benefits to income): 5 minutes
- Fix #5 (Remove phantom field): 2 minutes
- Testing: 1-2 hours

**Total:** 4-6 hours

---

**Last Updated:** October 19, 2025  
**Auditor:** GitHub Copilot (AI Assistant)  
**Status:** Awaiting user review and approval to proceed with fixes
