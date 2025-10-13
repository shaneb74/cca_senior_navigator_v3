# Cost Planner Architecture - Multi-Module Product

**Date:** October 12, 2025  
**Status:** Design Specification

---

## Overview

Cost Planner is a **multi-module product** with:
- **1 Base/Home Module** - Landing page, authentication gate, module router
- **8+ Sub-Modules** - Each calculating a specific cost/income component
- **Authentication Required** - Except for base and `recommendation_cost_detail`

---

## Architecture Pattern: Hub-and-Spoke

```
Cost Planner Product (Multi-Module)
│
├── Base Module (home/router)
│   ├── Welcome/intro screen
│   ├── Authentication check (mock for now)
│   ├── Module navigation/routing
│   └── Progress summary dashboard
│
└── Sub-Modules (each independent)
    ├── 1. Income Sources         (requires auth)
    ├── 2. Assets & Savings       (requires auth)
    ├── 3. Home Ownership         (requires auth)
    ├── 4. Insurance & Benefits   (requires auth)
    ├── 5. VA Benefits            (requires auth)
    ├── 6. Monthly Care Costs     (requires auth)
    ├── 7. Expense Adjustments    (requires auth)
    ├── 8. Projection Summary     (requires auth)
    └── 9. Recommendation Cost Detail (NO auth required)
```

---

## File Structure

```
products/cost_planner/
├── product.py                    # Product entry point & router
├── base_module_config.py         # Base/home module config
├── base_module_config.json       # Base module steps/fields
├── aggregator.py                 # Product-level outcome aggregation
├── auth.py                       # Mock authentication (future: real auth)
│
└── modules/                      # Individual calculation modules
    ├── income_sources/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py              # Calculate total income
    │
    ├── assets_savings/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py              # Calculate liquid assets
    │
    ├── home_ownership/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py              # Calculate home equity
    │
    ├── insurance_benefits/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py              # Calculate insurance coverage
    │
    ├── va_benefits/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py              # Calculate VA benefits
    │
    ├── monthly_care_costs/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py              # Calculate base care cost
    │
    ├── expense_adjustments/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py              # Calculate additional expenses
    │
    ├── projection_summary/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py              # Show timeline projection
    │
    └── recommendation_cost_detail/  # NO AUTH REQUIRED
        ├── module_config.py
        ├── module_config.json
        └── logic.py              # Show GCP recommendation cost breakdown
```

---

## Module Types

### Type 1: Base Module (Router/Gateway)

**Purpose:**
- Product landing page
- Authentication gate
- Module selection/navigation
- Progress dashboard

**Features:**
- Displays available modules as tiles
- Shows completion status for each module
- Enforces authentication before allowing sub-module access
- Allows "quick estimate" vs "full assessment" paths

**State Management:**
```python
st.session_state["cost"] = {
    "progress": 45,  # Overall product progress
    "auth_required": True,
    "auth_status": "authenticated",  # or "guest"
    "modules": {
        "income_sources": {
            "progress": 100,
            "status": "done",
            "outcome": {"total_income": 4500}
        },
        "assets_savings": {
            "progress": 0,
            "status": "new",
            "outcome": {}
        },
        # ... other modules
    }
}
```

### Type 2: Calculation Modules (Require Auth)

**Purpose:** Collect data and calculate specific financial component

**Examples:**
- `income_sources` → Calculate total monthly income
- `assets_savings` → Calculate liquid assets available
- `va_benefits` → Calculate VA benefit eligibility

**Pattern:** Same as GCP (uses `run_module()` with `ModuleConfig`)

**Returns:** `OutcomeContract` with domain-specific results

### Type 3: Public Modules (No Auth Required)

**Purpose:** Show information without requiring login

**Examples:**
- `recommendation_cost_detail` → Show typical costs for GCP recommendation tier
- Base module intro page → Landing/welcome

**Pattern:** Same module engine, but `auth.py` allows access

---

## Authentication Flow

