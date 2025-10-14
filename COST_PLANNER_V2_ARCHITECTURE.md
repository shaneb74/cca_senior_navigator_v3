# Cost Planner v2 Architecture

## Vision

Rebuild Cost Planner using extended module engine capabilities to achieve:
- **83% code reduction** (1,160 lines → ~200 lines in product.py)
- **Standardized patterns** (leverage module engine for all flows)
- **Reusable components** (ModuleHub, custom renderers)
- **Clean separation** (router, modules, aggregation, results)

---

## Architecture Principles

### 1. Extend, Don't Bypass
Instead of bypassing the module engine with custom rendering, **extend it** to handle Cost Planner's legitimate needs:
- Custom step renderers for unique UI requirements
- Sub-hub abstraction for module selection
- Multi-module aggregation for financial calculations

### 2. Standard Module Contract
Every Cost Planner sub-module follows the same pattern as GCP:
- `module.json` manifest (metadata, sections, questions)
- `logic.py` with `derive_outcome(answers, context) -> OutcomeContract`
- Managed by `core.modules.engine.run_module()`

### 3. Composition Over Duplication
- ModuleHub component for displaying sub-module tiles
- Custom renderer registry for special-case UI
- Aggregator pattern for combining outcomes

---

## New File Structure

```
products/
  └── cost_planner_v2/
      ├── __init__.py
      ├── product.py                    # Router only (~100 lines)
      ├── hub.py                        # Module dashboard
      ├── auth.py                       # Auth utilities (reuse existing)
      ├── aggregator.py                 # Multi-module outcome aggregation
      ├── profile.py                    # User profile flags management
      └── modules/
          ├── quick_estimate/
          │   ├── module.json           # Quick cost comparison
          │   ├── logic.py
          │   └── widgets.py            # Care type selector widget
          ├── income/
          │   ├── module.json
          │   └── logic.py
          ├── assets/
          │   ├── module.json
          │   └── logic.py
          ├── insurance/
          │   ├── module.json
          │   └── logic.py
          ├── va_benefits/
          │   ├── module.json
          │   └── logic.py
          ├── housing/
          │   ├── module.json
          │   └── logic.py
          ├── medicaid/
          │   ├── module.json
          │   └── logic.py
          └── summary/
              ├── module.json           # Expert review + timeline
              ├── logic.py              # Uses aggregator
              └── renderers.py          # Custom results rendering

core/
  └── modules/
      ├── engine.py                     # ✨ Enhanced with custom renderers
      ├── hub.py                        # ✨ NEW: ModuleHub component
      ├── registry.py                   # ✨ NEW: Custom renderer registry
      └── loader.py                     # ✨ NEW: Module discovery utilities
```

---

## Core Engine Extensions

### 1. Custom Step Renderer Registry

**File:** `core/modules/registry.py`

```python
"""Registry for custom step renderers.

Allows products to register custom rendering functions for specific steps
while keeping navigation/state management in the module engine.
"""

from typing import Any, Callable, Dict, Optional

# Type alias for renderer function
StepRenderer = Callable[[Any, Any, int, Dict[str, Any]], Optional[Dict[str, Any]]]

_CUSTOM_RENDERERS: Dict[str, StepRenderer] = {}


def register_step_renderer(step_id: str, renderer: StepRenderer) -> None:
    """Register a custom renderer for a step ID.
    
    Args:
        step_id: Unique identifier for the step type
        renderer: Function with signature (config, step, step_index, state) -> state_updates
    """
    _CUSTOM_RENDERERS[step_id] = renderer


def get_step_renderer(step_id: str) -> Optional[StepRenderer]:
    """Get custom renderer for a step ID.
    
    Args:
        step_id: Step identifier
    
    Returns:
        Renderer function or None if not registered
    """
    return _CUSTOM_RENDERERS.get(step_id)


def clear_registry() -> None:
    """Clear all registered renderers (for testing)."""
    _CUSTOM_RENDERERS.clear()
```

**Changes to `core/modules/engine.py`:**

```python
from core.modules import registry

def run_module(config: ModuleConfig) -> Dict[str, Any]:
    # ... existing setup ...
    
    step = config.steps[step_index]
    
    # Check for custom renderer
    custom_renderer = registry.get_step_renderer(step.id)
    if custom_renderer:
        # Custom renderer handles UI and returns state updates
        state_updates = custom_renderer(config, step, step_index, state)
        if state_updates:
            state.update(state_updates)
        return state
    
    # Otherwise use standard rendering
    # ... existing code ...
```

