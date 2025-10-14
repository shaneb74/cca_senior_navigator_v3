# Additional Services MCIP v2 Integration

**Status:** ✅ Complete  
**Date:** October 13, 2025  
**File:** `core/additional_services.py`

---

## Overview

The **Additional Services Layer** is MCIP's "salesy extension" - a dynamic recommendation engine that surfaces personalized recommendations across multiple hubs and contexts. It reads from MCIP v2 to deliver highly personalized, contextual suggestions.

### Key Concept

Additional Services acts as MCIP's outreach and coordination arm:
- **MCIP** = The conductor that orchestrates the journey
- **Additional Services** = The intelligent recommender that surfaces relevant tiles

### Recommendation Types

1. **Trusted Partners** → Live in Partners Hub
   - External service providers (Omcare, SeniorLife AI, Fall Prevention)
   - Vetted care coordination networks
   - Specialty care providers

2. **Product Tiles** → Live in Other Hubs
   - Cost Planner (recommended after GCP in Concierge Hub)
   - PFMA (recommended after Cost Planner in Concierge Hub)
   - Future products (can appear in any hub)

3. **Service Categories** → Future Hubs (Not Yet Built)
   - Estate Planning Hub
   - Retirement Planning Hub
   - Legal Services Hub
   - Financial Advisory Hub
   - Care Coordination Hub

Both MCIP and Additional Services read from the same unified data source to ensure consistency.

---

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                        MCIP v2                          │
│  ┌────────────────────┐  ┌─────────────────────────┐  │
│  │ CareRecommendation │  │   FinancialProfile      │  │
│  │  • tier            │  │  • monthly_cost         │  │
│  │  • confidence      │  │  • gap_amount           │  │
│  │  • flags[]         │  │  • runway_months        │  │
│  │  • rationale       │  │  • coverage_percentage  │  │
│  └────────────────────┘  └─────────────────────────┘  │
└──────────────┬──────────────────────┬──────────────────┘
               │                       │
               ▼                       ▼
    ┌──────────────────┐    ┌─────────────────────┐
    │  Flag-Based      │    │  Financial-Based    │
    │  Filtering       │    │  Filtering          │
    │                  │    │                     │
    │ • fall_risk      │    │ • cost_gap >= 500   │
    │ • cognitive_risk │    │ • runway_low <= 36  │
    │ • isolation_risk │    │                     │
    └──────────────────┘    └─────────────────────┘
               │                       │
               └───────────┬───────────┘
                           ▼
              ┌────────────────────────┐
              │  Additional Services   │
              │  Tile Routing          │
              └────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    ┌────────┐      ┌──────────┐      ┌──────────┐
    │Partners│      │ Product  │      │ Service  │
    │  Hub   │      │  Hubs    │      │  Hubs    │
    │        │      │          │      │ (Future) │
    │• Omcare│      │• Cost    │      │• Estate  │
    │• Senior│      │  Planner │      │  Planning│
    │  Life  │      │• PFMA    │      │• Retire- │
    │• Fall  │      │          │      │  ment    │
    │  Prev. │      │          │      │• Legal   │
    └────────┘      └──────────┘      └──────────┘
```

---

## MCIP Integration Details

### 1. Context Building (`_ctx()`)

**Old Approach (Legacy):**
```python
handoff = st.session_state.get("handoff", {})
for product_key, product_data in handoff.items():
    flags = product_data.get("flags", {})
```

**New Approach (MCIP v2):**
```python
from core.mcip import MCIP

# Primary: Get flags from MCIP CareRecommendation
care_rec = MCIP.get_care_recommendation()
if care_rec and care_rec.flags:
    for flag in care_rec.flags:
        all_flags[flag["id"]] = True

