# MCIP v2 Integration Specification

> **The Wizard Behind the Curtain**  
> MCIP (Master Care Intelligence Panel) is the conductor that sees all hubs, publishes care recommendations, and orchestrates the user journey—while maintaining clean boundaries between hubs, products, and modules.

---

## Executive Summary

**MCIP v2 is an event-driven integration layer** that:
1. **Sees all hubs** - Understands complete user state across the application
2. **Publishes recommendations** - Single source of truth for care tier, confidence, flags
3. **Fires events** - Notifies hubs when recommendations change
4. **Maintains boundaries** - Hubs never read product state; products never read module state

**Core Principle**: MCIP is the **only system** that reads across boundaries. Everyone else stays in their lane.

---

## System Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                         MCIP v2                              │
│                    (The Conductor)                           │
│  • Sees all hubs, products, and outcomes                    │
│  • Publishes care_recommendation to session state           │
│  • Fires events when recommendations change                 │
│  • Decides hub visibility and product unlocking             │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼─────┐         ┌────▼─────┐         ┌────▼─────┐
   │Concierge │         │ Learning │         │ Partners │
   │   Hub    │         │   Hub    │         │   Hub    │
   └────┬─────┘         └──────────┘         └──────────┘
        │
   ┌────┴────┬──────────┬──────────┐
   │         │          │          │
┌──▼──┐  ┌──▼──┐    ┌──▼──┐    ┌──▼──┐
│ GCP │  │Cost │    │PFMA │    │ ... │
│     │  │Plan │    │     │    │     │
└──┬──┘  └──┬──┘    └──┬──┘    └─────┘
   │        │           │
   │        │(internal  │
   │        │  hub)     │
   │        │           │
Modules   Modules    Steps
```

### Responsibility Matrix

| Layer | Sees | Publishes To | Reads From | Example |
|-------|------|--------------|------------|---------|
| **MCIP** | All hubs, products, outcomes | `st.session_state["mcip"]` | All product states | "GCP complete, unlock Cost Planner" |
| **Hub** | Own product tiles | Hub-level state | `st.session_state["mcip"]` only | Concierge Hub shows GCP tile |
| **Product** | Own modules | MCIP via contract | `st.session_state["mcip"]` only | GCP controls care_recommendation |
| **Module** | Own questions | Parent product | Parent product state only | care_recommendation asks ADL questions |

**Golden Rule**: Information flows **up** (module → product → MCIP) and **down** (MCIP → hub → product). Never **sideways** (product ↔ product).

---

## 1. MCIP State Contract

### 1.1 State Structure

```python
# Single source of truth: st.session_state["mcip"]
st.session_state["mcip"] = {
    "care_recommendation": {
        # Primary recommendation
        "tier": "assisted_living",           # independent | in_home | assisted_living | memory_care
        "tier_score": 72.5,                  # 0-100 confidence score
        "tier_rankings": [                   # All tiers ranked
            ("assisted_living", 72.5),
            ("in_home", 58.3),
            ("memory_care", 45.0),
            ("independent", 12.8)
        ],
        "confidence": 0.92,                  # 0.0-1.0 (percent of required questions answered)
        
        # Flags and drivers
        "flags": [
            {
                "id": "falls_risk",
                "label": "High Fall Risk",
                "description": "Recent falls or mobility challenges detected",
                "tone": "warning",           # info | warning | critical
                "priority": 1,               # Lower = higher priority
                "cta": {
                    "label": "See Safety Resources",
                    "route": "learning",
                    "filter": "fall_prevention"
                }
            },
            {
                "id": "memory_support",
                "label": "Memory Care Needed",
                "description": "Alzheimer's or dementia diagnosis present",
                "tone": "critical",
                "priority": 0,
                "cta": {
                    "label": "Find Memory Care Facilities",
                    "route": "partners",
                    "filter": "memory_care"
                }
            }
        ],
        
        "rationale": [
            "Needs help with bathing and dressing daily",
            "2+ falls in the past year",
            "Early-stage Alzheimer's diagnosis",
            "Lives alone without 24/7 supervision"
        ],
        
        # Provenance (for tracking and audit)
        "generated_at": "2025-10-13T14:32:18Z",
        "version": "4.0.0",                  # GCP scoring rules version
        "input_snapshot_id": "user_abc_2025_10_13_14_32",
        "rule_set": "standard_2025_q4",
        
        # Routing
        "next_step": {
            "product": "cost_planner",
            "route": "cost",
            "label": "See Cost Estimate",
            "reason": "Calculate financial impact of assisted living"
        },
        
        # Status
        "status": "complete",                # new | in_progress | complete | needs_update
        "last_updated": "2025-10-13T14:32:18Z",
        "needs_refresh": False               # Set to True when inputs change
    },
    
    "financial_profile": {
        # Cost Planner publishes this
        "estimated_monthly_cost": 5200,
        "coverage_percentage": 68,
        "gap_amount": 1664,
        "runway_months": 36,
        "confidence": 0.85,
        "generated_at": "2025-10-13T15:10:42Z",
        "status": "complete"
    },
    
    "advisor_appointment": {
        # PFMA publishes this
        "scheduled": True,
        "date": "2025-10-20",
        "time": "10:00 AM",
        "type": "phone",
        "confirmation_id": "PFMA-2025-12345",
        "generated_at": "2025-10-13T15:45:00Z",
        "status": "confirmed"
    },
    
    # Hub visibility and product unlocking
    "journey": {
        "current_hub": "concierge",
        "completed_products": ["gcp"],
        "unlocked_products": ["cost_planner", "pfma"],
        "recommended_next": "cost_planner"
    },
    
    # Event history (optional, for debugging)
    "events": [
        {
            "type": "mcip.recommendation.updated",
            "timestamp": "2025-10-13T14:32:18Z",
            "payload": {"tier": "assisted_living", "confidence": 0.92}
        },
        {
            "type": "mcip.flags.updated",
            "timestamp": "2025-10-13T14:32:18Z",
            "payload": {"flags": ["falls_risk", "memory_support"]}
        }
    ]
}
```

### 1.2 MCIP Helper Functions

```python
# core/mcip.py