### 2. ModuleHub Component

**File:** `core/modules/hub.py`

```python
"""Module hub component for displaying sub-module selection dashboard."""

from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from core.product_tile import ModuleTileCompact


class ModuleHub:
    """Dashboard for selecting and navigating between product sub-modules.
    
    Displays tiles for each module with:
    - Progress tracking
    - Conditional visibility based on profile
    - Lock/unlock logic
    - Navigation to module pages
    """
    
    def __init__(
        self,
        product_key: str,
        modules: List[Dict[str, Any]],
        base_route: str,
        title: str = "Select a Module",
        subtitle: Optional[str] = None,
    ):
        """Initialize module hub.
        
        Args:
            product_key: Product identifier (e.g., "cost_planner")
            modules: List of module definitions with keys:
                - id: Module identifier
                - title: Display title
                - description: Short description
                - icon: Emoji or icon
                - required: Whether module is required
                - visible_if: Callable returning bool for visibility
                - unlock_if: Callable returning bool for unlocked state
                - lock_msg: Message to show when locked
            base_route: Base URL for module navigation (e.g., "?page=cost&cost_module=")
            title: Hub title
            subtitle: Optional subtitle/instructions
        """
        self.product_key = product_key
        self.modules = modules
        self.base_route = base_route
        self.title = title
        self.subtitle = subtitle
    
    def render(self) -> None:
        """Render the module hub with tiles."""
        st.markdown(f"### {self.title}")
        if self.subtitle:
            st.caption(self.subtitle)
        
        # Filter visible modules
        visible_modules = [
            m for m in self.modules
            if m.get("visible_if", lambda: True)()
        ]
        
        if not visible_modules:
            st.warning("No modules available. Please update your profile.")
            return
        
        # Calculate required vs optional counts
        required_count = len([m for m in visible_modules if m.get("required", False)])
        
        st.caption(
            f"📊 {required_count} required module{'s' if required_count != 1 else ''} • "
            f"{len(visible_modules) - required_count} optional"
        )
        
        st.markdown("---")
        
        # Render tiles in 2-column grid
        for i in range(0, len(visible_modules), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(visible_modules):
                    module = visible_modules[i + j]
                    with col:
                        self._render_module_tile(module)
        
        st.markdown("---")
    
    def _render_module_tile(self, module: Dict[str, Any]) -> None:
        """Render a single module tile.
        
        Args:
            module: Module definition dict
        """
        module_id = module["id"]
        state_key = f"{self.product_key}.{module_id}"
        
        # Get progress from session state
        module_state = st.session_state.get(state_key, {})
        progress = float(module_state.get("progress", 0))
        
        # Check if locked
        is_locked = not module.get("unlock_if", lambda: True)()
        lock_msg = module.get("lock_msg", "Complete required modules first")
        
        # Create tile
        tile = ModuleTileCompact(
            key=module_id,
            title=f"{module.get('icon', '📄')} {module['title']}",
            blurb=module.get("description"),
            progress=progress,
            locked=is_locked,
            lock_msg=lock_msg,
            primary_route=f"{self.base_route}{module_id}",
            badge_text="Required" if module.get("required") else None,
        )
        tile.render()
```

### 3. Module Discovery Utilities

**File:** `core/modules/loader.py`

```python
"""Utilities for discovering and loading product modules."""

import importlib
from pathlib import Path
from typing import List, Optional
from core.modules.schema import ModuleConfig


def discover_product_modules(product: str) -> List[str]:
    """Discover available module names for a product.
    
    Args:
        product: Product identifier (e.g., "cost_planner_v2")
    
    Returns:
        List of module directory names
    """
    modules_dir = Path(__file__).parent.parent.parent / "products" / product / "modules"
    
    if not modules_dir.exists():
        return []
    
    return [
        d.name for d in modules_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".")
    ]


def load_product_module_config(product: str, module: str) -> ModuleConfig:
    """Load configuration for a product sub-module.
    
    Args:
        product: Product identifier
        module: Module identifier
    
    Returns:
        ModuleConfig instance
    
    Raises:
        ImportError: If module cannot be loaded
        AttributeError: If module doesn't have get_config()
    """
    module_path = f"products.{product}.modules.{module}.config"
    config_module = importlib.import_module(module_path)
    
    if not hasattr(config_module, "get_config"):
        raise AttributeError(
            f"Module {module_path} must define get_config() -> ModuleConfig"
        )
    
    return config_module.get_config()


def load_product_module_manifest(product: str, module: str) -> dict:
    """Load JSON manifest for a product sub-module.
    
    Args:
        product: Product identifier
        module: Module identifier
    
    Returns:
        Dict with module manifest data
    """
    import json
    
    manifest_path = (
        Path(__file__).parent.parent.parent
        / "products" / product / "modules" / module / "module.json"
    )
    
    with manifest_path.open() as f:
        return json.load(f)
```

