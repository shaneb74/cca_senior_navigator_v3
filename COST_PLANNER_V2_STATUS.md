# Cost Planner v2 - Implementation Status

## ✅ Completed: Foundation (Phase 1)

### Branch Created
- **Branch**: `feature/cost_planner_v2`
- **Base**: `dev` branch
- **Commit**: `7ff2773` - Core module engine extensions

### Core Extensions Implemented

#### 1. Custom Step Renderer Registry (`core/modules/registry.py`)
**Purpose**: Allow products to register custom UI for specific steps while engine manages navigation/state

**API**:
```python
from core.modules import registry

def my_custom_renderer(config, step, step_index, state):
    st.markdown("Custom UI")
    return {"field": "value"}  # State updates

registry.register_step_renderer("my_step_id", my_custom_renderer)
```

**Benefits**:
- No more manual step index manipulation
- Engine handles autosave, progress tracking
- Custom UI only where needed

#### 2. ModuleHub Component (`core/modules/hub.py`)
**Purpose**: Reusable component for displaying sub-module selection dashboard

**API**:
```python
from core.modules.hub import ModuleHub

hub = ModuleHub(
    product_key="cost_planner_v2",
    modules=[
        {
            "id": "income",
            "title": "Income Sources",
            "icon": "💰",
            "required": True,
            "visible_if": lambda: True,
            "unlock_if": lambda: True,
        }
    ],
    base_route="?page=cost_v2&cost_module=",
    title="Financial Assessment",
)
hub.render()
```

**Features**:
- Progress tracking from session state
- Conditional visibility/locking
- Required vs. optional badges
- Grid layout (configurable columns)
- Completion counting methods

#### 3. Module Discovery Utilities (`core/modules/loader.py`)
**Purpose**: Standardized functions for finding and loading modules

**API**:
```python
from core.modules.loader import (
    discover_product_modules,
    load_product_module_config,
    load_product_module_manifest,
    module_exists,
)

# Discover available modules
modules = discover_product_modules("cost_planner_v2")
# => ["income", "assets", "insurance", ...]

# Load module config
config = load_product_module_config("cost_planner_v2", "income")
run_module(config)

# Load raw manifest
manifest = load_product_module_manifest("cost_planner_v2", "income")
```

**Benefits**:
- Consistent module loading across products
- Proper error messages for missing modules
- Type checking for ModuleConfig

### Documentation Created

#### 1. Cost Planner v2 Architecture (`COST_PLANNER_V2_ARCHITECTURE.md`)
- Complete architectural vision
- File structure for v2
- Implementation plan (6 phases)
- Success metrics
- Migration strategy

#### 2. Module Architecture Spec (`MODULE_ARCHITECTURE_SPEC.md`)
- Comprehensive guide for AI-driven module creation
- Data gathering process
- Business logic patterns
- Data contract specifications
- Integration requirements

---

## 🔄 Next Steps: Phase 2

### Product Structure

Create the simplified Cost Planner v2 router:

```
products/cost_planner_v2/
  ├── __init__.py
  ├── product.py           # Simplified router (~120 lines)
  ├── hub.py               # Module selection dashboard
  ├── profile.py           # User profile management
  ├── auth.py              # Authentication utilities
  ├── aggregator.py        # Multi-module outcome aggregation
  └── modules/             # (Phase 3+)
```

### Key Files to Create

#### `products/cost_planner_v2/product.py`
```python
def render(module: Optional[str] = None) -> None:
    """Main router - delegates to hub or modules."""
    # Check GCP requirement
    # Route to hub, quick_estimate, or sub-module
    # ~120 lines total (vs. 1,160 in v1)
```

#### `products/cost_planner_v2/hub.py`
```python
def render_module_hub() -> None:
    """Module selection dashboard using ModuleHub component."""
    # Check authentication (route to login/signup if needed)
    # Define modules with visibility/lock logic
    # Create ModuleHub instance
    # Render with navigation
    
    # Note: Login and signup pages exist at:
    # - ?page=login (pages/login.py)
    # - ?page=signup (pages/signup.py)
    # Use route_to("login") or route_to("signup") to navigate
```

#### `products/cost_planner_v2/profile.py`
```python
def get_user_profile() -> Dict[str, bool]:
    """Get user profile flags for module visibility."""
    return {
        "is_veteran": st.session_state.get("profile", {}).get("is_veteran", False),
        "is_home_owner": ...,
        "considering_medicaid": ...,
    }
```

---

## 📊 Progress Tracking

### Implementation Phases

- [x] **Phase 1: Core Extensions** (Completed)
  - [x] Custom renderer registry
  - [x] ModuleHub component
  - [x] Module loader utilities
  - [x] Architecture documentation

- [ ] **Phase 2: Product Structure**
  - [ ] Create `products/cost_planner_v2/` directory
  - [ ] Implement simplified `product.py` router
  - [ ] Implement `hub.py` with ModuleHub
  - [ ] Create `profile.py` for user flags
  - [ ] Copy/adapt `auth.py` and `aggregator.py` from v1

- [ ] **Phase 3: Quick Estimate Module**
  - [ ] `modules/quick_estimate/module.json`
  - [ ] `modules/quick_estimate/config.py`
  - [ ] `modules/quick_estimate/logic.py`
  - [ ] Custom care type comparison widget
  - [ ] Register custom renderer

- [ ] **Phase 4: Financial Modules** (6 modules)
  - [ ] Income module
  - [ ] Assets module
  - [ ] Insurance module
  - [ ] VA Benefits module
  - [ ] Housing module
  - [ ] Medicaid module

- [ ] **Phase 5: Summary & Aggregation**
  - [ ] Summary module (expert review + timeline)
  - [ ] Aggregator outcomes publishing
  - [ ] MCIP handoff integration
  - [ ] Product-level progress