### Mock Implementation (Phase 1)

```python
# products/cost_planner/auth.py
import streamlit as st
from typing import Dict, Any


def is_authenticated() -> bool:
    """Check if user is authenticated (mock for now)."""
    return st.session_state.get("auth", {}).get("is_authenticated", False)


def require_auth() -> bool:
    """Gate content behind authentication.
    
    Returns:
        True if authenticated, False if blocked
    """
    if is_authenticated():
        return True
    
    # Mock: Show auth requirement message
    st.warning("🔒 Authentication required to continue")
    st.markdown("""
    This module requires you to log in to save your progress and access personalized features.
    
    **For now (mock):** Click the button below to simulate login.
    """)
    
    if st.button("🔓 Mock Login (Dev Mode)", type="primary"):
        st.session_state.setdefault("auth", {})["is_authenticated"] = True
        st.rerun()
    
    return False


def mock_login_button():
    """Show mock login button in sidebar (dev mode)."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔧 Dev Tools")
        
        if is_authenticated():
            st.success("✓ Authenticated")
            if st.button("🔓 Mock Logout"):
                st.session_state["auth"]["is_authenticated"] = False
                st.rerun()
        else:
            st.info("Not authenticated")
            if st.button("🔒 Mock Login"):
                st.session_state.setdefault("auth", {})["is_authenticated"] = True
                st.rerun()


# Module-level auth check decorator
def requires_auth(module_key: str):
    """Decorator to require auth for specific modules."""
    PUBLIC_MODULES = ["base", "recommendation_cost_detail"]
    
    if module_key in PUBLIC_MODULES:
        return True  # No auth required
    
    return require_auth()
```

---

## Product Entry Point (`product.py`)

```python
# products/cost_planner/product.py
from typing import Optional
import streamlit as st

from core.modules.engine import run_module
from products.cost_planner import auth
from products.cost_planner.base_module_config import get_base_config
from layout import render_shell_end, render_shell_start


def render(module: Optional[str] = None) -> None:
    """Render Cost Planner product.
    
    Args:
        module: Specific module to render (e.g., "income_sources")
                If None, renders base/home module
    """
    render_shell_start("", active_route="cost")
    
    # Show mock login controls in sidebar (dev mode)
    auth.mock_login_button()
    
    # Determine which module to render
    target_module = st.query_params.get("cost_module", module)
    
    if not target_module or target_module == "base":
        # Render base/home module (router/dashboard)
        _render_base_module()
    else:
        # Render specific calculation module
        _render_sub_module(target_module)
    
    render_shell_end()


def _render_base_module() -> None:
    """Render base/home module (landing + router)."""
    config = get_base_config()
    
    # Base module doesn't require auth (landing page is public)
    module_state = run_module(config)


def _render_sub_module(module_key: str) -> None:
    """Render a specific calculation module."""
    # Check authentication
    if not auth.requires_auth(module_key):
        return  # Auth gate blocks rendering
    
    # Import module config dynamically
    try:
        module_path = f"products.cost_planner.modules.{module_key}.module_config"
        import importlib
        config_module = importlib.import_module(module_path)
        config = config_module.get_config()
    except ImportError:
        st.error(f"Module '{module_key}' not found")
        if st.button("← Back to Cost Planner Home"):
            st.query_params.clear()
            st.query_params["page"] = "cost"
            st.rerun()
        return
    
    # Run the module
    module_state = run_module(config)
```

---

## Base Module Configuration

### `base_module_config.json`

