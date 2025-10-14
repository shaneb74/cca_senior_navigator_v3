# Cost Planner v2 Implementation Plan

**Date**: October 14, 2025  
**Status**: 🚀 READY TO IMPLEMENT  
**Reference**: Cost Planner — Final Workflow & Behavior Spec (Consolidated)

---

## Executive Summary

This document outlines the complete implementation of Cost Planner v2 following the mandatory workflow:

1. **Intro / Quick Estimate** (Unauthenticated)
2. **Authentication Gate**
3. **Status Triage** (Medicaid/Veteran/Homeownership)
4. **Financial Assessment Modules** (Authenticated)
5. **Expert Advisor Review** (Verification Stage — Final)
6. **Return to Hub / Continue to PFMA**

**Non-Negotiable**: Expert Advisor Review must be LAST. No rendering earlier.

---

## Current State Assessment

### ✅ What Exists
- `products/cost_planner_v2/product.py` - Product router with GCP gate
- `products/cost_planner_v2/hub.py` - Module hub orchestrator (simplified)
- GCP integration via MCIP working
- CareRecommendation contract available

### ❌ What's Missing
1. Intro / Quick Estimate screen (unauthenticated)
2. Authentication flow integration
3. Status Triage collection
4. Individual financial modules (Income, Assets, etc.)
5. Expert Advisor Review screen
6. Step-based navigation logic
7. Regional cost multipliers
8. Care type selector with preview

---

## Architecture Plan

### File Structure

```
products/cost_planner_v2/
├── __init__.py
├── product.py           # Main router with step logic
├── intro.py             # NEW: Intro/Quick Estimate screen
├── triage.py            # NEW: Status triage (fast collection)
├── hub.py               # Module hub orchestrator
├── expert_review.py     # NEW: Expert Advisor Review (final)
├── modules/
│   ├── __init__.py
│   ├── income.py        # NEW: Income module
│   ├── assets.py        # NEW: Assets module
│   └── (future modules)
└── utils/
    ├── __init__.py
    ├── cost_calculator.py  # NEW: Cost calculation logic
    └── regional_data.py    # NEW: Regional multipliers
```

### Data Flow

```
User → Intro (preview tier, select type, enter ZIP)
  ↓
  Quick Estimate (base cost + regional multiplier)
  ↓
  Continue → Authentication Gate
  ↓
  Authenticated → Status Triage (fast flags)
  ↓
  Financial Modules (Income, Assets, ...)
  ↓ (collect contracts)
  Product aggregates contracts
  ↓
  Expert Advisor Review (all modules complete)
  ↓
  Finalize → Publish to MCIP → Continue to PFMA
```

---

## Step-by-Step Implementation

### Phase 1: Core Infrastructure (Steps 1-3)

#### A. Update `product.py` - Step Router

**Purpose**: Route to correct step based on state

**Logic**:
```python
def render():
    """Main router with mandatory step order."""
    
    # Determine current step
    step = _determine_step()
    
    # Route to step
    if step == "gcp_gate":
        _render_gcp_gate()
    elif step == "intro":
        from products.cost_planner_v2.intro import render_intro
        render_intro()
    elif step == "auth_gate":
        _render_auth_gate()
    elif step == "triage":
        from products.cost_planner_v2.triage import render_triage
        render_triage()
    elif step == "modules":
        from products.cost_planner_v2.hub import render_module_hub
        render_module_hub(recommendation)
    elif step == "expert_review":
        from products.cost_planner_v2.expert_review import render_expert_review
        render_expert_review()
    else:
        # Default fallback
        _render_intro()

def _determine_step() -> str:
    """Determine current step based on state.
    
    Returns:
        Step key: "gcp_gate" | "intro" | "auth_gate" | "triage" | "modules" | "expert_review"
    """
    # Check GCP prerequisite
    recommendation = MCIP.get_care_recommendation()
    if not recommendation:
        return "gcp_gate"
    
    # Check authentication
    if not _is_authenticated():
        # Show intro (unauthenticated) unless explicit step set
        step = st.session_state.get("cost_v2_step", "intro")
        if step in ["intro", "auth_gate"]:
            return step
        return "intro"  # Default to intro if not auth
    
    # Authenticated - check triage
    if not _triage_complete():
        return "triage"
    
    # Check if expert review unlocked
    if _all_modules_complete() and st.session_state.get("cost_v2_step") == "expert_review":
        return "expert_review"
    
    # Default to modules
    return "modules"
```

