# Cost Planner vs GCP - Architecture Comparison

**Visual guide showing the difference between single-module and multi-module products**

---

## GCP (Single-Module Product)

### Structure
```
┌─────────────────────────────────────┐
│  GCP Product                        │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ care_recommendation Module    │ │
│  │                               │ │
│  │  Steps:                       │ │
│  │  1. Intro                     │ │
│  │  2. Demographics              │ │
│  │  3. Health Status             │ │
│  │  4. Living Situation          │ │
│  │  5. Support System            │ │
│  │  6. Results                   │ │
│  │                               │ │
│  │  Outcome: Care Tier           │ │
│  │  Flags: meds_mgmt, fall_risk  │ │
│  └───────────────────────────────┘ │
│                                     │
│  State: st.session_state["gcp"]    │
└─────────────────────────────────────┘
```

### Flow
```
User Journey:
  Hub → GCP Tile Click → care_recommendation Module (linear 6 steps) → Results → Back to Hub
  
State:
  st.session_state["gcp"] = {
    "progress": 85,
    "status": "doing",
    "recipient_name": "Mom",
    "help_overall": "...",
    ...all answers...,
    "_outcomes": {
      "recommendation": "assisted_living",
      "flags": {"meds_management_needed": True}
    }
  }
```

### Files
```
products/gcp/
├── product.py           # Entry point → run_module(config)
├── module_config.py     # Config loader
├── module_config.json   # 6 steps definition
└── logic.py             # derive_outcomes() → care tier
```

---

## Cost Planner (Multi-Module Product)

### Structure
```
┌─────────────────────────────────────────────────────────────────┐
│  Cost Planner Product                                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ BASE Module (Router/Dashboard)                            │ │
│  │                                                           │ │
│  │  Steps:                                                   │ │
│  │  1. Intro                                                 │ │
│  │  2. Path Selection (Quick vs Full)                       │ │
│  │  3. Module Dashboard ───────────────────┐                │ │
│  │                                          │                │ │
│  │  NO Authentication Required              │                │ │
│  └──────────────────────────────────────────┼────────────────┘ │
│                                             │                  │
│  ┌──────────────────────────────────────────┼────────────────┐ │
│  │ Sub-Modules (8 independent modules)      │                │ │
│  │                                          │                │ │
│  │  ┌────────────────────┐  🔒 Auth Required (6 modules)   │ │
│  │  │ 1. Income Sources  │───────────────────────────────── │ │
│  │  │    → total_income  │                                  │ │
│  │  └────────────────────┘                                  │ │
│  │  ┌────────────────────┐                                  │ │
│  │  │ 2. Assets/Savings  │  Each module has:               │ │
│  │  │    → liquid_assets │  • 3-5 steps                    │ │
│  │  └────────────────────┘  • Own state key                │ │
│  │  ┌────────────────────┐  • Own outcome                  │ │
│  │  │ 3. Home Ownership  │  • Back to dashboard nav        │ │
│  │  │    → home_equity   │                                  │ │
│  │  └────────────────────┘                                  │ │
│  │  ┌────────────────────┐                                  │ │
│  │  │ 4. Insurance       │                                  │ │
│  │  │    → coverage      │                                  │ │
│  │  └────────────────────┘                                  │ │
│  │  ┌────────────────────┐                                  │ │
│  │  │ 5. VA Benefits     │                                  │ │
│  │  │    → va_amount     │                                  │ │
│  │  └────────────────────┘                                  │ │
│  │  ┌────────────────────┐                                  │ │
│  │  │ 6. Care Costs      │                                  │ │
│  │  │    → monthly_cost  │                                  │ │
│  │  └────────────────────┘                                  │ │
│  │                                                           │ │
│  │  ┌────────────────────┐  🌐 NO Auth (2 public modules)  │ │
│  │  │ 7. Rec Cost Detail │───────────────────────────────  │ │
│  │  │    (public view)   │                                  │ │
│  │  └────────────────────┘                                  │ │
│  │  ┌────────────────────┐                                  │ │
│  │  │ 8. Quick Estimate  │  (not yet built)                │ │
│  │  └────────────────────┘                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Aggregator                                              │ │
│  │  Combines outcomes from modules 1-6                     │ │
│  │  → Product Outcome: "affordable" | "at_risk" | "..."   │ │
│  │  → Product Flags: financial_planning_needed, etc.      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  State: st.session_state["cost"] (product-level)             │
│         st.session_state["cost.MODULE"] (per-module)         │
└─────────────────────────────────────────────────────────────┘
```

### Flow
```
User Journey (Authenticated Path):
  Hub 
    → Cost Planner Tile Click 
    → Base Module (intro + dashboard)
    → User clicks "Income Sources" tile
    → Auth Check: Not authenticated
    → Mock Login Prompt
    → User clicks "Mock Login"
    → Income Sources Module (3 steps)
    → Module calculates: total_income = $5000
    → Back to dashboard
    → Income tile shows 100% complete
    → User clicks next module...
    → After all required modules complete
    → Aggregator calculates product outcome
    → Back to Hub (shows affordability result)

User Journey (Guest Path):
  Hub
    → GCP Complete (recommendation: "Assisted Living")
    → Additional Services tile appears: "Cost Breakdown"
    → Click tile
    → Routes to: recommendation_cost_detail module
    → Auth Check: Public module, NO auth required
    → Shows typical costs for Assisted Living
    → No personal data collected
```

