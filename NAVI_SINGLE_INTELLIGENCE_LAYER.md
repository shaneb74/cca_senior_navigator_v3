# 🤖 Navi Becomes The Single Intelligence Layer

**Epic:** Deprecate Hub Guide → Navi owns all guidance, orchestration, and service recommendations

## Vision

Navi evolves from "journey status banner" to **THE canonical intelligence layer**:
- Single source of truth for user guidance
- Coordinates entire journey across all products
- Drives Additional Services recommendations  
- Provides dynamic Q&A and contextual help
- Replaces and deprecates Hub Guide entirely

## Architecture: Before vs. After

### BEFORE (Multiple Intelligence Layers)
```
Hub Page:
  ├─ Header
  ├─ Hub Guide (orchestration, next steps, services)  ← DEPRECATED
  ├─ MCIP Journey Status (progress banner)             ← OLD LOCATION
  ├─ Product Tiles
  └─ Additional Services (driven by Hub Guide)

Product Page:
  ├─ Product Header
  ├─ Module Engine (built-in progress bar)            ← REMOVE
  ├─ Module Content
  └─ CTAs
```

### AFTER (Single Intelligence Layer)
```
Hub Page:
  ├─ Header
  ├─ Navi Panel (orchestration, guidance, services)   ← NEW CANONICAL
  │   ├─ Context-aware summary
  │   ├─ Next-best action
  │   ├─ 3 dynamic question chips
  │   └─ Additional Services orchestration
  ├─ Product Tiles
  └─ Additional Services Rail (driven by Navi)

Product Page:
  ├─ Product Header
  ├─ Navi Panel (module context, progress)            ← REPLACES MODULE PROGRESS BAR
  │   ├─ "Let's talk about mobility..."
  │   ├─ Progress: 2/5
  │   └─ Dynamic help
  ├─ Module Content (no more built-in progress)
  └─ CTAs
```

## Placement Rules

✅ **CORRECT:** Navi lives **under header, above content**
```
[Global Header]
[🤖 Navi Panel]        ← Always here
[Content: Tiles or Module]
```

❌ **WRONG:** Navi above header or missing
```
[🤖 Navi Panel]        ← NO! Not above header
[Global Header]
[Content]
```

## Responsibilities Matrix

| Responsibility | Hub Guide (OLD) | MCIP Journey Status (OLD) | Navi (NEW) |
|---|---|---|---|
| Journey coordination | ✅ | Partial | ✅ **OWNS** |
| Next-best actions | ✅ | ✅ | ✅ **CONSOLIDATES** |
| Product progress | ✅ | ✅ | ✅ **CONSOLIDATES** |
| Additional Services orchestration | ✅ | ❌ | ✅ **TAKES OVER** |
| Flag aggregation | ✅ | ❌ | ✅ **TAKES OVER** |
| Dynamic Q&A | ❌ | ❌ | ✅ **NEW** |
| Module-level guidance | ❌ | ❌ | ✅ **ALREADY BUILT** |
| Progress visualization | Partial | ✅ | ✅ **CONSOLIDATES** |

## Inputs (Read-Only)

Navi consumes existing data sources:

### 1. Product Contracts (via MCIP)
```python
from core.mcip import MCIP

# Get all product states
care_rec = MCIP.get_care_recommendation()      # GCP outcome
financial = MCIP.get_financial_profile()       # Cost Planner outcome
appointment = MCIP.get_advisor_appointment()   # PFMA outcome

# Get progress
progress = MCIP.get_journey_progress()
# Returns: {
#   "completed_count": 2,
#   "completed_products": ["gcp", "cost_planner"],
#   "total": 3
# }
```

### 2. Module State (when inside product)
```python
# Current module state from session
module_state = st.session_state.get(config.state_key, {})
current_step = st.session_state.get(f"{config.state_key}._step", 0)
```

### 3. Flag Set (aggregate across products)
```python
# NEW: Centralized flag accessor
from core.flags import get_all_flags

flags = get_all_flags()
# Returns: {
#   "veteran": True,
#   "fall_risk": True,
#   "memory_concerns": False,
#   ...
# }
```

**Rule:** Create ONE centralized flag accessor. No duplicate flag pipelines.