# Get financial data
financial_profile = MCIP.get_financial_profile()
```

**Benefits:**
- ✅ Single source of truth (MCIP)
- ✅ Structured flag format from GCP v4
- ✅ Access to financial data for cost-based recommendations
- ✅ Backwards compatible with legacy handoff

---

### 2. Visibility Rules (`_passes()`)

#### Flag-Based Rules (Existing)

```python
{
    "key": "omcare",
    "visible_when": [
        {"includes": {"path": "flags", "value": "medication_risk"}}
    ]
}
```

**How it works:**
- Reads `flags` dict from context
- Checks if flag key exists and is truthy
- GCP v4 publishes structured flags to MCIP
- Additional Services reads flags from MCIP

#### Financial Rules (New)

**Cost Gap Rule:**
```python
{
    "key": "elder_law_attorney",
    "visible_when": [
        {"cost_gap": {"value": 500}}  # Show if gap >= $500/month
    ]
}
```

**Runway Rule:**
```python
{
    "key": "reverse_mortgage",
    "visible_when": [
        {"runway_low": {"value": 36}}  # Show if runway <= 36 months
    ]
}
```

**How it works:**
- Reads `MCIP.get_financial_profile()`
- Checks `gap_amount` or `runway_months`
- Shows financially-relevant services automatically

---

### 3. Personalization (`get_additional_services()`)

**Subtitle Interpolation:**
```python
# Before: "Remote medication dispensing and adherence monitoring."
# After:  "Remote medication dispensing and adherence monitoring for Dorothy."

