# Cost Planner v2 - MCIP Integration Architecture

> **The Critical Handoff: GCP v4 → MCIP → Cost Planner v2**

This document defines how Cost Planner v2 integrates with MCIP to create seamless orchestration between care recommendation and financial planning.

---

## The Handoff Flow

```
GCP v4 completes
    ↓
Publishes CareRecommendation to MCIP
    ↓
MCIP stores in st.session_state["mcip"]["care_recommendation"]
    ↓
MCIP fires "mcip.recommendation.updated" event
    ↓
Concierge Hub refreshes (shows Cost Planner unlocked with silver gradient)
    ↓
User clicks Cost Planner tile
    ↓
Cost Planner v2 checks MCIP.get_care_recommendation()
    ↓
IF EXISTS: Show module hub with tier-appropriate modules
IF MISSING: Show friendly gate "Complete your Guided Care Plan first"
    ↓
User completes financial modules
    ↓
Cost Planner aggregates data
    ↓
Publishes FinancialProfile to MCIP
    ↓
MCIP fires "mcip.financial.updated" event
    ↓
Concierge Hub refreshes (shows PFMA unlocked)
```

---

## MCIP Data Contract

### What Cost Planner READS from MCIP

```python
recommendation = MCIP.get_care_recommendation()

# Cost Planner uses these fields:
recommendation.tier                 # "independent" | "in_home" | "assisted_living" | "memory_care"
recommendation.tier_score           # Float - used for filtering cost estimates
recommendation.confidence           # Float - shown in gate messaging
recommendation.flags                # List[Dict] - used for special cost considerations
recommendation.tier_rankings        # List[Tuple] - used for "What if?" comparisons
recommendation.next_step            # Dict - routing hint from GCP
```

### What Cost Planner PUBLISHES to MCIP

```python
from core.mcip import MCIP, FinancialProfile

financial_profile = FinancialProfile(
    # Monthly cost breakdown
    base_care_cost=4500.00,           # Core care/housing cost
    additional_services=850.00,        # Add-ons (therapy, transport, etc.)
    total_monthly_cost=5350.00,        # Base + additional
    
    # Annual projections
    annual_cost=64200.00,              # Total * 12
    three_year_projection=192600.00,   # With inflation
    five_year_projection=321000.00,    # With inflation
    
    # Funding sources
    funding_sources={
        "personal_savings": 2000.00,
        "family_contribution": 1500.00,
        "veteran_benefits": 1850.00,   # If qualified
        "insurance": 0.00,
        "medicare": 0.00,
        "medicaid": 0.00
    },
    funding_gap=0.00,                  # Cost - sources (negative = surplus)
    
    # Context
    care_tier="assisted_living",       # From MCIP recommendation
    region="northeast",                # User-specified
    facility_type="continuing_care",   # User selection
    
    # Provenance
    generated_at="2025-10-13T12:00:00Z",
    version="2.0.0",
    input_snapshot_id="cost_v2_anon_20251013_120000",
    
    # Status
    status="complete",
    last_updated="2025-10-13T12:00:00Z",
    needs_refresh=False
)

# Publish to MCIP (single source of truth)
MCIP.publish_financial_profile(financial_profile)
MCIP.mark_product_complete("cost_planner")
```

---

## Cost Planner v2 Architecture

### Product Structure

```
products/cost_planner_v2/
├── __init__.py
├── product.py                    # Entry point with MCIP gate
├── hub.py                        # Module hub (6 financial modules)
├── aggregator.py                 # Aggregates module outputs → FinancialProfile
└── modules/
    ├── base_care_cost/
    │   ├── module.json           # Questions about care tier, region, facility type
    │   ├── config.py             # Module config loader
    │   └── logic.py              # Cost lookup from config/regional_cost_config.json
    ├── care_hours/
    │   ├── module.json           # How many hours of care per day?
    │   ├── config.py
    │   └── logic.py              # Hourly rate * hours = additional cost
    ├── additional_services/
    │   ├── module.json           # Therapy, transport, activities, etc.
    │   ├── config.py
    │   └── logic.py              # Checkbox selection → costs
    ├── veteran_benefits/
    │   ├── module.json           # VA status, service period, disability rating
    │   ├── config.py
    │   └── logic.py              # Calculates Aid & Attendance eligibility
    ├── insurance_medicare/
    │   ├── module.json           # Medicare parts, supplemental, long-term care insurance
    │   ├── config.py
    │   └── logic.py              # Coverage amounts
    └── facility_selection/
        ├── module.json           # Browse/select specific facilities
        ├── config.py
        └── logic.py              # Facility-specific pricing
```