---

## Cost Planner v2 Implementation

### Product Router

**File:** `products/cost_planner_v2/product.py`

```python
"""Cost Planner v2 - Simplified router using extended module engine."""

from typing import Optional
import streamlit as st

from core.modules.engine import run_module
from core.modules.loader import load_product_module_config
from core.nav import route_to
from layout import render_shell_end, render_shell_start
from products.cost_planner_v2 import auth, hub


def render(module: Optional[str] = None) -> None:
    """Render Cost Planner v2 product.
    
    Routes to:
    - Quick Estimate (public, no auth)
    - Module Hub (after auth)
    - Individual modules (income, assets, etc.)
    - Summary (expert review + financial timeline)
    
    Args:
        module: Optional module key to render directly
    """
    render_shell_start("", active_route="cost")
    
    # Dev mode auth controls
    auth.mock_login_button()
    
    # Check GCP requirement
    if not _check_gcp_completed():
        _render_gcp_gate()
        render_shell_end()
        return
    
    # Determine target module from query params or argument
    target_module = st.query_params.get("cost_module", module)
    
    # Route to appropriate view
    if not target_module or target_module == "hub":
        # Show module selection hub
        hub.render_module_hub()
    elif target_module == "quick_estimate":
        # Public quick estimate (no auth required)
        _render_quick_estimate()
    else:
        # Load and render sub-module
        _render_sub_module(target_module)
    
    render_shell_end()


def _check_gcp_completed() -> bool:
    """Check if GCP has been completed (required dependency)."""
    gcp_state = st.session_state.get("gcp", {})
    
    # If state is empty, we're still loading
    if not gcp_state:
        return True  # Don't block on first render
    
    # Check progress
    return float(gcp_state.get("progress", 0)) >= 100


def _render_gcp_gate() -> None:
    """Show requirement to complete GCP first."""
    st.warning("⚠️ **Guided Care Plan Required**")
    st.markdown(
        """
        The Cost Planner depends on your personalized care recommendation.
        
        **Please complete the Guided Care Plan first** to:
        - Get your personalized care recommendation
        - See accurate cost estimates for your situation
        - Access the full Cost Planner features
        """
    )
    
    if st.button("← Go to Guided Care Plan", type="primary"):
        route_to("gcp")


def _render_quick_estimate() -> None:
    """Render quick estimate module (public, no auth)."""
    try:
        config = load_product_module_config("cost_planner_v2", "quick_estimate")
        run_module(config)
    except ImportError:
        st.error("❌ Quick Estimate module not yet implemented")


def _render_sub_module(module_key: str) -> None:
    """Render a specific calculation sub-module.
    
    Args:
        module_key: Module identifier (e.g., "income", "assets")
    """
    # Check authentication
    if not auth.check_module_access(module_key):
        return  # Auth gate displayed
    
    # Load module config
    try:
        config = load_product_module_config("cost_planner_v2", module_key)
    except ImportError:
        st.warning(f"⚠️ Module '{module_key}' is not yet implemented")
        st.info(
            f"""
            **Coming Soon**
            
            The **{module_key.replace('_', ' ').title()}** module is planned for Phase 2.
            
            Return to the Module Hub to explore available modules.
            """
        )
        if st.button("← Back to Module Hub"):
            st.query_params["cost_module"] = "hub"
            st.rerun()
        return
    except Exception as e:
        st.error(f"❌ Error loading module '{module_key}'")
        st.exception(e)
        return
    
    # Add navigation breadcrumb
    if st.button("← Back to Module Hub", key="_back_to_hub"):
        st.query_params["cost_module"] = "hub"
        st.rerun()
    
    st.divider()
    
    # Run module through standard engine
    run_module(config)


def register() -> dict:
    """Register Cost Planner v2 with the application."""
    return {
        "routes": {
            "cost_v2": render,
        },
        "tile": {
            "key": "cost_planner_v2",
            "title": "Cost Planner v2",
            "meta": ["≈15 min", "Requires GCP"],
            "progress_key": "cost_planner_v2.progress",
            "unlock_condition": lambda ss: ss.get("gcp", {}).get("progress", 0) >= 100,
        },
    }
```

