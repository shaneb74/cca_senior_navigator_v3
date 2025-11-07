# GCP & Cost Planner Refactor: Implementation Plan

## Executive Summary

**Approach**: Incremental refactor using adapters and facades to minimize disruption while achieving architecture goals.

**Duration**: 4-6 weeks (vs 8-12 weeks for big-bang rewrite)

**Risk Level**: LOW (vs HIGH for complete rewrite)

---

## Phase 1: Foundation (Week 1)

### 1.1 Extend MCIP Contracts ✅ (Already Exists)

**Current State**: 
- `CareRecommendation` dataclass exists in `core/mcip.py`
- `FinancialProfile` dataclass exists in `core/mcip.py`

**Action**: Document missing fields and add them:

```python
@dataclass
class CareRecommendation:
    # ... existing fields ...
    
    # Add missing documented fields:
    badls: list[str] = field(default_factory=list)
    iadls: list[str] = field(default_factory=list)
    cognition_level: int = 0  # 0=none, 1=mild, 2=moderate, 3=severe
    behaviors: list[str] = field(default_factory=list)
    hours_user_band: Optional[str] = None
    hours_llm_band: Optional[str] = None
    hours_calculated: Optional[float] = None
    risky_behaviors: bool = False
    spouse_or_partner_present: bool = False
```

**Files to update**:
- `core/mcip.py` (add fields)
- `products/gcp_v4/modules/care_recommendation/logic.py` (update publishing)

---

### 1.2 Create State Manager Facade

**Purpose**: Wrap session state access with typed interface

```python
# core/state_managers.py

from dataclasses import dataclass
from typing import Optional
import streamlit as st


@dataclass
class GCPState:
    """Typed accessor for GCP session state."""
    
    @classmethod
    def get_published_tier(cls) -> Optional[str]:
        """Get final published care tier."""
        return st.session_state.get("gcp", {}).get("published_tier")
    
    @classmethod
    def get_allowed_tiers(cls) -> list[str]:
        """Get allowed tiers after gates applied."""
        return st.session_state.get("gcp", {}).get("allowed_tiers", [])
    
    @classmethod
    def get_hours_band(cls) -> Optional[str]:
        """Get recommended hours band."""
        return st.session_state.get("gcp", {}).get("hours_llm")
    
    @classmethod
    def set_summary_ready(cls, ready: bool) -> None:
        """Mark GCP summary as ready for display."""
        st.session_state.setdefault("gcp", {})["summary_ready"] = ready
    
    # ... etc for all accessors


@dataclass
class CostPlannerState:
    """Typed accessor for Cost Planner session state."""
    
    @classmethod
    def get_selected_assessment(cls) -> Optional[str]:
        """Get currently selected care tier for cost estimate."""
        return st.session_state.get("cost", {}).get("selected_assessment")
    
    @classmethod
    def get_zip_code(cls) -> Optional[str]:
        """Get ZIP code for regional pricing."""
        return st.session_state.get("cost", {}).get("inputs", {}).get("zip")
    
    # ... etc
```

**Files to create**:
- `core/state_managers.py`

**Files to update** (gradually):
- Replace direct `st.session_state["gcp"]` with `GCPState.get_*()`
- Start with high-traffic files first (product.py, logic.py)

---

## Phase 2: Service Layer (Week 2-3)

### 2.1 Create GCP Service

**Purpose**: Encapsulate scoring, LLM adjudication, and publishing logic