---

## Implementation Plan

### Step 1: Create GCP Gate (CRITICAL)

**File:** `products/cost_planner_v2/product.py`

```python
"""Cost Planner v2 - MCIP-driven financial planning."""

import streamlit as st
from core.mcip import MCIP
from core.nav import route_to


def render():
    """Render Cost Planner v2 with MCIP gate."""
    
    # GATE: Check if GCP recommendation exists
    recommendation = MCIP.get_care_recommendation()
    
    if not recommendation:
        _render_gcp_gate()
        return
    
    # GATE PASSED: Show module hub
    from products.cost_planner_v2.hub import render_module_hub
    render_module_hub(recommendation)


def _render_gcp_gate():
    """Show friendly gate requiring GCP completion."""
    
    st.info("### 💡 Complete Your Guided Care Plan First")
    
    st.markdown("""
    Before we can calculate costs, we need to know what level of care is recommended.
    
    The **Guided Care Plan** takes just 2 minutes and will:
    - ✅ Assess daily living needs
    - ✅ Evaluate safety and cognitive factors
    - ✅ Recommend the right care level
    - ✅ Unlock personalized cost estimates
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🎯 Start Guided Care Plan", type="primary", use_container_width=True):
            route_to("gcp_v4")
    
    with col2:
        if st.button("🏠 Return to Hub", use_container_width=True):
            route_to("hub_concierge")
```

**Key Points:**
- ✅ No direct state reads from `st.session_state["gcp"]`
- ✅ Only reads from MCIP conductor
- ✅ Friendly UX - explains why gate exists
- ✅ Clear path forward (Start GCP button)

---

### Step 2: Module Hub with Tier-Appropriate Modules

**File:** `products/cost_planner_v2/hub.py`

```python
"""Cost Planner v2 module hub - orchestrates financial modules."""

import streamlit as st
from typing import List, Dict
from core.mcip import MCIP, CareRecommendation
from core.modules.hub import ModuleHub
from core.modules.loader import discover_modules


def render_module_hub(recommendation: CareRecommendation):
    """Render module hub with tier-appropriate modules.
    
    Args:
        recommendation: Care recommendation from MCIP
    """
    
    st.title("💰 Financial Planning")
    
    # Show context from GCP
    _render_care_context(recommendation)
    
    st.markdown("---")
    
    # Load and filter modules based on care tier
    all_modules = discover_modules("products/cost_planner_v2/modules")
    unlocked_modules = _filter_modules_by_tier(all_modules, recommendation.tier)
    
    # Render module hub
    hub = ModuleHub(
        product_key="cost_planner_v2",
        modules=unlocked_modules,
        state_key="cost_planner_v2",
        on_complete=_on_all_modules_complete
    )
    
    hub.render()


def _render_care_context(recommendation: CareRecommendation):
    """Show care recommendation context at top of hub.
    
    Args:
        recommendation: Care recommendation from MCIP
    """
    tier_label = recommendation.tier.replace("_", " ").title()
    confidence_pct = int(recommendation.confidence * 100)
    
    st.info(f"""
    **Based on your Guided Care Plan:**
    - 🎯 Recommended Care Level: **{tier_label}**
    - 📊 Confidence: {confidence_pct}%
    
    We'll calculate costs specific to **{tier_label}** care.
    """)


def _filter_modules_by_tier(modules: List[Dict], tier: str) -> List[Dict]:
    """Filter modules based on care tier.
    
    Some modules only apply to certain tiers:
    - base_care_cost: All tiers
    - care_hours: in_home only
    - facility_selection: assisted_living, memory_care
    - additional_services: All tiers
    - veteran_benefits: All tiers
    - insurance_medicare: All tiers
    
    Args:
        modules: All discovered modules
        tier: Care tier from recommendation
    
    Returns:
        List of modules appropriate for this tier
    """
    unlocked = []
    
    for module in modules:
        module_id = module.get("id", "")
        
        # care_hours only for in-home care
        if module_id == "care_hours" and tier != "in_home":
            continue
        
        # facility_selection only for facility-based care
        if module_id == "facility_selection" and tier in ["independent", "in_home"]:
            continue
        
        # All others unlocked
        unlocked.append(module)
    
    return unlocked


def _on_all_modules_complete():
    """Callback when all modules complete - aggregate and publish to MCIP."""
    
    from products.cost_planner_v2.aggregator import aggregate_and_publish
    
    # Aggregate module outputs into FinancialProfile
    aggregate_and_publish()
    
    # Show completion screen
    _render_completion_screen()


def _render_completion_screen():
    """Show completion screen with financial summary."""
    
    financial = MCIP.get_financial_profile()
    
    if not financial:
        st.error("❌ Unable to load financial profile")
        return
    
    st.success("✅ **Your Financial Plan is Complete!**")
    
    st.markdown("---")
    
    # Show cost breakdown
    st.markdown("### 💰 Monthly Cost Summary")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.metric("Base Care Cost", f"${financial.base_care_cost:,.0f}")
        st.metric("Additional Services", f"${financial.additional_services:,.0f}")
        st.metric("**Total Monthly Cost**", f"**${financial.total_monthly_cost:,.0f}**")
    
    with col2:
        st.metric("Funding Available", f"${sum(financial.funding_sources.values()):,.0f}")
        
        gap = financial.funding_gap
        if gap > 0:
            st.metric("Funding Gap", f"${gap:,.0f}", delta=f"-${gap:,.0f}", delta_color="inverse")
        else:
            st.metric("Surplus", f"${abs(gap):,.0f}", delta=f"+${abs(gap):,.0f}")
    
    st.markdown("---")
    
    # Show projections
    st.markdown("### 📊 Long-Term Projections")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Year 1", f"${financial.annual_cost:,.0f}")
    
    with col2:
        st.metric("3 Years", f"${financial.three_year_projection:,.0f}")
    
    with col3:
        st.metric("5 Years", f"${financial.five_year_projection:,.0f}")
    
    st.markdown("---")
    
    # Next steps
    st.markdown("### 🚀 Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📞 Schedule Advisor Call", type="primary", use_container_width=True):
            from core.nav import route_to
            route_to("pfma")
    
    with col2:
        if st.button("🏠 Return to Hub", use_container_width=True):
            from core.nav import route_to
            route_to("hub_concierge")
```