from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
import streamlit as st


@dataclass
class CareRecommendation:
    """Standardized care recommendation contract."""
    tier: str
    tier_score: float
    tier_rankings: List[tuple]
    confidence: float
    flags: List[Dict[str, Any]]
    rationale: List[str]
    generated_at: str
    version: str
    input_snapshot_id: str
    rule_set: str
    next_step: Dict[str, str]
    status: str
    last_updated: str
    needs_refresh: bool


@dataclass
class FinancialProfile:
    """Standardized financial profile contract."""
    estimated_monthly_cost: float
    coverage_percentage: float
    gap_amount: float
    runway_months: int
    confidence: float
    generated_at: str
    status: str


class MCIP:
    """Master Care Intelligence Panel - The Conductor."""
    
    STATE_KEY = "mcip"
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize MCIP state structure."""
        if cls.STATE_KEY not in st.session_state:
            st.session_state[cls.STATE_KEY] = {
                "care_recommendation": cls._default_care_recommendation(),
                "financial_profile": None,
                "advisor_appointment": None,
                "journey": {
                    "current_hub": "concierge",
                    "completed_products": [],
                    "unlocked_products": ["gcp"],
                    "recommended_next": "gcp"
                },
                "events": []
            }
    
    @classmethod
    def get_care_recommendation(cls) -> Optional[CareRecommendation]:
        """Get the current care recommendation.
        
        Returns:
            CareRecommendation object or None if not generated
        """
        cls.initialize()
        rec_data = st.session_state[cls.STATE_KEY].get("care_recommendation")
        
        if rec_data and rec_data.get("status") != "new":
            return CareRecommendation(**rec_data)
        return None
    
    @classmethod
    def publish_care_recommendation(cls, recommendation: CareRecommendation) -> None:
        """Publish a new care recommendation (called by GCP).
        
        Args:
            recommendation: CareRecommendation object
        """
        cls.initialize()
        
        # Store recommendation
        st.session_state[cls.STATE_KEY]["care_recommendation"] = asdict(recommendation)
        
        # Fire event
        cls._fire_event("mcip.recommendation.updated", {
            "tier": recommendation.tier,
            "confidence": recommendation.confidence,
            "generated_at": recommendation.generated_at
        })
        
        # Update journey
        cls._update_journey_after_recommendation(recommendation)
        
        # Refresh MCIP panels
        cls.refresh_panels()
    
    @classmethod
    def publish_financial_profile(cls, profile: FinancialProfile) -> None:
        """Publish financial profile (called by Cost Planner).
        
        Args:
            profile: FinancialProfile object
        """
        cls.initialize()
        st.session_state[cls.STATE_KEY]["financial_profile"] = asdict(profile)
        
        cls._fire_event("mcip.financial.updated", {
            "monthly_cost": profile.estimated_monthly_cost,
            "confidence": profile.confidence
        })
    
    @classmethod
    def publish_appointment(cls, appointment_data: Dict[str, Any]) -> None:
        """Publish advisor appointment (called by PFMA).
        
        Args:
            appointment_data: Appointment details
        """
        cls.initialize()
        st.session_state[cls.STATE_KEY]["advisor_appointment"] = appointment_data
        
        cls._fire_event("mcip.appointment.scheduled", {
            "date": appointment_data.get("date"),
            "type": appointment_data.get("type")
        })
    
    @classmethod
    def get_unlocked_products(cls) -> List[str]:
        """Get list of products user can access.
        
        Returns:
            List of product keys
        """
        cls.initialize()
        return st.session_state[cls.STATE_KEY]["journey"]["unlocked_products"]
    
    @classmethod
    def is_product_unlocked(cls, product_key: str) -> bool:
        """Check if a product is unlocked.
        
        Args:
            product_key: Product identifier (e.g., "cost_planner")
        
        Returns:
            True if unlocked, False otherwise
        """
        return product_key in cls.get_unlocked_products()
    
    @classmethod
    def mark_product_complete(cls, product_key: str) -> None:
        """Mark a product as completed.
        
        Args:
            product_key: Product identifier
        """
        cls.initialize()
        journey = st.session_state[cls.STATE_KEY]["journey"]
        
        if product_key not in journey["completed_products"]:
            journey["completed_products"].append(product_key)
        
        cls._fire_event("mcip.product.completed", {"product": product_key})
    
    @classmethod
    def get_recommended_next_product(cls) -> Optional[str]:
        """Get MCIP's recommended next product.
        
        Returns:
            Product key or None
        """
        cls.initialize()
        return st.session_state[cls.STATE_KEY]["journey"].get("recommended_next")
    
    @classmethod
    def refresh_panels(cls) -> None:
        """Clear cached MCIP panel markup to force re-render."""
        # Clear any cached components
        if "_mcip_panel_cache" in st.session_state:
            del st.session_state["_mcip_panel_cache"]
        
        if "_hub_guide_cache" in st.session_state:
            del st.session_state["_hub_guide_cache"]
    
    @classmethod
    def _fire_event(cls, event_type: str, payload: Dict[str, Any]) -> None:
        """Fire an MCIP event.
        
        Args:
            event_type: Event identifier (e.g., "mcip.recommendation.updated")
            payload: Event data
        """
        cls.initialize()
        
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload
        }
        
        st.session_state[cls.STATE_KEY]["events"].append(event)
        
        # Optional: Emit to analytics
        from core.events import log_event
        log_event(event_type, payload)
    
    @classmethod
    def _update_journey_after_recommendation(cls, recommendation: CareRecommendation) -> None:
        """Update journey state after new recommendation.
        
        Args:
            recommendation: CareRecommendation object
        """
        journey = st.session_state[cls.STATE_KEY]["journey"]
        
        # Mark GCP as complete
        if "gcp" not in journey["completed_products"]:
            journey["completed_products"].append("gcp")
        
        # Unlock next products
        journey["unlocked_products"] = ["gcp", "cost_planner", "pfma"]
        
        # Set recommended next
        journey["recommended_next"] = recommendation.next_step.get("product", "cost_planner")
    
    @classmethod
    def _default_care_recommendation(cls) -> Dict[str, Any]:
        """Default care recommendation when GCP hasn't run.
        
        Returns:
            Default recommendation dict
        """
        return {
            "tier": None,
            "tier_score": 0,
            "tier_rankings": [],
            "confidence": 0.0,
            "flags": [],
            "rationale": [],
            "generated_at": None,
            "version": None,
            "input_snapshot_id": None,
            "rule_set": None,
            "next_step": {
                "product": "gcp",
                "route": "gcp",
                "label": "Complete Guided Care Plan",
                "reason": "Get your personalized care recommendation"
            },
            "status": "new",
            "last_updated": None,
            "needs_refresh": False
        }
```

---

## 2. Event System

### 2.1 Event Types

| Event | Fired By | Consumed By | Payload | Purpose |
|-------|----------|-------------|---------|---------|
| `mcip.recommendation.updated` | GCP | Hub tiles, guide panels | `{tier, confidence, generated_at}` | New care recommendation available |
| `mcip.flags.updated` | GCP | Learning Hub, Partners Hub | `{flags: [flag_ids]}` | New risk/support flags detected |
| `mcip.financial.updated` | Cost Planner | Hub tiles, advisor prep | `{monthly_cost, confidence}` | Financial profile complete |
| `mcip.appointment.scheduled` | PFMA | Advisor system, notifications | `{date, type, confirmation_id}` | Advisor appointment booked |
| `mcip.product.completed` | MCIP | Hub progress indicators | `{product}` | Product marked complete |

### 2.2 Event Listeners

```python
# core/mcip_events.py

from typing import Callable, Dict, List
import streamlit as st


class MCIPEventBus:
    """Simple event bus for MCIP event subscriptions."""
    
    _listeners: Dict[str, List[Callable]] = {}
    
    @classmethod
    def subscribe(cls, event_type: str, callback: Callable) -> None:
        """Subscribe to an MCIP event.
        
        Args:
            event_type: Event identifier
            callback: Function to call when event fires
        """
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        
        cls._listeners[event_type].append(callback)
    
    @classmethod
    def emit(cls, event_type: str, payload: Dict) -> None:
        """Emit an MCIP event to all subscribers.
        
        Args:
            event_type: Event identifier
            payload: Event data
        """
        if event_type in cls._listeners:
            for callback in cls._listeners[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    print(f"Error in event listener for {event_type}: {e}")
    
    @classmethod
    def clear(cls) -> None:
        """Clear all event listeners (for testing)."""
        cls._listeners = {}


# Example: Hub Guide subscribes to recommendation updates
def on_recommendation_updated(payload: Dict) -> None:
    """Called when care recommendation changes."""
    # Clear cached guide panel
    if "_hub_guide_cache" in st.session_state:
        del st.session_state["_hub_guide_cache"]
    
    # Log analytics
    from core.events import log_event
    log_event("mcip.recommendation.viewed", {
        "tier": payload.get("tier"),
        "confidence": payload.get("confidence")
    })


# Subscribe at app initialization
MCIPEventBus.subscribe("mcip.recommendation.updated", on_recommendation_updated)
```

---

## 3. Hub Integration

### 3.1 Hub Responsibilities

Hubs consume MCIP signals to:
- Show/hide product tiles
- Highlight recommended next product
- Display product completion status
- Apply visual gradients to recommended tiles

**Hubs NEVER**:
- Read product state directly
- Call product functions
- Know about modules

### 3.2 Hub Integration Pattern

```python
# hubs/concierge.py

from core.mcip import MCIP
from core.product_tile import ProductTile


def render_concierge_hub():
    """Render Concierge Hub with MCIP integration."""
    
    # Get MCIP recommendation
    recommendation = MCIP.get_care_recommendation()
    unlocked_products = MCIP.get_unlocked_products()
    recommended_next = MCIP.get_recommended_next_product()
    
    # Render product tiles
    products = [
        {
            "key": "gcp",
            "title": "Guided Care Plan",
            "description": "Get your personalized care recommendation",
            "icon": "🎯",
            "route": "gcp",
            "unlocked": True,  # Always unlocked
            "completed": "gcp" in MCIP.get_unlocked_products(),
            "recommended": recommended_next == "gcp"
        },
        {
            "key": "cost_planner",
            "title": "Cost Planner",
            "description": "Estimate your monthly care costs",
            "icon": "💰",
            "route": "cost",
            "unlocked": MCIP.is_product_unlocked("cost_planner"),
            "completed": "cost_planner" in unlocked_products,
            "recommended": recommended_next == "cost_planner"
        },
        {
            "key": "pfma",
            "title": "Meet Your Advisor",
            "description": "Schedule a consultation with a care expert",
            "icon": "👤",
            "route": "pfma",
            "unlocked": MCIP.is_product_unlocked("pfma"),
            "completed": "pfma" in unlocked_products,
            "recommended": recommended_next == "pfma"
        }
    ]
    
    # Render tiles in grid
    cols = st.columns(3)
    for idx, product in enumerate(products):
        with cols[idx]:
            ProductTile(
                title=product["title"],
                description=product["description"],
                icon=product["icon"],
                route=product["route"],
                unlocked=product["unlocked"],
                completed=product["completed"],
                recommended=product["recommended"]  # Silver gradient
            ).render()
    
    # Render Hub Guide (shows recommendation summary)
    if recommendation and recommendation.status == "complete":
        _render_hub_guide(recommendation)


def _render_hub_guide(recommendation):
    """Render hub guide panel with MCIP recommendation."""
    st.markdown("---")
    st.markdown("### 🎯 Your Personalized Recommendation")
    
    tier_label = recommendation.tier.replace("_", " ").title()
    st.success(f"**Recommended Care Level:** {tier_label}")
    
    # Show confidence
    st.caption(f"Confidence: {int(recommendation.confidence * 100)}%")
    
    # Show key drivers
    if recommendation.rationale:
        st.markdown("**Key Factors:**")
        for reason in recommendation.rationale[:3]:
            st.markdown(f"• {reason}")
    
    # Show flags with CTAs
    if recommendation.flags:
        st.markdown("**Important Considerations:**")
        for flag in recommendation.flags:
            tone_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}
            emoji = tone_emoji.get(flag["tone"], "ℹ️")
            
            st.markdown(f"{emoji} **{flag['label']}**: {flag['description']}")
            
            if flag.get("cta"):
                if st.button(flag["cta"]["label"], key=f"flag_{flag['id']}"):
                    from core.nav import route_to
                    route_to(flag["cta"]["route"])
```

---

## 4. Product Integration

### 4.1 Product Responsibilities

Products:
- Control their modules
- Compute outcomes from module data
- **Publish outcomes to MCIP** via contract
- Read MCIP state for context (e.g., recommended care tier)

**Products NEVER**:
- Read other product's state
- Call other product's functions
- Know about other product's modules

### 4.2 Product Integration Pattern (GCP Example)

```python
# products/gcp_v4/product.py

from core.mcip import MCIP, CareRecommendation
from products.gcp_v4.scoring import compute_care_recommendation
from datetime import datetime


def render_gcp():
    """Render Guided Care Plan product."""
    
    # Run module engine (collects user answers)
    from core.modules.engine import run_module
    
    module_state = run_module("gcp", "care_recommendation")
    
    # If module is complete, compute recommendation
    if module_state.get("status") == "complete":
        _publish_recommendation_to_mcip(module_state)


def _publish_recommendation_to_mcip(module_state: dict) -> None:
    """Compute and publish care recommendation to MCIP.
    
    Args:
        module_state: Completed module state with user answers
    """
    # Import scoring engine
    from products.gcp_v4.scoring import ScoringEngine
    
    # Compute recommendation
    engine = ScoringEngine()
    result = engine.compute(module_state["answers"])
    
    # Build CareRecommendation contract
    recommendation = CareRecommendation(
        tier=result.tier,
        tier_score=result.tier_score,
        tier_rankings=result.tier_rankings,
        confidence=result.confidence,
        flags=result.flags,
        rationale=result.rationale,
        generated_at=datetime.utcnow().isoformat() + "Z",
        version="4.0.0",
        input_snapshot_id=f"user_{st.session_state.get('user_id', 'anon')}_{datetime.utcnow().strftime('%Y%m%d_%H%M')}",
        rule_set="standard_2025_q4",
        next_step={
            "product": "cost_planner",
            "route": "cost",
            "label": "See Cost Estimate",
            "reason": f"Calculate financial impact of {result.tier.replace('_', ' ')}"
        },
        status="complete",
        last_updated=datetime.utcnow().isoformat() + "Z",
        needs_refresh=False
    )
    
    # Publish to MCIP
    MCIP.publish_care_recommendation(recommendation)
    
    # Mark product complete
    MCIP.mark_product_complete("gcp")
```

### 4.3 Product Integration Pattern (Cost Planner Example)

```python
# products/cost_planner_v2/product.py

from core.mcip import MCIP, FinancialProfile
from datetime import datetime


def render_cost_planner():
    """Render Cost Planner product."""
    
    # Check if GCP is complete (gate)
    recommendation = MCIP.get_care_recommendation()
    if not recommendation or recommendation.status != "complete":
        _render_gcp_gate()
        return
    
    # Use recommendation.tier to pre-populate cost estimates
    recommended_tier = recommendation.tier
    
    # Run module hub (financial modules)
    from products.cost_planner_v2.hub import render_module_hub
    render_module_hub(recommended_tier)
    
    # If all modules complete, publish to MCIP
    if _all_modules_complete():
        _publish_financial_profile_to_mcip()


def _publish_financial_profile_to_mcip() -> None:
    """Compute and publish financial profile to MCIP."""
    
    # Aggregate financial data from modules
    from products.cost_planner_v2.aggregator import aggregate_financial_data
    
    financial_data = aggregate_financial_data()
    
    # Build FinancialProfile contract
    profile = FinancialProfile(
        estimated_monthly_cost=financial_data["monthly_cost"],
        coverage_percentage=financial_data["coverage_pct"],
        gap_amount=financial_data["gap"],
        runway_months=financial_data["runway"],
        confidence=financial_data["confidence"],
        generated_at=datetime.utcnow().isoformat() + "Z",
        status="complete"
    )
    
    # Publish to MCIP
    MCIP.publish_financial_profile(profile)
    
    # Mark product complete
    MCIP.mark_product_complete("cost_planner")


def _render_gcp_gate():
    """Show gate when GCP is not complete."""
    st.warning("⚠️ **Guided Care Plan Required**")
    st.markdown("Please complete your Guided Care Plan first to get personalized cost estimates.")
    
    if st.button("Go to Guided Care Plan", type="primary"):
        from core.nav import route_to
        route_to("gcp")
```

---

## 5. Module Integration

### 5.1 Module Responsibilities

Modules:
- Ask questions, gather data
- Compute outcomes via `logic.py`
- Publish outcomes to **parent product only**
- Store data in product-scoped state

**Modules NEVER**:
- Read MCIP state
- Know about other modules
- Publish directly to MCIP

### 5.2 Module Integration Pattern

```python
# products/gcp_v4/modules/care_recommendation/logic.py

from typing import Dict, Any


def derive_outcome(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Compute care recommendation outcome from answers.
    
    This function ONLY knows about its own questions and answers.
    It returns structured data to the product, which handles MCIP publishing.
    
    Args:
        answers: User responses to care recommendation questions
    
    Returns:
        Outcome dict (not yet a CareRecommendation - product handles that)
    """
    # Extract answers
    adl_support = answers.get("adl_support_level")
    falls = answers.get("falls_last_year", 0)
    memory_diagnosis = answers.get("memory_diagnosis")
    lives_alone = answers.get("lives_alone", False)
    
    # Compute tier scores (simplified example)
    scores = {
        "independent": 10,
        "in_home": 10,
        "assisted_living": 10,
        "memory_care": 10
    }
    
    rationale = []
    flags = []
    
    # Apply scoring logic
    if adl_support == "daily":
        scores["assisted_living"] += 25
        scores["in_home"] += 15
        rationale.append("Needs help with daily activities")
    
    if falls >= 2:
        scores["assisted_living"] += 20
        flags.append("falls_risk")
        rationale.append("2+ falls in the past year")
    
    if memory_diagnosis in ["alzheimers", "dementia"]:
        scores["memory_care"] += 40
        scores["assisted_living"] += 20
        flags.append("memory_support")
        rationale.append("Memory care diagnosis present")
    
    if lives_alone:
        scores["assisted_living"] += 15
        rationale.append("Lives alone without 24/7 supervision")
    
    # Determine winning tier
    tier_rankings = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winning_tier = tier_rankings[0][0]
    winning_score = tier_rankings[0][1]
    
    # Compute confidence (simplified)
    required_questions = ["adl_support_level", "falls_last_year", "memory_diagnosis", "lives_alone"]
    answered = sum(1 for q in required_questions if answers.get(q) is not None)
    confidence = answered / len(required_questions)
    
    # Return outcome (NOT a CareRecommendation yet - product will build that)
    return {
        "tier": winning_tier,
        "tier_score": winning_score,
        "tier_rankings": tier_rankings,
        "confidence": confidence,
        "flags": flags,
        "rationale": rationale
    }
