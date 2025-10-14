# MCIP → Hub → Product → Module: The Extensible Pattern

> **The real magic: A polymorphic architecture that scales to ANY product**

This document defines the universal pattern that makes the platform infinitely extensible. GCP and Cost Planner are just the first two implementations.

---

## The Hierarchy (Universal)

```
MCIP (Conductor)
 ├── sees all hubs
 ├── manages journey state
 ├── orchestrates product unlocking
 └── stores product outputs (care_recommendation, financial_profile, advisor_appointment, etc.)
     ↓
HUB (Concierge, Learning, Partners, Professional)
 ├── displays product tiles
 ├── reads MCIP for unlocking logic
 ├── applies silver gradient to recommended next
 └── NEVER reads product state directly
     ↓
PRODUCT (GCP, Cost Planner, PFMA, future products...)
 ├── has entry point: product.py with render()
 ├── checks MCIP for prerequisites (gates)
 ├── orchestrates modules or steps
 ├── publishes output contract to MCIP
 └── NEVER reads other product state directly
     ↓
MODULE (care_recommendation, base_care_cost, appointment_scheduling, etc.)
 ├── has module.json (questions)
 ├── has config.py (ModuleConfig loader)
 ├── has logic.py (compute outcome)
 ├── returns structured output
 └── NEVER knows about MCIP or products
```

---

## The Universal Product Interface

Every product implements this contract:

### 1. Entry Point (`product.py`)

```python
"""Universal Product Interface"""

import streamlit as st
from core.mcip import MCIP


def render():
    """Product entry point - called by navigation.
    
    RESPONSIBILITIES:
    1. Check MCIP for prerequisites (gates)
    2. Orchestrate modules/steps
    3. Publish output to MCIP when complete
    4. Show completion screen
    
    RULES:
    - NEVER read from other product state
    - ALWAYS read prerequisites from MCIP
    - ALWAYS publish output to MCIP
    - ALWAYS mark product complete in journey
    """
    
    # STEP 1: Gate - check prerequisites
    if not _check_prerequisites():
        _render_gate()
        return
    
    # STEP 2: Run product logic (modules, steps, forms, etc.)
    result = _run_product_logic()
    
    # STEP 3: Publish to MCIP when complete
    if result and result.get("status") == "complete":
        if not _already_published():
            _publish_to_mcip(result)
            _mark_published()
        
        _render_completion_screen()


def _check_prerequisites() -> bool:
    """Check if prerequisites met via MCIP."""
    # Example: Cost Planner checks for care_recommendation
    # Example: PFMA checks for care_recommendation + financial_profile
    pass


def _render_gate():
    """Show friendly gate with prerequisites."""
    pass


def _run_product_logic():
    """Run modules, steps, or custom flow."""
    pass


def _publish_to_mcip(result):
    """Publish product output to MCIP."""
    pass


def _render_completion_screen():
    """Show completion with next steps."""
    pass
```

### 2. Output Contract (Dataclass)

Every product defines its output contract in `core/mcip.py`:

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ProductOutputContract:
    """Base class for all product outputs.
    
    RULES:
    - Immutable after creation
    - Includes provenance (generated_at, version, input_snapshot_id)
    - Includes status (complete, needs_refresh)
    - JSON-serializable
    """
    
    # Provenance (required for all products)
    generated_at: str              # ISO 8601 timestamp
    version: str                   # Product version (e.g., "4.0.0")
    input_snapshot_id: str         # Unique ID for this output
    
    # Status (required for all products)
    status: str                    # "complete" | "in_progress" | "error"
    last_updated: str              # ISO 8601 timestamp
    needs_refresh: bool            # True if answers changed


# Example: GCP v4 output contract
@dataclass
class CareRecommendation(ProductOutputContract):
    """Output from Guided Care Plan."""
    tier: str                      # Care level recommendation
    tier_score: float              # Confidence score for tier
    tier_rankings: List[tuple]     # All tiers ranked
    confidence: float              # Overall confidence
    flags: List[Dict]              # Risk/support flags
    rationale: List[str]           # Key decision factors
    next_step: Dict                # Suggested next product
    rule_set: str                  # Scoring rules version