```python
# products/gcp_v4/services/gcp_service.py

from dataclasses import asdict
from typing import Any, Optional
from core.mcip import MCIP, CareRecommendation
from core.state_managers import GCPState
import streamlit as st


class GCPService:
    """Business logic for Guided Care Plan assessment.
    
    Responsibilities:
    - Load module.json configuration
    - Calculate deterministic tier from answers
    - Request LLM adjudication (if enabled)
    - Apply behavior gates
    - Publish final CareRecommendation to MCIP
    - Emit events for downstream consumers
    """
    
    def __init__(self, module_config: dict):
        """Initialize with module configuration.
        
        Args:
            module_config: Parsed module.json
        """
        self.config = module_config
    
    def calculate_deterministic_tier(
        self, 
        answers: dict[str, Any]
    ) -> tuple[str, float, dict]:
        """Calculate tier using only module.json scores.
        
        Args:
            answers: User answers with option IDs
            
        Returns:
            (tier, score, metadata)
        """
        # Delegate to existing logic.py (refactor internals later)
        from products.gcp_v4.modules.care_recommendation.logic import (
            derive_outcome
        )
        outcome = derive_outcome(answers, config=self.config)
        return (
            outcome.get("recommended_tier"),
            outcome.get("total_score", 0),
            outcome
        )
    
    def request_llm_adjudication(
        self,
        answers: dict[str, Any],
        deterministic_tier: str,
        allowed_tiers: list[str]
    ) -> Optional[tuple[str, float]]:
        """Request LLM tier suggestion (if enabled).
        
        Args:
            answers: User answers
            deterministic_tier: Fallback tier
            allowed_tiers: Tiers allowed after gates
            
        Returns:
            (llm_tier, confidence) or None if disabled/timeout
        """
        from ai.gcp_navi_engine import get_llm_tier_suggestion
        from products.gcp_v4.modules.care_recommendation.logic import (
            get_llm_tier_mode
        )
        
        mode = get_llm_tier_mode()
        if mode == "off":
            return None
        
        try:
            llm_tier, conf = get_llm_tier_suggestion(
                answers, 
                deterministic_tier,
                allowed_tiers
            )
            return (llm_tier, conf)
        except Exception as e:
            print(f"[GCP_SERVICE] LLM adjudication failed: {e}")
            return None
    
    def publish_recommendation(
        self,
        final_tier: str,
        answers: dict[str, Any],
        metadata: dict[str, Any]
    ) -> CareRecommendation:
        """Publish final recommendation to MCIP.
        
        Args:
            final_tier: Chosen tier
            answers: All user answers
            metadata: Additional context (scores, flags, etc.)
            
        Returns:
            Published CareRecommendation
        """
        from datetime import datetime
        from products.gcp_v4.modules.care_recommendation.flags import (
            build_flags
        )
        
        # Build flags from answers
        flags = build_flags(answers)
        
        # Create recommendation
        rec = CareRecommendation(
            tier=final_tier,
            tier_score=metadata.get("total_score", 0),
            tier_rankings=metadata.get("tier_rankings", []),
            confidence=metadata.get("confidence", 0.0),
            flags=[asdict(f) for f in flags],
            rationale=metadata.get("rationale", []),
            generated_at=datetime.utcnow().isoformat() + "Z",
            version="4.0",
            input_snapshot_id=metadata.get("snapshot_id", ""),
            rule_set=metadata.get("rule_set", "standard"),
            next_step={"product": "cost_planner", "label": "Estimate Costs"},
            status="complete",
            last_updated=datetime.utcnow().isoformat() + "Z",
            needs_refresh=False,
            allowed_tiers=metadata.get("allowed_tiers", []),
            # Extended fields
            badls=metadata.get("badls", []),
            iadls=metadata.get("iadls", []),
            cognition_level=metadata.get("cognition_level", 0),
            behaviors=metadata.get("behaviors", []),
            hours_user_band=metadata.get("hours_user_band"),
            hours_llm_band=metadata.get("hours_llm_band"),
            hours_calculated=metadata.get("hours_calculated"),
            risky_behaviors=metadata.get("risky_behaviors", False),
            spouse_or_partner_present=metadata.get("spouse_or_partner_present", False)
        )
        
        # Publish to MCIP
        MCIP.publish_care_recommendation(rec)
        
        # Also update GCP session state (backward compat)
        GCPState.set_published_tier(final_tier)
        GCPState.set_allowed_tiers(metadata.get("allowed_tiers", []))
        GCPState.set_summary_ready(True)
        
        # Emit completion event
        self._emit_event("gcp.careplan.ready", {
            "tier": final_tier,
            "confidence": rec.confidence
        })
        
        return rec
    
    def _emit_event(self, event_name: str, payload: dict) -> None:
        """Emit event for downstream consumers.
        
        Args:
            event_name: Event identifier
            payload: Event data
        """
        from core.events import log_event
        log_event(event_name, payload)
```

**Files to create**:
- `products/gcp_v4/services/__init__.py`
- `products/gcp_v4/services/gcp_service.py`

**Files to update**:
- `products/gcp_v4/product.py` - Use GCPService in results step

---

### 2.2 Create Cost Planner Service

**Purpose**: Encapsulate financial calculations and publishing

