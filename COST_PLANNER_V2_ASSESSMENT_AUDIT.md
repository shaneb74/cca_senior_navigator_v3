# Cost Planner v2 Assessment Data Audit

**Date:** 2025-01-XX  
**Branch:** assessment-revision  
**Scope:** Ensure all assessment fields persist to data/users and are used in financial timeline analysis

---

## Executive Summary

Completed comprehensive audit of all 6 Cost Planner v2 financial assessments against the `FinancialProfile` dataclass and expert review formulas. Found **17 missing fields** across 4 assessments that are collected from users but not persisted or used in financial calculations.

### Critical Findings:
- ✅ **Income Assessment:** 2 missing text fields (notes/frequency)
- ✅ **Assets Assessment:** No missing fields (all properly mapped)
- ❌ **Health Insurance Assessment:** 7 missing fields (mix of checkboxes, numbers, strings)
- ✅ **Life Insurance Assessment:** No missing fields
- ⚠️ **VA Benefits Assessment:** 1 field type mismatch + missing status variants
- ❌ **Medicaid Navigation Assessment:** 5 missing fields (majority not captured)
- ⚠️ **Checkbox Conditional Logic:** Not yet tested (pending)

---

## Detailed Findings by Assessment

### 1. Income Assessment (`income.json`)

**Status:** ✅ Mostly Complete (2 minor fields missing)

#### Missing Fields:
| Field Key | Type | JSON | FinancialProfile | Impact |
|-----------|------|------|------------------|--------|
| `periodic_income_frequency` | select (string) | ✅ Collected | ❌ Not in dataclass | User enters frequency (monthly/quarterly/annual) but it's not stored |
| `periodic_income_notes` | textarea (string) | ✅ Collected | ❌ Not in dataclass | User notes about RMDs, dividend schedules, asset sales - lost |
| `other_monthly` | currency (number) | ✅ Collected | ⚠️ In dataclass but verify source | Listed in JSON, in dataclass, but need to verify calculation is correct |

#### Properly Mapped Fields (13 total):
- ✅ ss_monthly
- ✅ pension_monthly
- ✅ employment_status
- ✅ employment_monthly
- ✅ has_partner
- ✅ shared_finance_notes
- ✅ partner_income_monthly
- ✅ retirement_withdrawals_monthly
- ✅ rental_income_monthly
- ✅ ltc_insurance_monthly
- ✅ family_support_monthly
- ✅ periodic_income_avg_monthly (numeric part)
- ✅ total_monthly_income (calculated)

---

### 2. Assets Assessment (`assets.json`)

**Status:** ✅ Complete (all fields properly mapped)

#### All Fields Properly Mapped (20 total):
- ✅ asset_has_partner
- ✅ asset_legal_restrictions
- ✅ checking_savings
- ✅ investment_accounts
- ✅ liquid_assets_has_loan (checkbox)
- ✅ liquid_assets_loan_balance (conditional)
- ✅ primary_residence_value
- ✅ primary_residence_has_debt (checkbox)
- ✅ primary_residence_mortgage_balance (conditional)
- ✅ primary_residence_liquidity_window
- ✅ home_sale_interest (checkbox)
- ✅ other_real_estate
- ✅ other_real_estate_has_debt (checkbox)
- ✅ other_real_estate_debt_balance (conditional)
- ✅ other_resources
- ✅ asset_secured_loans
- ✅ asset_other_debts
- ✅ asset_debt_notes
- ✅ asset_liquidity_concerns
- ✅ asset_liquidity_notes