**Key Points:**
- ✅ Receives `recommendation` from MCIP (no direct state access)
- ✅ Filters modules based on care tier
- ✅ Shows care context at top (tier, confidence)
- ✅ Publishes FinancialProfile to MCIP when complete
- ✅ Clean completion screen with next steps

---

### Step 3: Aggregator (Critical Integration Point)

**File:** `products/cost_planner_v2/aggregator.py`

```python
"""Aggregate module outputs into FinancialProfile for MCIP."""

import streamlit as st
from datetime import datetime
from core.mcip import MCIP, FinancialProfile


def aggregate_and_publish():
    """Aggregate all module outputs and publish to MCIP."""
    
    # Get module states
    state = st.session_state.get("cost_planner_v2", {})
    
    # Get care tier from MCIP
    recommendation = MCIP.get_care_recommendation()
    if not recommendation:
        st.error("❌ Cannot aggregate - no care recommendation")
        return
    
    # Extract costs from module outputs
    base_care = state.get("base_care_cost", {}).get("outcome", {})
    care_hours = state.get("care_hours", {}).get("outcome", {})
    additional = state.get("additional_services", {}).get("outcome", {})
    veteran = state.get("veteran_benefits", {}).get("outcome", {})
    insurance = state.get("insurance_medicare", {}).get("outcome", {})
    facility = state.get("facility_selection", {}).get("outcome", {})
    
    # Calculate totals
    base_cost = base_care.get("monthly_cost", 0.0)
    hours_cost = care_hours.get("monthly_cost", 0.0)
    additional_cost = additional.get("total_cost", 0.0)
    
    total_monthly = base_cost + hours_cost + additional_cost
    
    # Build funding sources
    funding_sources = {
        "personal_savings": insurance.get("personal_contribution", 0.0),
        "family_contribution": insurance.get("family_contribution", 0.0),
        "veteran_benefits": veteran.get("monthly_benefit", 0.0),
        "insurance": insurance.get("insurance_coverage", 0.0),
        "medicare": insurance.get("medicare_coverage", 0.0),
        "medicaid": insurance.get("medicaid_coverage", 0.0)
    }
    
    total_funding = sum(funding_sources.values())
    funding_gap = total_monthly - total_funding
    
    # Calculate projections (with 3% inflation)
    annual_cost = total_monthly * 12
    three_year = annual_cost * 3 * 1.03  # Simple inflation
    five_year = annual_cost * 5 * 1.05
    
    # Build FinancialProfile
    financial_profile = FinancialProfile(
        base_care_cost=base_cost + hours_cost,
        additional_services=additional_cost,
        total_monthly_cost=total_monthly,
        annual_cost=annual_cost,
        three_year_projection=three_year,
        five_year_projection=five_year,
        funding_sources=funding_sources,
        funding_gap=funding_gap,
        care_tier=recommendation.tier,
        region=base_care.get("region", "unknown"),
        facility_type=facility.get("facility_type", "standard"),
        generated_at=datetime.utcnow().isoformat() + "Z",
        version="2.0.0",
        input_snapshot_id=_generate_snapshot_id(),
        status="complete",
        last_updated=datetime.utcnow().isoformat() + "Z",
        needs_refresh=False
    )
    
    # Publish to MCIP
    MCIP.publish_financial_profile(financial_profile)
    MCIP.mark_product_complete("cost_planner")
    
    st.success("✅ Financial profile published to care intelligence system")


def _generate_snapshot_id() -> str:
    """Generate unique snapshot ID."""
    user_id = st.session_state.get("user_id", "anon")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"cost_v2_{user_id}_{timestamp}"
```

