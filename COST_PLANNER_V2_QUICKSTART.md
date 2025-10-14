# Cost Planner v2 - Quick Start Guide

## Overview

We're rebuilding Cost Planner with a clean architecture that reduces code by 86% while making it more maintainable and extensible.

**Branch**: `feature/cost_planner_v2`  
**Status**: Phase 1 Complete (Core Extensions) ✅  
**Next**: Phase 2 (Product Structure)

---

## What's New in v2?

### Core Extensions Added

1. **Custom Renderer Registry** (`core/modules/registry.py`)
   - Let products customize specific steps while engine handles navigation
   - Example: Quick estimate step uses custom care type comparison UI

2. **ModuleHub Component** (`core/modules/hub.py`)
   - Reusable sub-module dashboard with progress tracking
   - Handles conditional visibility and locking

3. **Module Discovery** (`core/modules/loader.py`)
   - Find and load modules dynamically
   - Standardized config loading with validation

### Architecture Changes

**Before (v1)**:
```
product.py (1,160 lines)
  ├── Custom rendering for 7 steps
  ├── Manual navigation logic
  ├── Duplicated tile rendering
  └── Hard-coded module discovery
```

**After (v2)**:
```
product.py (~120 lines)
  └── Simple router: hub or sub-module

hub.py (~50 lines)
  └── Uses ModuleHub component

modules/
  ├── income/ (manifest + logic)
  ├── assets/ (manifest + logic)
  └── ... (all follow same pattern)
```

---

## How to Use the New Extensions

### 1. Custom Step Renderer

```python
from core.modules import registry
import streamlit as st

def render_quick_estimate(config, step, step_index, state):
    """Custom renderer for quick estimate step."""
    st.markdown("### Quick Cost Estimate")
    
    # Your custom UI here
    care_type = st.selectbox(
        "Select care type",
        ["In-Home Care", "Assisted Living", "Memory Care"]
    )
    
    # Return state updates
    return {"care_type": care_type}

# Register it
registry.register_step_renderer("quick_estimate", render_quick_estimate)
```

### 2. ModuleHub Component

```python
from core.modules.hub import ModuleHub

modules = [
    {
        "id": "income",
        "title": "Income Sources",
        "description": "Social Security, pensions, etc.",
        "icon": "💰",
        "required": True,
        "visible_if": lambda: True,  # Always visible
        "unlock_if": lambda: True,   # Always unlocked
    },
    {
        "id": "va_benefits",
        "title": "VA Benefits",
        "description": "Veterans benefits",
        "icon": "🎖️",
        "required": False,
        "visible_if": lambda: is_veteran(),  # Conditional
        "unlock_if": lambda: income_complete(),
        "lock_msg": "Complete Income module first",
    },
]

hub = ModuleHub(
    product_key="cost_planner_v2",
    modules=modules,
    base_route="?page=cost_v2&cost_module=",
    title="Financial Assessment Modules",
)
hub.render()

# Check completion
if hub.all_required_completed():
    st.success("All required modules done!")
```

### 3. Module Discovery

```python
from core.modules.loader import (
    discover_product_modules,
    load_product_module_config,
)

# Find all available modules
modules = discover_product_modules("cost_planner_v2")
# => ["income", "assets", "insurance", ...]

# Load a specific module
config = load_product_module_config("cost_planner_v2", "income")

# Run it through standard engine
from core.modules.engine import run_module
run_module(config)
```

---

## Next Steps: Implementing Phase 2

### 1. Update Module Engine

Edit `core/modules/engine.py`, add after line ~30:

```python
from core.modules import registry

def run_module(config: ModuleConfig) -> Dict[str, Any]:
    # ... existing setup ...
    step = config.steps[step_index]
    
    # Check for custom renderer
    custom_renderer = registry.get_step_renderer(step.id)
    if custom_renderer:
        state_updates = custom_renderer(config, step, step_index, state)
        if state_updates:
            state.update(state_updates)
        return state
    
    # ... rest of standard rendering ...
```