```

**Key Point**: The module returns raw outcome data. The **product** (not the module) builds the full `CareRecommendation` contract and publishes to MCIP.

---

## 6. Fallback Behavior

### 6.1 No Recommendation Yet

When GCP hasn't run, MCIP provides default state:

```python
# Example: Rendering when no recommendation exists
recommendation = MCIP.get_care_recommendation()

if not recommendation or recommendation.status == "new":
    st.info("📋 **Complete Your Guided Care Plan**")
    st.markdown("Get started with your personalized care recommendation.")
    
    if st.button("Start Guided Care Plan", type="primary"):
        from core.nav import route_to
        route_to("gcp")
else:
    # Show recommendation
    _render_recommendation(recommendation)
```

### 6.2 Low Confidence Handling

```python
# Example: Handling low-confidence recommendations
recommendation = MCIP.get_care_recommendation()

if recommendation and recommendation.confidence < 0.7:
    st.warning("⚠️ **We Need More Information**")
    st.markdown(
        f"Your recommendation is based on {int(recommendation.confidence * 100)}% "
        "of the required information. Please answer a few more questions for a more accurate result."
    )
    
    if st.button("Complete Guided Care Plan", type="primary"):
        from core.nav import route_to
        route_to("gcp")
```

### 6.3 Stale Recommendation

```python
# Example: Detecting stale recommendations
recommendation = MCIP.get_care_recommendation()

