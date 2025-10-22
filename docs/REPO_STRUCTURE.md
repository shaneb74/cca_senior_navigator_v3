# Repository Structure

## Overview

This repository follows a **flat-within-domain** pattern: products, hubs, pages, and core are top-level domains with minimal nesting.

## Directory Tree (depth 3)

```
cca_senior_navigator_v3/
├── core/                      # Shared utilities, state, navigation
│   ├── flags.py               # Feature flag definitions
│   ├── nav.py                 # Navigation/routing engine
│   ├── state.py               # Session state management
│   ├── ui.py                  # UI helpers (HTML/CSS injection)
│   ├── paths.py               # Path resolution helpers
│   └── ... (22 core modules)
│
├── products/                  # Product tiles (GCP, Cost Planner, etc.)
│   ├── gcp_v4/                # ✅ CANONICAL Guided Care Plan
│   │   ├── product.py         # Main product entry point
│   │   └── modules/
│   │       └── care_recommendation/
│   │           ├── module.json    # ⚠️ ONLY module.json in products/
│   │           ├── logic.py       # Scoring + recommendation engine
│   │           ├── config.py      # Question/option configs
│   │           └── flags.py       # GCP-specific flags
│   │
│   ├── cost_planner_v2/       # ✅ CANONICAL Cost Planner
│   │   ├── product.py         # Main router
│   │   ├── intro.py           # Intro/Quick Estimate
│   │   ├── prepare_quick_estimate.py  # Keep-home logic
│   │   ├── assessments.py     # Financial Assessment hub
│   │   ├── expert_review.py   # Summary/results
│   │   ├── modules/           # Assessment JSON configs
│   │   │   └── assessments/
│   │   └── utils/             # Helpers (cost_calculator, regional_data, etc.)
│   │
│   ├── advisor_prep/          # Advisor Preparation tool
│   │   ├── product.py
│   │   ├── config/
│   │   └── modules/           # Question modules
│   │
│   ├── senior_trivia/         # Senior Trivia game
│   │   ├── product.py
│   │   └── modules/
│   │
│   ├── pfma_v3/               # Personal Financial Management
│   ├── resources_common/      # Shared "coming soon" placeholder
│   │   └── coming_soon.py     # Used by 8 simple products
│   │
│   └── ... (12 products total)
│
├── hubs/                      # Hub pages (concierge, learning, etc.)
│   ├── concierge.py
│   ├── learning.py
│   ├── partners.py
│   └── ... (7 hub files)
│
├── pages/                     # Top-level pages (welcome, login, etc.)
│   ├── welcome.py
│   ├── _stubs.py              # Shared page stubs
│   └── ... (12 page files)
│
├── static/                    # Static assets
│   └── images/
│       ├── logos/
│       └── ... (32 image files)
│
├── config/                    # App-wide configs
│   ├── nav.json               # Navigation structure
│   └── gcp/                   # GCP config JSONs (deprecated—now in modules/)
│
├── data/                      # User data (local persistence)
│   └── users/                 # User profiles (gitignored except demo/)
│
├── tests/                     # Test suite
│   ├── smoke_imports.py       # Basic import sanity check
│   └── test_*.py
│
└── docs/                      # Documentation
    ├── REPO_STRUCTURE.md      # This file
    ├── ARCHITECTURE.md        # Data flow + import rules
    └── CONTRIBUTING.md        # Contributor guidelines
```

---

## 📌 Source of Truth

### **Canonical GCP (Guided Care Plan)**
- **Path:** `products/gcp_v4/`
- **Module JSON:** `products/gcp_v4/modules/care_recommendation/module.json`
- **⚠️ CRITICAL:** Only **ONE** `module.json` allowed under `products/`. Pre-commit hook enforces this.
- **Entry Point:** `products/gcp_v4/product.py`
- **Scoring Logic:** `products/gcp_v4/modules/care_recommendation/logic.py`
- **Config:** `products/gcp_v4/modules/care_recommendation/config.py`