```json
{
  "product": "cost_planner",
  "state_key": "cost.base",
  "version": "2025.10.1",
  "steps": [
    {
      "id": "intro",
      "title": "Cost Planner",
      "subtitle": "Understand the true cost of care and plan for affordability.\n\nWe'll help you:\n• Calculate total monthly income\n• Assess available assets\n• Estimate care costs\n• Project timeline until asset depletion",
      "fields": [],
      "show_progress": false,
      "next_label": "Get Started"
    },
    {
      "id": "path_selection",
      "title": "Choose Your Path",
      "subtitle": "How detailed do you want to be?",
      "fields": [
        {
          "key": "assessment_path",
          "label": "Select your approach",
          "type": "radio",
          "required": true,
          "options": [
            {
              "label": "Quick Estimate (5 min)",
              "value": "quick",
              "help": "High-level estimate using your GCP recommendation"
            },
            {
              "label": "Full Assessment (15 min)",
              "value": "full",
              "help": "Detailed analysis with income, assets, and costs"
            }
          ]
        }
      ],
      "show_progress": false,
      "next_label": "Continue"
    },
    {
      "id": "module_dashboard",
      "title": "Cost Assessment Modules",
      "subtitle": "Complete each section to build your full financial picture.",
      "fields": [],
      "show_progress": false
    }
  ]
}
```

### `base_module_config.py`

```python
# products/cost_planner/base_module_config.py
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from core.modules.schema import FieldDef, ModuleConfig, StepDef


def _build_field(data: Dict[str, Any]) -> FieldDef:
    return FieldDef(
        key=data["key"],
        label=data["label"],
        type=data["type"],
        help=data.get("help"),
        required=data.get("required", False),
        options=data.get("options"),
        default=data.get("default"),
        visible_if=data.get("visible_if"),
    )


@lru_cache(maxsize=1)
def _load_config_payload() -> Dict[str, Any]:
    path = Path(__file__).with_name("base_module_config.json")
    with path.open() as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def get_base_config() -> ModuleConfig:
    """Load Cost Planner base/home module configuration."""
    payload = _load_config_payload()
    
    steps: List[StepDef] = []
    for step_data in payload.get("steps", []):
        fields = [_build_field(f) for f in step_data.get("fields", [])]
        
        # Special handling for module dashboard step
        if step_data["id"] == "module_dashboard":
            # This step will render module tiles dynamically
            # (see custom renderer in base module logic)
            pass
        
        steps.append(
            StepDef(
                id=step_data["id"],
                title=step_data["title"],
                subtitle=step_data.get("subtitle"),
                fields=fields,
                show_progress=step_data.get("show_progress", True),
                next_label=step_data.get("next_label", "Continue"),
            )
        )
    
    return ModuleConfig(
        product="cost_planner",
        state_key="cost.base",
        version=payload["version"],
        steps=steps,
        results_step_id=None,  # Base module doesn't have results
        outcomes_compute=None,  # No outcomes for base module
    )
```

---

## Module Routing & Navigation

### From Base Module to Sub-Modules

```python
# In base module's "module_dashboard" step custom renderer
# (injected via engine or custom step handler)

import streamlit as st
from core.product_tile import ProductTile

def render_module_tiles():
    """Render tiles for each sub-module."""
    cost_state = st.session_state.get("cost", {})
    modules_state = cost_state.get("modules", {})
    
    # Define all calculation modules
    MODULE_REGISTRY = [
        {
            "key": "income_sources",
            "title": "Income Sources",
            "desc": "Monthly income from all sources",
            "icon": "💰",
            "order": 1,
            "required": True,
        },
        {
            "key": "assets_savings",
            "title": "Assets & Savings",
            "desc": "Liquid assets and retirement accounts",
            "icon": "🏦",
            "order": 2,
            "required": True,
        },
        {
            "key": "home_ownership",
            "title": "Home Ownership",
            "desc": "Home equity and sale timeline",
            "icon": "🏠",
            "order": 3,
            "required": False,
        },
        # ... more modules
    ]
    
    for module_def in MODULE_REGISTRY:
        module_state = modules_state.get(module_def["key"], {})
        progress = module_state.get("progress", 0)
        status = module_state.get("status", "new")
        
        ProductTile(
            key=f"cost_module_{module_def['key']}",
            title=f"{module_def['icon']} {module_def['title']}",
            desc=module_def["desc"],
            meta=["Required"] if module_def["required"] else ["Optional"],
            cta="Start" if progress == 0 else "Continue",
            progress=progress,
            go=f"cost?cost_module={module_def['key']}",  # Route to sub-module
        ).render()
```