### State Structure
```javascript
// Product-level state
st.session_state["cost"] = {
  "progress": 62,  // Calculated: avg of module progress
  "outcome": {
    "recommendation": "at_risk",
    "flags": {"financial_planning_needed": true},
    "domain_scores": {
      "total_income": 5000,
      "monthly_care_cost": 6500,
      "months_until_depletion": 36
    }
  },
  "modules": {
    "income_sources": {"progress": 100, "status": "done"},
    "assets_savings": {"progress": 100, "status": "done"},
    "home_ownership": {"progress": 0, "status": "new"},
    // ... other modules
  }
}

// Module-level states (independent)
st.session_state["cost.income_sources"] = {
  "progress": 100,
  "status": "done",
  "monthly_income": 3000,
  "ss_benefits": 1500,
  "pension": 500,
  "_outcomes": {
    "recommendation": "sufficient_income",
    "domain_scores": {"total_income": 5000}
  }
}

st.session_state["cost.assets_savings"] = {
  "progress": 100,
  "status": "done",
  "liquid_assets": 250000,
  "retirement_accounts": 150000,
  "_outcomes": {
    "domain_scores": {"liquid_assets": 250000}
  }
}

// ... other module states
```

### Files
```
products/cost_planner/
├── product.py                    # Router: base vs sub-module
├── base_module_config.py         # Base module config
├── base_module_config.json       # Landing + dashboard
├── aggregator.py                 # Combine module outcomes
├── auth.py                       # Mock authentication
│
└── modules/
    ├── income_sources/
    │   ├── module_config.py      # Same pattern as GCP
    │   ├── module_config.json
    │   └── logic.py
    │
    ├── assets_savings/
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py
    │
    ├── recommendation_cost_detail/  # Public module
    │   ├── module_config.py
    │   ├── module_config.json
    │   └── logic.py
    │
    └── ... (5 more modules)
```

---

## Key Differences

| Aspect | GCP (Single-Module) | Cost Planner (Multi-Module) |
|--------|---------------------|------------------------------|
| **Entry Point** | `product.py` → `run_module()` | `product.py` → Router → `run_module()` |
| **Navigation** | Linear (step 1 → 2 → 3...) | Hub-and-spoke (dashboard → modules) |
| **State Keys** | One: `"gcp"` | Many: `"cost"` + `"cost.MODULE"` |
| **Progress** | Single bar (0-100%) | Product + per-module progress |
| **Authentication** | Not required | Required (except 2 modules) |
| **Outcomes** | Single calculation at end | Module outcomes → aggregated |
| **Routing** | `?page=gcp` | `?page=cost&cost_module=income_sources` |
| **User Flow** | Complete all steps in sequence | Complete modules in any order |
| **Module Count** | 1 module, 6 steps | 1 base + 8+ sub-modules |
| **Back Button** | Previous step | Back to dashboard |

---

## Routing Examples

### GCP Routing
```
Simple linear:
  ?page=gcp  → Renders care_recommendation module (step 1)
             → User clicks Continue (step 2)
             → User clicks Continue (step 3)
             → ...
             → Results page
             → Back to Hub
```

### Cost Planner Routing
```
Hub-and-spoke:
  ?page=cost  
    → Renders base module (intro)
    → User selects path
    → Dashboard with module tiles
  
  ?page=cost&cost_module=income_sources
    → Auth check (mock login if needed)
    → Renders income_sources module
    → User completes questions
    → Outcome: total_income = $5000
    → Back to dashboard (?page=cost)
  
  ?page=cost&cost_module=assets_savings
    → Auth check
    → Renders assets_savings module
    → User completes questions
    → Outcome: liquid_assets = $250000
    → Back to dashboard
  
  ?page=cost&cost_module=recommendation_cost_detail
    → NO auth check (public module)
    → Shows typical costs for care tier
    → Read-only view
```

---

## Engine Reuse

**Both use the SAME `core/modules/engine.py`**

```python
# GCP
from core.modules.engine import run_module
from products.gcp.module_config import get_config

config = get_config()  # Returns ModuleConfig for care_recommendation
run_module(config)     # Engine renders the module

# Cost Planner - Base Module
from core.modules.engine import run_module
from products.cost_planner.base_module_config import get_base_config

config = get_base_config()  # Returns ModuleConfig for base
run_module(config)          # SAME ENGINE

# Cost Planner - Sub-Module
from core.modules.engine import run_module
import importlib

config_module = importlib.import_module("products.cost_planner.modules.income_sources.module_config")
config = config_module.get_config()  # Returns ModuleConfig for income_sources
run_module(config)                   # SAME ENGINE
```

**Zero engine changes needed for multi-module products!**

---

## Authentication Layer

### GCP: No Authentication
```python
# products/gcp/product.py
def render() -> None:
    config = get_config()
    render_shell_start("", active_route="gcp")
    run_module(config)  # ← No auth check
    render_shell_end()
```