subtitle = subtitle.replace("{name}", person_name)
subtitle = subtitle.replace("{recommendation}", "Assisted Living")
```

**Data Sources:**
- `{name}` → `st.session_state.get("person_name")`
- `{recommendation}` → `MCIP.get_care_recommendation().tier`

**Example Output:**
> "Estimate monthly costs based on your **Assisted Living** recommendation."

---

## Service Types

### 1. Trusted Partners (Partners Hub)

**Purpose:** External service providers that live in the Partners Hub

**Examples:**
- **Omcare** → Medication management (`medication_risk` flag)
- **SeniorLife AI** → Wellness monitoring (`cognitive_risk`, `fall_risk` flags)
- **Fall Prevention** → Home safety (`fall_risk` flag)
- **Companion Care** → Social engagement (`isolation_risk` flag)
- **Memory Care Specialists** → Cognitive support (`cognitive_risk` flag)
- **Caregiver Support** → Respite services (`caregiver_burnout` flag)

**Hub Display:** `hubs/partners.py` or `hubs/trusted_partners.py`

**Configuration:**
```python
{
    "key": "omcare",
    "type": "partner",
    "title": "Omcare Medication Management",
    "subtitle": "Remote medication dispensing for {name}.",
    "hubs": ["concierge", "trusted_partners"],
    "visible_when": [
        {"includes": {"path": "flags", "value": "medication_risk"}}
    ]
}
```

**Current State:** ✅ Implemented and working

---

### 2. Product Tiles (Multiple Hubs)

**Purpose:** Other products in the product suite that can appear in any hub

**Examples:**
- **Cost Planner** → Calculate care costs (appears in Concierge Hub after GCP)
- **PFMA** → Schedule advisor meeting (appears in Concierge Hub after Cost Planner)
- **GCP** → Care assessment (always visible, appears in Concierge/Learning Hubs)

**Hub Display:** Can appear in any hub based on `hubs` config

**Configuration:**
```python
{
    "key": "cost_planner_recommend",
    "type": "product",
    "title": "Cost Planner",
    "subtitle": "Estimate monthly costs based on your {recommendation} recommendation.",
    "hubs": ["concierge"],
    "visible_when": [
        {"includes": {"path": "flags", "value": "cost_planner_enabled"}}
    ]
}
```

**Current State:** ✅ Partially implemented (Cost Planner, PFMA exist)

---

### 3. Service Category Tiles (Future Hubs)

**Purpose:** Specialized service categories that will have their own dedicated hubs

#### 3a. Estate Planning Services (Future Hub)

**Examples:**
- **Will & Trust Creation** → Legal documents for asset protection
- **Power of Attorney Setup** → Healthcare and financial decision-making
- **Beneficiary Planning** → Ensuring proper asset distribution
- **Estate Tax Planning** → Minimizing tax burden for heirs

**Triggers:**
- High asset values detected in Cost Planner
- Age-based recommendations (65+, 75+)
- Complex family situations (multiple beneficiaries)

**Future Hub:** `hubs/estate_planning.py`

**Sample Configuration:**
```python
{
    "key": "estate_planning_suite",
    "type": "service",
    "title": "Estate Planning Services",
    "subtitle": "Protect assets and plan for {name}'s legacy.",
    "hubs": ["concierge", "estate_planning"],
    "visible_when": [
        {"runway_low": {"value": 60}},  # Have substantial assets
        {"includes": {"path": "flags", "value": "complex_estate"}}
    ]
}
```

**Current State:** ❌ Not implemented (future enhancement)

---

#### 3b. Retirement Planning Services (Future Hub)

**Examples:**
- **Social Security Optimization** → Maximize benefits timing
- **Medicare Planning** → Part B/D enrollment, Medigap
- **Retirement Income Strategies** → Annuities, withdrawals, tax planning
- **401(k)/IRA Management** → Required distributions, conversions

**Triggers:**
- User approaching 65 (Medicare eligibility)
- Low runway with assets (need optimization)
- Complex retirement accounts detected

**Future Hub:** `hubs/retirement_planning.py`

**Sample Configuration:**
```python
{
    "key": "social_security_optimizer",
    "type": "service",
    "title": "Social Security Optimization",
    "subtitle": "Maximize retirement benefits for {name}.",
    "hubs": ["concierge", "retirement_planning"],
    "visible_when": [
        {"includes": {"path": "flags", "value": "retirement_age"}},
        {"cost_gap": {"value": 200}}  # Small gap, optimization could help
    ]
}
```

**Current State:** ❌ Not implemented (future enhancement)

---

#### 3c. Legal Services (Future Hub)

**Examples:**
- **Elder Law Attorney** → Long-term care planning, Medicaid
- **Healthcare Advocate** → Insurance claims, medical billing
- **Guardianship Services** → Legal authority for care decisions
- **Patient Rights Advocacy** → Healthcare facility disputes

**Triggers:**
- Medicaid planning needed (cost gaps, asset protection)
- Complex medical situations (multiple conditions, hospitalizations)
- Cognitive decline (power of attorney, guardianship)

**Future Hub:** `hubs/legal_services.py`

**Sample Configuration:**
```python
{
    "key": "elder_law_attorney",
    "type": "service",
    "title": "Elder Law Attorney",
    "subtitle": "Protect assets and plan for long-term care expenses.",
    "hubs": ["concierge", "legal_services", "trusted_partners"],
    "visible_when": [
        {"cost_gap": {"value": 500}},
        {"includes": {"path": "flags", "value": "medicaid_likely"}}
    ]
}
```

**Current State:** ✅ Elder Law Attorney exists as partner (can evolve into hub)

---

#### 3d. Financial Advisory Services (Future Hub)

**Examples:**
- **Reverse Mortgage Advisor** → Home equity for care funding
- **Long-Term Care Insurance** → Policy evaluation and enrollment
- **Asset Liquidation Planning** → Sell assets to fund care
- **Family Financial Coordination** → Multi-generational planning

**Triggers:**
- Low runway (<36 months)
- High monthly costs (>$4000)
- Significant home equity detected
- Family support patterns (multiple children contributing)

**Future Hub:** `hubs/financial_advisory.py`

**Sample Configuration:**
```python
{
    "key": "reverse_mortgage",
    "type": "service",
    "title": "Reverse Mortgage Options",
    "subtitle": "Unlock home equity to fund care costs for {name}.",
    "hubs": ["concierge", "financial_advisory", "trusted_partners"],
    "visible_when": [
        {"runway_low": {"value": 36}}
    ]
}
```

**Current State:** ✅ Reverse Mortgage exists as partner (can evolve into hub)

---

#### 3e. Care Coordination Services (Future Hub)

**Examples:**
- **Care Manager** → Daily care coordination and oversight
- **Family Portal** → Communication hub for distributed families
- **Medical Record Integration** → Centralize health information
- **Transition Support** → Hospital-to-home or home-to-facility

**Triggers:**
- Complex care needs (multiple flags)
- Family caregiver burnout
- Multiple healthcare providers
- Recent hospitalization or transition

**Future Hub:** `hubs/care_coordination.py`

**Sample Configuration:**
```python
{
    "key": "professional_care_manager",
    "type": "service",
    "title": "Professional Care Manager",
    "subtitle": "Coordinate all aspects of care for {name}.",
    "hubs": ["concierge", "care_coordination"],
    "visible_when": [
        {"includes": {"path": "flags", "value": "caregiver_burnout"}},
        {"includes": {"path": "flags", "value": "complex_care_needs"}}
    ]
}
```

**Current State:** ❌ Not implemented (future enhancement)

---

### Service Type Summary Table

| Service Type | Current State | Hub Location | Filtering Logic |
|--------------|---------------|--------------|-----------------|
| **Trusted Partners** | ✅ Implemented | `hubs/partners.py` | Flag-based (risk flags from GCP) |
| **Product Tiles** | ✅ Implemented | Multiple hubs | Journey-based (MCIP product state) |
| **Estate Planning** | ❌ Future | `hubs/estate_planning.py` | Asset-based + age-based |
| **Retirement Planning** | ❌ Future | `hubs/retirement_planning.py` | Age-based + optimization needs |
| **Legal Services** | ⚠️ Partial | `hubs/legal_services.py` | Complex care + financial needs |
| **Financial Advisory** | ⚠️ Partial | `hubs/financial_advisory.py` | Runway + cost gap based |
| **Care Coordination** | ❌ Future | `hubs/care_coordination.py` | Multi-flag + caregiver support |

---

## Rule Types Reference

### Existing Rules

| Rule Type | Description | Example |
|-----------|-------------|---------|
| `equals` | Path equals value | `{"equals": {"path": "role", "value": "professional"}}` |
| `includes` | Value in container (list/dict) | `{"includes": {"path": "flags", "value": "fall_risk"}}` |
| `exists` | Path exists and not None | `{"exists": {"path": "gcp.recommendation"}}` |
| `min_progress` | Numeric >= threshold | `{"min_progress": {"path": "cost.progress", "value": 100}}` |
| `role_in` | Role in allowed list | `{"role_in": ["professional", "admin"]}` |

### New Rules (MCIP Financial)

| Rule Type | Description | Example |
|-----------|-------------|---------|
| `cost_gap` | Financial gap >= threshold | `{"cost_gap": {"value": 500}}` |
| `runway_low` | Runway months <= threshold | `{"runway_low": {"value": 36}}` |

---

## Example User Journey

### Step 1: User Completes GCP

**MCIP State:**
```python
CareRecommendation(
    tier="assisted_living",
    confidence=0.85,
    flags=[
        {"id": "fall_risk", "label": "Falls Risk", ...},
        {"id": "medication_risk", "label": "Medication Management", ...}
    ]
)
```

**Additional Services Shows:**
- ✅ Omcare (medication_risk)
- ✅ Fall Prevention (fall_risk)
- ✅ Cost Planner (if enabled)

---

### Step 2: User Completes Cost Planner

**MCIP State:**
```python
FinancialProfile(
    estimated_monthly_cost=4500,
    gap_amount=800,          # Monthly gap
    runway_months=30,        # Funds last 30 months
    confidence=0.90
)
```

**Additional Services Adds:**
- ✅ Reverse Mortgage (runway_low: 30 <= 36)
- ✅ Elder Law Attorney (cost_gap: 800 >= 500)
- ✅ PFMA (cost.progress == 100)

---

## Backwards Compatibility

The integration maintains full backwards compatibility with legacy systems:

### Legacy Handoff Support

```python
# Old system still works
st.session_state["handoff"] = {
    "gcp": {
        "recommendation": "assisted_living",
        "flags": {
            "fall_risk": True,
            "medication_risk": True
        }
    }
}
```

### Migration Path

**Phase 1:** Products publish to MCIP (✅ Done - GCP v4, Cost Planner v2)  
**Phase 2:** Additional Services reads from MCIP (✅ Done - This doc)  
**Phase 3:** Deprecate handoff writes (Future - once all products migrate)

---

## Testing Checklist

### Flag-Based Services

- [ ] Complete GCP v4 with fall risk answers
- [ ] Verify `fall_risk` flag in MCIP
- [ ] Check Additional Services shows "Fall Prevention & Safety"
- [ ] Complete GCP v4 with medication complexity
- [ ] Verify `medication_risk` flag in MCIP
- [ ] Check Additional Services shows "Omcare"

### Financial Services

- [ ] Complete GCP v4 (any tier)
- [ ] Complete Cost Planner v2
- [ ] Verify financial profile in MCIP with gap > $500
- [ ] Check Additional Services shows "Elder Law Attorney"
- [ ] Set runway < 36 months in Cost Planner
- [ ] Check Additional Services shows "Reverse Mortgage Options"

### Personalization

- [ ] Enter name "Dorothy" in welcome flow
- [ ] Complete GCP → tier = "assisted_living"
- [ ] Check service subtitles show "for Dorothy"
- [ ] Check Cost Planner subtitle shows "Assisted Living recommendation"

---

## Code Locations

### Core Files
- **Main Logic:** `core/additional_services.py`
- **MCIP Integration:** `core/mcip.py`
- **GCP Flags:** `products/gcp_v4/modules/care_recommendation/flags.py`

### Usage Locations
- **Concierge Hub:** `hubs/concierge.py` (calls `get_additional_services()`)
- **Trusted Partners:** `hubs/trusted_partners.py`
- **Waiting Room:** `hubs/waiting_room.py`

---

## Future Enhancements

### Phase 1: Additional Rule Types

1. **Confidence-Based Filtering:**
   ```python
   {"min_confidence": {"path": "mcip.confidence", "value": 0.7}}
   ```

2. **Tier-Specific Services:**
   ```python
   {"tier_in": {"value": ["memory_care", "assisted_living"]}}
   ```

3. **Coverage Percentage:**
   ```python
   {"coverage_below": {"value": 50}}  # <50% covered
   ```

4. **Age-Based Filtering:**
   ```python
   {"age_range": {"value": "65_plus"}}
   ```

5. **Multi-Flag Combinations (AND logic):**
   ```python
   {"all_flags": {"value": ["fall_risk", "cognitive_risk", "medication_risk"]}}
   ```

---

### Phase 2: New Service Hubs

#### Estate Planning Hub (`hubs/estate_planning.py`)

**Services:**
- Will & Trust Creation
- Power of Attorney Setup
- Beneficiary Planning
- Estate Tax Planning
- Asset Protection Strategies

**Implementation Steps:**
1. Create hub file with standard hub structure
2. Uncomment estate planning tiles in REGISTRY
3. Add route to `config/nav.json`
4. Create hub-specific UI components
5. Test with high-asset users

**Timeline:** Q2 2026

---

#### Retirement Planning Hub (`hubs/retirement_planning.py`)

**Services:**
- Social Security Optimization
- Medicare Planning & Enrollment
- Retirement Income Strategies
- 401(k)/IRA Management
- Pension Coordination

**Implementation Steps:**
1. Create hub file
2. Uncomment retirement planning tiles in REGISTRY
3. Add age-based filtering logic
4. Integrate with Social Security API (if available)
5. Test with pre-retirement users (60-65)

**Timeline:** Q3 2026

---

#### Legal Services Hub (`hubs/legal_services.py`)

**Services:**
- Elder Law Attorney
- Healthcare Advocate
- Guardianship Services
- Patient Rights Advocacy
- Medicaid Application Assistance

**Implementation Steps:**
1. Promote Elder Law Attorney from partner to hub anchor
2. Create dedicated hub
3. Add legal service tiles
4. Partner with legal service providers
5. Add attorney matching logic

**Timeline:** Q1 2026 (High Priority)

---

#### Financial Advisory Hub (`hubs/financial_advisory.py`)

**Services:**
- Reverse Mortgage Advisor
- Long-Term Care Insurance
- Asset Liquidation Planning
- Family Financial Coordination
- Care Funding Strategies

**Implementation Steps:**
1. Promote Reverse Mortgage from partner to hub anchor
2. Create dedicated hub
3. Add financial advisory tiles
4. Integrate with financial calculators
5. Add advisor matching logic

**Timeline:** Q1 2026 (High Priority)

---

#### Care Coordination Hub (`hubs/care_coordination.py`)

**Services:**
- Professional Care Manager
- Family Communication Portal
- Medical Record Integration
- Transition Support (Hospital-to-Home)
- Multi-Provider Coordination

**Implementation Steps:**
1. Create hub file
2. Add care coordination tiles
3. Build family portal features
4. Integrate with EHR systems (future)
5. Add care team collaboration tools

**Timeline:** Q4 2026

---

### Phase 3: Enhanced Partner Network

1. **Expand Trusted Partners:**
   - Add 50+ vetted partners per category
   - Regional partner matching (based on zip code)
   - Insurance network integration
   - Partner rating/review system

2. **Partner API Integration:**
   - Real-time availability checking
   - Automated referral submission
   - Status tracking for user
   - Partner performance analytics

3. **Smart Matching:**
   - Multi-factor partner scoring
   - User preference learning
   - Historical outcome tracking
   - Network quality optimization

---

### Phase 4: Advanced Personalization

1. **Machine Learning Integration:**
   - Predictive service recommendations
   - User journey pattern analysis
   - Churn risk identification
   - Outcome prediction modeling

2. **Dynamic Pricing Display:**
   - Show estimated service costs
   - Compare pricing across partners
   - Insurance coverage estimation
   - ROI calculations for services

3. **Behavioral Triggers:**
   - Time-on-site based recommendations
   - Engagement pattern analysis
   - Abandoned journey recovery
   - Proactive outreach timing

---

### Potential New Services by Category

#### Trusted Partners (Expand Current)
- **Home Modification Services** (independent living + fall risk)
- **Telehealth Coordination** (cognitive risk + chronic conditions)
- **Nutrition & Meal Planning** (dietary restrictions + chronic conditions)
- **Transportation Services** (mobility limitations)
- **Adult Day Programs** (caregiver respite + social engagement)

#### Estate Planning Hub (New)
- **Special Needs Trusts** (disabled beneficiaries)
- **Charitable Giving Planning** (philanthropy + tax optimization)
- **Business Succession** (business owners)
- **Digital Estate Planning** (online accounts, cryptocurrency)

#### Retirement Planning Hub (New)
- **Long-Term Care Insurance Review** (pre-retirement planning)
- **Pension Maximization** (pension holders)
- **Tax-Efficient Withdrawal Strategies** (high assets)
- **Annuity Analysis** (guaranteed income needs)

#### Legal Services Hub (Expand Current)
- **Guardianship/Conservatorship** (cognitive decline)
- **Medical Advocacy** (complex healthcare disputes)
- **Insurance Appeals** (claim denials)
- **Facility Contract Review** (moving to assisted living)

#### Financial Advisory Hub (Expand Current)
- **Life Insurance Policy Evaluation** (viatical settlements)
- **Family Lending Coordination** (children contributing to care)
- **Trust Administration** (existing trusts)
- **Asset Protection Strategies** (high-net-worth)

#### Care Coordination Hub (New)
- **Hospital Discharge Planning** (transitions of care)
- **Multi-Specialist Coordination** (complex conditions)
- **Clinical Trial Matching** (treatment options)
- **Second Opinion Services** (major medical decisions)

---

## Summary

✅ **Additional Services now reads from MCIP v2**
- Gets flags from `CareRecommendation.flags`
- Gets financial data from `FinancialProfile`
- Personalizes with user name and care tier
- Shows financially-relevant services based on gaps/runway
- Maintains backwards compatibility with legacy handoff

✅ **Benefit to User:**
- Sees personalized recommendations immediately after GCP
- Gets financial services when they need them (after Cost Planner)
- Experiences consistent messaging across entire journey
- Never sees irrelevant services (smart flag-based filtering)

✅ **Benefit to System:**
- Single source of truth (MCIP)
- Clean separation of concerns
- Extensible rule system
- Easy to add new services without changing core logic

**Next Steps:**
1. Test flag-based filtering with GCP v4 outcomes
2. Test financial-based filtering with Cost Planner v2 outcomes
3. Add authentication integration for personalized "Hey Dorothy!" messaging
4. Create MCIP journey status component to show progress

---

**Document Version:** 1.0  
**Last Updated:** October 13, 2025  
**Author:** Development Team  
**Related Docs:** 
- `MCIP_PRODUCT_MODULE_PATTERN.md`
- `COST_PLANNER_V2_MCIP_INTEGRATION.md`
- `E2E_INTEGRATION_TEST_GUIDE.md`

---

## Hub Architecture & Integration

### Current Hub Ecosystem

```
┌─────────────────────────────────────────────────────────────┐
│                    Navigation Layer                         │
│                   (config/nav.json)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│  Product Hubs    │        │  Service Hubs    │
│  (Orchestrated)  │        │  (Recommended)   │
└──────────────────┘        └──────────────────┘
         │                           │
    ┌────┴────┬─────┬─────┐   ┌─────┴──────┬──────┐
    ▼         ▼     ▼     ▼   ▼            ▼      ▼