### **Canonical Cost Planner**
- **Path:** `products/cost_planner_v2/`
- **Entry Point:** `products/cost_planner_v2/product.py`
- **Quick Estimate:** `products/cost_planner_v2/intro.py` + `prepare_quick_estimate.py`
- **Financial Assessment:** `products/cost_planner_v2/assessments.py`
- **Expert Review:** `products/cost_planner_v2/expert_review.py`
- **Utilities:** `products/cost_planner_v2/utils/` (cost_calculator, regional_data, financial_helpers)
- **Assessment Configs:** `products/cost_planner_v2/modules/assessments/*.json`

### **No Legacy GCP Versions**
- ❌ `gcp_v1`, `gcp_v2`, `gcp_v3` do NOT exist
- Pre-commit hook blocks imports from legacy paths

---

## 🏗️ Adding a New Product

### **Pattern: Simple Product**
```
products/my_product/
├── __init__.py           # Optional, for package exports
├── product.py            # render() function (entry point)
└── utils.py              # Optional helpers
```

**Route registration:** Add to `config/nav.json`:
```json
{
  "key": "my_product",
  "label": "My Product",
  "module": "products.my_product.product:render"
}
```

### **Pattern: Complex Product (with modules/assessments)**
```
products/my_product/
├── product.py            # Main router
├── intro.py              # Entry screen
├── modules/              # Question/assessment configs (JSON)
│   └── my_module/
│       └── questions.json
└── utils/                # Product-specific helpers
    ├── calculator.py
    └── validators.py
```

---

## 📁 Directory Guidelines

### **When to use `modules/`**
- JSON-driven question/assessment configs
- Multi-step flows with dynamic rendering
- Examples: GCP care_recommendation, Cost Planner assessments

### **When to use `ui/`**
- Reusable UI components (cards, charts, forms)
- Summary/display logic separated from business logic
- Currently optional (products are small enough)

### **When to use `utils/`**
- Product-specific helpers (calculators, validators, formatters)
- Should NOT be imported by other products
- Examples: Cost Planner cost_calculator.py, regional_data.py

### **When to use `config/`**
- Static configuration (not user-facing questions)
- Example: Advisor Prep config/

---

## 🚫 Anti-Patterns

❌ **Don't create duplicate module.json files** (pre-commit blocks this)  
❌ **Don't create product subdirectories in hubs/ or pages/** (flat is fine)  
❌ **Don't import across products directly** (use core/* helpers)  
❌ **Don't hardcode static paths** (use `core.paths.get_static()`)  
❌ **Don't add gcp_v1/v2/v3 folders** (pre-commit blocks imports)

---

## 🔍 Finding Code

### **"Where is the GCP recommendation logic?"**
→ `products/gcp_v4/modules/care_recommendation/logic.py`

### **"Where are the Cost Planner keep_home rules?"**
→ `products/cost_planner_v2/prepare_quick_estimate.py` (lines 180-250)

### **"Where are feature flags defined?"**
→ `core/flags.py` (central registry)

### **"Where do I add a new hub?"**
→ Create `hubs/my_hub.py` with `render()` function, add to `config/nav.json`

### **"Where are static images loaded?"**
→ Use `core.paths.get_static("images/my_image.png")` for absolute paths

---

## 📊 Repository Statistics

- **Products:** 12 total (1 canonical GCP, 1 canonical Cost Planner, 10 others)
- **Hubs:** 7 files
- **Pages:** 12 files
- **Core Modules:** 22 files
- **Static Images:** 32 files
- **Module JSONs:** 1 (enforced by pre-commit)

---

## 🔄 Migration Notes

**From backup cleanup (2025-10-22):**
- Removed 108 backup files (30,773 lines)
- Added .gitignore patterns for `*.bak*`
- Pre-commit hook blocks backup file staging

**Current state:**
- ✅ No legacy GCP versions
- ✅ No duplicate module.json files
- ✅ Clean, normalized structure
- ✅ All imports use absolute paths