### Cost Planner: Conditional Authentication
```python
# products/cost_planner/product.py
from products.cost_planner import auth

def render(module: Optional[str] = None) -> None:
    render_shell_start("", active_route="cost")
    auth.mock_login_button()  # Dev controls
    
    target_module = st.query_params.get("cost_module", module)
    
    if not target_module or target_module == "base":
        _render_base_module()  # No auth for landing
    else:
        _render_sub_module(target_module)  # Conditional auth

def _render_sub_module(module_key: str) -> None:
    if not auth.requires_auth(module_key):  # ← Auth gate
        return  # Blocks rendering, shows login prompt
    
    # Module only renders if auth passes
    config = load_module_config(module_key)
    run_module(config)

# products/cost_planner/auth.py
def requires_auth(module_key: str) -> bool:
    PUBLIC_MODULES = ["base", "recommendation_cost_detail"]
    if module_key in PUBLIC_MODULES:
        return True  # No auth needed
    return require_auth()  # Check auth status
```

---

## Progress Tracking

### GCP: Single Progress Bar
```
Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Results
[========================================] 100%

Progress = (current_step + section_completion) / total_steps * 100
```

### Cost Planner: Multi-Level Progress
```
Product-Level Progress (Hub displays this):
  Income: ✓ 100%    Assets: ✓ 100%    Home: 50%    Insurance: 0%
  VA: 0%    Costs: 0%    Adjustments: 0%    Summary: 0%
  
  Product Progress = avg(100, 100, 50, 0, 0, 0, 0, 0) = 31%

Module-Level Progress (Within each module):
  Income Sources Module:
    Step 1 → Step 2 → Step 3 → Results
    [========================================] 100%
  
  Assets Module:
    Step 1 → Step 2 → Results
    [====================                    ] 50%
```

---

## Outcome Aggregation

### GCP: Single Outcome
```python
# products/gcp/logic.py
def derive_outcomes(...) -> OutcomeContract:
    # Calculate care tier from all answers
    score = calculate_care_need_score(answers)
    tier = determine_care_tier(score)
    
    return OutcomeContract(
        recommendation=tier,
        flags={"meds_management_needed": True, "fall_risk": True},
        domain_scores={"care_need_score": score}
    )

Result stored in:
  st.session_state["gcp"]["_outcomes"]
```

### Cost Planner: Multi-Module Aggregation
```python
# Each module returns its own outcome:

# Module 1: income_sources/logic.py
def derive_outcomes(...) -> OutcomeContract:
    total_income = sum(income_sources)
    return OutcomeContract(
        domain_scores={"total_income": total_income}
    )

# Module 2: assets_savings/logic.py
def derive_outcomes(...) -> OutcomeContract:
    liquid = calculate_liquid_assets(answers)
    return OutcomeContract(
        domain_scores={"liquid_assets": liquid}
    )

# Product aggregator combines all modules:
# products/cost_planner/aggregator.py
def aggregate_product_outcomes(modules: Dict) -> OutcomeContract:
    income = modules["income_sources"]["outcome"]["domain_scores"]["total_income"]
    assets = modules["assets_savings"]["outcome"]["domain_scores"]["liquid_assets"]
    costs = modules["monthly_care_costs"]["outcome"]["domain_scores"]["monthly_care_cost"]
    
    deficit = costs - income
    months = assets / deficit if deficit > 0 else 999
    
    tier = "affordable" if months > 60 else "at_risk" if months > 24 else "unsustainable"
    
    return OutcomeContract(
        recommendation=tier,
        flags={"financial_planning_needed": months < 60},
        domain_scores={
            "total_income": income,
            "liquid_assets": assets,
            "monthly_care_cost": costs,
            "months_until_depletion": months
        }
    )

Result stored in:
  st.session_state["cost"]["outcome"]  # Product-level
  st.session_state["cost.income_sources"]["_outcomes"]  # Module 1
  st.session_state["cost.assets_savings"]["_outcomes"]  # Module 2
  # ... etc
```

---

## Implementation Effort

### GCP (Already Built)
- ✅ 1 product file
- ✅ 1 module config
- ✅ 1 logic file
- ✅ 6 steps defined
- **Total: ~500 lines of code**

### Cost Planner (To Build)
- 🔨 1 product router (~100 lines)
- 🔨 1 base module config (~150 lines)
- 🔨 1 auth module (~80 lines)
- 🔨 1 aggregator (~120 lines)
- 🔨 8 sub-modules × (~200 lines each) = 1600 lines
- **Total: ~2,050 lines of code**

**But:** Each sub-module is a clone-and-customize of the GCP pattern!

---

## Summary

**GCP = Single-Module Product**
- One module, linear flow
- Simple routing
- Single outcome
- No authentication

**Cost Planner = Multi-Module Product**
- Base module + 8+ sub-modules
- Hub-and-spoke routing
- Aggregated outcomes
- Authentication required (except 2 public modules)

**Both use the same extensible engine (`core/modules/engine.py`)**

**Ready to build Cost Planner?** Follow `COST_PLANNER_ARCHITECTURE.md` → Implementation Phases