┌────────┐ ┌────┐ ┌───┐ ┌──┐ ┌─────────┐ ┌────┐ ┌────┐
│Concierge│ │GCP │ │Cost│ │PF│ │Partners │ │Learn│ │Wait│
│  Hub   │ │ v4 │ │ v2 │ │MA│ │   Hub   │ │ Hub │ │Room│
└────────┘ └────┘ └───┘ └──┘ └─────────┘ └────┘ └────┘
    │         ▲     ▲    ▲        │          │      │
    │         └─────┴────┘        │          │      │
    │      (MCIP orchestrates)    │          │      │
    │                              │          │      │
    └──────────────┬───────────────┴──────────┴──────┘
                   ▼
       ┌──────────────────────┐
       │ Additional Services  │
       │   (Dynamic Tiles)    │
       └──────────────────────┘
                   │
       Reads from MCIP v2 to filter/personalize
```

### Hub Types

#### 1. Product Hubs (MCIP-Orchestrated)

**Concierge Hub** (`hubs/concierge.py`)
- Central navigation hub
- Shows product tiles (GCP, Cost Planner, PFMA)
- Shows additional service recommendations
- Displays MCIP journey progress
- **Reads:** `MCIP.is_product_unlocked()`, `MCIP.is_product_complete()`
- **Shows:** Product tiles + Additional services filtered by hub="concierge"

**GCP v4** (`products/gcp_v4/product.py`)
- Guided Care Plan assessment
- Publishes CareRecommendation to MCIP
- Shows next steps based on outcome
- **Writes:** `MCIP.publish_care_recommendation()`

**Cost Planner v2** (`products/cost_planner_v2/product.py`)
- Financial planning and cost estimation
- Gated by MCIP (requires GCP completion)
- Publishes FinancialProfile to MCIP
- **Reads:** `MCIP.get_care_recommendation()`
- **Writes:** `MCIP.publish_financial_profile()`

**PFMA** (`products/pfma/product.py`)
- Plan with My Advisor scheduling
- Gated by Cost Planner completion
- Publishes AdvisorAppointment to MCIP
- **Reads:** `MCIP.get_financial_profile()`
- **Writes:** `MCIP.publish_appointment()`

---

#### 2. Service Hubs (Additional Services)

**Partners Hub** (`hubs/partners.py` / `hubs/trusted_partners.py`)
- Shows trusted partner services
- Filtered by flags from MCIP
- **Displays:** `get_additional_services(hub="trusted_partners")`
- **Examples:** Omcare, SeniorLife AI, Fall Prevention, Companion Care

**Learning Hub** (`hubs/learning.py`)
- Educational content and resources
- Always available (not gated)
- May show flag-based content recommendations
- **Displays:** `get_additional_services(hub="learning")` + static content

**Waiting Room Hub** (`hubs/waiting_room.py`)
- For users waiting for appointments/transitions
- Shows relevant services and content
- **Displays:** `get_additional_services(hub="waiting_room")`

---

#### 3. Future Service Hubs (Planned)

**Estate Planning Hub** (Future: `hubs/estate_planning.py`)
- Will & Trust Creation
- Power of Attorney Setup
- Beneficiary Planning
- **Trigger:** High assets (runway > 60 months) OR age-based
- **Displays:** `get_additional_services(hub="estate_planning")`

**Retirement Planning Hub** (Future: `hubs/retirement_planning.py`)
- Social Security Optimization
- Medicare Planning
- Retirement Income Strategies
- **Trigger:** Age 60-65 OR retirement_age flag
- **Displays:** `get_additional_services(hub="retirement_planning")`

**Legal Services Hub** (Future: `hubs/legal_services.py`)
- Elder Law Attorney
- Healthcare Advocate
- Guardianship Services
- **Trigger:** Medicaid planning OR complex care needs
- **Displays:** `get_additional_services(hub="legal_services")`

**Financial Advisory Hub** (Future: `hubs/financial_advisory.py`)
- Reverse Mortgage Options
- Long-Term Care Insurance
- Asset Liquidation Planning
- **Trigger:** Low runway (<36 months) OR high cost gap
- **Displays:** `get_additional_services(hub="financial_advisory")`

**Care Coordination Hub** (Future: `hubs/care_coordination.py`)
- Professional Care Manager
- Family Communication Portal
- Medical Record Integration
- **Trigger:** Caregiver burnout OR complex care needs
- **Displays:** `get_additional_services(hub="care_coordination")`

---

### How Additional Services Populates Hubs

**Single Function, Multiple Hubs:**

```python
# In any hub file:
from core.additional_services import get_additional_services