if recommendation and recommendation.needs_refresh:
    st.info("ℹ️ **Your Care Needs May Have Changed**")
    st.markdown("We noticed updates to your profile. Refresh your recommendation?")
    
    if st.button("Update Recommendation"):
        # Re-run GCP scoring
        from products.gcp_v4.product import recompute_recommendation
        recompute_recommendation()
```

---

## 7. Testing & QA

### 7.1 Unit Tests

```python
# tests/test_mcip_integration.py

import pytest
from core.mcip import MCIP, CareRecommendation
from datetime import datetime


def test_publish_care_recommendation():
    """Test publishing care recommendation to MCIP."""
    
    # Build recommendation
    rec = CareRecommendation(
        tier="assisted_living",
        tier_score=72.5,
        tier_rankings=[("assisted_living", 72.5), ("in_home", 58.3)],
        confidence=0.92,
        flags=[],
        rationale=["Needs daily ADL support"],
        generated_at=datetime.utcnow().isoformat() + "Z",
        version="4.0.0",
        input_snapshot_id="test_123",
        rule_set="test",
        next_step={"product": "cost_planner"},
        status="complete",
        last_updated=datetime.utcnow().isoformat() + "Z",
        needs_refresh=False
    )
    
    # Publish
    MCIP.publish_care_recommendation(rec)
    
    # Verify
    retrieved = MCIP.get_care_recommendation()
    assert retrieved.tier == "assisted_living"
    assert retrieved.confidence == 0.92
    assert MCIP.is_product_unlocked("cost_planner")