### 2. Create Product Structure

```bash
mkdir -p products/cost_planner_v2/modules
cd products/cost_planner_v2
touch __init__.py product.py hub.py profile.py auth.py aggregator.py
```

### 3. Implement Simple Router

`products/cost_planner_v2/product.py`:

```python
from typing import Optional
import streamlit as st
from core.modules.loader import load_product_module_config
from core.modules.engine import run_module
from layout import render_shell_start, render_shell_end

def render(module: Optional[str] = None):
    render_shell_start("", active_route="cost_v2")
    
    target = st.query_params.get("cost_module", module)
    
    if not target or target == "hub":
        from products.cost_planner_v2.hub import render_module_hub
        render_module_hub()
    else:
        config = load_product_module_config("cost_planner_v2", target)
        run_module(config)
    
    render_shell_end()
```

### 4. Create Module Hub

`products/cost_planner_v2/hub.py`:

```python
import streamlit as st
from core.modules.hub import ModuleHub
from core.nav import route_to
from products.cost_planner_v2.auth import is_authenticated

def render_module_hub():
    # Check authentication first
    if not is_authenticated():
        st.warning("🔒 **Sign in Required**")
        st.markdown("To access financial assessment, please sign in.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Hub", use_container_width=True):
                route_to("hub_concierge")
        with col2:
            if st.button("Sign In →", type="primary", use_container_width=True):
                route_to("login")
        
        if st.button("Create Free Account", use_container_width=True):
            route_to("signup")
        return
    
    modules = [
        {
            "id": "income",
            "title": "Income Sources",
            "description": "Social Security, pensions, etc.",
            "icon": "💰",
            "required": True,
            "visible_if": lambda: True,
            "unlock_if": lambda: True,
        },
        # ... more modules ...
    ]
    
    hub = ModuleHub(
        product_key="cost_planner_v2",
        modules=modules,
        base_route="?page=cost_v2&cost_module=",
        title="Financial Assessment",
    )
    hub.render()
```

### 5. Test It!

```bash
# Run app
streamlit run app.py

# Navigate to: http://localhost:8501/?page=cost_v2&cost_module=hub
```

---

## Module Structure Pattern

Every Cost Planner v2 module follows this structure:

```
modules/income/
  ├── module.json       # Manifest (questions, options, UI)
  ├── config.py         # Converts manifest to ModuleConfig
  └── logic.py          # derive_outcome(answers, context)
```

### Example: Income Module

`modules/income/module.json`:
```json
{
  "module": {
    "id": "income_sources",
    "name": "Income Sources",
    "version": "v1.0"
  },
  "sections": [
    {
      "id": "social_security",
      "title": "Social Security Income",
      "questions": [
        {
          "id": "ss_monthly_amount",
          "type": "currency",
          "label": "Monthly Social Security benefit",
          "required": true
        }
      ]
    }
  ]
}
```

`modules/income/config.py`:
```python
from core.modules.schema import ModuleConfig
from core.modules.base import load_module_manifest

def get_config() -> ModuleConfig:
    manifest = load_module_manifest("cost_planner_v2", "income")
    # Convert to ModuleConfig
    return ModuleConfig(
        product="cost_planner_v2",
        state_key="cost_planner_v2.income",
        version=manifest["module"]["version"],
        steps=_convert_sections(manifest["sections"]),
        outcomes_compute="products.cost_planner_v2.modules.income.logic:derive_outcome"
    )
```

`modules/income/logic.py`:
```python
from core.modules.schema import OutcomeContract

def derive_outcome(answers, context):
    total_income = (
        answers.get("ss_monthly_amount", 0) +
        answers.get("pension_monthly_amount", 0)
    )
    
    return OutcomeContract(
        recommendation=None,  # Not needed for financial modules
        flags={},
        domain_scores={"total_income": total_income},
        tags=["income_assessed"],
    )
```

