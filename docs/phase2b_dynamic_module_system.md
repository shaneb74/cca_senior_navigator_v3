Perfect 👌 — great call. This will keep Claude on the rails and protect all the careful work you’ve already locked down.

Here’s the **complete, one-file Markdown brief** for Phase 2B.
Just drop this into your repo as `docs/phase2b_dynamic_module_system.md` and tell Claude to follow it *exactly*.

---

```markdown
# Phase 2B — Dynamic Module System (Architecture Integration)

**Date:** 2025-10-29  
**Branch:** `feature/dynamic-module-system`  
**Owner:** Concierge Care Advisors / Senior Navigator  
**Purpose:** Implement a dynamic “Lobby → Product → Module” hierarchy that automatically loads product modules without hard-coded imports.  
**Primary Goal:** Introduce modular rendering logic only — no visual, CSS, or routing changes.

---

## 🎯 Objective

Create a **lightweight registry system** so that:
- The Lobby renders product tiles dynamically (complete from Phase 2A).  
- Each product page renders its modules automatically via a shared registry.  
- The system is extensible — adding a new module requires no manual imports or page updates.  

**Absolutely no:**
- CSS edits  
- Changes to NAVI, header, or footer  
- Removal of existing module logic  

---

## 🧩 Files & Structure

New file:  
```

/core/modules_registry.py

```

Modified files:  
```

/core/products.py
/pages/hub_lobby.py
/pages/product_guided_care_plan.py
/pages/product_cost_planner.py
/pages/product_plan_with_my_advisor.py

````

---

## 🧱 System Design

### 1. Module Registry

`core/modules_registry.py`
```python
# =====================================
#  Senior Navigator — Module Registry
# =====================================
from typing import Callable, Dict

# Registry maps product_key → list[module_render_functions]
MODULE_REGISTRY: Dict[str, list[Callable]] = {}

def register_module(product_key: str, render_fn: Callable):
    """Register a module render() function under a product."""
    MODULE_REGISTRY.setdefault(product_key, []).append(render_fn)

def get_modules_for_product(product_key: str):
    """Return all render functions for a product."""
    return MODULE_REGISTRY.get(product_key, [])
````

Each module registers itself with a simple call in its `__init__.py`:

```python
from core.modules_registry import register_module
from . import render as render_fn
register_module("cost_planner", render_fn)
```

---

### 2. Render Integration in `core/products.py`

Add:

```python
from core.modules_registry import get_modules_for_product

def render_product(product_key: str):
    """Render all modules associated with a product."""
    modules = get_modules_for_product(product_key)
    if not modules:
        st.info("No modules registered for this product.")
        return
    for render_fn in modules:
        try:
            render_fn()
        except Exception as e:
            st.error(f"Error rendering module: {e}")
```

---

### 3. Update Product Pages

Example (`pages/product_guided_care_plan.py`):

```python
import streamlit as st
from core.products import render_product

def render():
    st.title("Guided Care Plan")
    render_product("guided_care_plan")
```

Repeat for Cost Planner and Plan With My Advisor.

---

### 4. Preserve Lobby Behavior

Ensure `hub_lobby.py` still renders product tiles using the current dynamic tile loading logic from Phase 2A.
Do not change button actions or routes.

---

## 🧪 Verification Checklist

| Step | Expected Result                                                      |
| :--: | :------------------------------------------------------------------- |
|   1  | Run `streamlit run app.py`                                           |
|   2  | Go to `?page=hub_lobby` → Products display normally                  |
|   3  | Click Guided Care Plan → All associated modules render automatically |
|   4  | Click Cost Planner → Financial Assessment modules load               |
|   5  | Click Plan With My Advisor → Scheduling modules load                 |
|   6  | No CSS or layout changes                                             |
|   7  | No errors in console/logs                                            |

---

## 🚫 Restrictions for Claude

* ❌ Do not modify any existing module logic or render functions.
* ❌ Do not touch `core/nav.py` or `app.py`.
* ❌ No changes to visual presentation or CSS.
* ✅ Commit only to files listed above.
* ✅ Ensure imports are explicit and relative (paths must work in the existing package structure).
* ✅ All new functions must include docstrings and type hints.

---

## 🧾 Deliverables

| File                              | Lines | Purpose                            |
| --------------------------------- | ----- | ---------------------------------- |
| `core/modules_registry.py`        | ~40   | Registry system for module mapping |
| `core/products.py`                | +25   | Render integration                 |
| `product_guided_care_plan.py`     | +10   | Dynamic render hook                |
| `product_cost_planner.py`         | +10   | Dynamic render hook                |
| `product_plan_with_my_advisor.py` | +10   | Dynamic render hook                |

Total change: ≈ 95 lines.

---

## ✅ Expected Outcome

* Lobby Hub stays visually identical.
* Product pages load their modules automatically.
* Future modules can be added with a single registration call.
* Architecture prepares for Phase 3 (interactive tile states and progress sync).

---

**End of Document**

```

---

When you’re ready:  
📄 Add this file → `docs/phase2b_dynamic_module_system.md`  
🔀 Switch to branch → `feature/dynamic-module-system`  
▶️ Then just tell Claude:  
> “Follow the Phase 2B Dynamic Module System brief exactly as written.”  

That’ll keep him perfectly in line.
```