**Total lines: ~120** (vs. 1,160 in v1)

### Module Hub

**File:** `products/cost_planner_v2/hub.py`

```python
"""Module selection hub for Cost Planner v2."""

import streamlit as st
from core.modules.hub import ModuleHub
from core.nav import route_to
from products.cost_planner_v2.profile import get_user_profile


def render_module_hub() -> None:
    """Render the Cost Planner module selection dashboard."""
    st.markdown("### 💰 Cost Planner")
    st.caption("Complete your financial assessment to get personalized cost estimates.")
    
    st.markdown("---")
    
    # Get user profile for conditional visibility
    profile = get_user_profile()
    
    # Define all modules with visibility logic
    modules = [
        {
            "id": "income",
            "title": "Income Sources",
            "description": "Social Security, pensions, and other monthly income",
            "icon": "💰",
            "required": True,
            "visible_if": lambda: True,
            "unlock_if": lambda: True,
        },
        {
            "id": "assets",
            "title": "Assets & Savings",
            "description": "Bank accounts, investments, and liquid assets",
            "icon": "🏦",
            "required": True,
            "visible_if": lambda: True,
            "unlock_if": lambda: True,
        },
        {
            "id": "insurance",
            "title": "Insurance Coverage",
            "description": "Medicare, supplemental, and long-term care insurance",
            "icon": "🏥",
            "required": True,
            "visible_if": lambda: True,
            "unlock_if": lambda: True,
        },
        {
            "id": "va_benefits",
            "title": "VA Benefits",
            "description": "Veterans benefits and Aid & Attendance eligibility",
            "icon": "🎖️",
            "required": False,
            "visible_if": lambda: profile.get("is_veteran", False),
            "unlock_if": lambda: True,
        },
        {
            "id": "housing",
            "title": "Housing & Home Equity",
            "description": "Home value, mortgage, and housing-related costs",
            "icon": "🏡",
            "required": False,
            "visible_if": lambda: profile.get("is_home_owner", False),
            "unlock_if": lambda: True,
        },
        {
            "id": "medicaid",
            "title": "Medicaid Planning",
            "description": "Medicaid eligibility and spend-down strategies",
            "icon": "🏛️",
            "required": False,
            "visible_if": lambda: profile.get("considering_medicaid", False),
            "unlock_if": lambda: True,
        },
    ]
    
    # Create and render hub
    hub = ModuleHub(
        product_key="cost_planner_v2",
        modules=modules,
        base_route="?page=cost_v2&cost_module=",
        title="Financial Assessment Modules",
        subtitle="Complete the required modules to generate your personalized cost estimate.",
    )
    hub.render()
    
    # Show summary section when enough modules completed
    completed_required = _count_completed_required_modules(modules)
    total_required = len([m for m in modules if m.get("required")])
    
    if completed_required >= total_required:
        st.success(f"✅ All {total_required} required modules completed!")
        if st.button("Continue to Expert Review →", type="primary", use_container_width=True):
            st.query_params["cost_module"] = "summary"
            st.rerun()
    else:
        st.info(
            f"📊 Progress: {completed_required}/{total_required} required modules completed"
        )
    
    st.markdown("---")
    
    # Navigation
    if st.button("← Back to Concierge Hub", use_container_width=True):
        route_to("hub_concierge")


def _count_completed_required_modules(modules: list) -> int:
    """Count how many required modules have been completed."""
    count = 0
    for module in modules:
        if not module.get("required"):
            continue
        if not module.get("visible_if", lambda: True)():
            continue
        
        state_key = f"cost_planner_v2.{module['id']}"
        module_state = st.session_state.get(state_key, {})
        if float(module_state.get("progress", 0)) >= 100:
            count += 1
    
    return count
```