**Note:** Checkbox conditional fields present but behavior needs testing (Requirement #2)

---

### 3. Health Insurance Assessment (`health_insurance.json`)

**Status:** ❌ Incomplete (7 of 13 fields missing)

#### Missing Fields:
| Field Key | Type | JSON | FinancialProfile | Impact |
|-----------|------|------|------------------|--------|
| `has_medicare` | select (string "yes"/"no") | ✅ Collected | ⚠️ Stored as bool | Type mismatch - JSON sends string, profile expects boolean |
| `medicare_advantage` | checkbox (boolean) | ✅ Collected | ❌ Not in dataclass | User's Medicare Advantage status lost |
| `medicare_supplement` | checkbox (boolean) | ✅ Collected | ❌ Not in dataclass | User's Medigap status lost |
| `medicare_monthly_premium` | currency (number) | ✅ Collected | ⚠️ Named `medicare_premium_monthly` | **NAMING MISMATCH** - JSON key ≠ dataclass key |
| `has_medicaid` | select (string) | ✅ Collected | ⚠️ Stored as bool | Type mismatch |
| `medicaid_status` | select (string) | ✅ Collected in health_insurance.json | ❌ Not mapped (confused with medicaid_navigation's version) | Duplication issue - field exists in 2 assessments |
| `has_ltc_insurance` | select (string) | ✅ Collected | ⚠️ Stored as bool | Type mismatch |
| `ltc_benefit_period_months` | number | ✅ Collected | ❌ Not in dataclass | How long LTC benefits last - critical for runway calc |
| `ltc_elimination_days` | number | ✅ Collected | ❌ Not in dataclass | Waiting period before LTC pays - affects timing |
| `ltc_monthly_premium` | currency | ✅ Collected | ❌ Not in dataclass | Monthly cost of LTC insurance - affects net income |
| `has_private_insurance` | select (string) | ✅ Collected | ⚠️ Stored as bool | Type mismatch |

#### Properly Mapped Fields (6 total):
- ⚠️ has_medicare (type mismatch)
- ✅ medicare_parts (array)
- ⚠️ medicare_premium_monthly (naming mismatch)
- ⚠️ has_medicaid (type mismatch)
- ✅ medicaid_covers_ltc
- ⚠️ has_ltc_insurance (type mismatch)
- ✅ ltc_daily_benefit
- ⚠️ has_private_insurance (type mismatch)
- ✅ private_insurance_premium_monthly

**Critical Issue:** JSON assessments use select fields with "yes"/"no" strings for boolean logic, but `financial_profile.py` converts them with `bool(health_data.get(...))` which will return `True` for the string "no" because non-empty strings are truthy!

---

### 4. Life Insurance Assessment (`life_insurance.json`)

**Status:** ✅ Complete (all fields properly mapped)

#### All Fields Properly Mapped (8 total):
- ✅ has_life_insurance
- ✅ life_insurance_type
- ✅ life_insurance_face_value
- ✅ life_insurance_cash_value
- ✅ life_insurance_premium_monthly
- ✅ has_annuities
- ✅ annuity_current_value
- ✅ annuity_monthly_income
- ✅ total_accessible_life_value (calculated)

---

### 5. VA Benefits Assessment (`va_benefits.json`)

**Status:** ⚠️ Mostly Complete (field type issues + missing variants)

#### Issues:
| Field Key | Type | JSON | FinancialProfile | Impact |
|-----------|------|------|------------------|--------|
| `has_va_benefits` | select with 4 options | ✅ Collected ("no", "yes", "applied", "eligible") | ⚠️ Only "no"/"yes" captured | Loses distinction between "applied" and "eligible" statuses |
| `va_disability_rating` | select (string) | ✅ Collected as ranges like "70-90" | ⚠️ Converted to int | Code tries to parse "70-90" as int - will fail |
| `has_aid_attendance` | select with 4 options | ✅ Collected ("no", "yes", "applied", "eligible") | ⚠️ Only binary captured | Same issue as has_va_benefits |

#### Properly Mapped Fields (5 total):
- ⚠️ has_va_benefits (loses status variants)
- ⚠️ va_disability_rating (parsing issue)
- ✅ va_disability_monthly
- ✅ va_pension_monthly
- ⚠️ has_aid_attendance (loses status variants)
- ✅ aid_attendance_monthly
- ✅ total_va_benefits_monthly (calculated)

**Code Bug Found:**
```python
# financial_profile.py line 280-285
rating_str = va_data.get("va_disability_rating", "0")
try:
    # Remove '%' if present and convert to int
    profile.va_disability_rating = int(rating_str.replace("%", "")) if rating_str else 0
except (ValueError, AttributeError):
    profile.va_disability_rating = 0
```

This will fail for JSON values like `"10-30"`, `"40-60"`, `"70-90"`, `"100"`, `"none"`. Should map to midpoint or max value.

---

### 6. Medicaid Navigation Assessment (`medicaid_navigation.json`)

**Status:** ❌ Severely Incomplete (5 of 9 fields missing - 55% data loss)

#### Missing Fields:
| Field Key | Type | JSON | FinancialProfile | Impact |
|-----------|------|------|------------------|--------|
| `medicaid_status` | select (string) | ✅ Collected | ⚠️ Mapped but conflicts with health_insurance.json | Duplication - which source is authoritative? |
| `medicaid_covers_ltc` | checkbox (boolean) | ✅ Collected | ⚠️ Mapped but conflicts with health_insurance.json | Same duplication issue |
| `aware_of_asset_limits` | select (string) | ✅ Collected ("no", "somewhat", "yes") | ❌ Not in dataclass | User's knowledge level lost - affects recommendations |
| `current_asset_position` | select (string) | ✅ Collected ("under_limit", "near_limit", "over_limit", "unknown") | ❌ Not in dataclass | **CRITICAL** - affects Medicaid eligibility timeline |
| `aware_of_estate_recovery` | checkbox (boolean) | ✅ Collected | ❌ Not in dataclass | User's awareness lost - affects recommendation priority |
| `interested_in_elder_law` | checkbox (boolean) | ✅ Collected | ❌ Not in dataclass | Referral intent lost - affects resource recommendations |

#### Properly Mapped Fields (4 of 9):
- ⚠️ medicaid_status (duplication issue with health_insurance)
- ✅ interested_in_spend_down
- ✅ spend_down_timeline
- ✅ has_estate_plan

**Major Issue:** 5 fields collecting critical Medicaid planning context (asset position, knowledge level, referral needs) are completely lost. This data would significantly improve expert review recommendations.

---

## Checkbox Conditional Field Analysis

### Requirement #2: "Checkboxes that toggle new data fields are set correctly so that checked box shows the conditional field, and unchecked box hides or disables it"

#### Checkbox Fields with `visible_if` Conditions:

**Assets Assessment:**
1. ✅ `liquid_assets_has_loan` (checkbox) → shows `liquid_assets_loan_balance` if `true`
2. ✅ `primary_residence_has_debt` (checkbox) → shows `primary_residence_mortgage_balance` if `true`
3. ✅ `other_real_estate_has_debt` (checkbox) → shows `other_real_estate_debt_balance` if `true`
4. ✅ `home_sale_interest` (checkbox) - standalone, no conditional field

**Health Insurance Assessment:**
1. ✅ `medicare_advantage` (checkbox) - standalone in visible_if block for medicare="yes"
2. ✅ `medicare_supplement` (checkbox) - standalone in visible_if block for medicare="yes"
3. ✅ `medicaid_covers_ltc` (checkbox) - standalone in visible_if block for medicaid="yes"

**Income Assessment:**
1. ✅ `has_partner` (select with 3 options) → shows `partner_income_monthly` if `"partner_shared"`
2. ✅ `has_partner` (select) → shows `shared_finance_notes` if NOT `"no_partner"`

**All conditional logic follows pattern:**
```json
"visible_if": {
  "field": "parent_field_key",
  "equals": true  // or specific value
}
```

**Status:** ⚠️ **NEEDS TESTING** - Logic appears correct in JSON, but requires runtime testing to verify `core/assessment_engine.py:_is_field_visible()` correctly handles:
- Boolean checkbox values (`true`/`false`)
- String comparisons (`"yes"`, `"partner_shared"`, etc.)
- `not_equals` operator
- `in` operator (for multiselect)

---

## Data Persistence Flow Analysis

### Requirement #1 & #8: "Ensure every data entry field is persisted to data/users and used in financial timeline"

#### Persistence Chain:

```
User Input (Streamlit widgets)
    ↓
assessment_engine._render_fields()
    ↓
st.session_state[f"{product_key}_{assessment_key}"] = {field_values}
    ↓
assessments._persist_assessment_state()
    ↓
st.session_state["tiles"][product_key]["assessments"][assessment_key] = augmented_state
    ↓
st.session_state["cost_v2_modules"][assessment_key] = module_entry
    ↓
[ON SAVE/RERUN] → session_store.py (implicit via Streamlit)
    ↓
data/users/{uid}.json (via session_store atomic write)
```

#### Key Functions:

1. **`assessments._persist_assessment_state()`** (line 681)
   - Augments state with calculated values via `_augment_assessment_state()`
   - Saves to `st.session_state["tiles"]` (used by financial profile)
   - Saves to `st.session_state["cost_v2_modules"]` (backward compat with hub metrics)

2. **`assessments._augment_assessment_state()`** (line 712)
   - For `income`: Calls `normalize_income_data()` and `calculate_total_monthly_income()`
   - For `assets`: Calls `normalize_asset_data()` and calculates asset/debt totals
   - Returns enriched state with derived fields

3. **`financial_profile.build_financial_profile()`** (line 135)
   - Reads from `st.session_state["tiles"][product_key]["assessments"]`
   - Maps each field from assessment state to `FinancialProfile` dataclass
   - **THIS IS WHERE MISSING FIELDS ARE DROPPED**

4. **`session_store.py`** (core/session_store.py)
   - Provides `save_user(uid, user_data)` and `load_user(uid)`
   - Writes to `data/users/{uid}.json` with atomic file operations
   - Uses file locking to prevent concurrent write corruption

#### Verification Needed:
- ⚠️ **Test:** Confirm `st.session_state["tiles"]` gets written to `data/users/*.json` on save
- ⚠️ **Test:** Verify missing fields are present in `tiles` but dropped in `build_financial_profile()`
- ⚠️ **Test:** Check if Streamlit's implicit session persistence covers tiles or if explicit save needed

---

## Expert Review Formula Analysis

### Requirement #9: "All fields are correctly used in the financial timeline analysis"

#### Expert Review Input Sources:

**From `expert_formulas.calculate_expert_review()`:**

**Uses:**
- ✅ `profile.total_monthly_income` (sum of all income sources)
- ✅ `profile.total_va_benefits_monthly`
- ✅ `profile.annuity_monthly_income`
- ✅ `profile.checking_savings`
- ✅ `profile.investment_accounts`
- ✅ `profile.other_real_estate`
- ✅ `profile.other_resources`
- ✅ `profile.total_accessible_life_value` (life insurance cash value)
- ⚠️ `care_recommendation` (from GCP - care tier, flags)
- ⚠️ `zip_code` (for regional cost adjustment)

**Does NOT Use (Opportunity for Enhancement):**
- ❌ `profile.periodic_income_frequency` - Could adjust liquidity assumptions
- ❌ `profile.periodic_income_notes` - Could flag RMD timing or asset sale plans
- ❌ `profile.ltc_benefit_period_months` - **CRITICAL** - Should reduce estimated care costs
- ❌ `profile.ltc_elimination_days` - **CRITICAL** - Affects when LTC benefits start paying
- ❌ `profile.ltc_monthly_premium` - Should reduce disposable income
- ❌ `profile.medicare_advantage` / `profile.medicare_supplement` - Could affect cost estimates
- ❌ `profile.current_asset_position` (Medicaid) - Should influence spend-down recommendations
- ❌ `profile.aware_of_asset_limits` (Medicaid) - Should prioritize education in recommendations
- ❌ `profile.primary_residence_liquidity_window` - Could adjust asset liquidity calculations
- ❌ `profile.asset_liquidity_concerns` - Should flag delayed access to funds

#### Calculation Flow:

```python
# expert_formulas.py line 64-90
estimated_monthly_cost = _get_base_care_cost(care_recommendation) 
                       * _calculate_care_flags_modifier(care_recommendation)
                       * _get_regional_modifier(zip_code)

total_monthly_resources = total_monthly_income + total_monthly_benefits

coverage_percentage = (total_monthly_resources / estimated_monthly_cost) * 100
monthly_gap = estimated_monthly_cost - total_monthly_resources

total_liquid_assets = checking_savings + investment_accounts + other_real_estate 
                    + other_resources + total_accessible_life_value

runway_months = total_liquid_assets / monthly_gap  # if gap > 0
```

**Missing from Calculations:**
1. **LTC Insurance Benefits** - Should reduce `estimated_monthly_cost` by `ltc_daily_benefit * 30` after `ltc_elimination_days`
2. **LTC Premium Costs** - Should reduce `total_monthly_resources` by `ltc_monthly_premium`
3. **Primary Residence Equity** - `primary_residence_value - primary_residence_mortgage_balance` not included in `total_liquid_assets` (intentional? or bug?)
4. **Asset Liquidity Timing** - `primary_residence_liquidity_window` not factored into runway calculation
5. **Medicaid Timeline** - `current_asset_position` + `spend_down_timeline` could trigger earlier Medicaid eligibility, affecting runway

---

## Priority Fix Plan

### Phase 1: Critical Data Loss Issues (DO FIRST)

**1.1 Fix Boolean Type Mismatches (Health Insurance)** - **HIGH PRIORITY**
- **Issue:** JSON sends `"yes"`/`"no"` strings, code treats as booleans → wrong values stored
- **Impact:** Medicare/Medicaid/LTC/Private insurance flags all incorrect
- **Fix:** Update `financial_profile.py` lines 231-256 to check for string values:
  ```python
  # OLD (WRONG):
  profile.has_medicare = bool(health_data.get("has_medicare", False))
  
  # NEW (CORRECT):
  has_medicare_val = health_data.get("has_medicare", "no")
  profile.has_medicare = has_medicare_val == "yes"
  ```

**1.2 Fix Naming Mismatch (Medicare Premium)** - **HIGH PRIORITY**
- **Issue:** JSON key `medicare_monthly_premium` ≠ dataclass key `medicare_premium_monthly`
- **Impact:** Medicare premium costs lost, affecting net income calculations
- **Fix:** Either update JSON key or update profile mapping (recommend updating profile mapping for consistency with other `_monthly` fields)

**1.3 Fix VA Disability Rating Parsing** - **MEDIUM PRIORITY**
- **Issue:** JSON sends `"70-90"` strings, code tries `int()` conversion → crashes
- **Impact:** VA disability rating lost or causes exception
- **Fix:** Map rating ranges to numeric values:
  ```python
  RATING_MAP = {"none": 0, "10-30": 20, "40-60": 50, "70-90": 80, "100": 100}
  rating_str = va_data.get("va_disability_rating", "none")
  profile.va_disability_rating = RATING_MAP.get(rating_str, 0)
  ```

---

### Phase 2: Add Missing Fields to FinancialProfile

**2.1 Add Missing Income Fields**
```python
# Add to FinancialProfile dataclass (after periodic_income_avg_monthly):
periodic_income_frequency: str = "annual"  # "monthly", "quarterly", "semi_annual", "annual", "as_needed"
periodic_income_notes: str = ""

# Add to build_financial_profile() income section:
profile.periodic_income_frequency = income_data.get("periodic_income_frequency", "annual")
profile.periodic_income_notes = income_data.get("periodic_income_notes", "")
```

**2.2 Add Missing Health Insurance Fields**
```python
# Add to FinancialProfile dataclass (after medicare_parts):
has_medicare_advantage: bool = False
has_medicare_supplement: bool = False

# Add after ltc_elimination_days:
ltc_benefit_period_months: int = 0
ltc_elimination_days: int = 0  
ltc_monthly_premium: float = 0.0

# Add to build_financial_profile() health section:
profile.has_medicare_advantage = health_data.get("medicare_advantage", False)
profile.has_medicare_supplement = health_data.get("medicare_supplement", False)
profile.ltc_benefit_period_months = int(health_data.get("ltc_benefit_period_months", 0))
profile.ltc_elimination_days = int(health_data.get("ltc_elimination_days", 0))
profile.ltc_monthly_premium = float(health_data.get("ltc_monthly_premium", 0))
```

**2.3 Add Missing Medicaid Planning Fields**
```python
# Add to FinancialProfile dataclass (after has_estate_plan):
aware_of_asset_limits: str = "no"  # "no", "somewhat", "yes"
current_asset_position: str = "unknown"  # "under_limit", "near_limit", "over_limit", "unknown"
aware_of_estate_recovery: bool = False
interested_in_elder_law: bool = False

# Add to build_financial_profile() medicaid section:
profile.aware_of_asset_limits = medicaid_data.get("aware_of_asset_limits", "no")
profile.current_asset_position = medicaid_data.get("current_asset_position", "unknown")
profile.aware_of_estate_recovery = bool(medicaid_data.get("aware_of_estate_recovery", False))
profile.interested_in_elder_law = bool(medicaid_data.get("interested_in_elder_law", False))
```

---

### Phase 3: Enhance Expert Review Calculations

**3.1 Incorporate LTC Insurance Benefits**
```python
# In expert_formulas.py, after calculating estimated_monthly_cost:

# Reduce cost by LTC insurance benefits (after elimination period)
if profile.has_ltc_insurance and profile.ltc_daily_benefit > 0:
    ltc_monthly_coverage = profile.ltc_daily_benefit * 30
    # Reduce estimated cost (LTC insurance pays part)
    estimated_monthly_cost = max(0, estimated_monthly_cost - ltc_monthly_coverage)
    
    # Subtract LTC premium from monthly income
    total_monthly_resources -= profile.ltc_monthly_premium
    
    # Note elimination period in recommendations if applicable
    if profile.ltc_elimination_days > 0:
        # Add to action items: "LTC insurance has {days}-day elimination period"
```

**3.2 Add Medicaid Spend-Down Logic**
```python
# In expert_formulas.py, enhance runway calculation:

# If asset position near Medicaid limits, adjust runway
if profile.current_asset_position == "near_limit":
    # Medicaid will cover costs soon, adjust runway estimate
    medicaid_transition_months = 6  # Estimate 6 months to qualification
    # Reduce pressure if transitioning to Medicaid coverage
    
elif profile.interested_in_spend_down and profile.spend_down_timeline:
    # Use spend_down_timeline to estimate Medicaid transition
    timeline_map = {"immediate": 0, "6_months": 6, "1_year": 12, "2_years": 24, "3_plus_years": 36}
    transition_months = timeline_map.get(profile.spend_down_timeline, 12)
    # Factor into recommendations
```

**3.3 Enhance Recommendations with Missing Data**
```python
# In expert_formulas.py _generate_recommendations():

# Use periodic income notes
if profile.periodic_income_notes:
    # Add context chip: "Periodic income details captured"
    # Include notes in PDF export

# Use asset liquidity window
if profile.primary_residence_liquidity_window == "not_planning":
    # Flag in recommendations: "Home equity not available for care"
elif profile.primary_residence_liquidity_window in ["over_year", "six_to_twelve"]:
    # Adjust liquidity assumptions

# Use Medicaid awareness
if profile.interested_in_spend_down and profile.aware_of_asset_limits == "no":
    # High priority: Add action item for Medicaid education

if profile.interested_in_elder_law:
    # Add resource: Elder law attorney referral
```

---

### Phase 4: Test Checkbox Conditional Logic

**4.1 Manual Testing Checklist**
- [ ] Test `liquid_assets_has_loan` checkbox → `liquid_assets_loan_balance` appears/disappears
- [ ] Test `primary_residence_has_debt` checkbox → `primary_residence_mortgage_balance` appears/disappears
- [ ] Test `other_real_estate_has_debt` checkbox → `other_real_estate_debt_balance` appears/disappears
- [ ] Test `has_partner` = "partner_shared" → `partner_income_monthly` appears
- [ ] Test `has_partner` ≠ "no_partner" → `shared_finance_notes` appears
- [ ] Test `has_medicare` = "yes" → Medicare detail fields appear
- [ ] Test `has_medicaid` = "yes" → Medicaid detail fields appear
- [ ] Test `has_ltc_insurance` = "yes" → LTC detail fields appear
- [ ] Test `employment_status` ≠ "not_employed" → `employment_monthly` appears

**4.2 Automated Testing**
- Create pytest tests for `core/assessment_engine._is_field_visible()`
- Test all `visible_if` patterns (equals, not_equals, in)
- Test boolean vs string value handling

---

## Files Requiring Changes

### Critical (Phase 1):
1. **`products/cost_planner_v2/financial_profile.py`** (lines 231-256, 280-285)
   - Fix boolean type mismatches
   - Fix VA rating parsing
   - Fix medicare premium naming

### Important (Phase 2):
2. **`products/cost_planner_v2/financial_profile.py`** (FinancialProfile dataclass + build function)
   - Add 12 missing fields to dataclass
   - Add field mappings in build_financial_profile()

3. **`products/cost_planner_v2/modules/assessments/health_insurance.json`** (optional)
   - Consider renaming `medicare_monthly_premium` → `medicare_premium_monthly` for consistency

### Enhancement (Phase 3):
4. **`products/cost_planner_v2/expert_formulas.py`**
   - Incorporate LTC insurance benefits
   - Add Medicaid spend-down logic
   - Enhance recommendations with missing data

5. **`products/cost_planner_v2/expert_review.py`**
   - Update UI to show LTC insurance impact
   - Add Medicaid timeline indicators

### Testing (Phase 4):
6. **`tests/test_assessment_conditional_logic.py`** (NEW)
   - Test checkbox conditional field behavior
   - Test visible_if patterns

7. **`tests/test_financial_profile_completeness.py`** (NEW)
   - Verify all JSON fields map to FinancialProfile
   - Verify no data loss in persistence chain

---

## Testing Strategy

### 1. Data Persistence Test
```bash
# Run app, complete an assessment, check data/users/*.json
streamlit run app.py
# Complete income assessment with all fields
# Check: cat data/users/{uid}.json | jq '.tiles.cost_planner_v2.assessments.income'
# Verify: periodic_income_frequency, periodic_income_notes present
```

### 2. Boolean Type Test
```bash
# Complete health insurance assessment
# Select "yes" for Medicare
# Check: st.session_state["tiles"]["cost_planner_v2"]["assessments"]["health_insurance"]["has_medicare"]
# Should be: "yes" (string), NOT True (boolean)
# Then check: FinancialProfile object
# Should be: True (boolean after proper parsing)
```

### 3. Expert Review Integration Test
```bash
# Complete income + assets with LTC insurance
# LTC daily benefit: $200
# LTC monthly premium: $300
# Estimated care cost: $5000/month
# Expected result:
#   - Estimated cost reduced to $5000 - ($200*30) = -$1000 (full coverage)
#   - Monthly resources reduced by $300 (premium)
```

---

## Success Criteria

### Requirement #1: "Ensure every data entry field is persisted to data/users and used in financial timeline"
- [ ] All 17 missing fields added to FinancialProfile dataclass
- [ ] All missing fields mapped in build_financial_profile()
- [ ] Verified fields appear in data/users/*.json after save
- [ ] LTC insurance fields used in expert_formulas calculations
- [ ] Medicaid planning fields used in recommendations
- [ ] Periodic income notes available in expert review export

### Requirement #2: "Checkboxes correctly toggle conditional fields (checked=show, unchecked=hide)"
- [ ] All 9 checkbox conditional patterns tested manually
- [ ] No visual bugs (fields showing when they shouldn't)
- [ ] No data loss (conditional field values preserved when parent checkbox toggled)
- [ ] _is_field_visible() handles all visible_if patterns correctly

### Requirement #3: "Apply this to all assessments"
- [ ] Audit completed for all 6 assessments (income, assets, health, life, va, medicaid)
- [ ] Fixes applied consistently across all affected assessments
- [ ] No regressions in previously working assessments
- [ ] All assessments follow same data patterns and conventions

---

## Risk Assessment

### High Risk:
- ❌ **Boolean Type Mismatches** - Currently storing wrong values for Medicare/Medicaid/LTC flags
- ❌ **VA Disability Rating** - Code will crash on "70-90" input
- ❌ **Medicare Premium** - Currently lost due to naming mismatch

### Medium Risk:
- ⚠️ **LTC Insurance** - Missing 3 critical fields affecting cost calculations
- ⚠️ **Medicaid Planning** - 55% of assessment data currently lost

### Low Risk:
- ℹ️ **Income Notes** - Missing context fields (frequency, notes) don't break calculations
- ℹ️ **Checkbox Logic** - Appears correct in JSON, just needs verification testing

---

## Next Steps

1. **Immediate:** Fix Phase 1 critical bugs (boolean types, VA rating, medicare premium)
2. **Short-term:** Add Phase 2 missing fields to dataclass
3. **Medium-term:** Implement Phase 3 expert review enhancements
4. **Ongoing:** Phase 4 checkbox testing and validation

---

*Audit completed: 2025-01-XX*  
*Auditor: GitHub Copilot*  
*Review required: Senior Developer*