### From Sub-Module Back to Base

```python
# In sub-module results/completion
if st.button("← Back to Cost Planner"):
    st.query_params.clear()
    st.query_params["page"] = "cost"  # Routes to base module
    st.rerun()
```

---

## Product-Level Progress Aggregation

### `aggregator.py`

```python
# products/cost_planner/aggregator.py
from typing import Any, Dict
from core.modules.schema import OutcomeContract


def aggregate_product_outcomes(modules: Dict[str, Any]) -> OutcomeContract:
    """Aggregate all Cost Planner module outcomes into product-level result.
    
    Args:
        modules: Dict of module states, each with "outcome" key
    
    Returns:
        OutcomeContract with affordability recommendation
    """
    # Extract outcomes from completed modules
    income_outcome = modules.get("income_sources", {}).get("outcome", {})
    assets_outcome = modules.get("assets_savings", {}).get("outcome", {})
    costs_outcome = modules.get("monthly_care_costs", {}).get("outcome", {})
    
    # Calculate totals
    total_income = income_outcome.get("domain_scores", {}).get("total_income", 0)
    liquid_assets = assets_outcome.get("domain_scores", {}).get("liquid_assets", 0)
    monthly_care_cost = costs_outcome.get("domain_scores", {}).get("monthly_care_cost", 0)
    
    # Calculate affordability
    monthly_deficit = max(0, monthly_care_cost - total_income)
    
    if monthly_deficit == 0:
        months_until_depletion = 999
    else:
        months_until_depletion = liquid_assets / monthly_deficit if monthly_deficit > 0 else 0
    
    # Determine recommendation tier
    if months_until_depletion > 60:
        recommendation = "affordable"
        flags = {}
    elif months_until_depletion > 24:
        recommendation = "at_risk"
        flags = {"financial_planning_needed": True}
    else:
        recommendation = "unsustainable"
        flags = {
            "urgent_financial_planning": True,
            "va_benefits_check": True,
            "medicaid_eligible_check": True,
        }
    
    return OutcomeContract(
        recommendation=recommendation,
        flags=flags,
        domain_scores={
            "total_income": total_income,
            "liquid_assets": liquid_assets,
            "monthly_care_cost": monthly_care_cost,
            "monthly_deficit": monthly_deficit,
            "months_until_depletion": months_until_depletion,
        },
        tags=["affordability_assessed", "multi_module_aggregation"],
    )
```

---

## State Management

### Product-Level State
```python
st.session_state["cost"] = {
    "progress": 45,  # Calculated from module completion
    "outcome": {},   # Set when all required modules complete
    "modules": {
        "income_sources": {
            "progress": 100,
            "status": "done",
            "outcome": {...}
        },
        "assets_savings": {
            "progress": 50,
            "status": "doing",
            "outcome": {}
        },
        # ... other modules
    }
}
```

### Module-Level State
```python
st.session_state["cost.income_sources"] = {
    "progress": 100,
    "status": "done",
    "monthly_income": 3000,
    "ss_benefits": 1200,
    "pension": 800,
    "flags": {},
    "_outcomes": {
        "recommendation": "sufficient_income",
        "flags": {},
        "domain_scores": {
            "total_income": 5000
        }
    }
}
```

---

## Implementation Phases

### Phase 1: Base Module + Mock Auth ✅ Ready to Build
1. Create `products/cost_planner/` structure
2. Implement `auth.py` with mock authentication
3. Implement `product.py` router
4. Implement `base_module_config.py/json`
5. Test: Landing page, path selection, mock login

### Phase 2: First Calculation Module
1. Create `modules/income_sources/`
2. Implement module config + logic
3. Test: Auth gate, module rendering, back navigation
4. Verify: State isolation between modules