# Example: Cost Planner v2 output contract
@dataclass
class FinancialProfile(ProductOutputContract):
    """Output from Cost Planner."""
    base_care_cost: float          # Monthly base cost
    additional_services: float     # Monthly add-ons
    total_monthly_cost: float      # Total monthly
    annual_cost: float             # Year 1 projection
    three_year_projection: float   # 3-year with inflation
    five_year_projection: float    # 5-year with inflation
    funding_sources: Dict[str, float]  # Breakdown by source
    funding_gap: float             # Cost - sources
    care_tier: str                 # From MCIP recommendation
    region: str                    # Geographic region
    facility_type: str             # Facility selection


# Example: Future product - Medication Manager
@dataclass
class MedicationPlan(ProductOutputContract):
    """Output from Medication Manager."""
    medications: List[Dict]        # Med list with schedules
    interactions: List[Dict]       # Drug interactions
    cost_per_month: float          # Medication costs
    pharmacy_info: Dict            # Pharmacy details
    alerts: List[Dict]             # Critical alerts
```

### 3. Publishing to MCIP

```python
# In product.py after completion:

from core.mcip import MCIP, CareRecommendation  # Or FinancialProfile, etc.

# Build output contract
output = CareRecommendation(
    tier="assisted_living",
    tier_score=12.5,
    # ... all fields
)

# Publish to MCIP
MCIP.publish_care_recommendation(output)  # Or publish_financial_profile(), etc.

# Mark complete in journey
MCIP.mark_product_complete("gcp")  # Or "cost_planner", "pfma", etc.

# MCIP fires event automatically
# "mcip.recommendation.updated" or "mcip.financial.updated", etc.
```

---

## The Universal Module Pattern

Modules are **completely agnostic** to products and MCIP. They just compute outcomes.

### Module Structure

```
modules/module_name/
├── module.json          # Questions (declarative)
├── config.py            # Loads module.json → ModuleConfig
├── logic.py             # Computes outcome from answers
└── (optional) custom renderers, validators, etc.
```

### Module Interface

```python
# logic.py - Universal module interface