**Key Points:**
- ✅ Reads care tier from MCIP (not from gcp state)
- ✅ Aggregates module outputs into FinancialProfile
- ✅ Publishes to MCIP (single source of truth)
- ✅ Marks product complete in journey

---

## Critical Integration Points

### 1. **GCP Gate** (Most Important)
- **ALWAYS** check `MCIP.get_care_recommendation()` before showing content
- **NEVER** read from `st.session_state["gcp"]` directly
- Show friendly message if missing

### 2. **Tier-Based Filtering**
- Use `recommendation.tier` to unlock appropriate modules
- In-home care → show care_hours module
- Facility care → show facility_selection module

### 3. **Context Display**
- Show care tier + confidence at top of hub
- User sees connection between GCP and Cost Planner
- Builds trust in recommendation

### 4. **Publishing to MCIP**
- Aggregate all module outputs
- Build complete FinancialProfile
- Publish once (track with session state flag)
- Fire event for hubs to refresh

### 5. **Error Handling**
- If MCIP.get_care_recommendation() returns None → Show gate
- If aggregation fails → Show error, don't publish partial data
- If publishing fails → Log error, show retry option

---

## Testing Strategy

### Unit Tests
- `test_gcp_gate()` - Verify gate shows when recommendation missing
- `test_tier_filtering()` - Verify correct modules shown for each tier
- `test_aggregation()` - Verify financial calculations correct
- `test_publishing()` - Verify FinancialProfile structure

### Integration Tests
- `test_gcp_to_cost_flow()` - Complete GCP, verify Cost Planner unlocked
- `test_tier_propagation()` - GCP tier matches Cost Planner tier
- `test_complete_journey()` - GCP → Cost Planner → PFMA

### Manual Testing
1. Start with fresh session
2. Try to access Cost Planner → Should show gate
3. Complete GCP v4 → Recommendation published to MCIP
4. Access Cost Planner → Should show hub with modules
5. Complete modules → Financial profile published to MCIP
6. Check MCIP state → Should have both recommendation and financial

---

## Success Metrics

✅ **Clean Boundaries**: Cost Planner never reads gcp state directly  
✅ **Seamless Handoff**: User flows from GCP → Cost Planner without friction  
✅ **Context Preservation**: Care tier propagates correctly  
✅ **Single Source of Truth**: All data flows through MCIP  
✅ **Event-Driven Updates**: Hubs refresh automatically when products complete  

---

## Next Steps

1. ✅ **Implement product.py with GCP gate**
2. ✅ **Implement hub.py with tier-based filtering**
3. ✅ **Implement aggregator.py for MCIP publishing**
4. ⏳ **Create 6 financial modules** (simplified versions)
5. ⏳ **Register cost_v2 route in nav.json**
6. ⏳ **Test GCP → MCIP → Cost Planner flow**

---

**The magic happens in the handoff.** GCP publishes, MCIP stores, Cost Planner reads. Clean, orchestrated, beautiful. 🎯