## Outputs (UI Only, No Storage)

### 1. Next-Best Action
```python
{
  "action": "Calculate Your Care Costs",
  "reason": "Based on your Assisted Living recommendation",
  "route": "cost_v2",
  "icon": "💰"
}
```

### 2. Dynamic Suggested Questions (3 chips)
```python
[
  "What if I can't afford Assisted Living?",
  "Can I use VA benefits?",
  "What's included in the monthly cost?"
]
```

### 3. Additional Services Recommendations
```python
[
  "omcare",           # Based on flags
  "senior_life_ai",   # Ordered by relevance
  "veterans_benefits"
]
```

### 4. Context-Aware Guidance
```python
{
  "summary": "You're 2/3 complete! Great progress.",
  "context_boost": [
    "You chose Assisted Living (85% confidence)",
    "Estimated cost: $4,500/month (30 month runway)"
  ]
}
```

## Component Structure

### New File: `core/navi.py`
```python
"""
Navi - The Single Intelligence Layer

Owns:
- Journey coordination across all products
- Next-best action recommendations
- Dynamic Q&A and suggested questions
- Additional Services orchestration
- Flag aggregation and mapping
"""

class NaviOrchestrator:
    """Central coordinator for Navi's intelligence."""
    
    @staticmethod
    def get_context(hub_key: str = "concierge") -> NaviContext:
        """Get complete Navi context for current hub/product."""
        pass
    
    @staticmethod
    def get_next_action() -> Dict[str, str]:
        """Get next-best action for user."""
        pass
    
    @staticmethod
    def get_suggested_questions(flags: Dict[str, bool]) -> List[str]:
        """Get 3 dynamic question chips based on flags."""
        pass
    
    @staticmethod
    def get_additional_services(flags: Dict[str, bool]) -> List[str]:
        """Get recommended Additional Services based on flags."""
        pass


def render_navi_panel(
    location: str = "hub",  # "hub" or "product"
    hub_key: Optional[str] = None,
    product_key: Optional[str] = None,
    module_config: Optional[ModuleConfig] = None
) -> None:
    """Render Navi panel at canonical location.
    
    Args:
        location: "hub" or "product"
        hub_key: Hub identifier (for hub pages)
        product_key: Product identifier (for product pages)
        module_config: Module config (for product pages)
    """
    pass
```

### Updated: `core/flags.py` (NEW)
```python
"""
Centralized Flag Aggregation

Single source of truth for all flags across products/modules.
"""

def get_all_flags() -> Dict[str, bool]:
    """Aggregate flags from all products and modules.
    
    Returns:
        Dict mapping flag names to boolean values
    """
    flags = {}
    
    # Aggregate from GCP
    care_rec = MCIP.get_care_recommendation()
    if care_rec:
        flags.update(care_rec.flags or {})
    
    # Aggregate from Cost Planner
    financial = MCIP.get_financial_profile()
    if financial:
        flags.update(financial.flags or {})
    
    # Aggregate from PFMA
    appointment = MCIP.get_advisor_appointment()
    if appointment:
        flags.update(appointment.flags or {})
    
    return flags
```

### Updated: `hubs/concierge.py`
```python
def render():
    """Render Concierge Care Hub with Navi orchestration."""
    
    # Render Navi panel (replaces Hub Guide and MCIP journey status)
    render_navi_panel(location="hub", hub_key="concierge")
    
    # Render product tiles (unchanged)
    render_product_tiles()
    
    # Render Additional Services (driven by Navi)
    # Navi provides the service keys via context
    render_additional_services_rail()
```

### Updated: `products/gcp_v4/product.py`
```python
def render():
    """Render GCP v4 product."""
    
    # Load module config
    config = _load_module_config()
    
    # Render Navi panel at top (replaces module progress bar)
    render_navi_panel(
        location="product",
        product_key="gcp_v4",
        module_config=config
    )
    
    # Run module engine (without built-in progress bar)
    module_state = run_module(config, show_progress=False)
    
    # Handle completion/publishing
    if outcome:
        _publish_to_mcip(outcome, module_state)
```

## Deprecation Plan