def test_product_unlocking():
    """Test product unlocking after GCP completion."""
    
    # Initially only GCP unlocked
    assert MCIP.is_product_unlocked("gcp")
    assert not MCIP.is_product_unlocked("cost_planner")
    
    # Publish recommendation
    rec = _build_test_recommendation()
    MCIP.publish_care_recommendation(rec)
    
    # Cost Planner should now be unlocked
    assert MCIP.is_product_unlocked("cost_planner")
    assert MCIP.is_product_unlocked("pfma")
```

### 7.2 Integration Tests

```python
# tests/test_gcp_to_cost_planner_flow.py

def test_full_gcp_to_cost_planner_flow():
    """Test complete flow from GCP to Cost Planner."""
    
    # 1. Complete GCP
    gcp_answers = {
        "adl_support_level": "daily",
        "falls_last_year": 2,
        "memory_diagnosis": "none",
        "lives_alone": True
    }
    
    from products.gcp_v4.modules.care_recommendation.logic import derive_outcome
    outcome = derive_outcome(gcp_answers)
    
    # 2. Publish to MCIP
    rec = _build_recommendation_from_outcome(outcome)
    MCIP.publish_care_recommendation(rec)
    
    # 3. Verify Cost Planner can read recommendation
    retrieved = MCIP.get_care_recommendation()
    assert retrieved.tier == outcome["tier"]
    
    # 4. Cost Planner should be unlocked
    assert MCIP.is_product_unlocked("cost_planner")