```python
# products/cost_planner_v2/services/cost_service.py

from dataclasses import asdict
from typing import Any
from core.mcip import MCIP, FinancialProfile
from core.state_managers import CostPlannerState
from datetime import datetime


class CostPlannerService:
    """Business logic for Cost Planner financial assessments.
    
    Responsibilities:
    - Load assessment JSON configurations
    - Calculate monthly costs by tier
    - Compute coverage gaps
    - Publish FinancialProfile to MCIP
    - Emit events for downstream consumers
    """
    
    def __init__(self):
        """Initialize service."""
        pass
    
    def calculate_monthly_cost(
        self,
        tier: str,
        zip_code: str,
        hours: Optional[float] = None,
        **modifiers
    ) -> dict[str, Any]:
        """Calculate monthly cost for given tier and modifiers.
        
        Args:
            tier: Care tier (assisted_living, memory_care, etc.)
            zip_code: ZIP for regional pricing
            hours: Daily hours (for in-home care)
            **modifiers: Additional cost adjustments
            
        Returns:
            Dict with totals, segments, breakdown
        """
        # Delegate to existing utils (refactor internals later)
        from products.cost_planner_v2.utils.cost_calculator import (
            calculate_costs
        )
        return calculate_costs(tier, zip_code, hours, **modifiers)
    
    def publish_financial_profile(
        self,
        monthly_cost: float,
        coverage: dict[str, float],
        confidence: float
    ) -> FinancialProfile:
        """Publish financial profile to MCIP.
        
        Args:
            monthly_cost: Estimated monthly cost
            coverage: Coverage breakdown (income, assets, etc.)
            confidence: Confidence in estimate (0-1)
            
        Returns:
            Published FinancialProfile
        """
        # Calculate gap
        total_coverage = sum(coverage.values())
        gap = max(0, monthly_cost - total_coverage)
        
        # Calculate runway (months until depletion)
        liquid_assets = coverage.get("assets", 0)
        runway = int(liquid_assets / gap) if gap > 0 else 999
        
        # Create profile
        profile = FinancialProfile(
            estimated_monthly_cost=monthly_cost,
            coverage_percentage=(total_coverage / monthly_cost * 100) if monthly_cost > 0 else 0,
            gap_amount=gap,
            runway_months=runway,
            confidence=confidence,
            generated_at=datetime.utcnow().isoformat() + "Z",
            status="complete"
        )
        
        # Publish to MCIP
        MCIP.publish_financial_profile(profile)
        
        # Update Cost Planner session state (backward compat)
        CostPlannerState.set_completed(True)
        
        # Emit completion event
        self._emit_event("cost.financial_profile.ready", {
            "monthly_cost": monthly_cost,
            "confidence": confidence
        })
        
        return profile
    
    def _emit_event(self, event_name: str, payload: dict) -> None:
        """Emit event for downstream consumers."""
        from core.events import log_event
        log_event(event_name, payload)
```

**Files to create**:
- `products/cost_planner_v2/services/__init__.py`
- `products/cost_planner_v2/services/cost_service.py`

---

## Phase 3: Gradual Migration (Week 4-5)

### 3.1 Update GCP Product to Use Service

**Current**:
```python
# products/gcp_v4/product.py (results step)
from products.gcp_v4.modules.care_recommendation.logic import derive_outcome
outcome = derive_outcome(answers)
# ... manually publish to MCIP ...
```

**After**:
```python
# products/gcp_v4/product.py (results step)
from products.gcp_v4.services.gcp_service import GCPService

service = GCPService(module_config)
det_tier, score, metadata = service.calculate_deterministic_tier(answers)
llm_result = service.request_llm_adjudication(answers, det_tier, allowed_tiers)
final_tier = llm_result[0] if llm_result else det_tier
recommendation = service.publish_recommendation(final_tier, answers, metadata)
```

**Files to update**:
- `products/gcp_v4/product.py`

---

### 3.2 Update Cost Planner to Use Service

**Current**:
```python
# products/cost_planner_v2/quick_estimate.py
from products.cost_planner_v2.utils.cost_calculator import calculate_costs
totals = calculate_costs(...)
# ... manually update session state ...
```

**After**:
```python
# products/cost_planner_v2/quick_estimate.py
from products.cost_planner_v2.services.cost_service import CostPlannerService

service = CostPlannerService()
cost_data = service.calculate_monthly_cost(tier, zip_code, hours)
profile = service.publish_financial_profile(cost_data['monthly'], coverage, 0.85)
```