### 1. Remove Hub Guide
- [x] ~~`core/hub_guide.py`~~ - Already removed
- [ ] `core/base_hub.py` - Remove `hub_guide_block` parameter
- [ ] All hub files - Remove `compute_hub_guide()` calls

### 2. Remove Module Progress Bars
- [ ] `core/modules/engine.py` - Remove progress bar rendering
- [ ] `core/modules/layout.py` - Remove progress components
- [ ] Module configs - Remove `show_progress` flag (deprecated)

### 3. Consolidate Journey Status
- [ ] `core/ui.py` - Deprecate standalone `render_mcip_journey_status()`
- [ ] Merge functionality into `render_navi_panel()`

## Implementation Phases

### Phase 1: Create Core Navi System ⏳
1. Create `core/navi.py` with `NaviOrchestrator`
2. Create `core/flags.py` with centralized flag accessor
3. Build `render_navi_panel()` consolidating all intelligence
4. Add dynamic question system
5. Add Additional Services orchestration

### Phase 2: Update Hubs ⏳
1. Update `hubs/concierge.py` to use `render_navi_panel()`
2. Remove all `compute_hub_guide()` calls
3. Update Additional Services to read from Navi context
4. Test hub rendering and functionality

### Phase 3: Update Products ⏳
1. Update `products/gcp_v4/product.py`
2. Update `products/cost_planner_v2/product.py`
3. Update `products/pfma_v2/product.py`
4. Pass `module_config` to Navi for context

### Phase 4: Remove Module Progress Bars ⏳
1. Update `core/modules/engine.py` - Remove progress rendering
2. Navi now owns progress visualization
3. Test all modules still work

### Phase 5: Clean Up ⏳
1. Remove deprecated files
2. Update all imports
3. Remove unused parameters
4. Run full regression tests

## End-to-End Test Plan

### A. Placement & Presence
- [ ] On Concierge Hub: Header → Navi → Tiles → Services
- [ ] Inside GCP: Product Header → Navi → Module Content
- [ ] Inside Cost Planner: Product Header → Navi → Module Content
- [ ] Inside PFMA: Product Header → Navi → Module Content

### B. Dynamic Suggestions
- [ ] No flags: Shows 3 default starter questions
- [ ] With flags: Shows 3 relevant questions
- [ ] Clicking question: Moves to history, answer appears, refills to 3

### C. Next-Best Action
- [ ] GCP < 100%: Suggests starting/resuming GCP
- [ ] GCP = 100%, Cost < 100%: Suggests Cost Planner
- [ ] All complete: Offers "Explore services / resources"

### D. Additional Services
- [ ] Set veteran flag → Navi recommends VA benefits service
- [ ] Set fall_risk flag → Navi recommends Omcare
- [ ] Services appear in correct priority order

### E. Back to Hub Navigation
- [ ] From FAQs, "Back to Hub" → Concierge Care Hub (not Welcome)
- [ ] Browser back returns to FAQs correctly
- [ ] Session context preserved

### F. Regression Checks
- [ ] No visual overlap with header
- [ ] Tiles and modules work normally
- [ ] No double-rendering or conflicts
- [ ] All products complete successfully
- [ ] Export page still works
- [ ] Achievement badges still work

### G. Progress Visualization
- [ ] Navi shows module progress (2/5, etc.)
- [ ] Progress updates as user advances
- [ ] No more built-in module progress bars
- [ ] Navi IS the progress indicator

## Success Criteria

✅ **Single Intelligence Layer**
- Navi is the only component providing guidance
- No Hub Guide, no separate progress bars
- One source of truth for recommendations

✅ **Consistent Placement**
- Navi always under header, above content
- Same appearance in hubs and products
- Clean spacing rhythm maintained

✅ **Complete Functionality**
- Journey coordination works
- Additional Services driven by Navi
- Dynamic Q&A functional
- Progress visualization clear

✅ **Clean Deprecation**
- Hub Guide fully removed
- Module progress bars removed
- No duplicate intelligence layers

✅ **Zero Regressions**
- All products work normally
- All hubs function correctly
- Navigation preserved
- Data integrity maintained

---

**This is a major architectural upgrade.** Navi becomes the **canonical intelligence layer** for the entire application. 🤖✨