```

### 7.3 Persona Tests

```python
# tests/test_mcip_personas.py

@pytest.mark.parametrize("persona,expected_tier", [
    ("independent", "independent"),
    ("in_home", "in_home"),
    ("assisted_living", "assisted_living"),
    ("memory_care", "memory_care")
])
def test_persona_recommendations(persona, expected_tier):
    """Test MCIP recommendations for different personas."""
    
    answers = load_persona_answers(persona)
    outcome = derive_outcome(answers)
    
    assert outcome["tier"] == expected_tier
    assert outcome["confidence"] >= 0.8
```

---

## 8. Analytics & Audit

### 8.1 MCIP Event Logging

```python
# Example: Analytics tracking
from core.events import log_event

# Log when user views recommendation
log_event("mcip.recommendation.viewed", {
    "tier": recommendation.tier,
    "confidence": recommendation.confidence,
    "user_id": st.session_state.get("user_id"),
    "timestamp": datetime.utcnow().isoformat()
})

# Log when user clicks next step CTA
log_event("mcip.next_step.clicked", {
    "from_product": "gcp",
    "to_product": recommendation.next_step["product"],
    "tier": recommendation.tier
})

# Log flag interactions
log_event("mcip.flag.cta_clicked", {
    "flag_id": flag["id"],
    "cta_route": flag["cta"]["route"]
})
```

### 8.2 Historical Recommendations (Optional)

```python
# core/mcip_history.py