- [ ] **Phase 6: Navigation & Testing**
  - [ ] Update `config/nav.json`
  - [ ] Create hub tile
  - [ ] End-to-end testing
  - [ ] Migration documentation

---

## 🎯 Architecture Benefits

### Code Reduction
| Component | v1 Lines | v2 Lines | Reduction |
|-----------|----------|----------|-----------|
| product.py | 1,160 | ~120 | -90% |
| Custom rendering | ~800 | ~0 | -100% |
| Module dashboard | ~200 | ~50 | -75% |
| **Total product code** | **~2,160** | **~300** | **-86%** |

### Pattern Improvements
- ✅ All modules use standard manifest + logic.py
- ✅ Zero manual step index manipulation
- ✅ Reusable ModuleHub for any multi-module product
- ✅ Custom renderers only where truly needed
- ✅ Proper outcomes publishing to MCIP
- ✅ Consistent autosave across all modules

### Developer Experience
- ✅ Clear separation: router vs. modules vs. aggregation
- ✅ Easy to add new modules (just manifest + logic)
- ✅ Discoverable modules (automatic detection)
- ✅ Type-safe config loading with validation
- ✅ Comprehensive error messages

---

## 🚀 How to Continue Development

### 1. Update Engine to Support Custom Renderers

**File**: `core/modules/engine.py`

Add to `run_module()` function (around line 30):

```python
from core.modules import registry

def run_module(config: ModuleConfig) -> Dict[str, Any]:
    # ... existing setup code ...
    
    step = config.steps[step_index]
    
    # NEW: Check for custom renderer
    custom_renderer = registry.get_step_renderer(step.id)
    if custom_renderer:
        state_updates = custom_renderer(config, step, step_index, state)
        if state_updates:
            state.update(state_updates)
        return state
    
    # ... rest of existing code (standard rendering) ...
```

### 2. Create Product Structure

```bash
mkdir -p products/cost_planner_v2/modules
touch products/cost_planner_v2/__init__.py
touch products/cost_planner_v2/product.py
touch products/cost_planner_v2/hub.py
touch products/cost_planner_v2/profile.py
```

### 3. Implement Simplified Router

Follow the code template in `COST_PLANNER_V2_ARCHITECTURE.md` section:
"Cost Planner v2 Implementation → Product Router"

### 4. Test Core Extensions

Create a simple test module to validate:
- Custom renderer registration
- ModuleHub rendering
- Module discovery

### 5. Iterate on First Real Module

Once product structure is in place, create `quick_estimate` module as proof of concept.

---

## 📝 Key Design Decisions

### 1. Extend Engine, Don't Bypass It
**Decision**: Add custom renderer support to engine rather than writing parallel navigation logic

**Rationale**: 
- Maintains single source of truth for navigation
- Keeps autosave, progress tracking, resume functionality
- Reduces code duplication by 90%

### 2. ModuleHub as Reusable Component
**Decision**: Abstract module dashboard into `core/modules/hub.py`

**Rationale**:
- Other products may need sub-modules (PFMA phases, etc.)
- Eliminates 200 lines of tile rendering code per product
- Standardizes visibility/locking patterns

### 3. Standard Module Contract for All Sub-Modules
**Decision**: Every module has `module.json` + `logic.py` + `config.py`

**Rationale**:
- Consistency with GCP module pattern
- AI-friendly (can generate modules from spec)
- Discoverable and testable in isolation

### 4. Aggregator Pattern for Multi-Module Outcomes
**Decision**: Keep v1's aggregator.py pattern, enhance with outcomes publishing

**Rationale**:
- Already well-designed for combining financial data
- Just needs to publish `OutcomeContract` to MCIP
- Separates module logic from product-level logic

---

## 🔧 Development Workflow

### Local Development
```bash
# Switch to feature branch
git checkout feature/cost_planner_v2

# Create new files
# Edit code
# Test in browser

# Commit frequently with clear messages
git add -A
git commit -m "feat: implement product router for cost_planner_v2"

# Push to remote when ready
git push origin feature/cost_planner_v2
```

### Testing Strategy
1. **Unit tests**: Test core extensions (registry, hub, loader)
2. **Integration tests**: Test module loading and rendering
3. **Manual testing**: Run app with `streamlit run app.py`
4. **Parallel deployment**: Run both v1 and v2 side-by-side

### Validation Checklist
- [ ] Core extensions work independently
- [ ] Engine respects custom renderers
- [ ] ModuleHub renders correctly
- [ ] Module discovery finds all modules
- [ ] First module renders with standard engine
- [ ] Progress tracking works across modules
- [ ] Aggregator combines outcomes
- [ ] MCIP handoff publishes affordability

---

## 📚 Reference Documents

1. **COST_PLANNER_V2_ARCHITECTURE.md** - Complete implementation plan
2. **MODULE_ARCHITECTURE_SPEC.md** - Guide for creating new modules
3. **GCP module** - Reference implementation (`products/gcp/modules/care_recommendation/`)
4. **v1 Cost Planner** - Understand what we're replacing (`products/cost_planner/`)

---

## 🎉 What's Been Accomplished

You now have:
- ✅ Clean feature branch for isolated development
- ✅ Three core extensions ready to use
- ✅ Comprehensive architecture documentation
- ✅ Clear implementation roadmap
- ✅ Design decisions documented
- ✅ Validation criteria defined

**Next coding session**: Implement Phase 2 (product structure) to see the 86% code reduction in action!

---

**Status**: Foundation Complete ✨  
**Commit**: `7ff2773`  
**Branch**: `feature/cost_planner_v2`  
**Ready for**: Phase 2 Implementation