### Phase 3: Remaining Modules
1. Clone `income_sources` for each new module
2. Customize fields and logic per module
3. Test: Module independence, progress tracking

### Phase 4: Product Aggregation
1. Implement `aggregator.py`
2. Calculate product-level progress from modules
3. Set product outcome when all required modules complete
4. Test: Flag triggering for additional services

### Phase 5: Public Module (Recommendation Cost Detail)
1. Create `modules/recommendation_cost_detail/`
2. Allow access without auth
3. Pull GCP recommendation from handoff
4. Display typical cost ranges

---

## Key Differences from GCP

| Aspect | GCP (Single-Module) | Cost Planner (Multi-Module) |
|--------|---------------------|----------------------------|
| **Structure** | One module config | Base module + 8+ sub-modules |
| **Routing** | Direct to module | Base → sub-module routing |
| **Progress** | Single progress bar | Product-level + module-level |
| **Authentication** | Not required | Required (except 2 modules) |
| **Outcomes** | Single calculation | Aggregated from modules |
| **State Keys** | `"gcp"` | `"cost"` + `"cost.MODULE_NAME"` |
| **Navigation** | Linear steps | Hub-and-spoke |

---

## Navigation Flow Examples

### Example 1: User Starts Cost Planner
```
1. Click "Cost Planner" tile in hub
2. Routes to: ?page=cost
3. Renders: Base module intro
4. User clicks "Get Started"
5. Sees: Path selection (quick vs full)
6. User selects "Full Assessment"
7. Sees: Module dashboard with 8 tiles
```

### Example 2: User Starts Income Module
```
1. Clicks "Income Sources" tile
2. Routes to: ?page=cost&cost_module=income_sources
3. Auth check: Not authenticated
4. Shows: Mock login prompt
5. User clicks "Mock Login"
6. Auth check: Passes
7. Renders: Income sources module (3 steps)
8. User completes questions
9. Module calculates: total_income = $5000
10. User clicks "Back to Cost Planner"
11. Routes to: ?page=cost (base module dashboard)
12. Income Sources tile shows: 100% complete
```

### Example 3: Guest Views Recommendation Cost Detail
```
1. User completes GCP (not authenticated)
2. GCP recommends: "Assisted Living"
3. Additional services tile appears: "Cost Breakdown"
4. User clicks tile
5. Routes to: ?page=cost&cost_module=recommendation_cost_detail
6. Auth check: Public module, auth NOT required
7. Shows: Typical costs for Assisted Living
   - Base monthly cost: $4,500-$6,000
   - Memory care add-on: +$1,500
   - Level 2 care: +$800
8. No financial data collected (public info only)
```

---

## Testing Checklist

### Base Module
- [ ] Intro page loads
- [ ] Path selection works
- [ ] Module dashboard renders
- [ ] Tiles route to sub-modules
- [ ] Mock login appears in sidebar

### Authentication
- [ ] Mock login sets `auth.is_authenticated = True`
- [ ] Auth gate blocks protected modules
- [ ] Auth gate allows public modules
- [ ] Mock logout clears auth state

### Sub-Module
- [ ] Auth gate works before rendering
- [ ] Module loads with correct config
- [ ] State isolated per module
- [ ] Outcomes written to module state
- [ ] Back navigation returns to base

### Product Aggregation
- [ ] Product progress = avg(module progress)
- [ ] All required modules → product outcome calculated
- [ ] Flags from modules → additional services

---

## Next Steps

Ready to implement? Start with:

1. **Create folder structure** (see "File Structure" above)
2. **Copy `auth.py` template** (mock authentication)
3. **Copy `product.py` template** (router)
4. **Copy `base_module_config.py/json` templates** (landing + dashboard)
5. **Test base module** before building sub-modules

Then follow NEW_PRODUCT_QUICKSTART.md for each sub-module.

---

**Questions or ready to start coding?** 🚀