def store_recommendation_history(recommendation: CareRecommendation) -> None:
    """Store historical recommendation for audit trail."""
    
    if "mcip_history" not in st.session_state:
        st.session_state["mcip_history"] = []
    
    st.session_state["mcip_history"].append({
        "tier": recommendation.tier,
        "confidence": recommendation.confidence,
        "generated_at": recommendation.generated_at,
        "version": recommendation.version
    })


def detect_tier_change() -> bool:
    """Detect if recommendation tier changed significantly."""
    
    history = st.session_state.get("mcip_history", [])
    if len(history) < 2:
        return False
    
    previous_tier = history[-2]["tier"]
    current_tier = history[-1]["tier"]
    
    # Check if tier escalated (e.g., in_home → assisted_living)
    tier_order = ["independent", "in_home", "assisted_living", "memory_care"]
    prev_idx = tier_order.index(previous_tier)
    curr_idx = tier_order.index(current_tier)
    
    return abs(curr_idx - prev_idx) >= 2  # Jumped 2+ tiers
```

---

## 9. Migration Strategy

### 9.1 Current State → MCIP v2

**Phase 1: Add MCIP Layer (Non-Breaking)**
1. Add `core/mcip.py` with MCIP class
2. Initialize MCIP state at app startup
3. Existing products continue working (don't read MCIP yet)

**Phase 2: GCP v4 Integration**
1. Update GCP to publish to MCIP
2. Hubs start reading MCIP for GCP data
3. Remove direct GCP state reads from hubs

**Phase 3: Cost Planner v2 Integration**
1. Update Cost Planner to read MCIP for care tier
2. Publish financial profile to MCIP
3. Remove direct GCP state reads

**Phase 4: PFMA v2 Integration**
1. Update PFMA to publish appointment to MCIP
2. Advisor system reads MCIP for context

**Phase 5: Full Cutover**
1. All hubs read only MCIP state
2. All products publish only to MCIP
3. Remove legacy cross-product state reads

### 9.2 Backward Compatibility

During migration, support both patterns:

```python
# Temporary compatibility helper
def get_care_tier_legacy_compatible():
    """Get care tier from MCIP or legacy GCP state."""
    
    # Try MCIP first
    rec = MCIP.get_care_recommendation()
    if rec:
        return rec.tier
    
    # Fall back to legacy
    gcp_state = st.session_state.get("gcp", {})
    return gcp_state.get("recommended_tier")