---

## Implementation Plan

### Phase 1: Core Extensions (Week 1)
- [ ] `core/modules/registry.py` - Custom renderer registry
- [ ] `core/modules/hub.py` - ModuleHub component
- [ ] `core/modules/loader.py` - Module discovery utilities
- [ ] Update `core/modules/engine.py` to support custom renderers
- [ ] Unit tests for all core extensions

### Phase 2: Product Structure (Week 1)
- [ ] `products/cost_planner_v2/product.py` - Simplified router
- [ ] `products/cost_planner_v2/hub.py` - Module hub implementation
- [ ] `products/cost_planner_v2/profile.py` - User profile management
- [ ] `products/cost_planner_v2/auth.py` - Copy from v1, adapt
- [ ] `products/cost_planner_v2/aggregator.py` - Copy from v1, adapt

### Phase 3: Quick Estimate Module (Week 2)
- [ ] `modules/quick_estimate/module.json` - Manifest
- [ ] `modules/quick_estimate/config.py` - Config loader
- [ ] `modules/quick_estimate/logic.py` - Cost estimation logic
- [ ] `modules/quick_estimate/widgets.py` - Care type selector widget
- [ ] Register custom renderer for care type comparison

### Phase 4: Financial Modules (Weeks 3-4)
- [ ] Income module (manifest + logic)
- [ ] Assets module (manifest + logic)
- [ ] Insurance module (manifest + logic)
- [ ] VA Benefits module (manifest + logic)
- [ ] Housing module (manifest + logic)
- [ ] Medicaid module (manifest + logic)

### Phase 5: Summary & Aggregation (Week 5)
- [ ] Summary module (expert review + timeline)
- [ ] Update aggregator to publish OutcomeContract
- [ ] MCIP handoff for affordability recommendation
- [ ] Product-level progress tracking

### Phase 6: Navigation & Testing (Week 6)
- [ ] Update `config/nav.json` for cost_v2 route
- [ ] Create hub tile configuration
- [ ] End-to-end testing
- [ ] Documentation

---

## Success Metrics

### Code Quality
- ✅ Product router: 120 lines (vs. 1,160)
- ✅ All modules follow standard manifest pattern
- ✅ Zero custom navigation logic in modules
- ✅ Reusable ModuleHub component

### User Experience
- ✅ Quick Estimate accessible without auth
- ✅ Conditional module visibility based on profile
- ✅ Progress tracking across all modules
- ✅ Resume functionality for all modules
- ✅ Clear navigation breadcrumbs

### Technical Debt
- ✅ No manual step index manipulation
- ✅ No duplicated navigation logic
- ✅ Proper outcomes publishing to MCIP
- ✅ Standard autosave across all modules

---

## Migration Path

### Running Both Versions
During development, both v1 and v2 will coexist:
- v1: `?page=cost` (existing implementation)
- v2: `?page=cost_v2` (new implementation)

### Feature Flag
Once v2 is stable:
```python
# In config or environment
USE_COST_PLANNER_V2 = os.getenv("COST_PLANNER_V2", "false") == "true"

# In navigation
if USE_COST_PLANNER_V2:
    route = "cost_v2"
else:
    route = "cost"
```

### Cutover Plan
1. Complete v2 development and testing
2. Run both versions in staging for 1 week
3. Enable v2 for 25% of users
4. Monitor for issues
5. Gradually increase to 100%
6. Deprecate v1 after 2 weeks of stable v2

---

## Open Questions

1. **Authentication Strategy**: Keep mock auth or implement real OAuth?
2. **State Migration**: Should v1 state be migrated to v2 format?
3. **Module Order**: Enforce order or allow free navigation?
4. **Partial Saves**: Auto-save on each answer or on Continue?
5. **Expert Review**: Custom rendering or standard results section?

---

## Next Steps

1. ✅ Create feature branch
2. ⏳ Implement core extensions (registry, hub, loader)
3. ⏳ Build simplified product router
4. ⏳ Create first module (quick_estimate)
5. ⏳ Validate pattern with one financial module
6. ⏳ Scale to remaining modules

---

**Status**: Ready for implementation
**Branch**: `feature/cost_planner_v2`
**Target**: Production-ready in 6 weeks