---

## Testing Strategy

### Unit Tests
```python
# Test custom renderer registry
from core.modules import registry

def test_renderer():
    def my_renderer(config, step, idx, state):
        return {"test": "value"}
    
    registry.register_step_renderer("test", my_renderer)
    assert registry.has_step_renderer("test")
    
    renderer = registry.get_step_renderer("test")
    result = renderer(None, None, 0, {})
    assert result == {"test": "value"}

# Test module hub
from core.modules.hub import ModuleHub

def test_hub():
    hub = ModuleHub(
        product_key="test",
        modules=[{"id": "m1", "title": "M1"}],
        base_route="?test="
    )
    assert len(hub.get_visible_modules()) == 1
```

### Integration Tests
```python
# Test module loading
from core.modules.loader import load_product_module_config

def test_load_module():
    config = load_product_module_config("cost_planner_v2", "income")
    assert config.product == "cost_planner_v2"
    assert config.state_key == "cost_planner_v2.income"
```

### Manual Testing
1. Navigate to module hub: `?page=cost_v2&cost_module=hub`
2. Click on a module tile
3. Verify standard engine renders it
4. Complete module, check progress updates
5. Return to hub, see completion status

---

## Common Patterns

### Profile-Based Visibility
```python
def get_user_profile():
    profile = st.session_state.get("profile", {})
    return {
        "is_veteran": profile.get("is_veteran", False),
        "is_home_owner": profile.get("is_home_owner", False),
    }

modules = [
    {
        "id": "va_benefits",
        "visible_if": lambda: get_user_profile()["is_veteran"],
    }
]
```

### Prerequisite Locking
```python
def income_completed():
    state = st.session_state.get("cost_planner_v2.income", {})
    return state.get("progress", 0) >= 100

modules = [
    {
        "id": "assets",
        "unlock_if": lambda: income_completed(),
        "lock_msg": "Complete Income module first",
    }
]
```

### Progress Aggregation
```python
hub = ModuleHub(...)
hub.render()

# Check completion
required_done = hub.get_required_completed_count()
total_required = len([m for m in modules if m["required"]])

if hub.all_required_completed():
    st.button("Continue to Summary →")
```

---

## Troubleshooting

### Module Not Found
```
ImportError: Cannot import module config: products.cost_planner_v2.modules.income.config
```
**Fix**: Create `modules/income/config.py` with `get_config()` function

### Custom Renderer Not Called
```python
# Verify registration
from core.modules import registry
print(registry.list_registered_renderers())
# => ['quick_estimate', ...]

# Check step ID matches
config.steps[i].id == "quick_estimate"  # Must match exactly
```

### ModuleHub Shows No Modules
```python
# Check visibility functions
hub.get_visible_modules()  # Should return list

# Debug visibility
for module in modules:
    visible = module.get("visible_if", lambda: True)()
    print(f"{module['id']}: visible={visible}")
```

---

## Resources

- **Full Architecture**: `COST_PLANNER_V2_ARCHITECTURE.md`
- **Implementation Status**: `COST_PLANNER_V2_STATUS.md`
- **Module Spec**: `MODULE_ARCHITECTURE_SPEC.md`
- **GCP Reference**: `products/gcp/modules/care_recommendation/`

---

## Quick Commands

```bash
# Switch to feature branch
git checkout feature/cost_planner_v2

# Create new module
mkdir -p products/cost_planner_v2/modules/mymodule
touch products/cost_planner_v2/modules/mymodule/module.json
touch products/cost_planner_v2/modules/mymodule/config.py
touch products/cost_planner_v2/modules/mymodule/logic.py

# Run app
streamlit run app.py

# Commit changes
git add -A
git commit -m "feat: add mymodule"
```

---

**You're ready to build Cost Planner v2!** 🚀

Start with Phase 2: Create the product structure and see the 86% code reduction come to life.