# Get tiles filtered for this specific hub
tiles = get_additional_services(hub="concierge", limit=5)

# Each tile already knows:
# - Is it visible? (flags, financial data, journey state)
# - What's the personalized subtitle? ("for Dorothy", "Assisted Living")
# - Where does it route? (partner page, product, module)
# - What type is it? (partner, product, service, module)
```

**Example: Concierge Hub Integration**

```python
def render_concierge_hub():
    # Show products (orchestrated by MCIP)
    render_product_tiles()  # GCP, Cost Planner, PFMA
    
    # Show additional services (filtered by MCIP)
    additional_tiles = get_additional_services(hub="concierge", limit=3)
    render_additional_services_section(additional_tiles)
```

**Result:**
- User sees GCP (always available)
- User completes GCP → Cost Planner unlocks (MCIP)
- User sees Omcare tile (medication_risk flag from GCP)
- User completes Cost Planner → PFMA unlocks (MCIP)
- User sees Reverse Mortgage tile (runway < 36 months from Cost Planner)

---

### Hub Creation Pattern (For Future Hubs)

**Template for New Service Hub:**

```python
# hubs/new_hub.py
from core.additional_services import get_additional_services
from core.mcip import MCIP
import streamlit as st

def render():
    """Render the [Hub Name] hub."""
    
    # 1. Get user context
    person_name = st.session_state.get("person_name", "your loved one")
    
    # 2. Get MCIP data for context
    care_rec = MCIP.get_care_recommendation()
    financial = MCIP.get_financial_profile()
    
    # 3. Header with context
    st.markdown(f"# {hub_title}")
    st.markdown(f"Personalized recommendations for {person_name}")
    
    # 4. Show context from MCIP (optional)
    if care_rec:
        st.info(f"Based on {care_rec.tier.replace('_', ' ').title()} care recommendation")
    
    # 5. Get filtered tiles for this hub
    tiles = get_additional_services(hub="new_hub_key")
    
    # 6. Render tiles
    if tiles:
        for tile in tiles:
            render_service_tile(tile)
    else:
        st.info("No services available at this time.")
    
    # 7. Navigation
    if st.button("← Back to Concierge Hub"):
        st.switch_page("pages/hub_concierge.py")
```

**Steps to Add New Hub:**
1. Create hub file: `hubs/new_hub.py`
2. Add tiles to REGISTRY in `core/additional_services.py`
3. Set `hubs: ["concierge", "new_hub_key"]` in tile configs
4. Add route to `config/nav.json`
5. Test filtering logic with MCIP data
6. Add hub to navigation UI

---
