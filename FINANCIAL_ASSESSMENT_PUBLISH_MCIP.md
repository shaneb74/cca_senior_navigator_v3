# Financial Assessment V2 - Publish to MCIP Integration

**Date:** October 15, 2025  
**Status:** ✅ Complete and Verified

---

## Overview

The **"📊 Publish to MCIP"** button in the Financial Assessment hub aggregates all collected financial data, calculates a comprehensive financial timeline, and publishes a standardized `FinancialProfile` contract to MCIP for system-wide access.

---

## What Happens When "Publish to MCIP" is Pressed

### 1. Data Aggregation ✅

The system collects data from all completed modules:

#### Income Sources (Required Module)
```python
monthly_income_sources = {
    'social_security': ss_monthly,      # From income module
    'pension': pension_monthly,
    'employment': employment_monthly,
    'investment': investment_monthly,
    'other': other_monthly
}
total_monthly_income = sum(all sources)
```

#### Assets & Resources (Required Module)
```python
asset_categories = {
    'liquid': checking_savings + cds_money_market,
    'retirement': ira_traditional + ira_roth + k401_403b + other_retirement,
    'investments': stocks_bonds + mutual_funds,
    'real_estate': investment_property,
    'business': business_value,
    'other': other_assets_value
}
total_assets = sum(all categories)
liquid_assets = checking_savings + cds_money_market
```

#### VA Benefits (Optional Module)
```python
va_monthly_benefit = (
    va_disability_monthly +
    aid_attendance_monthly
)
```

#### Health Insurance (Optional Module)
```python
ltc_monthly_coverage = ltc_daily_benefit * 30  # Convert daily to monthly
has_medicare = user has Medicare coverage
```

#### Life Insurance (Optional Module)
- Tracked for reference but not counted as monthly income
- Cash value available as emergency asset

#### Medicaid Navigation (Optional Module)
- Planning information tracked
- Eligibility assessment stored

---

### 2. Cost Calculation ✅

The system calculates estimated monthly care costs based on the Care Recommendation from GCP:

```python
# Get care recommendation from MCIP
care_recommendation = MCIP.get_care_recommendation()

# Calculate costs using CostCalculator
if care_recommendation:
    cost_estimate = CostCalculator.calculate_comprehensive_estimate(
        care_tier=care_recommendation.tier,  # e.g., "assisted_living"
        zip_code=user_zip,                   # Regional adjustment
        state=user_state                     # State-specific costs
    )
    estimated_monthly_cost = cost_estimate.monthly_adjusted
else:
    # Fallback to national average
    estimated_monthly_cost = 5000
```

**Cost includes:**
- Base tier cost (independent, in_home, assisted_living, memory_care)
- Regional multiplier
- Condition-based add-ons from GCP flags:
  - Memory support (+20%)
  - Mobility issues (+15%)
  - High ADL support (+10%)
  - Medication management (+8%)
  - Behavioral care (+12%)
  - Fall risk (+8%)
  - Chronic conditions (+10%)

---

### 3. Financial Timeline Calculation ✅

The system calculates how long the user's resources will cover care costs:

```python
# Calculate monthly gap
monthly_gap = estimated_monthly_cost - total_monthly_income - total_monthly_coverage

# Calculate asset runway
if monthly_gap > 0 and liquid_assets > 0:
    runway_months = int(liquid_assets / monthly_gap)
elif monthly_gap <= 0:
    runway_months = 999  # Unlimited (fully covered)
else:
    runway_months = 0  # No liquid assets

# Calculate coverage percentage
coverage_percentage = int((
    (total_monthly_income + total_monthly_coverage) / 
    estimated_monthly_cost
) * 100)
```

**Example Calculation:**

```
User Data:
- Monthly Income: $3,500
- Liquid Assets: $50,000
- VA Benefits: $0
- LTC Insurance: $3,000/mo
- Care Tier: Assisted Living ($5,000/mo)

Calculation:
- Estimated Cost: $5,000/mo
- Total Resources: $3,500 + $3,000 = $6,500/mo
- Monthly Gap: $5,000 - $6,500 = -$1,500
- Coverage: 130% (FULLY COVERED!)
- Runway: Unlimited ✅
```

---

### 4. MCIP Contract Publishing ✅

The system publishes a standardized `FinancialProfile` contract to MCIP:

```python
financial_profile = FinancialProfile(
    estimated_monthly_cost=5000.00,      # From cost calculation
    coverage_percentage=100,              # % covered by income + benefits
    gap_amount=0.00,                      # Monthly shortfall (or surplus)
    runway_months=999,                    # Months assets will last
    confidence=0.95,                      # Very high (from detailed modules)
    generated_at="2025-10-15T10:30:00Z", # ISO timestamp
    status="complete"                     # Assessment complete
)

# Publish to MCIP
MCIP.publish_financial_profile(financial_profile)
```

---

### 5. Detailed Breakdown Storage ✅

Additional detailed data is stored in session state for Cost Planner access:

```python
st.session_state["financial_assessment_complete"] = {
    "income": {
        "sources": {
            "social_security": 1800,
            "pension": 1200,
            "employment": 0,
            "investment": 500,
            "other": 0
        },
        "total_monthly": 3500
    },
    "assets": {
        "categories": {
            "liquid": 50000,
            "retirement": 150000,
            "investments": 75000,
            "real_estate": 0,
            "business": 0,
            "other": 0
        },
        "total": 275000,
        "liquid": 50000
    },
    "coverage": {
        "va_benefit": 0,
        "ltc_coverage": 3000,
        "has_medicare": true,
        "total_monthly": 3000
    },
    "costs": {
        "estimated_monthly": 5000,
        "care_tier": "assisted_living"
    },
    "timeline": {
        "monthly_gap": -1500,      # Negative = surplus
        "runway_months": 999,       # Unlimited
        "coverage_percentage": 130
    },
    "generated_at": "2025-10-15T10:30:00Z"
}
```