```

---

## 10. Summary

### MCIP v2 Principles

1. **MCIP is the conductor** - Sees all hubs, orchestrates the journey
2. **Hubs are traffic controllers** - Display tiles, read MCIP only
3. **Products are module managers** - Control modules, publish to MCIP
4. **Modules are workers** - Ask questions, tell parent product only

### Data Flow

```
User answers questions
    ↓
Module computes outcome
    ↓
Product builds contract (CareRecommendation / FinancialProfile)
    ↓
Product publishes to MCIP
    ↓
MCIP fires events
    ↓
Hubs re-render with new MCIP state
    ↓
User sees updated tiles, recommendations, next steps
```

### Integration Checklist

**For New Products:**
- [ ] Product reads MCIP state for context (e.g., care tier)
- [ ] Product publishes outcome to MCIP via contract
- [ ] Product NEVER reads other product state directly
- [ ] Modules NEVER read MCIP state

**For Hubs:**
- [ ] Hub reads MCIP for product unlocking
- [ ] Hub reads MCIP for completion status
- [ ] Hub reads MCIP for recommended next product
- [ ] Hub NEVER reads product state directly

**For MCIP:**
- [ ] Define data contract for new product outcome
- [ ] Add helper method to publish outcome
- [ ] Add event type for outcome updates
- [ ] Update journey logic for unlocking

---

## Next Steps

1. **Implement MCIP core** (`core/mcip.py`)
2. **Implement event bus** (`core/mcip_events.py`)
3. **Update GCP v4** to publish `CareRecommendation`
4. **Update Concierge Hub** to read MCIP only
5. **Update Cost Planner v2** to publish `FinancialProfile`
6. **Update PFMA v2** to publish appointment data
7. **Add analytics tracking** for MCIP events
8. **Write integration tests** for full flow

---

**Ready to Build?** Start with Phase 1: MCIP Core Implementation 🚀