def derive_outcome(answers: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Compute module outcome from answers.
    
    Args:
        answers: User responses from module.json questions
        config: Optional configuration data
    
    Returns:
        Dict with module-specific outcome structure
        
    RULES:
    - Pure function (no side effects)
    - No MCIP awareness
    - No product awareness
    - Just answers → outcome
    """
    
    # Module-specific logic
    result = _compute(answers, config)
    
    return {
        "outcome_type": "module_name",
        "data": result,
        "confidence": 0.85,
        "metadata": {...}
    }
```

**Key Point:** The module doesn't care:
- ❌ What product is using it
- ❌ Where its output goes
- ❌ What happens after computation
- ✅ It just transforms `answers → outcome`

---

## Polymorphic Product Examples

### Example 1: GCP v4 (Module-Based Product)

```
User → ?page=gcp_v4
         ↓
    product.py checks prerequisites
         ↓ (none needed)
    Run module engine with care_recommendation module
         ↓
    module.json → questions
    logic.py → outcome
         ↓
    Build CareRecommendation from outcome
         ↓
    MCIP.publish_care_recommendation()
    MCIP.mark_product_complete("gcp")
         ↓
    Show completion screen
```

### Example 2: Cost Planner v2 (Module Hub Product)

```
User → ?page=cost_v2
         ↓
    product.py checks MCIP.get_care_recommendation()
         ↓ (exists)
    hub.py orchestrates 6 modules
         ↓
    Each module: questions → outcome
         ↓
    Aggregate all module outcomes
         ↓
    Build FinancialProfile from aggregate
         ↓
    MCIP.publish_financial_profile()
    MCIP.mark_product_complete("cost_planner")
         ↓
    Show completion screen
```

### Example 3: PFMA v2 (Step-Based Product)

```
User → ?page=pfma_v2
         ↓
    product.py checks prerequisites:
    - MCIP.get_care_recommendation() ✓
    - MCIP.get_financial_profile() ✓
         ↓
    engine.py runs step-driven funnel (not modules)
         ↓
    Steps defined in pfma_steps.json
         ↓
    Build AdvisorAppointment from step outputs
         ↓
    MCIP.publish_appointment()
    MCIP.mark_product_complete("pfma")
         ↓
    Show confirmation screen
```

### Example 4: Future Product - Care Transition Planner

```
User → ?page=transition_planner
         ↓
    product.py checks prerequisites:
    - MCIP.get_care_recommendation() ✓
    - MCIP.get_financial_profile() ✓
         ↓
    Custom workflow (not modules or steps)
    - Timeline builder
    - Checklist generator
    - Document prep
         ↓
    Build TransitionPlan from workflow outputs
         ↓
    MCIP.publish_transition_plan()
    MCIP.mark_product_complete("transition_planner")
         ↓
    Show completion screen with downloadable plan
```

**The pattern is universal.**

---

## Hub Integration (Polymorphic)

Hubs display tiles for ALL products using the same pattern:

```python
# In hubs/concierge.py

from core.mcip import MCIP

def render():
    """Render Concierge Hub."""
    
    # Get all products (from config or registry)
    products = [
        {"key": "gcp", "label": "Guided Care Plan"},
        {"key": "cost_planner", "label": "Cost Planner"},
        {"key": "pfma", "label": "Plan with Advisor"},
        {"key": "transition_planner", "label": "Care Transition"},  # Future
        # ... any number of products
    ]
    
    for product in products:
        _render_product_tile(product)


def _render_product_tile(product: Dict):
    """Render tile for any product (polymorphic)."""
    
    key = product["key"]
    
    # Check if unlocked via MCIP
    unlocked = MCIP.is_product_unlocked(key)
    
    # Check if completed via MCIP
    completed = MCIP.is_product_complete(key)
    
    # Check if recommended next via MCIP
    recommended = MCIP.get_recommended_next_product() == key
    
    # Render tile with appropriate styling
    if recommended:
        # Silver gradient border
        pass
    
    if completed:
        # Show checkmark
        pass
    
    if not unlocked:
        # Show lock icon
        pass
```

**Hub doesn't care:**
- ❌ What products exist
- ❌ How products work internally
- ❌ What products publish
- ✅ It just reads MCIP for state

---

## Adding a New Product (4 Steps)

### Step 1: Define Output Contract

```python
# In core/mcip.py

@dataclass
class NewProductOutput(ProductOutputContract):
    """Output from new product."""
    field1: str
    field2: float
    field3: List[Dict]
    # ... product-specific fields
```

### Step 2: Add MCIP Methods

```python
# In core/mcip.py - MCIP class

def publish_new_product(self, output: NewProductOutput):
    """Publish new product output to MCIP."""
    st.session_state["mcip"]["new_product_output"] = output
    self.events.emit("mcip.new_product.updated", output)


def get_new_product_output(self) -> Optional[NewProductOutput]:
    """Get new product output from MCIP."""
    return st.session_state["mcip"].get("new_product_output")
```

### Step 3: Implement Product

```python
# In products/new_product/product.py

from core.mcip import MCIP, NewProductOutput

def render():
    """Render new product."""
    
    # Check prerequisites
    if not _check_prerequisites():
        _render_gate()
        return
    
    # Run product logic
    result = _run_logic()
    
    # Publish to MCIP
    if result and result.get("status") == "complete":
        output = NewProductOutput(...)
        MCIP.publish_new_product(output)
        MCIP.mark_product_complete("new_product")
```

### Step 4: Register Route

```json
// In config/nav.json

{
  "key": "new_product",
  "label": "New Product",
  "module": "products.new_product.product:render",
  "hidden": true
}
```

**That's it.** The hub automatically displays the tile. MCIP handles orchestration.

---

## Key Principles (Universal Laws)

### 1. **Separation of Concerns**
- **MCIP**: Orchestration, journey management, state storage
- **Hubs**: Display, navigation, user guidance
- **Products**: Business logic, prerequisites, publishing
- **Modules**: Pure computation, answers → outcomes

### 2. **Single Source of Truth**
- All cross-product data flows through MCIP
- Products NEVER read each other's state
- Hubs NEVER read product state

### 3. **Polymorphism**
- Products are interchangeable
- Modules are interchangeable
- Hubs display any product
- MCIP orchestrates any journey

### 4. **Event-Driven**
- Products publish, events fire
- Hubs subscribe, caches refresh
- Decoupled, reactive architecture

### 5. **Declarative Configuration**
- module.json defines questions
- nav.json defines routes
- Products define output contracts
- Configuration, not code

---

## Scalability

This architecture scales to **unlimited products** because:

✅ **No coupling** - Products don't know about each other  
✅ **MCIP abstraction** - Central orchestration  
✅ **Polymorphic interface** - All products follow same pattern  
✅ **Event-driven** - Async updates via pub/sub  
✅ **Declarative** - Configuration drives behavior  

**Examples of future products that fit this pattern:**
- 🏥 **Healthcare Coordinator** - Tracks doctors, appointments, records
- 🏠 **Home Modification Planner** - Accessibility improvements
- 💊 **Medication Manager** - Drug interactions, refills, costs
- 📋 **Legal Documents** - POA, advance directives, wills
- 🚗 **Transportation Planner** - Medical transport, ride services
- 👨‍👩‍👧 **Family Caregiver Support** - Respite care, support groups
- 📊 **Quality Scorecard** - Facility ratings, inspection reports
- 🎯 **Care Transition Planner** - Moving checklists, timeline
- 💰 **Benefit Maximizer** - VA, Medicaid, tax deductions
- 🏛️ **Estate Planning** - Financial legacy, trusts

**Each one:**
1. Defines output contract
2. Implements product.py
3. Publishes to MCIP
4. Shows up in hubs automatically

---

## The Real Magic

```
MCIP doesn't care what products exist.
Hubs don't care what products do.
Products don't care about each other.
Modules don't care about products.

But together, they create a
seamless, intelligent, extensible
care navigation platform.

THAT'S the magic. 🎯
```

---

## GCP → Cost Planner: A Case Study

Now, in the context of this universal pattern, let's look at the GCP → Cost Planner handoff:

### What Makes It Work

1. **GCP v4** implements universal product interface:
   - ✅ Checks prerequisites (none needed)
   - ✅ Runs module engine
   - ✅ Publishes CareRecommendation to MCIP
   - ✅ Marks complete in journey

2. **MCIP** stores and orchestrates:
   - ✅ Stores care_recommendation
   - ✅ Fires "mcip.recommendation.updated" event
   - ✅ Updates journey state
   - ✅ Returns recommendation to any product that asks

3. **Cost Planner v2** implements universal product interface:
   - ✅ Checks prerequisites via MCIP (care_recommendation)
   - ✅ Runs module hub
   - ✅ Publishes FinancialProfile to MCIP
   - ✅ Marks complete in journey

4. **Concierge Hub** displays polymorphically:
   - ✅ Reads MCIP for GCP tile (complete ✓)
   - ✅ Reads MCIP for Cost Planner tile (unlocked, recommended 🌟)
   - ✅ Applies styling based on MCIP state

### Why It's Extensible

Tomorrow we add **PFMA v2**:
- Checks MCIP for care_recommendation + financial_profile
- Publishes AdvisorAppointment to MCIP
- Hub automatically displays tile
- **Zero changes to GCP or Cost Planner**

Next week we add **Medication Manager**:
- Checks MCIP for care_recommendation
- Publishes MedicationPlan to MCIP
- Hub automatically displays tile
- **Zero changes to existing products**

**That's extensibility.** 🚀

---

## Summary

**The hierarchy is the product:**
- MCIP → Hub → Product → Module

**The pattern is universal:**
- Check prerequisites → Run logic → Publish output → Show completion

**The magic is polymorphism:**
- Any product, any module, any journey
- Orchestrated by MCIP
- Displayed by hubs
- Zero coupling

**GCP and Cost Planner are just the first two implementations of an infinitely scalable pattern.** 🎯