---

### 6. Product Completion ✅

The system marks the Financial Assessment product as complete:

```python
# Mark in MCIP journey
MCIP.mark_product_complete("cost_v2")

# Set published flag
st.session_state["cost_planner_v2_published"] = True
```

---

## How Cost Planner Accesses the Data

### Via MCIP Contract
```python
from core.mcip import MCIP

# Get published financial profile
financial = MCIP.get_financial_profile()

# Access key metrics
monthly_cost = financial.estimated_monthly_cost  # 5000.00
coverage_pct = financial.coverage_percentage      # 100
gap = financial.gap_amount                        # 0.00
runway = financial.runway_months                  # 999
```

### Via Session State (Detailed Breakdown)
```python
# Get detailed financial data
financial_data = st.session_state.get("financial_assessment_complete")

# Access specific details
income_sources = financial_data["income"]["sources"]
asset_categories = financial_data["assets"]["categories"]
va_benefit = financial_data["coverage"]["va_benefit"]
care_tier = financial_data["costs"]["care_tier"]
```

---

## Timeline Visualization

The system provides visual indicators based on the financial timeline:

### Scenario 1: Fully Covered ✅
```
Monthly Cost: $5,000
Monthly Income: $3,500
Monthly Coverage: $3,000 (LTC)
Gap: -$1,500 (SURPLUS)
Runway: Unlimited

Display: "✅ Income and benefits fully cover monthly care costs!"
```

### Scenario 2: Asset Runway Available
```
Monthly Cost: $7,000
Monthly Income: $3,500
Monthly Coverage: $1,000 (VA)
Gap: $2,500
Liquid Assets: $100,000
Runway: 40 months (3.3 years)

Display: Progress bar + "Asset runway: 3.3 years of care coverage"
```

### Scenario 3: Immediate Need ⚠️
```
Monthly Cost: $6,500
Monthly Income: $2,000
Monthly Coverage: $0
Gap: $4,500
Liquid Assets: $5,000
Runway: 1 month

Display: "⚠️ Immediate financial planning recommended"
```

---

## Integration Points

### 1. Care Recommendation (from GCP)
- **Input:** Care tier (independent, in_home, assisted_living, memory_care)
- **Used For:** Cost calculation with regional adjustments and condition multipliers

### 2. Cost Planner V2
- **Receives:** Complete financial profile via MCIP
- **Uses:** Monthly costs, coverage %, gap, runway for planning
- **Displays:** Timeline projections, funding recommendations

### 3. Expert Review
- **Receives:** Financial data and care recommendation
- **Uses:** Complete picture for advisor consultation
- **Provides:** Personalized recommendations

### 4. Partner Matching
- **Receives:** Financial profile for filtering
- **Uses:** Budget constraints, payment options, coverage
- **Filters:** Facilities and services within budget

---

## Field Name Mappings

### Income Module → MCIP
- `ss_monthly` → `social_security`
- `pension_monthly` → `pension`
- `employment_monthly` → `employment`
- `investment_monthly` → `investment`
- `other_monthly` → `other`

### Assets Module → MCIP
- `checking_savings` + `cds_money_market` → `liquid`
- `ira_traditional` + `ira_roth` + `k401_403b` + `other_retirement` → `retirement`
- `stocks_bonds` + `mutual_funds` → `investments`
- `investment_property` → `real_estate`
- `business_value` → `business`
- `other_assets_value` → `other`

### VA Benefits Module → MCIP
- `va_disability_monthly` + `aid_attendance_monthly` → `va_benefit`

### Health Insurance Module → MCIP
- `ltc_daily_benefit` * 30 → `ltc_coverage`
- `has_medicare` → `has_medicare`

---

## User Benefits

### Before Publishing
- Data collected in individual modules
- No cross-module analysis
- No cost projections
- No timeline calculations

### After Publishing
- ✅ Complete financial picture aggregated
- ✅ Care costs calculated based on personalized recommendation
- ✅ Monthly gap identified
- ✅ Asset runway projected
- ✅ Coverage percentage calculated
- ✅ Data available system-wide
- ✅ Expert advisors can see complete profile
- ✅ Partner matching can filter by budget

---

## Success Confirmation

When publish completes:
1. ✅ Success message: "Financial profile published!"
2. Button changes to "Continue to Expert Review →"
3. MCIP contract available via `MCIP.get_financial_profile()`
4. Detailed data in `st.session_state["financial_assessment_complete"]`
5. Product marked complete in journey
6. Timeline visualization displayed

---

## Error Handling

The system includes fallback logic:

```python
# If care recommendation unavailable
if not care_recommendation:
    estimated_monthly_cost = 5000  # National average

# If cost calculation fails
try:
    cost_estimate = CostCalculator.calculate_comprehensive_estimate(...)
except Exception:
    # Use tier defaults
    tier_defaults = {
        'independent': 2500,
        'in_home': 4500,
        'assisted_living': 5000,
        'memory_care': 7000
    }

# If no liquid assets
if monthly_gap > 0 and liquid_assets == 0:
    runway_months = 0
    display = "⚠️ Immediate planning recommended"
```

---

## Testing Verification

To verify the publish function works:

1. Complete at minimum Income + Assets modules
2. Click "📊 Publish to MCIP" button
3. Check `st.session_state.mcip.financial_profile` is populated
4. Check `st.session_state.financial_assessment_complete` has all data
5. Verify timeline calculations match expected values
6. Navigate to Cost Planner → should see financial data
7. Navigate to Expert Review → should see complete profile

---

**Status:** ✅ All field mappings corrected, labels verified, MCIP integration complete!