**Files to update**:
- `products/cost_planner_v2/quick_estimate.py`
- `products/cost_planner_v2/expert_review.py`

---

## Phase 4: Testing & Documentation (Week 6)

### 4.1 Unit Tests

Create pure Python tests for services (no Streamlit required):

```python
# tests/test_gcp_service.py

def test_calculate_deterministic_tier():
    """Test deterministic tier calculation."""
    service = GCPService(mock_config)
    answers = {
        "adl_bathing": "needs_help",
        "adl_dressing": "needs_help",
        # ...
    }
    tier, score, meta = service.calculate_deterministic_tier(answers)
    assert tier == "assisted_living"
    assert score > 30

def test_publish_recommendation():
    """Test recommendation publishing."""
    service = GCPService(mock_config)
    rec = service.publish_recommendation("assisted_living", answers, metadata)
    assert rec.tier == "assisted_living"
    assert rec.schema_version == 2
```

**Files to create**:
- `tests/test_gcp_service.py`
- `tests/test_cost_service.py`
- `tests/test_state_managers.py`

---

### 4.2 Update Documentation

**Files to update**:
- `docs/GCP_ARCHITECTURE.md` (create new)
- `docs/COST_PLANNER_ARCHITECTURE.md` (create new)
- Update copilot instructions with new patterns

---

## Phase 5: Cleanup (Ongoing)

### 5.1 Deprecate Direct Session State Access

Gradually replace:
- `st.session_state["gcp"]` → `GCPState.get_*()`
- `st.session_state["cost"]` → `CostPlannerState.get_*()`

Track with grep:
```bash
# Find remaining direct accesses
grep -r 'session_state\["gcp"\]' products/
grep -r 'session_state\["cost"\]' products/
```

---

### 5.2 Refactor Logic.py Internals

Once GCPService is stable, refactor `logic.py` internals:
- Extract scoring functions
- Simplify LLM adjudication logic
- Remove Streamlit dependencies

**Keep for later** - not critical for initial refactor.

---

## Success Metrics

✅ **Phase 1 Complete When**:
- State managers created and tested
- 10+ direct session state accesses replaced

✅ **Phase 2 Complete When**:
- Both services created and integrated
- All publishing goes through services

✅ **Phase 3 Complete When**:
- Main product flows use services
- Old code paths deprecated

✅ **Phase 4 Complete When**:
- Unit test coverage >70%
- Documentation updated

✅ **Phase 5 Complete When**:
- <10 direct session state accesses remain
- All critical paths use typed interfaces

---

## Risk Mitigation

### Parallel Operation
- Services wrap existing logic initially
- Old code paths stay functional
- Can roll back any phase independently

### Incremental Testing
- Test each phase in isolation
- Feature flags for new vs old paths
- Gradual rollout to users

### Backward Compatibility
- Services maintain session state for consumers
- MCIP contracts remain stable
- No breaking changes to downstream code

---

## Comparison: Big-Bang vs Incremental

| Aspect | Big-Bang Rewrite | **Incremental (Recommended)** |
|--------|-----------------|------------------------------|
| Duration | 8-12 weeks | 4-6 weeks |
| Risk | HIGH | LOW |
| Testing | End only | Each phase |
| Rollback | Difficult | Easy |
| User Impact | All at once | Gradual |
| Code Review | Massive PR | Small PRs |
| Learning Curve | Steep | Gradual |

---

## Next Steps

1. **Review this plan** - Confirm approach with team
2. **Create branch** - Already done ✅ (`feature/refactor-gcp-cost-planner`)
3. **Start Phase 1** - Extend MCIP contracts + create state managers
4. **Commit frequently** - Small, reviewable PRs
5. **Test continuously** - Unit tests + manual verification

---

## Questions for Decision

1. **Event System**: Use existing `core.events` or create dedicated event bus?
   - **Recommendation**: Use existing - simpler, already integrated

2. **State Manager**: Class methods vs module functions?
   - **Recommendation**: Class methods - easier to test and extend

3. **Service Location**: `products/{product}/services/` or `core/services/`?
   - **Recommendation**: Product-specific - better encapsulation

4. **Migration Speed**: Aggressive (2 weeks) vs Conservative (6 weeks)?
   - **Recommendation**: Conservative - lower risk, better quality