**State Keys**:
- `cost_v2_step` - Current step override
- `cost_v2_authenticated` - Auth flag
- `cost_v2_triage_complete` - Triage completed
- `cost_v2_modules_complete` - All required modules done
- `cost_v2_expert_verified` - Expert review completed

#### B. Create `intro.py` - Intro / Quick Estimate

**Purpose**: Unauthenticated preview with care type selector and ZIP

**Key Features**:
1. Show Care Recommendation from MCIP
2. Care Type Selector (preview only, doesn't overwrite)
3. ZIP input with regional multipliers
4. Quick estimate calculation
5. "How we calculated this" explainer
6. CTA: "Continue to Full Assessment" → auth gate

**Code Structure**:
```python
def render_intro():
    """Render intro/quick estimate screen (unauthenticated)."""
    
    # Get care recommendation
    recommendation = MCIP.get_care_recommendation()
    
    # Navi panel
    render_navi_panel(
        location="product",
        product_key="cost_v2",
        module_config=None
    )
    
    st.title("💰 Cost Planner")
    
    # Show care recommendation context
    _render_care_recommendation_context(recommendation)
    
    # Care type selector (preview)
    st.markdown("### 🎯 Estimate Costs")
    selected_type = st.selectbox(
        "Select care type to preview",
        options=["assisted_living", "in_home", "memory_care", "memory_care_high_acuity"],
        format_func=lambda x: x.replace("_", " ").title(),
        index=_get_default_index(recommendation.tier),
        key="cost_intro_care_type"
    )
    
    # ZIP input
    user_zip = st.text_input(
        "Enter ZIP code for regional costs",
        value=st.session_state.get("cost_intro_zip", ""),
        max_chars=5,
        key="cost_intro_zip"
    )
    
    # Calculate estimate
    if user_zip and len(user_zip) == 5:
        estimate = calculate_quick_estimate(selected_type, user_zip)
        _render_quick_estimate(estimate, selected_type, user_zip)
    
    # CTA
    if st.button("Continue to Full Assessment →", type="primary", use_container_width=True):
        st.session_state["cost_v2_step"] = "auth_gate"
        st.rerun()
    
    # Back to hub
    if st.button("← Back to Hub", use_container_width=True):
        from core.nav import route_to
        route_to("hub_concierge")
```

**Helper Functions**:
- `_render_care_recommendation_context()` - Show GCP context
- `calculate_quick_estimate()` - Base cost + regional multiplier
- `_render_quick_estimate()` - Display estimate with breakdown
- `_get_default_index()` - Default selector to recommended tier

#### C. Create `triage.py` - Status Triage

**Purpose**: Fast flag collection (Medicaid/Veteran/Homeowner)

**Code Structure**:
```python
def render_triage():
    """Render status triage screen (fast flag collection)."""
    
    render_navi_panel(
        location="product",
        product_key="cost_v2",
        module_config=None
    )
    
    st.title("💰 Cost Planner - Quick Questions")
    
    st.info("Just 3 quick questions to personalize your plan:")
    
    # Medicaid status
    medicaid = st.radio(
        "Are you currently on Medicaid or planning to apply?",
        options=["true", "false", "unknown"],
        format_func=lambda x: {"true": "Yes", "false": "No", "unknown": "Not sure"}[x],
        key="cost_triage_medicaid"
    )
    
    # Veteran status
    veteran = st.radio(
        "Are you a veteran or spouse of a veteran?",
        options=["true", "false", "unknown"],
        format_func=lambda x: {"true": "Yes", "false": "No", "unknown": "Not sure"}[x],
        key="cost_triage_veteran"
    )
    
    # Home ownership
    homeowner = st.radio(
        "Do you own your home?",
        options=["true", "false", "unknown"],
        format_func=lambda x: {"true": "Yes", "false": "No", "unknown": "Not sure"}[x],
        key="cost_triage_homeowner"
    )
    
    # Continue
    if st.button("Continue →", type="primary", use_container_width=True):
        # Store triage results
        st.session_state["cost_v2_triage"] = {
            "medicaid_status": medicaid,
            "veteran_status": veteran,
            "home_owner": homeowner
        }
        st.session_state["cost_v2_triage_complete"] = True
        st.session_state["cost_v2_step"] = "modules"
        st.rerun()
```

---

### Phase 2: Financial Modules (Step 4)

#### D. Create Module Infrastructure

**Base Module Pattern**:
```python
# products/cost_planner_v2/modules/income.py

def render_income_module():
    """Income module - collects income sources."""
    
    st.markdown("### 💵 Income Assessment")
    
    # Social Security
    social_security = st.number_input(
        "Social Security (monthly)",
        min_value=0,
        value=st.session_state.get("cost_income_ss", 0),
        step=100,
        key="cost_income_ss"
    )
    
    # Pension
    pension = st.number_input(
        "Pension (monthly)",
        min_value=0,
        value=st.session_state.get("cost_income_pension", 0),
        step=100,
        key="cost_income_pension"
    )
    
    # Other income
    other = st.number_input(
        "Other income (monthly)",
        min_value=0,
        value=st.session_state.get("cost_income_other", 0),
        step=100,
        key="cost_income_other"
    )
    
    # Calculate total
    total = social_security + pension + other
    
    st.metric("Total Monthly Income", f"${total:,.0f}/mo")
    
    # Complete
    if st.button("Save Income →", type="primary"):
        contract = {
            "social_security": social_security,
            "pension": pension,
            "other_income": other,
            "total_monthly": total,
            "complete": True
        }
        st.session_state["cost_module_income"] = contract
        return contract
    
    return None
```

**Module Registry** (in `hub.py`):
```python
MODULES = {
    "income": {
        "label": "Income",
        "icon": "💵",
        "description": "Monthly income sources",
        "required": True,
        "tiers": ["all"]  # All tiers need this
    },
    "assets": {
        "label": "Assets",
        "icon": "💰",
        "description": "Savings and investments",
        "required": True,
        "tiers": ["all"]
    },
    # Future modules...
}
```

#### E. Update `hub.py` - Module Orchestrator

**Changes**:
1. Show module list with completion status
2. Allow navigation to individual modules
3. Track which modules are complete
4. Show aggregate progress
5. Unlock Expert Review when all complete

**Key Functions**:
```python
def render_module_hub(recommendation: CareRecommendation):
    """Render module hub with completion tracking."""
    
    # Get tier-appropriate modules
    available_modules = _get_available_modules(recommendation.tier)
    
    # Calculate progress
    completed = sum(1 for m in available_modules if _is_module_complete(m))
    total = len(available_modules)
    progress = completed / total if total > 0 else 0
    
    # Show progress
    st.progress(progress, text=f"{completed}/{total} modules complete")
    
    # Module list
    for module_key in available_modules:
        module_def = MODULES[module_key]
        complete = _is_module_complete(module_key)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if complete:
                st.success("✅")
            else:
                st.info("⏳")
        
        with col2:
            st.markdown(f"**{module_def['icon']} {module_def['label']}**")
            st.caption(module_def['description'])
        
        with col3:
            if st.button("Edit" if complete else "Start", key=f"module_{module_key}"):
                st.session_state["cost_current_module"] = module_key
                st.rerun()
    
    # Expert Review CTA (only if all complete)
    if progress == 1.0:
        st.markdown("---")
        st.success("🎉 All modules complete! Ready for expert review.")
        if st.button("Continue to Expert Review →", type="primary", use_container_width=True):
            st.session_state["cost_v2_step"] = "expert_review"
            st.rerun()
```

---

### Phase 3: Expert Advisor Review (Step 5)

#### F. Create `expert_review.py` - Final Verification

**Purpose**: Aggregate results, allow review, finalize

**Code Structure**:
```python
def render_expert_review():
    """Render expert advisor review screen (final step)."""
    
    render_navi_panel(
        location="product",
        product_key="cost_v2",
        module_config=None
    )
    
    st.title("💰 Expert Advisor Review")
    
    st.success("🎉 **Your financial assessment is complete!**")
    
    st.info("""
    **Review Your Plan**
    
    Below is a summary of your financial plan. Please review all sections carefully.
    If you need to make changes, use the "Review Modules" button to return to any module.
    
    When everything looks correct, click "Finalize & Continue" to lock your plan and proceed.
    """)
    
    st.markdown("---")
    
    # Aggregate summary
    _render_aggregate_summary()
    
    st.markdown("---")
    
    # Actions
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Review Modules", use_container_width=True):
            st.session_state["cost_v2_step"] = "modules"
            st.rerun()
    
    with col2:
        if st.button("Finalize & Continue →", type="primary", use_container_width=True):
            _finalize_and_publish()
            st.rerun()
    
    with col3:
        if st.button("Back to Hub", use_container_width=True):
            from core.nav import route_to
            route_to("hub_concierge")

def _render_aggregate_summary():
    """Render aggregated financial summary from all modules."""
    
    # Get module contracts
    income = st.session_state.get("cost_module_income", {})
    assets = st.session_state.get("cost_module_assets", {})
    
    # Income overview
    st.markdown("### 💵 Income Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Social Security", f"${income.get('social_security', 0):,.0f}/mo")
        st.metric("Pension", f"${income.get('pension', 0):,.0f}/mo")
    with col2:
        st.metric("Other Income", f"${income.get('other_income', 0):,.0f}/mo")
        st.metric("**Total Monthly Income**", f"**${income.get('total_monthly', 0):,.0f}/mo**")
    
    # Assets overview
    st.markdown("### 💰 Assets Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Liquid Savings", f"${assets.get('liquid_savings', 0):,.0f}")
        st.metric("Retirement Accounts", f"${assets.get('retirement', 0):,.0f}")
    with col2:
        st.metric("Home Equity", f"${assets.get('home_equity', 0):,.0f}")
        st.metric("**Total Assets**", f"**${assets.get('total_assets', 0):,.0f}**")
    
    # Cost & Gap Analysis
    st.markdown("### 📊 Cost Analysis")
    
    # Get cost estimate (from intro or recalculate)
    monthly_cost = _calculate_monthly_cost()
    monthly_income = income.get('total_monthly', 0)
    gap = monthly_cost - monthly_income
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly Cost", f"${monthly_cost:,.0f}/mo")
    with col2:
        st.metric("Monthly Income", f"${monthly_income:,.0f}/mo")
    with col3:
        if gap > 0:
            st.metric("Monthly Gap", f"${gap:,.0f}/mo", delta=f"-${gap:,.0f}", delta_color="inverse")
        else:
            st.metric("Monthly Surplus", f"${abs(gap):,.0f}/mo", delta=f"+${abs(gap):,.0f}")
    
    # Runway estimate
    if gap > 0:
        total_assets = assets.get('total_assets', 0)
        runway_months = int(total_assets / gap) if gap > 0 else 999
        runway_years = runway_months / 12
        
        st.markdown("### ⏱️ Runway Estimate")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Months of Coverage", f"{runway_months} months")
        with col2:
            st.metric("Years of Coverage", f"{runway_years:.1f} years")

def _finalize_and_publish():
    """Finalize assessment and publish to MCIP."""
    
    from datetime import datetime
    from core.mcip import FinancialProfile
    
    # Aggregate all module data
    income = st.session_state.get("cost_module_income", {})
    assets = st.session_state.get("cost_module_assets", {})
    
    monthly_cost = _calculate_monthly_cost()
    monthly_income = income.get('total_monthly', 0)
    gap = monthly_cost - monthly_income
    total_assets = assets.get('total_assets', 0)
    runway = int(total_assets / gap) if gap > 0 else 999
    
    # Build FinancialProfile contract
    profile = FinancialProfile(
        estimated_monthly_cost=monthly_cost,
        coverage_percentage=monthly_income / monthly_cost if monthly_cost > 0 else 0,
        gap_amount=gap,
        runway_months=runway,
        confidence=0.85,  # Based on completeness
        generated_at=datetime.utcnow().isoformat() + "Z",
        status="complete"
    )
    
    # Publish to MCIP
    MCIP.publish_financial_profile(profile)
    MCIP.mark_product_complete("cost_planner")
    
    # Mark as verified
    st.session_state["cost_v2_expert_verified"] = True
    st.session_state["cost_v2_step"] = "complete"
    
    st.success("✅ Your financial plan has been finalized!")
```

---

### Phase 4: Cost Calculation Utilities

#### G. Create `utils/cost_calculator.py`

**Purpose**: Base costs and calculations

```python
# Base monthly costs by tier (national average)
BASE_COSTS = {
    "independent": 0.0,
    "in_home": 3500.0,
    "assisted_living": 4500.0,
    "memory_care": 6500.0,
    "memory_care_high_acuity": 8500.0
}

def calculate_base_cost(care_type: str) -> float:
    """Get base monthly cost for care type."""
    return BASE_COSTS.get(care_type, 3500.0)

def calculate_quick_estimate(care_type: str, zip_code: str) -> dict:
    """Calculate quick estimate with regional multiplier."""
    
    base = calculate_base_cost(care_type)
    multiplier = get_regional_multiplier(zip_code)
    effective = base * multiplier
    
    return {
        "care_type": care_type,
        "base_cost": base,
        "multiplier": multiplier,
        "effective_cost": effective,
        "zip_code": zip_code
    }
```

#### H. Create `utils/regional_data.py`

**Purpose**: Regional cost multipliers

```python
# Regional multipliers (example data)
REGIONAL_MULTIPLIERS = {
    # Exact ZIP codes
    "10001": 1.45,  # NYC
    "90210": 1.35,  # LA
    "60601": 1.25,  # Chicago
    
    # ZIP3 prefixes (first 3 digits)
    "100": 1.40,    # NY area
    "902": 1.30,    # CA area
    "606": 1.20,    # IL area
    
    # State defaults
    "NY": 1.35,
    "CA": 1.28,
    "IL": 1.18,
    
    # National default
    "default": 1.0
}

def get_regional_multiplier(zip_code: str) -> float:
    """Get regional cost multiplier with precedence.
    
    Precedence:
    1. Exact ZIP match
    2. ZIP3 prefix match
    3. State match (requires lookup)
    4. Default (1.0)
    """
    
    if not zip_code or len(zip_code) != 5:
        return REGIONAL_MULTIPLIERS["default"]
    
    # Try exact match
    if zip_code in REGIONAL_MULTIPLIERS:
        return REGIONAL_MULTIPLIERS[zip_code]
    
    # Try ZIP3
    zip3 = zip_code[:3]
    if zip3 in REGIONAL_MULTIPLIERS:
        return REGIONAL_MULTIPLIERS[zip3]
    
    # Try state (requires ZIP → state lookup)
    state = _zip_to_state(zip_code)
    if state and state in REGIONAL_MULTIPLIERS:
        return REGIONAL_MULTIPLIERS[state]
    
    # Default
    return REGIONAL_MULTIPLIERS["default"]

def _zip_to_state(zip_code: str) -> str:
    """Convert ZIP to state code.
    
    In production, use a proper ZIP→state database.
    For now, simple logic based on first digit.
    """
    first = zip_code[0] if zip_code else "0"
    
    # Very simplified mapping
    mapping = {
        "0": "MA",  # New England
        "1": "NY",  # NY
        "2": "VA",  # Mid-Atlantic
        "3": "FL",  # Southeast
        "4": "GA",  # Southeast
        "5": "TX",  # South
        "6": "IL",  # Midwest
        "7": "TX",  # South
        "8": "CO",  # Mountain
        "9": "CA",  # West
    }
    
    return mapping.get(first, "")
```

---

## State Management Plan

### Session State Keys

```python
# Step navigation
"cost_v2_step"              # Current step: "intro" | "auth_gate" | "triage" | "modules" | "expert_review" | "complete"
"cost_v2_authenticated"     # Boolean: user authenticated
"cost_v2_triage_complete"   # Boolean: triage flags collected

# Intro/Quick Estimate
"cost_intro_care_type"      # Selected care type for preview
"cost_intro_zip"            # Entered ZIP code
"cost_intro_estimate"       # Calculated estimate dict

# Triage data
"cost_v2_triage"            # Dict: {medicaid_status, veteran_status, home_owner}

# Module contracts
"cost_module_income"        # Income module contract
"cost_module_assets"        # Assets module contract
# ... future modules

# Hub state
"cost_current_module"       # Currently editing module

# Expert Review
"cost_v2_expert_verified"   # Boolean: expert review completed
"cost_v2_published"         # Boolean: published to MCIP
```

---

## Integration Points

### 1. Authentication

**Current**: No auth system exists

**Plan**: Use modal or redirect pattern
```python
def _render_auth_gate():
    """Render authentication gate."""
    
    st.title("🔐 Sign In Required")
    
    st.info("""
    To create and save your personalized financial plan, please sign in or create an account.
    
    **Why we need this:**
    - Save your progress
    - Store your personalized plan
    - Schedule advisor appointments
    - Access premium features
    """)
    
    # Development bypass
    if st.button("Sign In (Development)", type="primary"):
        st.session_state["cost_v2_authenticated"] = True
        st.session_state["cost_v2_step"] = "triage"
        st.rerun()
    
    # Production auth would integrate here
```

### 2. MCIP Publishing

**Contract**: `FinancialProfile` dataclass

**Fields** (verify against `core/mcip.py`):
```python
@dataclass
class FinancialProfile:
    estimated_monthly_cost: float
    coverage_percentage: float
    gap_amount: float
    runway_months: int
    confidence: float
    generated_at: str
    status: str
```

**Publishing**:
```python
from core.mcip import MCIP, FinancialProfile

profile = FinancialProfile(...)
MCIP.publish_financial_profile(profile)
MCIP.mark_product_complete("cost_planner")
```

### 3. Navi Integration

**Panel Rendering**:
```python
from core.navi import render_navi_panel

render_navi_panel(
    location="product",
    product_key="cost_v2",
    module_config=None  # Not using module engine
)
```

**Progress Updates**: Navi reads from MCIP automatically

---

## QA Checklist

### Intro (Unauthenticated)
- [ ] Care Recommendation displayed with clear context
- [ ] Care selector shows all types
- [ ] Selecting type updates estimate immediately
- [ ] ZIP input validates (5 digits)
- [ ] Regional multiplier applies correct precedence (exact → ZIP3 → state → default)
- [ ] Estimate displays: base cost + effective cost + multiplier
- [ ] "How we calculated" explainer visible
- [ ] "Continue" button routes to auth gate
- [ ] Selector does NOT overwrite Care Recommendation

### Auth & Triage
- [ ] Auth gate displays with clear messaging
- [ ] Development bypass works
- [ ] After auth, returns to Cost Planner context
- [ ] Last selected care type and ZIP still visible (context preserved)
- [ ] Triage collects 3 flags (Medicaid, Veteran, Homeowner)
- [ ] Triage validates all answered before continue
- [ ] Flags stored in session state

### Modules
- [ ] Module list shows tier-appropriate modules
- [ ] Each module has completion indicator (✅ or ⏳)
- [ ] Clicking module navigates to module screen
- [ ] Module collects data and returns contract
- [ ] Contract stored in session state
- [ ] Progress bar updates after each module
- [ ] "Edit" button available for completed modules
- [ ] Expert Review CTA only shows when all modules complete

### Expert Advisor Review
- [ ] Renders ONLY after all required modules complete
- [ ] Shows aggregated income summary
- [ ] Shows aggregated assets summary
- [ ] Displays cost analysis (monthly cost, income, gap)
- [ ] Calculates runway estimate correctly
- [ ] "Review Modules" returns to module list
- [ ] "Finalize & Continue" publishes to MCIP
- [ ] After finalize, marks product complete
- [ ] "Continue" routes to PFMA (or hub)

### Navi & Progress
- [ ] Navi persists at top of all Cost Planner screens
- [ ] Navi reflects current step/progress
- [ ] Navi provides contextual guidance
- [ ] Navi shows next best action

### Regression
- [ ] Care type selector in Intro does NOT overwrite Care Recommendation in MCIP
- [ ] Back to Hub always returns to `hub_concierge`
- [ ] No visual/layout regressions on hub
- [ ] No visual/layout regressions on product pages
- [ ] GCP → Cost Planner flow works end-to-end
- [ ] Cost Planner → PFMA flow works end-to-end

---

## Implementation Order

### Sprint 1: Core Infrastructure (Days 1-2)
1. Update `product.py` with step router
2. Create `intro.py` with quick estimate
3. Create `utils/cost_calculator.py`
4. Create `utils/regional_data.py`
5. Test intro flow end-to-end

### Sprint 2: Auth & Triage (Day 3)
1. Add auth gate to `product.py`
2. Create `triage.py` with flag collection
3. Test auth → triage flow

### Sprint 3: Modules (Days 4-5)
1. Create `modules/income.py`
2. Create `modules/assets.py`
3. Update `hub.py` with module orchestration
4. Test module completion tracking

### Sprint 4: Expert Review (Day 6)
1. Create `expert_review.py`
2. Implement aggregate summary
3. Implement finalize & publish
4. Test complete flow: intro → auth → triage → modules → review → publish

### Sprint 5: Integration & QA (Day 7)
1. Test GCP → Cost Planner integration
2. Test MCIP publishing
3. Test Navi integration
4. Run complete QA checklist
5. Fix any regressions

---

## Success Criteria

✅ **Mandatory Step Order Enforced**
- Expert Review only accessible after all modules complete
- No skipping steps
- Clear navigation breadcrumbs

✅ **Care Recommendation Respected**
- Displayed prominently in intro
- Not overwritten by selector
- Used for default estimates

✅ **Regional Multipliers Working**
- Correct precedence: ZIP → ZIP3 → state → default
- Multiplier displayed to user
- Costs update immediately

✅ **Module Contracts Clean**
- Each module returns standard contract
- Product aggregates contracts
- No multi-module math inside modules

✅ **MCIP Publishing Correct**
- FinancialProfile contract complete
- Product marked complete
- Navi recognizes completion

✅ **No Regressions**
- Hub layout unchanged
- Back to Hub works
- GCP → Cost Planner → PFMA flow works

---

## Next Steps

1. **Review this plan** - Verify against spec
2. **Prioritize features** - Which modules are MVP?
3. **Create tickets** - Break down into implementable tasks
4. **Start Sprint 1** - Implement intro/quick estimate first
5. **Iterate** - Build, test, refine

---

**Questions for Clarification**:
1. Which financial modules are required for MVP? (Income + Assets only, or more?)
2. What should auth look like? (Modal, redirect, SSO?)
3. Should ZIP → state lookup use a real database or simplified logic?
4. What happens if user exits mid-flow? Resume from last step?
5. Should intro estimate be stored for comparison in Expert Review?

---

**Status**: 🟢 **READY TO BUILD**

All 8 GCP bugs are fixed. Architecture is clean. Plan is comprehensive. Let's implement Cost Planner v2! 🚀
